"""
动态工作流构建器
根据配置文件动态构建和执行数据处理规则
"""

import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, List
from datetime import datetime
import yaml

# 尝试导入langgraph，如果失败则提供模拟
try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("警告: langgraph未安装，将使用简化的工作流")


# 模块日志输出
def log(message: str, level: str = "INFO"):
    """日志输出函数"""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [workflow_builder] {message}")
    except:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level} - [workflow_builder] {message.encode('ascii', 'replace').decode('ascii')}")


class ConfigError(Exception):
    """配置错误异常"""
    pass


def load_rules_config(config_path: str = None) -> Dict[str, Any]:
    """加载节点配置文件"""
    if config_path is None:
        # 默认使用 rules 目录下的配置文件
        current_dir = Path(__file__).parent
        config_path = current_dir / "nodes_config.yaml"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        log(f"成功加载节点配置: {config_path}")
        return config
    except Exception as e:
        log(f"加载配置文件失败: {e}", "ERROR")
        # 返回默认配置
        return {
            "workflow": {
                "type": "sequential",  # sequential, parallel
                "state_key": "product_data"  # 状态中的数据键名
            },
            "nodes": {
                "format_fba_id": {
                    "module": "format_fba_id",
                    "function": "apply_fba_rule",
                    "description": "格式化FBA箱号"
                },
                "replace_parentheses": {
                    "module": "replace_parentheses",
                    "function": "apply_parentheses_rule",
                    "description": "替换英文括号为中文括号"
                },
                "calculate_totals": {
                    "module": "calculate_totals",
                    "function": "apply_calculate_rules",
                    "description": "计算价格相关字段"
                },
                "fill_missing_values": {
                    "module": "fill_missing_values",
                    "function": "apply_fill_missing_values_rule",
                    "description": "补充空值"
                }
            },
            "edges": [
                {"from": "START", "to": "format_fba_id"},
                {"from": "format_fba_id", "to": "replace_parentheses"},
                {"from": "replace_parentheses", "to": "calculate_totals"},
                {"from": "calculate_totals", "to": "fill_missing_values"},
                {"from": "fill_missing_values", "to": "END"}
            ],
            "disabled_nodes": []
        }


def validate_rule_path(module_path: str, function_name: str) -> bool:
    """验证规则路径是否安全"""
    # 基本安全检查：防止路径遍历攻击
    if ".." in module_path or "/" in module_path or "\\" in module_path:
        return False

    # 检查是否为.py文件
    rules_dir = Path(__file__).parent
    full_path = rules_dir / f"{module_path}.py"

    # 确保文件在rules目录内
    try:
        full_path.resolve().relative_to(rules_dir.resolve())
        return True
    except ValueError:
        return False


def load_rule_function(module_name: str, function_name: str) -> Callable:
    """动态加载规则函数"""
    # 安全验证
    if not validate_rule_path(module_name, function_name):
        raise ConfigError(f"不安全的模块路径: {module_name}")

    try:
        # 获取 rules 目录的绝对路径
        rules_dir = Path(__file__).parent
        module_file = rules_dir / f"{module_name}.py"

        if not module_file.exists():
            raise FileNotFoundError(f"规则文件不存在: {module_file}")

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 获取函数
        if not hasattr(module, function_name):
            raise AttributeError(f"函数 {function_name} 在模块 {module_name} 中不存在")

        func = getattr(module, function_name)
        log(f"成功加载规则函数: {module_name}.{function_name}")
        return func

    except (ConfigError, FileNotFoundError, AttributeError) as e:
        log(f"加载规则函数失败 {module_name}.{function_name}: {e}", "ERROR")
        raise
    except Exception as e:
        log(f"加载规则函数时发生未知错误 {module_name}.{function_name}: {e}", "ERROR")
        # 返回一个默认的处理函数（不改变数据）
        def dummy_func(data):
            log(f"警告: 使用空函数替代 {module_name}.{function_name}", "WARNING")
            return data
        return dummy_func


def create_node_function(node_name: str, node_config: Dict[str, Any]) -> Callable:
    """创建节点函数"""
    module_name = node_config["module"]
    function_name = node_config["function"]
    description = node_config.get("description", "")

    rule_func = load_rule_function(module_name, function_name)

    def node_function(state):
        """动态生成的节点函数"""
        # 从状态中获取数据键名
        state_key = node_config.get("state_key", "product_data")
        data = state[state_key]

        try:
            # 调用规则函数处理数据
            processed_data = rule_func(data)
            if description:
                log(f"节点 {node_name} 处理完成: {description}")
            else:
                log(f"节点 {node_name} 处理完成")
            return {state_key: processed_data}
        except Exception as e:
            log(f"节点 {node_name} 处理失败: {e}", "ERROR")
            # 出错时返回原始数据
            return {state_key: data}

    # 设置函数名称
    node_function.__name__ = f"node_{node_name}"

    return node_function


