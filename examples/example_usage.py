"""
ExcelConvert 使用示例

展示三种使用方式：
1. 命令行参数方式
2. 环境变量配置方式（.env文件）
3. Python API 调用方式
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import convert_excel


def example_1_command_line():
    """
    方式1：命令行参数方式

    优点：
    - 灵活，每次运行可以指定不同参数
    - 适合临时任务和测试

    使用方法：
    ```bash
    # 处理单个文件
    python main.py -i data/test.xlsx

    # 使用E盘目录
    python main.py -i E:/input/test.xlsx \\
        --raw-dir E:/input \\
        --temp-dir E:/temp \\
        --output-dir E:/output

    # 批量处理
    python main.py -i data/ --batch
    ```
    """
    print("=" * 60)
    print("方式1：命令行参数方式")
    print("=" * 60)
    print("\n在命令行执行：")
    print("  python main.py -i data/test.xlsx")
    print("\n或使用自定义目录：")
    print("  python main.py -i E:/input/test.xlsx \\")
    print("      --raw-dir E:/input \\")
    print("      --temp-dir E:/temp \\")
    print("      --output-dir E:/output")
    print()


def example_2_env_file():
    """
    方式2：环境变量配置方式（.env文件）

    优点：
    - 配置集中管理
    - 不需要每次输入参数
    - 适合固定的工作流程

    使用方法：
    1. 复制 .env.example 为 .env
    2. 在 .env 文件中配置目录
    3. 运行：python main.py
    """
    print("=" * 60)
    print("方式2：环境变量配置方式（.env文件）")
    print("=" * 60)

    # 展示 .env 文件内容
    env_content = """
# .env 文件内容示例：

# 原始输入目录
RAW_DIR=E:/input

# 预处理输出目录
PREPROCESS_DIR=E:/preprocess

# 临时文件目录（IDR + 图片）
TEMP_DIR=E:/temp

# 转换后JSON目录
TRANSFORMED_DIR=E:/transformed

# 最终输出目录
OUTPUT_DIR=E:/output

# Excel模板目录
TEMPLATES_DIR=E:/templates

# LLM API配置（智能字段映射）
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_API_KEY=your-api-key-here
LLM_MODEL=glm-4.5-x
"""

    print("\n1. 创建 .env 文件：")
    print("   cp .env.example .env")

    print("\n2. 编辑 .env 文件，配置目录：")
    print(env_content)

    print("\n3. 直接运行（使用环境变量配置）：")
    print("   python main.py")
    print("   # 或指定输入文件")
    print("   python main.py -i data/test.xlsx")
    print()


def example_3_python_api():
    """
    方式3：Python API 调用方式

    优点：
    - 可以集成到其他Python脚本
    - 灵活的编程控制
    - 适合自动化工作流

    使用方法：
    - 导入 convert_excel 函数
    - 传递参数调用
    """
    print("=" * 60)
    print("方式3：Python API 调用方式")
    print("=" * 60)

    # 示例1：简单调用（使用默认目录）
    print("\n示例1：简单调用（使用默认目录）")
    print("-" * 40)
    print("from main import convert_excel")
    print("success = convert_excel('data/test.xlsx')")
    print("if success:")
    print("    print('转换成功！')")

    # 示例2：使用E盘目录
    print("\n示例2：使用E盘目录")
    print("-" * 40)
    print("from main import convert_excel")
    print("success = convert_excel(")
    print("    'E:/input/test.xlsx',")
    print("    raw_dir='E:/input',")
    print("    temp_dir='E:/temp',")
    print("    output_dir='E:/output'")
    print(")")

    # 示例3：从环境变量加载配置
    print("\n示例3：从环境变量加载配置（.env文件）")
    print("-" * 40)
    print("# .env 文件已配置好目录")
    print("from main import convert_excel")
    print("success = convert_excel('data/test.xlsx')")
    print("# 函数会自动读取 .env 中的配置")

    # 示例4：批量处理
    print("\n示例4：批量处理目录")
    print("-" * 40)
    print("from main import convert_excel")
    print("success = convert_excel(")
    print("    'data/input/',")
    print("    batch=True,")
    print("    output_dir='E:/output'")
    print(")")

    print()


def example_4_your_use_case():
    """
    你的具体需求：使用E盘目录

    展示三种方式如何实现你的需求
    """
    print("=" * 60)
    print("你的需求：使用E盘目录")
    print("=" * 60)

    print("\n方式1：命令行参数")
    print("-" * 40)
    print("python main.py -i E:/input/test.xlsx \\")
    print("    --raw-dir E:/input \\")
    print("    --preprocess-dir E:/preprocess \\")
    print("    --temp-dir E:/temp \\")
    print("    --transformed-dir E:/transformed \\")
    print("    --output-dir E:/output \\")
    print("    --templates-dir E:/templates")

    print("\n方式2：.env文件配置")
    print("-" * 40)
    print("# .env 文件内容：")
    print("RAW_DIR=E:/input")
    print("PREPROCESS_DIR=E:/preprocess")
    print("TEMP_DIR=E:/temp")
    print("TRANSFORMED_DIR=E:/transformed")
    print("OUTPUT_DIR=E:/output")
    print("TEMPLATES_DIR=E:/templates")
    print("")
    print("# 然后运行：")
    print("python main.py -i E:/input/test.xlsx")

    print("\n方式3：Python API")
    print("-" * 40)
    print("from main import convert_excel")
    print("")
    print("success = convert_excel(")
    print("    'E:/input/test.xlsx',")
    print("    raw_dir='E:/input',")
    print("    preprocess_dir='E:/preprocess',")
    print("    temp_dir='E:/temp',")
    print("    transformed_dir='E:/transformed',")
    print("    output_dir='E:/output',")
    print("    templates_dir='E:/templates'")
    print(")")

    print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "ExcelConvert 使用示例" + " " * 28 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    example_1_command_line()
    input("按回车继续...")

    example_2_env_file()
    input("按回车继续...")

    example_3_python_api()
    input("按回车继续...")

    example_4_your_use_case()

    print("=" * 60)
    print("总结")
    print("=" * 60)
    print("""
优先级顺序：
  命令行参数 > Python API参数 > .env文件 > 默认值

推荐用法：
  - 临时任务：使用命令行参数
  - 固定工作流：使用 .env 文件
  - 集成到脚本：使用 Python API

配置文件位置：
  - .env.example：配置模板
  - .env：你的实际配置（需要自己创建）
    """)


if __name__ == "__main__":
    main()
