# 121XML Folder Consolidation — 2026-07-27

Cleanup performed on this project folder to remove duplicates and separate concerns, based on
review of `121xml Package 2026-07-25.zip` (the most current package) plus loose files that had
accumulated in the folder.

## Structure after cleanup

- **Root** — the standard itself, current version only:
  - `121XML_Architecture_Guide_v2.md` (canonical architecture/implementation guide, v1.1)
  - `121XML_Technical_Reference.txt` (quick-reference card: type system, axioms A1–A3, rules
    R4–R7, conformance levels L0–L3 — distinct content from the guide, kept as-is)
  - `121XML_Program_State.121xml` (living program-state instance document; also serves as a
    real example of the format)
  - `diagrams/` — the four current SVG architecture diagrams
- **Business/** — investor and commercial collateral (not the spec itself): 8 pptx decks, 4 docx
  documents, and `121XML Discussion on Monetizing.docx`/`.pdf` (the working document where most of
  the commercial strategy and hardware vision originated)
- **Archive/** — superseded/historical material, kept for provenance:
  - `121_XML Model.docx` and `121_XML Model - additional ref.docx` — early drafts, flagged in
    `121XML_Program_State.121xml` review history as "thesis only... 95% third-party filler,"
    status: superseded
  - `121XML_Architecture_Guide.html` and `121XML_Architecture_Explanation.txt` — earlier drafts
    of what became `121XML_Architecture_Guide_v2.md`
  - `121XML-open source equivelant of Obsidian relationship model.pdf` — exploratory reference
    material for the 3D relationship-visualizer concept, not core spec
  - `Source-Zips/` — the three original package zips, kept as a backup snapshot of pre-cleanup
    state

## Removed

- Duplicate extracted folder `121XMIL Package/` (fully superseded — same 7 files now live in
  `Business/`, current versions)
- Stray Word lock file `~$1_XML Model - additional ref.docx`

## Moved out of this project entirely

- **SystemClean toolkit** — a full set of PowerShell scripts for Windows user-profile
  consolidation (`RK-*.ps1`, `SystemClean-README.md`, `SYSTEMCLEAN-FILE-ORGANIZATION.txt`) had
  been bundled into the 121xml zip by mistake. Moved to `F:\AI\Claude\Projects\SystemClean\`
  (its own stated location per its README), fully separate from 121XML.
- **121XMLSilicon** — the hardware/silicon vision (native chip-level 121XML execution, FPGA
  prototyping, silicon IP licensing) was interwoven into the software seed narrative. Per open
  issue #4 in the program state ("Silicon funded inside seed... move to Series B vision line"),
  this has been split into its own project: `F:\AI\Claude\Projects\121XMLSilicon\`, seeded with a
  concept README extracted from the relevant passages in
  `Business\121XML Discussion on Monetizing.docx`. The source document itself was left intact in
  `Business/` for full context.
