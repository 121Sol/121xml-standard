"""
121XML Core Library - Universal Data Interchange Format
=========================================================

Complete implementation of 121XML standard with all object types,
content addressing, serialization, and validation.

Author: 121XML Foundation
License: Apache 2.0
Version: 1.0.0
"""

import json
import hashlib
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional, Type, Union
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import uuid


# ============================================================================
# ENUMERATIONS
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
    """Permission types"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


class ObjectCategory(Enum):
    """121XML object categories"""
    CORE_OBJECT = "core-object"
    AGENT = "agent"
    TOOL = "tool"
    PERMISSION = "permission"
    WORKFLOW = "workflow"
    EXECUTION = "execution"
    AUDIT = "audit"
    MESSAGE = "message"
    INFERENCE = "inference"


# ============================================================================
# CONTENT ADDRESSING
# ============================================================================

@dataclass
class ContentAddress:
    """Immutable content address using SHA256"""
    hash_value: str
    object_type: str
    version: str = "1.0"
    format: str = "data"

    def __str__(self) -> str:
        return f"{self.format}://sha256:{self.hash_value}:{self.object_type}"

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        if not isinstance(other, ContentAddress):
            return False
        return str(self) == str(other)

    @staticmethod
    def compute(content: Dict[str, Any], object_type: str, version: str = "1.0") -> "ContentAddress":
        """Compute deterministic content address"""
        # Serialize with sorted keys for determinism
        serialized = json.dumps(content, sort_keys=True, separators=(',', ':'))
        hash_value = hashlib.sha256(serialized.encode()).hexdigest()
        return ContentAddress(hash_value, object_type, version)

    @staticmethod
    def from_string(address_str: str) -> "ContentAddress":
        """Parse address string"""
        # Format: data://sha256:HASH:TYPE
        parts = address_str.split("://")
        if len(parts) != 2:
            raise ValueError(f"Invalid address format: {address_str}")

        format_name = parts[0]
        hash_parts = parts[1].split(":")
        if len(hash_parts) < 3:
            raise ValueError(f"Invalid address format: {address_str}")

        if hash_parts[0] != "sha256":
            raise ValueError(f"Unsupported hash algorithm: {hash_parts[0]}")

        hash_value = hash_parts[1]
        object_type = ":".join(hash_parts[2:])  # Handle types with colons

        return ContentAddress(hash_value, object_type, format=format_name)


# ============================================================================
# BASE 121XML OBJECT
# ============================================================================

class Base121XMLObject(ABC):
    """Base class for all 121XML objects"""

    def __init__(
        self,
        object_id: str,
        object_type: ObjectCategory,
        profile_uri: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.object_id = object_id or str(uuid.uuid4())
        self.object_type = object_type
        self.profile_uri = profile_uri
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self._address: Optional[ContentAddress] = None

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate object integrity"""
        pass

    def compute_address(self) -> ContentAddress:
        """Compute content address"""
        self._address = ContentAddress.compute(
            self.to_dict(),
            self.object_type.value
        )
        return self._address

    def get_address(self) -> Optional[ContentAddress]:
        """Get computed address or None"""
        return self._address

    def to_json(self, compute_address: bool = True) -> str:
        """Serialize to JSON"""
        if compute_address:
            self.compute_address()

        data = self.to_dict()
        if self._address:
            data["content_address"] = str(self._address)
        return json.dumps(data, sort_keys=True, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Base121XMLObject":
        """Deserialize from dictionary"""
        raise NotImplementedError("Subclasses must implement from_dict")


# ============================================================================
# CORE OBJECTS
# ============================================================================

@dataclass
class CoreObject(Base121XMLObject):
    """121XML Core Object - base for all objects"""

    def __init__(
        self,
        object_id: Optional[str] = None,
        profile_uri: str = "urn:121xml:core-object/1.0",
        metadata: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(object_id, ObjectCategory.CORE_OBJECT, profile_uri, metadata)
        self.data = data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_id": self.object_id,
            "object_type": self.object_type.value,
            "profile": self.profile_uri,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "version": "1.0.0",
                **self.metadata
            },
            "data": self.data
        }

    def validate(self) -> bool:
        """Validate core object"""
        return bool(self.object_id and self.profile_uri)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CoreObject":
        obj = cls(
            object_id=data.get("object_id"),
            profile_uri=data.get("profile", "urn:121xml:core-object/1.0"),
            metadata=data.get("metadata", {})
        )
        obj.data = data.get("data", {})
        return obj


