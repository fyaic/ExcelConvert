#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
计算规则
计算价格相关字段：产品总个数、申报总价、采购总价
"""

from typing import Dict, Any

# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [calculate_totals] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [calculate_totals] {message.encode('ascii', 'replace').decode('ascii')}")

def apply_calculate_totals_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数 - 计算价格相关字段

    计算规则：
    1. 产品总个数 = 总箱数 × 单箱个数
    2. 申报总价 = 申报单价 × 产品总个数
    3. 采购总价 = 采购单价 × 产品总个数

    Args:
        data: 包含产品数据的字典

    Returns:
        处理后的数据字典
    """
    # 在这里实现你的业务逻辑
    changed = False

    try:
        # 计算产品总个数
        total_boxes = data.get("总箱数")
        pieces_per_box = data.get("单箱个数") or data.get("单箱\n个数")

        if total_boxes is not None and pieces_per_box is not None:
            try:
                total_boxes = float(str(total_boxes).strip()) if str(total_boxes).strip() != 'null' else None
                pieces_per_box = float(str(pieces_per_box).strip()) if str(pieces_per_box).strip() != 'null' else None

                if total_boxes is not None and pieces_per_box is not None and total_boxes > 0 and pieces_per_box > 0:
                    calculated_total = int(total_boxes * pieces_per_box)
                    data["产品总个数"] = calculated_total
                    changed = True
                    log(f"产品总个数: {total_boxes} × {pieces_per_box} = {calculated_total}")
            except (ValueError, TypeError):
                pass

        # 获取最终的产品总个数
        product_total_count = data.get("产品总个数")
        if product_total_count is None or product_total_count == 'null' or str(product_total_count).strip() == '':
            return data

        try:
            product_total_count = float(product_total_count)
        except (ValueError, TypeError):
            return data

        # 计算申报总价
        declare_unit_price = data.get("申报单价")
        if declare_unit_price is not None and declare_unit_price != 'null':
            try:
                declare_unit_price = float(str(declare_unit_price).strip())
                calculated_total_price = round(declare_unit_price * product_total_count, 4)
                data["申报总价"] = calculated_total_price
                changed = True
                log(f"申报总价: {declare_unit_price} × {product_total_count} = {calculated_total_price}")
            except (ValueError, TypeError):
                pass

        # 计算采购总价
        purchase_unit_price = data.get("采购单价")
        if purchase_unit_price is not None and purchase_unit_price != 'null':
            try:
                purchase_unit_price = float(str(purchase_unit_price).strip())
                calculated_purchase_price = round(purchase_unit_price * product_total_count, 4)
                data["采购总价"] = calculated_purchase_price
                changed = True
                log(f"采购总价: {purchase_unit_price} × {product_total_count} = {calculated_purchase_price}")
            except (ValueError, TypeError):
                pass

    except Exception as e:
        log(f"计算错误: {e}")

    if changed:
        log("计算规则处理完成")

    return data

# 兼容性函数（保持与旧代码兼容）
def apply_calculate_rules(data: Dict[str, Any]) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return apply_calculate_totals_rule(data)

# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "总箱数": 10,
        "单箱个数": 100,
        "申报单价": 15.0,
        "采购单价": 12.0
    }

    # 执行规则
    result = apply_calculate_totals_rule(test_data)
    print("处理结果:", result)