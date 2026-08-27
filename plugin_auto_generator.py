"""
121XML Plugin Auto-Generator
=============================

Automatically generates Claude plugins from 121XML schemas.
Reads schema definitions and produces production-ready plugin manifests.

Features:
- Schema-to-plugin compilation
- Automatic skill generation
- Manifest generation
- Tool definition extraction
- Resource embedding
- Capability detection

Author: 121XML Foundation
License: Apache 2.0
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PluginManifest:
    """Plugin manifest (plugin.json)"""
    name: str
    version: str
    description: str
    capabilities: List[str]
    tools: List[Dict]
    resources: List[Dict]
    prompts: List[Dict]
    
    def to_json(self) -> str:
        """Generate plugin.json"""
        return json.dumps({
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": self.capabilities,
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "generated": datetime.utcnow().isoformat() + "Z"
        }, indent=2)


@dataclass
class SkillDefinition:
    """Skill manifest (.skill)"""
    name: str
    description: str
    triggers: List[str]
    implementation: str
    
    def to_json(self) -> str:
        """Generate SKILL.md content"""
        return f"""# {self.name}

**Description:** {self.description}

**Triggers:** {', '.join(self.triggers)}

**Implementation:**
```
{self.implementation}
```

Generated: {datetime.utcnow().isoformat()}Z
"""


class PluginAutoGenerator:
    """Generates plugins from 121XML schemas"""
    
    def __init__(self):
        self.generated_plugins: List[PluginManifest] = []
        self.generated_skills: List[SkillDefinition] = []
    
    def generate_from_schema(self, schema: Dict, schema_name: str) -> PluginManifest:
        """
        Generate plugin from 121XML schema definition.
        
        Args:
            schema: 121XML schema object
            schema_name: Name for the plugin
        
        Returns:
            PluginManifest ready to deploy
        """
        
        # Extract capabilities from schema
        capabilities = self._extract_capabilities(schema)
        
        # Extract tools from schema
        tools = self._extract_tools(schema)
        
        # Extract resources from schema
        resources = self._extract_resources(schema)
        
        # Extract prompts from schema
        prompts = self._extract_prompts(schema)
        
        # Create manifest
        manifest = PluginManifest(
            name=schema_name,
            version="1.0.0",
            description=schema.get("description", f"121XML plugin for {schema_name}"),
            capabilities=capabilities,
            tools=tools,
            resources=resources,
            prompts=prompts
        )
        
        self.generated_plugins.append(manifest)
        return manifest
    
    def _extract_capabilities(self, schema: Dict) -> List[str]:
        """Extract plugin capabilities from schema"""
        capabilities = []
        
        if "tools" in schema:
            capabilities.append("tools")
        if "resources" in schema:
            capabilities.append("resources")
        if "prompts" in schema:
            capabilities.append("prompts")
        
        # Add 121XML-specific capabilities
        capabilities.extend([
            "content_addressing",
            "schema_discovery",
            "lossless_compression"
        ])
        
        return capabilities
    
    def _extract_tools(self, schema: Dict) -> List[Dict]:
        """Extract tool definitions from schema"""
        tools = []
        
        if "tools" not in schema:
            return tools
        
        for tool_name, tool_def in schema.get("tools", {}).items():
            tool = {
                "name": tool_name,
                "description": tool_def.get("description", ""),
                "input_schema": tool_def.get("input_schema", {}),
                "_121xml_schema": tool_def.get("_schema", f"urn:121xml:tool-{tool_name}/1.0")
            }
            tools.append(tool)
        
        return tools
    
    def _extract_resources(self, schema: Dict) -> List[Dict]:
        """Extract resource definitions from schema"""
        resources = []
        
        if "resources" not in schema:
            return resources
        
        for resource_uri, resource_def in schema.get("resources", {}).items():
            resource = {
                "uri": resource_uri,
                "name": resource_def.get("name", ""),
                "description": resource_def.get("description", ""),
                "mime_type": resource_def.get("mime_type", "application/json"),
                "_121xml_schema": resource_def.get("_schema", f"urn:121xml:resource-{resource_uri}/1.0")
            }
            resources.append(resource)
        
        return resources
    
    def _extract_prompts(self, schema: Dict) -> List[Dict]:
        """Extract prompt definitions from schema"""
        prompts = []
        
        if "prompts" not in schema:
            return prompts
        
        for prompt_name, prompt_def in schema.get("prompts", {}).items():
            prompt = {
                "name": prompt_name,
                "description": prompt_def.get("description", ""),
                "arguments": prompt_def.get("arguments", []),
                "template": prompt_def.get("template", ""),
                "_121xml_schema": prompt_def.get("_schema", f"urn:121xml:prompt-{prompt_name}/1.0")
            }
            prompts.append(prompt)
        
        return prompts
    
    def generate_skill(self, plugin: PluginManifest, trigger_keywords: List[str]) -> SkillDefinition:
        """Generate a skill definition from plugin"""
        
        implementation = f"""
Initialize MCP Server: {plugin.name}

Capabilities:
{json.dumps(plugin.capabilities, indent=2)}

