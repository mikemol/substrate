# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `tests` package marker — and it is now a marker and nothing else.

Run:  `python3 -m pytest` (from the repo root, or anywhere — see below).

⚑⚑ THIS FILE USED TO MUTATE `sys.path`, AND THAT IS WHAT WAS RETIRED UNDER Ⓝ73″
⟡the-tests-seam.  It computed the repo root from its own `__file__` and pushed
`scratch/` and `scripts/` onto `sys.path` at import time, so a bare `import agda_lex`
resolved from any cwd.  The REACH was correct and is still needed — `stubs/agda_lex.pyi`
and `stubs/gen_build_makefiles.pyi` are keyed on the BARE module name, so a
`scratch.agda_lex` spelling bypasses the stub and drags mypy into untyped source.  What
was wrong was the MECHANISM: a runtime path mutation is an import that nothing can
check, resolved against whatever state the process happens to hold, and the operator
refused the shape outright (2026-08-31: *"NOO. No sys.path modification."*).

⚑ THE REPLACEMENT IS A DECLARATION, NOT CODE.  `[tool.pytest.ini_options] pythonpath` in
`pyproject.toml` names `scratch` and `scripts`, and pytest resolves them against the
ROOTDIR — the directory holding the file that declares the config.  So the
CWD-INDEPENDENCE this file's old docstring argued for is preserved exactly, and it is now
a line a reader can check rather than a side effect of an import.

⚑ SO WHY DOES THE FILE SURVIVE AT ALL, RATHER THAN GOING WITH ITS CONTENTS.  `corpus.py`
is reached as `from tests import corpus`, and that spelling is what makes the fixture
module TYPED: without the package, mypy reports `Cannot find implementation or library
stub for module named "corpus"` and every fixture reference becomes an `Any` that
`disallow_any_expr` then refuses.  Deleting the marker would trade a checked import for
an unchecked one — the same trade the `sys.path` insert was making, arrived at from the
other direction.

⚑ `scripts/` and `scratch/` are UNGUARDED by Λ8 (`check_scratch_independence.py`,
`ROOTS = ["jea", "el-atlas"]`), so importing `scratch/agda_lex.py` from here is legal.
`jea/` and `el-atlas/` are NOT — nothing under those roots may import this.
"""

from __future__ import annotations
