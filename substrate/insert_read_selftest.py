# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.insert_read` — the import-surface reader.

⚑ THE LOAD-BEARING CASE IS THE ONE THE ORIGIN COULD NOT ANSWER. `sys.path.insert(0, HERE)`
carries no literal and no inline `__file__` walk, so a call-node-only resolver reported it
UNKNOWN — 157 of 492 inserts in the live census. If the case below ever reads UNKNOWN
again, the binding resolver has been disconnected and the reader has silently returned to
covering two thirds of its subject.

⚑⚑ AND THE LITERAL CASES ARE PINNED BESIDE IT FOR THE OPPOSITE REASON. Adding a resolver
must not CHANGE an answer that was already definite, so a bare `"scratch"` and a joined
path are asserted to still resolve exactly as before. A change there would mean the new
layer is overriding the old one rather than filling its gap.
"""

from __future__ import annotations

import ast

from substrate import insert_read

_LABEL = "scratch/prose_apex.py"


def _call(src: str) -> ast.Call:
    """Return the call a one-line fixture holds."""
    stmt = ast.parse(src).body[0]
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        msg = f"fixture is not a call expression: {src!r}"
        raise TypeError(msg)
    return stmt.value


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the mutation detector ────────────────────────────────────────────────
    check("insert is a mutation", passed=insert_read.is_mutation(_call('sys.path.insert(0, "x")')))
    check(
        "append is a mutation (same hazard, other end)",
        passed=insert_read.is_mutation(_call('sys.path.append("x")')),
    )
    check(
        "an unrelated insert is NOT a mutation",
        passed=not insert_read.is_mutation(_call('items.insert(0, "x")')),
    )
    check(
        "a sys attribute that is not path is NOT a mutation",
        passed=not insert_read.is_mutation(_call('sys.argv.insert(0, "x")')),
    )

    # ── literal targets must resolve EXACTLY as before the resolver landed ───
    check(
        "a bare literal names its directory",
        passed=insert_read.target_of(_call('sys.path.insert(0, "scratch")'), _LABEL, {})
        == "scratch",
    )
    check(
        "a joined literal names its last segment",
        passed=insert_read.target_of(_call('sys.path.insert(0, "a/b/scripts")'), _LABEL, {})
        == "scripts",
    )

    # ── THE CASE THE ORIGIN COULD NOT ANSWER ─────────────────────────────────
    # `HERE = os.path.dirname(os.path.abspath(__file__))` then `insert(0, HERE)`.
    # The origin saw no literal and no inline __file__ walk, and reported UNKNOWN.
    check(
        "a bound HERE resolves to the file's own directory",
        passed=insert_read.target_of(_call("sys.path.insert(0, HERE)"), _LABEL, {"HERE": 1})
        == "scratch",
    )

    # ⚑ AND THE PARENT WALK MUST NOT COLLAPSE TO THE SAME ANSWER. `ROOT` one level up
    # from `scratch/` is the repo root, not `scratch` — attributing a root insert to
    # `scratch` would move the wrong module in a drain plan.
    check(
        "a bound ROOT resolves to the parent, not the file's own directory",
        passed=insert_read.target_of(_call("sys.path.insert(0, ROOT)"), _LABEL, {"ROOT": 2})
        == insert_read.ROOT_DIR,
    )

    # ⚑ THE `str(ROOT)` WRAPPER IS THE ELIZA-TEST IDIOM, ~36 FILES — half the sites
    # this reader still could not name at the last count. `Path` arithmetic yields a
    # Path, so the insert wraps it in `str()`, and a resolver that walks only for
    # `__file__` sees a call with a bare name inside. The name still carries the depth,
    # so the wrapper must not defeat resolution.
    check(
        "a str(ROOT) wrapper resolves through the wrapped name",
        passed=insert_read.target_of(_call("sys.path.insert(0, str(ROOT))"), _LABEL, {"ROOT": 2})
        == insert_read.ROOT_DIR,
    )

    # ── the refusal survives the new layer ───────────────────────────────────
    check(
        "an unresolvable name is still UNKNOWN",
        passed=insert_read.target_of(_call("sys.path.insert(0, SOMEWHERE)"), _LABEL, {})
        == insert_read.UNKNOWN,
    )

    # ── bare-import reading ──────────────────────────────────────────────────
    tree = ast.parse("import vfs\nimport os.path\nfrom ratchet import x\n")
    names = insert_read.bare_names(tree)
    check("a bare import is collected", passed="vfs" in names)
    check("a dotted import is NOT collected", passed="os.path" not in names)
    check("a bare `from` is collected", passed="ratchet" in names)

    # ⚑ `from scripts import ratchet` names a PACKAGE and needs no insert — the
    # measured defect the origin's docstring records.
    pkg = ast.parse("from scripts import ratchet\n")
    check(
        "a `from` naming a package is NOT drain population",
        passed="scripts" not in insert_read.bare_names(pkg),
    )

    # ── the whole-file reader ────────────────────────────────────────────────
    module = ast.parse(
        "import os\nimport sys\n"
        "HERE = os.path.dirname(os.path.abspath(__file__))\n"
        "sys.path.insert(0, HERE)\n",
    )
    found = insert_read.inserts(module, _LABEL)
    check("the file reader finds the one insert", passed=len(found) == 1)
    check(
        "an unresolved insert reports itself as unresolved",
        passed=not insert_read.Insert("x.py", 1, insert_read.UNKNOWN).resolved,
    )
    check(
        "and resolves it through the module's own binding",
        passed=bool(found) and found[0].target == "scratch",
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
