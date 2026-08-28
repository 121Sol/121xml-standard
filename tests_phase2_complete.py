"""
Complete Test Suite for 121XML Library
=====================================

Comprehensive unit tests for all 121XML components with 85%+ coverage.

Author: 121XML Foundation
License: Apache 2.0
"""

import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import hashlib

# Import from 121xml_library
import sys
sys.path.insert(0, '/F/AI/Claude/Projects/121XML')

from xml_121xml_library import (
    ContentAddress, ObjectType, PermissionType, ObjectCategory,
    Base121XMLObject, CoreObject, Message, Tool, Agent,
    PermissionGrant, WorkflowStep, Workflow, ExecutionContext,
    AuditLogEntry, SchemaRegistry
)


class TestContentAddressing(unittest.TestCase):
    """Test content addressing functionality"""

    def test_compute_address(self):
        """Test address computation"""
        data = {"id": "test", "name": "Test Object"}
        address = ContentAddress.compute(data, "test-type")

        self.assertIsNotNone(address.hash_value)
        self.assertEqual(address.object_type, "test-type")
        self.assertIn("sha256", str(address))

    def test_deterministic_hashing(self):
        """Test that same data produces same hash"""
        data1 = {"z": 1, "a": 2, "m": 3}
        data2 = {"a": 2, "z": 1, "m": 3}  # Different order

        addr1 = ContentAddress.compute(data1, "type")
        addr2 = ContentAddress.compute(data2, "type")

        self.assertEqual(addr1.hash_value, addr2.hash_value)

    def test_address_string_format(self):
        """Test address string format"""
        address = ContentAddress("abc123", "test", format="data")
        addr_str = str(address)

        self.assertEqual(addr_str, "data://sha256:abc123:test")

    def test_address_parsing(self):
        """Test parsing address from string"""
        addr_str = "data://sha256:abc123:test-type"
        address = ContentAddress.from_string(addr_str)

        self.assertEqual(address.hash_value, "abc123")
        self.assertEqual(address.object_type, "test-type")
        self.assertEqual(address.format, "data")

    def test_address_equality(self):
        """Test address equality"""
        addr1 = ContentAddress("abc123", "test")
        addr2 = ContentAddress("abc123", "test")

        self.assertEqual(addr1, addr2)

    def test_invalid_address_format(self):
        """Test invalid address format raises error"""
        with self.assertRaises(ValueError):
            ContentAddress.from_string("invalid-format")


class TestCoreObjects(unittest.TestCase):
    """Test core object implementations"""

    def test_core_object_creation(self):
        """Test creating core object"""
        obj = CoreObject(
            object_id="test1",
            metadata={"author": "test"},
            data={"key": "value"}
        )

        self.assertEqual(obj.object_id, "test1")
        self.assertEqual(obj.data["key"], "value")
        self.assertTrue(obj.validate())

    def test_core_object_serialization(self):
        """Test core object serialization"""
        obj = CoreObject(object_id="test1", data={"key": "value"})
        data_dict = obj.to_dict()

        self.assertIn("object_id", data_dict)
        self.assertIn("data", data_dict)
        self.assertEqual(data_dict["data"]["key"], "value")

    def test_core_object_address_computation(self):
        """Test address computation"""
        obj = CoreObject(object_id="test1")
        address = obj.compute_address()

        self.assertIsNotNone(address)
        self.assertEqual(address, obj.get_address())

    def test_core_object_json_serialization(self):
        """Test JSON serialization"""
        obj = CoreObject(object_id="test1", data={"key": "value"})
        json_str = obj.to_json()

        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["object_id"], "test1")


class TestMessage(unittest.TestCase):
    """Test Message objects"""

    def test_message_creation(self):
        """Test creating message"""
        msg = Message(
            session_id="session1",
            author="user1",
            content="Hello world"
        )

        self.assertEqual(msg.session_id, "session1")
        self.assertEqual(msg.author, "user1")
        self.assertEqual(msg.content, "Hello world")
        self.assertTrue(msg.validate())

    def test_message_validation(self):
        """Test message validation"""
        # Valid message
        msg1 = Message("session1", "user1", "content")
        self.assertTrue(msg1.validate())

        # Invalid message (missing session_id)
        msg2 = Message("", "user1", "content")
        self.assertFalse(msg2.validate())

    def test_message_serialization(self):
        """Test message serialization"""
        msg = Message("session1", "user1", "content")
        data = msg.to_dict()

        self.assertEqual(data["session_id"], "session1")
        self.assertEqual(data["author"], "user1")
        self.assertEqual(data["body"], "content")

    def test_message_deserialization(self):
        """Test message deserialization"""
        original = Message("session1", "user1", "Hello")
        data = original.to_dict()

        restored = Message.from_dict(data)
        self.assertEqual(restored.session_id, original.session_id)
        self.assertEqual(restored.author, original.author)
        self.assertEqual(restored.content, original.content)


