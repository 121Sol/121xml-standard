# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
121XML Agentic Operating System - Core Engine Implementation
============================================================

Universal protocol and schema translation for AI agents.
Author: 121XML Foundation
License: Apache 2.0
"""

import json
import hashlib
import time
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import threading
from collections import defaultdict


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class ObjectType(Enum):
    """121XML object types"""
    MAP = "map"
    SEQUENCE = "seq"
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    NULL = "null"


class PermissionType(Enum):
    """Permission grant types"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class ContentAddress:
    """Immutable content address using SHA256"""
    hash_value: str
    object_type: str
    format: str = "data"  # Format: data://sha256:HASH:TYPE

    def __str__(self) -> str:
        return f"{self.format}://sha256:{self.hash_value}:{self.object_type}"

    @staticmethod
    def compute(content: Dict[str, Any], object_type: str) -> "ContentAddress":
        """Compute content address for 121XML object"""
        # Serialize with sorted keys for deterministic hashing
        serialized = json.dumps(content, sort_keys=True, separators=(',', ':'))
        hash_value = hashlib.sha256(serialized.encode()).hexdigest()
        return ContentAddress(hash_value, object_type)


@dataclass
class PermissionGrant:
    """User-granted permission for system access"""
    grant_id: str
    user_id: str
    system_id: str
    permissions: List[PermissionType]
    created_at: datetime
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Check if permission grant is currently valid"""
        if self.revoked_at:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    def has_permission(self, permission: PermissionType) -> bool:
        """Check if grant includes specific permission"""
        return permission in self.permissions and self.is_valid()

    def revoke(self):
        """Revoke this permission grant"""
        self.revoked_at = datetime.utcnow()


@dataclass
class AuditLogEntry:
    """Immutable audit trail entry"""
    entry_id: str
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    permission: PermissionType
    status: str  # "allowed" or "denied"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "permission": self.permission.value,
            "status": self.status,
            "metadata": self.metadata
        }


# ============================================================================
# PROTOCOL ADAPTERS
# ============================================================================

class ProtocolAdapter(ABC):
    """Base class for protocol adapters"""

    @abstractmethod
    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert incoming request to 121XML format"""
        pass

    @abstractmethod
    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to protocol format"""
        pass

    @abstractmethod
    def get_protocol_name(self) -> str:
        """Get protocol name"""
        pass


class RESTAdapter(ProtocolAdapter):
    """REST API protocol adapter"""

    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert REST request to 121XML"""
        return {
            "protocol": "rest",
            "method": request.get("method", "GET"),
            "path": request.get("path", "/"),
            "headers": request.get("headers", {}),
            "body": request.get("body", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to REST"""
        return {
            "status_code": response.get("status_code", 200),
            "headers": response.get("headers", {"Content-Type": "application/json"}),
            "body": response.get("body", {})
        }

    def get_protocol_name(self) -> str:
        return "REST"


class gRPCAdapter(ProtocolAdapter):
    """gRPC protocol adapter"""

    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert gRPC request to 121XML"""
        return {
            "protocol": "grpc",
            "service": request.get("service", ""),
            "method": request.get("method", ""),
            "message": request.get("message", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to gRPC"""
        return {
            "message": response.get("body", {}),
            "status": response.get("status", "OK")
        }

    def get_protocol_name(self) -> str:
        return "gRPC"


class WebSocketAdapter(ProtocolAdapter):
    """WebSocket protocol adapter"""

    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert WebSocket message to 121XML"""
        return {
            "protocol": "websocket",
            "event": request.get("event", ""),
            "data": request.get("data", {}),
            "timestamp": datetime.utcnow().isoformat()
        }

    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to WebSocket"""
        return {
            "event": response.get("event", "message"),
            "data": response.get("body", {})
        }

    def get_protocol_name(self) -> str:
        return "WebSocket"


# ============================================================================
# SCHEMA TRANSLATORS
# ============================================================================

class SchemaTranslator(ABC):
    """Base class for schema translators"""

    @abstractmethod
    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Translate incoming schema to 121XML"""
        pass

    @abstractmethod
    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Translate 121XML to target schema"""
        pass

    @abstractmethod
    def get_schema_type(self) -> str:
        """Get schema type name"""
        pass


class JSONSchemaTranslator(SchemaTranslator):
    """JSON Schema translator"""

    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert JSON to 121XML"""
        return {
            "schema_type": "json",
            "data": data,
            "original_schema": schema or {}
        }

    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert 121XML to JSON"""
        return data.get("data", data)

    def get_schema_type(self) -> str:
        return "JSON Schema"


class ProtobufTranslator(SchemaTranslator):
    """Protocol Buffers translator"""

    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert Protobuf to 121XML"""
        return {
            "schema_type": "protobuf",
            "data": data,
            "proto_definition": schema or {}
        }

    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert 121XML to Protobuf"""
        return data.get("data", data)

    def get_schema_type(self) -> str:
        return "Protobuf"


class GraphQLTranslator(SchemaTranslator):
    """GraphQL schema translator"""

    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert GraphQL to 121XML"""
        return {
            "schema_type": "graphql",
            "data": data,
            "graphql_schema": schema or {}
        }

    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert 121XML to GraphQL"""
        return data.get("data", data)

    def get_schema_type(self) -> str:
        return "GraphQL"


# ============================================================================
# CORE AGENTIC ENGINE
# ============================================================================

@dataclass
class ToolDefinition:
    """Definition of an agentic tool"""
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions_required: List[PermissionType]
    handler: Optional[Callable] = None

    def to_profile(self) -> Dict[str, Any]:
        """Convert to 121XML profile"""
        return {
            "profile": "urn:121xml:agentic-tool/1.0",
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "permissions_required": [p.value for p in self.permissions_required]
        }


@dataclass
class AgentDefinition:
    """Definition of an agentic agent"""
    agent_id: str
    name: str
    model: str
    description: str
    available_tools: List[str]
    supported_protocols: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_profile(self) -> Dict[str, Any]:
        """Convert to 121XML profile"""
        return {
            "profile": "urn:121xml:agentic-app-agent/1.0",
            "agent_id": self.agent_id,
            "name": self.name,
            "model": self.model,
            "description": self.description,
            "available_tools": self.available_tools,
            "supported_protocols": self.supported_protocols,
            "metadata": self.metadata
        }


@dataclass
class ExecutionContext:
    """Context for tool/agent execution"""
    execution_id: str
    user_id: str
    agent_id: str
    start_time: datetime
    permission_grant: PermissionGrant
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_calls: List[Dict] = field(default_factory=list)

    def to_121xml(self) -> Dict[str, Any]:
        """Convert to 121XML format"""
        return {
            "execution_id": self.execution_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "start_time": self.start_time.isoformat(),
            "permissions": [p.value for p in self.permission_grant.permissions],
            "metadata": self.metadata,
            "tool_calls": self.tool_calls
        }


class StateManager:
    """Manages agent state"""

    def __init__(self):
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.session_states: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.RLock()

    def set_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """Set agent state"""
        with self.lock:
            self.agent_states[agent_id] = state

    def get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Get agent state"""
        with self.lock:
            return self.agent_states.get(agent_id, {})

    def set_session_state(self, session_id: str, state: Dict[str, Any]):
        """Set session state"""
        with self.lock:
            self.session_states[session_id] = state

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state"""
        with self.lock:
            return self.session_states.get(session_id, {})


class MemoryManager:
    """Manages agent memory and context"""

    def __init__(self, max_size: int = 1000):
        self.memory: Dict[str, List[Dict]] = defaultdict(list)
        self.max_size = max_size
        self.references: Dict[str, ContentAddress] = {}

    def store(self, key: str, content: Dict[str, Any]) -> ContentAddress:
        """Store content and return address"""
        address = ContentAddress.compute(content, "memory_entry")
        self.memory[key].append({
            "address": str(address),
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Trim if exceeds max size
        if len(self.memory[key]) > self.max_size:
            self.memory[key] = self.memory[key][-self.max_size:]

        self.references[str(address)] = address
        return address

    def retrieve(self, address: str) -> Optional[Dict[str, Any]]:
        """Retrieve content by address"""
        return self.references.get(address)

    def get_context(self, key: str, limit: int = 10) -> List[Dict]:
        """Get recent context for key"""
        return self.memory[key][-limit:] if key in self.memory else []


class PermissionManager:
    """Manages user permissions and access control"""

    def __init__(self):
        self.grants: Dict[str, PermissionGrant] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.lock = threading.RLock()

    def create_grant(self, user_id: str, system_id: str,
                     permissions: List[PermissionType],
                     expires_in_hours: Optional[int] = None) -> PermissionGrant:
        """Create new permission grant"""
        grant_id = str(uuid.uuid4())
        grant = PermissionGrant(
            grant_id=grant_id,
            user_id=user_id,
            system_id=system_id,
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
                       if expires_in_hours else None
        )

        with self.lock:
            self.grants[grant_id] = grant

        return grant

    def check_permission(self, grant_id: str, permission: PermissionType) -> bool:
        """Check if grant has permission"""
        with self.lock:
            grant = self.grants.get(grant_id)
            return grant.has_permission(permission) if grant else False

    def log_access(self, user_id: str, action: str, resource: str,
                   permission: PermissionType, status: str):
        """Log access attempt"""
        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource=resource,
            permission=permission,
            status=status
        )

        with self.lock:
            self.audit_log.append(entry)

    def get_audit_log(self, user_id: Optional[str] = None) -> List[AuditLogEntry]:
        """Get audit log entries"""
        with self.lock:
            if user_id:
                return [e for e in self.audit_log if e.user_id == user_id]
            return self.audit_log.copy()


class AgenticEngine:
    """Core 121XML Agentic Engine"""

    def __init__(self):
        # Protocol adapters
        self.protocol_adapters: Dict[str, ProtocolAdapter] = {
            "rest": RESTAdapter(),
            "grpc": gRPCAdapter(),
            "websocket": WebSocketAdapter()
        }

        # Schema translators
        self.schema_translators: Dict[str, SchemaTranslator] = {
            "json": JSONSchemaTranslator(),
            "protobuf": ProtobufTranslator(),
            "graphql": GraphQLTranslator()
        }

        # Core managers
        self.state_manager = StateManager()
        self.memory_manager = MemoryManager()
        self.permission_manager = PermissionManager()

        # Registered tools and agents
        self.tools: Dict[str, ToolDefinition] = {}
        self.agents: Dict[str, AgentDefinition] = {}

        # Execution history
        self.executions: Dict[str, ExecutionContext] = {}

    def register_tool(self, tool: ToolDefinition):
        """Register a tool"""
        self.tools[tool.tool_id] = tool

    def register_agent(self, agent: AgentDefinition):
        """Register an agent"""
        self.agents[agent.agent_id] = agent

    def process_request(self, protocol: str, schema_type: str,
                        request: Dict[str, Any],
                        permission_grant: PermissionGrant) -> Dict[str, Any]:
        """Process incoming request through protocol/schema translation"""

        # Check permission
        if not permission_grant.is_valid():
            self.permission_manager.log_access(
                permission_grant.user_id,
                "process_request",
                "unknown",
                PermissionType.READ,
                "denied"
            )
            return {"error": "Permission denied or expired"}

        # Get protocol adapter
        adapter = self.protocol_adapters.get(protocol)
        if not adapter:
            return {"error": f"Unsupported protocol: {protocol}"}

        # Get schema translator
        translator = self.schema_translators.get(schema_type)
        if not translator:
            return {"error": f"Unsupported schema: {schema_type}"}

        # Convert to 121XML
        protocol_layer = adapter.to_121xml(request)
        schema_layer = translator.to_121xml(protocol_layer)

        # Log access
        self.permission_manager.log_access(
            permission_grant.user_id,
            "process_request",
            f"{protocol}:{schema_type}",
            PermissionType.READ,
            "allowed"
        )

        # Store in memory and get address
        address = self.memory_manager.store(
            f"{permission_grant.user_id}:requests",
            schema_layer
        )

        return {
            "status": "success",
            "address": str(address),
            "121xml_data": schema_layer
        }

    def execute_tool(self, tool_id: str, parameters: Dict[str, Any],
                     execution_context: ExecutionContext) -> Dict[str, Any]:
        """Execute a tool with permission checking"""

        tool = self.tools.get(tool_id)
        if not tool:
            return {"error": f"Tool not found: {tool_id}"}

        # Check permissions
        for required_perm in tool.permissions_required:
            if not execution_context.permission_grant.has_permission(required_perm):
                self.permission_manager.log_access(
                    execution_context.user_id,
                    f"execute_tool:{tool_id}",
                    tool_id,
                    required_perm,
                    "denied"
                )
                return {"error": f"Permission denied: {required_perm.value}"}

        # Execute tool
        if tool.handler:
            result = tool.handler(parameters)
        else:
            result = {"message": f"Tool {tool.name} executed successfully"}

        # Log execution
        execution_context.tool_calls.append({
            "tool_id": tool_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        })

        self.permission_manager.log_access(
            execution_context.user_id,
            f"execute_tool:{tool_id}",
            tool_id,
            PermissionType.EXECUTE,
            "allowed"
        )

        # Store result
        address = self.memory_manager.store(
            f"{execution_context.user_id}:tool_results",
            result
        )

        return {
            "status": "success",
            "result": result,
            "address": str(address)
        }

    def create_execution_context(self, user_id: str, agent_id: str,
                                 permission_grant: PermissionGrant) -> ExecutionContext:
        """Create execution context"""
        context = ExecutionContext(
            execution_id=str(uuid.uuid4()),
            user_id=user_id,
            agent_id=agent_id,
            start_time=datetime.utcnow(),
            permission_grant=permission_grant
        )
        self.executions[context.execution_id] = context
        return context

    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        return {
            "tools_registered": len(self.tools),
            "agents_registered": len(self.agents),
            "protocol_adapters": list(self.protocol_adapters.keys()),
            "schema_translators": list(self.schema_translators.keys()),
            "total_executions": len(self.executions),
            "audit_log_entries": len(self.permission_manager.audit_log)
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Initialize engine
    engine = AgenticEngine()

    # Define a tool
    email_tool = ToolDefinition(
        tool_id="tool_send_email",
        name="Send Email",
        description="Send an email to a recipient",
        input_schema={
            "to": "string",
            "subject": "string",
            "body": "string"
        },
        output_schema={
            "success": "boolean",
            "message_id": "string"
        },
        permissions_required=[PermissionType.EXECUTE],
        handler=lambda params: {
            "success": True,
            "message_id": str(uuid.uuid4())
        }
    )

    engine.register_tool(email_tool)

    # Define an agent
    agent = AgentDefinition(
        agent_id="agent_assistant",
        name="General Assistant",
        model="claude-opus-5",
        description="General purpose AI assistant",
        available_tools=["tool_send_email"],
        supported_protocols=["rest", "grpc", "websocket"]
    )

    engine.register_agent(agent)

    # Create permission grant
    grant = engine.permission_manager.create_grant(
        user_id="user_123",
        system_id="engine",
        permissions=[PermissionType.READ, PermissionType.EXECUTE],
        expires_in_hours=24
    )

    # Process request
    result = engine.process_request(
        protocol="rest",
        schema_type="json",
        request={
            "method": "POST",
            "path": "/agents/assistant/chat",
            "body": {"message": "Hello!"}
        },
        permission_grant=grant
    )

    print("Request Processing Result:")
    print(json.dumps(result, indent=2))

    # Create execution context and execute tool
    context = engine.create_execution_context(
        user_id="user_123",
        agent_id="agent_assistant",
        permission_grant=grant
    )

    tool_result = engine.execute_tool(
        tool_id="tool_send_email",
        parameters={
            "to": "test@example.com",
            "subject": "Test",
            "body": "Hello world"
        },
        execution_context=context
    )

    print("\nTool Execution Result:")
    print(json.dumps(tool_result, indent=2))

    # Show engine status
    print("\nEngine Status:")
    print(json.dumps(engine.get_status(), indent=2))

    # Show audit log
    print("\nAudit Log:")
    for entry in engine.permission_manager.get_audit_log():
        print(f"  {entry.timestamp.isoformat()} - {entry.action}: {entry.status}")
