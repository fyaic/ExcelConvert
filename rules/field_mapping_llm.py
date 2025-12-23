#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM字段映射规则 - 批量映射版本
使用大语言模型智能识别和映射非标准字段名到标准字段名
一次性处理一行数据的所有字段，提高效率
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import requests.exceptions

# 标准字段列表（31个）
STANDARD_FIELDS = [
    "FBA箱号", "中文品名", "英文品名", "SKU码", "海关编码",
    "材质（中文）", "材质（英文）", "品牌", "品牌类型", "型号", "用途",
    "带电、磁", "总箱数", "单箱净重", "单箱毛重", "单箱个数",
    "产品总个数", "申报单价", "申报总价", "申报币种", "采购单价",
    "采购总价", "采购币种", "长 cm", "宽 cm", "高 cm",
    "亚马逊内部编号 REFERENCE ID（PO）", "仓库代码 AMAZON", "FBA仓库地址",
    "图片", "产品在平台链接"
]

# LLM失败标志（模块级别，避免重复调用失败的API）
_llm_failed = False

def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [field_mapping_llm] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [field_mapping_llm] {message.encode('ascii', 'replace').decode('ascii')}")

def load_env():
    """加载.env文件"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 加载环境变量
load_env()

def call_llm_for_batch_mapping(field_names: list, cache: Dict[str, str] = None) -> Dict[str, str]:
    """
    调用LLM API进行批量字段映射

    Args:
        field_names: 待映射的字段名列表（一行数据中的所有键）
        cache: 缓存字典，避免重复调用

    Returns:
        映射结果字典 {原字段名: 映射后字段名}
    """
    global _llm_failed

    # 如果之前LLM调用失败过，直接跳过
    if _llm_failed:
        log("LLM之前调用失败，跳过本次映射")
        return {}

    mapping_result = {}
    unmapped_fields = []

    # 检查缓存和标准字段
    for field_name in field_names:
        # 如果已经是标准字段，直接映射
        if field_name in STANDARD_FIELDS:
            mapping_result[field_name] = field_name
            continue

        # 检查缓存
        if cache is not None and field_name in cache:
            mapping_result[field_name] = cache[field_name]
            continue

        unmapped_fields.append(field_name)

    # 如果没有需要映射的字段，直接返回
    if not unmapped_fields:
        log(f"所有字段已在缓存或已是标准字段，跳过LLM调用（缓存命中: {len(mapping_result)} 个字段）")
        return mapping_result

    # 构建批量映射提示词
    fields_str = "\n".join([f"- {field}" for field in unmapped_fields])

    # System Prompt: 定义角色和通用规则
    system_prompt = """你是一个专业的跨境电商数据字段映射助手。你的任务是将Excel表格中的非标准字段名精确映射到预定义的标准字段名。

【标准字段列表及含义】
FBA箱号: 亚马逊FBA箱子的编号
中文品名: 产品中文名称
英文品名: 产品英文名称
SKU码: 库存保持单位编码
海关编码: 海关申报用的HS编码
材质（中文）: 产品材质的中文名称
材质（英文）: 产品材质的英文名称
品牌: 产品品牌
品牌类型: 品牌类型（如自主品牌、贴牌等）
型号: 产品型号
用途: 产品用途说明
带电、磁: 是否带电或磁（普货/带电/带磁）
总箱数: 总箱数数量
单箱净重: 单个箱子的净重
单箱毛重: 单个箱子的毛重
单箱个数: 单个箱子内产品数量
产品总个数: 所有产品的总数量
申报单价: 申报单价
申报总价: 申报总金额
申报币种: 申报使用的货币（如USD、CAD、CNY等）
采购单价: 采购单价
采购总价: 采购总金额
采购币种: 采购使用的货币（如USD、CAD、CNY等）
长 cm: 产品长度，单位厘米
宽 cm: 产品宽度，单位厘米
高 cm: 产品高度，单位厘米
亚马逊内部编号 REFERENCE ID（PO）: 亚马逊内部的采购订单号
仓库代码 AMAZON: 亚马逊仓库代码（如YYZ7、ONT2等）
FBA仓库地址: FBA仓库的详细地址
图片: 产品图片
产品在平台链接: 产品在电商平台的链接
VAT号: 增值税税号（注意：不是币种！）

