# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.insert_scope` — where a `sys.path` mutation sits.

⚑⚑⚑ THE CLASSIFICATION LICENSES A CODEMOD, so a wrong answer is a wrong EDIT. Calling a
function-scoped insert module-level would license deleting a site that runs per call, changing
when an import happens in code nobody re-ran; calling a guarded one plain would delete the
condition along with the mutation. Both directions are pinned.

⚑⚑ AND `FUNCTION` BEATS `GUARDED` WHEN BOTH APPLY. A guarded insert inside a function is
still a per-call site, and a caller deciding what is mechanically drainable must not see it as
merely conditional. That precedence is asserted directly rather than left to argument order.

⚑ THE FIXTURES ARE PARSED SOURCE, NOT REPO FILES. A case reading the tree would be a
measurement — red the next time anyone edits an unrelated tool, and green for reasons that
have nothing to do with the traversal.
"""

from __future__ import annotations

import ast

from substrate import insert_scope

_MODULE_LEVEL = """
import sys
sys.path.insert(0, 'alpha')
"""

_IN_FUNCTION = """
import sys
def go():
    sys.path.insert(0, 'alpha')
"""

_IN_METHOD = """
import sys
class C:
    def go(self):
        sys.path.insert(0, 'alpha')
"""

_GUARDED = """
import sys
if 'alpha' not in sys.path:
    sys.path.insert(0, 'alpha')
"""

_TRY_GUARDED = """
import sys
try:
    import alpha
except ImportError:
    sys.path.insert(0, 'alpha')
"""

_GUARDED_IN_FUNCTION = """
import sys
def go():
    if True:
        sys.path.insert(0, 'alpha')
"""

_NESTED = """
import sys
def outer():
    def inner():
        sys.path.insert(0, 'alpha')
"""


def _one(src: str) -> insert_scope.Site:
    """Parse `src` and return its single mutation site."""
    return insert_scope.sites(ast.parse(src), "fixture.py")[0]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the three scopes ─────────────────────────────────────────────────────
    check(
        "a top-level insert is module scope",
        passed=_one(_MODULE_LEVEL).scope == insert_scope.MODULE,
    )
    check(
        "an insert in a function is function scope",
        passed=_one(_IN_FUNCTION).scope == insert_scope.FUNCTION,
    )
    # ⚑ A METHOD IS A FUNCTION. Without this, every class-bound bootstrap reads as
    # module-level and becomes falsely drainable.
    check(
        "an insert in a method is function scope",
        passed=_one(_IN_METHOD).scope == insert_scope.FUNCTION,
    )
    check("an insert under an `if` is guarded", passed=_one(_GUARDED).scope == insert_scope.GUARDED)
    # ⚑ A `try` FALLBACK CARRIES A CONDITION TOO — it runs only when an import failed.
    check(
        "an insert in an except handler is guarded",
        passed=_one(_TRY_GUARDED).scope == insert_scope.GUARDED,
    )

    # ── precedence: function beats guard ─────────────────────────────────────
    # ⚑ THE TIMING QUESTION DOMINATES THE CONDITION QUESTION.
    check(
        "a guarded insert inside a function is FUNCTION, not guarded",
        passed=_one(_GUARDED_IN_FUNCTION).scope == insert_scope.FUNCTION,
    )

    # ── the enclosing name is the INNERMOST function ────────────────────────
    # ⚑ A NESTED DEF MUST NAME THE INNER ONE, or a reader looking for the site's owner is
    # sent to a function that does not contain it.
    check(
        "a nested def reports the innermost enclosing function",
        passed=_one(_NESTED).enclosing == "inner",
    )
    check(
        "and a module-level site has no enclosing function",
        passed=_one(_MODULE_LEVEL).enclosing == "",
    )

    # ── mechanical is exactly the unguarded module-level case ───────────────
    check("a module-level site is mechanically drainable", passed=_one(_MODULE_LEVEL).is_mechanical)
    # ⚑ THE TWO DIRECTIONS THAT MUST NOT BE DRAINED BY A CODEMOD.
    check("a function-scoped site is NOT", passed=not _one(_IN_FUNCTION).is_mechanical)
    check("and a guarded site is NOT", passed=not _one(_GUARDED).is_mechanical)

    # ── grouping and filtering agree ────────────────────────────────────────
    every = (
        insert_scope.sites(ast.parse(_MODULE_LEVEL), "a.py")
        + insert_scope.sites(ast.parse(_IN_FUNCTION), "b.py")
        + insert_scope.sites(ast.parse(_GUARDED), "c.py")
    )
    grouped = insert_scope.by_scope(every)
    check(
        "grouping partitions every site", passed=sum(len(v) for v in grouped.values()) == len(every)
    )
    check(
        "and the mechanical set is the module group",
        passed=insert_scope.mechanical(every) == grouped[insert_scope.MODULE],
    )

    # ── the target is resolved by the existing authority ────────────────────
    # ⚑ TWO QUESTIONS, ONE AUTHORITY EACH. If this reader re-derived the directory, the two
    # censuses could disagree about the same site.
    check(
        "the site carries the directory the insert names",
        passed=_one(_MODULE_LEVEL).target == "alpha",
    )

    # ── a file with no mutation yields none ─────────────────────────────────
    check(
        "a file that mutates nothing yields no sites",
        passed=insert_scope.sites(ast.parse("import sys\nx = 1\n"), "d.py") == [],
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


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
