"""
Excel通用格式转换引擎主程序

整合四个独立模块：
1. excel_preprocessing - Excel预处理
2. excel_to_json - Excel转IDR格式
3. json_transformer - JSON数据转换（多智能体协作）
4. json_to_excel - JSON转Excel输出

使用配置驱动的设计，支持多种客户模板。
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# 尝试导入 python-dotenv，如果不存在则跳过
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# 导入四个模块
try:
    from src.excel_preprocess import preprocess_excel
    from src.excel_to_json import excel_to_idr, batch_convert
    from src.json_transformer import transform_idr_from_temp, batch_transform
    from src.json_to_excel import json_to_excel, batch_convert_json
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有模块文件都在 src/ 目录下")
    sys.exit(1)


def load_env_config():
    """加载环境变量配置

    优先级：命令行参数 > 环境变量 > 默认值

    Returns:
        dict: 包含所有目录配置的字典
    """
    # 尝试加载 .env 文件
    env_loaded = False
    if DOTENV_AVAILABLE:
        env_loaded = load_dotenv()
        if env_loaded:
            log("成功加载 .env 文件")
        else:
            log("警告: .env 文件未找到或为空")
    else:
        log("警告: python-dotenv 未安装，无法读取 .env 文件")
        log("提示: 运行 'pip install python-dotenv' 安装")

    # 从环境变量读取配置（如果存在）
    config = {
        'raw_dir': os.getenv('RAW_DIR'),
        'preprocess_dir': os.getenv('PREPROCESS_DIR'),
        'temp_dir': os.getenv('TEMP_DIR'),
        'transformed_dir': os.getenv('TRANSFORMED_DIR'),
        'output_dir': os.getenv('OUTPUT_DIR'),
        'templates_dir': os.getenv('TEMPLATES_DIR'),
    }

    # 显示读取到的配置
    if config:
        log("从环境变量读取到以下配置:")
        for key, value in config.items():
            if value:
                log(f"  {key} = {value}")

    # 过滤掉 None 值（未设置的环境变量）
    return {k: v for k, v in config.items() if v is not None}

# 简化日志
def log(msg: str) -> None:
    """简化日志输出"""
    print(f"[MAIN] {msg}")


class ExcelConversionEngine:
    """Excel转换引擎主类"""

    def __init__(self,
                 customer_template: str = "customer_a",
                 raw_dir: Optional[str] = None,
                 preprocess_dir: Optional[str] = None,
                 temp_dir: Optional[str] = None,
                 transformed_dir: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 templates_dir: Optional[str] = None):
        self.customer_template = customer_template

        # 基础数据目录（用于兼容）
        self.data_dir = Path("data")

        # 6个核心目录配置 - 支持完全自定义
        self.raw_dir = Path(raw_dir) if raw_dir else self.data_dir / "raw"
        self.preprocess_dir = Path(preprocess_dir) if preprocess_dir else self.data_dir / "preprocess"
        self.temp_dir = Path(temp_dir) if temp_dir else self.data_dir / "temp"
        self.transformed_dir = Path(transformed_dir) if transformed_dir else self.data_dir / "transformed"
        self.output_dir = Path(output_dir) if output_dir else self.data_dir / "output"
        self.templates_dir = Path(templates_dir) if templates_dir else self.data_dir / "templates"

    def process_single_file(self,
                           input_file: Union[str, Path],
                           output_file: Optional[Union[str, Path]] = None,
                           skip_preprocessing: bool = False) -> bool:
        """处理单个Excel文件"""
        try:
            input_path = Path(input_file)
            log(f"开始处理文件: {input_path.name}")

            # 第一步：预处理（如果需要）
            if skip_preprocessing:
                log("跳过预处理步骤")
                # 预处理函数返回的是文件列表，这里我们需要取第一个文件
                preprocess_files = [input_path]
            else:
                log("步骤1: Excel预处理")
                # 预处理函数返回成功处理的文件列表
                preprocess_files = preprocess_excel(input_path, str(self.preprocess_dir))
                if not preprocess_files:
                    log("预处理失败")
                    return False
                log(f"  预处理完成: {len(preprocess_files)} 个文件")

            # 处理每个预处理后的文件（通常只有一个）
            all_success = True
            for preprocess_file in preprocess_files:
                preprocess_path = Path(preprocess_file)
                log(f"  处理文件: {preprocess_path.name}")

                # 第二步：Excel转IDR
                log("步骤2: Excel转IDR格式")
                idr_file = excel_to_idr(preprocess_path, str(self.temp_dir))
                if not idr_file:
                    log("Excel转IDR失败")
                    all_success = False
                    continue
                log(f"  IDR文件: {Path(idr_file).name}")

                # 第三步：JSON转换
                log("步骤3: JSON数据转换（多智能体）")
                # 保持与独立运行一致：transform_idr_from_temp 会创建子目录
                # transform_idr_from_temp 从temp目录读取，输出到transformed目录
                # 返回的是完整路径，包含了子目录结构
                transformed_file = transform_idr_from_temp(
                    Path(idr_file).name,
                    str(self.transformed_dir),
                    None,  # script_config参数未被使用，传入None
                    str(self.temp_dir)  # 传递自定义的 temp_dir
                )
                if not transformed_file:
                    log("JSON转换失败")
                    all_success = False
                    continue
                log(f"  转换完成: {Path(transformed_file).name}")

                # 第四步：JSON转Excel
                log("步骤4: JSON转Excel输出")
                if output_file is None:
                    # 去掉final前缀，直接使用原文件名
                    output_name = f"{preprocess_path.stem}.xlsx"
                    output_path = self.output_dir / output_name
                else:
                    output_path = Path(output_file)

                # 确保输出目录存在
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # json_to_excel函数需要的参数
                # 注意：json_to_excel函数使用模板文件（Excel），不是YAML配置
                # template_path是Excel模板文件路径，如果不提供会使用默认值
                # 这里我们传递自定义的目录配置
                success = json_to_excel(
                    input_path=str(transformed_file),
                    output_path=str(output_path),
                    template_path=None,  # 使用默认模板
                    process_images=True,
                    templates_dir=str(self.templates_dir),
                    temp_dir=str(self.temp_dir)
                )
                if not success:
                    log("JSON转Excel失败")
                    all_success = False
                else:
                    log(f"  最终输出: {output_path.name}")

            log(f"文件处理完成: {'成功' if all_success else '部分失败'}")
            return all_success

        except Exception as e:
            log(f"处理文件时出错: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_batch(self,
                     input_dir: Union[str, Path],
                     skip_preprocessing: bool = False) -> Dict[str, bool]:
        """批量处理Excel文件"""
        input_path = Path(input_dir)
        log(f"开始批量处理: {input_path}")

        # 查找所有Excel文件
        excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
        if not excel_files:
            log("未找到Excel文件")
            return {}

        log(f"找到 {len(excel_files)} 个Excel文件:")
        for idx, f in enumerate(excel_files, 1):
            log(f"  {idx}. {f.name}")

        # 处理结果汇总
        results = {}

        # 逐个处理文件（使用单文件处理逻辑）
        for excel_file in excel_files:
            log(f"\n处理文件: {excel_file.name}")
            success = self.process_single_file(excel_file, skip_preprocessing=skip_preprocessing)
            results[excel_file.name] = success

        # 统计结果
        success_count = sum(1 for success in results.values() if success)
        log(f"\n批量处理完成:")
        log(f"  成功: {success_count}/{len(results)} 个文件")

        for file, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            log(f"  {status} {file}")

        return results

    def run_pipeline(self,
                    input_path: Union[str, Path],
                    batch: bool = False,
                    output_file: Optional[Union[str, Path]] = None,
                    skip_preprocessing: bool = False) -> bool:
        """运行完整的转换管道"""
        log(f"启动转换管道（模板: {self.customer_template}）")
        log(f"输入: {input_path}")
        if output_file:
            log(f"输出: {output_file}")

        # 创建必要的目录
        for directory in [self.raw_dir, self.preprocess_dir, self.temp_dir, self.transformed_dir, self.output_dir, self.templates_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 判断是文件还是目录
        input_p = Path(input_path)

        # 优先判断是否为文件
        if input_p.is_file():
            # 处理单个文件
            log(f"检测到文件，执行单文件处理")
            success = self.process_single_file(input_path, output_file, skip_preprocessing)
            log(f"处理完成: {'成功' if success else '失败'}")
            return success
        elif input_p.is_dir():
            # 处理目录（批量）
            log(f"检测到目录，执行批量处理")
            results = self.process_batch(input_path, skip_preprocessing)
            success_count = sum(1 for success in results.values() if success)
            log(f"批量处理完成: {success_count}/{len(results)} 个文件成功")
            return success_count > 0
        else:
            # 路径既不是文件也不是目录
            log(f"错误: 路径不存在 - {input_path}")
            return False


def main():
    """主函数入口 - 支持环境变量和命令行参数"""

    # 默认执行完整管道：读取 data/raw 中的所有Excel文件
    default_input = "data/raw"

    # 加载环境变量配置
    log("=" * 60)
    log("开始加载配置...")
    env_config = load_env_config()
    log("=" * 60)

    # 如果没有命令行参数，使用默认值或环境变量
    if len(sys.argv) == 1:
        # 使用环境变量中的 raw_dir 作为默认输入（如果配置了）
        input_path = env_config.get('raw_dir') or default_input
        output_file = None
        skip_preprocessing = False
        batch = False

        # 使用环境变量配置（如果存在）
        raw_dir = env_config.get('raw_dir')
        preprocess_dir = env_config.get('preprocess_dir')
        temp_dir = env_config.get('temp_dir')
        transformed_dir = env_config.get('transformed_dir')
        output_dir = env_config.get('output_dir')
        templates_dir = env_config.get('templates_dir')

        # 显示配置信息
        log("=" * 60)
        log("最终使用的配置:")
        log(f"  输入路径: {input_path}")
        if raw_dir:
            log(f"  raw_dir: {raw_dir}")
        if preprocess_dir:
            log(f"  preprocess_dir: {preprocess_dir}")
        if temp_dir:
            log(f"  temp_dir: {temp_dir}")
        if transformed_dir:
            log(f"  transformed_dir: {transformed_dir}")
        if output_dir:
            log(f"  output_dir: {output_dir}")
        if templates_dir:
            log(f"  templates_dir: {templates_dir}")
        log("=" * 60)
    else:
        # 有参数则解析
        parser = argparse.ArgumentParser(
            description="Excel通用格式转换引擎",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  # 默认执行完整管道（无参数时）
  python main.py

  # 处理单个文件
  python main.py -i data/test.xlsx

  # 批量处理
  python main.py -i data/ --batch

  # 处理整个目录
  python main.py -i data/input/

  # 指定输出文件
  python main.py -i data/test.xlsx -o output/result.xlsx

  # 跳过预处理（如果文件已经是标准格式）
  python main.py -i data/test.xlsx --skip-preprocessing

  # 自定义目录（例如使用 E 盘目录）
  python main.py -i E:/input --raw-dir E:/input --preprocess-dir E:/preprocess \\
                --temp-dir E:/temp --transformed-dir E:/transformed --output-dir E:/output

  # 只指定部分目录（其他使用默认值或环境变量）
  python main.py -i data/input.xlsx --temp-dir E:/temp --output-dir E:/output

注意：
  1. 优先级：命令行参数 > 环境变量 > 默认值
  2. 可以在 .env 文件中配置目录（参考 .env.example）
  3. 未指定的目录将使用默认值 data/{raw,preprocess,temp,transformed,output,templates}
            """
        )

        parser.add_argument("-i", "--input", default=default_input,
                           help="输入文件或目录路径（默认: data/raw）")
        parser.add_argument("-o", "--output",
                           help="输出文件路径（仅单文件模式）")
        parser.add_argument("--batch", action="store_true",
                           help="批量处理模式（默认）")
        parser.add_argument("--skip-preprocessing", action="store_true",
                           help="跳过预处理步骤")

        # 6个核心目录配置参数（如果未指定，将使用环境变量或默认值）
        parser.add_argument("--raw-dir",
                           help="原始输入目录（默认: data/raw 或环境变量 RAW_DIR）")
        parser.add_argument("--preprocess-dir",
                           help="预处理输出目录（默认: data/preprocess 或环境变量 PREPROCESS_DIR）")
        parser.add_argument("--temp-dir",
                           help="临时文件目录（默认: data/temp 或环境变量 TEMP_DIR）")
        parser.add_argument("--transformed-dir",
                           help="转换后JSON目录（默认: data/transformed 或环境变量 TRANSFORMED_DIR）")
        parser.add_argument("--output-dir",
                           help="最终输出目录（默认: data/output 或环境变量 OUTPUT_DIR）")
        parser.add_argument("--templates-dir",
                           help="Excel模板目录（默认: data/templates 或环境变量 TEMPLATES_DIR）")

        args = parser.parse_args()

        input_path = args.input
        batch = args.batch
        output_file = args.output
        skip_preprocessing = args.skip_preprocessing

        # 获取目录配置（命令行参数优先，未指定则使用环境变量）
        raw_dir = args.raw_dir or env_config.get('raw_dir')
        preprocess_dir = args.preprocess_dir or env_config.get('preprocess_dir')
        temp_dir = args.temp_dir or env_config.get('temp_dir')
        transformed_dir = args.transformed_dir or env_config.get('transformed_dir')
        output_dir = args.output_dir or env_config.get('output_dir')
        templates_dir = args.templates_dir or env_config.get('templates_dir')

    # 创建转换引擎（使用自定义目录配置）
    engine = ExcelConversionEngine(
        customer_template="default",
        raw_dir=raw_dir,
        preprocess_dir=preprocess_dir,
        temp_dir=temp_dir,
        transformed_dir=transformed_dir,
        output_dir=output_dir,
        templates_dir=templates_dir
    )

    # 运行转换管道
    # 传递batch参数（如果用户明确指定了）
    success = engine.run_pipeline(
        input_path=input_path,
        batch=batch if 'batch' in locals() else None,
        output_file=output_file,
        skip_preprocessing=skip_preprocessing
    )

    if success:
        print("\n转换成功完成！")
        sys.exit(0)
    else:
        print("\n转换失败！")
        sys.exit(1)


