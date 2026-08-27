# 121AI — MVP Project & Technical Architecture
*v2 · 30 July 2026 · Revised after reviewing the full 121XML project folder (F:\AI\Claude\Projects\121XML)*

## What changed from v1

v1 was drafted from five documents only. The fuller project folder adds a canonical architecture guide (`121XML_Architecture_Guide_v2.md`), four SVG diagrams, and a living program-state file (`121XML_Program_State.121xml`) that records open issues and pending decisions. This version aligns the MVP to that canonical architecture instead of inventing parallel terminology, and calls out one real inconsistency that needs a decision before any connector gets built.

**Also confirmed by the folder cleanup:** the hardware/silicon vision has already been split into its own project (`F:\AI\Claude\Projects\121XMLSilicon`) and a stray unrelated toolkit (`SystemClean`) was removed. Neither belongs in this architecture — good, nothing to undo here.

## 1. One thing to resolve before writing any code

The spec uses two different profile URI schemes in different documents, and this will break interoperability if it isn't picked now:

- `121XML_Architecture_Guide_v2.md` and all four diagrams use `urn:121xml:contact/1.1`
- `121XML_Program_State.121xml` (the actual governing instance document) uses `https://spec.121.us/121xml/1.1` as the profile, with a separate `id="program.state.2026-07-23"` attribute
- The original Technical Reference's worked example also uses the `https://spec.121.us/...` form

R6 requires "every document declares its profile URI and version" — but a receiver that only recognizes one scheme won't recognize the other. This needs to be one convention, not two, before the first real profile (Contact) is written. Recommendation: use the `https://spec.121.us/121xml/1.1/<object-type>` form (resolvable HTTPS URI, can actually host a spec page later) and treat `urn:121xml:...` in the Architecture Guide's examples as shorthand notation to be corrected, not a second valid form.

## 2. What the MVP proves

One sentence: **a 121XML-native object can be created, stored, viewed as a relationship graph, and moved losslessly in and out of at least one external system — through a UI a non-engineer could use.**

The Program State file lists "first vertical: contact federation, or M&A diligence data rooms" as an open decision (item 3 under `decisions_pending`). This MVP architecture implicitly resolves that in favor of **contact federation** — it's the object type with a real proof point already (879→341 dedup) and a named "universal contact importer" component marked `working` in `assets_built`. Worth having Rashad explicitly ratify that choice rather than letting it default silently, since M&A diligence rooms is also a real candidate and ties more directly to 121 Solutions' existing client relationships.

