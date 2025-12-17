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
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

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

# 简化日志
def log(msg: str) -> None:
    """简化日志输出"""
    print(f"[MAIN] {msg}")


class ExcelConversionEngine:
    """Excel转换引擎主类"""

    def __init__(self,
                 customer_template: str = "customer_a",
                 data_dir: str = "data"):
        self.customer_template = customer_template
        self.data_dir = Path(data_dir)

        # 目录结构
        self.preprocess_dir = self.data_dir / "preprocess"
        self.temp_dir = self.data_dir / "temp"
        self.transformed_dir = self.data_dir / "transformed"
        self.output_dir = self.data_dir / "output"

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
                preprocess_files = preprocess_excel(input_path)
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
                idr_file = excel_to_idr(preprocess_path, self.temp_dir)
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
                    self.transformed_dir,
                    None  # script_config参数未被使用，传入None
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
                # 这里我们暂时不使用模板，让函数使用默认处理方式
                success = json_to_excel(
                    input_path=str(transformed_file),
                    output_path=str(output_path),
                    template_path=None  # 使用默认处理方式
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

        log(f"找到 {len(excel_files)} 个Excel文件")

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
        for directory in [self.preprocess_dir, self.temp_dir, self.transformed_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 判断是文件还是目录
        input_p = Path(input_path)

        if input_p.is_file() or (batch is False):
            # 处理单个文件
            success = self.process_single_file(input_path, output_file, skip_preprocessing)
            log(f"处理完成: {'成功' if success else '失败'}")
            return success
        else:
            # 处理目录（批量）
            results = self.process_batch(input_path, skip_preprocessing)
            success_count = sum(1 for success in results.values() if success)
            log(f"批量处理完成: {success_count}/{len(results)} 个文件成功")
            return success_count > 0


def main():
    """主函数入口 - 简化版"""

    # 默认执行完整管道：读取 data/raw 中的所有Excel文件
    default_input = "data/raw"
    default_template = "customer_a"

    # 如果没有命令行参数，使用默认值
    if len(sys.argv) == 1:
        input_path = default_input
        template = default_template
        output_file = None
        skip_preprocessing = False
        # 不设置batch，让run_pipeline自动判断
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
            """
        )

        parser.add_argument("-i", "--input", default=default_input,
                           help="输入文件或目录路径（默认: data/raw）")
        parser.add_argument("-o", "--output",
                           help="输出文件路径（仅单文件模式）")
        # 移除了模板参数，系统使用动态规则处理所有格式
        parser.add_argument("--batch", action="store_true",
                           help="批量处理模式（默认）")
        parser.add_argument("--skip-preprocessing", action="store_true",
                           help="跳过预处理步骤")
        parser.add_argument("--data-dir", default="data",
                           help="数据文件目录（默认: data）")

        args = parser.parse_args()

        input_path = args.input
        # 不强制设置batch，让run_pipeline自动判断
        batch = args.batch  # 如果用户指定了--batch则使用
        output_file = args.output
        skip_preprocessing = args.skip_preprocessing

    # 创建转换引擎（使用默认模板，通过规则系统处理各种格式）
    engine = ExcelConversionEngine(
        customer_template="default",
        data_dir="data"
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


if __name__ == "__main__":
    main()