# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `tenant_pragma` — the admitted tenants, and the reader they are bound into.

⚑⚑ THE LOAD-BEARING CASE IS THE DIFFERENTIAL AGAINST THE STORE. `ADMITTED` repeats
`store.TENANT_FLAGS` so clean modules need not import an untyped one; a repetition nobody checks
is two authorities, so this suite reads the store's tuple and asserts the two agree.

⚑ READ BY PARSING, NOT IMPORTING. Importing `jea.metalanguage.store` here drags its untyped body
through this file's type check (278 findings, measured) — the same reason `ADMITTED` is repeated
at all. The assignment is a literal, so `ast` reads it without executing the module.

The tree is the working directory, resolved at this CLI entry.
"""

from __future__ import annotations

import ast
import sys
import tempfile
from pathlib import Path

from substrate import tenant_pragma

# The store authority, relative to the tree.
_STORE = ("jea", "metalanguage", "store.py")

# The exit a refused invocation returns.
_USAGE_EXIT = 2


def store_tenants(root: Path) -> tuple[str, ...] | None:
    """Return the store's `TENANT_FLAGS` without `--`, or None when it declares no literal tuple."""
    tree = ast.parse(root.joinpath(*_STORE).read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "TENANT_FLAGS" for t in node.targets):
            continue
        value: object = ast.literal_eval(node.value)
        if isinstance(value, tuple):
            return tuple(str(f).removeprefix("--") for f in value)
    return None


def _reader_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the cases for the bound reader, over suites written under `tmp`."""
    live = tmp / "live.py"
    live.write_text("# selftest-tenant: live\n", encoding="utf-8")
    typo = tmp / "typo.py"
    typo.write_text("# selftest-tenant: sandbx\n", encoding="utf-8")
    none = tmp / "none.py"
    none.write_text("x = 1\n", encoding="utf-8")
    return [
        ("an admitted tenant reads as its flag", tenant_pragma.tenant(str(live)) == "--live"),
        ("a misspelled tenant reads as undeclared", tenant_pragma.tenant(str(typo)) is None),
        ("no pragma reads as undeclared", tenant_pragma.tenant(str(none)) is None),
    ]


def main(argv: list[str]) -> int:
    """Run every case; exit 1 if any failed. Refuses any argument but `--selftest`."""
    if argv[1:] not in ([], ["--selftest"]):
        sys.stderr.write("tenant_pragma_selftest: takes no argument but --selftest\n")
        return _USAGE_EXIT
    with tempfile.TemporaryDirectory() as tmp:
        cases = _reader_cases(Path(tmp))
    held = store_tenants(Path.cwd())
    cases.append(
        (
            "ADMITTED agrees with store.TENANT_FLAGS",
            held is not None and set(held) == set(tenant_pragma.ADMITTED),
        )
    )
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"tenant-pragma selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE: its predicate needs an entry point AND
# the `--selftest` literal, and a suite without it is written, green, and run by nothing.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
