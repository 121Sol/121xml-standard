"""
121XML Agentic Operating System - REST API Implementation
=========================================================

FastAPI-based REST endpoints for the 121XML Agentic OS.
Author: 121XML Foundation
License: Apache 2.0
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json

from agentic_os_core import (
    AgenticEngine, ToolDefinition, AgentDefinition, ExecutionContext,
    PermissionGrant, PermissionType, ContentAddress
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PermissionGrantRequest(BaseModel):
    """Request to create permission grant"""
    user_id: str
    system_id: str
    permissions: List[str]  # "read", "write", "execute", etc.
    expires_in_hours: Optional[int] = 24

    class Config:
        example = {
            "user_id": "user_123",
            "system_id": "engine",
            "permissions": ["read", "execute"],
            "expires_in_hours": 24
        }


class ToolRequest(BaseModel):
    """Request to execute a tool"""
    tool_id: str
    parameters: Dict[str, Any]

    class Config:
        example = {
            "tool_id": "tool_send_email",
            "parameters": {
                "to": "user@example.com",
                "subject": "Hello",
                "body": "This is a test"
            }
        }


class AgentRequest(BaseModel):
    """Request to process with agent"""
    agent_id: str
    protocol: str = "rest"
    schema_type: str = "json"
    data: Dict[str, Any]

    class Config:
        example = {
            "agent_id": "agent_assistant",
            "protocol": "rest",
            "schema_type": "json",
            "data": {"message": "Hello assistant"}
        }


class ToolRegistrationRequest(BaseModel):
    """Request to register new tool"""
    tool_id: str
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions_required: List[str]

    class Config:
        example = {
            "tool_id": "tool_send_email",
            "name": "Send Email",
            "description": "Send an email message",
            "input_schema": {
                "to": "string",
                "subject": "string",
                "body": "string"
            },
            "output_schema": {
                "success": "boolean",
                "message_id": "string"
            },
            "permissions_required": ["execute"]
        }


class AgentRegistrationRequest(BaseModel):
    """Request to register new agent"""
    agent_id: str
    name: str
    model: str
    description: str
    available_tools: List[str]
    supported_protocols: List[str] = ["rest", "grpc", "websocket"]

    class Config:
        example = {
            "agent_id": "agent_assistant",
            "name": "General Assistant",
            "model": "claude-opus-5",
            "description": "General purpose AI assistant",
            "available_tools": ["tool_send_email"],
            "supported_protocols": ["rest", "grpc", "websocket"]
        }


class ProcessRequestModel(BaseModel):
    """Request to process data"""
    protocol: str
    schema_type: str
    request: Dict[str, Any]


class RevokingrantRequest(BaseModel):
    """Request to revoke permission grant"""
    grant_id: str


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class PermissionGrantResponse(BaseModel):
    """Response containing permission grant"""
    grant_id: str
    user_id: str
    system_id: str
    permissions: List[str]
    created_at: str
    expires_at: Optional[str]
    is_valid: bool


class ToolExecutionResponse(BaseModel):
    """Response from tool execution"""
    status: str
    result: Dict[str, Any]
    address: str
    execution_time_ms: float


class ProcessResponse(BaseModel):
    """Response from processing request"""
    status: str
    address: str
    protocol: str
    schema_type: str
    timestamp: str


class StatusResponse(BaseModel):
    """Engine status response"""
    tools_registered: int
    agents_registered: int
    protocol_adapters: List[str]
    schema_translators: List[str]
    total_executions: int
    audit_log_entries: int
    timestamp: str


class AuditLogEntryResponse(BaseModel):
    """Audit log entry response"""
    entry_id: str
    timestamp: str
    user_id: str
    action: str
    resource: str
    permission: str
    status: str


# ============================================================================
# API SERVER
# ============================================================================

class AgenticOSServer:
    """121XML Agentic OS REST API Server"""

    def __init__(self):
        self.app = FastAPI(
            title="121XML Agentic Operating System",
            description="Universal Protocol & Schema Translation for AI Agents",
            version="1.0.0"
        )
        self.engine = AgenticEngine()
        self.setup_routes()
        self.setup_middleware()

    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""

        # ====== HEALTH & STATUS ======

        @self.app.get("/health", tags=["Health"])
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

        @self.app.get("/status", response_model=StatusResponse, tags=["Status"])
        async def get_status():
            """Get engine status"""
            status = self.engine.get_status()
            return StatusResponse(
                **status,
                timestamp=datetime.utcnow().isoformat()
            )

        # ====== PERMISSION MANAGEMENT ======

        @self.app.post("/permissions/grant", response_model=PermissionGrantResponse, tags=["Permissions"])
        async def create_permission_grant(request: PermissionGrantRequest):
            """Create new permission grant"""
            try:
                permissions = [PermissionType[p.upper()] for p in request.permissions]
            except KeyError as e:
                raise HTTPException(status_code=400, detail=f"Invalid permission: {e}")

            grant = self.engine.permission_manager.create_grant(
                user_id=request.user_id,
                system_id=request.system_id,
                permissions=permissions,
                expires_in_hours=request.expires_in_hours
            )

            return PermissionGrantResponse(
                grant_id=grant.grant_id,
                user_id=grant.user_id,
                system_id=grant.system_id,
                permissions=[p.value for p in grant.permissions],
                created_at=grant.created_at.isoformat(),
                expires_at=grant.expires_at.isoformat() if grant.expires_at else None,
                is_valid=grant.is_valid()
            )

        @self.app.post("/permissions/revoke", tags=["Permissions"])
        async def revoke_grant(request: RevokingrantRequest):
            """Revoke permission grant"""
            grant = self.engine.permission_manager.grants.get(request.grant_id)
            if not grant:
                raise HTTPException(status_code=404, detail="Grant not found")

            grant.revoke()
            return {"status": "revoked", "grant_id": request.grant_id}

        @self.app.get("/permissions/{grant_id}", response_model=PermissionGrantResponse, tags=["Permissions"])
        async def get_grant(grant_id: str):
            """Get permission grant details"""
            grant = self.engine.permission_manager.grants.get(grant_id)
            if not grant:
                raise HTTPException(status_code=404, detail="Grant not found")

            return PermissionGrantResponse(
                grant_id=grant.grant_id,
                user_id=grant.user_id,
                system_id=grant.system_id,
                permissions=[p.value for p in grant.permissions],
                created_at=grant.created_at.isoformat(),
                expires_at=grant.expires_at.isoformat() if grant.expires_at else None,
                is_valid=grant.is_valid()
            )

        # ====== TOOL MANAGEMENT ======

        @self.app.post("/tools/register", tags=["Tools"])
        async def register_tool(request: ToolRegistrationRequest):
            """Register new tool"""
            permissions = []
            for p in request.permissions_required:
                try:
                    permissions.append(PermissionType[p.upper()])
                except KeyError:
                    raise HTTPException(status_code=400, detail=f"Invalid permission: {p}")

            tool = ToolDefinition(
                tool_id=request.tool_id,
                name=request.name,
                description=request.description,
                input_schema=request.input_schema,
                output_schema=request.output_schema,
                permissions_required=permissions
            )

            self.engine.register_tool(tool)

            return {
                "status": "registered",
                "tool_id": tool.tool_id,
                "name": tool.name,
                "profile": tool.to_profile()
            }

        @self.app.get("/tools/{tool_id}", tags=["Tools"])
        async def get_tool(tool_id: str):
            """Get tool details"""
            tool = self.engine.tools.get(tool_id)
            if not tool:
                raise HTTPException(status_code=404, detail="Tool not found")

            return {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "output_schema": tool.output_schema,
                "permissions_required": [p.value for p in tool.permissions_required],
                "profile": tool.to_profile()
            }

        @self.app.get("/tools", tags=["Tools"])
        async def list_tools():
            """List all registered tools"""
            return {
                "tools": [
                    {
                        "tool_id": t.tool_id,
                        "name": t.name,
                        "description": t.description
                    }
                    for t in self.engine.tools.values()
                ],
                "count": len(self.engine.tools)
            }

        # ====== AGENT MANAGEMENT ======

        @self.app.post("/agents/register", tags=["Agents"])
        async def register_agent(request: AgentRegistrationRequest):
            """Register new agent"""
            agent = AgentDefinition(
                agent_id=request.agent_id,
                name=request.name,
                model=request.model,
                description=request.description,
                available_tools=request.available_tools,
                supported_protocols=request.supported_protocols
            )

            self.engine.register_agent(agent)

            return {
                "status": "registered",
                "agent_id": agent.agent_id,
                "name": agent.name,
                "profile": agent.to_profile()
            }

        @self.app.get("/agents/{agent_id}", tags=["Agents"])
        async def get_agent(agent_id: str):
            """Get agent details"""
            agent = self.engine.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "model": agent.model,
                "description": agent.description,
                "available_tools": agent.available_tools,
                "supported_protocols": agent.supported_protocols,
                "profile": agent.to_profile()
            }

        @self.app.get("/agents", tags=["Agents"])
        async def list_agents():
            """List all registered agents"""
            return {
                "agents": [
                    {
                        "agent_id": a.agent_id,
                        "name": a.name,
                        "model": a.model,
                        "description": a.description
                    }
                    for a in self.engine.agents.values()
                ],
                "count": len(self.engine.agents)
            }

        # ====== TOOL EXECUTION ======

        @self.app.post("/agents/{agent_id}/execute-tool", response_model=ToolExecutionResponse, tags=["Execution"])
        async def execute_tool(agent_id: str, request: ToolRequest, x_grant_id: str = Header(...)):
            """Execute tool via agent"""
            # Get permission grant
            grant = self.engine.permission_manager.grants.get(x_grant_id)
            if not grant:
                raise HTTPException(status_code=401, detail="Invalid grant")

            if not grant.is_valid():
                raise HTTPException(status_code=401, detail="Grant expired or revoked")

            # Verify agent exists
            agent = self.engine.agents.get(agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail="Agent not found")

            # Create execution context
            context = self.engine.create_execution_context(
                user_id=grant.user_id,
                agent_id=agent_id,
                permission_grant=grant
            )

            # Execute tool
            import time
            start_time = time.time()
            result = self.engine.execute_tool(
                tool_id=request.tool_id,
                parameters=request.parameters,
                execution_context=context
            )
            execution_time = (time.time() - start_time) * 1000

            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return ToolExecutionResponse(
                status=result.get("status", "unknown"),
                result=result.get("result", {}),
                address=result.get("address", ""),
                execution_time_ms=execution_time
            )

        # ====== REQUEST PROCESSING ======

        @self.app.post("/process", response_model=ProcessResponse, tags=["Processing"])
        async def process_request(request: ProcessRequestModel, x_grant_id: str = Header(...)):
            """Process request through protocol/schema translation"""
            # Get permission grant
            grant = self.engine.permission_manager.grants.get(x_grant_id)
            if not grant:
                raise HTTPException(status_code=401, detail="Invalid grant")

            if not grant.is_valid():
                raise HTTPException(status_code=401, detail="Grant expired or revoked")

            # Process
            result = self.engine.process_request(
                protocol=request.protocol,
                schema_type=request.schema_type,
                request=request.request,
                permission_grant=grant
            )

            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return ProcessResponse(
                status=result["status"],
                address=result["address"],
                protocol=request.protocol,
                schema_type=request.schema_type,
                timestamp=datetime.utcnow().isoformat()
            )

        # ====== AUDIT LOG ======

        @self.app.get("/audit", tags=["Audit"])
        async def get_audit_log(user_id: Optional[str] = None):
            """Get audit log"""
            entries = self.engine.permission_manager.get_audit_log(user_id)
            return {
                "entries": [
                    AuditLogEntryResponse(
                        entry_id=e.entry_id,
                        timestamp=e.timestamp.isoformat(),
                        user_id=e.user_id,
                        action=e.action,
                        resource=e.resource,
                        permission=e.permission.value,
                        status=e.status
                    ).dict()
                    for e in entries
                ],
                "count": len(entries)
            }

        # ====== SCHEMA & PROTOCOL INFO ======

        @self.app.get("/protocols", tags=["Info"])
        async def list_protocols():
            """List supported protocols"""
            return {
                "protocols": list(self.engine.protocol_adapters.keys()),
                "count": len(self.engine.protocol_adapters)
            }

        @self.app.get("/schemas", tags=["Info"])
        async def list_schemas():
            """List supported schemas"""
            return {
                "schemas": list(self.engine.schema_translators.keys()),
                "count": len(self.engine.schema_translators)
            }

    def get_app(self) -> FastAPI:
        """Get FastAPI app"""
        return self.app


# ============================================================================
# INITIALIZATION & STARTUP
# ============================================================================

def create_server() -> AgenticOSServer:
    """Create server instance"""
    server = AgenticOSServer()
    return server


# For running with: uvicorn 121xml_agentic_os_api:app --reload
server = create_server()
app = server.get_app()


if __name__ == "__main__":
    import uvicorn

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
