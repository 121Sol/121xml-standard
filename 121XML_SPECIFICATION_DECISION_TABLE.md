# 121XML Specification — Feature & Decision Table

**Purpose:** This is the single editable working document for cleaning up the 121XML specification before we move to architecture and use cases. Every row is one feature/concept pulled from the ~90 spec, strategy, report, and reference files in this project (full detail and citations live in [`121XML_MASTER_IDEAS_CONSOLIDATION.md`](121XML_MASTER_IDEAS_CONSOLIDATION.md) — this table is the action layer on top of it, not a replacement for it).

**How to use this:** Fill in the **Decision** and **Keep in v1?** columns for each row (edit directly in this file, or copy the tables into a spreadsheet if that's easier to work in). Leave a row blank if you're not ready to decide yet — nothing here is final until you mark it. Once every row in Part A has a decision, we'll know which spec files are genuinely redundant and safe to retire, and we can move to architecture/use cases with a settled foundation instead of ~10 unresolved contradictions underneath it.

**Legend — Status:** `Built` (working code exists) · `Spec'd` (fully designed, not built) · `Partial` (designed + some code, unverified) · `Concept` (early/undeveloped idea) · `Contradicted` (two+ docs disagree)

---

## Part A — Scope & Strategy Decisions (resolve these first — they determine which rows in Part B even matter)

| # | Question | Why it matters | Current state | Decision |
|---|---|---|---|---|
| A1 | Is 121XML v1 scope **one narrow vertical** (e.g. SAP/ERP invoicing) or the **universal-everything** claim (any language/protocol/standard)? | Every downstream spec decision (which converters, which profiles, how much to build) depends on this. Currently unresolved — the Universal Spec, the 15-Part Roadmap, and the "Honest Strategic Assessment" all argue for different scopes. |  |  |
| A2 | What's the **funding/scale target**: ~$3–5M seed for a narrow play, or ~$30–50M for the broad platform? | Same technology, two very different asks appear in the docs for the same underlying product. |  |  |
| A3 | What's the **first vertical/use case**, concretely? | Five different candidates appear across the docs (contact federation, M&A diligence, SAP invoicing, banking payments, healthcare interop) with no single doc picking one. |  |  |
| A4 | What's the **brand/positioning stance**: "AI-powered" (v5 Sovereign AI Workspace framing) or explicitly anti-AI-hype ("Execution Coefficient," no black boxes)? | These are opposite marketing stances used at different points for the same product. |  |  |
| A5 | Is **121XML** the standard/format layer, and **121XQ** the product/workspace built on it — is that split final, or should they merge into one story? | Affects how we name/scope everything below. |  |  |
| A6 | Do we keep the **standards-body partnering** stance ("help W3C/IETF/HL7/etc. adopt facets of this") or the **"we are the universal replacement"** stance? Both appear; they imply different GTM motions. |  |  |  |

---

## Part B — Core Technical Features

| # | Feature | Description | Status | Source | Clarification Question | Decision | Keep in v1? |
|---|---|---|---|---|---|---|---|
| B1 | Name-Value primitive | Every object reduces to Name/Value pairs — the foundational lowest-common-denominator claim. | Concept | `Knowledge_Base/121_XML_Model.md` | Keep as the plain-language pitch, or fully superseded by the v4 facet model below? | | |
| B2 | Three Axioms (A1–A3) | Composition over inheritance, explicit type tags, homogeneous sequences — enables one profile → 6-language codegen. | Spec'd/Partial | `specs/121XML_Architecture_Guide_v2.md` +2 | Are these axioms still binding under the v4 SCSO redesign, or superseded? | | |
| B3 | Four Rules (R4–R7) | Sorted keys, explicit null-vs-absent, profile URI, SHA-256 content addressing. | Spec'd | `specs/121XML_Architecture_Guide_v2.md` +2 | **R5/R6 meaning drifted** between early and mature docs (see A-note below) — which definition is canonical? | | |
| B4 | Conformance levels L0–L3 | Syntactic → Structural → Canonical → Round-Trip Certified, with L2/L3 as paid certification tiers. | Spec'd, no issuing process | `specs/121XML_Architecture_Guide_v2.md` | Who certifies L2/L3? Is a certification business even in scope for v1? | | |
| B5 | Content addressing (`data://sha256:HASH:TYPE`) | Immutable, deterministic, self-describing addresses; basis for R7 hashing/tamper-proofing. | Partial (`xml121_addresser.py` unverified) | pervasive | Verify the addresser actually runs before relying on it elsewhere. | | |
| B6 | v4 Self-Contained Semantic Object (SCSO) | Object = signed Merkle-DAG of facets (payload/shape/context/rules/relations/provenance/space), each deferring to an existing standard (JSON Schema, JSON-LD, Datalog, W3C VC+DID). Encoding moves to CBOR/JCS + IPLD CIDs. | Design draft, nothing built | `specs/121XML_v4_SEMANTIC_OBJECT_DESIGN.md` | Is this the canonical object model going forward, replacing the earlier axioms/rules framing? | | |
| B7 | v5 synthesis — 121XQ sovereign AI workspace | Extends v4 into a product: one object graph, multiple lenses (Notion/Obsidian/Proton/Graphify-style), adds encrypted vault (L3.5) + projection layer (L4). | Design draft | `specs/121XQ_AI_OS_SPEC_v5_SYNTHESIS.md` | Is this the most current target architecture? Supersede everything before it? | | |
| B8 | Relations facet | Formal edge model (`{type, to, label, dir, props, order, valid_time, weight}`), ~20 core edge types, wikilink compilation. | Design draft, detailed | `specs/121XQ_RELATIONS_FACET_SPEC.md` | Ready to lock as-is, or still open? | | |
| B9 | Object profiles | 7 primary profiles (note/database/view/workspace/org-node/agent/pipeline) + supporting profiles. | Design draft | `specs/121XQ_OBJECT_PROFILES_SPEC.md` | Which profiles are actually needed for the chosen v1 use case (A3)? | | |
| B10 | Encrypted local-first vault (L3.5) | Two-plane CID model (semantic identity vs. storage address); private vs. shared/enterprise encryption modes. | Design draft, 8 crypto decisions unapproved | `specs/121XQ_VAULT_SPEC.md` | The shared-mode "confirm-by-hash" tradeoff was never disclosed in earlier compression marketing — approve, reject, or redesign? | | |
| B11 | Schema embedding vs. schema-free-by-reference | Early docs: embed full XSD in every packet. Mature spec: R6 is a profile-URI *pointer*, not embedded schema. Both called "schema-free." | Contradicted | backup `121xml_SCHEMA_EMBEDDING_STRATEGY.md` vs. mature R6 | Which one is actually "121XML" — embedded or referenced? | | |
| B12 | Universal specification language claim | 121XML claimed capable of representing *any* computing system — language grammars, compiler IR, protocols, standards, unbounded. | Early concept, unbounded | root `121XML_UNIVERSAL_SPEC.121xml` | Directly tied to A1 — keep the unbounded claim or scope it down? | | |
| B13 | Lossless compaction engine | Content-addressed sparse references replace truncation; claims 90–96% token reduction, 0% loss. | Spec'd + partial code | `specs/121XML_COMPACTION_ENGINE.md`, `xml121_compaction_engine.py` | Has this ever been run against a real long session to verify the reduction numbers? | | |
| B14 | Content-addressed inference architecture | "Git + IPFS + Inference" — immutable raw data + composable inference objects with lineage, shareable across agents. | Spec'd, not built | `specs/CONTENT_ADDRESSED_INFERENCE_ARCHITECTURE.md` | Never carried into the v4/v5 redesign despite being a conceptual ancestor of `relations`/`provenance` — merge in or drop? | | |
| B15 | Universal Memory Architecture | Persistent knowledge graph replacing lossy compaction; claims 78% token savings, 100% info preservation. | Spec'd + worked example | `specs/UNIVERSAL_MEMORY_ARCHITECTURE_ANALYSIS.md` +2 | Does this replace B13 (compaction engine), or do both exist for different purposes? | | |
| B16 | Sovereign data architecture | Data never leaves user storage; only addresses/metadata shared; permission grants with expiry/revocation. | Spec'd, not built | `specs/SOVEREIGN_DATA_ARCHITECTURE.md` | Consistent with B10's vault design? | | |
| B17 | 12-principle security/sovereignty spec | Self-custody keys, zero-knowledge, geofencing, decentralized topologies, portability, immutable audit, SBOM, etc. | Spec'd | `strategy/121XML_PRINCIPLES_SECURITY_SOVEREIGNTY.md` | Formally adopt as binding constraints on every future spec? | | |
| B18 | Agentic OS / protocol-schema adapter layer | Any protocol/schema converts to 121XML at the edge; one internal engine; adapters convert back out. | Spec'd + partial code | `specs/AGENTIC_OS_ARCHITECTURE.md` +2 | Verify `xml121_agent_orchestrator.py` actually runs. | | |
| B19 | MCP server / 121XML translator | Bidirectional 121XML↔JSON-RPC; built-in SWIFT MT103 + ISO 20022 PACS.008 support. | Claimed working, unverified per project's own audit | `xml121_mcp_server.py`, backup Phase 0 audit | Smoke-test before trusting "COMPLETE" status. | | |
| B20 | Voice connectors + native device integration | Siri/Google/Alexa (OS spec) vs. Siri/Google/Cortana/HarmonyOS Celia (native app reports) — two different platform sets. | Spec'd + code, unverified | `specs/121XML_AI_OS_MASTER_SPEC.md`, `reports/NATIVE_DEVICE_INTEGRATION_COMPLETE.md` | Reconcile the two voice-platform lists into one canonical set. | | |
| B21 | Format converters (30–50+ specs, 8 sectors) | SWIFT↔ISO20022, HL7↔FHIR, UBL↔ebXML, GraphQL, Protobuf, + finance/healthcare/education/geo/media/AI-ML/supply-chain/HR/non-profit. | Mostly spec'd; only SWIFT+ISO20022 verified working | `specs/121XML_AI_OS_MASTER_SPEC.md`, `reports/BUSINESS_CASE_VALIDATION_REPORT.md` | Tied to A1/A3 — which converters are actually needed for the chosen scope/vertical? | | |
| B22 | Document/media converters | DOCX/PDF/MD/XLSX/image ↔ 121xml. | Spec'd once, never referenced again | backup `121xml_CONVERTERS_SPEC.md` | In or out of v1? | | |
| B23 | AI/LLM model-definition profile | Wraps ONNX/PyTorch/TF/HuggingFace model metadata as a 121xml object with R7 hash — "model as a brain embedded in the app." | Spec'd once with LLaMA-2 example, never referenced again | backup `121xml_AI_MODEL_SPEC.md` | This is a distinctive idea (came up independently in the Meet121 research too) — worth reviving? | | |
| B24 | Auto-conversion feasibility matrix | Concrete difficulty/cost/success-rate table across 50 languages, 50 protocols, 40 standards; recommends 15-format Year-1 MVP. | Analysis only, never cross-referenced | backup `121xml_AUTO_CONVERSION_FEASIBILITY_MATRIX.md` | This is the most concrete "what to build first" data in the whole corpus — should it directly drive B21/A3? | | |
| B25 | Tab 2 object-graph renderer/editor | Pure projection of the vault; derives backlinks/version-history at read time; edits write new versions. | Design draft | `specs/121XQ_TAB2_RENDERER_SPEC.md` | Depends on B7/B10 being locked first. | | |
| B26 | 121ObjectMap | Reusable relationship-graph UI component, intended as "always tab 2" across every future 121-branded product. | Design draft + HTML seed exists | `specs/121XQ_ORCHESTRATION_PLAN_2026-08-19.md` | Confirm this is still the shared-component plan. | | |
| B27 | Embedded-platform template | Artifact-centric integration pattern (Grammarly/Canva/Office-AI style) — state attaches to the document, not a conversation. | Spec'd once as template | `specs/EMBEDDED_PLATFORM_TEMPLATE.md` | Relevant to any current product plan, or shelve? | | |
| B28 | 121XMLSilicon (hardware-native content addressing) | Staged roadmap: CPU-native crypto → DPU/CXL offload → FPGA proof → licensable IP. Deliberately spun out of the software project. | Own spun-off project | backup `121XMLSilicon/README.md` +1 | Confirm it stays fully separate (per diligence flag) and isn't pulled back into 121XML scope. | | |
| B29 | Session-continuity / anti-drift protocol | Every session reads `MASTER_DEFINITIONS.121xml`, populates `SESSION_CONTEXT_TEMPLATE.121xml`, checks proposals against `VALIDATION_FRAMEWORK.121xml`'s 4 hard-stop boundaries. | **Built and actually used** | root `.121xml` files | This is working process, not just spec — should this document itself be updated once Part A decisions land? | | |
| B30 | Claim Register / banned-claims governance | Formal list of banned unsourced claims (dollar figures, "100x," named companies as pipeline when only researched). | Built, self-imposed | `121XML_Claim_Register_v2.docx` | Keep enforcing against this list for any new material we write? | | |
| B31 | 121xml-banking plugin (concrete artifact) | Working auto-generated MCP plugin: SWIFT MT103 + ISO 20022 PACS.008 tools/resources/prompts. | **Built, concrete example exists** | `plugins/121xml-banking/*` | This is the single most concrete "it works" proof point in the whole project — should it be the reference example in the cleaned-up spec? | | |

---

## Part C — Contradictions Needing a Ruling (from the master consolidation, §5)

| # | Contradiction | Docs in conflict | Decision |
|---|---|---|---|
| C1 | R5/R6 rule definitions drifted (early: R5=no dropped fields, R6=field preservation; mature: R5=null-vs-absent, R6=profile URI) | backup `121XML_PROJECT_RECAP_STATUS.md` vs. `specs/121XML_Architecture_Guide_v2.md` | |
| C2 | Performance claim inversion ("100x"/"CPU registers" vs. "not faster than Protobuf, trades byte efficiency for decoupling") | Diligence Review flag vs. `specs/121XML_Architecture_Guide_v2.md` | |
| C3 | Centralization ban vs. marketplace/registry ambitions (plugin marketplace, community spec library, shared 121ObjectMap) | `VALIDATION_FRAMEWORK.121xml` vs. `specs/121XML_AI_OS_SPECS_BRAINSTORM.md` | |
| C4 | Dedup/privacy tradeoff surfaced late — "94% compression" marketed unconditionally, but cross-tenant dedup requires convergent encryption + a "confirm-by-hash" privacy leak, only disclosed in the Vault Spec | Early marketing docs vs. `specs/121XQ_VAULT_SPEC.md` | |
| C5 | "COMPLETE"/"PRODUCTION READY" claims vs. verified reality (Phase 0 audit found live site stale, `121xq.com` had no DNS, none of 31 Python files smoke-tested) | ~12 session/report files vs. `reports/PHASE0_GROUND_TRUTH.md` | |

---

## Next steps (per your instruction)

1. You fill in Part A (scope/strategy) and Part B/C decisions in this file.
2. Once decisions land, I'll identify exactly which spec/strategy/report files are superseded by each "kept" decision, propose a specific delete/archive list (not delete anything without you confirming the list), and reduce the project down to one clean set of files.
3. Then: architecture, then use cases — per your sequencing.
