#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSON数据转换模块 - 动态工作流版（修复导入路径）
完全基于配置文件构建工作流，支持灵活的节点管理
"""

import json
import os
import sys
import time
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from langgraph.graph import StateGraph, START, END

# 添加项目根目录到sys.path，确保可以导入rules模块
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入动态工作流构建器
from rules.workflow_builder import build_dynamic_workflow


def log(message: str, level: str = "INFO"):
    """简化的日志函数"""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - {message.encode('ascii', 'replace').decode('ascii')}")


# --- 定义图的状态 ---
class GraphState(TypedDict):
    """图的状态定义"""
    product_data: Dict[str, Any]


# --- 创建工作流 ---
def create_workflow():
    """创建并编译动态LangGraph工作流"""
    return build_dynamic_workflow()


# --- 处理函数 ---
def process_json_with_langgraph(input_data: Union[str, List[Dict]], app=None) -> List[Dict]:
    """使用动态LangGraph处理JSON数据"""
    if app is None:
        app = create_workflow()

    if isinstance(input_data, str):
        try:
            data_list = json.loads(input_data)
        except json.JSONDecodeError as e:
            log(f"JSON解析错误: {e}")
            return []
    else:
        data_list = input_data

    if not isinstance(data_list, list):
        log("输入的JSON应该是一个数组")
        return []

    processed_list = []

    for idx, item in enumerate(data_list):
        if not isinstance(item, dict):
            log(f"跳过非字典项: 索引 {idx}")
            continue

        log(f"处理产品 {idx + 1}/{len(data_list)}: {item.get('中文品名', '未知')}")

        final_state = app.invoke({"product_data": item})
        processed_item = final_state["product_data"]
        processed_list.append(processed_item)

    return processed_list


# --- 入口函数 ---
def transform_idr_to_json(input_path: Union[str, Path],
                        output_dir: Union[str, Path] = "data/transformed",
                        script_config: Optional[str] = None) -> str:
    """
    转换IDR格式JSON到标准JSON

    Args:
        input_path: 输入的IDR格式JSON文件路径
        output_dir: 输出目录（默认: data/transformed）
        script_config: 脚本配置文件路径（当前未使用）

    Returns:
        输出文件的路径
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 构建输出文件路径
    output_file = output_dir / input_path.name

    success = _transform_json_file(input_path, output_file)

    if success:
        return str(output_file)
    else:
        return None


