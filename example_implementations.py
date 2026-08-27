"""
121XML Agentic OS - Example Implementations
===========================================

Working examples of agents, tools, and workflows.
Author: 121XML Foundation
License: Apache 2.0
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

from agentic_os_core import (
    AgenticEngine, ToolDefinition, AgentDefinition, ExecutionContext,
    PermissionType, ContentAddress
)


# ============================================================================
# EXAMPLE 1: EMAIL CLASSIFICATION AGENT
# ============================================================================

def setup_email_classification_agent(engine: AgenticEngine) -> tuple:
    """Setup complete email classification agent with tools"""

    # Define tool: Read Email
    read_email_tool = ToolDefinition(
        tool_id="tool_read_email",
        name="Read Email",
        description="Read an email from inbox",
        input_schema={
            "type": "object",
            "properties": {
                "email_id": {
                    "type": "string",
                    "description": "Email identifier"
                },
                "format": {
                    "type": "string",
                    "enum": ["text", "html"],
                    "default": "text"
                }
            },
            "required": ["email_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "from": {"type": "string"},
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "timestamp": {"type": "string"}
            }
        },
        permissions_required=[PermissionType.READ],
        handler=lambda p: {
            "id": p["email_id"],
            "from": "customer@example.com",
            "to": "support@company.com",
            "subject": "Need help with account",
            "body": "I'm having trouble accessing my account after password reset",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # Define tool: Classify Email
    classify_email_tool = ToolDefinition(
        tool_id="tool_classify_email",
        name="Classify Email",
        description="Classify email by urgency and category",
        input_schema={
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "body": {"type": "string"}
            },
            "required": ["subject", "body"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["billing", "technical", "account", "feedback", "spam"]
                },
                "urgency": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"]
                },
                "confidence": {"type": "number"}
            }
        },
        permissions_required=[PermissionType.EXECUTE],
        handler=lambda p: {
            "category": "account",
            "urgency": "high",
            "confidence": 0.94
        }
    )

    # Define tool: Create Ticket
    create_ticket_tool = ToolDefinition(
        tool_id="tool_create_ticket",
        name="Create Support Ticket",
        description="Create support ticket for email",
        input_schema={
            "type": "object",
            "properties": {
                "email_id": {"type": "string"},
                "category": {"type": "string"},
                "urgency": {"type": "string"},
                "summary": {"type": "string"}
            },
            "required": ["email_id", "category", "summary"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "status": {"type": "string"},
                "created_at": {"type": "string"}
            }
        },
        permissions_required=[PermissionType.WRITE],
        handler=lambda p: {
            "ticket_id": f"TKT-{str(uuid.uuid4())[:8].upper()}",
            "status": "open",
            "created_at": datetime.utcnow().isoformat()
        }
    )

    # Register tools
    engine.register_tool(read_email_tool)
    engine.register_tool(classify_email_tool)
    engine.register_tool(create_ticket_tool)

    # Register agent
    email_agent = AgentDefinition(
        agent_id="agent_email_classifier",
        name="Email Classifier Agent",
        model="claude-opus-5",
        description="Classifies incoming emails and creates support tickets",
        available_tools=[
            "tool_read_email",
            "tool_classify_email",
            "tool_create_ticket"
        ],
        supported_protocols=["rest", "grpc", "websocket"]
    )

    engine.register_agent(email_agent)

    return email_agent, [read_email_tool, classify_email_tool, create_ticket_tool]


def demo_email_classification():
    """Demonstration of email classification workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Email Classification Agent")
    print("="*60)

    # Initialize engine
    engine = AgenticEngine()

    # Setup agent and tools
    agent, tools = setup_email_classification_agent(engine)

    # Create permission grant
    grant = engine.permission_manager.create_grant(
        user_id="support_team@company.com",
        system_id="engine",
        permissions=[
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.EXECUTE
        ],
        expires_in_hours=8
    )

    print(f"\nAgent: {agent.name}")
    print(f"Tools Available: {', '.join(agent.available_tools)}")
    print(f"Permission Grant: {grant.grant_id}")
    print(f"Permissions: {', '.join([p.value for p in grant.permissions])}")

    # Create execution context
    context = engine.create_execution_context(
        user_id="support_team@company.com",
        agent_id="agent_email_classifier",
        permission_grant=grant
    )

    # Simulate workflow
    print("\n--- Workflow Execution ---")

    # Step 1: Read email
    print("\nStep 1: Reading email...")
    read_result = engine.execute_tool(
        tool_id="tool_read_email",
        parameters={"email_id": "email_12345"},
        execution_context=context
    )
    email_content = read_result["result"]
    print(f"✓ Email read successfully")
    print(f"  From: {email_content['from']}")
    print(f"  Subject: {email_content['subject']}")
    print(f"  Address: {read_result['address']}")

    # Step 2: Classify email
    print("\nStep 2: Classifying email...")
    classify_result = engine.execute_tool(
        tool_id="tool_classify_email",
        parameters={
            "subject": email_content["subject"],
            "body": email_content["body"]
        },
        execution_context=context
    )
    classification = classify_result["result"]
    print(f"✓ Email classified")
    print(f"  Category: {classification['category']}")
    print(f"  Urgency: {classification['urgency']}")
    print(f"  Confidence: {classification['confidence']*100:.1f}%")

    # Step 3: Create ticket
    print("\nStep 3: Creating support ticket...")
    ticket_result = engine.execute_tool(
        tool_id="tool_create_ticket",
        parameters={
            "email_id": "email_12345",
            "category": classification["category"],
            "urgency": classification["urgency"],
            "summary": email_content["subject"]
        },
        execution_context=context
    )
    ticket = ticket_result["result"]
    print(f"✓ Support ticket created")
    print(f"  Ticket ID: {ticket['ticket_id']}")
    print(f"  Status: {ticket['status']}")

    # Show audit trail
    print("\n--- Audit Trail ---")
    audit_entries = engine.permission_manager.get_audit_log("support_team@company.com")
    for entry in audit_entries[-5:]:  # Show last 5 entries
        print(f"[{entry.timestamp.strftime('%H:%M:%S')}] {entry.action}: {entry.status}")


