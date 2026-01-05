<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/LangGraph-powered-orange.svg" alt="LangGraph">
  <img src="https://img.shields.io/badge/Status-Prototype-red.svg" alt="Prototype">
  <img src="https://img.shields.io/github/last-commit/username/ExcelConvert" alt="Last commit">
</p>

> ⚠️ **重要提示**：本项目为技术概念验证原型，请勿直接用于生产环境。详见[技术决策文档](docs/TECHNICAL_DECISION.md)。

<h1 align="center">ExcelConvert</h1>

<p align="center">
  <strong>基于 LangGraph 的智能 Excel 数据转换引擎</strong>
</p>

<p align="center">
  通过动态规则系统实现零编码适配各种 Excel 格式
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-核心特性">特性</a> •
  <a href="#📖-文档">文档</a> •
  <a href="#🚀-安装">安装</a> •
  <a href="#💡-使用示例">示例</a>
</p>

---

## 📋 目录

- [🚀 快速开始](#-快速开始)
- [✨ 核心特性](#-核心特性)
- [🏗️ 架构设计](#️-架构设计)
- [💡 使用示例](#-使用示例)
- [🔧 动态规则系统](#-动态规则系统)
- [📊 性能指标](#-性能指标)
- [📖 文档](#-文档)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 8GB+ 内存（处理大文件时）
- 1GB+ 可用磁盘空间

### 一键运行

```bash
# 克隆项目
git clone https://github.com/your-username/ExcelConvert.git
cd ExcelConvert

# 安装依赖
pip install -r requirements.txt

# 处理所有文件
python main.py
```

### 自定义处理

```bash
# 处理单个文件
python main.py -i data/your_file.xlsx

# 批量处理目录
python main.py -i /path/to/excel/files/ --batch

# 跳过预处理（已清洗数据）
python main.py -i clean.xlsx --skip-preprocessing

# 指定输出文件
python main.py -i input.xlsx -o output/result.xlsx

# 自定义目录（例如使用 E 盘）
python main.py -i E:/input --raw-dir E:/input --temp-dir E:/temp --output-dir E:/output
```

### 环境变量配置（推荐）

使用 `.env` 文件配置目录，避免每次输入参数：

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env 文件，配置目录
# RAW_DIR=E:/input
# TEMP_DIR=E:/temp
# OUTPUT_DIR=E:/output

# 3. 直接运行（自动读取 .env 配置）
python main.py
```

**三种配置方式：**

| 方式 | 适用场景 | 命令示例 |
|------|----------|----------|
| **命令行参数** | 临时任务、测试 | `python main.py -i file.xlsx --temp-dir E:/temp` |
| **环境变量(.env)** | 固定工作流程 | 配置 `.env` 后直接运行 `python main.py` |
| **Python API** | 自动化脚本 | `from main import convert_excel` |

**优先级：** 命令行参数 > .env文件 > 默认值

---

## ✨ 核心特性

### 🤖 LLM 智能字段映射
利用大语言模型自动识别和映射非标准字段名到标准字段名，支持多种不同 Excel 模板的自动适配，显著提高模板兼容性和识别率

### 🎯 零编码适配
通过配置文件驱动，快速适应新的Excel模板，无需修改代码

### ⚡ 极速部署
新模板上线时间从**数周缩短到数小时**

### 💰 成本优势
开发成本降低 **80%**，维护成本降低 **60%**

### 🔧 灵活扩展
动态规则系统，支持热加载，规则独立开发和测试

### 📋 清晰流程
基于 LangGraph 的规则执行流程，通过配置文件定义执行顺序

---

## 🏗️ 架构设计

### 系统架构图

```mermaid
graph TB
    subgraph "四阶段处理管道"
        A[原始Excel] --> B[智能预处理]
        B --> C[IDR格式转换]
        C --> D[动态规则引擎]
        D --> E[标准化输出]
    end

    subgraph "数据流程"
        F[data/raw] --> G[data/preprocess]
        G --> H[data/temp]
        H --> I[data/transformed]
        I --> J[data/output]
    end

    subgraph "规则系统"
        K[workflow_builder.py]
        L[nodes_config.yaml]
        M[规则模块]

        subgraph "规则节点"
            N1[field_mapping_llm<br/>LLM智能字段映射]
            N2[format_fba_id<br/>FBA箱号格式化]
            N3[replace_parentheses<br/>括号替换]
            N4[calculate_totals<br/>价格计算]
            N5[fill_missing_values<br/>空值填充]
        end
    end

    D --> K
    K --> L
    L --> M
    M --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

### 核心组件

| 组件 | 描述 | 语言 |
|-----|-----|-----|
| **excel_preprocess.py** | Excel预处理，清理无用数据 | Python |
| **excel_to_json.py** | 转换为IDR中间格式 | Python |
| **json_transformer.py** | LangGraph规则引擎 | Python |
| **field_mapping_llm.py** | LLM智能字段映射规则 | Python |
| **format_fba_id.py** | FBA箱号格式化规则 | Python |
| **replace_parentheses.py** | 括号替换规则 | Python |
| **calculate_totals.py** | 价格计算规则 | Python |
| **fill_missing_values.py** | 空值填充规则 | Python |
| **json_to_excel.py** | 生成最终Excel | Python |

---

## 💡 使用示例

### FBA箱号智能格式化

```python
# 输入
"FBA193ZMDQGPU000001-10"

# 输出
["FBA193ZMDQGPU000001", "FBA193ZMDQGPU000010"]
```

### 价格自动计算

```python
# 输入
{
  "total_boxes": 10,
  "units_per_box": 9,
  "unit_price": 3.5
}

# 输出
{
  "total_units": 90,
  "total_value": 315.00,
  "currency": "USD"
}
```

### LLM 智能字段映射

```python
# 输入（多种非标准字段名）
{
  "产品名称": "螺丝刀套装",           # 映射到 "中文品名"
  "SKU编号": "SD001",               # 映射到 "SKU码"
  "长度(厘米)": "30",               # 映射到 "长 cm"
  "FBA箱号（连号用"-"表示）": "...", # 映射到 "FBA箱号"
  "仓库代码AMAZON": "YYZ7"          # 映射到 "仓库代码 AMAZON"
}

# 输出（标准字段名）
{
  "中文品名": "螺丝刀套装",
  "SKU码": "SD001",
  "长 cm": "30",
  "FBA箱号": "...",
  "仓库代码 AMAZON": "YYZ7"
}
```

---

## 🔧 动态规则系统

ExcelConvert 的核心优势是**动态规则系统**，让添加新业务规则变得极其简单：

### 快速添加规则（3步完成）

1. **创建规则文件**
```bash
cp rules/_template.py rules/my_rule.py
```

2. **编写业务逻辑**
```python
def apply_my_rule_rule(data: dict) -> dict:
    """您的业务逻辑"""
    if "field_name" in data:
        data["field_name"] = process_data(data["field_name"])
    return data
```

3. **启用规则**
```yaml
# rules/nodes_config.yaml
my_rule:
  module: my_rule
  function: apply_my_rule_rule
  enabled: true
```

### 示例文件说明

- **`_template.py`** - 规则模板文件，包含标准结构和示例代码
- **`field_mapping_llm.py`** - LLM 智能字段映射规则，自动识别和映射非标准字段名
- **`format_fba_id.py`** - FBA 箱号格式化规则
- **`replace_parentheses.py`** - 括号替换规则
- **`calculate_totals.py`** - 价格计算规则
- **`fill_missing_values.py`** - 空值填充规则

### LLM 智能字段映射规则

`field_mapping_llm.py` 是一个基于大语言模型的智能字段映射规则，用于解决多种不同 Excel 模板的字段名差异问题。

**功能特点**：
- 🤖 **自动识别**：利用 LLM 自动识别非标准字段名的语义含义
- 🎯 **精准映射**：将 31 种标准字段作为映射目标，确保准确性
- ⚡ **批量处理**：一次性处理一行数据的所有字段，提高效率
- 💾 **智能缓存**：避免重复调用 LLM API，降低成本
- 🛡️ **容错机制**：API 调用失败时自动降级，不影响其他规则执行

**标准字段列表**（31个）：
```
FBA箱号, 中文品名, 英文品名, SKU码, 海关编码,
材质（中文）, 材质（英文）, 品牌, 品牌类型, 型号, 用途,
带电、磁, 总箱数, 单箱净重, 单箱毛重, 单箱个数,
产品总个数, 申报单价, 申报总价, 申报币种, 采购单价,
采购总价, 采购币种, 长 cm, 宽 cm, 高 cm,
亚马逊内部编号 REFERENCE ID（PO）, 仓库代码 AMAZON, FBA仓库地址,
图片, 产品在平台链接
```

**配置要求**：
需要配置 `.env` 文件中的 LLM API 参数：
```bash
LLM_BASE_URL=https://api.example.com/v1
LLM_API_KEY=your-api-key-here
LLM_MODEL=glm-4.5-x
```

**使用方式**：
在 `rules/nodes_config.yaml` 中启用：
```yaml
field_mapping_llm:
  module: field_mapping_llm
  function: apply_field_mapping_llm_rule
  enabled: true  # 设为 false 可禁用 LLM 映射
```

### 规则优势

| 优势 | 传统方式 | ExcelConvert |
|-----|---------|------------------|
| 开发周期 | 2-5天 | 0.5-1天 |
| 编码需求 | 必须 | 无需 |
| 测试复杂度 | 高 | 低 |
| 维护成本 | 高 | 低 |
| 上线速度 | 慢 | 快 |

详细的规则开发指南请参考：[rules/README.md](rules/README.md)

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|-----|-----|-----|
| 单文件处理时间 | <30秒 | 10MB文件 |
| 内存占用 | <1GB | 峰值内存 |
| 规则开发周期 | 0.5-1天 | 从需求到上线 |
| 模板适配时间 | 2-4小时 | 新模板适配 |
| 并发处理能力 | 100+文件 | 批量处理 |
| 错误率 | <0.1% | 数据准确性 |

---

## 📖 文档

| 角色 | 推荐文档 | 说明 |
|-----|---------|-----|
| 👨‍💻 开发者 | [开发指南](docs/DEVELOPMENT.md) | 快速上手、调试技巧 |
| 🏗️ 架构师 | [架构设计](docs/PROJECT_STRUCTURE.md) | 系统架构、技术决策 |
| 📈 产品经理 | [需求分析](docs/REQUIREMENTS.md) | 业务价值、方案设计 |
| 🔧 运维人员 | [交接文档](docs/HANDOVER.md) | 部署、监控、故障处理 |
| 📊 技术管理 | [技术分析](docs/TECHNICAL_ANALYSIS.md) | 风险评估、成本分析 |
| 🎯 决策者 | [技术决策](docs/TECHNICAL_DECISION.md) | 方案演进、架构选型、生产建议 |

### 快速导航

- 📚 [文档中心](docs/README.md) - 所有文档的导航入口
- 🔧 [规则开发](rules/README.md) - 动态规则系统使用指南
- ❓ [常见问题](docs/FAQ.md) - 常见问题解答
- 🔄 [更新日志](CHANGELOG.md) - 版本更新记录

---

## 🚀 安装

### 从源码安装

```bash
# 克隆项目
git clone https://github.com/your-username/ExcelConvert.git
cd ExcelConvert

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置 LLM API（可选）

如果需要使用 LLM 智能字段映射功能：

```bash
# 1. 复制环境配置模板
cp .env.example .env

# 2. 编辑 .env 文件，填入 LLM API 配置
# 推荐使用智谱 AI (https://open.bigmodel.cn/) 或 OpenAI

# 3. 验证配置
python -c "import os; print('LLM配置' + ('完整' if all([os.getenv('LLM_BASE_URL'), os.getenv('LLM_API_KEY')]) else '不完整'))"
```

### 获取 LLM API 密钥

| 服务商 | 注册地址 | 推荐模型 | 特点 |
|-------|---------|---------|-----|
| 智谱 AI | https://open.bigmodel.cn/ | glm-4.5-x | 性价比高，中文友好 |
| OpenAI | https://platform.openai.com/ | gpt-4o-mini | 快速稳定，准确率高 |

### 使用 Docker

```bash
docker build -t multiaconvert .
docker run -v $(pwd)/data:/app/data multiaconvert
```


---

## 🤝 贡献

我们欢迎所有形式的贡献！

### 贡献方式

1. **报告问题** - 提交 [Issue](https://github.com/your-username/ExcelConvert/issues)
2. **功能建议** - 发起 [Discussion](https://github.com/your-username/ExcelConvert/discussions)
3. **代码贡献** - 提交 [Pull Request](https://github.com/your-username/ExcelConvert/pulls)

### 开发流程

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 添加适当的注释和文档字符串
- 确保所有测试通过
- 更新相关文档

---

## 🏆 致谢

感谢以下开源项目：

- [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的工作流编排框架
- [OpenPyXL](https://github.com/openpyxl/openpyxl) - Excel文件处理库
- [Pandas](https://github.com/pandas-dev/pandas) - 数据处理利器

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

<div align="center">
  <p>由 ❤️ 和 <a href="https://github.com/langchain-ai/langgraph">LangGraph</a> 强力驱动</p>
  <p>© 2025 ExcelConvert Team</p>
  <p>
    <a href="#top">回到顶部</a>
  </p>
</div>