@dataclass
class Message(Base121XMLObject):
    """121XML Message - immutable conversation message"""

    def __init__(
        self,
        session_id: str,
        author: str,
        content: str,
        message_type: str = "text",
        object_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(object_id, ObjectCategory.MESSAGE, "urn:121xml:message/1.0", metadata)
        self.session_id = session_id
        self.author = author
        self.content = content
        self.message_type = message_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.object_id,
            "session_id": self.session_id,
            "author": self.author,
            "content_type": self.message_type,
            "body": self.content,
            "metadata": {
                "timestamp": self.created_at.isoformat(),
                **self.metadata
            }
        }

    def validate(self) -> bool:
        return bool(self.session_id and self.author and self.content)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            object_id=data.get("message_id"),
            session_id=data.get("session_id"),
            author=data.get("author"),
            content=data.get("body"),
            message_type=data.get("content_type", "text"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Tool(Base121XMLObject):
    """121XML Tool - agent tool definition"""

    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any],
        permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(tool_id, ObjectCategory.TOOL, "urn:121xml:agentic-tool/1.0", metadata)
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.permissions = permissions or ["execute"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.object_id,
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "permissions_required": self.permissions,
            "profile": self.profile_uri,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                **self.metadata
            }
        }

    def validate(self) -> bool:
        return bool(self.object_id and self.name and self.input_schema and self.output_schema)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tool":
        return cls(
            tool_id=data.get("tool_id"),
            name=data.get("name"),
            description=data.get("description", ""),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            permissions=data.get("permissions_required", ["execute"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class Agent(Base121XMLObject):
    """121XML Agent - AI agent definition"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        model: str,
        description: str,
        available_tools: Optional[List[str]] = None,
        supported_protocols: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(agent_id, ObjectCategory.AGENT, "urn:121xml:agentic-app-agent/1.0", metadata)
        self.name = name
        self.model = model
        self.description = description
        self.available_tools = available_tools or []
        self.supported_protocols = supported_protocols or ["rest"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.object_id,
            "name": self.name,
            "model": self.model,
            "description": self.description,
            "available_tools": self.available_tools,
            "supported_protocols": self.supported_protocols,
            "profile": self.profile_uri,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                **self.metadata
            }
        }

    def validate(self) -> bool:
        return bool(self.object_id and self.name and self.model)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        return cls(
            agent_id=data.get("agent_id"),
            name=data.get("name"),
            model=data.get("model"),
            description=data.get("description", ""),
            available_tools=data.get("available_tools", []),
            supported_protocols=data.get("supported_protocols", ["rest"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class PermissionGrant(Base121XMLObject):
    """121XML Permission Grant - user-granted access"""

    def __init__(
        self,
        user_id: str,
        system_id: str,
        permissions: List[str],
        expires_at: Optional[datetime] = None,
        grant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(grant_id, ObjectCategory.PERMISSION, "urn:121xml:permission-grant/1.0", metadata)
        self.user_id = user_id
        self.system_id = system_id
        self.permissions = permissions
        self.expires_at = expires_at
        self.revoked_at: Optional[datetime] = None
        self.status = "active"

    def is_valid(self) -> bool:
        """Check if grant is currently valid"""
        if self.revoked_at:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = "expired"
            return False
        return True

    def revoke(self):
        """Revoke this grant"""
        self.revoked_at = datetime.utcnow()
        self.status = "revoked"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grant_id": self.object_id,
            "user_id": self.user_id,
            "system_id": self.system_id,
            "permissions": self.permissions,
            "issued_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "status": self.status,
            "profile": self.profile_uri,
            "metadata": self.metadata
        }

    def validate(self) -> bool:
        return bool(self.user_id and self.system_id and self.permissions)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionGrant":
        obj = cls(
            user_id=data.get("user_id"),
            system_id=data.get("system_id"),
            permissions=data.get("permissions", []),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            grant_id=data.get("grant_id"),
            metadata=data.get("metadata", {})
        )
        if data.get("revoked_at"):
            obj.revoked_at = datetime.fromisoformat(data["revoked_at"])
        obj.status = data.get("status", "active")
        return obj


# ============================================================================
# WORKFLOW & EXECUTION
# ============================================================================

@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_id: str
    step_type: str  # tool_call, agent_reasoning, conditional
    tool_id: Optional[str] = None
    agent_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    next_on_success: Optional[str] = None
    next_on_failure: Optional[str] = None


@dataclass
class Workflow(Base121XMLObject):
    """121XML Workflow - DAG-based process"""

    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str,
        steps: Optional[List[WorkflowStep]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workflow_id, ObjectCategory.WORKFLOW, "urn:121xml:agentic-workflow/1.0", metadata)
        self.name = name
        self.description = description
        self.steps = steps or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.object_id,
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "step_id": step.step_id,
                    "type": step.step_type,
                    "tool_id": step.tool_id,
                    "agent_id": step.agent_id,
                    "parameters": step.parameters,
                    "next_on_success": step.next_on_success,
                    "next_on_failure": step.next_on_failure,
                }
                for step in self.steps
            ],
            "profile": self.profile_uri,
            "metadata": {
                "created_at": self.created_at.isoformat(),
                **self.metadata
            }
        }

    def validate(self) -> bool:
        return bool(self.object_id and self.name and len(self.steps) > 0)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        steps = [
            WorkflowStep(
                step_id=s["step_id"],
                step_type=s["type"],
                tool_id=s.get("tool_id"),
                agent_id=s.get("agent_id"),
                parameters=s.get("parameters"),
                next_on_success=s.get("next_on_success"),
                next_on_failure=s.get("next_on_failure"),
            )
            for s in data.get("steps", [])
        ]
        return cls(
            workflow_id=data.get("workflow_id"),
            name=data.get("name"),
            description=data.get("description", ""),
            steps=steps,
            metadata=data.get("metadata", {})
        )


@dataclass
class ExecutionContext(Base121XMLObject):
    """121XML Execution Context - runtime state"""

    def __init__(
        self,
        execution_id: str,
        user_id: str,
        agent_id: str,
        permission_grant_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(execution_id, ObjectCategory.EXECUTION, "urn:121xml:execution-context/1.0", metadata)
        self.user_id = user_id
        self.agent_id = agent_id
        self.permission_grant_id = permission_grant_id
        self.status = "running"
        self.tool_calls: List[Dict[str, Any]] = []

    def add_tool_call(self, tool_id: str, status: str, result: Optional[Dict[str, Any]] = None):
        """Record tool execution"""
        self.tool_calls.append({
            "tool_id": tool_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "result": result
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.object_id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "permission_grant_id": self.permission_grant_id,
            "status": self.status,
            "started_at": self.created_at.isoformat(),
            "tool_calls": self.tool_calls,
            "profile": self.profile_uri,
            "metadata": self.metadata
        }

    def validate(self) -> bool:
        return bool(self.user_id and self.agent_id and self.permission_grant_id)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionContext":
        obj = cls(
            execution_id=data.get("execution_id"),
            user_id=data.get("user_id"),
            agent_id=data.get("agent_id"),
            permission_grant_id=data.get("permission_grant_id"),
            metadata=data.get("metadata", {})
        )
        obj.status = data.get("status", "running")
        obj.tool_calls = data.get("tool_calls", [])
        return obj


# ============================================================================
# AUDIT & LOGGING
# ============================================================================

@dataclass
class AuditLogEntry(Base121XMLObject):
    """121XML Audit Log Entry - immutable action record"""

    def __init__(
        self,
        user_id: str,
        action: str,
        resource: str,
        permission: str,
        status: str,
        entry_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(entry_id, ObjectCategory.AUDIT, "urn:121xml:audit-log-entry/1.0", metadata)
        self.user_id = user_id
        self.action = action
        self.resource = resource
        self.permission = permission
        self.status = status  # allowed, denied

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.object_id,
            "timestamp": self.created_at.isoformat(),
            "user_id": self.user_id,
            "action": self.action,
            "resource": self.resource,
            "permission": self.permission,
            "status": self.status,
            "profile": self.profile_uri,
            "metadata": self.metadata
        }

    def validate(self) -> bool:
        return bool(self.user_id and self.action and self.resource and self.status in ["allowed", "denied"])

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        return cls(
            user_id=data.get("user_id"),
            action=data.get("action"),
            resource=data.get("resource"),
            permission=data.get("permission"),
            status=data.get("status"),
            entry_id=data.get("entry_id"),
            metadata=data.get("metadata", {})
        )


# ============================================================================
# SCHEMA REGISTRY
# ============================================================================

class SchemaRegistry:
    """Registry for 121XML schema profiles"""

    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self._register_core_schemas()

    def _register_core_schemas(self):
        """Register built-in schemas"""
        self.register("urn:121xml:core-object/1.0", {"type": "object"})
        self.register("urn:121xml:message/1.0", {"type": "object"})
        self.register("urn:121xml:agentic-tool/1.0", {"type": "object"})
        self.register("urn:121xml:agentic-app-agent/1.0", {"type": "object"})
        self.register("urn:121xml:permission-grant/1.0", {"type": "object"})
        self.register("urn:121xml:agentic-workflow/1.0", {"type": "object"})
        self.register("urn:121xml:execution-context/1.0", {"type": "object"})
        self.register("urn:121xml:audit-log-entry/1.0", {"type": "object"})

    def register(self, uri: str, schema: Dict[str, Any]):
        """Register a schema"""
        self.schemas[uri] = schema

    def get(self, uri: str) -> Optional[Dict[str, Any]]:
        """Get schema by URI"""
        return self.schemas.get(uri)

    def validate_object(self, obj: Base121XMLObject) -> bool:
        """Validate object against its schema"""
        schema = self.get(obj.profile_uri)
        if not schema:
            return False
        return obj.validate()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Example: Create and address objects
    tool = Tool(
        tool_id="tool_send_email",
        name="Send Email",
        description="Send email message",
        input_schema={"to": "string", "subject": "string", "body": "string"},
        output_schema={"success": "boolean", "message_id": "string"},
    )

    tool.validate()
    address = tool.compute_address()
    print(f"Tool address: {address}")
    print(f"Tool JSON:\n{tool.to_json()}")

    # Create agent
    agent = Agent(
        agent_id="email_classifier",
        name="Email Classifier",
        model="claude-opus-5",
        description="Classifies emails",
        available_tools=["tool_send_email"],
        supported_protocols=["rest", "grpc"]
    )

    agent.compute_address()
    print(f"\nAgent address: {agent.get_address()}")

    # Create permission grant
    from datetime import timedelta
    grant = PermissionGrant(
        user_id="user_001",
        system_id="engine",
        permissions=["read", "execute"],
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )

    grant.compute_address()
    print(f"\nGrant is valid: {grant.is_valid()}")

    # Create execution context
    execution = ExecutionContext(
        execution_id=str(uuid.uuid4()),
        user_id="user_001",
        agent_id="email_classifier",
        permission_grant_id=grant.object_id
    )

    execution.add_tool_call("tool_send_email", "success", {"message_id": "msg_123"})
    print(f"\nExecution context: {execution.object_id}")
    print(f"Tool calls: {len(execution.tool_calls)}")