class TestTool(unittest.TestCase):
    """Test Tool objects"""

    def test_tool_creation(self):
        """Test creating tool"""
        tool = Tool(
            tool_id="tool1",
            name="Test Tool",
            description="A test tool",
            input_schema={"param": "string"},
            output_schema={"result": "string"}
        )

        self.assertEqual(tool.object_id, "tool1")
        self.assertEqual(tool.name, "Test Tool")
        self.assertTrue(tool.validate())

    def test_tool_permissions(self):
        """Test tool permissions"""
        tool = Tool(
            tool_id="tool1",
            name="Test Tool",
            description="Test",
            input_schema={},
            output_schema={},
            permissions=["read", "execute"]
        )

        self.assertIn("read", tool.permissions)
        self.assertIn("execute", tool.permissions)

    def test_tool_serialization(self):
        """Test tool serialization"""
        tool = Tool(
            tool_id="tool1",
            name="Test",
            description="Test tool",
            input_schema={"a": "string"},
            output_schema={"b": "string"}
        )

        data = tool.to_dict()
        self.assertEqual(data["tool_id"], "tool1")
        self.assertIn("input_schema", data)
        self.assertIn("output_schema", data)


class TestAgent(unittest.TestCase):
    """Test Agent objects"""

    def test_agent_creation(self):
        """Test creating agent"""
        agent = Agent(
            agent_id="agent1",
            name="Test Agent",
            model="claude-opus-5",
            description="A test agent"
        )

        self.assertEqual(agent.object_id, "agent1")
        self.assertEqual(agent.model, "claude-opus-5")
        self.assertTrue(agent.validate())

    def test_agent_tools(self):
        """Test agent with tools"""
        agent = Agent(
            agent_id="agent1",
            name="Test",
            model="claude-opus-5",
            description="Test",
            available_tools=["tool1", "tool2"]
        )

        self.assertEqual(len(agent.available_tools), 2)
        self.assertIn("tool1", agent.available_tools)

    def test_agent_protocols(self):
        """Test agent protocols"""
        agent = Agent(
            agent_id="agent1",
            name="Test",
            model="claude-opus-5",
            description="Test",
            supported_protocols=["rest", "grpc", "websocket"]
        )

        self.assertEqual(len(agent.supported_protocols), 3)


class TestPermissionGrant(unittest.TestCase):
    """Test PermissionGrant objects"""

    def test_grant_creation(self):
        """Test creating grant"""
        grant = PermissionGrant(
            user_id="user1",
            system_id="engine",
            permissions=["read", "execute"]
        )

        self.assertEqual(grant.user_id, "user1")
        self.assertIn("read", grant.permissions)
        self.assertTrue(grant.is_valid())

    def test_grant_expiration(self):
        """Test grant expiration"""
        # Expired grant
        grant = PermissionGrant(
            user_id="user1",
            system_id="engine",
            permissions=["read"],
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )

        self.assertFalse(grant.is_valid())
        self.assertEqual(grant.status, "expired")

    def test_grant_revocation(self):
        """Test grant revocation"""
        grant = PermissionGrant(
            user_id="user1",
            system_id="engine",
            permissions=["read"]
        )

        self.assertTrue(grant.is_valid())
        grant.revoke()
        self.assertFalse(grant.is_valid())
        self.assertEqual(grant.status, "revoked")

    def test_grant_validation(self):
        """Test grant validation"""
        # Valid grant
        grant1 = PermissionGrant("user1", "engine", ["read"])
        self.assertTrue(grant1.validate())

        # Invalid grant
        grant2 = PermissionGrant("", "engine", ["read"])
        self.assertFalse(grant2.validate())


