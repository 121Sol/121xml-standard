# Phase 0 — Ground Truth & Canonical Corpus Reconciliation

**Author:** Claude Code (orchestrator)  ·  **Date:** 2026-08-19  ·  **Mode:** read-only recon
**Scope of this pass (user-approved):** reconcile the corpus + verify live sites, then report.
**Nothing built, pushed, moved, or deployed.**

---

## 1. Corpus at a glance

- Location: `F:\AI\.Claude\projects\121XML`
- **274 files / 454.7 MB** (excluding `node_modules`, `__pycache__`).
- **443 MB (97%) is 4 session-export files** → archive/gitignore, never commit:
  `RK 121MXML eco system session.rtf` (217 MB), `.pdf` (114 MB), `_Optimized.pdf` (112 MB), `.docx` (5.4 MB).
- Real substance ≈ **12 MB**: 90 `.md`, 31 `.py`, 29 `.html`, 19 `.121xml`, 15 `.txt`, 14 `.json`, decks.
- Timeline: **2026-07-07 → 2026-08-19**. Brand evolved **121AI → 121XML → 121XQ** (rebrand 2026-08-09).

## 2. Verified live-site status (2026-08-19)

| Domain | DNS | HTTP | Reality |
|---|---|---|---|
| **121xml.com** | 104.21.14.186 (Cloudflare) | **200**, 17,982 B, *"121XML - Lossless Data Protection & AI Environment"* | **LIVE**, but serves the **old single-page `index.html`** — pre-121XQ rebrand |
| **www.121xml.com** | (Cloudflare) | 200, identical | mirror of apex |
| **121xq.com** | **none** | fails | **NOT LIVE** — domain not pointed/configured |

> Consequence: the live site is stale vs. the current 121XQ brand + master spec. `121xq.com`
> needs DNS + first deploy. Every prior `DEPLOYMENT_COMPLETE` doc overstated the live state.

## 3. Canonical vs. superseded (recommended dispositions)

Legend: **KEEP** = canonical source of truth · **MERGE** = fold into a canonical doc ·
**ARCHIVE** = historical, move to `/archive` · **IGNORE** = never commit (bloat).

### 3.1 The standard & core spec — **KEEP (authoritative set)**
- `Knowledge_Base/121_XML_Model.md` (+ `_Additional_Reference.md`) — foundational Name-Value axiom
- `121XML_AI_OS_MASTER_SPEC.md` (98 KB, Aug 8) — **primary spec**
- `121XML_ARCHITECTURE_MEMORY_DETERMINISM.md`, `121XML_PRINCIPLES_SECURITY_SOVEREIGNTY.md`
- `121XML_AI_OS_FINAL_SPECIFICATIONS.md`, `121XML_FRAMEWORK_SPECIFICATION_SUMMARY.md`
- `121XML_UNIVERSAL_SPEC.121xml`, `MASTER_DEFINITIONS.121xml`, `ARCHITECTURE.121xml`
- **ARCHIVE (older/brainstorm):** `121XML_Architecture_Guide_v2.md` (Jul 25), `121XML_AI_OS_SPECS_BRAINSTORM.md`,
  `121XML_V3_TO_AI_OS_UPGRADE.md`, `121xml_complete_reference.md`

### 3.2 Brand & positioning — **KEEP 121XQ set; ARCHIVE 121AI set**
- KEEP (Aug 9): `121XQ_BRAND_POSITIONING.md`, `121XQ_QUICK_REFERENCE.md`, `121XQ_LAUNCH_STRATEGY.md`,
  `WHAT_IS_XQ_TECHNICAL_GUIDE.md`, `121XQ_REBRANDING_COMPLETE.md`
- ARCHIVE (superseded brand): `121AI_BRAND_GUIDELINES.md`, `121AI_BUSINESS_CASE.md`,
  `121AI_MVP_Architecture.md`, `121AI_Foundation_Synthesis.md`, `121AI_DEPLOYMENT_GUIDE.md`

