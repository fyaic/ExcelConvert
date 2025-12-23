# 动态规则系统开发指南

> 🎯 **零编码添加业务规则**，无需修改核心代码即可快速适应新的Excel模板

## 📖 目录

- [快速上手](#-快速上手)
- [规则文件详解](#-规则文件详解)
- [示例文件说明](#-示例文件说明)
- [配置管理](#-配置管理)
- [开发规范](#-开发规范)
- [常见问题](#-常见问题)

---

## 🚀 快速上手

### 添加新规则只需3步

#### 1️⃣ 创建规则文件

```bash
# 从模板创建（推荐新手）
cp _template.py your_new_rule.py

# 或从示例创建（推荐有经验的开发者）
cp price_validation.py your_new_rule.py
```

#### 2️⃣ 编写业务逻辑

打开创建的文件，找到主函数 `apply_xxx_rule`，在其中实现您的逻辑：

```python
def apply_your_rule_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """您的规则处理函数"""
    # 检查需要的字段是否存在
    if "目标字段" in data and data["目标字段"]:
        # 处理数据
        original_value = data["目标字段"]
        data["目标字段"] = process_value(original_value)

        # 记录日志
        log(f"字段已更新: {original_value} -> {data['目标字段']}")

    return data
```

#### 3️⃣ 启用规则

在 `nodes_config.yaml` 中添加您的规则：

```yaml
nodes:
  # ... 其他规则 ...

  # 添加您的规则
  your_rule:
    module: your_new_rule        # 文件名（不含.py）
    function: apply_your_rule_rule # 主函数名
    description: "规则描述"
    enabled: true                # 启用规则

edges:
  # ... 定义执行顺序 ...
  - from: 前一个规则
    to: your_rule               # 插入您的规则
  - from: your_rule
    to: 后一个规则
```

保存即可生效，无需重启！

---

## 📁 规则文件详解

### 标准结构

每个规则文件必须包含以下要素：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则描述：简要说明规则的作用
"""

from typing import Dict, Any

# 1. 日志函数（必须）
def log(message: str, level: str = "INFO"):
    """日志输出"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [规则名] {message}")
    except:
        pass

# 2. 主处理函数（必须）
def apply_规则名_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数

    Args:
        data: 产品数据字典

    Returns:
        处理后的数据字典
    """
    # 您的业务逻辑
    return data

# 3. 兼容性函数（可选）
def apply_规则名(data: Dict[str, Any]) -> Dict[str, Any]:
    """向后兼容的别名函数"""
    return apply_规则名_rule(data)
```

---

## 📚 示例文件说明

我们提供了三个示例文件，帮助您快速上手：

### 1️⃣ `_template.py` - 基础模板

**用途**：最简单的规则模板，适合**初学者**快速开始

**特点**：
- ✅ 包含最基础的结构
- ✅ 详细的注释说明
- ✅ 示例代码展示常见操作
- ✅ 测试代码帮助验证

**何时使用**：
- 第一次编写规则时
- 需要简单的数据转换时
- 学习规则系统的工作原理时

### 2️⃣ `price_validation.py` - 完整示例

**用途**：展示如何编写**复杂的业务规则**，适合作为参考

**功能展示**：
- ✅ 数据验证（价格范围检查）
- ✅ 计算逻辑（利润率计算）
- ✅ 条件判断（异常警告）
- ✅ 数据增强（添加计算结果）

**学习要点**：
```python
# 1. 安全的数值获取
price = safe_float(data.get("申报单价"))
cost = safe_float(data.get("采购单价"))

# 2. 数据验证
if price and cost and 0 < price < 10000:
    # 验证通过
    log(f"价格验证通过: {price}")
else:
    # 验证失败
    log(f"价格异常: {price}")

# 3. 计算并保存结果
if price and cost:
    profit_margin = (price - cost) / cost * 100
    data["利润率"] = round(profit_margin, 2)
```

**何时参考**：
- 需要实现复杂逻辑时
- 需要进行数据验证时
- 需要添加计算字段时

### 3️⃣ `field_mapping_llm.py` - LLM 智能字段映射

**用途**：使用**大语言模型**智能识别和映射非标准字段名到标准字段名

**核心价值**：
- 🤖 **自动识别**：利用 LLM 自动识别字段名的语义含义
- 🎯 **精准映射**：支持 31 种标准字段的自动映射
- ⚡ **批量处理**：一次性处理一行数据的所有字段
- 💾 **智能缓存**：避免重复调用 LLM API，降低成本
- 🛡️ **容错机制**：API 失败时自动降级，不影响其他规则

**标准字段列表**（31个）：
```
FBA箱号, 中文品名, 英文品名, SKU码, 海关编码,
材质（中文）, 材质（英文）, 品牌, 品牌类型, 型号, 用途,
带电、磁, 总箱数, 单箱净重, 单箱毛重, 单箱个数,
产品总个数, 申报单价, 申报总价, 申报币种, 采购单价,
采购总价, 采购币种, 长 cm, 宽 cm, 高 cm,
亚马逊内部编号 REFERENCE ID（PO）, 仓库代码 AMAZON, FBA仓库地址,
图片, 产品在平台链接
```

**配置要求**：
需要在项目根目录的 `.env` 文件中配置 LLM API：
```bash
LLM_BASE_URL=https://api.example.com/v1
LLM_API_KEY=your-api-key-here
LLM_MODEL=glm-4.5-x
```

**推荐服务商**：
| 服务商 | 注册地址 | 推荐模型 | 特点 |
|-------|---------|---------|-----|
| 智谱 AI | https://open.bigmodel.cn/ | glm-4.5-x | 性价比高，中文友好 |
| OpenAI | https://platform.openai.com/ | gpt-4o-mini | 快速稳定，准确率高 |

**何时使用**：
- 处理多种不同客户的 Excel 模板时
- 字段名格式差异较大时
- 需要减少手动配置映射规则时

---

## ⚙️ 配置管理

### `nodes_config.yaml` 详解

```yaml
# 节点定义
nodes:
  format_fba_id:
    module: format_fba_id              # Python文件名
    function: apply_fba_rule           # 主函数名
    description: "格式化FBA箱号"       # 规则描述
    enabled: true                      # 是否启用

# 执行流程
edges:
  - from: START                       # 起始节点
    to: format_fba_id                 # 第一个规则
  - from: format_fba_id
    to: replace_parentheses           # 第二个规则
  # ... 更多规则
  - from: fill_missing_values
    to: END                          # 结束节点
```

### 启用/禁用规则

临时禁用规则：
```yaml
your_rule:
  module: your_rule
  function: apply_your_rule_rule
  description: "规则描述"
  enabled: false    # 设为 false 即可禁用
```

### 调整执行顺序

通过修改 `edges` 来调整规则执行顺序：
```yaml
edges:
  # 原顺序：A -> B -> C
  - from: A
    to: B
  - from: B
    to: C

  # 改为：A -> C -> B
  - from: A
    to: C      # C 先执行
  - from: C
    to: B      # B 后执行
```

---

## 📋 现有规则列表

| 规则文件 | 主函数 | 功能描述 | 复杂度 |
|---------|--------|---------|--------|
| `field_mapping_llm.py` | `apply_field_mapping_llm_rule` | LLM智能字段映射，支持31种标准字段 | 🔴 复杂 |
| `format_fba_id.py` | `apply_fba_rule` | FBA箱号格式化，支持多种格式 | 🟡 中等 |
| `replace_parentheses.py` | `apply_parentheses_rule` | 英文括号转中文括号 | 🟢 简单 |
| `calculate_totals.py` | `apply_calculate_rule` | 计算总价、总数量等 | 🟡 中等 |
| `fill_missing_values.py` | `apply_fill_rule` | 填充默认值（品牌、型号等） | 🟢 简单 |
| `price_validation.py` | `apply_price_validation_rule` | 价格验证和利润率计算 | 🔴 复杂（示例） |

---

## 📝 开发规范

### 命名规范

- **文件名**：使用下划线分隔的小写字母（如 `my_rule.py`）
- **主函数**：`apply_规则名_rule`（如 `apply_my_rule_rule`）
- **日志标识**：`[规则名]`（如 `[my_rule]`）

### 代码规范

```python
# ✅ 好的实践
def apply_my_rule_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """规则处理函数"""
    changed = False

    # 1. 检查字段是否存在
    if "字段名" not in data:
        return data

    # 2. 类型检查
    value = data["字段名"]
    if not isinstance(value, str):
        return data

    # 3. 处理数据
    if value.strip():  # 非空检查
        data["字段名"] = value.strip().upper()
        changed = True
        log(f"字段已格式化")

    return data
```

### 错误处理

```python
# ✅ 始终捕获异常
try:
    result = risky_operation(data)
    data["结果"] = result
    log(f"操作成功: {result}")
except Exception as e:
    log(f"操作失败: {e}", "WARNING")
    # 继续处理，不要中断流程

return data
```

### 性能优化

```python
# ✅ 使用缓存（如果需要）
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_lookup(value: str):
    """昂贵的查找操作"""
    # 执行查询
    return result

# ✅ 批量处理
def batch_process(values: List[str]) -> List[str]:
    """批量处理，减少循环次数"""
    return [transform(v) for v in values if v]
```

---

## ❓ 常见问题

### Q: 如何调试规则？

**A**: 添加详细日志
```python
def debug_rule(data):
    log(f"输入数据: {data}")  # 查看输入
    # ... 处理逻辑 ...
    log(f"输出数据: {data}")  # 查看输出
    return data
```

### Q: 规则之间如何传递数据？

**A**: 通过共享的 `data` 字典
```python
# 规则1
def rule1(data):
    data["计算结果"] = calculate(data["输入"])
    return data

# 规则2
def rule2(data):
    if "计算结果" in data:
        result = data["计算结果"]
        # 使用规则1的结果
```

### Q: 如何处理条件执行？

**A**: 在规则内部添加条件判断
```python
def conditional_rule(data):
    # 只处理特定条件的数据
    if data.get("类型") == "特殊类型":
        # 执行特殊处理
        process_special(data)
    return data
```

### Q: 规则执行失败怎么办？

**A**: 系统会继续执行后续规则，不会中断
```python
def safe_rule(data):
    try:
        # 尝试执行
        return process(data)
    except Exception as e:
        # 记录错误但不中断
        log(f"规则执行失败: {e}", "ERROR")
        return data  # 返回原始数据
```

---

## 🎯 最佳实践

1. **保持简单** - 一个规则只做一件事
2. **充分测试** - 使用各种边界条件测试
3. **记录日志** - 关键操作都要记录日志
4. **优雅失败** - 遇到错误不要中断流程
5. **文档完整** - 为复杂规则编写说明文档

---

## 🔗 相关链接

- [返回项目首页](../README.md)
- [查看文档中心](../docs/README.md)
- [了解系统架构](../docs/PROJECT_STRUCTURE.md)

---

<p align="center">
  <strong>💡 提示</strong>：从 <code>_template.py</code> 开始，参考 <code>price_validation.py</code>，快速上手！
</p>