Out of scope for this pass: agent/session/memory object types, MCP/A2A protocol bridging, multi-tenant auth, and the L2/L3 certification business (paid conformance, per the Architecture Guide's ~$500/yr and ~$2,000/yr figures — those are commercial machinery, not MVP concerns).

## 3. Mapping the MVP onto the canonical 5-layer architecture

The Architecture Guide already defines five layers. The MVP should be described as a concrete instance of those layers, not a separate design:

| Canonical layer | MVP implementation |
|---|---|
| **Layer 1: Source Systems** | CSV file, then one CRM export format. (Guide lists six source types generally — MVP handles the two most tractable.) |
| **Layer 2: Conversion Gateway (Inbound)** | Python ingest adapter: profile loader → A1–A3 type enforcement → R4 canonical sort → R7 hash envelope. This is Pattern 1 (Generating 121XML) from the Technical Reference, applied literally. |
| **Layer 3: Canonical 121XML (in-memory)** | Same as spec — but the MVP also persists this layer (SQLite), which the canonical guide treats as transient. Persistence is the MVP's one addition to the reference architecture. |
| **Layer 4: Output Transformation** | MVP needs only Path A (Storage) and a partial Path C (Transmission, localhost only). Codegen (Path B) and Reference/docs (Path D) are deferred — no need for six-language codegen until there's a second consumer beyond this one UI. |
| **Layer 5: Consumption** | Pattern A (schema-free parser) only. The relationship graph UI is a schema-free reader — it never needs generated code because it's reading from the same object store that wrote the data. |

This mapping matters because it means the MVP doesn't need to build a fifth of a new architecture — it needs to build a thin, working slice through all five existing layers, end to end, on one object type.

## 4. The core loop

```
Source system (CSV / CRM export)
        │
        ▼
  Ingest adapter (Layer 2)  ──────►  121XML Contact object (typed, hashed, profiled)
        │                                       │
        │                                       ▼
        │                          Local object store (Layer 3, persisted)
        │                                       │
        ▼                                       ▼
  Round-trip export  ◄──────────────  Relationship graph UI (Layer 5)
  (byte-compare test, L3)              (reads objects, renders nodes/edges)
```

Every read/write goes through the same serializer, so R7 round-trip integrity is enforced by construction rather than tested after the fact.

## 5. Component breakdown

**5.1 Object model.** One profile: `https://spec.121.us/121xml/1.1/contact` (see §1 on resolving the URI scheme first). Fields: name, email, phone, address (nested map), organization (ref), tags (seq), source-system, source-id, `__hash`. This is close to verbatim the contact example already in the Technical Reference and the Architecture Guide's Layer 3 example — no new spec design needed, just formal publication as a profile document.

**5.2 Ingest adapter.** Python module per source format. Implements Pattern 1 from the Technical Reference exactly: traverse → tag types (A2) → sort keys (R4) → hash (R7) → emit. This is also where field-coverage gets measured for the round-trip scoreboard.

**5.3 Object store.** SQLite: one table (`id`, `raw_xml`, `profile`, `version`, `hash`, `updated_at`) plus an edge index for `ref` fields (organization links, dedup merges). Swap-in point later: a real graph DB once relationship queries outgrow SQLite joins.

**5.4 Relationship graph UI.** Electron + React, force-directed graph (`react-force-graph`). This is a literal implementation of the "3D relationship workspace" already marked `working` in the Program State's `assets_built` list — worth checking what that existing component actually contains before rebuilding it from scratch; it may already be most of this piece.

**5.5 Local API.** FastAPI service exposing `GET /objects`, `GET /objects/:id`, `POST /objects`, `GET /objects/:id/roundtrip`. This is the seam where an MCP server attaches later without touching the object model — expose the same store as MCP tools (`search_contacts`, `get_contact`, `merge_contacts`) once an external agent needs to reach in.

**5.6 Round-trip harness.** Implements the Architecture Guide's L3 test exactly: load N production records → export → reimport schema-free → byte-compare field by field → publish scoreboard (pass/partial/fail per field), matching the HTML report format already specified in the guide. This is simultaneously the MVP's test suite and the Pilot Proposal's deliverable #3 — same code serves both purposes.

## 6. Recommended stack

| Layer | Choice | Why |
|---|---|---|
| Object serialization | Python, hand-rolled | Exact control over key sorting (R4) and type tagging (A2) — generic XML libraries won't enforce the axioms. |
| Object store (MVP) | SQLite | Zero ops, file-based, matches "local-first" positioning. |
| Local API | FastAPI | Minimal, typed, straightforward to expose as an MCP server later. |
| Desktop UI | Electron + React | Matches the AIEOS Nexus screenshot's evident stack; reusable as a web app later. |
| Graph rendering | `react-force-graph` (three.js-backed) | Delivers the "3D relationship workspace" language literally. |
| Round-trip harness | Plain Python + `pytest` | It's a test, not a product surface — no framework needed. |

Nothing here requires a token, blockchain, or custom silicon — and the silicon question is now moot for this project specifically, since it lives in `121XMLSilicon` as a separate effort.

## 7. Build sequence

1. **Resolve the profile URI convention (§1)** — a decision, not engineering work, but blocking.
2. Publish the Contact profile document.
3. Build the serializer/parser pair with hash + round-trip check; prove it on 10 records.
4. **Audit the existing "assets_built" components** (Python AST compiler, JSON-to-121XML proxy, SHA-256 envelope, 3D relationship workspace, universal contact importer, structural test suite) before building anything new — the Program State marks all six as `working`, so some of steps 3-6 here may already exist and just need locating and verifying rather than rebuilding.
5. Build the CSV ingest adapter against a real (anonymized) contact export — reproduce the 879→341 result on new data as the credibility check.
6. Build the local API and persistent object store.
7. Build or adapt the graph UI last.
8. Run the round-trip harness, publish the field scoreboard — this becomes both the MVP's proof and reusable pilot collateral.

## 8. Open decisions for you

- **Ratify the first vertical** as Contact federation (implied by this MVP) vs. M&A diligence data rooms (the Program State's other stated candidate) — this document assumes Contact, but it's your call to make explicit.
- **Pick one profile URI scheme** (§1) — recommend `https://spec.121.us/121xml/1.1/...` over the `urn:121xml:...` form used in the Architecture Guide's examples.
- **Locate and inspect the six "working" components** referenced in the Program State before scoping new build work — if the 3D relationship workspace or contact importer already exist as real code (not just claims), this MVP could be mostly integration rather than new development.
- Electron vs. web app for the UI, and whether the round-trip scoreboard goes public now or stays internal — both carried over from v1, still open.
