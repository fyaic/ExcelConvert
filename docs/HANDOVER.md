# ExcelConvert 项目交接文档

## 项目概述

ExcelConvert 是一个基于 LangGraph 的 Excel 数据转换引擎，通过动态规则系统处理各种 Excel 格式。核心价值在于无需修改代码即可快速适应新的 Excel 模板。

### 快速理解
- **输入**：任意格式的 Excel 文件
- **处理**：四阶段管道（预处理→IDR转换→规则应用→输出生成）
- **输出**：标准化的 Excel 文件
- **核心特点**：通过修改 YAML 配置和添加 Python 规则即可扩展功能

## 一、作为产品经理如何承接

### 1.1 理解核心价值
- 解决了 Excel 格式不统一的数据处理痛点
- 将原本需要数天的开发工作缩短到几小时
- 规则可复用，降低持续维护成本

### 1.2 市场定位
- **目标用户**：电商运营、数据分析师、供应链管理
- **使用场景**：多平台数据整合、供应商数据标准化
- **竞争优势**：零编码配置规则，快速上线

### 1.3 功能迭代路线
1. **短期（1个月）**
   - 增加常用规则库（日期格式化、货币转换等）
   - 支持更多 Excel 特性（合并单元格、条件格式）

2. **中期（3个月）**
   - Web 管理界面
   - 规则市场（社区贡献规则）
   - 批量任务管理

3. **长期（6个月）**
   - AI 辅助规则生成
   - 云服务部署
   - API 对接能力

### 1.4 商业模式
- **开源版本**：基础功能免费
- **专业版**：高级规则、技术支持
- **企业版**：私有部署、定制开发

## 二、作为技术人员如何承接

### 2.1 技术栈理解

#### 核心依赖
```python
# 主要技术栈
langgraph>=0.0.30    # 工作流引擎
openpyxl>=3.1.0      # Excel操作
pandas>=2.0.0        # 数据处理
pyyaml>=6.0          # 配置解析
requests>=2.31.0     # HTTP请求（LLM API调用）
python-dotenv>=1.0.0 # 环境变量管理
```

#### 项目结构
```
ExcelConvert/
├── main.py                 # 主入口，完整流程编排
├── src/                    # 核心处理模块
│   ├── excel_preprocess.py    # Excel清洗
│   ├── excel_to_json.py       # 转IDR格式
│   ├── json_transformer.py    # LangGraph规则引擎
│   └── json_to_excel.py       # 输出Excel
├── rules/                  # 动态规则系统
│   ├── workflow_builder.py    # 动态工作流构建
│   ├── nodes_config.yaml      # 规则配置
│   └── *.py                   # 各个规则实现
└── data/                   # 数据处理目录
```

### 2.2 开发环境搭建
```bash
# 1. 克隆项目
git clone <repository_url>
cd ExcelConvert

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 LLM API（可选）
cp .env.example .env
# 编辑 .env 文件，填入 LLM API 配置

# 5. 测试运行
python main.py -i test.xlsx
```

### 2.3 开发新规则

#### 步骤1：创建规则文件
```bash
cp rules/_template.py rules/my_new_rule.py
```

#### 步骤2：实现规则逻辑
```python
# rules/my_new_rule.py
def apply_my_new_rule_rule(data: dict) -> dict:
    """应用新规则"""
    # 获取需要处理的字段
    value = data.get("字段名")
    if value:
        # 处理逻辑
        data["新字段"] = process_value(value)
    return data
```

#### 步骤3：配置规则
```yaml
# rules/nodes_config.yaml
nodes:
  my_new_rule:
    module: my_new_rule
    function: apply_my_new_rule_rule
    description: "我的新规则"
    enabled: true

edges:
  - from: calculate_totals
    to: my_new_rule
  - from: my_new_rule
    to: END
```

### 2.4 调试技巧
```python
# 1. 添加日志
from datetime import datetime
def log(msg): print(f"{datetime.now()} [DEBUG] {msg}")

# 2. 单独测试规则
if __name__ == "__main__":
    test_data = {"字段名": "测试值"}
    result = apply_my_new_rule_rule(test_data)
    print(result)

# 3. 完整流程调试
python main.py -i debug.xlsx --skip-preprocessing
```

### 2.5 性能优化
- **内存优化**：分块读取大文件
- **并发优化**：多进程处理多个文件
- **缓存优化**：复用已加载的工作簿

## 三、作为运维人员如何承接

### 3.1 部署方案

#### 单机部署
```bash
# 1. 准备环境
yum install python38 python38-pip

# 2. 创建服务用户
useradd -m excelconv

# 3. 安装应用
sudo -u excelconv bash
git clone <repo>
cd ExcelConvert
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Docker部署（推荐）
```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 3.2 监控配置

