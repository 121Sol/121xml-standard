# 121XML Agentic OS - Developer Guide
## Building Solid AI Agentic Applications

**Status:** Practical Implementation Guide  
**Reference:** AGENTIC_OS_ARCHITECTURE.md | MASTER_DEFINITIONS.121xml

---

## QUICK START: 5 MINUTES

### 1. Define Your Agent (121XML Profile)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map profile="urn:121xml:agentic-app-agent/1.0" version="1.0">
  
  <str name="agent_id">email_classifier</str>
  <str name="agent_name">Email Classification Agent</str>
  <str name="agent_role">Classify incoming emails and route to appropriate team</str>
  
  <!-- AI Model -->
  <str name="model">claude-opus-5</str>
  <str name="model_provider">anthropic</str>
  
  <!-- Available Tools -->
  <seq name="available_tools" of="str">
    <str>data://sha256:tool_read_email:tool</str>
    <str>data://sha256:tool_create_ticket:tool</str>
    <str>data://sha256:tool_send_notification:tool</str>
  </seq>
  
  <!-- Protocol Support -->
  <seq name="supported_protocols" of="str">
    <str>rest</str>
    <str>grpc</str>
    <str>websocket</str>
  </seq>
  
  <!-- Metadata -->
  <map name="metadata">
    <str name="version">1.0.0</str>
    <str name="created_timestamp">2026-08-06T13:00:00Z</str>
    <str name="owner">email-team</str>
  </map>
  
</map>
```

### 2. Define Your Tools (121XML Profiles)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map profile="urn:121xml:agentic-tool/1.0" version="1.0">
  
  <str name="tool_id">read_email</str>
  <str name="tool_name">Read Email</str>
  <str name="tool_address">data://sha256:tool_read_email:tool</str>
  
  <str name="description">Read email content from mailbox</str>
  
  <!-- Input Parameters -->
  <map name="parameters">
    <str name="profile">urn:121xml:parameter-list/1.0</str>
    
    <seq name="required_params" of="map">
      <map>
        <str name="param_name">email_id</str>
        <str name="param_type">str</str>
        <str name="param_description">Email message ID</str>
      </map>
    </seq>
    
    <seq name="optional_params" of="map">
      <map>
        <str name="param_name">include_attachments</str>
        <str name="param_type">bool</str>
        <str name="param_default">false</str>
      </map>
    </seq>
  </map>
  
  <!-- Return Type -->
  <map name="return_type">
    <str name="type">map</str>
    <seq name="fields" of="str">
      <str>from, to, subject, body, timestamp</str>
    </seq>
  </map>
  
  <!-- Permissions Required -->
  <map name="permissions">
    <str name="requires_grant">email_read_access</str>
  </map>
  
  <!-- Execution Metadata -->
  <map name="execution">
    <str name="timeout_seconds">30</str>
    <bool name="requires_user_approval">false</bool>
    <bool name="logs_data_access">true</bool>
  </map>
  
</map>
```

### 3. Deploy Your Agent

```python
from agentic_os import AgenticOS, Agent, Tool

# Initialize OS
os = AgenticOS()

# Load agent profile
agent_profile = os.load_profile("email_classifier.121xml")

# Create agent instance
agent = Agent(
    profile=agent_profile,
    model="claude-opus-5",
    protocols=["rest", "grpc", "websocket"]
)

# Register tools
agent.register_tools([
    "read_email.121xml",
    "create_ticket.121xml",
    "send_notification.121xml"
])

# Deploy to endpoints
os.deploy_agent(
    agent=agent,
    rest_endpoint="/agents/email-classifier",
    grpc_service="EmailClassifierService",
    websocket_endpoint="/ws/email-classifier"
)

# Done! Agent now works via REST, gRPC, and WebSocket
```

---

## EXAMPLES BY PROTOCOL

### Example 1: REST API

**User calls:**
```bash
curl -X POST http://localhost:8000/agents/email-classifier/process \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "msg_12345",
    "include_attachments": true
  }'
```

**System internally converts to 121XML:**
```xml
<map profile="urn:121xml:rest-request/1.0">
  <str name="endpoint">/agents/email-classifier/process</str>
  <str name="method">POST</str>
  <str name="email_id">msg_12345</str>
  <bool name="include_attachments">true</bool>
</map>
```

**Agent processes (all internal operations in 121XML):**
1. Validates input against MASTER_DEFINITIONS
2. Checks permission grant for user
3. Calls tool: `read_email` (returns 121XML)
4. Creates inference (reasoning in 121XML)
5. Returns response (121XML)