# ============================================================================
# EXAMPLE 2: DATA ANALYSIS AGENT
# ============================================================================

def setup_data_analysis_agent(engine: AgenticEngine) -> tuple:
    """Setup data analysis agent with computational tools"""

    # Tool: Load Dataset
    load_data_tool = ToolDefinition(
        tool_id="tool_load_data",
        name="Load Dataset",
        description="Load data for analysis",
        input_schema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "filters": {
                    "type": "object",
                    "properties": {
                        "date_from": {"type": "string"},
                        "date_to": {"type": "string"}
                    }
                }
            },
            "required": ["dataset_id"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "rows": {"type": "integer"},
                "columns": {"type": "integer"},
                "data": {"type": "object"}
            }
        },
        permissions_required=[PermissionType.READ],
        handler=lambda p: {
            "rows": 1000,
            "columns": 15,
            "data": {
                "samples": 100,
                "features": ["id", "timestamp", "value", "category"]
            }
        }
    )

    # Tool: Analyze Dataset
    analyze_tool = ToolDefinition(
        tool_id="tool_analyze_data",
        name="Analyze Data",
        description="Perform statistical analysis",
        input_schema={
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "correlation", "distribution"]
                }
            },
            "required": ["data", "analysis_type"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "analysis_type": {"type": "string"},
                "results": {"type": "object"},
                "confidence": {"type": "number"}
            }
        },
        permissions_required=[PermissionType.EXECUTE],
        handler=lambda p: {
            "analysis_type": p["analysis_type"],
            "results": {
                "mean": 45.2,
                "median": 43.5,
                "std_dev": 12.3,
                "min": 10,
                "max": 95
            },
            "confidence": 0.99
        }
    )

    # Tool: Generate Report
    report_tool = ToolDefinition(
        tool_id="tool_generate_report",
        name="Generate Report",
        description="Generate analysis report",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "analyses": {
                    "type": "array",
                    "items": {"type": "object"}
                }
            },
            "required": ["title", "analyses"]
        },
        output_schema={
            "type": "object",
            "properties": {
                "report_id": {"type": "string"},
                "filename": {"type": "string"},
                "url": {"type": "string"}
            }
        },
        permissions_required=[PermissionType.WRITE],
        handler=lambda p: {
            "report_id": str(uuid.uuid4()),
            "filename": "analysis_report.pdf",
            "url": "https://reports.company.com/report_" + str(uuid.uuid4())[:8]
        }
    )

    # Register tools
    engine.register_tool(load_data_tool)
    engine.register_tool(analyze_tool)
    engine.register_tool(report_tool)

    # Register agent
    analysis_agent = AgentDefinition(
        agent_id="agent_data_analyst",
        name="Data Analysis Agent",
        model="claude-opus-5",
        description="Performs data analysis and generates reports",
        available_tools=[
            "tool_load_data",
            "tool_analyze_data",
            "tool_generate_report"
        ],
        supported_protocols=["rest", "grpc"]
    )

    engine.register_agent(analysis_agent)

    return analysis_agent, [load_data_tool, analyze_tool, report_tool]


