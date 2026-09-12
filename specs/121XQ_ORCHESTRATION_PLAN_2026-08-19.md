# 121XML / 121XQ AI OS — GitHub, 121ObjectMap & Deployment Orchestration Plan

**Author:** Claude Code (orchestrator)  ·  **Created:** 2026-08-19
**Status:** ⏸️ AWAITING APPROVAL + decisions (§5). Nothing executed.
**Sources read (verified):** `Knowledge_Base/121_XML_Model.md`, `121XML_AI_OS_FINAL_SPECIFICATIONS.md`,
`121XML_OBJECT_GRAPH_INTEGRATION.md`, plus full file inventory of `…\projects\121XML`.

---

## 1. My understanding of 121XML (proof-of-appreciation)

**The primitive.** Every object — real or virtual — is expressible as **Name–Value pairs**.
Persons, orgs, relationships, atoms, database rows, even other formats (XML/JSON/code)
reduce to this lowest common denominator. This makes 121XML a universal interchange:
"any protocol → any other protocol," and AI can convert anything to anything (e.g. Python→Java, HL7→FHIR).

**Self-describing packets.** The data packet carries its own structure/metadata, so a
receiver decodes it **without any external namespace or pre-shared schema**. Realized via:
- **Profile URI (R6):** `urn:121xml:type/version` — schema discovery built into the packet.
- **Explicit type tags (A2):** every object carries `_type`.

**Determinism, losslessness, immutability.**
- **A1** composition over inheritance · **A2** explicit type tags · **A3** homogeneous sequences
- **R4** alphabetically sorted keys (deterministic bytes) · **R5** explicit null vs absent
- **R6** profile URI · **R7** SHA256 content addressing `data://sha256:HASH:TYPE`
- Claims: 90–96% token compression at **0% loss**, bit-perfect round-trip, tamper-evident.

**Sovereignty / web3 angle.** Local control via private/public-key encryption (AES-256 at rest,
TLS 1.3 in transit); user chooses where data lives; content addressing = immutable audit trail.

**121XQ AI OS** is the product layer sitting **above** all AI engines (Claude/GPT/Gemini/…),
making them fungible. It spans multiple industry systems — **121DevTeam, 121Healthcare,
121FinTech, 121Solutions**, etc. — each reusing the same skills/tools and the same dashboard.

**121ObjectMap** = the standardized relationship-graph UI: any object rendered as nodes (sensible
icons + colors) with tidy labelled relationship lines (aiarcs.app/studio style), each node
clickable for info and **drillable** to the next layer (Folder→subfolder→file; Org→Dept→Role→Person→Attributes→Relationships). A first-generation version already exists as
`121xml_object_graph_visualizer.html`; the task is to **standardize it into one reusable component**.

---

## 2. Verified reality vs. document claims (transparency)

| Item | Documents say | Actually verified (2026-08-19) |
|---|---|---|
| GitHub deployment | Many `DEPLOYMENT_COMPLETE` / `PRODUCTION_DEPLOYMENT_COMPLETE` docs | **`gh` NOT logged in** (`gh auth status` → not logged into any host). Unverifiable as deployed. |
| Git identity | — | Global user = **`Claude DevTeam <devteam@121solutions.com>`**, NOT the stated `rashadkhan4mna@gmail.com` |
| 121xml.com / 121xq.com | "Deploy to 121xml.com" guides exist | Live status **not yet checked** (Phase 0 will verify via browser) |
| Corpus | Single coherent spec | ~200 files with heavy duplication + overlapping/contradictory "final" versions → needs reconciliation |
| 121ObjectMap | "Production ready" HTML | One standalone HTML; not yet a standardized, drill-down, multi-system component |

> Per your directive, **nothing above is reported as done until re-verified.** Existing
> "COMPLETE" docs are treated as *drafts/claims*, not ground truth.

### 2a. Verified deployment facts (2026-08-19, read-only)
- **121xq.com** → **NO DNS A record**: domain not pointed/live yet. Must be configured before deploy.
- **121xml.com** → **104.21.14.186 (Cloudflare)**: proxied via Cloudflare, not a direct HostArmada IP.
  SSH to the proxied domain likely won't reach the shell — need the **real HostArmada host/IP**.
- HostArmada notes say host=`121xml.com` port=`19199` user=`xml` webroot=`/var/www/121xml/`,
  server-side key `id_121xq` (private key lives on the SERVER, per the notes).
- **Local `~/.ssh`** (`C:\Users\Owner\.ssh`) contains `121connect_deploy`, `121connect_deploy_rsa`
  (+ `.pub`), `config.backup`, `known_hosts` — **NOT** `id_121xq`, and **no active `config`**.
  So the deploy key↔host mapping is not wired locally yet.
- **`gh` not authenticated** to any host.

### Decisions locked (from user, 2026-08-19)
- Owner: **a 121 org** (121solutions/121group) — must confirm it exists; I cannot create it.
- Auth/transport: **SSH** (HostArmada for deploy; GitHub SSH for git). GitHub still needs a
  one-time you-driven auth bootstrap for repo/org API operations.
- Scope: **full pipeline to deploy**.
- Verification: **my rigorous self-QA** for now.

### Architecture locked (from user, 2026-08-19, second round)
- **Two projects / two repos / two sites:**
  - `121xml` → **121xml.com** — the standard + reference site/tools.
  - `121xq`  → **121XQ.com** — the AI OS platform.
- **Brand:** both coexist — 121XML = the standard; 121XQ = the OS.
- **121ObjectMap = a standardized shared component that is always the 2nd TAB in every app**
  (both projects now, and future 121DevTeam / 121Healthcare / 121FinTech / 121Solutions).
  Built once to one standard (icon/color nodes, labelled edges, click-for-info, N-layer drill-down
  Folder→file AND Org→Dept→Role→Person→Attributes→Relationships), reused everywhere — NOT its own repo.