【映射规则】
1. 根据字段名的语义含义进行映射，而非字段值
2. 优先选择含义完全匹配的标准字段
3. 字段名相似度较高但含义不同时，不要强行映射
4. 找不到合适映射时，忽略该字段（不要猜测映射）

【特别注意】
- VAT号 = 增值税税号（Tax ID），绝对不是申报币种或采购币种！
- 币种字段（申报币种、采购币种）包含货币代码如 USD、CAD、CNY、EUR 等
- 仓库代码是亚马逊仓库的简称，如 YYZ7、ONT2、LGB8 等

【输出格式】
只返回JSON格式的映射关系，格式：{"原字段名": "目标字段名"}
示例：{"产品名称": "中文品名", "SKU编号": "SKU码", "长度": "长 cm"}
注意：直接输出JSON对象，不要使用markdown代码块"""

    # User Prompt: 具体的待映射字段
    user_prompt = f"""请将以下字段名映射到标准字段名：

【待映射字段名】
{fields_str}"""

    log(f"调用LLM进行字段映射（待映射字段数: {len(unmapped_fields)}）")

    try:
        import requests

        # 获取配置
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY")  # 修正键名
        model = os.getenv("LLM_MODEL", "glm-4.5-x")

        if not all([base_url, api_key]):
            log("LLM配置不完整，跳过字段映射", "WARNING")
            return mapping_result

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1  # 低温度确保稳定输出
        }

        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=90  # 超时时间90秒
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()

            # 清理可能的markdown格式
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # 修复双花括号问题（LLM可能学习错误示例）
            if content.startswith("{{") and content.endswith("}}"):
                content = content[1:-1]

            # 解析JSON映射关系
            try:
                batch_mapping = json.loads(content)
                log(f"批量映射成功，返回 {len(batch_mapping)} 个映射关系")

                # 更新映射结果并缓存
                for original, mapped in batch_mapping.items():
                    if mapped in STANDARD_FIELDS:
                        # 关键修复：检查目标标准字段是否已在原始数据中存在
                        # 如果已存在，拒绝LLM的映射建议，保留原有数据
                        if mapped in field_names:
                            log(f"跳过映射: {original} -> {mapped}（目标字段已存在，保留原数据）")
                            continue
                        mapping_result[original] = mapped
                        if cache is not None:
                            cache[original] = mapped
                        log(f"字段映射: {original} -> {mapped}")

            except json.JSONDecodeError as e:
                log(f"解析映射JSON失败: {e}", "WARNING")

        else:
            log(f"API调用失败: {response.status_code}", "WARNING")
            _llm_failed = True  # 标记失败，避免后续重复调用

    except requests.exceptions.Timeout as e:
        log(f"LLM调用超时（{90}秒），跳过字段映射: {e}", "WARNING")
        _llm_failed = True  # 标记失败，避免后续重复调用
    except Exception as e:
        log(f"LLM调用异常: {e}", "WARNING")
        # 只在网络/API错误时标记失败，解析错误不标记
        if "429" in str(e) or "timeout" in str(e).lower() or "connection" in str(e).lower():
            _llm_failed = True

    return mapping_result

def apply_field_mapping_llm_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数 - LLM字段映射（批量版本）
    只处理键的映射，不管值的内容

    Args:
        data: 包含产品数据的字典（一行Excel数据）

    Returns:
        处理后的数据字典（键名已映射到标准字段名）
    """
    if not isinstance(data, dict):
        log("输入数据不是字典格式，跳过处理", "WARNING")
        return data

    # 预处理：清理字段名中的换行符和特殊字符
    cleaned_data = {}
    for key, value in data.items():
        # 替换换行符和制表符
        clean_key = str(key).replace('\n', '').replace('\r', '').replace('\t', '')

        # 处理特殊情况：保留完整的字段名
        # 例如："采购币种（默认使用人民币）" 应保持完整
        # 只移除纯粹的备注信息，如："备注：请提供FBA编号"

        # 检查是否包含"备注"字样
        if '备注' in clean_key:
            # 移除备注部分
            clean_key = clean_key.split('备注')[0].strip()
        # 或者处理"：请提供"这样的格式
        elif '：请提供' in clean_key:
            clean_key = clean_key.split('：请提供')[0].strip()
        # 或者处理以冒号开头的说明
        elif '：' in clean_key and len(clean_key.split('：')[1]) > 0:
            # 检查冒号后的内容是否是说明文字
            after_colon = clean_key.split('：')[1]
            if any(word in after_colon for word in ['请提供', '默认', '单位', '说明']):
                clean_key = clean_key.split('：')[0].strip()

        # 移除空格
        clean_key = clean_key.strip()

        cleaned_data[clean_key] = value

    data = cleaned_data

    # 全局缓存字典（在多次调用中保持）
    if not hasattr(apply_field_mapping_llm_rule, '_cache'):
        apply_field_mapping_llm_rule._cache = {}

    cache = apply_field_mapping_llm_rule._cache

    # 获取所有字段名（一行数据中的所有键）
    original_keys = list(data.keys())
    log(f"开始处理一行数据，共 {len(original_keys)} 个字段")

    # 显示输入前的键名
    log(f"[输入前] 原始键名列表:")
    for i, key in enumerate(original_keys, 1):
        log(f"[输入前] {i:2d}. {key}")

    # 批量映射所有键名
    mapping_result = call_llm_for_batch_mapping(original_keys, cache)

    # 显示映射结果
    log(f"[映射结果] 键名映射关系:")
    for original_key, mapped_key in mapping_result.items():
        log(f"[映射结果] {original_key} -> {mapped_key}")

    # 应用映射关系，重新组合数据
    new_data = {}
    mapping_count = 0

    for original_key, value in data.items():
        # 获取映射后的键名
        mapped_key = mapping_result.get(original_key, original_key)

        if mapped_key != original_key:
            new_data[mapped_key] = value
            mapping_count += 1
        else:
            new_data[original_key] = value

    # 显示输入后的键名
    final_keys = list(new_data.keys())
    log(f"[输入后] 映射后键名列表:")
    for i, key in enumerate(final_keys, 1):
        log(f"[输入后] {i:2d}. {key}")

    log(f"字段映射完成，成功映射 {mapping_count} 个字段")
    return new_data

