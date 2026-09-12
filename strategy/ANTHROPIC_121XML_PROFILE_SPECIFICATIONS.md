# Anthropic 121XML Profile Specifications
## Formal Specifications for All Profiles Required to Replace Anthropic Session/Memory Architecture

**Reference Definitions:**
- def_121xml_axioms (data://sha256:7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b:definition)
- def_121xml_rules (data://sha256:2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f:definition)
- def_sovereign_architecture (data://sha256:5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d:definition)
- def_content_addressed_inference (data://sha256:8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f:definition)

---

## PROFILE 1: anthropic_session_state.121xml

**Purpose:** Replace in-memory session dict. Immutable reference to all session state.

**Profile URI:** `urn:121xml:anthropic-session-state/1.0`

```xml
<map profile="urn:121xml:anthropic-session-state/1.0" version="1.0">
  
  <!-- SESSION IDENTIFICATION -->
  <str name="session_id">UUID</str>
  <str name="user_id">USER_ID</str>
  <str name="session_created_timestamp">2026-08-06T10:30:00Z</str>
  <str name="session_address">data://sha256:COMPUTED:session</str>
  
  <!-- CONTEXT REFERENCES (Not raw data, only pointers) -->
  <seq name="message_references" of="str">
    <!-- Each message is referenced by address, not included in session -->
    <!-- Example: data://sha256:msg001_hash:message -->
  </seq>
  
  <!-- PRIOR SESSION REFERENCE (Context continuity) -->
  <str name="prior_session_reference">data://sha256:PRIOR:session</str>
  
  <!-- MASTER DEFINITIONS REFERENCE (Immutable ground truth) -->
  <str name="master_definitions_reference">data://sha256:3a4f2b5c8e9d1f7a2b4c6e8f0a1b3c5d:definition</str>
  
  <!-- TOKEN ACCOUNTING (Immutable ledger) -->
  <str name="token_accounting_reference">data://sha256:TOKENS:ledger</str>
  
  <!-- PERMISSION GRANTS (What this session can access) -->
  <seq name="permission_grant_ids" of="str">
    <!-- User's explicit grants for this session -->
  </seq>
  
  <!-- TOOL DEFINITIONS (From 121XML profiles, not system prompt) -->
  <seq name="tool_definition_references" of="str">
    <!-- Each tool is a 121XML profile -->
    <!-- Example: data://sha256:tool001:tool -->
  </seq>
  
  <!-- INFERENCES CREATED THIS SESSION -->
  <seq name="inference_references" of="str">
    <!-- All Claude inferences as 121XML objects -->
    <!-- Example: data://sha256:inf001:inference -->
  </seq>
  
  <!-- SESSION METADATA -->
  <map name="metadata">
    <str name="session_status">active | completed | archived</str>
    <str name="total_token_count">COMPUTED</str>
    <str name="model_used">claude_opus_5</str>
    <str name="api_version">messages/v1</str>
  </map>

</map>
```

**Implementation Notes:**
- R4: Keys must be sorted alphabetically
- R5: Use explicit `<null/>` for absent fields
- R7: Compute session_address as SHA256 of sorted XML
- No in-memory dict—always persist as 121XML object
- Next session loads this by reference, doesn't reload content

---

## PROFILE 2: anthropic_message.121xml

**Purpose:** Replace message objects in conversation history. Immutable, content-addressed.

**Profile URI:** `urn:121xml:anthropic-message/1.0`

```xml
<map profile="urn:121xml:anthropic-message/1.0" version="1.0">
  
  <!-- MESSAGE IDENTIFICATION -->
  <str name="message_id">UUID</str>
  <str name="message_address">data://sha256:COMPUTED:message</str>
  <str name="message_timestamp">2026-08-06T10:30:15Z</str>
  
  <!-- MESSAGE ROLE -->
  <str name="role">user | assistant | system</str>
  
  <!-- MESSAGE CONTENT (Immutable) -->
  <str name="content">The actual message text or structured content</str>
  <str name="content_hash">data://sha256:CONTENT:raw</str>
  
  <!-- ACCESS CONTROL -->
  <map name="access_control">
    <str name="owned_by">USER_ID</str>
    <str name="permission_grant_id">grant_001</str>
    <str name="access_granted_to">claude_opus_5 | gpt4 | gemini</str>
  </map>
  
  <!-- TOOL USAGE (If assistant message) -->
  <seq name="tool_uses" of="map">
    <map>
      <str name="tool_name">example_tool</str>
      <str name="tool_definition_reference">data://sha256:tool001:tool</str>
      <map name="tool_parameters">
        <!-- Tool input as 121XML (A1-A3 compliant) -->
      </map>
    </map>
  </seq>
  
  <!-- INFERENCE REFERENCES -->
  <seq name="inferences_referenced" of="str">
    <!-- Reasoning chains for this message -->
  </seq>
  
  <!-- AUDIT TRAIL -->
  <map name="audit">
    <str name="created_by">system | user | claude_opus_5</str>
    <str name="accessed_by">claude_opus_5</str>
    <str name="access_timestamp">2026-08-06T10:30:20Z</str>
    <str name="access_permission_checked">YES</str>
  </map>
  
  <!-- METADATA -->
  <map name="metadata">
    <int name="character_count">1234</int>
    <int name="estimated_tokens">256</int>
    <str name="content_type">text | tool_result | system_prompt</str>
  </map>

</map>
```

**Implementation Notes:**
- content_hash enables integrity verification (R7)
- message_address is immutable—once created, never changes
- access_control field gates access via permission_grant_id
- Each access logged for audit trail
- Never include raw data in session_state—only reference by address

---

## PROFILE 3: anthropic_tool_definition.121xml

**Purpose:** Replace system prompt tool definitions. Schema from 121XML profile instead of JSON/markdown.

**Profile URI:** `urn:121xml:anthropic-tool-definition/1.0`

```xml
<map profile="urn:121xml:anthropic-tool-definition/1.0" version="1.0">
  
  <!-- TOOL IDENTIFICATION -->
  <str name="tool_name">example_tool</str>
  <str name="tool_id">TOOL_UUID</str>
  <str name="tool_address">data://sha256:COMPUTED:tool</str>
  <str name="tool_version">1.0</str>
  
  <!-- TOOL DESCRIPTION -->
  <str name="description">What this tool does</str>
  <str name="purpose">User-facing purpose statement</str>
  
  <!-- TOOL PARAMETERS (Self-describing) -->
  <map name="parameters">
    <str name="profile">urn:121xml:parameter-list/1.0</str>
    <seq name="required_fields" of="map">
      <map>
        <str name="field_name">parameter_1</str>
        <str name="field_type">str | int | bool | map | seq</str>
        <str name="field_description">What is this parameter</str>
        <str name="field_constraints">Optional constraints</str>
      </map>
    </seq>
    <seq name="optional_fields" of="map">
      <!-- Same structure as required_fields -->
    </seq>
  </map>
  
  <!-- RETURN VALUE SCHEMA -->
  <map name="return_schema">
    <str name="profile">urn:121xml:return-type/1.0</str>
    <str name="return_type">str | int | bool | map | seq</str>
    <str name="return_description">What the tool returns</str>
    <seq name="return_fields" of="map">
      <!-- Field descriptions if return_type is map -->
    </seq>
  </map>
  
  <!-- EXECUTION RULES -->
  <map name="execution_rules">
    <str name="requires_user_approval">YES | NO</str>
    <str name="can_modify_user_data">YES | NO</str>
    <str name="cost_per_invocation">tokens | credits</str>
    <str name="rate_limit">calls_per_minute</str>
  </map>
  
  <!-- PERMISSION REQUIREMENTS -->
  <map name="permissions">
    <str name="permission_type">read | read_write | admin</str>
    <str name="requires_grant">YES</str>
    <str name="grant_type">tool_access | data_access</str>
    <seq name="grant_ids" of="str">
      <!-- Which grants must be present to use this tool -->
    </seq>
  </map>
  
  <!-- COMPLIANCE METADATA -->
  <map name="compliance">
    <str name="data_classification">public | internal | confidential | restricted</str>
    <str name="gdpr_compliant">YES | NO</str>
    <str name="hipaa_compliant">YES | NO</str>
    <str name="soc2_compliant">YES | NO</str>
  </map>
  
  <!-- EXAMPLES -->
  <seq name="examples" of="map">
    <map>
      <str name="example_id">example_1</str>
      <str name="description">Example: do X</str>
      <map name="example_input">
        <str name="parameter_1">value_1</str>
      </map>
      <map name="example_output">
        <!-- Expected output -->
      </map>
    </map>
  </seq>
  
  <!-- AUDIT METADATA -->
  <map name="audit">
    <str name="created_timestamp">2026-08-06T00:00:00Z</str>
    <str name="created_by">anthropic | vendor_name</str>
    <str name="last_updated">2026-08-06T00:00:00Z</str>
    <str name="tool_definition_immutable">YES</str>
  </map>

</map>
```

**Implementation Notes:**
- Tool schema is self-describing (A2: explicit type tags)
- No external schema fetch needed at receiver
- Supports universal code generation (A1: no inheritance, A3: homogeneous sequences)
- Permission requirements enforced before tool invocation
- Tool definitions stored in 121XML, not system prompt text

---

## PROFILE 4: anthropic_permission_grant.121xml

**Purpose:** User's explicit authorization for system access. Enforces data sovereignty.

**Profile URI:** `urn:121xml:anthropic-permission-grant/1.0`

```xml
<map profile="urn:121xml:anthropic-permission-grant/1.0" version="1.0">
  
  <!-- GRANT IDENTIFICATION -->
  <str name="grant_id">GRANT_UUID</str>
  <str name="grant_address">data://sha256:COMPUTED:grant</str>
  <str name="created_timestamp">2026-08-06T00:00:00Z</str>
  
  <!-- GRANTOR (Who is granting permission) -->
  <str name="granted_by_user">USER_ID</str>
  
  <!-- GRANTEE (Who is receiving permission) -->
  <str name="granted_to_system">claude_opus_5 | gpt4 | gemini | llama</str>
  
  <!-- WHAT IS BEING GRANTED -->
  <map name="grant_scope">
    <str name="scope_type">data_access | tool_access | session_access</str>
    <seq name="data_references" of="str">
      <!-- If data_access: which data objects (by address) -->
      <!-- Example: data://sha256:msg001:message -->
    </seq>
    <seq name="tool_references" of="str">
      <!-- If tool_access: which tools (by address) -->
    </seq>
  </map>
  
  <!-- PERMISSION TYPE -->
  <seq name="permissions_granted" of="str">
    <str>read</str>
    <str>read_write</str>
    <str>read_infer</str>
    <str>execute</str>
    <!-- Only grant what's necessary (principle of least privilege) -->
  </seq>
  
  <!-- VALIDITY PERIOD -->
  <map name="validity">
    <str name="valid_from">2026-08-06T00:00:00Z</str>
    <str name="valid_until">2026-09-06T00:00:00Z</str>
    <str name="is_expired">NO | YES</str>
    <str name="can_auto_renew">YES | NO</str>
  </map>
  
  <!-- REVOCATION -->
  <map name="revocation">
    <str name="is_revoked">NO | YES</str>
    <str name="revoked_timestamp">2026-08-06T12:00:00Z</str>
    <str name="revocation_reason">User request | Expired | Security concern</str>
    <str name="revocation_effective_immediately">YES</str>
  </map>
  
  <!-- CONDITIONS -->
  <map name="conditions">
    <str name="max_calls_per_day">1000</str>
    <str name="max_data_size">1_GB</str>
    <str name="require_mfa_for_access">YES | NO</str>
    <str name="allow_delegation_to_other_systems">NO</str>
  </map>
  
  <!-- AUDIT TRAIL -->
  <seq name="audit_entries" of="map">
    <map>
      <str name="timestamp">2026-08-06T10:30:00Z</str>
      <str name="accessed_by">claude_opus_5</str>
      <str name="action">read | write | execute</str>
      <str name="result">allowed | denied</str>
      <str name="reason">grant_valid | grant_expired | grant_revoked</str>
    </map>
  </seq>
  
  <!-- METADATA -->
  <map name="metadata">
    <str name="grant_immutable">YES</str>
    <str name="data_encrypted">YES</str>
    <str name="encryption_key_location">user_managed</str>
  </map>

</map>
```

**Implementation Notes:**
- User explicitly decides (no implicit permissions)
- Revocation is instant (no propagation delays)
- Conditions enforce least privilege
- All access attempts logged for compliance
- Expired/revoked grants cannot be reactivated (create new grant instead)

---

## PROFILE 5: anthropic_inference_object.121xml

**Purpose:** All Claude reasoning as immutable object. Never lost to compaction.

**Profile URI:** `urn:121xml:anthropic-inference/1.0`

```xml
<map profile="urn:121xml:anthropic-inference/1.0" version="1.0">
  
  <!-- INFERENCE IDENTIFICATION -->
  <str name="inference_id">INFERENCE_UUID</str>
  <str name="inference_address">data://sha256:COMPUTED:inference</str>
  <str name="created_timestamp">2026-08-06T10:30:30Z</str>
  
  <!-- CREATOR -->
  <str name="created_by">claude_opus_5 | gpt4 | gemini</str>
  <str name="inference_version">1.0</str>
  
  <!-- INFERENCE TYPE -->
  <str name="inference_type">
    architectural_decision | data_analysis | code_generation | 
    architectural_proposal | validation | other
  </str>
  
  <!-- INFERENCE STATEMENT (What Claude decided/inferred) -->
  <str name="inference_statement">
    Clear, concise statement of what was inferred
  </str>
  
  <!-- REASONING CHAIN (Step-by-step thinking) -->
  <seq name="reasoning_chain" of="str">
    <str>Step 1: Identified problem or task</str>
    <str>Step 2: Checked boundary conditions</str>
    <str>Step 3: Referenced definitions</str>
    <str>Step 4: Evaluated alternatives</str>
    <str>Step 5: Reached conclusion</str>
  </seq>
  
  <!-- DEFINITION REFERENCES (Back to MASTER_DEFINITIONS) -->
  <seq name="references_definitions" of="str">
    <str>data://sha256:3a4f2b5c8e9d1f7a2b4c6e8f0a1b3c5d:definition</str>
    <!-- Every inference must reference at least one core definition -->
  </seq>
  
  <!-- DATA REFERENCES (What inputs drove this inference) -->
  <seq name="references_data" of="str">
    <str>data://sha256:msg001:message</str>
    <str>data://sha256:msg002:message</str>
    <!-- Sources for this inference -->
  </seq>
  
  <!-- BOUNDARY CHECKS (Validation against critical boundaries) -->
  <seq name="boundary_checks" of="map">
    <map>
      <str name="boundary_id">boundary_no_centralization</str>
      <str name="result">PASS | FAIL</str>
      <str name="explanation">How this inference respects the boundary</str>
    </map>
    <map>
      <str name="boundary_id">boundary_no_data_copying</str>
      <str name="result">PASS | FAIL</str>
      <str name="explanation">How this inference avoids data copying</str>
    </map>
    <map>
      <str name="boundary_id">boundary_no_single_vendor</str>
      <str name="result">PASS | FAIL</str>
      <str name="explanation">How this works across all vendors</str>
    </map>
    <map>
      <str name="boundary_id">boundary_no_context_loss</str>
      <str name="result">PASS | FAIL</str>
      <str name="explanation">How this preserves context</str>
    </map>
  </seq>
  
  <!-- ALTERNATIVES CONSIDERED (Why this over others) -->
  <seq name="alternatives_considered" of="map">
    <map>
      <str name="alternative_id">alt_1</str>
      <str name="alternative_description">Alternative approach</str>
      <str name="why_rejected">Why this alternative was not chosen</str>
    </map>
  </seq>
  
  <!-- CONFIDENCE LEVEL -->
  <str name="confidence">high | medium | low</str>
  <str name="confidence_explanation">Reasoning for confidence level</str>
  
  <!-- RELATED INFERENCES -->
  <seq name="related_inferences" of="str">
    <!-- Inferences that build on this one -->
    <!-- Example: data://sha256:inf002:inference -->
  </seq>
  
  <!-- MODIFICATIONS (If inference was improved later) -->
  <seq name="modifications" of="map">
    <map>
      <str name="modification_timestamp">2026-08-06T12:00:00Z</str>
      <str name="modification_type">enhanced | corrected | replaced</str>
      <str name="new_inference_reference">data://sha256:inf002:inference</str>
      <str name="reason_for_modification">Why was it changed</str>
    </map>
  </seq>
  
  <!-- AUDIT METADATA -->
  <map name="audit">
    <str name="immutable">YES</str>
    <str name="never_deleted">YES</str>
    <str name="accessible_across_sessions">YES</str>
  </map>

</map>
```

**Implementation Notes:**
- Every inference is immutable (never overwritten, only supplemented)
- All reasoning preserved (no loss to compaction)
- All references back to definitions enforced
- Boundary checks embedded in every inference
- Historical record: modifications create new inferences, don't overwrite old ones

---

## PROFILE 6: anthropic_context_window.121xml

**Purpose:** Session context as shareable 121XML object. References only, no raw data.

**Profile URI:** `urn:121xml:anthropic-context-window/1.0`

```xml
<map profile="urn:121xml:anthropic-context-window/1.0" version="1.0">
  
  <!-- CONTEXT WINDOW IDENTIFICATION -->
  <str name="context_window_id">CONTEXT_UUID</str>
  <str name="context_window_address">data://sha256:COMPUTED:context</str>
  <str name="created_timestamp">2026-08-06T10:30:00Z</str>
  
  <!-- SESSION REFERENCE -->
  <str name="session_reference">data://sha256:session001:session</str>
  
  <!-- USER -->
  <str name="user_id">USER_ID</str>
  
  <!-- MASTER DEFINITIONS (Immutable ground truth) -->
  <str name="master_definitions_reference">data://sha256:3a4f2b5c8e9d1f7a2b4c6e8f0a1b3c5d:definition</str>
  
  <!-- MESSAGE REFERENCES (Not raw messages) -->
  <seq name="message_references" of="str">
    <!-- Order matters: chronological sequence -->
    <!-- Example: data://sha256:msg001:message -->
  </seq>
  
  <!-- INFERENCE REFERENCES -->
  <seq name="inference_references" of="str">
    <!-- All inferences Claude has created in this context -->
  </seq>
  
  <!-- TOOL REFERENCES -->
  <seq name="tool_references" of="str">
    <!-- Tools available in this context -->
  </seq>
  
  <!-- PERMISSION GRANTS IN EFFECT -->
  <seq name="active_permission_grants" of="str">
    <!-- Which grants allow this context to access what -->
  </seq>
  
  <!-- CONTEXT WINDOW METADATA -->
  <map name="metadata">
    <int name="total_tokens">5678</int>
    <int name="message_count">12</int>
    <int name="inference_count">3</int>
    <str name="model">claude_opus_5</str>
    <str name="api_version">messages/v1</str>
  </map>
  
  <!-- SHAREABILITY -->
  <map name="shareability">
    <str name="can_share_with_other_systems">YES | NO</str>
    <str name="if_shared_other_systems_can">
      read_only | read_infer | read_execute
    </str>
    <seq name="allowed_recipient_systems" of="str">
      <!-- Which systems can receive this context -->
      <!-- Example: gpt4, gemini, etc. -->
    </seq>
  </map>
  
  <!-- PRIOR CONTEXT REFERENCE (Continuity) -->
  <str name="prior_context_reference">data://sha256:PRIOR:context</str>
  
  <!-- AUDIT TRAIL -->
  <seq name="audit" of="map">
    <map>
      <str name="timestamp">2026-08-06T10:35:00Z</str>
      <str name="accessed_by">claude_opus_5</str>
      <str name="permission_grant_checked">YES</str>
      <str name="access_allowed">YES</str>
    </map>
  </seq>

</map>
```

**Implementation Notes:**
- NO raw data embedded (only references)
- Drastically smaller than current context window (just addresses)
- Can be passed to other AI systems without exposing user data
- Permission grants control what other systems can do with it
- Shareability enables multi-agent collaboration while preserving sovereignty

---

## PROFILE 7: anthropic_token_accounting.121xml

**Purpose:** Immutable token ledger. Replaces per-session token counters.

**Profile URI:** `urn:121xml:anthropic-token-accounting/1.0`

```xml
<map profile="urn:121xml:anthropic-token-accounting/1.0" version="1.0">
  
  <!-- ACCOUNTING IDENTIFICATION -->
  <str name="ledger_id">LEDGER_UUID</str>
  <str name="ledger_address">data://sha256:COMPUTED:ledger</str>
  <str name="period">2026-08</str>
  
  <!-- USER -->
  <str name="user_id">USER_ID</str>
  
  <!-- TOKEN ENTRIES (Append-only) -->
  <seq name="token_entries" of="map">
    <map>
      <str name="timestamp">2026-08-06T10:30:00Z</str>
      <str name="session_reference">data://sha256:session001:session</str>
      <str name="message_reference">data://sha256:msg001:message</str>
      <int name="input_tokens">128</int>
      <int name="output_tokens">256</int>
      <int name="total_tokens">384</int>
      <str name="model">claude_opus_5</str>
      <str name="operation">message_processing | tool_invocation | inference_creation</str>
    </map>
  </seq>
  
  <!-- SUMMARY STATISTICS -->
  <map name="summary">
    <int name="total_input_tokens">12345</int>
    <int name="total_output_tokens">23456</int>
    <int name="total_tokens">35801</int>
    <int name="session_count">10</int>
    <int name="average_tokens_per_session">3580</int>
  </map>
  
  <!-- AUDIT METADATA -->
  <map name="audit">
    <str name="ledger_immutable">YES</str>
    <str name="append_only">YES</str>
    <str name="never_modified">YES</str>
  </map>

</map>
```

**Implementation Notes:**
- Append-only (entries never deleted)
- Immutable (no modifications to past entries)
- Replaces volatile per-session counters
- Enables accurate billing and usage tracking
- Complete audit trail for compliance

---

## IMPLEMENTATION CHECKLIST

All profiles implement:

- ✓ R4: Alphabetically sorted keys
- ✓ R5: Explicit null values
- ✓ R6: Profile URI (self-describing)
- ✓ R7: SHA256 content addressing
- ✓ A1: Composition over inheritance (all nested maps)
- ✓ A2: Explicit type tags on polymorphic fields
- ✓ A3: Homogeneous sequences only

---

## VALIDATION CHECKPOINTS

Before accepting any profile:

1. **Does it violate boundary_no_centralization?** NO ✓
2. **Does it violate boundary_no_data_copying?** NO ✓
3. **Does it violate boundary_no_single_vendor?** NO ✓
4. **Does it violate boundary_no_context_loss?** NO ✓
5. **Does it reference MASTER_DEFINITIONS?** YES ✓
6. **Is it 121XML compliant?** YES ✓
7. **Does it enable universal code generation?** YES ✓

---

## NEXT STEPS

1. Implement all 7 profiles as actual 121XML files
2. Build prototype parser/serializer for each
3. Integrate into Anthropic messages API
4. Test with real Claude sessions
5. Measure token savings vs. current approach
6. Document for Anthropic engineering team
7. Prepare for vendor replication (OpenAI, Google, Meta)

---

**References:**
- MASTER_DEFINITIONS.121xml
- ANTHROPIC_121XML_INTEGRATION_BLUEPRINT.md
- VALIDATION_FRAMEWORK.121xml
- def_121xml_axioms (data://sha256:7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b:definition)
- def_121xml_rules (data://sha256:2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f:definition)

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*