---
name: project_scratch_independence_gate
description: "Pre-commit gate Λ8 (scratch-independence): a PROMOTED project (jea/, agda/, scripts/) must not reference scratch/ at runtime in LIVE code. Comments and .md ledgers are exempt; a default arg value / path string is not. Repoint to a real home or make the caller supply it."
metadata:
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Hit 2026-07-11 committing `jea/metalanguage/synth_agda_prototype.py` (the ⟡pipeline-driver). The
pre-commit hook runs **scratch-independence (Λ8)**: it FAILS a commit if a file under a *promoted*
project (`jea/`, and by the same rule `agda/`/`scripts/`) has a LIVE `scratch/...` path reference. My
tool had `--out` default to `scratch/generated/PermGapPrototype.agda` — a live default-arg value on
line 251 — and the commit aborted (script exit 0, but HEAD did NOT move —
[[feedback_verify_commit_landed_not_exit_code]] caught it).

**Why:** a promoted project must be self-contained; `scratch/` is ungoverned working space, so a
promoted tool that reads/writes a fixed scratch/ path at runtime creates a hidden dependency on
throwaway state. The gate distinguishes LIVE code (a string the program actually uses — arg defaults,
path constants, `open(...)`) from EXEMPT prose (comments, docstrings, `.md` ledgers). The error message
is explicit: *"repoint the path to the artifact's real home, or — if this is a dated HISTORICAL note —
move it into a comment or a .md ledger."*

**How to apply:** when adding a tool/script under a promoted dir, do NOT bake a `scratch/` path into
live code. For an output path the tool WRITES: make `--out` required (caller chooses, e.g. a temp dir),
or default to a real artifacts home under the project — never `scratch/`. Docstring usage examples may
mention any path (exempt), but keep them off `scratch/` for cleanliness. This is one facet of the
open ⟡G-scratch governance thread. Grep the gate: `scripts/*precommit*` / the `scratch-independence`
check. Sibling of [[feedback_verify_commit_landed_not_exit_code]] (how I noticed the abort).
