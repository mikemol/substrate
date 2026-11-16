---
name: reference_python_venv
description: "The repo's Python env is a uv-managed .venv at the substrate root, active by default (VIRTUAL_ENV set); deps tracked in requirements.txt. Has numpy/scipy/sympy/matplotlib/pyvista/cupy-cuda13x/networkx/textual. Don't lose track of it."
metadata: 
  node_type: memory
  type: reference
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The substrate has a **uv-managed virtualenv at `/home/mikemol/github/substrate/.venv`**,
active by default in this environment (`VIRTUAL_ENV` set; `python3` resolves into it). It
kept getting lost track of because it had no manifest — now it does.

- **Manifest:** `requirements.txt` at the repo root (committed) — the exact `uv pip freeze`
  lock. Recreate the env with `uv venv && uv pip install -r requirements.txt`. Add a dep
  with `uv pip install <pkg>` then re-freeze (`uv pip freeze > requirements.txt`).
- **`.venv/` is gitignored** (binary, ~GB, machine-specific) — never commit it; the
  manifest is the tracked record.
- **Installed (top-level uses):** numpy, scipy, sympy, mpmath, matplotlib, pyvista,
  networkx, textual, rich, cyclopts. The geometry/decal work uses matplotlib+pyvista
  ([[discipline/feedback_2d_first_then_conform]]); el-atlas's depsort + tests are
  **sympy-native** (now runs in-env).
- **cupy is `cupy-cuda13x==14.0.1`** (CUDA-13-specific) — pin THAT, never the generic
  `cupy`; re-resolving it (a blanket `uv sync`/`uv add cupy`) would install the wrong
  build. This is why the env is managed via frozen requirements, not a re-resolving lock.
- Scripts (`scripts/*.py`, the el-atlas `tools/*.py`) run under this `python3`. The "Just
  Enough Agda" term-algebra → sympy(+cupy) evaluator work lives here.
