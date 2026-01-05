# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ExcelConvert 是一个基于 LangGraph 的智能 Excel 数据转换引擎，通过动态规则系统实现零编码适配各种 Excel 格式。

> ⚠️ **重要**：这是技术概念验证原型项目，仅供学习参考。生产环境请根据[技术决策文档](docs/TECHNICAL_DECISION.md)使用自身技术栈重新实现。

## 环境配置

### 目录配置（6个核心目录）

项目支持通过 **命令行参数**、**.env文件** 或 **Python API** 三种方式配置目录：

| 目录 | 默认值 | 环境变量 | 说明 |
|------|--------|----------|------|
| raw | `data/raw` | `RAW_DIR` | 原始输入Excel文件 |
| preprocess | `data/preprocess` | `PREPROCESS_DIR` | 预处理后的Excel |
| temp | `data/temp` | `TEMP_DIR` | IDR格式JSON + 图片 |
| transformed | `data/transformed` | `TRANSFORMED_DIR` | 规则处理后的JSON |
| output | `data/output` | `OUTPUT_DIR` | 最终输出的Excel |
| templates | `data/templates` | `TEMPLATES_DIR` | Excel模板文件 |

**配置优先级：** 命令行参数 > .env文件 > 默认值

### 方式1：.env文件配置（推荐）

```bash
# 1. 创建 .env 文件
cp .env.example .env

# 2. 编辑 .env，配置目录（示例使用E盘）
RAW_DIR=E:/input
PREPROCESS_DIR=E:/preprocess
TEMP_DIR=E:/temp
TRANSFORMED_DIR=E:/transformed
OUTPUT_DIR=E:/output
TEMPLATES_DIR=E:/templates

# 3. 直接运行
python main.py
```

### 方式2：命令行参数

```bash
# 处理单个文件
python main.py -i data/test.xlsx

# 使用E盘目录
python main.py -i E:/input/test.xlsx --raw-dir E:/input --temp-dir E:/temp --output-dir E:/output
```

### 方式3：Python API

```python
from main import convert_excel

# 使用自定义目录
success = convert_excel(
    "E:/input/test.xlsx",
    raw_dir="E:/input",
    temp_dir="E:/temp",
    output_dir="E:/output"
)
```

### LLM API 配置（用于智能字段映射）
项目使用 `.env` 文件管理 LLM API 配置。首次使用时：
```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件，配置 LLM API
# 推荐使用智谱 AI (https://open.bigmodel.cn/) 或 OpenAI
# LLM_BASE_URL=https://api.example.com/v1
# LLM_API_KEY=your-api-key-here
# LLM_MODEL=glm-4.5-x
```

## 核心命令

### 运行转换
```bash
# 处理 data/raw/ 目录下所有 Excel 文件（最常用）
python main.py

# 处理单个文件
python main.py -i data/your_file.xlsx

# 批量处理目录
python main.py -i /path/to/excel/files/ --batch

# 跳过预处理（已清洗数据）
python main.py -i clean.xlsx --skip-preprocessing

# 指定输出文件
python main.py -i input.xlsx -o output/result.xlsx
```

### 开发环境
```bash
# 激活虚拟环境（Windows）
.venv\Scripts\activate
# 或（Linux/Mac）
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 查看虚拟环境中的已安装包
pip list

# 验证 LLM 配置（如果使用智能字段映射）
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('LLM配置' + ('完整' if all([os.getenv('LLM_BASE_URL'), os.getenv('LLM_API_KEY')]) else '不完整'))"
```

## 架构概述

### 四阶段处理管道
1. **Excel预处理** (`src/excel_preprocess.py`) - 清理无用sheet、删除空行
2. **Excel转IDR** (`src/excel_to_json.py`) - 转换为标准化的IDR中间格式
3. **动态规则引擎** (`src/json_transformer.py`) - 基于 LangGraph 的工作流引擎，应用业务规则
4. **生成输出** (`src/json_to_excel.py`) - 将处理后的数据转换为最终Excel格式

### 数据流程
```
data/raw/ → data/preprocess/ → data/temp/ → data/transformed/ → data/output/
```

### 动态规则系统
规则系统位于 `rules/` 目录：
- `workflow_builder.py` - 动态工作流引擎核心
- `nodes_config.yaml` - 规则执行配置（控制规则的启用、禁用和执行顺序）
- 各种规则模块（如 `format_fba_id.py`, `calculate_totals.py`）

