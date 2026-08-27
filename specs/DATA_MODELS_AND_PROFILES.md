# 121XML Agentic OS - Data Models & Profiles
## Complete Specifications for All System Objects

---

## Table of Contents
1. [Core Object Profiles](#core-object-profiles)
2. [Agent Profiles](#agent-profiles)
3. [Tool Profiles](#tool-profiles)
4. [Permission & Security Profiles](#permission--security-profiles)
5. [Workflow & State Profiles](#workflow--state-profiles)
6. [Audit & Logging Profiles](#audit--logging-profiles)

---

## CORE OBJECT PROFILES

### 1. 121XML Core Object Profile
**URI:** `urn:121xml:core-object/1.0`

Defines base structure for all 121XML objects with immutable content addressing.

```xml
<map profile="urn:121xml:core-object/1.0" version="1.0">
  <str name="object_id">unique_identifier</str>
  <str name="object_type">definition|agent|tool|permission|workflow|execution</str>
  <str name="profile">urn:121xml:core-object/1.0</str>
  
  <map name="metadata">
    <str name="created_at">ISO8601 timestamp</str>
    <str name="created_by">user_id</str>
    <str name="version">version string</str>
    <str name="description">human readable description</str>
  </map>
  
  <map name="content_address">
    <str name="hash">SHA256 hash of object</str>
    <str name="format">data://sha256:HASH:TYPE</str>
  </map>
  
  <map name="signing">
    <str name="algorithm">sha256WithRSAEncryption</str>
    <str name="signature">base64 encoded signature</str>
    <str name="certificate">base64 encoded cert chain</str>
  </map>
</map>
```

---

### 2. Context Window Profile
**URI:** `urn:121xml:context-window/1.0`

Immutable context window containing conversation history and references.

```xml
<map profile="urn:121xml:context-window/1.0">
  <str name="context_id">uuid</str>
  <str name="user_id">user identifier</str>
  <str name="session_id">session identifier</str>
  
  <map name="metadata">
    <str name="created_at">ISO8601</str>
    <str name="last_updated">ISO8601</str>
    <int name="message_count">total messages</int>
    <int name="token_count">approximate tokens</int>
  </map>
  
  <seq name="message_references" of="str">
    <str>data://sha256:msg_hash_1:message</str>
    <str>data://sha256:msg_hash_2:message</str>
  </seq>
  
  <seq name="inference_references" of="str">
    <str>data://sha256:inference_hash_1:inference</str>
    <str>data://sha256:inference_hash_2:inference</str>
  </seq>
  
  <map name="state_snapshot">
    <str name="focus_topic">current topic</str>
    <map name="variables">
      <str name="key">value</str>
    </map>
  </map>
</map>
```

---

### 3. Message Profile
**URI:** `urn:121xml:message/1.0`

Immutable message object with author, content, and metadata.

```xml
<map profile="urn:121xml:message/1.0">
  <str name="message_id">uuid</str>
  <str name="session_id">session reference</str>
  <str name="author">user | agent_id | system</str>
  <str name="content_type">text | structured | multimedia</str>
  
  <str name="body">message content</str>
  
  <map name="structured_body">
    <str name="type">instruction | response | question | statement</str>
    <map name="data">
      <str name="field">value</str>
    </map>
  </map>
  
  <map name="metadata">
    <str name="timestamp">ISO8601</str>
    <str name="token_count">estimated tokens</str>
    <seq name="tags" of="str">
      <str>tag1</str>
      <str>tag2</str>
    </seq>
  </map>
  
  <map name="addressing">
    <str name="hash">SHA256</str>
    <str name="address">data://sha256:HASH:message</str>
  </map>
</map>
```

---

## AGENT PROFILES

### 4. Agent Definition Profile
**URI:** `urn:121xml:agentic-app-agent/1.0`

Defines an agentic application.

```xml
<map profile="urn:121xml:agentic-app-agent/1.0">
  <str name="agent_id">unique identifier</str>
  <str name="name">agent display name</str>
  <str name="model">claude-opus-5 | gpt-4 | gemini-pro | llama-2</str>
  <str name="description">what agent does</str>
  
  <map name="capabilities">
    <str name="reasoning">true/false</str>
    <str name="tool_use">true/false</str>
    <str name="vision">true/false</str>
    <str name="code_execution">true/false</str>
  </map>
  
  <seq name="available_tools" of="str">
    <str>data://sha256:tool_hash_1:tool</str>
    <str>data://sha256:tool_hash_2:tool</str>
  </seq>
  
  <seq name="supported_protocols" of="str">
    <str>rest</str>
    <str>grpc</str>
    <str>websocket</str>
  </seq>
  
  <map name="configuration">
    <float name="temperature">0.0-1.0</float>
    <int name="max_tokens">2000</int>
    <seq name="system_prompts" of="str">
      <str>system instruction</str>
    </seq>
  </map>
  
  <seq name="required_permissions" of="str">
    <str>read</str>
    <str>execute</str>
  </seq>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:agent</str>
  </map>
</map>
```

---

### 5. Agent State Profile
**URI:** `urn:121xml:agent-state/1.0`

Captures current state of an agent execution.

```xml
<map profile="urn:121xml:agent-state/1.0">
  <str name="state_id">uuid</str>
  <str name="agent_id">agent reference</str>
  <str name="execution_id">current execution</str>
  
  <map name="current_context">
    <str name="focus">current task focus</str>
    <int name="depth">reasoning depth</int>
    <seq name="active_tools" of="str">
      <str>tool_id</str>
    </seq>
  </map>
  
  <map name="reasoning_state">
    <seq name="reasoning_steps" of="map">
      <map>
        <int name="step">1</int>
        <str name="description">what happened</str>
        <str name="reasoning">why</str>
      </map>
    </seq>
  </map>
  
  <map name="memory">
    <seq name="short_term" of="str">
      <str>data://sha256:recent_message:message</str>
    </seq>
    <seq name="long_term" of="str">
      <str>data://sha256:important_inference:inference</str>
    </seq>
  </map>
  
  <str name="status">running | paused | completed | error</str>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:state</str>
  </map>
</map>
```

---

## TOOL PROFILES

### 6. Agentic Tool Profile
**URI:** `urn:121xml:agentic-tool/1.0`

Defines a tool that agents can invoke.

```xml
<map profile="urn:121xml:agentic-tool/1.0">
  <str name="tool_id">unique identifier</str>
  <str name="name">display name</str>
  <str name="description">what tool does</str>
  
  <map name="input_schema">
    <str name="type">object | array | string | etc</str>
    <map name="properties">
      <map name="property_name">
        <str name="type">string</str>
        <str name="description">parameter description</str>
        <str name="default">default value</str>
      </map>
    </map>
    <seq name="required" of="str">
      <str>required_param</str>
    </seq>
  </map>
  
  <map name="output_schema">
    <str name="type">object</str>
    <map name="properties">
      <map name="result">
        <str name="type">any</str>
      </map>
    </map>
  </map>
  
  <seq name="permissions_required" of="str">
    <str>read</str>
    <str>execute</str>
  </seq>
  
  <map name="execution">
    <str name="type">sync | async | batch</str>
    <int name="timeout_ms">5000</int>
    <int name="retry_count">3</int>
  </map>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:tool</str>
  </map>
</map>
```

---

### 7. Tool Execution Result Profile
**URI:** `urn:121xml:tool-execution-result/1.0`

Immutable record of tool execution.

```xml
<map profile="urn:121xml:tool-execution-result/1.0">
  <str name="execution_id">uuid</str>
  <str name="tool_id">which tool</str>
  <str name="agent_id">which agent</str>
  <str name="user_id">who invoked</str>
  
  <map name="request">
    <str name="timestamp">ISO8601</str>
    <map name="parameters">
      <str name="key">value</str>
    </map>
  </map>
  
  <map name="result">
    <str name="status">success | failure | timeout</str>
    <str name="timestamp">ISO8601</str>
    <map name="output">
      <str name="key">value</str>
    </map>
    <str name="error">null or error message</str>
  </map>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:result</str>
  </map>
</map>
```

---

## PERMISSION & SECURITY PROFILES

### 8. Permission Grant Profile
**URI:** `urn:121xml:permission-grant/1.0`

User-authorized access to system resources.

```xml
<map profile="urn:121xml:permission-grant/1.0">
  <str name="grant_id">uuid</str>
  <str name="user_id">who grants access</str>
  <str name="system_id">what system gets access</str>
  
  <seq name="permissions" of="str">
    <str>read</str>
    <str>write</str>
    <str>execute</str>
    <str>delete</str>
  </seq>
  
  <map name="scope">
    <seq name="resources" of="str">
      <str>resource_id_1</str>
      <str>resource_id_2</str>
    </seq>
    <str name="scope_type">specific | all | filtered</str>
    <map name="filters">
      <str name="key">value</str>
    </map>
  </map>
  
  <map name="temporal">
    <str name="issued_at">ISO8601</str>
    <str name="expires_at">ISO8601 or null for never</str>
  </map>
  
  <str name="status">active | revoked | expired</str>
  
  <str name="revoked_at">ISO8601 or null</str>
  <str name="revocation_reason">if revoked</str>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:grant</str>
  </map>
</map>
```

---

### 9. Encryption Metadata Profile
**URI:** `urn:121xml:encryption-metadata/1.0`

Describes encryption of sensitive data.

```xml
<map profile="urn:121xml:encryption-metadata/1.0">
  <str name="metadata_id">uuid</str>
  <str name="encrypted_resource_id">what is encrypted</str>
  
  <map name="encryption">
    <str name="algorithm">AES-256-GCM</str>
    <str name="key_derivation">PBKDF2</str>
    <str name="nonce">base64 encoded nonce</str>
    <str name="tag">authentication tag</str>
  </map>
  
  <str name="key_holder">user_id who holds decryption key</str>
  <str name="key_location">local | hsm | kms | tpm</str>
  
  <str name="location">where data stored</str>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:metadata</str>
  </map>
</map>
```

---

## WORKFLOW & STATE PROFILES

### 10. Workflow Definition Profile
**URI:** `urn:121xml:agentic-workflow/1.0`

DAG-based workflow of steps.

```xml
<map profile="urn:121xml:agentic-workflow/1.0">
  <str name="workflow_id">unique identifier</str>
  <str name="name">workflow name</str>
  <str name="description">what workflow does</str>
  
  <seq name="steps" of="map">
    <map>
      <str name="step_id">step_1</str>
      <str name="name">step name</str>
      <str name="type">tool_call | agent_reasoning | conditional | parallel | subprocess</str>
      
      <map name="action">
        <str name="agent_id">for agent_reasoning</str>
        <str name="tool_id">for tool_call</str>
        <map name="parameters">
          <str name="key">value</str>
        </map>
      </map>
      
      <map name="flow_control">
        <str name="next_on_success">next_step_id</str>
        <str name="next_on_failure">error_handler_step</str>
        <str name="timeout_ms">30000</str>
      </map>
      
      <map name="error_handling">
        <str name="strategy">retry | fallback | abort</str>
        <int name="max_retries">3</int>
      </map>
    </map>
  </seq>
  
  <map name="entry_point">
    <str name="step_id">first step</str>
  </map>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:workflow</str>
  </map>
</map>
```

---

### 11. Execution Context Profile
**URI:** `urn:121xml:execution-context/1.0`

Runtime context for agent/workflow execution.

```xml
<map profile="urn:121xml:execution-context/1.0">
  <str name="execution_id">uuid</str>
  <str name="user_id">who initiated</str>
  <str name="agent_id">which agent</str>
  <str name="workflow_id">if part of workflow</str>
  
  <map name="timing">
    <str name="started_at">ISO8601</str>
    <str name="current_step_started">ISO8601</str>
    <str name="deadline">ISO8601 or null</str>
  </map>
  
  <map name="permission_grant">
    <str name="grant_id">active permission</str>
  </map>
  
  <map name="state">
    <str name="current_step">step_id</str>
    <str name="status">running | completed | failed | timeout</str>
    <seq name="completed_steps" of="str">
      <str>step_id</str>
    </seq>
  </map>
  
  <seq name="tool_calls" of="map">
    <map>
      <str name="tool_id">tool used</str>
      <str name="status">success | failure</str>
      <str name="timestamp">ISO8601</str>
      <str name="result_address">data://sha256:...:result</str>
    </map>
  </seq>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:context</str>
  </map>
</map>
```

---

## AUDIT & LOGGING PROFILES

### 12. Audit Log Entry Profile
**URI:** `urn:121xml:audit-log-entry/1.0`

Immutable record of system action.

```xml
<map profile="urn:121xml:audit-log-entry/1.0">
  <str name="entry_id">uuid</str>
  <str name="timestamp">ISO8601</str>
  
  <map name="actor">
    <str name="user_id">who did action</str>
    <str name="system_id">or which system</str>
  </map>
  
  <map name="action">
    <str name="action_type">create | read | update | delete | execute</str>
    <str name="resource">what was accessed</str>
    <str name="resource_type">message | agent | tool | grant</str>
  </map>
  
  <map name="authorization">
    <str name="permission_required">what permission</str>
    <str name="grant_id">which grant checked</str>
    <str name="decision">allowed | denied</str>
  </map>
  
  <map name="result">
    <str name="status">success | failure</str>
    <str name="error">null or error message</str>
  </map>
  
  <map name="metadata">
    <str name="ip_address">source IP</str>
    <str name="user_agent">browser/client</str>
    <seq name="tags" of="str">
      <str>security_relevant</str>
    </seq>
  </map>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:audit</str>
  </map>
  
  <map name="signature">
    <str name="hash">chain hash to previous entry</str>
    <str name="signature">digital signature</str>
  </map>
</map>
```

---

### 13. System Event Profile
**URI:** `urn:121xml:system-event/1.0`

Log of system-level events.

```xml
<map profile="urn:121xml:system-event/1.0">
  <str name="event_id">uuid</str>
  <str name="timestamp">ISO8601</str>
  
  <str name="event_type">agent_registered | tool_executed | error_occurred | threshold_exceeded</str>
  
  <map name="event_data">
    <str name="key">value</str>
  </map>
  
  <str name="severity">info | warning | error | critical</str>
  
  <seq name="references" of="str">
    <str>data://sha256:related_object:type</str>
  </seq>
  
  <map name="addressing">
    <str name="address">data://sha256:HASH:event</str>
  </map>
</map>
```

---

## IMPLEMENTATION NOTES

### Immutability Guarantee
All profiles include a `content_address` section with SHA256 hash. Once a profile is created:
- The hash is immutable
- Any modification changes the hash
- References always point to specific version
- Perfect auditability

### References Pattern
All cross-references use content addresses:
```
data://sha256:ABC123DEF456:message
data://sha256:XYZ789:tool
data://sha256:MNO456:agent
```

No direct object embedding. This ensures:
- Zero data duplication
- Perfect referential integrity
- User data sovereignty (only hashes transmitted)
- Infinite scalability

### Deterministic Hashing
All profiles use sorted JSON for SHA256 computation:
```json
{
  "a_field": "first alphabetically",
  "b_field": "second",
  "z_field": "last"
}
```

This ensures identical objects always produce identical hashes.

### Profile Evolution
When updating a profile specification:
1. Increment version in URI: `urn:121xml:profile/2.0`
2. Maintain backward compatibility in engine
3. New hash reflects schema changes
4. No breaking changes to existing references

---

## USAGE EXAMPLES

### Creating a Tool Profile

```python
tool = {
    "profile": "urn:121xml:agentic-tool/1.0",
    "tool_id": "tool_send_email",
    "name": "Send Email",
    "description": "Send email message",
    "input_schema": {
        "type": "object",
        "properties": {
            "to": {"type": "string"},
            "subject": {"type": "string"},
            "body": {"type": "string"}
        },
        "required": ["to", "subject", "body"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message_id": {"type": "string"}
        }
    },
    "permissions_required": ["execute"],
    "execution": {
        "type": "async",
        "timeout_ms": 5000,
        "retry_count": 3
    }
}

# Compute content address
address = ContentAddress.compute(tool, "tool")
# Result: data://sha256:ABC123...:tool
```

### Permission Grant Flow

```python
# User explicitly grants permission
grant = PermissionGrant(
    grant_id="grant_001",
    user_id="user_123",
    system_id="engine",
    permissions=[PermissionType.READ, PermissionType.EXECUTE],
    created_at=datetime.utcnow(),
    expires_at=datetime.utcnow() + timedelta(hours=24)
)

# Engine checks grant before any access
if grant.is_valid() and grant.has_permission(PermissionType.EXECUTE):
    # Proceed with execution
    execute_tool(...)
else:
    # Deny access
    log_audit("denied")
```

---

## COMPLIANCE NOTES

### GDPR Compliance
- Data address stored (not raw data)
- User-held encryption keys
- Instant deletion via reference removal
- Full audit trail

### HIPAA Compliance
- End-to-end encryption required
- Immutable audit logs
- Access controls at permission level
- Entity authentication via signatures

### CCPA Compliance
- User control over data storage location
- Right to deletion implemented
- Data portability via 121XML references
- No unauthorized secondary use

---

**Status:** Complete Specification Package  
**Version:** 1.0  
**Last Updated:** August 6, 2026