# ================================
# Python API 接口
# ================================

def convert_excel(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    raw_dir: Optional[str] = None,
    preprocess_dir: Optional[str] = None,
    temp_dir: Optional[str] = None,
    transformed_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    templates_dir: Optional[str] = None,
    skip_preprocessing: bool = False,
    batch: bool = False
) -> bool:
    """
    Excel转换的Python API接口

    Args:
        input_path: 输入文件或目录路径
        output_path: 输出文件路径（可选，仅单文件模式）
        raw_dir: 原始输入目录
        preprocess_dir: 预处理输出目录
        temp_dir: 临时文件目录（IDR + 图片）
        transformed_dir: 转换后JSON目录
        output_dir: 最终输出目录
        templates_dir: Excel模板目录
        skip_preprocessing: 是否跳过预处理
        batch: 是否批量处理

    Returns:
        bool: 是否成功

    Example:
        >>> # 简单调用（使用默认目录）
        >>> success = convert_excel("data/test.xlsx")
        >>>
        >>> # 使用E盘目录
        >>> success = convert_excel(
        ...     "E:/input/test.xlsx",
        ...     raw_dir="E:/input",
        ...     temp_dir="E:/temp",
        ...     output_dir="E:/output"
        ... )
        >>>
        >>> # 从环境变量加载配置
        >>> success = convert_excel("data/test.xlsx")
    """
    # 加载环境变量配置
    env_config = load_env_config()

    # 合并参数：显式参数 > 环境变量 > None
    raw_dir = raw_dir or env_config.get('raw_dir')
    preprocess_dir = preprocess_dir or env_config.get('preprocess_dir')
    temp_dir = temp_dir or env_config.get('temp_dir')
    transformed_dir = transformed_dir or env_config.get('transformed_dir')
    output_dir = output_dir or env_config.get('output_dir')
    templates_dir = templates_dir or env_config.get('templates_dir')

    # 创建转换引擎
    engine = ExcelConversionEngine(
        customer_template="default",
        raw_dir=raw_dir,
        preprocess_dir=preprocess_dir,
        temp_dir=temp_dir,
        transformed_dir=transformed_dir,
        output_dir=output_dir,
        templates_dir=templates_dir
    )

    # 运行转换管道
    return engine.run_pipeline(
        input_path=input_path,
        batch=batch,
        output_file=output_path,
        skip_preprocessing=skip_preprocessing
    )


if __name__ == "__main__":
    main()