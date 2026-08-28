# 121XML Specification — Feature & Decision Table

**Status: Round 1 decisions recorded 2026-08-28 (Rashad Khan).** Remaining open items are marked `OPEN` below. Full backing detail remains in [`121XML_MASTER_IDEAS_CONSOLIDATION.md`](121XML_MASTER_IDEAS_CONSOLIDATION.md).

**Legend:** þ Agreed · O Claude Designed (accepted as Claude's contribution) · ý Not Agreed · `OPEN` = still needs a decision

---

## Part A — Scope & Strategy Decisions

| # | Question | Decision (RK, 2026-08-28) |
|---|---|---|
| A1 | Narrow vertical vs. universal-everything claim? | **No v1 scope restriction.** 121xml is a standard for converting *any* format. Any programming language with a definitive spec (rules, syntax, semantics, attributes) is itself a set of objects expressible in 121xml value pairs — Python, Rust, etc. — so automated cross-language conversion is feasible and in scope. This explicitly overrides the earlier "narrow & deep, ERP-only" recommendation. |
| A2 | Funding/scale target? | **Not needed at this stage.** No funding-scale decision required right now. |
| A3 | First vertical/use case? | **Contact Federation / CRM.** |
| A4 | Brand/positioning stance? | `OPEN` — **assigned to a branding specialist** (subagent or 121Enterprises) to research and decide. Not decided by RK directly. |
| A5 | Is 121XML=standard, 121XQ=product split final? | **Yes, final.** 121XML = standard/format layer. 121XQ = the AI OS built on 121XML principles/specs — see D1 below, largely compatible with Proton Lumo's architecture. |
| A6 | Standards-body partner vs. "universal replacement" stance? | **Collaboration is better.** Pursue the standards-body partnering stance, not a "we replace everything" stance. |

---

## Part B — Core Technical Features: Decisions

| # | Feature | Decision |
|---|---|---|
| B1 | Name-Value primitive | þ Agreed |
| B2 | Three Axioms A1–A3 | O Claude Designed |
| B3 | Four Rules R4–R7 | O Claude Designed |
| B4 | Conformance levels L0–L3 | O Claude Designed |
| B5 | Content addressing | þ Agreed |
| B6 | v4 SCSO redesign | þ Agreed |
| B7 | v5 synthesis (121XQ sovereign AI workspace) | þ Agreed |
| B8 | Relations facet | þ Agreed — **note: relations are just another object in 121xml**, not a privileged/special facet type. *(Flag for QA: this nuances the v4 facet-based design, where `relations` is currently one of several named facets — reconcile.)* |
| B9 | Object profiles | þ Agreed — **note: a profile is an object, or a collection thereof.** |
| B10 | Encrypted local-first vault (L3.5) | þ Agreed |
| B11 | Schema embedding vs. schema-free-by-reference | þ Agreed (schema embedding) / ý Not Agreed (that it's a contradiction). **See D2 below — this is fully resolved, not a contradiction: two different things were being conflated.** |
| B12 | Universal specification language claim | þ Agreed — **verify** (technical verification needed before relying on the unbounded claim) |
| B13 | Lossless compaction engine | þ Agreed — **verify** (run against a real long session before trusting the 90–96% figure) |
| B14 | Content-addressed inference architecture | þ Agreed — **needs refining** |
| B15 | Universal Memory Architecture | þ Agreed |
| B16 | Sovereign data architecture | þ Agreed |
| B17 | 12-principle security/sovereignty spec | þ Agreed |
| B18 | Agentic OS / adapter layer | þ Agreed |
| B19 | MCP server / translator | þ Agreed |
| B20 | Voice connectors + native device integration | þ Agreed — **or pivot toward Agentic clone personas** (i.e. AI persona clones handling voice/video, not just generic assistant-platform hooks). **Action: update the platform list to the current leading native device/AV/chat technologies, ordered by descending user count** (replaces the old Siri/Google/Alexa vs. Siri/Google/Cortana/HarmonyOS split). |
| B21 | Format converters | þ Agreed — **target list superseded/extended by the standards compatibility list in D2 below**, which replaces the old abstract feasibility matrix with real named standards + real usage scale. |
| B22 | Document/media converters | þ Agreed |
| B23 | AI/LLM model-definition profile | þ Agreed |
| B24 | Auto-conversion feasibility matrix | þ Agreed — see D2 (superseded by real standards list) |
| B25 | Tab 2 object-graph renderer/editor | þ Agreed |
| B26 | 121ObjectMap | þ Agreed |
| B27 | Embedded-platform template | þ Agreed — **scope: lives in 121Enterprise** |
| B28 | 121XMLSilicon | þ Agreed — **stays a separate project** (confirmed, not pulled back into 121XML scope) |
| B29 | Session-continuity / anti-drift protocol | þ Agreed — **must be built in** (enforced mechanism going forward, not just a documented process) |
| B30 | Claim Register / banned-claims governance | **Resolved 2026-08-28: `121XML_Claim_Register_v2.docx` determined to be a Claude CoWork fabrication (including its cited "approved" sources, e.g. the "Fivetran Enterprise Data Infrastructure Benchmark, 2026" and the $7.5B–$33.8B market-size range) — deleted, both copies. The document's 4-part *structure* (banned language / approved claims / claims-with-cost / sourcing standard) is accepted as a governance framework to reuse going forward. Its specific *content* — every banned/approved claim, every cited figure — is void and must be rebuilt from genuinely verified sources, not reused from the deleted file.** |
| B31 | 121xml-banking plugin | þ Agreed — kept as the reference working example |

---

## Part C — Contradictions: Rulings

| # | Contradiction | Ruling |
|---|---|---|
| C1 | R5/R6 rule-definition drift | **Assigned to the 121Enterprise team to resolve.** Note for the team: this contradiction was introduced by Claude Code work across different sessions — not a deliberate design change, so there is no "intended" version to preserve; pick whichever definition is more internally consistent with the mature v4/v5 specs. |
| C2 | Performance claim inversion ("100x"/CPU-register claim vs. "not faster than Protobuf") | **Scrub the earlier claim** from any circulating materials. The mature "trades byte efficiency for decoupling" framing is correct and stands. |
| C3 | Centralization ban vs. marketplace ambitions | **Reconciled, not a real contradiction.** The `VALIDATION_FRAMEWORK.121xml` hard ban on central registries applies to **121XML the standard's core architecture** (no forced central index for the format itself). It does **not** apply to **121XQ**, which is an AI OS/ecosystem built on top of 121XML and is allowed to have internal marketplace/registry structures — 121Metaverse, 121Skills, Virtual Assistants (job/role/persona-described agents), and other objects that can be traded, gifted, or lent are all legitimate parts of the 121XQ ecosystem, not violations of the 121XML-level ban. |
| C4 | Dedup/privacy tradeoff disclosed late | **Assigned to a 121Enterprise specialist** to research, reconcile, and remove inconsistencies between the early "94% compression" marketing claim and the Vault Spec's later cross-tenant privacy disclosure. |
| C5 | "COMPLETE"/"PRODUCTION READY" claims vs. verified reality | **Remove all such claims/comments** from existing docs. **121Enterprise team to rebuild the affected components after the revised specs are agreed** — not just relabel status, redo the work under the settled spec. |

---

## Part D — New Inputs From This Round (2026-08-28)

### D1. Backend model router — Proton Lumo comparison (`OPEN` decision)

RK's observation: most 121XML/121XQ concepts closely match **Lumo by Proton** ([github.com/ProtonLumo](https://github.com/ProtonLumo)). Lumo's proprietary backend "router" dynamically selects among multiple models depending on task:
- General reasoning and text (their default/proprietary model)
- **OpenHands 32B** — a Qwen fine-tune specialized for coding and multi-step tasks
- **OLMO 2 32B** — built by the Allen Institute for AI

121XQ (the AI OS built on 121XML) already lets the user select a backend processing engine. RK's proposal: **consider adding OpenHands 32B and OLMO 2 32B as additional selectable backend engines**, alongside whatever's already offered. Key differentiator to preserve vs. Lumo: 121XML/121XQ specs keep data fully private — the user owns both the data and the security keys, with no data leaks by design (per the sovereign data architecture, B16, and the 12-principle security spec, B17). Nearly all Lumo's features and rules appear compatible with what's already spec'd.

**Open question (unresolved — needs an explicit decision):** *"Does it make sense to have a similar [Lumo-style multi-backend-router] architecture for our products?"* — Recommend this go to whoever owns 121XQ's AI-OS architecture (121Enterprise / Claude with RK) as a formal design decision, not assumed yes by default.

### D2. Schema embedding vs. schema-free — full resolution (closes B11 / C on this topic)

RK's clarification splits this into two genuinely separate concerns that earlier docs had conflated as one "schema embedding vs. schema-free" contradiction. Both are true; they answer different questions:

**(a) Data Definition side — how 121xml itself defines an object.** 121xml's object model is close to a JSON-B-style approach: *any* object, concept, rule, data structure, or relationship reduces to a name/value pair, and is store-addressable for fast retrieval. It is secured by user-owned public/private key pairs under industry-standard, zero-trust security protocols. Once an object is defined — including all of its dependent elements (facets, rules, type, relationships, attributes) — **that full definition is embedded at transmission time as a header packet alongside the data**, in a JSON-B-like format. This is schema embedding, and it is **agreed and correct** for how 121xml defines and transmits its own objects.

**(b) Data Transmission Protocols / XML-standards compatibility — a separate concern.** 121xml must remain compatible with (able to ingest/convert to and from) the large, well-established universe of real-world XML-based standards already in production use. If a sender transmits a data packet identifying a known standard or namespace, 121xml infrastructure must recognize and convert it. **This is not a contradiction with (a)** — it's a compatibility/converter requirement layered on top of 121xml's own embedded-definition model. RK supplied the following concrete, prioritized target list — **this supersedes the old, more abstract Auto-Conversion Feasibility Matrix (B24) as the real target list** for B21 (Format converters):

| Domain | Standard | Purpose | Approx. Scale |
|---|---|---|---|
| **Web Tech & Infra** | SVG | 2D web graphics | Billions of web pages |
| | RSS / Atom | Blog/news/podcast syndication | 400M+ active podcast listeners |
| | XHTML | Web page layout | Millions of legacy/static pages |
| | SAML | Enterprise SSO authentication | 1B+ enterprise users/day |
| | XMPP | Instant messaging / presence | Hundreds of millions of users |
| | SOAP | Enterprise web services | Hundreds of thousands of legacy integrations |
| **Business & Finance** | XBRL | Digital financial statements / SEC filings | 100,000+ public companies/regulators |
| | FpML | OTC derivatives trading | Thousands of banks/hedge funds/clearing houses |
| | FIXML | Global trading (FIX protocol XML variant) | Thousands of institutional brokerages/exchanges |
| | ISO 20022 (XML) | Global financial messaging (SWIFT) | 11,000+ financial institutions |
| | cXML | B2B e-commerce procurement | Millions of businesses (e.g. SAP Ariba) |
| **Document & Productivity** | Office Open XML (docx/xlsx/pptx) | MS Office default format | 1.2B+ Office users |
| | OpenDocument Format (odt/ods/odp) | LibreOffice/Google Docs compat | 300M+ users |
| | DITA | Technical documentation authoring | Tens of thousands of enterprise doc systems |
| **Healthcare** | HL7 v3 / CDA | Electronic health record exchange | Hundreds of thousands of hospitals/clinics |
| **Logistics & Geo-Spatial** | GPX | GPS waypoint/route/track sharing | 100M+ users (Strava, Garmin, etc.) |
| | KML | Geographic data visualization | 1B+ Google Earth/Maps users |
| **Aerospace & Trajectory** | AIXM | Digital airspace boundaries/restrictions | FAA, Eurocontrol, 100+ aviation authorities |
| | FIXM | Dynamic 4D flight trajectories | Global commercial/military air traffic mgmt |
| | NASA-UTM | Low-altitude drone 4D flight paths | Hundreds of global drone operators |
| **Drone Telemetry & Mission Planning** | MAVLink (XML schemas) | Drone telemetry / 4D path tracking | Millions of defense/commercial/open-source drones |
| | KML `<gx:Track>` | 3D position + timestamp mapping | Hundreds of thousands of drone/military GIS tools |
| | STANAG 4586 | NATO drone control / 4D vehicle status | All Allied military forces |
| **Tactical Data Links & Defense** | Cursor-on-Target (CoT) | US military real-time asset tracking | Millions of military assets (incl. ATAK) |
| | STANAG 4609 (KLV) | NATO video-to-UTC-timestamp metadata | Virtually all Western military ISR drone platforms |

### D3. Assignment log (who does what next)

| Item | Assigned to |
|---|---|
| A4 — branding/positioning stance | Branding specialist (subagent or 121Enterprises), research-driven decision |
| C1 — R5/R6 canonical resolution | 121Enterprise team |
| C2 — scrub inverted performance claims from circulating material | 121Enterprise team |
| C4 — dedup/privacy tradeoff reconciliation | 121Enterprise specialist |
| C5 — remove false "complete" claims; rebuild affected components post-spec-agreement | 121Enterprise team |
| D1 — Lumo-style multi-backend-router decision | `OPEN` — needs an explicit decision, owner TBD |
| B30 — Claim Register clarification | **Resolved** — document was fabricated, deleted; framework kept, content voided (see B30 row above) |

### D4. Build sequencing (proposed, not yet executed)

RK's direction: get 121Enterprise team agents to QA all 121xml + 121xq specs against these decisions, then design and build the 121xml standard implementation and the 121xq AI OS (incl. converters, dashboards, tools), followed by 121Metaverse and the Industry Verticals — sequenced or parallel, at Claude's discretion.

**Proposed phasing:**
- **Phase 1 — QA pass (in progress as of 2026-08-28):** an agent reconciles the full 121XML + 121XQ spec corpus against every decision recorded above, flags any spec content that's now contradicted by a Part A/B/C ruling, and produces a QA'd, internally-consistent spec bundle. Low-risk, analysis/writing only.
- **Phase 2 — design:** per-track architecture design (121XML core, 121XQ AI OS + addons, 121Metaverse, Industry Verticals), grounded in the QA'd Phase 1 output.
- **Phase 3 — build:** actual implementation, once Phase 2 designs are reviewed.

Phase 1 is running now. **Phases 2–3 are a much larger commitment (real build effort across five tracks) and are held for review before launch, rather than started unsupervised.**

---

## Next steps

1. `OPEN` items remaining: A4 (branding) and D1 (Lumo-style backend router) still need decisions. B30 (Claim Register) is now resolved — see above.
2. Phase 1 QA agent pass is running against this table.
3. Once Phase 1 lands: review its output, then decide whether to proceed to Phase 2 (design) per track.