**REST Adapter converts back to JSON:**
```json
{
  "status": "success",
  "classification": "support_ticket",
  "confidence": 0.95,
  "suggested_team": "support",
  "inference_id": "inf_12345"
}
```

### Example 2: gRPC Service

**Proto definition (automatically generated from 121XML):**
```protobuf
service EmailClassifier {
  rpc ProcessEmail(EmailRequest) returns (ClassificationResponse);
  rpc GetStatus(StatusRequest) returns (StatusResponse);
}

message EmailRequest {
  string email_id = 1;
  bool include_attachments = 2;
}

message ClassificationResponse {
  string status = 1;
  string classification = 2;
  double confidence = 3;
  string suggested_team = 4;
  string inference_id = 5;
}
```

**Client calls:**
```python
import grpc
from email_classifier_pb2 import EmailRequest
from email_classifier_pb2_grpc import EmailClassifierStub

channel = grpc.insecure_channel('localhost:50051')
stub = EmailClassifierStub(channel)

request = EmailRequest(
    email_id="msg_12345",
    include_attachments=True
)

response = stub.ProcessEmail(request)
print(f"Classification: {response.classification}")
```

**System flow (identical to REST):**
1. gRPC Adapter parses Protobuf → 121XML
2. Agentic Engine processes (121XML)
3. Response Adapter converts 121XML → Protobuf

### Example 3: WebSocket (Real-Time Streaming)

**Client connects:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/email-classifier');

ws.onopen = () => {
  // Send initial context
  ws.send(JSON.stringify({
    type: 'init',
    user_id: 'user_123',
    session_id: 'sess_456'
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(`Agent: ${response.message}`);
  
  // Send follow-up
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Reclassify as urgent'
  }));
};
```

**System flow:**
1. WebSocket Adapter parses incoming JSON → 121XML
2. Agentic Engine maintains stateful conversation (121XML context window)
3. Agent streams responses back
4. WebSocket Adapter converts 121XML → JSON for each frame

---

## MULTI-PROTOCOL DEPLOYMENT

### Same Agent, Different Protocols

```python
from agentic_os import AgenticOS

# Load agent once
os = AgenticOS()
agent = os.load_agent("email_classifier.121xml")

# Deploy to REST
os.add_rest_endpoint(
    agent=agent,
    path="/api/v1/classify-email",
    methods=["POST"]
)

# Deploy to gRPC
os.add_grpc_service(
    agent=agent,
    service_name="EmailClassifier",
    port=50051
)

# Deploy to WebSocket
os.add_websocket_endpoint(
    agent=agent,
    path="/ws/email-classifier",
    max_connections=1000
)

# Deploy to GraphQL (also supported)
os.add_graphql_endpoint(
    agent=agent,
    query_field="classifyEmail",
    mutation_field="submitEmailFeedback"
)

