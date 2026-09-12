# 121XML Agentic OS - Deployment & Getting Started Guide
## Complete Implementation Instructions

---

## QUICK START (5 Minutes)

### 1. Installation

```bash
# Clone repository
git clone https://github.com/121xml/agentic-os.git
cd agentic-os

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Server

```bash
# Start REST API server
python -m uvicorn 121xml_agentic_os_api:app --reload --host 0.0.0.0 --port 8000

# Server running at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 3. Create Permission Grant

```bash
curl -X POST http://localhost:8000/permissions/grant \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "system_id": "engine",
    "permissions": ["read", "execute"],
    "expires_in_hours": 24
  }'

# Response:
# {
#   "grant_id": "grant_abc123...",
#   "status": "active",
#   "expires_at": "2026-08-07T13:00:00"
# }
```

### 4. Register Tool

```bash
curl -X POST http://localhost:8000/tools/register \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "tool_hello",
    "name": "Hello Tool",
    "description": "Simple hello world tool",
    "input_schema": {
      "type": "object",
      "properties": {
        "name": {"type": "string"}
      }
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "greeting": {"type": "string"}
      }
    },
    "permissions_required": ["execute"]
  }'
```

### 5. Execute Tool

```bash
curl -X POST http://localhost:8000/agents/agent_001/execute-tool \
  -H "Content-Type: application/json" \
  -H "X-Grant-Id: grant_abc123..." \
  -d '{
    "tool_id": "tool_hello",
    "parameters": {
      "name": "World"
    }
  }'
```

---

## DOCKER DEPLOYMENT

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY 121xml_agentic_os_*.py .
COPY 121xml_plugin_sdk.py .

# Expose ports
EXPOSE 8000 50051 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "121xml_agentic_os_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t 121xml-agentic-os:latest .

# Run container
docker run -d \
  --name 121xml-engine \
  -p 8000:8000 \
  -p 50051:50051 \
  -p 8001:8001 \
  -e LOG_LEVEL=INFO \
  121xml-agentic-os:latest

# View logs
docker logs -f 121xml-engine

# Stop container
docker stop 121xml-engine
```

---

## KUBERNETES DEPLOYMENT

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: 121xml-config
namespace: agentic-os
data:
  LOG_LEVEL: "INFO"
  REST_PORT: "8000"
  GRPC_PORT: "50051"
  WEBSOCKET_PORT: "8001"
  MAX_WORKERS: "10"
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: 121xml-engine
  namespace: agentic-os
spec:
  replicas: 3
  selector:
    matchLabels:
      app: 121xml-engine
  template:
    metadata:
      labels:
        app: 121xml-engine
    spec:
      containers:
      - name: engine
        image: 121xml-agentic-os:latest
        imagePullPolicy: Always
        
        ports:
        - name: rest
          containerPort: 8000
        - name: grpc
          containerPort: 50051
        - name: websocket
          containerPort: 8001
        
        envFrom:
        - configMapRef:
            name: 121xml-config
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /status
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - 121xml-engine
              topologyKey: kubernetes.io/hostname
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: 121xml-engine-service
  namespace: agentic-os
spec:
  type: LoadBalancer
  selector:
    app: 121xml-engine
  ports:
  - name: rest
    port: 80
    targetPort: 8000
  - name: grpc
    port: 50051
    targetPort: 50051
  - name: websocket
    port: 8001
    targetPort: 8001
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace agentic-os

# Apply configuration
kubectl apply -f k8s-configmap.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml

# Check deployment
kubectl get deployments -n agentic-os
kubectl get pods -n agentic-os
kubectl get svc -n agentic-os

# View logs
kubectl logs -f deployment/121xml-engine -n agentic-os
```

---

## DEVELOPMENT SETUP

### Project Structure

```
121xml-agentic-os/
├── 121xml_agentic_os_core.py          # Core engine
├── 121xml_agentic_os_api.py           # REST API
├── 121xml_plugin_sdk.py                # Plugin framework
├── requirements.txt                    # Dependencies
├── tests/
│   ├── test_core.py                   # Core tests
│   ├── test_api.py                    # API tests
│   └── test_plugins.py                # Plugin tests
├── examples/
│   ├── hello_agent.py                 # Example agent
│   ├── email_tool_plugin.py            # Example tool
│   └── workflow_example.py             # Example workflow
├── docs/
│   ├── API.md                          # API documentation
│   ├── PLUGIN_DEVELOPMENT.md           # Plugin guide
│   └── DEPLOYMENT.md                   # Deployment guide
└── README.md
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run with logging
pytest -v -s
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test
pytest

# 3. Format code
black .
flake8 .
mypy --strict .

# 4. Commit changes
git add .
git commit -m "Add my feature"

# 5. Create pull request
git push origin feature/my-feature
```

