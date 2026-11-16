# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.path_binding` — the one-hop resolver for a path-holding name.

⚑ EVERY CASE IS A REAL SPELLING FROM THE TREE, not an invented one. The census that
motivated this module found 111 `HERE` bindings and 157 unattributable inserts, so the
shapes below are transcribed from the files that produced those counts. An invented
fixture would pin the resolver to a spelling nobody writes, which is the defect this
module exists to fix one layer up.

⚑⚑ AND THE REFUSALS ARE ASSERTED AS FIRMLY AS THE RESOLUTIONS. A resolver that guesses
produces a well-formed wrong attribution, which reads as a measurement and is worse than
the admitted gap it replaces. The cases where `resolve_arg` MUST return None are the
load-bearing half of this suite, not its edge cases.
"""

from __future__ import annotations

import ast

from substrate import path_binding

OWN_DIR = 1
PARENT_DIR = 2


def _first_call(src: str) -> ast.Call:
    """Return the call expression a one-line fixture holds."""
    stmt = ast.parse(src).body[0]
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        msg = f"fixture is not a call expression: {src!r}"
        raise TypeError(msg)
    return stmt.value


def _arg_of(src: str) -> ast.expr:
    """Return the path argument of a `sys.path.insert(0, X)` fixture."""
    return _first_call(src).args[1]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the dominant spelling: HERE = dirname(abspath(__file__)) ──────────────
    here = ast.parse("import os\nHERE = os.path.dirname(os.path.abspath(__file__))\n")
    derived = path_binding.file_derived_names(here)
    check("HERE is recognised as file-derived", passed="HERE" in derived)
    check("HERE has depth 1 (the file's own directory)", passed=derived.get("HERE") == OWN_DIR)

    # ── the parent walk: ROOT = dirname(dirname(abspath(__file__))) ───────────
    root = ast.parse(
        "import os\nROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n",
    )
    check(
        "a doubled dirname reads as the parent, not the file's own directory",
        passed=path_binding.file_derived_names(root).get("ROOT") == PARENT_DIR,
    )

    # ── the pathlib spelling ─────────────────────────────────────────────────
    plib = ast.parse("from pathlib import Path\nHERE = Path(__file__).parent\n")
    check(
        "Path(__file__).parent is recognised",
        passed=path_binding.file_derived_names(plib).get("HERE") == OWN_DIR,
    )

    # ── an alias carries its source's depth ──────────────────────────────────
    alias = ast.parse(
        "import os\nHERE = os.path.dirname(os.path.abspath(__file__))\nBASE = HERE\n",
    )
    check(
        "an alias inherits the depth it was bound from",
        passed=path_binding.file_derived_names(alias).get("BASE") == OWN_DIR,
    )

    # ── resolving the ARGUMENT of an insert ──────────────────────────────────
    check(
        "a bare name argument resolves through the binding",
        passed=path_binding.resolve_arg(_arg_of("sys.path.insert(0, HERE)"), {"HERE": OWN_DIR})
        == OWN_DIR,
    )

    check(
        "join(HERE, '..') raises the depth rather than reading as HERE",
        passed=path_binding.resolve_arg(
            _arg_of('sys.path.insert(0, os.path.join(HERE, ".."))'), {"HERE": OWN_DIR}
        )
        == PARENT_DIR,
    )

    check(
        "the inline idiom still resolves with no binding at all",
        passed=path_binding.resolve_arg(
            _arg_of("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))"), {}
        )
        == OWN_DIR,
    )

    # ── THE REFUSALS: what must NOT be attributed ────────────────────────────
    check(
        "an unbound name is NOT attributed",
        passed=path_binding.resolve_arg(_arg_of("sys.path.insert(0, SOMEWHERE)"), {"HERE": OWN_DIR})
        is None,
    )

    # ⚑ A name bound inside a function is not a module-level fact. Attributing it
    # would let whichever branch parsed last decide the answer.
    scoped = ast.parse(
        "import os\ndef f():\n    HERE = os.path.dirname(os.path.abspath(__file__))\n",
    )
    check(
        "a function-scoped binding is NOT collected",
        passed="HERE" not in path_binding.file_derived_names(scoped),
    )

    # ⚑ A path from the environment is a runtime value; no static depth exists.
    env = ast.parse("import os\nHERE = os.environ['SOME_ROOT']\n")
    check(
        "a name bound from the environment is NOT file-derived",
        passed="HERE" not in path_binding.file_derived_names(env),
    )

    check(
        "a bare literal is left to the caller's own resolver",
        passed=path_binding.resolve_arg(_arg_of('sys.path.insert(0, "scratch")'), {}) is None,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
