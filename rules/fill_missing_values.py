"""
默认值填充规则
补充空值字段，包括单箱个数、单箱净重和各种默认值
"""

from typing import Dict, Any

# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [fill_missing_values] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [fill_missing_values] {message.encode('ascii', 'replace').decode('ascii')}")

def fill_missing_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    补充空值字段

    填充规则：
    1. 单箱个数 = 产品总个数 ÷ 总箱数
    2. 单箱净重 = 单箱毛重 - 1
    3. 品牌类型字段：空值或"无"都改为"无品牌"
    4. 其他品牌字段：空值改为"无"
    5. 型号字段：空值改为"无"
    6. SKU码字段：空值改为"无"
    7. 产品在平台链接字段：空值改为"/"
    """
    filled = []

    try:
        # 计算单箱个数
        if not data.get("单箱个数") or data.get("单箱个数") == 'null':
            if not data.get("单箱\n个数") or data.get("单箱\n个数") == 'null':
                total_pieces = str(data.get("产品总个数", "")).strip()
                total_boxes = str(data.get("总箱数", "")).strip()
                if total_pieces and total_boxes and total_pieces != 'null' and total_boxes != 'null':
                    if float(total_boxes) > 0:
                        calculated_pieces = int(float(total_pieces) / float(total_boxes))
                        if "单箱个数" in data:
                            data["单箱个数"] = calculated_pieces
                        elif "单箱\n个数" in data:
                            data["单箱\n个数"] = calculated_pieces
                        filled.append(f"单箱个数={calculated_pieces}")

        # 计算单箱净重
        if not data.get("单箱净重") or data.get("单箱净重") == 'null':
            if not data.get("单箱\n净重") or data.get("单箱\n净重") == 'null':
                gross_weight = data.get("单箱毛重") or data.get("单箱\n毛重")
                if gross_weight and gross_weight != 'null':
                    try:
                        gross_weight = float(str(gross_weight).strip())
                        calculated_net_weight = round(gross_weight - 1, 4)
                        if "单箱净重" in data:
                            data["单箱净重"] = calculated_net_weight
                        elif "单箱\n净重" in data:
                            data["单箱\n净重"] = calculated_net_weight
                        filled.append(f"单箱净重={calculated_net_weight}")
                    except (ValueError, TypeError):
                        pass

        # 填充品牌字段
        brand_fields = [k for k in data.keys() if '品牌' in k]
        for field in brand_fields:
            value = data.get(field)
            if '品牌类型' in field:
                if value is None or value == 'null' or str(value).strip() in ['', '无']:
                    data[field] = "无品牌"
                    filled.append(f"{field}=无品牌")
            elif value is None or value == 'null' or str(value).strip() == '':
                data[field] = "无"
                filled.append(f"{field}=无")

        # 填充型号字段
        model_fields = [k for k in data.keys() if '型号' in k]
        for field in model_fields:
            value = data.get(field)
            if value is None or value == 'null' or str(value).strip() == '':
                data[field] = "无"
                filled.append(f"{field}=无")

        # 填充SKU码字段
        sku_fields = [k for k in data.keys() if 'SKU码' in k]
        for field in sku_fields:
            value = data.get(field)
            if value is None or value == 'null' or str(value).strip() == '':
                data[field] = "无"
                filled.append(f"{field}=无")

        # 填充平台链接字段
        platform_link_fields = [k for k in data.keys() if '平台链接' in k]
        for field in platform_link_fields:
            value = data.get(field)
            if value is None or value == 'null' or str(value).strip() == '':
                data[field] = "/"
                filled.append(f"{field}=/")

    except (ValueError, TypeError, ZeroDivisionError) as e:
        log(f"填充错误: {e}")

    if filled:
        log(f"填充完成: {', '.join(filled)}")

    return data

# 主要规则函数，用于动态加载
def apply_fill_missing_values_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """主要规则函数，用于动态工作流调用"""
    return fill_missing_values(data)