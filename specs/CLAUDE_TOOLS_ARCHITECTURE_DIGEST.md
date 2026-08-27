# Claude Tools Architecture & Best Practices Digest

**Date:** August 6, 2026 | **Source:** platform.claude.com/docs/agents-and-tools/tool-use/define-tools

---

## I. CORE ARCHITECTURE: Tool Definition Stack

### A. Tool Specification Structure
Every tool has 4 core components:

```
TOOL DEFINITION (JSON Schema)
├── name (string) - Regex: ^[a-zA-Z0-9_-]{1,64}$
├── description (plaintext) - CRITICAL for performance
├── input_schema (JSON Schema object) - Parameters & validation
└── input_examples (optional array) - Concrete usage patterns
```

### B. Hierarchy of Tool Processing
When Claude API receives a tool request:

```
1. API Construction Layer
   ├─ Takes tool definitions from "tools" top-level parameter
   └─ Creates special system prompt

2. System Prompt Generation
   ├─ Constructs instructional context:
   │  ├─ Formatting instructions
   │  ├─ JSON Schema tool definitions
   │  ├─ User system prompt
   │  └─ Tool configuration
   └─ Result: Model receives full tooling context

3. Model Decision Layer
   ├─ Claude reads tool definitions
   ├─ Evaluates when/how to use tools
   ├─ Generates tool_use content blocks
   └─ Returns response with natural language + tool calls

4. Tool Execution (Client Side)
   ├─ Application parses tool_use blocks
   ├─ Executes actual tool logic
   ├─ Formats results as tool_result messages
   └─ Sends back to Claude in conversation
```

---

## II. SYSTEM PROMPT & CONTEXT MANAGEMENT

### The Auto-Generated Tool Prompt Structure:
```
"In this environment you have access to a set of tools..."
├─ FORMATTING INSTRUCTIONS
│  └─ How to structure tool calls (strings as-is, objects/arrays as JSON)
│
├─ TOOL DEFINITIONS IN JSON SCHEMA
│  └─ Every tool Claude can access
│
├─ USER SYSTEM PROMPT
│  └─ Your custom instructions
│
└─ TOOL CONFIGURATION
   └─ tool_choice, strict settings, etc.
```

**Key insight:** Tool definitions become part of the system prompt, meaning they occupy token space in your context window and can be cached.

### Context & Caching Implications:
- ✓ Tool definitions are **CACHED** (same tools = cache hit)
- ✓ User system prompt is **CACHED** (rarely changes)
- ✗ `tool_choice` changes **INVALIDATE** cached message blocks
- ✓ Tool content itself stays cached even if tool_choice varies

---

## III. TOOL DEFINITION BEST PRACTICES

### **Golden Rule: Description > Schema**
Description quality is the **single most important factor** in tool performance.