print("Agent deployed to 4 protocols simultaneously!")
# All protocols share exact same agent logic
# All protocols handle their own serialization
# All protocols route through 121XML core engine
```

---

## TOOL COMPOSITION

### Define Complex Workflows

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map profile="urn:121xml:agentic-workflow/1.0" version="1.0">
  
  <str name="workflow_id">email_processing_pipeline</str>
  <str name="workflow_name">Email Processing Pipeline</str>
  
  <!-- Workflow Steps (DAG) -->
  <seq name="steps" of="map">
    
    <!-- Step 1: Read Email -->
    <map>
      <str name="step_id">step_read</str>
      <str name="step_type">tool_call</str>
      <str name="tool_reference">data://sha256:tool_read_email:tool</str>
      <str name="next_on_success">step_analyze</str>
      <str name="next_on_failure">step_error</str>
      <map name="input">
        <str name="email_id">{{email_id}}</str>
      </map>
    </map>
    
    <!-- Step 2: Analyze Content -->
    <map>
      <str name="step_id">step_analyze</str>
      <str name="step_type">agent_reasoning</str>
      <str name="agent_reference">data://sha256:agent_classifier:agent</str>
      <str name="prompt">Classify this email and determine routing</str>
      <str name="next_on_success">step_route</str>
      <str name="next_on_failure">step_error</str>
      <map name="context">
        <str name="email_content">{{step_read.output.body}}</str>
      </map>
    </map>
    
    <!-- Step 3: Route to Team -->
    <map>
      <str name="step_id">step_route</str>
      <str name="step_type">conditional</str>
      <seq name="conditions" of="map">
        <map>
          <str name="condition">classification == 'urgent'</str>
          <str name="next">step_urgent_routing</str>
        </map>
        <map>
          <str name="condition">classification == 'support'</str>
          <str name="next">step_support_routing</str>
        </map>
        <map>
          <str name="condition">true</str>
          <str name="next">step_default_routing</str>
        </map>
      </seq>
    </map>
    
    <!-- Step 4a: Urgent -->
    <map>
      <str name="step_id">step_urgent_routing</str>
      <str name="step_type">tool_call</str>
      <str name="tool_reference">data://sha256:tool_alert_exec:tool</str>
      <str name="next_on_success">step_complete</str>
    </map>
    
    <!-- Step 4b: Support -->
    <map>
      <str name="step_id">step_support_routing</str>
      <str name="step_type">tool_call</str>
      <str name="tool_reference">data://sha256:tool_create_ticket:tool</str>
      <str name="next_on_success">step_complete</str>
    </map>
    
    <!-- Step 4c: Default -->
    <map>
      <str name="step_id">step_default_routing</str>
      <str name="step_type">tool_call</str>
      <str name="tool_reference">data://sha256:tool_queue_message:tool</str>
      <str name="next_on_success">step_complete</str>
    </map>
    
    <!-- Step 5: Complete -->
    <map>
      <str name="step_id">step_complete</str>
      <str name="step_type">return_result</str>
      <map name="output">
        <str name="status">processed</str>
        <str name="classification">{{step_analyze.output.classification}}</str>
      </map>
    </map>
    
    <!-- Error Handler -->
    <map>
      <str name="step_id">step_error</str>
      <str name="step_type">error_handler</str>
      <map name="output">
        <str name="status">error</str>
        <str name="error_message">{{error.message}}</str>
      </map>
    </map>
    
  </seq>
  
</map>
```

---

## PERMISSION & ACCESS CONTROL

### User Grants Permission to Agent

```xml
<?xml version="1.0" encoding="UTF-8"?>
<map profile="urn:121xml:agentic-permission-grant/1.0" version="1.0">
  
  <str name="grant_id">grant_email_classify_001</str>
  <str name="granted_by">user_123</str>
  <str name="granted_to_agent">email_classifier</str>
  
  <!-- What is being granted -->
  <map name="scope">
    <str name="scope_type">agent_access</str>
    <seq name="tool_access" of="str">
      <str>read_email</str>
      <str>create_ticket</str>
      <str>send_notification</str>
    </seq>
  </map>
  
  <!-- What agent can do -->
  <seq name="permissions" of="str">
    <str>read_email_content</str>
    <str>create_support_tickets</str>
    <str>send_notifications</str>
  </seq>
  
  <!-- Time limits -->
  <map name="validity">
    <str name="valid_from">2026-08-06T00:00:00Z</str>
    <str name="valid_until">2026-12-06T00:00:00Z</str>
    <bool name="can_auto_renew">true</bool>
  </map>
  
  <!-- Usage limits -->
  <map name="limits">
    <int name="max_emails_per_day">10000</int>
    <int name="max_tickets_per_day">1000</int>
  </map>
  
  <!-- Revocation -->
  <map name="revocation">
    <bool name="is_revoked">false</bool>
    <str name="revocation_timestamp">null</str>
  </map>
  
</map>
```

---

## TESTING YOUR AGENT

### Unit Test

```python
import unittest
from agentic_os import Agent

class TestEmailClassifier(unittest.TestCase):
    
    def setUp(self):
        self.agent = Agent.load("email_classifier.121xml")
    
    def test_classify_support_email(self):
        """Test that support emails are classified correctly"""
        input_121xml = {
            "email_id": "test_001",
            "body": "My account is locked. Please help."
        }
        
        result = self.agent.process_121xml(input_121xml)
        
        self.assertEqual(result["classification"], "support")
        self.assertGreater(result["confidence"], 0.9)
    
    def test_classify_urgent_email(self):
        """Test that urgent emails are flagged"""
        input_121xml = {
            "email_id": "test_002",
            "body": "URGENT: Production system down!"
        }
        
        result = self.agent.process_121xml(input_121xml)
        
        self.assertEqual(result["classification"], "urgent")
    
    def test_permission_check(self):
        """Test that permission grants are respected"""
        # Create request without permission grant
        input_121xml = {
            "email_id": "test_003",
            "body": "Test email"
        }
        
        # Should fail without permission
        with self.assertRaises(PermissionDenied):
            self.agent.process_121xml(input_121xml)

if __name__ == '__main__':
    unittest.main()
```