- GitHub user: **rashadkhan4mna@gmail.com**; org name TBD. HostArmada SSH via **keys** (KB provided);
  password only as a fallback the USER types (my shell is non-interactive — can't answer ssh pw prompts).
- Repo topology supersedes the old monorepo `121xml-aios` idea in `121XML_GITHUB_STRATEGY.md`.

### Proposed Phase 1 skeleton (per project, 121ObjectMap shared)
```
121xml/                         121xq/
├── web/  (tab1: standard)      ├── web/  (tab1: AI OS)
│   └── objectmap/ (tab2 std)    │   └── objectmap/ (tab2 std)  <- same standardized component
├── docs/spec, brand, arch…     ├── docs/…
├── core/ (engine+tests)        ├── core/ (platform)
├── infra/  DEPLOYMENT.md        ├── infra/  DEPLOYMENT.md
├── archive/  .gitignore         ├── archive/  .gitignore
```
121ObjectMap is developed once in a shared source and vendored into each app's Tab 2 to guarantee
identical behavior across all 121XQ systems.

---

## 3. Blocking constraints I must flag now

1. **GitHub auth is a you-action.** This session is non-interactive; I cannot run
   `gh auth login`'s browser/device flow, and I must never handle your GitHub password/token
   directly. You authenticate; I then operate the authenticated CLI. (Options in §5.)
2. **Account identity must be settled** (gmail vs 121solutions) before any repo is created —
   it determines ownership, org, and commit attribution.
3. **"121ObjectMap skill"** is not an installed Claude skill. I can build it as a reusable,
   standardized web component (evolving your existing visualizer) + a generator — but that is
   *new build*, not invoking an existing skill.
4. **Multi-AI cross-check (Abacus + ChatGPT).** I cannot natively call Abacus/ChatGPT APIs.
   I can (a) do rigorous self-QA, and (b) drive them in the browser **if** you're logged in and
   approve each visit. Fully automated tri-AI verification isn't guaranteed — need your steer.

---

## 4. Proposed phased plan (DevTeam workstreams)

**Phase 0 — Recon & Reconciliation (read-only)**
- Full inventory + dedup map of the 121XML corpus; identify the *single* canonical spec set.
- Verify live status of 121xml.com / 121xq.com (browser).
- Confirm DNS/hosting owner, existing repos (once authed).
- Output: `PHASE0_GROUND_TRUTH.md` + reconciled canonical index. **← review gate**

**Phase 1 — GitHub foundation**
- You authenticate `gh` (§5); set correct git identity.
- Create/confirm repos: `121xml` (standard + libs), `121xq` (AI OS platform), `121-objectmap`
  (dashboard component), optionally per-industry repos. Add `.gitignore` (exclude `node_modules`,
  the 100–230 MB session RTF/PDF exports, secrets), LICENSE, README, CI (`.github/workflows`).
- Commit the reconciled canonical source. **← review gate before first push**

**Phase 2 — 121ObjectMap standardization**
- Extract one reusable component from `121xml_object_graph_visualizer.html`:
  nodes with typed icons+colors, labelled edges, click-for-info, N-layer drill-down
  (Folder→file AND Org→Dept→Role→Person→Attributes→Relationships).
- Standard JSON/121XML graph schema so **every** 121XQ system (DevTeam/Healthcare/FinTech/…)
  renders through the same board. Live "monitor & intervene" control surface.
- QA against real objects: a filesystem tree, and a 121Solutions org model.

**Phase 3 — 121Solutions data ingestion**
- Consume `F:\121Group\SmarterMergers\SMBrochures` (20 solution one-pagers + investor/monetization
  decks) → structured 121XML object model of the 121Solutions brand & product catalogue
  (121 CRM, Analytics, Skills, Pay, Club, Ride, BPO, BizMatch, SmarterMergers, …) for 121ObjectMap.

**Phase 4 — Deployment**
- Deploy standardized site + 121ObjectMap to **121xml.com** and **121xq.com** via the chosen host
  (verify which: the repo has nginx/k8s/terraform/Dockerfiles AND static HTML — Phase 0 decides).
- Update all related material to the reconciled canonical version.

**Phase 5 — Verify / QA / cross-check**
- Functional QA of every deployed surface; link/asset checks; graph drill-down checks.
- Cross-verification pass (self-QA always; Abacus/ChatGPT per §3.4 decision).
- Output: verified status report — only then is anything reported "done."

**Throughout:** standardized real-time dashboard of DevTeam agents (state JSONL → auto-refresh
HTML in the in-app browser), with user monitor/intervene controls. Logs + rollback notes kept.

---

## 5. Decisions I need before executing

1. **GitHub account/owner** — repos under `rashadkhan4mna@gmail.com` personal, or a
   `121solutions`/`121group` org? (This sets identity + ownership.)
2. **How you'll authenticate gh** — (a) you run `gh auth login --web` and complete the device
   code, or (b) you create a fine-grained PAT and load it yourself into the env. I never see the secret.
3. **Repo topology** — monorepo (`121xq` with packages) vs. multi-repo (`121xml`, `121xq`,
   `121-objectmap`, per-industry). Recommend multi-repo for the standard + a platform monorepo.
4. **121ObjectMap** — confirm I should *build* the standardized component from your existing
   visualizer (yes/adjust).
5. **Tri-AI verification** — self-QA only, or also drive Abacus + ChatGPT in the browser
   (needs you logged in + per-visit approval)?
6. **Scope of this pass** — do all phases, or stop after Phase 0+1 (get code safely into GitHub)
   and review before 121ObjectMap/deploy?

---

*No repos created, no auth performed, no files deployed. Awaiting your answers to §5.*

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*