Available Tools: {len(plugin.tools)}
{json.dumps([t['name'] for t in plugin.tools], indent=2)}

Available Resources: {len(plugin.resources)}
{json.dumps([r['uri'] for r in plugin.resources], indent=2)}

Available Prompts: {len(plugin.prompts)}
{json.dumps([p['name'] for p in plugin.prompts], indent=2)}
"""
        
        skill = SkillDefinition(
            name=plugin.name,
            description=plugin.description,
            triggers=trigger_keywords,
            implementation=implementation
        )
        
        self.generated_skills.append(skill)
        return skill
    
    def generate_complete_plugin_package(self, schema: Dict, 
                                        schema_name: str,
                                        output_dir: Path) -> Dict:
        """
        Generate complete plugin package (all files).
        
        Returns:
            Dictionary with file paths and content
        """
        
        # Generate plugin manifest
        plugin = self.generate_from_schema(schema, schema_name)
        
        # Generate skills
        skill = self.generate_skill(
            plugin,
            trigger_keywords=[schema_name, schema.get("keyword", "")]
        )
        
        # Prepare output files
        files = {
            "plugin.json": plugin.to_json(),
            "SKILL.md": skill.to_json(),
            "schema.121xml": json.dumps(schema, indent=2),
            "README.md": self._generate_readme(plugin)
        }
        
        # Create directory structure
        plugin_dir = output_dir / schema_name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Write files
        for filename, content in files.items():
            (plugin_dir / filename).write_text(content)
        
        return {
            "plugin_dir": str(plugin_dir),
            "files": list(files.keys()),
            "plugin_name": schema_name,
            "capabilities": plugin.capabilities,
            "tools": len(plugin.tools),
            "resources": len(plugin.resources),
            "prompts": len(plugin.prompts)
        }
    
    def _generate_readme(self, plugin: PluginManifest) -> str:
        """Generate plugin README"""
        return f"""# {plugin.name}

{plugin.description}

## Version
{plugin.version}

## Capabilities
{json.dumps(plugin.capabilities, indent=2)}

## Tools ({len(plugin.tools)})
{json.dumps([t['name'] for t in plugin.tools], indent=2)}

## Resources ({len(plugin.resources)})
{json.dumps([r['uri'] for r in plugin.resources], indent=2)}

## Prompts ({len(plugin.prompts)})
{json.dumps([p['name'] for p in plugin.prompts], indent=2)}

## Generated
{datetime.utcnow().isoformat()}Z

This plugin was auto-generated from 121XML schema.
"""


class BankingPluginGenerator:
    """Specialized generator for banking plugins"""
    
    @staticmethod
    def generate_banking_plugin(output_dir: Path) -> Dict:
        """Generate banking workflow plugin"""
        
        banking_schema = {
            "name": "121xml-banking",
            "description": "Banking workflow plugin for SWIFT and ISO 20022 payments",
            "keyword": "banking",
            "_schema": "urn:121xml:plugin-banking/1.0",
            
            "tools": {
                "swift_wire_transfer": {
                    "description": "Execute SWIFT MT103 wire transfer",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"},
                            "sender_account": {"type": "string"},
                            "receiver_account": {"type": "string"},
                            "invoice_number": {"type": "string"}
                        }
                    }
                },
                "iso20022_credit_transfer": {
                    "description": "Execute ISO 20022 PACS.008 credit transfer",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number"},
                            "currency": {"type": "string"},
                            "debtor_iban": {"type": "string"},
                            "creditor_iban": {"type": "string"},
                            "invoice_number": {"type": "string"}
                        }
                    }
                }
            },
            
            "resources": {
                "banking://schema/swift-mt103": {
                    "name": "SWIFT MT103 Schema",
                    "description": "SWIFT MT103 wire transfer format specification",
                    "mime_type": "application/json"
                },
                "banking://schema/iso20022-pacs008": {
                    "name": "ISO 20022 PACS.008 Schema",
                    "description": "ISO 20022 credit transfer format specification",
                    "mime_type": "application/json"
                }
            },
            
            "prompts": {
                "payment_workflow": {
                    "description": "Template for payment workflow execution",
                    "arguments": [
                        {"name": "workflow_type", "type": "string"},
                        {"name": "amount", "type": "number"},
                        {"name": "currency", "type": "string"}
                    ],
                    "template": "Execute {workflow_type} for {amount} {currency}"
                }
            }
        }
        
        generator = PluginAutoGenerator()
        return generator.generate_complete_plugin_package(
            banking_schema,
            "121xml-banking",
            output_dir
        )


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("121XML PLUGIN AUTO-GENERATOR - DEMO")
    print("=" * 70)
    
    output_dir = Path("/sessions/trusting-inspiring-gates/mnt/121XML/plugins")
    
    # Generate banking plugin
    result = BankingPluginGenerator.generate_banking_plugin(output_dir)
    
    print("\n✅ Banking Plugin Generated:")
    print(json.dumps(result, indent=2))
    
    print("\n📁 Files created:")
    for file in result["files"]:
        file_path = Path(result["plugin_dir"]) / file
        size = file_path.stat().st_size if file_path.exists() else 0
        print(f"   • {file} ({size} bytes)")

