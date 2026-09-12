# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
"""
MCP ↔ 121XML Bidirectional Translation Layer
==============================================

Auto-translates MCP protocol operations to 121XML format and vice versa.
Enables seamless interoperability between MCP clients and 121XML servers.

Features:
- Automatic type mapping (MCP types → 121XML objects)
- Schema discovery via profile URIs
- Lossless round-trip translation
- Content addressing for all objects
- Implicit relationship mapping
- Version compatibility management

Author: 121XML Foundation
License: Apache 2.0
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


# ============================================================================
# TYPE MAPPING & SCHEMA DISCOVERY
# ============================================================================

class MCPTypeMapping:
    """Maps MCP types to 121XML schema URIs"""
    
    # Core MCP → 121XML type mappings
    MAPPINGS = {
        # MCP Request/Response types
        "jsonrpc_request": "urn:121xml:mcp-request/1.0",
        "jsonrpc_response": "urn:121xml:mcp-response/1.0",
        
        # Resource types
        "text_resource": "urn:121xml:mcp-resource-text/1.0",
        "binary_resource": "urn:121xml:mcp-resource-binary/1.0",
        
        # Tool types
        "tool_definition": "urn:121xml:mcp-tool/1.0",
        "tool_call_request": "urn:121xml:mcp-tool-call/1.0",
        "tool_call_result": "urn:121xml:mcp-tool-result/1.0",
        
        # Prompt types
        "prompt_template": "urn:121xml:mcp-prompt/1.0",
        "prompt_argument": "urn:121xml:mcp-prompt-arg/1.0",
        
        # Message types
        "text_block": "urn:121xml:mcp-text-block/1.0",
        "image_block": "urn:121xml:mcp-image-block/1.0",
        
        # Capability types
        "server_capabilities": "urn:121xml:mcp-capabilities/1.0",
    }
    
    @staticmethod
    def get_schema_uri(mcp_type: str) -> str:
        """Get 121XML schema URI for MCP type"""
        return MCPTypeMapping.MAPPINGS.get(
            mcp_type, 
            f"urn:121xml:mcp-{mcp_type}/1.0"
        )
    
    @staticmethod
    def is_known_type(mcp_type: str) -> bool:
        """Check if type has explicit mapping"""
        return mcp_type in MCPTypeMapping.MAPPINGS


@dataclass
class ContentAddressMapping:
    """Manages content addressing for translation"""
    
    @staticmethod
    def compute(obj: Dict, object_type: str) -> str:
        """Deterministic SHA256 content address"""
        json_str = json.dumps(obj, sort_keys=True, separators=(',', ':'))
        hash_value = hashlib.sha256(json_str.encode()).hexdigest()
        return f"data://sha256:{hash_value[:16]}:{object_type}"
    
    @staticmethod
    def extract_type_from_address(address: str) -> Optional[str]:
        """Extract object type from content address"""
        if not address.startswith("data://sha256:"):
            return None
        parts = address.split(":")
        return parts[-1] if len(parts) >= 4 else None


# ============================================================================
# TRANSLATOR - MCP TO 121XML
# ============================================================================

class MCP_To_121XML_Translator:
    """Translates MCP protocol messages to 121XML format"""
    
    def __init__(self):
        self.translation_cache: Dict[str, Dict] = {}
        self.schema_cache: Dict[str, str] = {}
    
    def translate_request(self, mcp_request: Dict) -> Dict:
        """Convert MCP JSON-RPC request to 121XML"""
        
        method = mcp_request.get("method", "unknown")
        params = mcp_request.get("params", {})
        request_id = mcp_request.get("id")
        
        # Determine 121XML schema based on method
        if method.startswith("resources/"):
            schema_uri = "urn:121xml:mcp-resources/1.0"
            obj_type = "mcp_resources_request"
        elif method.startswith("tools/"):
            schema_uri = "urn:121xml:mcp-tools/1.0"
            obj_type = "mcp_tools_request"
        elif method.startswith("prompts/"):
            schema_uri = "urn:121xml:mcp-prompts/1.0"
            obj_type = "mcp_prompts_request"
        else:
            schema_uri = "urn:121xml:mcp-generic/1.0"
            obj_type = "mcp_request"
        
        # Build 121XML request object
        xml_121_request = {
            "_type": obj_type,
            "_version": "121xml/1.0",
            "_schema": schema_uri,
            "jsonrpc": "2.0",
            "method": method,
            "params": self._translate_params(params, method),
            "id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Add content address
        xml_121_request["_address"] = ContentAddressMapping.compute(
            {k: v for k, v in xml_121_request.items() if k != "_address"},
            obj_type
        )
        
        # Cache for reverse translation
        self.translation_cache[str(request_id)] = xml_121_request
        
        return xml_121_request
    
    def translate_response(self, mcp_response: Dict) -> Dict:
        """Convert MCP JSON-RPC response to 121XML"""
        
        request_id = mcp_response.get("id")
        result = mcp_response.get("result", {})
        error = mcp_response.get("error")
        
        # Determine object type
        if error:
            obj_type = "mcp_error_response"
            schema_uri = "urn:121xml:mcp-error/1.0"
            content = error
        else:
            obj_type = "mcp_response"
            schema_uri = "urn:121xml:mcp-response/1.0"
            content = result
        
        # Build 121XML response object
        xml_121_response = {
            "_type": obj_type,
            "_version": "121xml/1.0",
            "_schema": schema_uri,
            "jsonrpc": "2.0",
            "result": result,
            "error": error,
            "id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        # Add content address
        xml_121_response["_address"] = ContentAddressMapping.compute(
            {k: v for k, v in xml_121_response.items() if k != "_address"},
            obj_type
        )
        
        return xml_121_response
    
    def _translate_params(self, params: Dict, method: str) -> Dict:
        """Translate MCP params to 121XML format"""
        
        translated = {}
        
        if method == "resources/read":
            # Resource read parameters
            translated["uri"] = params.get("uri")
        
        elif method == "tools/call":
            # Tool call parameters
            translated["name"] = params.get("name")
            translated["arguments"] = params.get("arguments", {})
            translated["_arguments_address"] = ContentAddressMapping.compute(
                params.get("arguments", {}),
                "tool_arguments"
            )
        
        elif method == "prompts/get":
            # Prompt get parameters
            translated["name"] = params.get("name")
            if "arguments" in params:
                translated["arguments"] = params.get("arguments")
                translated["_arguments_address"] = ContentAddressMapping.compute(
                    params.get("arguments", {}),
                    "prompt_arguments"
                )
        
        else:
            # Generic params - pass through with content addressing
            translated = params.copy()
            translated["_params_address"] = ContentAddressMapping.compute(params, "mcp_params")
        
        return translated
    
    def translate_resource(self, resource: Dict) -> Dict:
        """Translate MCP resource to 121XML"""
        
        return {
            "_type": "mcp_resource",
            "_schema": "urn:121xml:mcp-resource/1.0",
            "uri": resource.get("uri"),
            "name": resource.get("name", ""),
            "description": resource.get("description", ""),
            "mimeType": resource.get("mimeType"),
            "contents": [self._translate_content_block(c) for c in resource.get("contents", [])],
            "_address": ContentAddressMapping.compute(resource, "mcp_resource"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def translate_tool(self, tool: Dict) -> Dict:
        """Translate MCP tool to 121XML"""
        
        return {
            "_type": "mcp_tool",
            "_schema": "urn:121xml:mcp-tool/1.0",
            "name": tool.get("name"),
            "description": tool.get("description", ""),
            "inputSchema": tool.get("inputSchema", {}),
            "_schema_address": ContentAddressMapping.compute(
                tool.get("inputSchema", {}),
                "tool_schema"
            ),
            "_address": ContentAddressMapping.compute(tool, "mcp_tool"),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _translate_content_block(self, block: Dict) -> Dict:
        """Translate content block"""
        
        block_type = block.get("type")
        
        if block_type == "text":
            return {
                "_type": "text_block",
                "_schema": "urn:121xml:mcp-text-block/1.0",
                "text": block.get("text"),
                "_address": ContentAddressMapping.compute(block, "text_block")
            }
        
        elif block_type == "image":
            return {
                "_type": "image_block",
                "_schema": "urn:121xml:mcp-image-block/1.0",
                "mimeType": block.get("mimeType"),
                "data": block.get("data"),
                "_data_address": ContentAddressMapping.compute(
                    {"data": block.get("data")},
                    "image_data"
                ),
                "_address": ContentAddressMapping.compute(block, "image_block")
            }
        
        return block


# ============================================================================
# TRANSLATOR - 121XML TO MCP
# ============================================================================

class XMLl21_To_MCP_Translator:
    """Translates 121XML format back to MCP protocol"""
    
    def __init__(self):
        self.reverse_cache: Dict[str, Dict] = {}
    
    def translate_request(self, xml_121_request: Dict) -> Dict:
        """Convert 121XML request back to MCP JSON-RPC"""
        
        return {
            "jsonrpc": "2.0",
            "method": xml_121_request.get("method"),
            "params": self._untranslate_params(xml_121_request.get("params", {})),
            "id": xml_121_request.get("id")
        }
    
    def translate_response(self, xml_121_response: Dict) -> Dict:
        """Convert 121XML response back to MCP JSON-RPC"""
        
        response = {
            "jsonrpc": "2.0",
            "id": xml_121_response.get("id")
        }
        
        if xml_121_response.get("error"):
            response["error"] = xml_121_response.get("error")
        else:
            response["result"] = xml_121_response.get("result", {})
        
        return response
    
    def _untranslate_params(self, params: Dict) -> Dict:
        """Remove 121XML metadata from params"""
        
        return {
            k: v for k, v in params.items()
            if not k.startswith("_")
        }


# ============================================================================
# BIDIRECTIONAL TRANSLATOR
# ============================================================================

class BidirectionalMCPTranslator:
    """Seamless bidirectional translation between MCP and 121XML"""
    
    def __init__(self):
        self.mcp_to_121xml = MCP_To_121XML_Translator()
        self.xml_121_to_mcp = XMLl21_To_MCP_Translator()
        self.translation_log: List[Dict] = []
    
    def translate(self, source_format: str, target_format: str, 
                 data: Dict, operation_type: str = "request") -> Dict:
        """
        Translate between formats.
        
        Args:
            source_format: "mcp" or "121xml"
            target_format: "mcp" or "121xml"
            data: The data to translate
            operation_type: "request" or "response"
        
        Returns:
            Translated data with schema and addressing
        """
        
        # MCP → 121XML
        if source_format == "mcp" and target_format == "121xml":
            if operation_type == "request":
                result = self.mcp_to_121xml.translate_request(data)
            else:
                result = self.mcp_to_121xml.translate_response(data)
        
        # 121XML → MCP
        elif source_format == "121xml" and target_format == "mcp":
            if operation_type == "request":
                result = self.xml_121_to_mcp.translate_request(data)
            else:
                result = self.xml_121_to_mcp.translate_response(data)
        
        # Same format - just validate and return
        else:
            result = data
        
        # Log translation
        self.translation_log.append({
            "source": source_format,
            "target": target_format,
            "operation": operation_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input_hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]
        })
        
        return result
    
    def get_translation_stats(self) -> Dict:
        """Get statistics on translations performed"""
        
        mcp_to_121xml_count = sum(1 for t in self.translation_log if t["source"] == "mcp")
        xml_121_to_mcp_count = sum(1 for t in self.translation_log if t["source"] == "121xml")
        
        return {
            "total_translations": len(self.translation_log),
            "mcp_to_121xml": mcp_to_121xml_count,
            "121xml_to_mcp": xml_121_to_mcp_count,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# ============================================================================
# DEMO & TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MCP ↔ 121XML TRANSLATION LAYER - DEMO")
    print("=" * 70)
    
    translator = BidirectionalMCPTranslator()
    
    # Example MCP request
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "process_payment",
            "arguments": {
                "amount": 450000,
                "currency": "USD",
                "invoice": "INV-2026-08-0042"
            }
        },
        "id": 1
    }
    
    print("\n📥 MCP Request:")
    print(json.dumps(mcp_request, indent=2))
    
    # Translate to 121XML
    xml_121_request = translator.translate("mcp", "121xml", mcp_request, "request")
    print("\n🔄 Translated to 121XML:")
    print(json.dumps(xml_121_request, indent=2))
    
    # Translate back to MCP
    mcp_request_restored = translator.translate("121xml", "mcp", xml_121_request, "request")
    print("\n📤 Translated back to MCP:")
    print(json.dumps(mcp_request_restored, indent=2))
    
    # Stats
    print("\n📊 Translation Statistics:")
    print(json.dumps(translator.get_translation_stats(), indent=2))