def demo_data_analysis():
    """Demonstration of data analysis workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Data Analysis Agent")
    print("="*60)

    # Initialize engine
    engine = AgenticEngine()

    # Setup agent
    agent, tools = setup_data_analysis_agent(engine)

    # Create permission grant
    grant = engine.permission_manager.create_grant(
        user_id="analyst@company.com",
        system_id="engine",
        permissions=[
            PermissionType.READ,
            PermissionType.WRITE,
            PermissionType.EXECUTE
        ],
        expires_in_hours=24
    )

    print(f"\nAgent: {agent.name}")
    print(f"Model: {agent.model}")

    # Create execution context
    context = engine.create_execution_context(
        user_id="analyst@company.com",
        agent_id="agent_data_analyst",
        permission_grant=grant
    )

    # Execute workflow
    print("\n--- Data Analysis Workflow ---")

    # Step 1: Load data
    print("\nStep 1: Loading dataset...")
    load_result = engine.execute_tool(
        tool_id="tool_load_data",
        parameters={
            "dataset_id": "sales_2024_q3",
            "filters": {
                "date_from": "2024-07-01",
                "date_to": "2024-09-30"
            }
        },
        execution_context=context
    )
    data_info = load_result["result"]
    print(f"✓ Dataset loaded")
    print(f"  Rows: {data_info['rows']}")
    print(f"  Columns: {data_info['columns']}")

    # Step 2: Analyze data
    print("\nStep 2: Analyzing data...")
    analysis_result = engine.execute_tool(
        tool_id="tool_analyze_data",
        parameters={
            "data": data_info["data"],
            "analysis_type": "distribution"
        },
        execution_context=context
    )
    analysis = analysis_result["result"]
    print(f"✓ Analysis complete")
    print(f"  Mean: {analysis['results']['mean']}")
    print(f"  Std Dev: {analysis['results']['std_dev']}")
    print(f"  Confidence: {analysis['confidence']*100:.1f}%")

    # Step 3: Generate report
    print("\nStep 3: Generating report...")
    report_result = engine.execute_tool(
        tool_id="tool_generate_report",
        parameters={
            "title": "Q3 2024 Sales Analysis",
            "analyses": [analysis]
        },
        execution_context=context
    )
    report = report_result["result"]
    print(f"✓ Report generated")
    print(f"  Report ID: {report['report_id']}")
    print(f"  File: {report['filename']}")
    print(f"  URL: {report['url']}")


# ============================================================================
# EXAMPLE 3: MULTI-STEP WORKFLOW
# ============================================================================

def demo_multi_step_workflow():
    """Demonstration of complex workflow with multiple agents"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Step Workflow with Multiple Agents")
    print("="*60)

    # Initialize engine
    engine = AgenticEngine()

    # Setup both agents
    email_agent, email_tools = setup_email_classification_agent(engine)
    analysis_agent, analysis_tools = setup_data_analysis_agent(engine)

    # Create permission grants
    email_grant = engine.permission_manager.create_grant(
        user_id="workflow@company.com",
        system_id="engine",
        permissions=[PermissionType.READ, PermissionType.WRITE, PermissionType.EXECUTE],
        expires_in_hours=24
    )

    analysis_grant = engine.permission_manager.create_grant(
        user_id="workflow@company.com",
        system_id="engine",
        permissions=[PermissionType.READ, PermissionType.WRITE, PermissionType.EXECUTE],
        expires_in_hours=24
    )

    print("\nWorkflow Definition:")
    print("1. Email Agent reads and classifies customer inquiries")
    print("2. Data Analysis Agent analyzes customer trends")
    print("3. Results are combined for decision making")

    # Execute workflow
    print("\n--- Executing Workflow ---")

    # Phase 1: Email Classification
    print("\nPhase 1: Email Classification Agent")
    email_context = engine.create_execution_context(
        user_id="workflow@company.com",
        agent_id="agent_email_classifier",
        permission_grant=email_grant
    )

    read_result = engine.execute_tool(
        tool_id="tool_read_email",
        parameters={"email_id": "email_54321"},
        execution_context=email_context
    )
    print(f"  ✓ Processed email: {read_result['result']['subject']}")

    classify_result = engine.execute_tool(
        tool_id="tool_classify_email",
        parameters={
            "subject": read_result["result"]["subject"],
            "body": read_result["result"]["body"]
        },
        execution_context=email_context
    )
    print(f"  ✓ Classification: {classify_result['result']['category']} ({classify_result['result']['urgency']})")

    # Phase 2: Data Analysis
    print("\nPhase 2: Data Analysis Agent")
    analysis_context = engine.create_execution_context(
        user_id="workflow@company.com",
        agent_id="agent_data_analyst",
        permission_grant=analysis_grant
    )

    load_result = engine.execute_tool(
        tool_id="tool_load_data",
        parameters={"dataset_id": "customer_feedback"},
        execution_context=analysis_context
    )
    print(f"  ✓ Loaded data: {load_result['result']['rows']} rows")

    analyze_result = engine.execute_tool(
        tool_id="tool_analyze_data",
        parameters={
            "data": load_result["result"]["data"],
            "analysis_type": "summary"
        },
        execution_context=analysis_context
    )
    print(f"  ✓ Analysis confidence: {analyze_result['result']['confidence']*100:.1f}%")

    # Summary
    print("\n--- Workflow Complete ---")
    print(f"Total Tool Executions: {len(email_context.tool_calls) + len(analysis_context.tool_calls)}")
    print(f"Total Audit Entries: {len(engine.permission_manager.get_audit_log())}")

    # Show engine statistics
    status = engine.get_status()
    print(f"\nEngine Statistics:")
    print(f"  Registered Tools: {status['tools_registered']}")
    print(f"  Registered Agents: {status['agents_registered']}")
    print(f"  Total Executions: {status['total_executions']}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("121XML AGENTIC OS - WORKING EXAMPLES")
    print("="*60)

    # Run examples
    demo_email_classification()
    demo_data_analysis()
    demo_multi_step_workflow()

    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60 + "\n")
