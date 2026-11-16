---
name: project-retrospective-as-navigation-aid
description: "decomposition/cotype_retrospective.md and the SQLite behind it are a deliberate onboarding aid for the assistant; treat them as the primary entry point into the substrate project, not a side artifact."
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

The substrate project is documented in `cotype-free-self-extending-grammar.md` (8158 lines, 534 KB). The `decomposition/` folder pipeline (`build_cotype_db.py` → `cotype_decomposition.sqlite` → `interpret_cotype_retrospective.py` → `cotype_retrospective.md`) was built by the user specifically to optimize the assistant's ability to familiarize itself with that dense source.

**Why:** The markdown is too dense to read end-to-end productively; the retrospective collapses it into 65 line-anchored moves (M1–M41 with versioned variants) with axis-signatures, focus text, and probe-state anchors. The user invested in this scaffolding because it pays for itself every session.

**How to apply:**
- When starting a substrate-related task, read `decomposition/cotype_retrospective.md` first to orient on the move timeline before opening the source markdown.
- The retrospective narrates design history that landed as the `.py` files at repo root — not a standalone literary artifact. Late moves map to specific code: M34 (S₄/A₄ chirality) → `s4_structure.py`; M41 v22.0 / v21.1 (AddressedOp + `verify_every_receipt_carries_structural_address`) → `applied_grammar.py` + `verify_applied_grammar.py`.
- Use the SQLite directly for targeted queries: `sections` for the spine, `triples` for line-anchored facts, `retrospective_moves` for chronology, `retrospective_axis_transitions` for dynamics. Schema documented in `decomposition/README.md`.
- Every move row carries `start_line`/`end_line` into the source markdown — jump there rather than scanning.
- See [[project-mcp-decomposition-deferred]] for the planned interface over this database.
