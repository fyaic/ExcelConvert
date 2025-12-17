#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
价格验证规则
新增节点示例：验证价格是否合理
"""

from typing import Dict, Any
# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [price_validation] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [price_validation] {message.encode('ascii', 'replace').decode('ascii')}")

def apply_price_validation_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数 - 验证价格是否合理

    Args:
        data: 包含产品数据的字典

    Returns:
        处理后的数据字典
    """
    # 在这里实现你的业务逻辑
    changed = False
    warnings = []

    try:
        # 获取申报单价和采购单价
        declare_price = data.get("申报单价")
        purchase_price = data.get("采购单价")

        if declare_price and purchase_price:
            # 安全转换价格
            declare_price = safe_float_convert(declare_price)
            purchase_price = safe_float_convert(purchase_price)

            if declare_price is not None and purchase_price is not None:
                # 计算利润率
                if purchase_price > 0:
                    profit_margin = (declare_price - purchase_price) / purchase_price * 100

                    # 检查利润率是否过低（低于10%）
                    if profit_margin < 10:
                        warnings.append(f"利润率过低: {profit_margin:.2f}%")

                    # 检查申报价是否低于采购价
                    if declare_price < purchase_price:
                        warnings.append("申报价格低于采购价格")

                    # 添加利润率到数据中
                    data["利润率"] = round(profit_margin, 2)
                    changed = True

                    if profit_margin < 0:
                        data["利润警告"] = "负利润"
                    elif profit_margin < 10:
                        data["利润警告"] = "低利润"
                    else:
                        data["利润警告"] = "正常"

                    # 记录日志
                    log(f"价格验证完成，利润率: {profit_margin:.2f}%")

    except Exception as e:
        log(f"价格验证时发生错误: {e}")

    if warnings:
        log(f"价格验证警告: {', '.join(warnings)}")

    if changed:
        log("价格验证规则处理完成")

    return data


# 兼容性函数（保持与旧代码兼容）
def apply_price_validation(data: Dict[str, Any]) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return apply_price_validation_rule(data)

# 辅助函数
def safe_float_convert(value) -> float:
    """
    安全的浮点数转换

    Args:
        value: 原始值

    Returns:
        转换后的浮点数或None
    """
    if value is None or value == 'null' or str(value).strip() == '':
        return None
    try:
        return float(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "中文品名": "测试商品",
        "申报单价": "15.00",
        "采购单价": "12.00"
    }

    # 执行规则
    result = apply_price_validation_rule(test_data)
    print("处理结果:", result)