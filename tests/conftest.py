# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The collection anchor for `tests/`, holding no logic on purpose.

⚑⚑ ITS EMPTINESS IS THE FINDING, NOT AN OVERSIGHT.  A `conftest.py` was written under
Ⓝ73″ ⟡the-tests-seam to replace `tests/__init__.py`'s `sys.path` insert, on the
expectation that the reach would move here.  It did not: `[tool.pytest.ini_options]
pythonpath` in `pyproject.toml` supplies `scratch/` and `scripts/` DECLARATIVELY, and a
declaration a reader can check is strictly better than a fixture that computes the same
answer at import time.  Reproducing the reach here would have re-minted the retired
mechanism inside its own replacement.

⚑ WHAT IT STILL DOES.  Its presence marks `tests/` as a conftest directory, which is what
gives every suite below it a common collection root regardless of the cwd pytest is
invoked from — the CWD-INDEPENDENCE property the retired `__init__.py` argued for and
implemented the wrong way.  It is also the honest home for any future fixture that is
genuinely shared across these suites; today none is, and inventing one to justify the
file would be the theatre this tree names elsewhere.

⚑ NO PATH CODE MAY BE ADDED HERE.  A `sys.path` mutation in a conftest is the same
unchecked import as one in an `__init__.py`, wearing pytest's uniform.  If a suite needs
a directory on the path, it goes in `pythonpath` in `pyproject.toml`, where the gate and
the reader can both see it.
"""

from __future__ import annotations
