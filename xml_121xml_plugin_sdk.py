"""
121XML Agentic Operating System - Plugin SDK
==============================================

Framework for developing custom plugins (protocol adapters, schema translators, tools).
Author: 121XML Foundation
License: Apache 2.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import json


# ============================================================================
# PLUGIN TYPES & INTERFACES
# ============================================================================

class PluginType(Enum):
    """Types of plugins"""
    PROTOCOL_ADAPTER = "protocol_adapter"
    SCHEMA_TRANSLATOR = "schema_translator"
    TOOL = "tool"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    plugin_id: str
    plugin_type: PluginType
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def to_121xml_profile(self) -> Dict[str, Any]:
        """Convert to 121XML profile"""
        return {
            "profile": "urn:121xml:plugin/1.0",
            "plugin_id": self.plugin_id,
            "plugin_type": self.plugin_type.value,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "dependencies": self.dependencies
        }


class PluginBase(ABC):
    """Base class for all plugins"""

    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize plugin - return True if successful"""
        pass

    @abstractmethod
    def shutdown(self):
        """Shutdown plugin - cleanup resources"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate plugin integrity"""
        pass

    def get_profile(self) -> Dict[str, Any]:
        """Get plugin profile as 121XML"""
        return self.metadata.to_121xml_profile()


# ============================================================================
# PROTOCOL ADAPTER PLUGIN
# ============================================================================

class ProtocolAdapterPlugin(PluginBase):
    """Base class for protocol adapter plugins"""

    @abstractmethod
    def get_protocol_name(self) -> str:
        """Get protocol name (e.g., 'rest', 'grpc', 'mqtt')"""
        pass

    @abstractmethod
    def get_supported_versions(self) -> List[str]:
        """Get supported protocol versions"""
        pass

    @abstractmethod
    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert incoming request to 121XML"""
        pass

    @abstractmethod
    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to protocol format"""
        pass

    def get_capabilities(self) -> List[str]:
        return [
            "convert_to_121xml",
            "convert_from_121xml",
            f"protocol:{self.get_protocol_name()}"
        ]

    def get_profile(self) -> Dict[str, Any]:
        """Get protocol adapter profile"""
        profile = super().get_profile()
        profile.update({
            "protocol_name": self.get_protocol_name(),
            "supported_versions": self.get_supported_versions()
        })
        return profile


# ============================================================================
# SCHEMA TRANSLATOR PLUGIN
# ============================================================================

class SchemaTranslatorPlugin(PluginBase):
    """Base class for schema translator plugins"""

    @abstractmethod
    def get_schema_type(self) -> str:
        """Get schema type (e.g., 'json', 'protobuf', 'graphql')"""
        pass

    @abstractmethod
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """Validate schema definition"""
        pass

    @abstractmethod
    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert incoming data to 121XML"""
        pass

    @abstractmethod
    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert 121XML data to target schema"""
        pass

    def get_capabilities(self) -> List[str]:
        return [
            "translate_to_121xml",
            "translate_from_121xml",
            f"schema:{self.get_schema_type()}"
        ]

    def get_profile(self) -> Dict[str, Any]:
        """Get schema translator profile"""
        profile = super().get_profile()
        profile.update({
            "schema_type": self.get_schema_type(),
            "bidirectional": True
        })
        return profile


# ============================================================================
# TOOL PLUGIN
# ============================================================================

@dataclass
class ToolCapability:
    """Tool capability definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions: List[str]


class ToolPlugin(PluginBase):
    """Base class for tool plugins"""

    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        self.capabilities: Dict[str, ToolCapability] = {}

    @abstractmethod
    def get_tools(self) -> List[str]:
        """Get list of tool names provided by this plugin"""
        pass

    @abstractmethod
    def get_tool_capability(self, tool_name: str) -> Optional[ToolCapability]:
        """Get capability definition for tool"""
        pass

    @abstractmethod
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool and return result"""
        pass

    def get_capabilities(self) -> List[str]:
        return [f"tool:{name}" for name in self.get_tools()]

    def get_profile(self) -> Dict[str, Any]:
        """Get tool plugin profile"""
        profile = super().get_profile()
        profile.update({
            "tools": self.get_tools(),
            "tool_capabilities": {
                name: {
                    "name": cap.name,
                    "description": cap.description,
                    "input_schema": cap.input_schema,
                    "output_schema": cap.output_schema,
                    "permissions": cap.permissions
                }
                for name, cap in self.capabilities.items()
            }
        })
        return profile


