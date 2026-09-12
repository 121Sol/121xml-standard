# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121XML Agent Orchestrator & Tool Dispatcher
Intelligent routing and orchestration of AI agents and tools

Version: 1.0.0
License: Proprietary - 121 Group
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import uuid


class AgentRole(Enum):
    """Agent roles in the system"""
    PRIMARY = "primary"  # Main responder
    SPECIALIST = "specialist"  # Domain expert
    VALIDATOR = "validator"  # Quality checker
    EXECUTOR = "executor"  # Action performer
    AGGREGATOR = "aggregator"  # Result combiner
    MONITOR = "monitor"  # Oversight


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    BACKGROUND = 1


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class Tool:
    """Tool specification"""
    name: str
    description: str
    category: str
    required_permissions: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_count: int = 3
    cost_estimate: float = 0.0


@dataclass
class Agent:
    """Agent specification"""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    role: AgentRole = AgentRole.SPECIALIST
    capabilities: List[str] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    model: str = "claude"
    expertise_domains: List[str] = field(default_factory=list)
    success_rate: float = 0.95  # Historical success rate
    average_response_time_ms: float = 1000.0
    max_concurrent_tasks: int = 10
    current_task_count: int = 0
    is_available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task to be executed"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    deadline: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: float = 0.0
    error_message: str = ""
    result_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Plan for task execution"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    agents: List[Agent] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)
    steps: List[Dict[str, Any]] = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_time_ms: float = 0.0
    confidence_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolRegistry:
    """Registry of available tools"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._initialize_default_tools()

    def _initialize_default_tools(self):
        """Initialize default tools"""
        self.register_tool(Tool(
            name="format_converter",
            description="Convert between data formats (SWIFT, ISO20022, JSON, etc.)",
            category="data_processing",
            required_permissions=["data_read", "data_write"],
            input_schema={"source_format": "string", "target_format": "string", "data": "string"},
            output_schema={"success": "boolean", "converted_data": "string"}
        ))

        self.register_tool(Tool(
            name="content_addresser",
            description="Generate content addresses and verify integrity",
            category="data_integrity",
            required_permissions=["data_read"],
            input_schema={"content": "string", "content_type": "string"},
            output_schema={"address": "string", "hash": "string"}
        ))

        self.register_tool(Tool(
            name="data_compressor",
            description="Compress data losslessly with 94% savings",
            category="data_optimization",
            required_permissions=["data_read", "data_write"],
            input_schema={"data": "string", "aggressiveness": "integer"},
            output_schema={"compressed": "string", "ratio": "float"}
        ))

        self.register_tool(Tool(
            name="database_query",
            description="Query any supported database",
            category="data_access",
            required_permissions=["database_read"],
            input_schema={"database": "string", "query": "string"},
            output_schema={"rows": "array", "row_count": "integer"}
        ))

        self.register_tool(Tool(
            name="audit_logger",
            description="Log operations for compliance and auditing",
            category="compliance",
            required_permissions=["audit_write"],
            input_schema={"event_type": "string", "details": "object"},
            output_schema={"event_id": "string", "logged_at": "string"}
        ))

    def register_tool(self, tool: Tool):
        """Register a tool"""
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(tool_name)

    def list_tools(self, category: Optional[str] = None) -> List[Tool]:
        """List all tools, optionally filtered by category"""
        if category:
            return [t for t in self.tools.values() if t.category == category]
        return list(self.tools.values())

    def get_tools_for_task(self, required_tools: List[str]) -> List[Tool]:
        """Get specific tools for a task"""
        return [self.get_tool(name) for name in required_tools if name in self.tools]


class AgentRegistry:
    """Registry of available agents"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize default agents"""
        self.register_agent(Agent(
            name="Primary Responder",
            description="Main agent for handling requests",
            role=AgentRole.PRIMARY,
            capabilities=["conversation", "reasoning", "planning"],
            available_tools=["format_converter", "database_query"],
            expertise_domains=["general_knowledge", "finance"]
        ))

        self.register_agent(Agent(
            name="Format Specialist",
            description="Expert in format conversion and data transformation",
            role=AgentRole.SPECIALIST,
            capabilities=["format_conversion", "validation"],
            available_tools=["format_converter", "content_addresser"],
            expertise_domains=["SWIFT", "ISO20022", "HL7", "JSON"]
        ))

        self.register_agent(Agent(
            name="Data Validator",
            description="Validates data quality and integrity",
            role=AgentRole.VALIDATOR,
            capabilities=["validation", "verification"],
            available_tools=["content_addresser", "audit_logger"],
            expertise_domains=["data_quality", "compliance"]
        ))

        self.register_agent(Agent(
            name="Executor Agent",
            description="Executes transactions and performs actions",
            role=AgentRole.EXECUTOR,
            capabilities=["execution", "transaction_handling"],
            available_tools=["database_query", "audit_logger"],
            expertise_domains=["transactions", "payments"]
        ))

    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """Get all agents with specific role"""
        return [a for a in self.agents.values() if a.role == role]

    def get_available_agents(self) -> List[Agent]:
        """Get all available agents"""
        return [a for a in self.agents.values() if a.is_available]

    def find_best_agent_for_task(self, task: Task) -> Optional[Agent]:
        """Find best agent for task based on expertise and availability"""
        candidates = []

        for agent in self.get_available_agents():
            if agent.current_task_count >= agent.max_concurrent_tasks:
                continue

            # Score based on expertise and success rate
            score = agent.success_rate
            for domain in task.metadata.get("expertise_required", []):
                if domain in agent.expertise_domains:
                    score += 0.1

            candidates.append((agent, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return None


class AgentOrchestrator:
    """Orchestrates agents and tools for task execution"""

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.agent_registry = AgentRegistry()
        self.task_queue: List[Task] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.active_plans: Dict[str, ExecutionPlan] = {}

    def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        task.status = TaskStatus.QUEUED
        self.task_queue.append(task)

        # Sort by priority
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)

        return task.task_id

    def plan_execution(self, task: Task) -> Optional[ExecutionPlan]:
        """Create execution plan for task"""
        plan = ExecutionPlan(task_id=task.task_id)

        # Find suitable agents
        primary_agent = self.agent_registry.find_best_agent_for_task(task)
        if not primary_agent:
            return None

        plan.agents.append(primary_agent)

        # Find required tools
        for tool_name in task.required_tools:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                plan.tools.append(tool)
                plan.estimated_cost += tool.cost_estimate
                plan.estimated_time_ms += tool.timeout_seconds * 1000

        # Create execution steps
        plan.steps = [
            {
                "step": 1,
                "agent": primary_agent.name,
                "action": "analyze_task",
                "description": f"Analyze and plan: {task.description}"
            },
            {
                "step": 2,
                "agent": primary_agent.name,
                "tools": task.required_tools,
                "description": "Execute task using available tools"
            },
            {
                "step": 3,
                "agent": "validator",
                "action": "validate_results",
                "description": "Validate results"
            }
        ]

        # Calculate confidence
        plan.confidence_score = primary_agent.success_rate

        self.active_plans[plan.plan_id] = plan
        return plan

    def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute task according to plan"""
        import time
        start_time = time.time()

        task = next((t for t in self.task_queue if t.task_id == plan.task_id), None)
        if not task:
            return {"success": False, "error": "Task not found"}

        task.status = TaskStatus.EXECUTING
        task.started_at = datetime.utcnow().isoformat()

        try:
            # Execute each step
            results = {}
            for step in plan.steps:
                step_result = self._execute_step(step, task)
                results[f"step_{step['step']}"] = step_result

            task.status = TaskStatus.COMPLETED
            task.output_data = results
            task.result_confidence = plan.confidence_score
            task.completed_at = datetime.utcnow().isoformat()

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow().isoformat()

        task.execution_time_ms = (time.time() - start_time) * 1000

        # Log execution
        self.execution_history.append({
            "task_id": task.task_id,
            "status": task.status.value,
            "execution_time_ms": task.execution_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "success": task.status == TaskStatus.COMPLETED,
            "task_id": task.task_id,
            "results": task.output_data,
            "execution_time_ms": task.execution_time_ms,
            "confidence": task.result_confidence
        }

    def _execute_step(self, step: Dict[str, Any], task: Task) -> Dict[str, Any]:
        """Execute a single step"""
        result = {
            "step": step.get("step"),
            "status": "completed",
            "output": f"Executed {step.get('description')}"
        }

        # In production, would call actual agent/tool
        if "tools" in step:
            for tool_name in step["tools"]:
                tool = self.tool_registry.get_tool(tool_name)
                if tool:
                    result[f"tool_{tool_name}"] = {"executed": True}

        return result

    def route_to_agents(self, task: Task) -> Dict[str, Any]:
        """Route task to appropriate agents"""
        # Create plan
        plan = self.plan_execution(task)
        if not plan:
            return {"success": False, "error": "Could not create execution plan"}

        # Execute plan
        return self.execute_plan(plan)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        task = next((t for t in self.task_queue if t.task_id == task_id), None)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "assigned_agents": task.assigned_agents,
            "progress": task.execution_time_ms / 1000.0 if task.execution_time_ms > 0 else 0
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestration statistics"""
        completed_tasks = [t for t in self.task_queue if t.status == TaskStatus.COMPLETED]
        failed_tasks = [t for t in self.task_queue if t.status == TaskStatus.FAILED]

        return {
            "total_tasks": len(self.task_queue),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "success_rate": len(completed_tasks) / len(self.task_queue) if self.task_queue else 0,
            "total_agents": len(self.agent_registry.agents),
            "total_tools": len(self.tool_registry.tools),
            "average_execution_time_ms": (
                sum(t.execution_time_ms for t in completed_tasks) / len(completed_tasks)
                if completed_tasks else 0
            )
        }


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()

    # Create a task
    task = Task(
        description="Convert SWIFT payment to ISO20022",
        priority=TaskPriority.HIGH,
        required_tools=["format_converter", "content_addresser"],
        input_data={"format": "SWIFT", "target": "ISO20022"},
        metadata={"expertise_required": ["SWIFT", "ISO20022"]}
    )

    # Submit task
    task_id = orchestrator.submit_task(task)
    print(f"Task submitted: {task_id}")

    # Plan execution
    plan = orchestrator.plan_execution(task)
    print(f"Plan created: {plan.plan_id if plan else 'None'}")

    # Execute
    if plan:
        result = orchestrator.execute_plan(plan)
        print(f"Execution result: {result}")

    # Get statistics
    stats = orchestrator.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")