#### 日志监控
```python
# 在 main.py 中添加日志配置
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/multiaconvert.log'),
        logging.StreamHandler()
    ]
)
```

#### 资源监控
```bash
# 监控脚本
#!/bin/bash
while true; do
    ps aux | grep "python main.py" | grep -v grep
    free -h
    df -h /app/data
    sleep 60
done
```

### 3.3 备份策略
- **配置备份**：rules/ 目录版本控制
- **数据备份**：data/output/ 定期归档
- **日志轮转**：按日期分割日志文件

### 3.4 故障处理

#### 常见问题
1. **内存不足**
   ```bash
   # 解决方案
   ulimit -v unlimited  # 取消内存限制
   export PYTHONMALLOC=malloc  # 使用malloc分配器
   ```

2. **文件权限**
   ```bash
   # 解决方案
   chown -R excelconv:excelconv /app/ExcelConvert
   chmod +x main.py
   ```

3. **依赖缺失**
   ```bash
   # 解决方案
   pip freeze > requirements_new.txt
   pip install -r requirements_new.txt
   ```

## 四、作为最终用户如何使用

### 4.1 快速开始（无需编码）

#### 场景1：处理单个文件
```bash
# 最简单的使用
python main.py
```
- 会自动处理 `data/raw/` 目录下的所有 Excel 文件
- 处理结果在 `data/output/` 目录

#### 场景2：批量处理
```bash
# 处理指定目录
python main.py -i /path/to/excel/files

# 跳过预处理（如果文件已经很干净）
python main.py -i clean.xlsx --skip-preprocessing
```

### 4.2 常见需求配置

#### 需求1：LLM 智能字段映射
- 文件已包含：`rules/field_mapping_llm.py`
- 支持自动识别和映射 31 种标准字段
- 需要配置 `.env` 文件中的 LLM API 参数
- 推荐使用智谱 AI 或 OpenAI 的 API 服务

#### 需求2：FBA箱号格式化
- 文件已包含：`rules/format_fba_id.py`
- 默认启用，无需配置

#### 需求3：价格计算
- 文件已包含：`rules/calculate_totals.py`
- 自动计算总价、总个数等

#### 需求4：填充默认值
- 文件已包含：`rules/fill_missing_values.py`
- 自动填充缺失的品牌、型号等字段

### 4.3 自定义需求（无需编码）

#### 场景：添加新的数据处理规则
1. **准备数据示例**
   - 提供 input.xlsx 和期望的 output.xlsx
   - 记录转换规则说明

2. **联系技术支持**
   - 通过 GitHub Issues 提交需求
   - 附上示例文件和规则说明

3. **获取新规则**
   - 技术团队提供新规则文件
   - 替换 rules/ 目录中的文件
   - 更新 nodes_config.yaml 配置

4. **测试使用**
   ```bash
   # 测试新规则
   python main.py -i test_file.xlsx
   ```

### 4.4 常见问题

#### Q1：处理失败怎么办？
A1：检查以下几点：
- 文件是否为有效的 Excel 格式
- data/ 目录是否有写权限
- 查看控制台错误信息

#### Q2：如何跳过某个步骤？
A2：使用参数控制
```bash
# 跳过预处理
python main.py -i file.xlsx --skip-preprocessing
```

#### Q3：处理大文件很慢？
A3：优化建议：
- 确保内存充足（建议8GB+）
- 关闭其他占用内存的程序
- 考虑分批处理

## 五、紧急联系信息

### 技术支持
- GitHub Issues: [项目地址]/issues
- 邮箱：support@multiaconvert.com

### 文档资源
- 项目 README：快速上手指南（包含 LLM 配置说明）
- CLAUDE.md：开发人员详细指南
- PROJECT_STRUCTURE.md：架构说明（包含 LLM 字段映射架构）
- rules/README.md：规则开发指南（包含 field_mapping_llm.py 详细说明）
- .env.example：LLM API 配置模板

### 版本信息
- 当前版本：v1.0.0
- Python 要求：3.8+
- 主要依赖：LangGraph 0.0.30+, openpyxl 3.1.0+

---

## 交接检查清单

- [ ] 项目已可正常运行
- [ ] 所有依赖已正确安装
- [ ] 配置文件已设置
- [ ] 测试文件可正常处理
- [ ] 日志系统正常工作
- [ ] 备份策略已实施
- [ ] 监控脚本已部署
- [ ] 文档已完整更新
- [ ] 团队培训已完成
- [ ] 紧急联系方式已确认

**交接完成日期**：____年__月__日
**交接人**：________________
**接收人**：________________