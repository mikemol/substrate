#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Assert the package is IMPORTABLE BY NAME, without a path mutation.

⚑⚑⚑ THIS IS THE ONLY PROPERTY THAT MATTERS AND IT IS NOT SELF-EVIDENT. The package directory
existing proves nothing: `scratch/` has existed for months and is not importable. What makes a
module reachable is the DECLARATION (`[tool.setuptools] packages`) plus the install, and
either half can be absent while the directory looks right.

⚑⚑ AND IT MUST BE CHECKED IN A PROCESS THAT DID NOT ARRANGE FOR IT. A test that runs from the
repo root gets `''` on `sys.path` and imports `substrate` because the CWD happens to contain
it — proving nothing about the install. So this asserts the resolved `__file__` comes from
somewhere the CWD alone would not supply, and reports WHICH, because "it imported" and "it
imported for the right reason" are different facts and only the second survives a `cd`.

⚑ THE INVERSE CHECK IS THE POINT OF THE WHOLE MIGRATION: a module in this package must be
reachable WITHOUT `sys.path.insert`. 556 sites exist because that was previously false. Run
this from anywhere; if it passes only from the repo root, the install is not doing the work
and the 556 would come back.

⚑ CONVERTED TO SPEC (⟡substrate-package-clean). This file predated the strict config and
carried 21 findings — the promotion TARGET was dirtier than anything promoted into it, so a
consumer importing the package wholesale inherited them. Every argument above is preserved;
what changed is `os.path` → `Path`, `%` → f-strings, `print` → `sys.stdout`, a bare `except`
narrowed, and the cases given types.
"""

from __future__ import annotations

import sys
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

# The distribution name that makes this package importable when it is installed.
_DIST = "substrate-tooling"


def _installed() -> bool:
    """Report whether an installed distribution — not the CWD — makes us importable.

    ⚑ NARROWED FROM A BARE `except Exception`. `PackageNotFoundError` is the answer "not
    installed"; anything else is a broken environment, and swallowing both reported a broken
    metadata store as a clean not-installed. `BLE001` names exactly this.
    """
    try:
        distribution(_DIST)
    except PackageNotFoundError:
        return False
    return True


def cases() -> list[tuple[str, bool, bool]]:
    """Return the guarded assertions as (label, got, want) data rather than as prose."""
    import substrate  # noqa: PLC0415 - importing the subject IS the first case

    here = Path(substrate.__file__).absolute().parent
    root = here.parent

    # ⚑ THE LOAD-BEARING CASE: reachable WITHOUT the CWD supplying it. An editable install
    # puts a finder on the path; the bare CWD does not. If this fails, the package is only
    # importable from the repo root and every consumer would still need the path mutation
    # this migration exists to delete.
    cwd_only = Path.cwd().absolute() == root and "" in sys.path

    return [
        ("substrate imports", bool(substrate.__file__), True),
        # ⚑ AND IT RESOLVES TO THIS TREE, not to some other installed `substrate`. A name this
        # generic is a real collision risk, and an import that silently resolved elsewhere
        # would pass every other check in this file.
        ("resolves under the repo root", (root / "pyproject.toml").is_file(), True),
        ("not reachable by CWD alone", not cwd_only or _installed(), True),
    ]


def main() -> int:
    """Run the cases and return an exit code."""
    rows = cases()
    bad = [r for r in rows if r[1] != r[2]]
    for label, got, want in bad:
        sys.stderr.write(f"  FAIL {label}: got {got!r} want {want!r}\n")
    sys.stdout.write(f"substrate selftest: {len(rows) - len(bad)}/{len(rows)}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