def transform_idr_from_temp(file_name: str = None,
                            output_dir: Union[str, Path] = "data/transformed",
                            script_config: Optional[str] = None,
                            temp_dir: Union[str, Path] = "data/temp") -> Union[str, List[str]]:
    """
    从 temp 目录转换IDR文件到 transform 目录

    Args:
        file_name: 文件名（如 "CDKJ.json"），如果为None则处理所有文件
        output_dir: 输出目录（默认: data/transformed）
        script_config: 脚本配置文件路径（当前未使用）
        temp_dir: 临时文件目录（默认: data/temp）

    Returns:
        输出文件路径（单个文件或列表）
    """
    temp_dir = Path(temp_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if file_name:
        # 处理单个文件
        input_file = temp_dir / file_name

        # 查找子目录中的文件
        if not input_file.exists():
            for sub_dir in temp_dir.iterdir():
                if sub_dir.is_dir():
                    potential_file = sub_dir / file_name
                    if potential_file.exists():
                        input_file = potential_file
                        break

        if input_file.exists():
            # 计算相对于temp目录的路径，保持子目录结构
            rel_path = input_file.relative_to(temp_dir)
            output_path = output_dir / rel_path
            # 确保父目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            success = _transform_json_file(input_file, output_path)
            if success:
                return str(output_path)
        return None
    else:
        # 处理所有文件
        results = []
        json_files = list(temp_dir.rglob("*.json"))

        for json_file in json_files:
            # 保持相对路径结构
            rel_path = json_file.relative_to(temp_dir)
            output_file = output_dir / rel_path
            output_file.parent.mkdir(parents=True, exist_ok=True)

            success = _transform_json_file(json_file, output_file)
            if success:
                results.append(str(output_file))

        return results


# --- 内部文件处理函数 ---
def _transform_json_file(input_file: Path, output_file: Path) -> bool:
    """内部函数：转换单个JSON文件"""
    try:
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 检查文件结构
        if not isinstance(json_data, dict) or 'data' not in json_data:
            log(f"警告: 文件 {input_file} 不是有效的IDR格式（缺少data字段），直接处理整个文件")
            data_to_process = json_data
            metadata = None
        else:
            metadata = json_data.get('metadata')
            data_to_process = json_data['data']
            log(f"读取文件: {input_file}, metadata记录数: {metadata.get('records') if metadata else '未知'}, data包含 {len(data_to_process)} 条记录")

        # 处理data部分
        processed_data = process_json_with_langgraph(data_to_process)

        # 构建输出数据
        if metadata is not None:
            output_data = {
                'metadata': metadata,
                'data': processed_data
            }
            # 更新metadata中的记录数
            output_data['metadata']['records'] = len(processed_data)
        else:
            output_data = processed_data

        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        log(f"转换完成: {output_file}")
        return True

    except Exception as e:
        log(f"转换失败: {e}")
        return False


# --- 兼容性函数 ---
def transform_json(input_file: Union[str, Path],
                   output_file: Union[str, Path],
                   script_config: Optional[str] = None) -> bool:
    """兼容性函数：转换单个JSON文件（只处理data部分，保留metadata）"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    return _transform_json_file(input_path, output_path)


def batch_transform(input_dir: Union[str, Path],
                   output_dir: Union[str, Path],
                   script_config: Optional[str] = None) -> Dict[str, bool]:
    """批量转换JSON文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}

    # 查找所有JSON文件（包括子目录）
    json_files = list(input_path.rglob("*.json"))

    if not json_files:
        log(f"在目录 {input_path} 中未找到JSON文件")
        return results

    log(f"找到 {len(json_files)} 个JSON文件（包括子目录）")

    # 处理每个文件
    for json_file in json_files:
        output_file = output_path / json_file.name
        success = transform_json(json_file, output_file, script_config)
        results[json_file.name] = success

    # 统计结果
    success_count = sum(1 for success in results.values() if success)
    log(f"批量转换完成: {success_count}/{len(results)} 个文件成功")

    return results


# --- 命令行接口 ---
def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="JSON数据转换工具 - 动态工作流版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用默认参数（从 temp 读取，输出到 transformed）
  python src/json_transformer_fixed.py

  # 指定文件
  python src/json_transformer_fixed.py input.json output.json

  # 指定目录
  python src/json_transformer_fixed.py input_dir output_dir

  # 批量处理模式
  python src/json_transformer_fixed.py --batch input_dir output_dir
        """
    )

    parser.add_argument("input", nargs='?', default="data/temp",
                       help="输入文件或目录（默认: data/temp）")
    parser.add_argument("output", nargs='?', default="data/transformed",
                       help="输出文件或目录（默认: data/transformed）")
    parser.add_argument("--batch", action="store_true", help="批量处理模式")
    parser.add_argument("--script-config", help="脚本配置文件（当前未使用）")

    args = parser.parse_args()

    # 如果没有提供参数，使用默认行为（从temp处理所有文件到transformed）
    if args.input == "data/temp" and args.output == "data/transformed" and not args.batch:
        print("使用默认参数：从 data/temp 处理所有文件到 data/transformed")
        results = transform_idr_from_temp()
        if results:
            print(f"\n处理完成！成功处理 {len(results)} 个文件:")
            for result in results:
                print(f"  - {result}")
        else:
            print("\n没有找到需要处理的文件")
        return

    if args.batch:
        # 批量处理
        results = batch_transform(args.input, args.output, args.script_config)
        print(f"\n批量处理结果:")
        for filename, success in results.items():
            status = "成功" if success else "失败"
            print(f"  {filename}: {status}")
    else:
        # 单文件处理
        success = transform_json(args.input, args.output, args.script_config)
        if success:
            print("\n转换成功！")
        else:
            print("\n转换失败！")
            sys.exit(1)


if __name__ == "__main__":
    main()