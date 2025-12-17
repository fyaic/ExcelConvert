#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
规则模板文件
所有规则文件都应遵循此结构
"""

from typing import Dict, Any

# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [rule_name] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [rule_name] {message.encode('ascii', 'replace').decode('ascii')}")

def apply_rule_template(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数

    Args:
        data: 包含产品数据的字典

    Returns:
        处理后的数据字典
    """
    # 在这里实现你的业务逻辑
    changed = False

    # 示例：处理特定字段
    if "字段名" in data and data["字段名"]:
        original_value = data["字段名"]
        # 进行转换
        data["字段名"] = process_value(original_value)
        changed = True

        # 记录日志
        log(f"字段已更新: {original_value} -> {data['字段名']}")

    if changed:
        log("规则处理完成")

    return data

# 兼容性函数（保持与旧代码兼容）
def apply_rule_name_alias(data: Dict[str, Any]) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return apply_rule_template(data)

# 辅助函数
def process_value(value: Any) -> Any:
    """
    处理值的辅助函数

    Args:
        value: 原始值

    Returns:
        处理后的值
    """
    # 在这里实现具体的处理逻辑
    return value

# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = {
        "字段名": "测试值",
        "其他字段": "其他值"
    }

    # 执行规则
    result = apply_rule_template(test_data)
    print("处理结果:", result)