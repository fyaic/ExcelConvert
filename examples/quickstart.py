"""
ExcelConvert Python API 快速开始

这是一个简化的示例，展示如何在Python脚本中使用ExcelConvert
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import convert_excel


def main():
    print("ExcelConvert Python API 快速开始")
    print("=" * 50)

    # ========================================
    # 示例1：处理单个文件（使用默认目录）
    # ========================================
    print("\n示例1：处理单个文件（使用默认目录）")
    print("-" * 50)

    # success = convert_excel("data/test.xlsx")
    # if success:
    #     print("✓ 转换成功！")
    # else:
    #     print("✗ 转换失败！")

    print("代码：")
    print("  success = convert_excel('data/test.xlsx')")

    # ========================================
    # 示例2：使用E盘目录
    # ========================================
    print("\n示例2：使用E盘目录")
    print("-" * 50)

    # success = convert_excel(
    #     "E:/input/test.xlsx",
    #     raw_dir="E:/input",
    #     preprocess_dir="E:/preprocess",
    #     temp_dir="E:/temp",
    #     transformed_dir="E:/transformed",
    #     output_dir="E:/output",
    #     templates_dir="E:/templates"
    # )

    print("代码：")
    print("  success = convert_excel(")
    print("      'E:/input/test.xlsx',")
    print("      raw_dir='E:/input',")
    print("      temp_dir='E:/temp',")
    print("      output_dir='E:/output'")
    print("  )")

    # ========================================
    # 示例3：使用.env文件配置
    # ========================================
    print("\n示例3：使用.env文件配置")
    print("-" * 50)

    print("步骤：")
    print("  1. 复制 .env.example 为 .env")
    print("  2. 在 .env 中配置目录")
    print("  3. 运行代码：")
    print()
    print("  success = convert_excel('data/test.xlsx')")
    print("  # 函数会自动从 .env 读取配置")

    # ========================================
    # 示例4：批量处理
    # ========================================
    print("\n示例4：批量处理目录")
    print("-" * 50)

    # success = convert_excel(
    #     "data/input/",
    #     batch=True,
    #     temp_dir="E:/temp",
    #     output_dir="E:/output"
    # )

    print("代码：")
    print("  success = convert_excel(")
    print("      'data/input/',")
    print("      batch=True,")
    print("      output_dir='E:/output'")
    print("  )")

    # ========================================
    # 实际运行示例（取消注释即可运行）
    # ========================================
    print("\n" + "=" * 50)
    print("实际运行示例")
    print("=" * 50)

    # 取消下面的注释来实际运行转换
    # success = convert_excel(
    #     "data/test.xlsx",  # 修改为你的实际文件路径
    #     temp_dir="E:/temp",
    #     output_dir="E:/output"
    # )
    #
    # if success:
    #     print("\n✓ 转换成功！")
    # else:
    #     print("\n✗ 转换失败！")

    print("\n提示：取消注释上面的代码来实际运行转换")


if __name__ == "__main__":
    main()
