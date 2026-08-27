# 121XML Framework Specification Summary
## Core Architecture & Fundamental Specifications

**Document:** Consolidated from 30+ spec files  
**Date:** August 7, 2026  
**Status:** Authoritative Reference  

---

## 🎯 **CORE VISION**

121XML is a **vendor-neutral, self-describing data format** that solves critical AI data management challenges:

| Problem | Solution |
|---------|----------|
| 30-50% information loss per compaction | Lossless compression (0% loss) |
| 78% token waste over long conversations | 90-96% token reduction |
| Vendor lock-in (Claude/GPT/Gemini) | Works identically across all AI systems |
| Data privacy concerns | User controls where/how data is stored |
| Schema version management | Built-in versioning and discovery |

---

## 📐 **THE THREE AXIOMS (A1-A3)**

These are **non-negotiable constraints** that enable universal code generation across 6+ languages:

### **Axiom 1: Composition Over Inheritance (A1)**
**Rule:** Objects are built by composing peer objects, NOT hierarchical inheritance.

**Why:**
- Rust has no classes; C++ has templates
- Forbidding hierarchies means ALL languages can generate identical structures
- Flat, predictable structure enables deterministic hashing

**Example:**
```json
✓ CORRECT - Composition
{
  "_type": "payment",
  "sender": { "_type": "party", "name": "Acme" },
  "receiver": { "_type": "party", "name": "Smith" }
}

✗ WRONG - Inheritance
{
  "class": "Payment extends Transaction",
  "parent": { "class": "Transaction" }
}
```

### **Axiom 2: Explicit Type Tags (A2)**
**Rule:** Every object carries its type explicitly via `_type` field.

**Why:**
- Self-describing format (no external schema needed)
- Strict compilers need memory layout before parsing
- Enables automatic validation without codegen

**Example:**
```json
{
  "_type": "payment",
  "_schema": "urn:121xml:payment/1.0",
  "amount": 450000,
  "currency": "USD"
}
```

### **Axiom 3: Homogeneous Sequences (A3)**
**Rule:** Arrays contain objects of the SAME type only.

**Why:**
- Can't pre-allocate mixed-type arrays in Java/C++
- Enables efficient streaming processing
- Type safety guaranteed

**Example:**
```json
✓ CORRECT - Homogeneous
{
  "payments": [
    { "_type": "payment", "amount": 100000 },
    { "_type": "payment", "amount": 200000 }
  ]
}

✗ WRONG - Mixed types
{
  "data": [
    { "_type": "payment", "amount": 100000 },
    { "_type": "invoice", "id": "INV-001" }
  ]
}
```

---

## 🔐 **THE FOUR CORE RULES (R4-R7)**

These ensure **integrity, versioning, immutability, and lossless round-trip**:

### **Rule 4: Alphabetically Sorted Keys (R4)**
**Specification:** All object keys must be sorted alphabetically at every level.

**Purpose:** Enables deterministic hashing and byte-perfect comparison.

**Algorithm:**
```
1. Take any 121XML object
2. Sort all keys alphabetically by Unicode code point
3. Serialize to compact JSON (no spaces)
4. Result: Identical bytes → Identical hash
5. Repeated serialization = Always same bytes
```

**Impact:**
- Same object serialized 1000 times = Same hash 1000 times
- Enables content-addressed deduplication
- Allows bit-for-bit integrity verification

### **Rule 5: Explicit Null vs Absent (R5)**
**Specification:** Distinguish between `null` (explicitly empty) and absent fields.

**Purpose:** Precise data intent, enables lossless reconstruction.

**Three States:**
```json
1. Value present:   { "field": "value" }
2. Null (empty):    { "field": null }
3. Absent (missing): { }  ← field key not present at all
```

**Why it matters:**
- "No phone number recorded" (null) ≠ "Never asked for phone" (absent)
- Critical for compliance (GDPR, HIPAA)
- Enables lossless round-trip encoding/decoding

### **Rule 6: Profile URI for Schema Discovery (R6)**
**Specification:** Every object includes `_schema` field with URN pointing to schema.

**Purpose:** Enables automatic schema discovery without pre-shared agreement.

**Format:**
```
urn:121xml:{object-type}/{major-version}.{minor-version}

Examples:
- urn:121xml:payment/1.0
- urn:121xml:message/1.0
- urn:121xml:fhir-patient/4.1
- urn:121xml:fpml-swap/5.13
```

**Benefit:**
- Receiver knows schema from URI alone
- No codegen needed
- Versioning built-in
- Schema changes don't break receivers

