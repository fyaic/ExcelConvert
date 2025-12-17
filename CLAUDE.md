# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

ExcelConvert 是一个基于 LangGraph 的智能 Excel 数据转换引擎，通过动态规则系统实现零编码适配各种 Excel 格式。

> ⚠️ **重要**：这是技术概念验证原型项目，仅供学习参考。生产环境请根据[技术决策文档](docs/TECHNICAL_DECISION.md)使用自身技术栈重新实现。

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
# 激活虚拟环境
.venv\Scripts\activate  # Windows

# 安装依赖（示例，根据实际情况补充）
pip install openpyxl pandas pyyaml langgraph
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

## 技术要点

### 添加新规则
1. 复制模板：`cp rules/_template.py rules/your_rule.py`
2. 实现业务逻辑函数（命名格式：`apply_your_rule_rule`）
3. 在 `rules/nodes_config.yaml` 中添加节点配置
4. 在 edges 中定义执行顺序
5. 保存即生效，无需修改主代码

### LangGraph 工作流
- 使用 StateGraph 管理数据状态传递
- 通过 YAML 配置灵活定义节点执行顺序
- 支持串行、并行和自定义工作流类型

### 数据格式
- IDR (Intermediate Data Representation) 是项目使用的中间格式
- 所有 Excel 数据首先转换为 IDR 格式的 JSON
- 规则引擎处理 IDR 格式数据
- 最后转换为最终输出格式

## 常见开发任务

### 调试转换问题
1. 检查 `data/temp/` - 查看 IDR 格式的中间输出
2. 检查 `data/transformed/` - 查看规则处理后的结果
3. 在规则中添加 `log()` 输出调试信息
4. 单独测试问题规则

### 测试单个规则
```bash
python rules/your_rule.py
```

### 查看项目结构
```bash
# 查看输出文件
ls data/output/

# 查看中间结果
ls data/temp/
ls data/transformed/
```

## 注意事项

- 项目使用 Python 3.8+
- 处理大文件时建议 8GB+ 内存
- 虚拟环境位于 `.venv/` 目录
- 主入口是 `main.py`，协调四个核心模块
- 规则系统支持热加载，修改配置后无需重启