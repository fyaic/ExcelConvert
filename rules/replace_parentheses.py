"""
括号替换规则
将英文括号替换为中文括号
"""

from typing import Dict, Any

# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [replace_parentheses] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [replace_parentheses] {message.encode('ascii', 'replace').decode('ascii')}")

def replace_parentheses(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    替换英文括号为中文括号

    将数据中所有字符串字段的英文括号 ( ) 替换为中文括号 （ ）
    """
    changed = False

    for key, value in data.items():
        if isinstance(value, str):
            if '(' in value or ')' in value:
                data[key] = value.replace('(', '（').replace(')', '）')
                changed = True
                log(f"字段 '{key}' 括号已替换")

    if changed:
        log("所有英文括号已替换为中文括号")

    return data

# 主要规则函数，用于动态加载
def apply_parentheses_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """主要规则函数，用于动态工作流调用"""
    return replace_parentheses(data)