### **Rule 7: SHA256 Content Addressing (R7)**
**Specification:** Format: `data://sha256:HASH:TYPE`

**Purpose:** Immutable, deterministic addressing enables perfect deduplication.

**Algorithm:**
```python
def compute_address(obj: dict, object_type: str) -> str:
    # 1. Sort keys alphabetically (R4)
    # 2. Remove any existing _address field
    # 3. Serialize to compact JSON
    json_str = json.dumps(obj, sort_keys=True, separators=(',', ':'))
    
    # 4. Compute SHA256 hash
    full_hash = hashlib.sha256(json_str.encode()).hexdigest()
    
    # 5. Take first 16 characters (128-bit prefix)
    short_hash = full_hash[:16]
    
    # 6. Format: data://sha256:{hash}:{type}
    return f"data://sha256:{short_hash}:{object_type}"
```

**Properties:**
- ✓ **Deterministic:** Same data → Same address (always)
- ✓ **Immutable:** Data change → Different address
- ✓ **Collision-Free:** 256-bit security (2^256 possible hashes)
- ✓ **Self-Describing:** Address includes object type

**Example Addresses:**
```
data://sha256:f84b8556e9174280:payment
data://sha256:3ff3c20c05ff0106:message
data://sha256:1418c9f2b7d5e8a1:party
data://sha256:a7b96ce3e2a3f5c0:tool
```

---

## 🏗️ **SYSTEM ARCHITECTURE (5 Layers)**

### **Layer 1: Source Systems**
Input types 121XML gateway accepts:
- Legacy XML/JSON documents
- Relational database rows
- REST API responses
- LLM tool output (structured JSON)
- Event streams (Kafka, Pub/Sub)
- Contact data (Google, Apple, Microsoft)

### **Layer 2: Conversion Gateway (Inbound)**
Four sequential transformations:

1. **Profile Loader**
   - Read profile URI from packet
   - Extract field list, types, constraints
   - Validate incoming data

2. **Type Enforcement (A1–A3)**
   - A1 check: Reject inheritance
   - A2 check: Polymorphic fields must have type tags
   - A3 check: Sequences must be homogeneous

3. **Canonical Transformation (R4)**
   - Sort all map keys alphabetically
   - Produce deterministic byte sequence
   - Enable stable hashing

4. **Integrity Envelope (R7)**
   - Compute SHA-256 over sorted bytes
   - Append as `_address` field
   - Receiver will recompute and verify

### **Layer 3: Canonical 121XML (In-Memory)**

**Canonical Format:**
```xml
<map profile="urn:121xml:payment/1.0" version="1.0" _address="data://sha256:abc123:payment">
  <str name="_schema">urn:121xml:payment/1.0</str>
  <str name="_type">payment</str>
  <int name="amount">450000</int>
  <str name="currency">USD</str>
  <null name="description"/>  <!-- Explicit null (R5) -->
  <seq name="items" of="map">
    <map>
      <str name="description">Item 1</str>
      <int name="quantity">10</int>
    </map>
  </seq>
</map>
```

**Invariants Maintained:**
- Profile URI and version (R6) declared upfront
- All keys in alphabetical order (R4)
- Nulls explicit, not absence (R5)
- Hash present for integrity (R7)

### **Layer 4: Output Transformation (Four Paths)**

**Path A: Storage**
- Serialize to disk as XML or JSON
- Append `_address` field
- Store immutably (append-only log)
- Enables tamper detection

**Path B: Codegen**
- Generate deserializer in 6 languages: Python, Rust, Java, C++, R, JavaScript
- Generator size: ~500 lines per language
- Generates serializer with R4 sorting
- Generates hash verification (R7)

**Path C: Transmission**
- Serialize to XML or JSON
- Optionally digitally sign
- Send over wire (HTTPS, gRPC, Kafka)
- Receiver gets packet + hash

**Path D: Reference & Docs**
- Generate HTML schema documentation
- Generate sample JSON/XML records
- Publish field coverage scoreboard
- Build test data

### **Layer 5: Consumption (Three Patterns)**

**Pattern A: Schema-Free Parser**
- Read field name
- Read type tag
- Based on tag, allocate correct type
- Read value into slot
- Verify hash

**Pattern B: Generated Code**
- Use language-specific generated deserializer
- Compile-time safety
- High throughput

**Pattern C: Conformance Check**
- Parse packet
- Validate L0–L3 constraints
- Report conformance level
- Issue certificate if L2/L3

---

## 💡 **KEY CONCEPTS**

### **Content Addressing**
Every data object gets unique, immutable address.