---

## PLUGIN DEVELOPMENT

### Create Custom Tool Plugin

```python
# my_custom_tool.py
from 121xml_plugin_sdk import ToolPlugin, PluginMetadata, ToolCapability, PluginType

class MyCustomToolPlugin(ToolPlugin):
    def __init__(self):
        metadata = PluginMetadata(
            plugin_id="plugin_my_custom_tool",
            plugin_type=PluginType.TOOL,
            name="My Custom Tool",
            version="1.0.0",
            author="Your Name",
            description="My custom tool plugin"
        )
        super().__init__(metadata)
        
        # Define tool capability
        self.capabilities["my_action"] = ToolCapability(
            name="my_action",
            description="Perform custom action",
            input_schema={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                }
            },
            output_schema={
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                }
            },
            permissions=["execute"]
        )

    def initialize(self) -> bool:
        print("Initializing custom tool plugin")
        return True

    def shutdown(self):
        print("Shutting down custom tool plugin")

    def validate(self) -> bool:
        return len(self.capabilities) > 0

    def get_tools(self):
        return list(self.capabilities.keys())

    def get_tool_capability(self, tool_name):
        return self.capabilities.get(tool_name)

    def execute(self, tool_name, parameters):
        if tool_name == "my_action":
            return {
                "result": f"Processed: {parameters.get('input')}"
            }
        return {"error": f"Unknown tool: {tool_name}"}
```

### Register Plugin

```python
from 121xml_agentic_os_core import AgenticEngine
from my_custom_tool import MyCustomToolPlugin

# Initialize engine
engine = AgenticEngine()

# Create and register plugin
plugin = MyCustomToolPlugin()
engine.register_tool(ToolDefinition(
    tool_id="plugin_my_custom_tool",
    name="My Custom Tool",
    description="My custom tool",
    input_schema={...},
    output_schema={...},
    permissions_required=[PermissionType.EXECUTE],
    handler=plugin.execute
))
```

### Create Custom Protocol Adapter

```python
# my_protocol.py
from 121xml_plugin_sdk import ProtocolAdapterPlugin, PluginMetadata, PluginType

class MyProtocolAdapter(ProtocolAdapterPlugin):
    def __init__(self):
        metadata = PluginMetadata(
            plugin_id="plugin_my_protocol",
            plugin_type=PluginType.PROTOCOL_ADAPTER,
            name="My Protocol Adapter",
            version="1.0.0",
            author="Your Name",
            description="Adapter for custom protocol"
        )
        super().__init__(metadata)

    def initialize(self) -> bool:
        return True

    def shutdown(self):
        pass

    def validate(self) -> bool:
        return True

    def get_protocol_name(self) -> str:
        return "myprotocol"

    def get_supported_versions(self) -> list:
        return ["1.0"]

    def to_121xml(self, request: dict) -> dict:
        # Convert from your protocol to 121XML
        return {
            "protocol": "myprotocol",
            "data": request
        }

    def from_121xml(self, response: dict) -> dict:
        # Convert from 121XML to your protocol
        return response.get("data", response)
```

---

## EXAMPLE: EMAIL CLASSIFIER AGENT

### Step 1: Register Tool

```python
# Register email reading tool
engine.register_tool(ToolDefinition(
    tool_id="tool_read_email",
    name="Read Email",
    description="Read an email message",
    input_schema={
        "type": "object",
        "properties": {
            "email_id": {"type": "string"}
        }
    },
    output_schema={
        "type": "object",
        "properties": {
            "from": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"}
        }
    },
    permissions_required=[PermissionType.READ],
    handler=lambda p: {
        "from": "sender@example.com",
        "subject": "Test Email",
        "body": "This is a test message"
    }
))

# Register classifier tool
engine.register_tool(ToolDefinition(
    tool_id="tool_classify_email",
    name="Classify Email",
    description="Classify email by category",
    input_schema={
        "type": "object",
        "properties": {
            "subject": {"type": "string"},
            "body": {"type": "string"}
        }
    },
    output_schema={
        "type": "object",
        "properties": {
            "category": {"type": "string"},
            "confidence": {"type": "number"}
        }
    },
    permissions_required=[PermissionType.EXECUTE],
    handler=lambda p: {
        "category": "urgent",
        "confidence": 0.92
    }
))
```

### Step 2: Register Agent

```python
# Register email classifier agent
engine.register_agent(AgentDefinition(
    agent_id="agent_email_classifier",
    name="Email Classifier",
    model="claude-opus-5",
    description="Automatically classifies incoming emails",
    available_tools=[
        "tool_read_email",
        "tool_classify_email"
    ],
    supported_protocols=["rest", "grpc", "websocket"]
))
```

### Step 3: Define Workflow