### 3.3 Deployment docs — **COLLAPSE 13 → 1 canonical `DEPLOYMENT.md`**
MERGE all of these (heavy overlap, session-by-session "complete" claims):
`DEPLOYMENT_COMPLETE`, `DEPLOYMENT_GUIDE`, `DEPLOYMENT_GUIDE_COMPLETE`, `DEPLOYMENT_INSTRUCTIONS`,
`DEPLOYMENT_READY_STATUS`, `DEPLOYMENT_READY_SUMMARY`, `DEPLOYMENT_CONFIG`, `DEPLOYMENT_TO_121XML_COM`,
`DEPLOYMENT_AND_GETTING_STARTED`, `PRODUCTION_DEPLOYMENT_COMPLETE`, `FINAL_DEPLOYMENT_CHECKLIST`,
`PHASE_14_SITE_CONFIG_COMPLETE`, `PRODUCTION_VERIFICATION`.
KEEP working scripts (dedupe): `deploy.sh`, `PRODUCTION_DEPLOYMENT.sh`, `DEPLOY_PowerShell.ps1`,
`setup-github-repos.ps1`, `push-*.ps1` — verify before trusting.

### 3.4 Architecture / memory / agentic — **KEEP**
`AGENTIC_OS_ARCHITECTURE.md`, `AGENTIC_OS_DEVELOPER_GUIDE.md`, `AGENTIC_OS_SUMMARY.md`,
`SOVEREIGN_DATA_ARCHITECTURE.md`, `CONTENT_ADDRESSED_INFERENCE_ARCHITECTURE.md`,
`UNIVERSAL_MEMORY_ARCHITECTURE_ANALYSIS.md`, `MEMORY_IMPLEMENTATION_WALKTHROUGH.md`,
`DATA_MODELS_AND_PROFILES.md`, `121XML_COMPACTION_ENGINE.md`

### 3.5 AI-integration blueprints — **KEEP (one per engine)**
`ANTHROPIC_121XML_INTEGRATION_BLUEPRINT.md`, `ANTHROPIC_121XML_PROFILE_SPECIFICATIONS.md`,
`121XML_ANTHROPIC_INTEGRATION_STRATEGY.md`, and `OpenAI/`, `Google_Gemini/`, `DeepSeek/`,
`Microsoft_Copilot/`, `ByteDance_Alibaba/` blueprints.

### 3.6 Code — **KEEP → repo `/core`, `/native`, `/tests`**
Engine: `xml121_*.py` (main_engine, converter, compaction_engine, addresser, auditor, compressor,
database_adapters, format_profiles, mcp_server, agent_orchestrator, persistence_layer, voice_connectors),
`121xml_library.py`, `121xml_plugin_sdk.py`, `mcp_121xml_translator.py`, `mcp_compaction_integration.py`,
`converter_tool.py`, `backend_api_server.py`, `deploy_manager.py`, `plugin_auto_generator.py`.
Native: `Agent121AI*.{kt,swift,cs,ts}`. Tests: `test_121ai_complete.py`, `tests_compaction_engine.py`,
`tests_phase2_complete.py`, `deployment_verification.py`. **All need a smoke-test before "works" is claimed.**

### 3.7 Web/UI — **pick ONE canonical site build; ARCHIVE prototypes; 121ObjectMap = component seed**
- Live now: `index.html` == `121xml_complete_platform.html` (17,623 B).
- Candidates for canonical site: `website_v3_complete.html` (55 KB, most complete), `website_v2_interactive.html`.
- **121ObjectMap seed:** `121xml_object_graph_visualizer.html`, `121ai-neuro-graph-interface.html`,
  `schema_explorer.html`, `content_addressing_explorer.html`.
- ARCHIVE the many one-off prototype HTMLs after the canonical build is chosen.