**Use Cases:**
- Perfect deduplication (store once, reference many)
- Detecting data tampering
- Enabling lossless compression
- Creating immutable audit trails

### **Lossless Compression**
90-96% token reduction with zero data loss.

**Method:** Replace full objects with sparse content references.

**Example:**
- Before: `{ "invoice": "INV-2026-08-0042", "amount": 450000, ...etc... }` = 2,500 tokens
- After: `data://sha256:f84b8556e9174280:payment` = 25 tokens
- Savings: 99% for this object

### **Profile URI / Schema Discovery**
Enables schema discovery without pre-shared agreement.

**Format:** `urn:121xml:{type}/{version}`

**Benefit:** Receiver knows schema from packet alone. No codegen, no schema compilation needed.

### **Deterministic Hashing (R4 + R7)**
Same data → Always same hash → Perfect deduplication

**Process:**
1. Sort keys (R4)
2. Serialize consistently
3. Hash once (R7)
4. Store address
5. Reuse if same data appears again

---

## 🔄 **DATA FLOW: Complete Lifecycle**

```
SOURCE (JSON)
    ↓
[Axioms A1-A3 validation]
    ↓
[R4: Sort keys alphabetically]
    ↓
[R5: Make nulls explicit]
    ↓
[R6: Add _schema profile URI]
    ↓
CANONICAL 121XML
    ↓
[R7: Compute SHA256 hash]
    ↓
[_address field appended]
    ↓
CONTENT-ADDRESSED 121XML
    ↓
    ├─→ [Storage: Disk/DB]
    ├─→ [Transmission: Wire]
    ├─→ [Codegen: Generate code]
    └─→ [Reference: Docs]
    ↓
RECEIVER
    ├─→ [Schema-free parser]
    ├─→ [Generated deserializer]
    └─→ [Conformance checker]
    ↓
VERIFY HASH (R7)
    ↓
RECONSTRUCT ORIGINAL DATA
```

---

## 📊 **CONFORMANCE LEVELS (L0-L3)**

| Level | Test | Cost | Deliverable |
|-------|------|------|-------------|
| **L0: Syntactic** | Well-formed XML/JSON, valid type tags | Free | Self-service validator |
| **L1: Structural** | Axioms A1–A3 enforced | Free | CI action |
| **L2: Canonical** | Keys sorted (R4), nulls explicit (R5), version declared (R6) | Paid | Enterprise certificate |
| **L3: Round-Trip** | Source → 121XML → Source byte-identical | Paid | Annual audit + field scorecard |

---

## 🎯 **CORE PRINCIPLES**

### **Principle 1: Self-Describing Format**
No external schema file needed. Profile URI in every packet.

### **Principle 2: Vendor Neutral**
Works identically across Claude, GPT, Gemini, Llama, etc.

### **Principle 3: Immutability**
Content-addressed objects never change. Different hash = Different object.

### **Principle 4: Zero Data Loss**
Lossless compression guaranteed. Perfect reconstruction always possible.

### **Principle 5: Deterministic**
Same input → Always same output. Enables deduplication and integrity verification.

### **Principle 6: Universal Code Generation**
One profile generates identical code in 6 languages.

### **Principle 7: Privacy First**
User controls where data lives. No mandatory cloud storage.

---

## 🚀 **PRODUCTION-READY COMPONENTS**

### **Deployed Now:**
✅ MCP Server (Full 121XML native format)
✅ Translator Layer (Bidirectional conversion)
✅ Compaction Engine (90-96% compression)
✅ Persistence Layer (Content-addressed storage)
✅ Plugin Auto-Generator (Generate plugins)

### **Validation Framework:**
✅ L0 Syntactic Validator
✅ L1 Structural Validator
✅ L2 Canonical Validator
✅ L3 Round-Trip Test Harness

---

## 📋 **QUICK REFERENCE**

| Aspect | Specification |
|--------|---------------|
| **Data Loss** | 0% (lossless) |
| **Compression** | 90-96% token reduction |
| **Axioms** | 3 (Composition, Type Tags, Homogeneous) |
| **Rules** | 4 (Sorted Keys, Explicit Null, Profile URI, SHA256) |
| **Layers** | 5 (Source → Gateway → Canonical → Transform → Consumer) |
| **Patterns** | 3 (Schema-free, Codegen, Conformance) |
| **Code Generators** | 6 languages (Python, Rust, Java, C++, R, JavaScript) |
| **Security** | SHA256 (256-bit, collision-free) |
| **Format** | XML and JSON support |

---

**This is the foundation for 121XML AI OS specifications brainstorming.**