### Integration Test (REST)

```python
import requests

def test_email_classifier_rest_api():
    """Test agent via REST endpoint"""
    
    response = requests.post(
        "http://localhost:8000/agents/email-classifier/process",
        json={
            "email_id": "msg_12345",
            "include_attachments": False
        },
        headers={
            "Authorization": "Bearer user_token_123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "confidence" in data
    assert "inference_id" in data
    
    print(f"✓ Classification: {data['classification']}")
    print(f"✓ Confidence: {data['confidence']}")
```

### Integration Test (gRPC)

```python
import grpc
from email_classifier_pb2 import EmailRequest
from email_classifier_pb2_grpc import EmailClassifierStub

def test_email_classifier_grpc():
    """Test agent via gRPC endpoint"""
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = EmailClassifierStub(channel)
    
    request = EmailRequest(
        email_id="msg_12345",
        include_attachments=False
    )
    
    response = stub.ProcessEmail(request)
    
    assert response.status == "success"
    assert response.classification in ["support", "urgent", "billing", "general"]
    assert 0 <= response.confidence <= 1
    
    print(f"✓ Classification: {response.classification}")
    print(f"✓ Confidence: {response.confidence}")
```

---

## DEPLOYMENT CHECKLIST

Before deploying your agent:

- [ ] Define agent profile (121XML)
- [ ] Define all tools (121XML profiles)
- [ ] Define workflows (121XML DAGs)
- [ ] Create permission grants (121XML)
- [ ] Add permission checks to tools
- [ ] Write unit tests (121XML input)
- [ ] Write integration tests (REST/gRPC/WebSocket)
- [ ] Test all protocol endpoints
- [ ] Enable audit logging
- [ ] Test permission revocation
- [ ] Performance test (load testing)
- [ ] Security review (permission model)
- [ ] Documentation (agent capabilities, tools, workflows)

---

## BEST PRACTICES

### 1. Define Clear Tool Boundaries

Each tool should do ONE thing and do it well. Let workflows compose tools.

✓ GOOD: `read_email`, `create_ticket`, `send_notification`
✗ BAD: `process_email_end_to_end` (does too much)

### 2. Use Content Addressing

Always reference data by immutable address, not by copying:

✓ GOOD: `<str name="email_reference">data://sha256:msg_123:raw</str>`
✗ BAD: `<map name="email_content">{full email data}</map>`

### 3. Keep Agent Logic Protocol-Agnostic

Agent reasoning should be identical regardless of protocol:

✓ GOOD: Agent returns 121XML, adapters convert to protocol
✗ BAD: Different agent logic for REST vs gRPC

### 4. Test Permission Model

Verify that permission grants are enforced:

✓ GOOD: Unauthenticated request fails with 403
✓ GOOD: Revoked permission blocks access immediately
✗ BAD: Permission checks only in one protocol

### 5. Document Tool Contracts

Each tool needs clear documentation:

- What it does
- What it requires (permissions)
- What it returns
- Failure modes
- Error handling

---

## TROUBLESHOOTING

### Agent not responding via gRPC but works via REST

**Cause:** gRPC Proto definition not matching 121XML schema

**Fix:** Regenerate Proto from 121XML tool profiles:
```bash
agentic-os generate-proto email_classifier.121xml > email_classifier.proto
```

### Permission denied on tool call

**Cause:** User doesn't have required permission grant

**Fix:** Check permission grant is active and not revoked:
```bash
agentic-os check-grant user_123 email_classifier
```

### Tool returning unexpected format

**Cause:** Tool not returning 121XML, or Schema Translator error

**Fix:** Validate tool output:
```bash
agentic-os validate-tool-output read_email tool_result.121xml
```

---

## NEXT STEPS

1. **Clone template agent:** `agentic-os new-agent my-agent`
2. **Define your tools** in 121XML
3. **Test locally** (REST endpoint by default)
4. **Add additional protocols** (gRPC, WebSocket)
5. **Deploy to production** (Kubernetes manifests included)

---

**Happy agentic building! 🚀**

**Questions? Check out:**
- AGENTIC_OS_ARCHITECTURE.md (system design)
- MASTER_DEFINITIONS.121xml (core concepts)
- /examples/email-classifier/ (complete working example)
- /plugins/ (protocol & schema adapters)
