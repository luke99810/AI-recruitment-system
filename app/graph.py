
"""
Graph DAG 编排引擎：管理 Agent 工作流的 DAG 拓扑、并行执行、条件分支。

核心概念：
- GraphNode: 一个可执行节点（Agent调用或数据处理）
- GraphEdge: 有向边，表示数据依赖
- GraphOrchestrator: 执行引擎，按拓扑顺序调度节点

特性：
- JD解析和简历解析 并行执行
- 条件分支（基于匹配分数决定后续路径）
- 显式数据传递（节点间通过返回值传递，不依赖全局状态）
- 内建 Harness 包裹每个节点执行
"""

from __future__ import annotations
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum

from .harness import AgentHarness, HarnessResult


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class GraphNode:
    """DAG 中的一个节点"""
    name: str
    fn: Callable                           # 执行函数 fn(inputs: dict) -> Any
    harness: Optional[AgentHarness] = None # 执行护栏（可选）
    depends_on: list[str] = field(default_factory=list)  # 依赖的节点名
    condition: Optional[Callable] = None   # 条件分支 fn(inputs) -> str (下一个节点名)
    timeout: int = 120                     # 超时（秒）
    metadata: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    """DAG 中的有向边"""
    from_node: str
    to_node: str
    data_key: Optional[str] = None  # 从from_node结果中提取哪个字段传给to_node


@dataclass
class NodeResult:
    """节点执行结果"""
    node_name: str
    status: NodeStatus
    output: Any = None
    error: Optional[str] = None
    harness_result: Optional[HarnessResult] = None
    duration_ms: float = 0
    timestamp: float = field(default_factory=time.time)


