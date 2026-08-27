# 121AI Project Status — Save Point
*2026-07-31 · for resuming later*

## Where things stand

**Foundation review complete.** `121AI_Foundation_Synthesis.md` consolidates the original five 121XML docs and maps them against the ecosystem vision (universal object standard, dropdown/relationship-map UI, any input/output agent).

**Full project reviewed by date stamp.** The complete `F:\AI\Claude\Projects\121XML` folder has been read end-to-end: canonical Architecture Guide v2, the Program State instance document, all diagrams, and the Business collateral. Two things need your attention there (not yet resolved):

1. **Two conflicting profile URI schemes** are in active use — `urn:121xml:contact/1.1` (Architecture Guide) vs. `https://spec.121.us/121xml/1.1` (Program State, Technical Reference). Pick one before more connector code gets written.
2. **The three newest pitch decks** (`121XML-Executive-Summary.pptx`, `121XML-Project-Overview.pptx`, `121XML-Technical-Architecture-Guide.pptx`, all dated 2026-07-27) reintroduce claims your own Claim Register banned two days earlier — unsourced "$500B+ waste" figures, hardware/native-processor claims, unsourced performance numbers. Flagged, not yet redlined. Say the word if you want the same redline treatment the Diligence Review gave the source doc.

**MVP architecture drafted** (`121AI_MVP_Architecture.md`, v2): scoped to one object type (Contact, reusing your 879→341 dedup proof point) and a relationship-graph UI, mapped onto the canonical 5-layer architecture rather than a new one. Stack: Python serializer, SQLite, FastAPI, Electron + React, `react-force-graph`. Three decisions still explicitly open — see the doc's closing section.

**Research deliverables built:**
- `Agentic_Tech_Objects_Table.xlsx` — sourced comparison of 21 agentic-tech objects (agent, memory, MCP, A2A, etc.)
- `121XML_Comparison_Table.csv` — .121xml vs. MCP vs. ONNX vs. Mem0 vs. GGUF, with connector-building notes for each

**Folder-tree demo built and working end-to-end:**
- `FDrive_Folder_Structure.121xml` — your `F:\AI\CLAUDE\PROJECTS` tree (4,730 dirs, 38,703 files) converted to conformant 121XML, round-trip verified byte-for-byte
- `FDrive_Folder_Mindmap_3D.html` — interactive 3D viewer (drag to relink, branch coloring, 45°-step rotation per axis, whole-tree or per-subtree). Zero external dependencies.
- `start-server.bat` — required to enable the real filesystem "Commit changes" button (browsers block that API on a plain double-clicked file; needs `http://localhost`). Everything else in the viewer works without it.
- **Not yet browser-tested** — validated statically only (syntax, structure, embedded data). Report back anything that misbehaves.

## Next likely steps (pick up here)

1. Decide the profile URI convention and ratify "first vertical" (Contact federation, assumed but not confirmed) — both block further connector/profile work.
2. Locate and audit the six components the Program State claims are already "working" (AST compiler, JSON proxy, hash envelope, 3D relationship workspace, contact importer, test suite) — the MVP may be mostly integration if they're real.
3. Decide whether to redline the three newest pitch decks against the Claim Register.
4. Open `FDrive_Folder_Mindmap_3D.html` in a real browser and report bugs.
