# ExcelConvert 开发指南

## 项目概述

ExcelConvert 是一个Excel数据转换引擎，通过动态规则系统处理各种Excel格式，无需为每个客户单独配置模板。

### 核心特性
- **动态规则系统**：通过YAML配置控制业务逻辑
- **模块化设计**：四阶段处理管道，各模块独立可测试
- **开箱即用**：无需复杂配置，直接运行即可处理Excel文件

## 项目结构

```
ExcelConvert/
├── main.py                    # 主程序入口 - 协调四个核心模块
├── src/                       # 核心源代码（4个独立模块）
│   ├── excel_preprocess.py    # Excel预处理：清理无用sheet、删除空行
│   ├── excel_to_json.py       # Excel→IDR格式转换
│   ├── json_transformer.py    # JSON数据转换（基于LangGraph的工作流引擎核心）
│   └── json_to_excel.py       # IDR格式→Excel输出
├── rules/                     # 业务规则目录 - 动态扩展
│   ├── workflow_builder.py    # 动态工作流引擎（LangGraph）
│   ├── nodes_config.yaml      # 规则执行配置文件
│   └── [各种业务规则模块]      # 独立的规则实现文件
├── data/                      # 数据处理流程
│   ├── raw/                   # 原始Excel文件
│   ├── preprocess/            # 预处理后文件
│   ├── temp/                  # IDR格式JSON和图片
│   ├── transformed/           # 转换后JSON数据
│   └── output/                # 最终Excel输出
└── .venv/                     # Python虚拟环境
```

## 快速开始

### 运行转换
```bash
# 最简单：处理 data/raw/ 中所有Excel文件
python main.py

# 处理单个文件
python main.py -i data/example.xlsx

# 跳过预处理（已清洗的文件）
python main.py -i data/clean.xlsx --skip-preprocessing
```

### 开发环境
```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install openpyxl pandas pyyaml langgraph
```

### 调试方法
```bash
# 查看输出
ls data/output/

# 检查中间结果
ls data/temp/      # IDR格式
ls data/transformed/  # 转换后JSON
```

## 核心数据流程

```
原始Excel → 预处理 → IDR格式JSON → 规则转换 → 最终Excel
   ↓          ↓         ↓          ↓         ↓
data/raw/  preprocess/  data/temp/  transformed/  output/
```

1. **Excel预处理**：清理无用sheet、删除空行、标准化格式
2. **Excel→IDR**：提取数据和图片，生成标准化的IDR格式JSON
3. **规则转换**：应用业务规则（FBA格式化、价格计算等）
4. **生成输出**：根据客户模板生成最终Excel

## 规则开发

### 添加新规则
1. 复制模板：`cp rules/_template.py rules/your_rule.py`
2. 实现业务逻辑
3. 更新配置：在 `rules/nodes_config.yaml` 添加：
   ```yaml
   your_rule:
     module: your_rule
     function: apply_your_rule_rule
     description: "规则描述"
     enabled: true
   ```
4. 保存即生效

### 技术要点
- **动态加载**：系统运行时自动加载规则
- **错误隔离**：单个规则失败不影响其他规则
- **状态管理**：通过LangGraph传递数据状态

### 故障排除

**常见问题：**
- 模块导入失败 → 检查 `src/` 和 `rules/` 目录文件
- 规则不执行 → 检查 `nodes_config.yaml` 配置
- 输出为空 → 检查输入数据格式

**调试方法：**
- 查看 `data/temp/` 和 `data/transformed/` 中间结果
- 在规则中添加 `log()` 输出
- 单独测试规则：`python rules/your_rule.py`