class GraphOrchestrator:
    """
    DAG 编排器：按拓扑顺序执行节点，支持并行和条件分支。

    Usage:
        graph = GraphOrchestrator()
        graph.add_node(GraphNode(name="parse_jd", fn=parse_jd_fn, harness=harness))
        graph.add_node(GraphNode(name="parse_resume", fn=parse_resume_fn, harness=harness))
        graph.add_node(GraphNode(name="match", fn=match_fn, depends_on=["parse_jd", "parse_resume"]))
        results = graph.run(initial_input={"jd_text": "...", "resume_text": "..."})
    """

    def __init__(self, name: str = "recruitment-pipeline", max_workers: int = 4):
        self.name = name
        self.max_workers = max_workers
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []
        self.results: dict[str, NodeResult] = {}
        # 全局数据池：节点产出存入这里，下游节点从这里取
        self.data_pool: dict[str, Any] = {}
        # 执行日志
        self.execution_log: list[dict] = []

    # ── 构建 API ──────────────────────────────────────

    def add_node(self, node: GraphNode) -> "GraphOrchestrator":
        self.nodes[node.name] = node
        return self

    def add_edge(self, from_node: str, to_node: str, data_key: str = None) -> "GraphOrchestrator":
        self.edges.append(GraphEdge(from_node, to_node, data_key))
        # 自动添加依赖关系
        if to_node in self.nodes:
            node = self.nodes[to_node]
            if from_node not in node.depends_on:
                node.depends_on.append(from_node)
        return self

    def _topological_sort(self) -> list[list[str]]:
        """
        Kahn 算法拓扑排序，返回分层列表（同层可并行）。
        [[layer0_nodes], [layer1_nodes], ...]
        """
        in_degree = {name: 0 for name in self.nodes}
        adj = {name: [] for name in self.nodes}

        for node in self.nodes.values():
            for dep in node.depends_on:
                if dep in self.nodes:
                    in_degree[node.name] += 1
                    adj[dep].append(node.name)

        queue = deque([name for name, deg in in_degree.items() if deg == 0])
        layers = []

        while queue:
            layer = list(queue)
            layers.append(layer)
            next_queue = deque()
            for name in layer:
                for neighbor in adj[name]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            queue = next_queue

        # 检查是否有环
        processed = sum(len(L) for L in layers)
        if processed != len(self.nodes):
            unprocessed = [n for n, d in in_degree.items() if d > 0]
            raise ValueError(f"Graph has a cycle! Unprocessed nodes: {unprocessed}")

        return layers

    # ── 执行引擎 ──────────────────────────────────────

    def run(self, initial_input: dict = None) -> dict[str, NodeResult]:
        """
        执行整个 DAG。

        Args:
            initial_input: 初始输入数据（注入到 data_pool）

        Returns:
            {node_name: NodeResult} 每个节点的执行结果
        """
        if initial_input:
            self.data_pool.update(initial_input)

        layers = self._topological_sort()
        self.execution_log.append({
            "event": "graph_start",
            "layers": [[n for n in layer] for layer in layers],
            "total_nodes": len(self.nodes),
            "timestamp": time.time(),
        })

        for layer_idx, layer in enumerate(layers):
            self._execute_layer(layer, layer_idx)

        # 处理条件分支（condition 定义的动态路由）
        self._process_conditions()

        self.execution_log.append({
            "event": "graph_end",
            "results": {n: r.status.value for n, r in self.results.items()},
            "timestamp": time.time(),
        })

        return self.results

    def _execute_layer(self, layer: list[str], layer_idx: int):
        """执行一层节点（层内并行）"""
        if len(layer) == 1:
            # 单节点直接执行
            self._execute_node(layer[0])
            return

        # 多节点并行执行
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(layer))) as executor:
            futures = {executor.submit(self._execute_node, name): name for name in layer}
            for future in as_completed(futures):
                node_name = futures[future]
                try:
                    future.result(timeout=300)
                except Exception as e:
                    self.results[node_name] = NodeResult(
                        node_name=node_name,
                        status=NodeStatus.FAILED,
                        error=str(e),
                    )

    def _execute_node(self, node_name: str):
        """执行单个节点"""
        node = self.nodes[node_name]
        t0 = time.time()

        # 构建输入：从 data_pool 中提取依赖节点的产出
        inputs = self._build_inputs(node)

        self.execution_log.append({
            "event": "node_start",
            "node": node_name,
            "input_keys": list(inputs.keys()) if inputs else [],
            "timestamp": time.time(),
        })

        try:
            # Harness 包裹执行
            if node.harness:
                result = node.harness.run(
                    agent_fn=node.fn,
                    input_data=inputs,
                    schema=node.metadata.get("output_schema"),
                )
                output = result.data
                harness_result = result
            else:
                # 无 Harness 直接执行（不推荐生产使用）
                output = node.fn(inputs)
                harness_result = None

            # 将产出写入 data_pool
            self.data_pool[node_name] = output

            duration = (time.time() - t0) * 1000

            self.results[node_name] = NodeResult(
                node_name=node_name,
                status=NodeStatus.SUCCESS,
                output=output,
                harness_result=harness_result,
                duration_ms=duration,
            )

            self.execution_log.append({
                "event": "node_success",
                "node": node_name,
                "duration_ms": duration,
                "output_type": type(output).__name__,
                "timestamp": time.time(),
            })

        except Exception as e:
            duration = (time.time() - t0) * 1000

            self.results[node_name] = NodeResult(
                node_name=node_name,
                status=NodeStatus.FAILED,
                error=str(e),
                duration_ms=duration,
            )

            self.execution_log.append({
                "event": "node_failed",
                "node": node_name,
                "error": str(e),
                "duration_ms": duration,
                "timestamp": time.time(),
            })

            # 不向上抛出，让其他节点继续执行
            # 依赖该节点的下游节点会在 _build_inputs 中检测到 FAILED 并跳过

    def _build_inputs(self, node: GraphNode) -> dict:
        """为节点构建输入数据（从 data_pool 中取依赖产出的数据）"""
        # 根节点（无依赖）直接使用全部 data_pool
        if not node.depends_on:
            return dict(self.data_pool)

        inputs = {}

        for dep in node.depends_on:
            dep_result = self.results.get(dep)
            if dep_result and dep_result.status == NodeStatus.SUCCESS:
                dep_output = dep_result.output
                # 如果只有一个依赖且输出是 dict → 展开合并（保持兼容）
                # 如果有多个依赖 → 按节点名包装，避免 key 冲突
                if len(node.depends_on) == 1 and isinstance(dep_output, dict):
                    inputs.update(dep_output)
                else:
                    # 多依赖时，按节点名作为 namespace
                    # 同时在顶层也放一份（向下兼容）
                    if isinstance(dep_output, dict):
                        inputs[dep] = dep_output
                        # 对于 parse_jd/parse_resume 这种，也展开到顶层
                        if dep in ("parse_jd", "parse_resume"):
                            inputs.update(dep_output)
                    else:
                        inputs[dep] = dep_output
            elif dep in self.data_pool:
                inputs[dep] = self.data_pool[dep]

        return inputs

    def _process_conditions(self):
        """处理条件分支：根据 condition 函数动态路由"""
        for node_name, node in self.nodes.items():
            if not node.condition:
                continue

            node_result = self.results.get(node_name)
            if not node_result or node_result.status != NodeStatus.SUCCESS:
                continue

            inputs = self._build_inputs(node)
            try:
                next_node = node.condition(inputs)
                if next_node:
                    self.execution_log.append({
                        "event": "condition_routed",
                        "from": node_name,
                        "to": next_node,
                        "timestamp": time.time(),
                    })
            except Exception as e:
                self.execution_log.append({
                    "event": "condition_error",
                    "node": node_name,
                    "error": str(e),
                    "timestamp": time.time(),
                })

    # ── 查询 API ──────────────────────────────────────

    def get_result(self, node_name: str) -> Optional[NodeResult]:
        return self.results.get(node_name)

    def get_output(self, node_name: str) -> Any:
        r = self.results.get(node_name)
        return r.output if r else None

    def get_execution_summary(self) -> dict:
        """获取执行摘要"""
        total = len(self.results)
        success = sum(1 for r in self.results.values() if r.status == NodeStatus.SUCCESS)
        failed = sum(1 for r in self.results.values() if r.status == NodeStatus.FAILED)
        total_duration = sum(r.duration_ms for r in self.results.values())
        return {
            "graph_name": self.name,
            "total_nodes": total,
            "success": success,
            "failed": failed,
            "total_duration_ms": total_duration,
            "details": {
                name: {"status": r.status.value, "duration_ms": r.duration_ms}
                for name, r in self.results.items()
            },
        }

    def print_dag(self) -> str:
        """打印 DAG 结构（Mermaid 格式）"""
        lines = ["graph TD"]
        for node_name, node in self.nodes.items():
            label = node.metadata.get("label", node_name)
            lines.append(f"    {node_name}[{label}]")
            for dep in node.depends_on:
                lines.append(f"    {dep} --> {node_name}")
        return "\n".join(lines)
