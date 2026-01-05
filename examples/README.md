# ExcelConvert 使用示例

本目录包含使用 ExcelConvert 的示例代码和说明。

## 📁 文件说明

- `example_usage.py` - 完整的使用示例，展示三种使用方式
- `quickstart.py` - 快速开始示例，简化的代码示例
- `README.md` - 本文件

## 🚀 三种使用方式

### 方式1：命令行参数

适合临时任务和测试。

```bash
# 处理单个文件
python main.py -i data/test.xlsx

# 使用E盘目录
python main.py -i E:/input/test.xlsx \
    --raw-dir E:/input \
    --temp-dir E:/temp \
    --output-dir E:/output

# 批量处理
python main.py -i data/ --batch
```

### 方式2：环境变量配置（.env文件）

适合固定的工作流程。

**步骤：**

1. 复制配置模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件：
```bash
# .env 文件内容
RAW_DIR=E:/input
PREPROCESS_DIR=E:/preprocess
TEMP_DIR=E:/temp
TRANSFORMED_DIR=E:/transformed
OUTPUT_DIR=E:/output
TEMPLATES_DIR=E:/templates
```

3. 运行（自动读取 .env 配置）：
```bash
python main.py
# 或
python main.py -i data/test.xlsx
```

### 方式3：Python API

适合集成到其他Python脚本和自动化工作流。

```python
from main import convert_excel

# 使用E盘目录
success = convert_excel(
    "E:/input/test.xlsx",
    raw_dir="E:/input",
    preprocess_dir="E:/preprocess",
    temp_dir="E:/temp",
    transformed_dir="E:/transformed",
    output_dir="E:/output",
    templates_dir="E:/templates"
)

if success:
    print("转换成功！")
else:
    print("转换失败！")
```

## 📝 运行示例

### 查看完整示例

```bash
python examples/example_usage.py
```

### 查看快速开始示例

```bash
python examples/quickstart.py
```

## 🔧 配置优先级

```
命令行参数 > Python API参数 > .env文件 > 默认值
```

**示例：**

- `.env` 中设置了 `TEMP_DIR=E:/temp`
- 命令行执行 `python main.py --temp-dir E:/custom_temp`
- 最终使用 `E:/custom_temp`（命令行优先）

## 💡 推荐用法

| 场景 | 推荐方式 | 说明 |
|------|----------|------|
| 临时任务、测试 | 命令行参数 | 灵活，无需修改文件 |
| 固定工作流程 | .env文件 | 配置集中，管理方便 |
| 集成到脚本 | Python API | 可编程控制，适合自动化 |

## 📚 更多信息

- [主项目README](../README.md)
- [开发指南](../docs/DEVELOPMENT.md)
- [配置模板](../.env.example)
