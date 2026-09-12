# 121XML Architecture & Implementation Guide

**Version:** 1.1 | **Date:** 2026-07-23 | **Status:** Complete with Visual Diagrams

---

## Overview

This guide explains the 121XML reference architecture across four visual diagrams, implementation patterns, and a 6-week development roadmap. It is intended for architects and senior engineers tasked with building 121XML support into production systems.

**Key takeaway:** 121XML is not faster than Protobuf. It trades byte efficiency for decoupling. Use it when receivers cannot know the schema in advance, or when schema changes must not force redeployment.

---

## Table of Contents

1. [The Four Architecture Diagrams](#the-four-architecture-diagrams)
2. [Core Rules & Axioms](#core-rules--axioms)
3. [Implementation Layers](#implementation-layers)
4. [Data Flow: Encoding → Transmission → Decoding](#data-flow-encoding--transmission--decoding)
5. [Validation & Conformance Pipeline](#validation--conformance-pipeline)
6. [Code Generation Strategy](#code-generation-strategy)
7. [Usage Patterns & Decision Tree](#usage-patterns--decision-tree)
8. [6-Week Implementation Roadmap](#6-week-implementation-roadmap)
9. [Testing & Round-Trip Verification](#testing--round-trip-verification)

---

## The Four Architecture Diagrams

### 1. **121XML_Architecture_Diagram.svg** — System Layers
Shows five integration layers:

- **Layer 1: Source Systems** — Legacy JSON, APIs, databases, LLM tools, event streams, contact graphs
- **Layer 2: Conversion Gateway (Inbound)** — Profile loader, type enforcement (A1–A3), canonical transformation (R4), integrity envelope
- **Layer 3: Canonical 121XML (In-Memory)** — Self-describing data structure with provenance
- **Layer 4: Output Transformation** — Four parallel paths: Storage, Codegen, Transmission, Reference
- **Layer 5: Consumption** — Three receiver patterns: schema-free parser, generated code, conformance checker

**When to use:** Reference this diagram when explaining how 121XML fits into an existing system architecture.

---

### 2. **121XML_DataFlow_Diagram.svg** — Packet Lifecycle
Shows complete journey of a data packet:

- **Phase 1: Encoding (Sender)**
  - Serialize domain object
  - Apply axioms A1–A3
  - Sort keys by code point (R4)
  - Compute SHA-256 hash (R7)
  - Emit final packet

- **Phase 2: Transmission**
  - Encode to XML or JSON
  - Send over wire (HTTPS, gRPC, Kafka)
  - __hash field travels with packet
  - No pre-shared schema needed

- **Phase 3: Decoding (Receiver)**
  - Parse packet without knowing schema in advance
  - Allocate memory based on type tags (A2)
  - Reconstruct domain objects
  - Verify SHA-256 hash (R7)
  - Accept or reject based on integrity check

**Why this works:** The receiver needs only the profile URI (R6). No codegen, no schema compilation. The packet is self-describing.

**Key property — the hash journey:**
```
Sender computes hash over sorted bytes (R4 ensures order)
→ Appends hash as __hash field
→ Receiver recomputes hash over same bytes
→ If hashes match, data survived transmission untouched
→ If hashes differ, packet was corrupted or tampered
```

---

### 3. **121XML_Conformance_Diagram.svg** — Validation Pipeline
Shows four conformance levels and how to test round-trip integrity:

| Level | Test | Cost | Deliverable |
|-------|------|------|-------------|
| **L0: Syntactic** | Well-formed XML/JSON, valid type tags | Free | Self-service validator |
| **L1: Structural** | Axioms A1–A3 enforced, codegen works in 6 langs | Free | CI action |
| **L2: Canonical** | Keys sorted (R4), null explicit (R5), version declared (R6) | Paid | Enterprise certificate |
| **L3: Round-Trip** | Source → 121XML → Source byte-identical (R7) | Paid | Annual audit + field scorecard |

**Round-Trip Harness (L3):**
1. Load 100 representative records from production
2. Export to 121XML, apply R4, compute hashes
3. Re-import, parse schema-free, verify hashes
4. Byte-compare original vs. re-imported, field by field
5. Publish scoreboard: which fields survived perfectly? Which failed?

**Openness principle:** Failures are disclosed prominently. A field that cannot round-trip cleanly is documented and explained. This honesty is what makes L3 credible to buyers.

---

### 4. **121XML_Codegen_Diagram.svg** — Multi-Language Code Generation
Shows how one 121XML profile generates working code in six languages:

**Input:** A single profile (e.g., Contact.121xml)

**Output:** Working implementations in:
- Python (type hints, dataclasses)
- Rust (memory-safe structs, no unsafe)
- Java (POJOs with reflection support)
- C++ (STL containers, no raw pointers)
- R (S4 classes, formal slots)
- JavaScript/TypeScript (interfaces + functions)

**Why this is possible:** The three axioms (A1, A2, A3) eliminate language-specific features that cannot be universally represented.

- **A1: Composition, no inheritance** → All six languages have structs/records; only two have inheritance
- **A2: Explicit type tags** → Memory allocation before parsing works in all six
- **A3: Homogeneous sequences** → Vec<String>, List<String>, vector<string> are isomorphic

**Generator size:** Each language generator is ~500 lines of code. Small, because the rules are strict.

---

## Core Rules & Axioms

### Three Axioms (A1–A3)
These are non-negotiable constraints that enable universal code generation:

| Axiom | Rule | Why |
|-------|------|-----|
| **A1** | Composition over inheritance | Rust has no classes; C++ has templates. Forbidding hierarchies everywhere means all languages can generate identical structures. |
| **A2** | Explicit type tags on polymorphic fields | Strict compilers need memory layout before parsing. Tags go in the data; no out-of-band schema. |
| **A3** | Homogeneous sequences only | Mixed-type arrays cannot be pre-allocated in Java or C++. All members must share one type. |

### Four Rules (R4–R7)
These ensure integrity, versioning, and lossless round-trip:

| Rule | Constraint | Benefit |
|------|-----------|---------|
| **R4** | Keys sorted alphabetically by Unicode code point | Deterministic byte order enables stable hashing. Repeated serialization = identical bytes. |
| **R5** | Null is explicit, not absence | Three distinct states: value, null (known but empty), absent (key never set). No ambiguity. |
| **R6** | Profile URI and version declared in packet | Receiver knows schema without pre-shared agreement. Versioning is built in. |
| **R7** | SHA-256 hash appended as __hash field | Sender and receiver independently verify integrity. Provenance travels with data. |

---

## Implementation Layers

### Layer 1: Source Systems

**Input types your 121XML gateway must accept:**
- Legacy XML / JSON documents
- Relational database rows (SQL CONVERT to XML, then gateway)
- REST API responses
- LLM tool output (structured as JSON)
- Event stream payloads (Kafka topics, Pub/Sub messages)
- Contact data from Google Contacts, Apple Contacts, Microsoft People

**Transformation logic at this layer:**
- Map source fields to 121XML types (int, dec, str, bool, seq, map, ref, null)
- Handle missing / optional fields (R5: explicit null)
- Flatten or nest as needed to conform to axioms

---

### Layer 2: Conversion Gateway (Inbound)

Four sequential transformations:

#### 2a. Profile Loader
- Read profile URI from packet or config
- Extract field list, types, constraints
- Validate that incoming data matches schema

#### 2b. Type Enforcement (A1–A3)
- **A1 check:** Reject inheritance. Use only nested maps for composition.
- **A2 check:** Polymorphic fields must have type tags.
- **A3 check:** Sequences must be homogeneous (all members same type).

#### 2c. Canonical Transformation (R4)
- Sort all map keys alphabetically by Unicode code point
- Produce deterministic byte sequence
- Enables stable hashing

#### 2d. Integrity Envelope (R7)
- Compute SHA-256 over sorted bytes
- Append as __hash field
- Receiver will recompute and compare

---

### Layer 3: Canonical 121XML (In-Memory)

The canonical representation:
```
<map profile="urn:121xml:contact/1.1" version="1.1" __hash="sha256:abc123...">
  <str name="email">alice@example.com</str>
  <str name="name">Alice Smith</str>
  <int name="phone">5551234567</int>
  <null name="fax"/>  <!-- Explicit null, R5 -->
  <seq name="tags" of="str">
    <str>vip</str>
    <str>active</str>
  </seq>
</map>
```

**Invariants maintained:**
- Profile URI and version (R6) declared upfront
- All keys in order (R4)
- Nulls explicit (R5)
- Hash present (R7)

---

### Layer 4: Output Transformation (Four Paths)

#### Path A: Storage
- Serialize to disk as XML or JSON
- Append __hash field
- Store immutably (append-only log)
- Enables tamper detection

#### Path B: Codegen
- Generate deserialiser in Python, Rust, Java, C++, R, JavaScript
- Generates serialiser (with R4 sorting)
- Generates hash verification (R7)
- Codegen runs once per language, ship as library

#### Path C: Transmission
- Serialize to XML or JSON
- Optionally sign (digital signature)
- Send over wire (HTTPS, gRPC, Kafka)
- Receiver gets packet + hash, no schema fetch needed

#### Path D: Reference & Docs
- Generate HTML schema documentation
- Generate sample JSON/XML records
- Publish field coverage scoreboard
- Build test data

---

### Layer 5: Consumption (Three Patterns)

#### Pattern A: Schema-Free Parser
**Use when:** Receiver may not have generated code, or is running in sandboxed environment

```
while not at EOF:
  1. Read field name
  2. Read type tag (str, int, seq, map, etc.)
  3. Based on tag, allocate correct type
  4. Read value into allocated slot
  5. Append to output object
final: Read and verify __hash (R7)
```

**Advantage:** No codegen, no recompile on schema change. Perfect for API proxies, logging, data warehouses.

#### Pattern B: Generated Code
**Use when:** High throughput, strict compile-time safety

Generated deserialiser:
```
Contact deserialize(String s) throws ParseException {
  Contact out = new Contact();
  XMLParser p = new XMLParser(s);
  p.expectTag("map");
  p.expectAttr("profile", "urn:121xml:contact/1.1");
  
  while (p.hasMore()) {
    String field = p.readFieldName();
    switch (field) {
      case "email": 
        p.expectType("str");
        out.email = p.readString();
        break;
      case "phone":
        p.expectType("int");
        out.phone = p.readInt();
        break;
      // ...
    }
  }
  
  String hash = p.readAttr("__hash");
  if (!verifyHash(out, hash)) throw new ParseException("Hash mismatch");
  return out;
}
```

#### Pattern C: Conformance Check
**Use when:** Validating data pipeline, testing compliance

```
1. Parse packet
2. Validate L0–L3 constraints
3. Report conformance level
4. Issue certificate if L2/L3
```

---

## Data Flow: Encoding → Transmission → Decoding

### Phase 1: Encoding (Sender)

**Input:** Domain object in memory
```
{
  name: "alice",
  email: "alice@example.com",
  phone: 5551234567,
  tags: ["vip", "active"]
}
```

**Step 1: Apply Axioms A1–A3**
- No inheritance: use nested maps (A1) ✓
- Type tags for polymorphic fields (A2) ✓
- Homogeneous sequences (A3) ✓

**Step 2: Sort Keys (R4)**
Alphabetical order by Unicode code point:
```
email, name, phone, tags
```

**Step 3: Compute Hash (R7)**
```
bytes = serialize(sorted_fields)
hash = SHA256(bytes)
__hash = "sha256:" + hex(hash)
```

**Output:** 121XML packet ready for transmission

### Phase 2: Transmission

**Format options:**
- XML: `<map profile="..." version="..." __hash="...">...</map>`
- JSON: `{"profile": "...", "version": "...", "__hash": "...", "email": "...", ...}`

**Transport:**
- HTTPS (encrypted)
- gRPC (binary envelope)
- Kafka (append-only log)
- REST API (JSON in HTTP body)

**Invariants:** __hash field travels unmodified with data

### Phase 3: Decoding (Receiver)

**Precondition:** Receiver knows nothing about Contact schema in advance

**Step 1: Read Profile URI (R6)**
```
profile_uri = packet.attr("profile")
// "urn:121xml:contact/1.1"
// Tells receiver: this is a contact record, version 1.1
```

**Step 2: Parse Schema-Free**
```
for field in packet.fields():
  type_tag = field.type()  // "str", "int", "seq", etc.
  allocate memory[type_tag]
  value = field.value()
  object[field.name] = value
```

**Step 3: Verify Hash (R7)**
```
stored_hash = packet.attr("__hash")
computed_hash = SHA256(sorted_bytes)
if computed_hash != stored_hash:
  throw new TamperingException()
```

**Output:** Trusted domain object, or rejection with clear error

---

## Validation & Conformance Pipeline

### Conformance Levels Explained

#### L0: Syntactic Validation
**Checks:**
- XML or JSON is well-formed (non-negotiable)
- All type tags are valid (<str>, <int>, <seq>, <map>, <bool>, <dec>, <ref>, <null>)
- Nesting is legal

**Cost:** Free (self-service)

**Distribution:** Validator CLI available on GitHub
```bash
$ 121xml-validate packet.xml
✓ L0 PASS
```

#### L1: Structural Validation
**Checks:**
- A1: No inheritance hierarchies
- A2: All polymorphic fields tagged
- A3: All sequences homogeneous

**Benefit:** Proves that all six language generators will produce code that compiles.

**Cost:** Free (CI action)

**Distribution:** GitHub Actions, GitLab CI templates

#### L2: Canonical Validation
**Checks:**
- R4: Keys are sorted alphabetically
- R5: Null is explicit (not confused with absence)
- R6: Profile URI and version declared

**Benefit:** Hashes are stable and repeatable. Can be signed for provenance.

**Cost:** Paid subscription, ~$500/year per team

**Distribution:** Enterprise dashboard

#### L3: Round-Trip Certified
**Checks:** The ultimate test
- Source → 121XML → Source must be byte-identical
- Tested across 100 representative records
- Tested in all six languages simultaneously
- Field coverage scorecard published

**Benefit:** Guarantees lossless interchange. Buyer can trust data integrity.

**Cost:** Paid subscription, annual re-certification (~$2,000/year)

**Distribution:** Annual audit certificate + field scorecard report

---

## Code Generation Strategy

### Universal Codegen Pattern

**Input:** 121XML profile file

**Process:**
```
for language in [python, rust, java, cpp, r, javascript]:
  generate_struct(profile, language)
  generate_serialiser(profile, language)
  generate_deserialiser(profile, language)
  generate_hash_function(profile, language)
  ship_as_library(language, "121xml-contact-1.1")
```

### Example: Contact Profile

**Input profile:**
```xml
<map profile="urn:121xml:contact/1.1" version="1.1">
  <str name="email"/>
  <int name="phone"/>
  <seq name="tags" of="str"/>
</map>
```

**Generated Rust:**
```rust
pub struct Contact {
  email: String,
  phone: i64,
  tags: Vec<String>,
}

impl Contact {
  pub fn serialize(&self) -> String { ... }
  pub fn deserialize(s: &str) -> Result<Contact, ParseError> { ... }
  pub fn verify_hash(&self) -> bool { ... }
}
```

**Generated Python:**
```python
class Contact:
  def __init__(self):
    self.email: str
    self.phone: int
    self.tags: list[str]
  
  def serialize(self) -> str: ...
  @staticmethod
  def deserialize(s: str) -> Contact: ...
  def verify_hash(self) -> bool: ...
```

**All six generate identically, modulo language idioms.**

---

## Usage Patterns & Decision Tree

### When to Use 121XML

**Use 121XML if:**
- [ ] Receiver does not know schema in advance
- [ ] Schema changes must not force receiver recompile/redeploy
- [ ] Data integrity (tamper detection) is critical
- [ ] You need to carry schemas across vendor lock-in (LLM vendor switching)
- [ ] Field-level round-trip guarantees matter more than throughput

**Examples:**
1. **Contact federation:** Syncing contacts between Google, Apple, Microsoft without redeploying client
2. **M&A diligence:** Data rooms where buyer tool may not have been updated with latest schema
3. **Clinical trial data:** Regulatory audit trail; hash proves integrity
4. **LLM tool schema carry-over:** Claude → GPT → Gemini without re-mapping

### When NOT to Use 121XML

**Do not use if:**
- [ ] Throughput is critical (< 1ms latency requirement)
- [ ] Payload size is extremely constrained (IoT, satellite)
- [ ] Receiver knows schema 100% in advance and never changes
- [ ] You are optimizing for CPU, not flexibility

**Use Protobuf / MessagePack instead:** Smaller, faster, designed for known schemas.

### Decision Tree
```
Does receiver know schema in advance?
  ├─ YES → Use Protobuf
  └─ NO → 121XML is a candidate
       Does schema change often?
         ├─ Rarely → Still consider Protobuf + versioning
         └─ Frequently → 121XML wins
```

---

## 6-Week Implementation Roadmap

### Week 1–2: Model & Specification

**Deliverables:**
- Finalize 121XML profile for your use case
- Define fields, types, constraints
- Write 50-record sample JSON/XML in current format
- Agree on L0 vs L1 vs L2 vs L3 targets

**Time:** 40 hours

**Artifacts:**
- profile.121xml (formal)
- sample-records.json (current format)
- conformance-target.md (which levels to target)

### Week 3–4: Implement Core Runtime

**Core Runtimes:** Python, Rust

**Deliverables:**
- `121xml.py` library with serialize/deserialize/hash functions
- `121xml` Rust crate with same API
- Both pass L0–L2 validation
- Both round-trip 50 sample records

**Time:** 80 hours

**Artifacts:**
- `121xml-py/121xml.py` (500 lines)
- `121xml-rs/lib.rs` (600 lines)
- `test_roundtrip.py` / `test_roundtrip.rs`

### Week 5: Codegen + Other Languages

**Deliverables:**
- Code generators for Java, C++, JavaScript
- All six languages generate + compile
- Codegen is idempotent (run twice, same output)

**Time:** 60 hours

**Artifacts:**
- `codegen/contact_gen.py` (generates in all six)
- `output/contact.java` / `contact.cpp` / `contact.ts` (generated)

### Week 6: Round-Trip Harness & Reporting

**Deliverables:**
- Load 100 production records
- Export → import in all six languages
- Publish field coverage scoreboard
- Decide: L2 or L3 certification

**Time:** 40 hours

**Artifacts:**
- `harness/round_trip_test.py`
- `output/conformance_report_2026_07_23.html` (field-by-field scoreboard)

---

## Testing & Round-Trip Verification

### Round-Trip Test Suite

**Objective:** Prove that source → 121XML → source is byte-identical

### Setup
```python
from collections import namedtuple

# Load production data
records = load_json("production_contacts_2026_01.json")  # 100 records

# Define which fields should survive
profile = Profile.load("contact_121xml_v1.1.xml")

# Establish baseline
for record in records:
  record['_baseline'] = json.dumps(record, sort_keys=True)
```

### Export Phase
```python
exported = []
for record in records:
  xml = serialize(record)  # Apply A1–A3, R4, R7
  hash_value = record.get('__hash')
  exported.append((record, xml, hash_value))
```

### Import Phase
```python
imported = []
for record, xml, hash_value in exported:
  obj = deserialize(xml)  # Schema-free
  verify_hash(obj, hash_value)  # R7
  imported.append(obj)
```

### Comparison
```python
results = {'pass': 0, 'fail': 0, 'partial': 0}
scoreboard = []

for original, reimported in zip(records, imported):
  comparison = compare_fields(original, reimported)
  
  if comparison['all_fields_identical']:
    results['pass'] += 1
    scoreboard.append(('email', 'PASS', 100))
  elif comparison['some_fields_lost']:
    results['partial'] += 1
    for field, percent_intact in comparison['field_loss'].items():
      scoreboard.append((field, 'FAIL' if percent_intact < 100 else 'PASS', percent_intact))
  else:
    results['fail'] += 1

print(f"Pass: {results['pass']}/100")
print(f"Partial: {results['partial']}/100 (some fields lost)")
print(f"Fail: {results['fail']}/100 (severe corruption)")
```

### Publish Results
```html
<h2>Contact-to-121XML Round-Trip Report</h2>
<table>
  <tr><th>Field</th><th>Status</th><th>Success Rate</th></tr>
  <tr><td>email</td><td>✓ PASS</td><td>100/100</td></tr>
  <tr><td>name</td><td>✓ PASS</td><td>100/100</td></tr>
  <tr><td>phone</td><td>✓ PASS</td><td>100/100</td></tr>
  <tr><td>internal_id</td><td>✗ FAIL</td><td>0/100 (not exported)</td></tr>
  <tr><td>created_at</td><td>⚠ PARTIAL</td><td>89/100 (TZ lost)</td></tr>
</table>

<p><strong>Failures disclosed:</strong> internal_id is not part of the export pipeline; created_at loses timezone on re-import (stored as UTC strings only).</p>

<p><strong>Recommendation:</strong> L2 Canonical (L3 pending fix for created_at).</p>
```

---

## Appendix: Command Reference

### Validation CLI
```bash
# L0: Syntactic check
$ 121xml-validate packet.xml
✓ L0 PASS

# L1: Structural check (A1–A3)
$ 121xml-validate --structural packet.xml
✓ L1 PASS (codegen will work)

# L2: Canonical check (R4–R6)
$ 121xml-validate --canonical packet.xml
✓ L2 PASS (hashes stable)

# L3: Round-trip (requires reference data)
$ 121xml-validate --roundtrip packet.xml --baseline original.json
✓ L3 PASS (8/10 fields perfect round-trip)
```

### Codegen CLI
```bash
# Generate Python from profile
$ 121xml-codegen python contact_v1.1.xml -o output/contact.py

# Generate all six languages
$ 121xml-codegen all contact_v1.1.xml -o output/

# Verify generated code compiles
$ 121xml-codegen python contact_v1.1.xml --test
✓ Python: compiles, runs, passes round-trip harness
✓ Rust: compiles, runs, passes round-trip harness
✓ Java: compiles, runs, passes round-trip harness
✓ C++: compiles, runs, passes round-trip harness
✓ R: compiles, runs, passes round-trip harness
✓ JavaScript: compiles, runs, passes round-trip harness
```

---

## Summary

121XML is a typed data interchange format designed for scenarios where flexibility and integrity matter more than throughput. Its three axioms (A1–A3) and four rules (R4–R7) enable:

1. **Universal code generation** in six languages from one profile
2. **Schema-free parsing** at the receiver (no codegen needed)
3. **Tamper detection** via SHA-256 hashes that travel with data
4. **Lossless round-trip** tested and certified annually
5. **Zero coupling** between sender and receiver (profiles, not schemas)

The implementation is small (~500 lines per language generator), the validation is composable (L0 → L1 → L2 → L3), and the conformance reporting is honest (failures disclosed, not hidden).

**Next step:** Choose your first vertical, run a 90-day pilot, and publish your field coverage scoreboard.

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*