# 兼容性函数（保持与旧代码兼容）
def apply_field_mapping_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return apply_field_mapping_llm_rule(data)

# 测试代码
if __name__ == "__main__":
    # 测试数据（模拟一行Excel数据）
    test_data = {
        "产品名称": "螺丝刀套装",      # 应映射到"中文品名"
        "SKU编号": "SD001",          # 应映射到"SKU码"
        "FBA箱号": "FBA1915DRGZJU000001-U000002",  # 已经是标准字段
        "长度(厘米)": "30",          # 应映射到"长 cm"
        "宽度(厘米)": "20",          # 应映射到"宽 cm"
        "高度(厘米)": "10",          # 应映射到"高 cm"
        "材质": "塑料",              # 应映射到"材质（中文）"
        "品牌类型": "境外品牌",       # 已经是标准字段
        "箱子总数": "2",               # 应映射到"总箱数"
        "单箱个数": "80",            # 已经是标准字段
        "自定义字段": "测试值"        # 无映射
    }

    print("测试数据（一行Excel数据）:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")

    print("\n开始批量处理...")
    print("-" * 50)

    # 执行规则
    result = apply_field_mapping_llm_rule(test_data)

    print("\n处理结果:")
    for key, value in result.items():
        marker = " [标准字段]" if key in STANDARD_FIELDS else ""
        print(f"  {key}: {value}{marker}")

    # 统计
    standard_count = sum(1 for key in result if key in STANDARD_FIELDS)
    print(f"\n标准化统计: {standard_count}/{len(result)} 个字段已标准化")