```python
workflow = {
    "profile": "urn:121xml:agentic-workflow/1.0",
    "workflow_id": "wf_email_classification",
    "name": "Email Classification Workflow",
    "steps": [
        {
            "step_id": "step_1_read",
            "type": "tool_call",
            "tool_id": "tool_read_email",
            "next_on_success": "step_2_classify"
        },
        {
            "step_id": "step_2_classify",
            "type": "tool_call",
            "tool_id": "tool_classify_email",
            "next_on_success": None
        }
    ]
}
```

### Step 4: Execute

```bash
# Create permission grant
GRANT_ID=$(curl -X POST http://localhost:8000/permissions/grant \
  -d '{"user_id":"user_001","permissions":["read","execute"]}' \
  | jq -r '.grant_id')

# Execute workflow
curl -X POST http://localhost:8000/agents/agent_email_classifier/execute-tool \
  -H "X-Grant-Id: $GRANT_ID" \
  -d '{"tool_id":"tool_read_email","parameters":{"email_id":"123"}}'
```

---

## MONITORING & OBSERVABILITY

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed status
curl http://localhost:8000/status
```

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("121xml")

# Logs automatically captured:
# - Permission checks
# - Tool executions
# - Workflow steps
# - Errors and exceptions
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram
import time

# Tool execution metrics
tool_executions = Counter('tool_executions_total', 'Total tool executions', ['tool_id', 'status'])
tool_duration = Histogram('tool_execution_seconds', 'Tool execution duration', ['tool_id'])

# Capture metrics
tool_executions.labels(tool_id='tool_send_email', status='success').inc()
```

### Audit Trail Query

```bash
# Get all audit entries
curl http://localhost:8000/audit

# Get audit entries for specific user
curl http://localhost:8000/audit?user_id=user_001
```

---

## CONFIGURATION

### Environment Variables

```bash
# Server
REST_PORT=8000
GRPC_PORT=50051
WEBSOCKET_PORT=8001
HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security
REQUIRE_AUTH=true
TOKEN_EXPIRY_HOURS=24
MAX_PERMISSION_DURATION=720

# Performance
MAX_WORKERS=10
EXECUTION_TIMEOUT_MS=30000
MEMORY_CACHE_SIZE=1000

# Database
DB_URL=sqlite:///121xml.db
DB_ECHO=false
```

### Config File

```yaml
# config.yaml
server:
  rest_port: 8000
  grpc_port: 50051
  websocket_port: 8001
  host: 0.0.0.0

logging:
  level: INFO
  format: json
  file: 121xml.log

security:
  require_auth: true
  token_expiry_hours: 24

performance:
  max_workers: 10
  execution_timeout_ms: 30000
  memory_cache_size: 1000

storage:
  audit_log_retention_days: 90
  encryption_algorithm: AES-256-GCM
```

---

## TROUBLESHOOTING

### Permission Denied

```python
# Check permission grant
grant = engine.permission_manager.grants.get(grant_id)
if not grant:
    print("Grant not found")
elif not grant.is_valid():
    print("Grant expired or revoked")
elif not grant.has_permission(PermissionType.EXECUTE):
    print("Missing execute permission")

# Check audit log
audit_entries = engine.permission_manager.get_audit_log(user_id)
for entry in audit_entries:
    print(f"{entry.status}: {entry.action}")
```

### Tool Execution Failure

```python
# Check tool exists
if tool_id not in engine.tools:
    print(f"Tool not found: {tool_id}")

# Validate parameters
tool = engine.tools[tool_id]
import jsonschema
try:
    jsonschema.validate(parameters, tool.input_schema)
except jsonschema.ValidationError as e:
    print(f"Invalid parameters: {e}")

# Check permissions
for perm in tool.permissions_required:
    if not permission_grant.has_permission(perm):
        print(f"Missing permission: {perm.value}")
```

### Performance Issues

```python
# Check engine status
status = engine.get_status()
print(f"Active executions: {status['total_executions']}")

# Monitor tool execution time
import time
start = time.time()
result = engine.execute_tool(tool_id, parameters, context)
duration_ms = (time.time() - start) * 1000
print(f"Tool execution took {duration_ms}ms")

# Check memory usage
import sys
memory_usage = sys.getsizeof(engine.memory_manager.memory)
print(f"Memory usage: {memory_usage} bytes")
```

---

## NEXT STEPS

1. **Read the full API documentation** at `docs/API.md`
2. **Build your first plugin** using `plugin_sdk.py`
3. **Deploy to production** using Docker/Kubernetes
4. **Monitor and scale** using provided tools
5. **Join community** for support and contributions

---

**Status:** Production Ready  
**Version:** 1.0  
**Last Updated:** August 6, 2026

For more information visit: https://121xml.com

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*