# ============================================================================
# COMPLIANCE PLUGIN
# ============================================================================

class CompliancePlugin(PluginBase):
    """Base class for compliance plugins"""

    @abstractmethod
    def get_compliance_standards(self) -> List[str]:
        """Get compliance standards (e.g., 'GDPR', 'HIPAA', 'CCPA')"""
        pass

    @abstractmethod
    def check_compliance(self, data: Dict[str, Any], standard: str) -> Dict[str, Any]:
        """Check if data meets compliance standard"""
        pass

    @abstractmethod
    def sanitize(self, data: Dict[str, Any], standard: str) -> Dict[str, Any]:
        """Sanitize data to meet compliance standard"""
        pass

    def get_capabilities(self) -> List[str]:
        return [f"compliance:{s}" for s in self.get_compliance_standards()]

    def get_profile(self) -> Dict[str, Any]:
        """Get compliance plugin profile"""
        profile = super().get_profile()
        profile.update({
            "standards": self.get_compliance_standards()
        })
        return profile


# ============================================================================
# PLUGIN REGISTRY & LOADER
# ============================================================================

class PluginRegistry:
    """Registry for managing plugins"""

    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_metadata: Dict[str, Dict[str, Any]] = {}

    def register(self, plugin: PluginBase) -> bool:
        """Register plugin"""
        if not plugin.validate():
            return False

        if not plugin.initialize():
            return False

        self.plugins[plugin.metadata.plugin_id] = plugin
        self.plugin_metadata[plugin.metadata.plugin_id] = plugin.get_profile()
        return True

    def unregister(self, plugin_id: str):
        """Unregister plugin"""
        plugin = self.plugins.get(plugin_id)
        if plugin:
            plugin.shutdown()
            del self.plugins[plugin_id]
            del self.plugin_metadata[plugin_id]

    def get_plugin(self, plugin_id: str) -> Optional[PluginBase]:
        """Get plugin by ID"""
        return self.plugins.get(plugin_id)

    def find_by_type(self, plugin_type: PluginType) -> List[PluginBase]:
        """Find plugins by type"""
        return [p for p in self.plugins.values() if p.metadata.plugin_type == plugin_type]

    def find_by_capability(self, capability: str) -> List[PluginBase]:
        """Find plugins with specific capability"""
        return [p for p in self.plugins.values() if capability in p.get_capabilities()]

    def get_all_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all plugin profiles"""
        return self.plugin_metadata.copy()


# ============================================================================
# EXAMPLE PLUGINS
# ============================================================================

class RESTProtocolPlugin(ProtocolAdapterPlugin):
    """Example REST protocol adapter plugin"""

    def __init__(self):
        metadata = PluginMetadata(
            plugin_id="plugin_rest_protocol",
            plugin_type=PluginType.PROTOCOL_ADAPTER,
            name="REST Protocol Adapter",
            version="1.0.0",
            author="121XML Foundation",
            description="HTTP/REST protocol adapter for 121XML"
        )
        super().__init__(metadata)

    def initialize(self) -> bool:
        return True

    def shutdown(self):
        pass

    def validate(self) -> bool:
        return True

    def get_protocol_name(self) -> str:
        return "rest"

    def get_supported_versions(self) -> List[str]:
        return ["1.0", "1.1", "2.0"]

    def to_121xml(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert REST request to 121XML"""
        return {
            "protocol": "rest",
            "method": request.get("method", "GET"),
            "path": request.get("path", "/"),
            "headers": request.get("headers", {}),
            "body": request.get("body", {}),
            "query_params": request.get("query_params", {})
        }

    def from_121xml(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert 121XML response to REST"""
        return {
            "status_code": response.get("status_code", 200),
            "headers": response.get("headers", {}),
            "body": response.get("body", {})
        }


class JSONSchemaPlugin(SchemaTranslatorPlugin):
    """Example JSON Schema translator plugin"""

    def __init__(self):
        metadata = PluginMetadata(
            plugin_id="plugin_json_schema",
            plugin_type=PluginType.SCHEMA_TRANSLATOR,
            name="JSON Schema Translator",
            version="1.0.0",
            author="121XML Foundation",
            description="JSON Schema translator for 121XML"
        )
        super().__init__(metadata)

    def initialize(self) -> bool:
        return True

    def shutdown(self):
        pass

    def validate(self) -> bool:
        return True

    def get_schema_type(self) -> str:
        return "json"

    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        return "$schema" in schema or "type" in schema

    def to_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert JSON data to 121XML"""
        return {
            "schema_type": "json",
            "data": data,
            "schema": schema or {}
        }

    def from_121xml(self, data: Dict[str, Any], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Convert 121XML to JSON"""
        return data.get("data", data)


class EmailToolPlugin(ToolPlugin):
    """Example email tool plugin"""

    def __init__(self):
        metadata = PluginMetadata(
            plugin_id="plugin_email_tools",
            plugin_type=PluginType.TOOL,
            name="Email Tools",
            version="1.0.0",
            author="121XML Foundation",
            description="Email sending and management tools"
        )
        super().__init__(metadata)

        # Define capabilities
        self.capabilities["send_email"] = ToolCapability(
            name="send_email",
            description="Send email message",
            input_schema={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "cc": {"type": "array", "items": {"type": "string"}},
                    "bcc": {"type": "array", "items": {"type": "string"}}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message_id": {"type": "string"}
                }
            },
            permissions=["execute"]
        )

    def initialize(self) -> bool:
        return True

    def shutdown(self):
        pass

    def validate(self) -> bool:
        return len(self.capabilities) > 0

    def get_tools(self) -> List[str]:
        return list(self.capabilities.keys())

    def get_tool_capability(self, tool_name: str) -> Optional[ToolCapability]:
        return self.capabilities.get(tool_name)

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool"""
        if tool_name == "send_email":
            # Simulate email sending
            import uuid
            return {
                "success": True,
                "message_id": str(uuid.uuid4()),
                "to": parameters.get("to"),
                "subject": parameters.get("subject")
            }
        return {"error": f"Unknown tool: {tool_name}"}


# ============================================================================
# PLUGIN EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create registry
    registry = PluginRegistry()

    # Register plugins
    rest_plugin = RESTProtocolPlugin()
    json_plugin = JSONSchemaPlugin()
    email_plugin = EmailToolPlugin()

    registry.register(rest_plugin)
    registry.register(json_plugin)
    registry.register(email_plugin)

    # List all plugins
    print("Registered Plugins:")
    profiles = registry.get_all_profiles()
    for plugin_id, profile in profiles.items():
        print(f"\n{profile['name']} (v{profile['version']})")
        print(f"  Type: {profile['plugin_type']}")
        print(f"  Description: {profile['description']}")
        print(f"  Capabilities: {', '.join(profile.get('capabilities', []))}")

    # Find plugins by type
    print("\n\nProtocol Adapters:")
    protocol_plugins = registry.find_by_type(PluginType.PROTOCOL_ADAPTER)
    for plugin in protocol_plugins:
        print(f"  - {plugin.metadata.name}")

    # Execute tool
    print("\n\nExecuting Tool:")
    email_plugin_instance = registry.get_plugin("plugin_email_tools")
    result = email_plugin_instance.execute("send_email", {
        "to": "user@example.com",
        "subject": "Test",
        "body": "This is a test email"
    })
    print(f"Send Email Result: {json.dumps(result, indent=2)}")