### 3.8 Session/status/progress — **ARCHIVE (historical)**
`SESSION_3_COMPLETION_SUMMARY`, `SESSION2_PROGRESS_SUMMARY`, `PROTECTION_CHECKPOINT_SESSION2`,
`STATUS_UPDATE`, `STATUS_SUMMARY.121xml`, `PHASE5_121XML_AI_OS_COMPLETE`, `INTERACTIVE_PLATFORM_COMPLETE`,
`LOGO_INTEGRATION_COMPLETE`, `PLATFORM_INTEGRATION_COMPLETE_SUMMARY`,
`121XML_MCP_INFRASTRUCTURE_DEPLOYMENT_COMPLETE`, `CONSOLIDATION_NOTES`, `FOLDER_ANALYSIS_SUMMARY`,
`DELIVERY_SUMMARY`, `DELIVERABLES_ROADMAP_15_PARTS`, `MATERIALS_UPDATE_ROADMAP`,
`SESSION_3_COMPLETION_SUMMARY`, `README_IMPLEMENTATION`, `IMPLEMENTATION_MASTER_PLAN`, `PROJECT_EXECUTION_PLAN`.

### 3.9 Business/GTM decks — **KEEP newest; ARCHIVE dupes**
KEEP `BUSINESS_CASE_VALIDATION_REPORT.md` (Aug 16, newest), `121XML_AI_OS_VALUE_PROPOSITION.md`.
Decks (`.pptx/.docx/.pdf`) — keep latest of each theme; two identical `121XML_Diligence_Readiness_Review.pptx`
copies detected (dedupe).

### 3.10 Infra — **KEEP**
`Dockerfile`, `docker-compose.deploy.yml`, `kubernetes.yaml`, `terraform_main.tf`, `nginx.conf`,
`requirements.txt` / `requirements-prod.txt`, `.github_workflows_ci.yml`.

### 3.11 **IGNORE (never commit)**
`node_modules/`, `__pycache__/`, the 4 `RK 121MXML eco system session.*` exports (443 MB),
`data/objects/*.archive` (regenerable), any file containing secrets, and `ssh info 121xq.txt`
(contains server key context — must NOT go to a repo).

## 4. Conflicts / risks flagged

1. **Brand drift:** live site = "121XML"; current canon = "121XQ". Decide the public brand before deploy.
2. **13 competing deployment docs** with contradictory "COMPLETE" claims — none reflect that
   `121xq.com` is unpointed. Treat all as drafts until the single canonical `DEPLOYMENT.md` is written.
3. **Secret hygiene:** `ssh info 121xq.txt`, `outputs/SSH_DEPLOYMENT_GUIDE.md`, and any hardcoded creds
   in `deploy_*.ps1`/`.sh` must be excluded and moved to env/secret storage before any push.
4. **Unverified code:** 31 `.py` + native apps claim "production" but have not been run here.
5. **Duplicate artifacts:** identical decks; `index.html`==`121xml_complete_platform.html`; multiple
   near-identical website_*.html — choose one canonical each.

## 5. Recommended canonical layout to carry into Phase 1 (repo skeleton)

```
121xq/ (or 121xml-aios)
├── docs/spec/       <- 3.1 standard + core spec (MASTER_SPEC as primary)
├── docs/brand/      <- 3.2 121XQ set
├── docs/architecture/ <- 3.4
├── docs/integrations/ <- 3.5 per-engine blueprints
├── docs/business/   <- 3.9 newest only
├── DEPLOYMENT.md    <- 3.3 single merged canonical
├── core/            <- 3.6 python engine + tests
├── native/          <- 3.6 native apps
├── web/             <- 3.7 chosen canonical site
├── objectmap/        <- 3.7 graph component seed
├── infra/           <- 3.10
├── archive/         <- everything ARCHIVE above (kept, not primary)
└── .gitignore       <- 3.11
```

## 6. Open decisions before Phase 1

1. **Public brand:** `121XQ` everywhere, or keep `121XML` for the standard + `121XQ` for the OS?
2. **Repo name:** `121xq` (platform) + separate `121xml` (standard) + `121-objectmap`, or single
   monorepo `121xml-aios` (per the GitHub strategy doc)?
3. **Canonical site build:** confirm `website_v3_complete.html` as the base (vs. current live `index.html`).
4. Plus the 3 external gates from the orchestration plan: **121 org**, **gh auth bootstrap**, **real HostArmada SSH host/key**.

---
*End of Phase 0. Read-only. Awaiting your review + the §6 decisions before any Phase 1 build.*