**`nodes_config.yaml` 配置说明**：
- `nodes` - 定义所有可用的规则节点及其执行函数
- `enabled` - 控制单个规则的启用/禁用状态
- `edges` - 定义规则执行的顺序和流程
- `disabled_nodes` - 全局禁用特定规则（优先级高于 enabled 字段）
- `node_groups` - 规则分组，便于批量管理

## 技术要点

### 添加新规则
1. 复制模板：`cp rules/_template.py rules/your_rule.py`
2. 实现业务逻辑函数（命名格式：`apply_your_rule_rule`）
3. 在 `rules/nodes_config.yaml` 中添加节点配置
4. 在 edges 中定义执行顺序
5. 保存即生效，无需修改主代码

### 禁用规则
有三种方式可以禁用规则：
1. **单个禁用**：在 `nodes_config.yaml` 中将规则的 `enabled` 设为 `false`
2. **全局禁用**：将规则名称添加到 `disabled_nodes` 列表
3. **临时禁用**：从 `edges` 中移除该规则的连接关系

### LangGraph 工作流
- 使用 StateGraph 管理数据状态传递
- 通过 YAML 配置灵活定义节点执行顺序
- 支持串行、并行和自定义工作流类型

### 数据格式
- IDR (Intermediate Data Representation) 是项目使用的中间格式
- 所有 Excel 数据首先转换为 IDR 格式的 JSON
- 规则引擎处理 IDR 格式数据
- 最后转换为最终输出格式

### 依赖说明
核心依赖（见 `requirements.txt`）：
- `openpyxl` - Excel 文件读写
- `pandas` - 数据处理和分析
- `PyYAML` - YAML 配置文件解析
- `langgraph` - 工作流编排引擎
- `requests` - HTTP 请求（LLM API 调用）
- `python-dotenv` - 环境变量管理

## 常见开发任务

### 调试转换问题
1. 检查 `data/temp/` - 查看 IDR 格式的中间输出
2. 检查 `data/transformed/` - 查看规则处理后的结果
3. 查看控制台输出的规则执行日志
4. 在规则中添加 `print()` 输出调试信息
5. 使用 `--skip-preprocessing` 跳过预处理步骤加快调试
6. 逐个禁用规则以定位问题来源

### 测试单个规则
```bash
# 直接运行规则文件（包含 __main__ 部分）
python rules/your_rule.py

# 在 Python 交互环境中测试
python -c "from rules.your_rule import apply_your_rule_rule; print(apply_your_rule_rule(test_data))"
```

### 管理规则执行顺序
编辑 `rules/nodes_config.yaml` 文件：
- 修改 `edges` 部分调整规则执行顺序
- 使用 `enabled: false` 禁用特定规则
- 使用 `disabled_nodes` 列表批量禁用规则
- 修改 `workflow.type` 切换工作流类型（sequential/parallel/custom）

### 查看项目结构
```bash
# 查看输出文件
ls data/output/

# 查看中间结果
ls data/temp/
ls data/transformed/

# 查看项目目录结构（跨平台）
find . -name "*.py" -o -name "*.yaml" | grep -v __pycache__ | sort
```

### 性能优化
```bash
# 处理大文件时的建议
# 1. 使用跳过预处理选项
python main.py -i large_file.xlsx --skip-preprocessing

# 2. 批量处理时使用并行（如果支持）
python main.py -i data/large_files/ --batch
```

## 注意事项

- 项目使用 Python 3.8+（当前虚拟环境使用 Python 3.13）
- 处理大文件时建议 8GB+ 内存
- 虚拟环境位于 `.venv/` 目录
- 主入口是 `main.py`，协调四个核心模块
- 规则系统支持热加载，修改 `nodes_config.yaml` 后无需重启
- 项目使用 LangGraph 进行工作流管理，所有规则通过配置文件动态加载

## 标准字段列表（31个）

LLM 智能字段映射规则使用以下标准字段作为映射目标：

```
FBA箱号, 中文品名, 英文品名, SKU码, 海关编码,
材质（中文）, 材质（英文）, 品牌, 品牌类型, 型号, 用途,
带电、磁, 总箱数, 单箱净重, 单箱毛重, 单箱个数,
产品总个数, 申报单价, 申报总价, 申报币种, 采购单价,
采购总价, 采购币种, 长 cm, 宽 cm, 高 cm,
亚马逊内部编号 REFERENCE ID（PO）, 仓库代码 AMAZON, FBA仓库地址,
图片, 产品在平台链接
```

这些标准字段定义了输出 Excel 的列结构，新增规则应遵循此字段命名规范。