def build_workflow_from_edges(workflow, nodes: Dict[str, Any], edges: List[Dict]):
    """根据边配置构建工作流"""
    node_names = list(nodes.keys())

    # 添加边
    for edge in edges:
        from_node = edge["from"]
        to_node = edge["to"]

        if from_node == "START":
            workflow.add_edge(START, to_node)
        elif to_node == "END":
            workflow.add_edge(from_node, END)
        else:
            workflow.add_edge(from_node, to_node)

    return node_names


def build_dynamic_workflow(config_path: str = None):
    """根据配置动态构建工作流"""
    # 加载配置
    config = load_rules_config(config_path)
    workflow_config = config.get("workflow", {})
    nodes_config = config.get("nodes", {})
    edges_config = config.get("edges", [])
    disabled_nodes = config.get("disabled_nodes", [])

    # 获取状态键名
    state_key = workflow_config.get("state_key", "product_data")

    # 定义状态类型
    from typing import Dict, Any
    GraphState = Dict[str, Any]

    # 创建工作流
    if LANGGRAPH_AVAILABLE:
        workflow = StateGraph(GraphState)
    else:
        # 简化版工作流（当langgraph不可用时）
        return create_simple_workflow(nodes_config, disabled_nodes, state_key)

    # 添加节点
    active_nodes = {}
    node_names = []

    for node_name, node_config in nodes_config.items():
        if node_name in disabled_nodes:
            log(f"跳过已禁用的节点: {node_name}")
            continue

        try:
            # 添加状态键到配置中
            node_config["state_key"] = state_key

            # 创建节点函数
            node_func = create_node_function(node_name, node_config)

            # 添加到工作流
            workflow.add_node(node_name, node_func)
            active_nodes[node_name] = node_config
            node_names.append(node_name)
            log(f"添加节点: {node_name} -> {node_config['module']}.{node_config['function']}")
        except Exception as e:
            log(f"创建节点失败 {node_name}: {e}", "ERROR")
            continue

    # 构建执行流程
    if not node_names:
        log("警告: 没有可用的节点", "WARNING")
        return workflow.compile()

    # 根据配置构建工作流
    if edges_config:
        # 使用边配置
        build_workflow_from_edges(workflow, active_nodes, edges_config)
    else:
        # 默认串行流程
        workflow.add_edge(START, node_names[0])
        for i in range(len(node_names) - 1):
            workflow.add_edge(node_names[i], node_names[i + 1])
        workflow.add_edge(node_names[-1], END)

    # 编译工作流
    app = workflow.compile()
    log(f"动态工作流构建完成，包含 {len(node_names)} 个节点")

    return app


def create_simple_workflow(nodes_config: Dict[str, Any], disabled_nodes: List[str], state_key: str):
    """创建简化版工作流（当langgraph不可用时）"""
    active_nodes = {}

    for node_name, node_config in nodes_config.items():
        if node_name in disabled_nodes:
            continue

        try:
            module_name = node_config["module"]
            function_name = node_config["function"]
            rule_func = load_rule_function(module_name, function_name)
            active_nodes[node_name] = rule_func
        except Exception as e:
            log(f"跳过节点 {node_name}: {e}", "WARNING")

    def simple_workflow(data):
        """简化版工作流执行器"""
        result = data
        for node_name, rule_func in active_nodes.items():
            try:
                result = rule_func(result)
                log(f"执行节点: {node_name}")
            except Exception as e:
                log(f"节点 {node_name} 执行失败: {e}", "ERROR")
        return result

    # 模拟LangGraph的接口
    class SimpleWorkflow:
        def invoke(self, state):
            result = simple_workflow(state[state_key])
            return {state_key: result}

    log(f"简化版工作流创建完成，包含 {len(active_nodes)} 个节点")
    return SimpleWorkflow()


# 使用示例
if __name__ == "__main__":
    # 测试动态工作流
    app = build_dynamic_workflow()

    # 测试数据
    test_data = {
        "FBA箱号": "FBA1915DRGZJU000001-U000002",
        "中文品名": "螺丝刀套装",
        "品牌类型": "境外品牌（贴牌生产）",
        "总箱数": "2",
        "单箱个数": "80"
    }

    # 执行工作流
    result = app.invoke({"product_data": test_data})
    print("处理结果:", result["product_data"])