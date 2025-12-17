#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FBA箱号格式化规则
处理各种格式的FBA箱号，转换为标准格式
"""

import re
from typing import Dict, Any

# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    from datetime import datetime
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [format_fba_id] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [format_fba_id] {message.encode('ascii', 'replace').decode('ascii')}")

def format_fba_id(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化FBA箱号

    处理规则：
    1. U分隔格式: FBA1915DRGZJU000001-U000002 -> FBA1915DRGZJU000001-FBA1915DRGZJU000002
    2. 简短连字符格式: FBA193ZMDQGPU000001-10 -> FBA193ZMDQGPU000001-FBA193ZMDQGPU000010
    3. 逗号分隔格式: FBA15L4KXSK8U000001,FBA15L4KXSK8U000002 -> FBA15L4KXSK8U000001-FBA15L4KXSK8U000002
    4. 12位FBAID格式: FBA15L4KXSK8 + 总箱数20 -> FBA15L4KXSK8U000001-FBA15L4KXSK8U000020
    """
    # 获取FBA箱号字段
    fba_id = None
    fba_field_name = None
    for key in data.keys():
        if 'FBA' in key and '箱号' in key:
            fba_id = data[key]
            fba_field_name = key
            break

    if not fba_id or not isinstance(fba_id, str):
        return data

    # 规则1: 处理U分隔格式
    if '-U' in fba_id:
        parts = fba_id.split('-U')
        if len(parts) == 2:
            start_id = parts[0]
            end_id = parts[1].zfill(6)

            if 'U' in start_id:
                base_fba_id = start_id.split('U')[0]
                full_end_id = f"{base_fba_id}U{end_id}"
                data[fba_field_name] = f"{start_id}-{full_end_id}"
                log(f"U分隔格式: {fba_id} -> {data[fba_field_name]}")
                return data

    # 规则2: 处理简短连字符格式
    if '-' in fba_id and '-U' not in fba_id:
        parts = fba_id.split('-')
        if len(parts) == 2:
            start_part = parts[0]
            end_part = parts[1]

            if 'FBA' in start_part and end_part.isdigit():
                match = re.match(r'(.*?)(\d+)$', start_part)
                if match:
                    fba_prefix = match.group(1)
                    start_num = match.group(2)
                    end_num_padded = end_part.zfill(len(start_num))
                    end_id = f"{fba_prefix}{end_num_padded}"

                    data[fba_field_name] = f"{start_part}-{end_id}"
                    log(f"简短连字符格式: {fba_id} -> {data[fba_field_name]}")
                    return data

    # 规则3: 处理逗号分隔格式
    if ',' in fba_id:
        ids = [id.strip() for id in fba_id.split(',')]
        if len(ids) > 1:
            data[fba_field_name] = f"{ids[0]}-{ids[-1]}"
            log(f"逗号分隔格式: {fba_id} -> {data[fba_field_name]}")
            return data

    # 规则4: 处理12位FBAID格式
    if len(fba_id) == 12 and fba_id.startswith('FBA'):
        total_boxes = data.get("总箱数")

        if total_boxes is None:
            for key in data.keys():
                if '箱数' in key and '总' in key:
                    total_boxes = data[key]
                    break

        try:
            total_boxes_int = int(total_boxes)
            if total_boxes_int > 0:
                if total_boxes_int < 10:
                    end_suffix = f"00000{total_boxes_int}"
                elif total_boxes_int < 100:
                    end_suffix = f"0000{total_boxes_int}"
                elif total_boxes_int < 1000:
                    end_suffix = f"000{total_boxes_int}"
                else:
                    end_suffix = f"{total_boxes_int:06d}"

                data[fba_field_name] = f"{fba_id}U000001-{fba_id}U{end_suffix}"
                log(f"12位FBAID格式: {fba_id} -> {data[fba_field_name]} (总箱数: {total_boxes_int})")
                return data
        except (ValueError, TypeError):
            log(f"警告: 无法根据总箱数生成箱号")

    return data

def apply_fba_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主要规则处理函数 - 格式化FBA箱号

    Args:
        data: 包含产品数据的字典

    Returns:
        处理后的数据字典
    """
    # 调用实际的格式化函数
    return format_fba_id(data)

# 兼容性函数（保持与旧代码兼容）
def apply_format_fba_id_rule(data: Dict[str, Any]) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return apply_fba_rule(data)