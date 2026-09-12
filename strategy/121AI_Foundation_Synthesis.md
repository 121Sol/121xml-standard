# 121AI / 121XML — Foundation Synthesis
*Consolidated review of existing project documents · 30 July 2026*

## What exists today

Five documents currently define the project. Together they cover the technical spec, the language discipline for external claims, the commercial pilot vehicle, and an internal diligence audit:

1. **121XML_Technical_Reference.txt** — the spec itself: 8 primitive types, three axioms (A1 composition over inheritance, A2 explicit type tagging, A3 homogeneous sequences), four canonical rules (R4 sorted keys, R5 null-is-not-absence, R6 namespaced versioning, R7 lossless round-trip), and four conformance levels (L0 syntactic → L3 round-trip certified).
2. **121xml Standard Key Facts to Emphasize.docx** — a 15-minute pitch script built on the same axioms, plus proof points: 30 passing tests, 879→341 contact deduplication, SAP→Salesforce claimed at 6 months → 2 weeks.
3. ~~**121XML_Claim_Register_v2.docx**~~ — the governing document for language. It bans nine specific claims (unsourced dollar figures, "100x performance," "writes bytes directly into CPU registers," named firms shown as pipeline, the $ONEOM token) and gives the approved replacement for each. **[Update 2026-08-28: determined to be a Claude CoWork fabrication — including its own cited "approved" sources — and deleted. Its 4-part structure is kept as a framework; its content is void. See `121XML_SPECIFICATION_DECISION_TABLE.md` B30.]**
4. **121XML_Enterprise_Pilot_Proposal_v2.docx** — a fixed-scope, fixed-fee 90-day evaluation template: profile authoring, conversion gateway, round-trip harness, hash verification, structural relationship viewer. Explicitly scoped to *not* be a throughput benchmark.
5. **121XML_Diligence_Readiness_Review.pptx** — an internal red-team pass against a longer source document (not in this folder), dated the same day as the Claim Register. It withdrew two earlier objections (a working Python AST→121XML compiler exists; six components are built) and confirmed four live risks: unsourced figures, the inverted CPU-register performance claim, silicon/FPGA spend inside a seed round, and the $ONEOM token's securities exposure.

## How this maps to the ecosystem vision you described

Your framing today — a universal standard that any AI system or legacy tool can read/write bidirectionally, with a dropdown or Obsidian-style relationship-map interface, letting users mix any input/output agents or tools — is **consistent with what's already spec'd**, but the existing documents describe the *protocol and enterprise-pilot* layer, not the *ecosystem/UI* layer:

- The **schema-in-band design** (R6 profile URI, A2 type tags) is exactly what would let arbitrary AI systems parse an object they've never seen — the technical precondition for "any input agent, any output agent."
- The **"3D relationship workspace"** and **"structural relationship viewer"** are named as already-built or in-scope components in two documents (Key Facts and Pilot Proposal). This is the closest existing artifact to the Obsidian-style graph UI you're describing — worth checking what actually exists in code before citing it further, since the Diligence Review treats "six components built" as a claim under scrutiny, not a verified fact.
- Nothing in the five documents yet describes the **dropdown/agent-selection UI**, the **connector/tool marketplace concept**, or **programmatic conversion of standard AI-space objects** (prompts, tool schemas, traces) as a distinct deliverable — the closest is one Claim Register line: *"Carry tool schemas, prompts and traces across vendors without redeployment."* That's a one-sentence claim, not a spec.

## Gaps and open questions

- **No document defines the object model for AI-native artifacts** (agent configs, tool/function schemas, prompts, conversation traces, connector definitions) the way the Technical Reference defines the general type system. If the ecosystem vision is the next phase, this is the missing spec.
- **No UI/UX spec exists** for the dropdown selector or relationship-map interface — only a claimed "3D relationship workspace" component of unverified status.
- **The Diligence Review references a source document not present in this folder** ("121XML_Discussion_on_Monetizing.docx," ~18,570 words) — that's where the fuller monetization/vertical/token narrative lives. Worth locating if you want the complete picture.
- **Four items are flagged as unresolved and blocking** in the Diligence Review as of 23 July 2026: unsourced figures still in investor material, the $ONEOM token, the inverted performance claim, and FPGA/silicon spend inside the seed. ~~The Claim Register already reflects the corrected language for the first three~~ — **the Claim Register itself was later determined fabricated and deleted (2026-08-28), so this no longer holds; these four items should be treated as still open** until re-verified against real sources. It's not clear from these documents whether the source deck itself was ever edited.
- **Conformance levels L2/L3 (paid, certification-based)** are defined but no pricing, audit process, or authority (who issues certification?) is specified anywhere.

## Suggested next step

If you're moving toward the ecosystem/UI layer next, the natural sequencing based on what's already validated would be: (1) confirm what's actually built vs. claimed for the relationship-map component, since that's your closest existing asset to the Obsidian-style UI; (2) draft the AI-object type profile (agent, tool schema, prompt, trace) as a named profile URI under the existing R6 versioning scheme, so it inherits the round-trip and conformance machinery already spec'd rather than starting a parallel system.

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*