#### What Great Descriptions Include:
1. **What the tool does** (clear, specific)
2. **When to use it** (and when NOT to use it)
3. **Each parameter's purpose** (how each affects behavior)
4. **Caveats & limitations** (what it won't return, edge cases)
5. **Target:** 3-4 sentences minimum, more for complex tools

#### Example - GOOD Description:
```
"Get current stock price for a given ticker symbol. 
Use this when user asks about stock prices, valuations, 
or market data. The 'ticker' parameter is the stock 
symbol (e.g., 'AAPL'). Returns current price, 24h 
change, and market status. Does NOT return historical 
data or predictions."
```

#### Example - POOR Description:
```
"Get stock data."
```

### **Consolidation Pattern: Fewer, Richer Tools**
- ❌ Anti-pattern: `create_pr`, `review_pr`, `merge_pr` (3 tools)
- ✅ Pattern: One `github_pr` tool with action parameter
  - Reduces selection ambiguity
  - Easier for Claude to navigate
  - Clearer intent for complex workflows

### **Namespacing Convention**
When tools span multiple services:
- ✅ Good: `github_list_prs`, `slack_send_message`, `notion_query_db`
- ❌ Bad: `list_prs`, `send_message`, `query_db` (ambiguous at scale)

**Why:** Tool search becomes unambiguous; scales better as your tool library grows.

### **Response Shaping Philosophy**
Design tool responses to return **high-signal information only**:
- Use semantic stable identifiers (UUIDs, slugs) not internal refs
- Include only fields Claude needs for next reasoning step
- Bloated responses waste context, obscure signal
- Example: Return `{id, name, status}` not `{id, name, status, timestamp, internal_ref_1, internal_ref_2, ...}`

---

## IV. INPUT EXAMPLES: The Optional Amplifier

### When to Use `input_examples`
- Complex tools with nested objects
- Optional parameters (show which are really optional)
- Format-sensitive inputs
- Ambiguous parameter combinations

### How It Works:
```python
"input_examples": [
    {"location": "San Francisco, CA", "unit": "fahrenheit"},
    {"location": "Tokyo, Japan", "unit": "celsius"},
    {"location": "New York, NY"}  # Shows 'unit' is truly optional
]
```

### Cost-Benefit:
- **Cost:** ~20–50 tokens for simple examples, ~100–200 for nested
- **Benefit:** Significantly better accuracy for complex tools
- **Note:** Only for user-defined and Anthropic-schema tools (NOT server tools)

---

## V. TOOL CHOICE: CONTROLLING MODEL BEHAVIOR

### Four Control Levels:

| Option | Behavior | Use Case |
|--------|----------|----------|
| `auto` | Claude decides to call tools or not | Default; flexible |
| `any` | Must call one tool, but Claude picks which | Guarantee action |
| `tool` | Force specific named tool | Structured workflows |
| `none` | Prevent all tool use | Conversation only |

### State Machine:
```
User Request
    ↓
[tool_choice setting]
    ├─ auto → Claude chooses (or no tools)
    ├─ any  → Must pick one tool
    ├─ tool → Must use specified tool
    └─ none → No tools allowed
    ↓
Tool Call (or response)
```

### Cache Invalidation Pattern:
```
Same tools + Same system prompt = CACHE HIT
           ↓
        Change tool_choice
           ↓
        Message blocks invalidated
        (but tool definitions remain cached!)
```

### Natural Language with Forced Tools:
- ❌ Setting `tool_choice: tool` suppresses natural language explanation
- ✅ Use `tool_choice: auto` + explicit user message: 
  ```
  "What's the weather in London? Use the get_weather tool in your response."
  ```

### Model Behavior with Tools:
Claude may comment naturally before calling tools:
```json
{
  "content": [
    {
      "type": "text",
      "text": "I'll help you check the weather in San Francisco."
    },
    {
      "type": "tool_use",
      "name": "get_weather",
      "input": {"location": "San Francisco, CA"}
    }
  ]
}
```
This conversational style is intentional and creates better UX.

---

## VI. STRICT TOOL USE: Schema Validation

### The Pattern:
```
Combine:
- tool_choice: {"type": "any"}
- strict: true (on tool definitions)
        ↓
GUARANTEE: Tool called + Inputs strictly match schema
```

This is the highest level of tool execution certainty.

---

## VII. MODEL SELECTION GUIDE

### Claude Opus 5 (Recommended for tools):
- ✓ Complex tools with many parameters
- ✓ Ambiguous queries requiring clarification
- ✓ Multiple tools to choose from
- ✓ Seeks clarification when needed

### Claude Haiku (Use for simple cases):
- ✓ Straightforward, single-parameter tools
- ⚠️ May infer missing optional parameters (risky)
- ✓ Cost-effective for simple tool chains

---

## VIII. MEMORY, SESSION & CACHING INTERPLAY

### How Tool Definitions Fit Into Session Memory:

```
SESSION LIFECYCLE
├─ Initial Request
│  ├─ Tools parameter provided
│  └─ System prompt generated (includes tool defs)
│
├─ Caching Layer (Prompt Caching)
│  ├─ Tool definitions: CACHED ✓ (static, reused)
│  ├─ User system prompt: CACHED ✓ (rarely changes)
│  ├─ Message history: POTENTIALLY CACHED ✓
│  └─ tool_choice: NOT CACHED ✗ (changes invalidate)
│
├─ Multi-Turn Conversation
│  ├─ Tool definitions persist in context
│  ├─ Each turn adds to context window
│  ├─ Conversation history accumulates
│  └─ Cache maintained until invalidation trigger
│
└─ Memory Management
   ├─ Context compaction: Summarize old turns
   ├─ Context editing: Remove irrelevant history
   ├─ Session data: Tool call history + results
   └─ Prompt caching: Amortize cost across turns
```

### Key Principle:
Tool definitions are **static content** suited for caching. They should be identical across related requests in a session/workflow.

---

## IX. PRACTICAL ARCHITECTURE PATTERNS

### Pattern 1: Tool Library with Namespacing
```python
tools = [
    # GitHub tools
    {"name": "github_list_prs", ...},
    {"name": "github_create_pr", ...},
    
    # Slack tools
    {"name": "slack_send_message", ...},
    {"name": "slack_list_channels", ...},
    
    # Database tools
    {"name": "db_query", ...},
    {"name": "db_insert", ...}
]
# Clear organization, easy selection
```

### Pattern 2: Action-Parameter Consolidation
```python
{
    "name": "github_pr",
    "description": "Manage GitHub PRs: list, create, review, merge",
    "input_schema": {
        "properties": {
            "action": {"enum": ["list", "create", "review", "merge"]},
            "pr_number": {"type": "integer"},
            "title": {"type": "string"},
            # ... more params
        }
    }
}
```

### Pattern 3: Example-Driven Complex Tools
```python
{
    "name": "search_documents",
    "input_schema": {
        "properties": {
            "query": {"type": "string"},
            "filters": {
                "type": "object",
                "properties": {
                    "date_range": {"type": "array"},
                    "categories": {"type": "array"}
                }
            }
        }
    },
    "input_examples": [
        {"query": "Q3 revenue", "filters": {"categories": ["finance"]}},
        {"query": "launch timeline", "filters": {
            "date_range": ["2026-01", "2026-06"],
            "categories": ["product", "engineering"]
        }},
        {"query": "customer feedback"}  # Shows filters are optional
    ]
}
```

---

## X. ANTI-PATTERNS & GOTCHAS

### ❌ Don't Do This:

1. **Vague Descriptions**
   - ❌ "Get data" → ✅ "Retrieve customer data from Q3 2026, including orders and support tickets. Use when user asks about specific customer history. Returns customer ID, order details, and ticket summaries but NOT payment information due to PCI compliance."

2. **Too Many Single-Purpose Tools**
   - ❌ Separate tools for each action
   - ✅ Consolidate with action parameter

3. **Bloated Tool Responses**
   - ❌ Return entire database records
   - ✅ Return only semantic identifiers + required fields

4. **Unnamespaced Tools at Scale**
   - ❌ `create`, `update`, `delete`
   - ✅ `notion_create_page`, `slack_update_message`, `github_delete_branch`

5. **Inconsistent Examples**
   - ❌ Examples that don't validate against schema
   - ✅ Every example must be schema-valid

6. **Ignoring tool_choice Caching**
   - ❌ Changing tool_choice constantly (invalidates cache)
   - ✅ Use same tool_choice per workflow, vary via user prompts

7. **Forced Tool Use Without Natural Language**
   - ❌ `tool_choice: tool` with `"Explain what you're doing"`
   - ✅ Use `tool_choice: auto` + user message requesting tool

---

## XI. SESSION DATA FLOW WITH TOOLS

```
USER REQUEST (Token: T0)
    ↓
SYSTEM PROMPT GENERATION (includes tools)
    ↓ [CACHE CHECK: tools + system prompt cached? → YES = cost ÷ N]
CLAUDE REASONING
    ├─ Reads tool definitions from system prompt
    ├─ Decides which tool(s) to call
    └─ Generates tool_use content blocks
    ↓
APPLICATION HANDLES TOOL CALL
    ├─ Parses tool_use block
    ├─ Validates input against schema (if strict=true)
    ├─ Executes tool logic
    └─ Returns tool_result message
    ↓
CLAUDE CONTINUES (Token: T0 + tool result size)
    ├─ Sees tool result in conversation history
    ├─ Reasons about result
    ├─ May call more tools or respond to user
    └─ Session memory accumulates
    ↓
CONVERSATION CONTINUES
    ├─ Tool definitions stay cached (if unchanged)
    ├─ New turns use cached system prompt + tools
    ├─ Only new message content incurs token cost
    └─ Session data persists: [tools used, results obtained, reasoning path]
```

---

## XII. RECOMMENDED WORKFLOW FOR YOUR PROJECTS

### Setup Phase (Do Once):
1. **Define tool library** with proper namespacing
2. **Write detailed descriptions** (3-4 sentences minimum)
3. **Create input_examples** for complex tools
4. **Test with Claude Opus 5** for complex workflows
5. **Enable strict mode** if schema enforcement is critical

### Per-Request Phase:
1. **Pass consistent tools** (enables caching)
2. **Use tool_choice: auto** unless you need forced execution
3. **Let Claude decide** when to use tools
4. **Return semantic data** not raw records
5. **Accumulate session history** for multi-turn reasoning

### Optimization Phase:
1. **Monitor cache hit rates** (tool definitions should hit)
2. **Consolidate tools** if library grows beyond 20
3. **Refine descriptions** based on Claude's choices
4. **Use input_examples** if Claude misunderstands formats
5. **Review tool_choice patterns** to improve cache efficiency

---

## XIII. KEY TAKEAWAYS

| Concept | Key Point | Action |
|---------|-----------|--------|
| **Description** | Most important factor in tool performance | Invest time: 3-4 sentences + caveats |
| **Hierarchy** | System prompt > Tool defs > Message content | Plan tool definitions carefully |
| **Caching** | Tools are static & cacheable | Reuse same tools across requests |
| **tool_choice** | Controls when tools are called | Use auto + prompting, not forced |
| **Consolidation** | Fewer rich tools > many simple tools | Group by service, use action parameter |
| **Examples** | Amplifies learning for complex tools | Use for nested objects, optional params |
| **Responses** | Return semantic data only | Include IDs + key fields, not everything |
| **Models** | Opus 5 for complex, Haiku for simple | Choose based on tool complexity |

---

## XIV. CROSS-REFERENCE: Tool Use Docs Topics

To deepen your understanding, explore:
- **How Tool Use Works** - Details on model's tool selection process
- **Build a Tool-Using Agent** - End-to-end tutorial
- **Handle Tool Calls** - Parsing tool_use blocks, formatting responses
- **Parallel Tool Use** - Multiple simultaneous tool calls
- **Tool Runner (SDK)** - Let SDK handle agentic loops
- **Strict Tool Use** - Schema validation details
- **Tool Reference** - Full directory of Anthropic tools
- **Prompt Caching** - Detailed cache strategy

---

## XV. APPLYING TO YOUR COWORK SESSION

### Your Current Tooling:
You have access to:
- **Computer control** (mcp__computer-use__*)
- **Bash execution** (mcp__workspace__bash)
- **File operations** (Read, Write, Edit)
- **Web access** (mcp__workspace__web_fetch, WebSearch)
- **Task management** (TaskCreate, TaskUpdate)
- **Chrome/Browser** (mcp__claude-in-chrome__*)

### Optimization for Your Workflow:
1. **Namespace consistently:** All file tools under one concept, all computer control under another
2. **Describe comprehensively:** Each tool's description should explain when to use it vs alternatives
3. **Batch operations:** Use computer_batch to reduce round-trips (caching + efficiency)
4. **Session data:** Keep tool_choice consistent within a workflow (improves cache hit rate)
5. **Examples for clarity:** If you extend tools, use examples for format-sensitive parameters

---

**End Digest**