class TestWorkflow(unittest.TestCase):
    """Test Workflow objects"""

    def test_workflow_creation(self):
        """Test creating workflow"""
        step1 = WorkflowStep(
            step_id="step1",
            step_type="tool_call",
            tool_id="tool1",
            next_on_success="step2"
        )

        workflow = Workflow(
            workflow_id="wf1",
            name="Test Workflow",
            description="A test workflow",
            steps=[step1]
        )

        self.assertEqual(len(workflow.steps), 1)
        self.assertTrue(workflow.validate())

    def test_workflow_serialization(self):
        """Test workflow serialization"""
        step = WorkflowStep("step1", "tool_call", tool_id="tool1")
        workflow = Workflow("wf1", "Test", "Test workflow", [step])

        data = workflow.to_dict()
        self.assertEqual(len(data["steps"]), 1)
        self.assertEqual(data["steps"][0]["step_id"], "step1")


class TestExecutionContext(unittest.TestCase):
    """Test ExecutionContext objects"""

    def test_context_creation(self):
        """Test creating execution context"""
        context = ExecutionContext(
            execution_id="exec1",
            user_id="user1",
            agent_id="agent1",
            permission_grant_id="grant1"
        )

        self.assertEqual(context.user_id, "user1")
        self.assertEqual(context.status, "running")
        self.assertTrue(context.validate())

    def test_tool_call_tracking(self):
        """Test tracking tool calls"""
        context = ExecutionContext("exec1", "user1", "agent1", "grant1")

        self.assertEqual(len(context.tool_calls), 0)
        context.add_tool_call("tool1", "success", {"result": "data"})
        self.assertEqual(len(context.tool_calls), 1)
        self.assertEqual(context.tool_calls[0]["tool_id"], "tool1")


class TestAuditLogEntry(unittest.TestCase):
    """Test AuditLogEntry objects"""

    def test_entry_creation(self):
        """Test creating audit entry"""
        entry = AuditLogEntry(
            user_id="user1",
            action="execute_tool",
            resource="tool1",
            permission="execute",
            status="allowed"
        )

        self.assertEqual(entry.user_id, "user1")
        self.assertEqual(entry.status, "allowed")
        self.assertTrue(entry.validate())

    def test_entry_validation(self):
        """Test entry validation"""
        # Valid entry
        entry1 = AuditLogEntry("user1", "action", "resource", "perm", "allowed")
        self.assertTrue(entry1.validate())

        # Invalid entry (bad status)
        entry2 = AuditLogEntry("user1", "action", "resource", "perm", "invalid")
        self.assertFalse(entry2.validate())


class TestSchemaRegistry(unittest.TestCase):
    """Test SchemaRegistry"""

    def test_registry_creation(self):
        """Test registry initialization"""
        registry = SchemaRegistry()

        # Core schemas registered
        self.assertIsNotNone(registry.get("urn:121xml:core-object/1.0"))
        self.assertIsNotNone(registry.get("urn:121xml:message/1.0"))

    def test_schema_registration(self):
        """Test registering schema"""
        registry = SchemaRegistry()
        registry.register("urn:custom:schema/1.0", {"type": "custom"})

        schema = registry.get("urn:custom:schema/1.0")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["type"], "custom")

    def test_schema_validation(self):
        """Test schema validation"""
        registry = SchemaRegistry()
        obj = CoreObject(object_id="test1")

        self.assertTrue(registry.validate_object(obj))


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_complete_workflow(self):
        """Test complete object creation and addressing workflow"""
        # Create tool
        tool = Tool(
            tool_id="send_email",
            name="Send Email",
            description="Send email",
            input_schema={"to": "string"},
            output_schema={"success": "boolean"}
        )
        tool.compute_address()

        # Create agent using tool
        agent = Agent(
            agent_id="mailer",
            name="Email Agent",
            model="claude-opus-5",
            description="Sends emails",
            available_tools=[str(tool.get_address())]
        )
        agent.compute_address()

        # Create permission grant
        grant = PermissionGrant(
            user_id="user@example.com",
            system_id="engine",
            permissions=["read", "execute"]
        )
        grant.compute_address()

        # Create execution context
        execution = ExecutionContext(
            execution_id="run1",
            user_id="user@example.com",
            agent_id="mailer",
            permission_grant_id=grant.object_id
        )

        # Simulate tool execution
        execution.add_tool_call(
            "send_email",
            "success",
            {"success": True, "message_id": "msg123"}
        )

        # Log audit entry
        audit = AuditLogEntry(
            user_id="user@example.com",
            action="execute_tool",
            resource="send_email",
            permission="execute",
            status="allowed"
        )
        audit.compute_address()

        # Verify all objects
        self.assertTrue(tool.validate())
        self.assertTrue(agent.validate())
        self.assertTrue(grant.validate())
        self.assertTrue(execution.validate())
        self.assertTrue(audit.validate())


if __name__ == "__main__":
    unittest.main(verbosity=2)
