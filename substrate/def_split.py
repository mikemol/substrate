# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which parts of one oversized function could become their own definitions.

⚑⚑⚑ "THIS FILE DOES TOO MUCH" HAS A SHARPER FORM ONE LEVEL DOWN: this DEF does too much. A
2,173-line dispatch is not a file needing lint repair — it is one function that should be many,
and its finding count is a consequence rather than the problem. Reading it as lint debt
schedules ten thousand fixes; reading it as a decomposition schedules a handful of extractions.

⚑⚑ THE UNIT IS A TOP-LEVEL BRANCH OF THE BODY, because a CLI dispatch is a chain of
`if <mode>:` arms and each arm is one job. An arm that reads only the function's arguments and
module-level names is liftable as-is; one that reads a local bound by an earlier arm is not,
until that local becomes a parameter. That distinction IS the blocker list.

⚑ AND THE BLOCKER IS SHARED LOCAL STATE, NOT SIZE. An arm's length says nothing about whether
it can move — a fifty-line arm reading nothing but its inputs lifts cleanly, while a three-line
arm reading a local computed two hundred lines earlier drags that computation with it. Ranking
by length would send an operator at the wrong arm first.

⚑⚑ AND THIS READER PRINTS WHAT IT CANNOT SEE. A peer's discipline, adopted after their audit
found four binding forms this missed: *if the qualifier is checkable, put it in the OUTPUT, not
a sentence* — because a hedge in prose does not survive a summary while a bound in the output
does. `BLIND_TO` and `OVER_REPORTS` are measured against fixtures, not assumed, and `render`
emits them beside every result.

⚑ THIS REPORTS WHAT IS LIFTABLE, NOT WHAT SHOULD BE LIFTED. Which arms belong together is a
judgement about coherence; which ones CAN move without carrying state is a fact, and the fact
is what nobody currently has.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

#: Binding forms this reader cannot resolve — each verified to slip past the binder.
#: ⚑⚑⚑ A FORM LISTED HERE THAT THE READER ACTUALLY CATCHES WOULD BE A FALSE CAVEAT, which is
#: its own dishonesty: it makes the tool look more careful than it is while hiding that the
#: real gap lies elsewhere. These were measured against fixtures, not reasoned about.
BLIND_TO = (
    "a name bound through globals() or setattr",
    "a name bound by exec",
    "a name arriving via `from x import *`",
    "a name declared nonlocal in a nested def",
)

#: ⚑ AND ONE KNOWN OVER-REPORT, stated rather than quietly carried. `del x` unbinds the name,
#: so a later read is a NameError and not a dependency — this reader still calls it shared
#: state. Over-reporting BLOCKS an extraction rather than licensing a broken one, which is the
#: safe direction, so it is disclosed instead of fixed.
OVER_REPORTS = ("a name that was `del`eted before the later read",)


@dataclass(frozen=True, slots=True)
class Arm:
    """One top-level branch of a function body, and what it depends on."""

    index: int
    kind: str
    line: int
    lines: int
    reads_locals: tuple[str, ...]

    @property
    def is_liftable(self) -> bool:
        """Whether this arm can move out without carrying local state.

        ⚑ READING NOTHING LOCAL IS THE WHOLE TEST. An arm that touches only parameters and
        module-level names is a function already, spelled as a branch.
        """
        return not self.reads_locals


def _stored(node: ast.AST) -> set[str]:
    """Return the names a target expression binds."""
    return {
        n.id for n in ast.walk(node) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
    }


def _assignment_targets(stmt: ast.stmt) -> set[str]:
    """Return names bound by an assignment statement, if this is one."""
    if isinstance(stmt, ast.Assign):
        return {n for t in stmt.targets for n in _stored(t)}
    if isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
        return _stored(stmt.target)
    return set()


def _statement_bound(node: ast.AST) -> set[str]:
    """Return names bound by a statement form that outlives its own block.

    ⚑⚑⚑ PYTHON HAS NO BLOCK SCOPE, and every form here was MISSED on first measurement — a
    peer audit's checklist of binding forms a scanner must not misread is what surfaced them.
    A `for` target, a `with … as` and a walrus all outlive their statement, so a later arm can
    read them. Reporting those arms as liftable licenses an extraction that BREAKS, which is
    the dangerous direction: the over-report it replaced merely wasted a look.

    ⚑ `except … as` IS THE ODD ONE — Python DELETES the name at handler exit, so a later read
    is a NameError. It is bound anyway, because an arm reading it is broken code this reader
    should surface rather than bless as liftable.
    """
    if isinstance(node, ast.NamedExpr) and isinstance(node.target, ast.Name):
        return {node.target.id}
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return _stored(node.target)
    if isinstance(node, ast.withitem) and node.optional_vars is not None:
        return _stored(node.optional_vars)
    if isinstance(node, ast.ExceptHandler) and node.name:
        return {node.name}
    return set()


def _pattern_bound(node: ast.AST) -> set[str]:
    """Return names bound by a `match` pattern capture.

    ⚑ SEPARATED FROM THE STATEMENT FORMS BECAUSE `PLR0911` FIRED, and it was right for the
    reason it is always right in this repo: two families of thing in one function. A pattern
    capture escapes its `case` exactly as a `for` target escapes its loop.
    """
    if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
        return {node.name}
    if isinstance(node, ast.MatchMapping) and node.rest:
        return {node.rest}
    return set()


def _declared(node: ast.AST) -> set[str]:
    """Return names this node declares — a definition or a function-scoped import.

    ⚑ A FUNCTION-SCOPED IMPORT BINDS, and the population this was written for is full of
    them: the dispatch reaches its siblings by bare `import` inside the body. Missing these
    would call an arm liftable while it depends on a module another arm imported.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return {a.asname or a.name.split(".")[0] for a in node.names if a.name != "*"}
    return set()


def _bound_at_top(stmt: ast.stmt) -> set[str]:
    """Return the names this statement binds into the enclosing function's scope.

    ⚑ ONLY WHAT ESCAPES THE STATEMENT. A first cut walked each prior statement entirely and
    counted every nested binding, so on a 70-arm dispatch it reported 78 shared locals gating
    64 arms — when the arms are independent `if` blocks that merely reuse short names. The
    three families below are what genuinely reaches a later arm.
    """
    names = _assignment_targets(stmt)
    for node in ast.walk(stmt):
        names |= _statement_bound(node)
        names |= _pattern_bound(node)
        names |= _declared(node)
    return names


def _assigned_before(body: list[ast.stmt], upto: int) -> set[str]:
    """Return the local names bound by statements before index `upto`."""
    names: set[str] = set()
    for stmt in body[:upto]:
        names |= _bound_at_top(stmt)
    return names


def _reads(stmt: ast.stmt) -> set[str]:
    """Return every name this statement loads."""
    return {n.id for n in ast.walk(stmt) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def arms(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Arm]:
    """Return the top-level statements of `func`, each with the locals it reads.

    ⚑ EVERY TOP-LEVEL STATEMENT IS AN ARM, not only the `if`s. A dispatch interleaves setup
    with branches, and the setup is exactly what the branches depend on — reporting only the
    branches would hide the state that blocks them.
    """
    params = {a.arg for a in func.args.args} | {a.arg for a in func.args.kwonlyargs}
    out: list[Arm] = []
    for i, stmt in enumerate(func.body):
        prior = _assigned_before(func.body, i) - params
        reads = _reads(stmt) & prior
        # ⚑ `end_lineno` IS DECLARED ON `ast.stmt` AND STILL OPTIONAL. Reaching it through
        # `getattr` would leak `Any` into the length; the `or` covers None without a dynamic
        # lookup.
        end = stmt.end_lineno or stmt.lineno
        out.append(
            Arm(
                index=i,
                kind=type(stmt).__name__,
                line=stmt.lineno,
                lines=end - stmt.lineno + 1,
                reads_locals=tuple(sorted(reads)),
            )
        )
    return out


def find(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    """Return the named top-level function, or None."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def blockers(found: list[Arm]) -> dict[str, int]:
    """Return each shared local and how many arms it blocks.

    ⚑⚑ THIS IS THE ACTIONABLE READING. A local read by many arms is one extraction that
    frees all of them — turning it into a parameter, or computing it in the callee. Ranking
    the locals rather than the arms is what converts a wall of branches into a short list of
    decisions.
    """
    counts: dict[str, int] = {}
    for arm in found:
        for name in arm.reads_locals:
            counts[name] = counts.get(name, 0) + 1
    return counts


def bounds() -> str:
    """Render what this reader cannot see, for printing beside any result."""
    out = ["  ⚑ THIS READER IS BLIND TO:"]
    out.extend(f"      {b}" for b in BLIND_TO)
    out.append("  ⚑ AND OVER-REPORTS:")
    out.extend(f"      {o}" for o in OVER_REPORTS)
    out.append("      (over-reporting blocks an extraction; it never licenses a broken one)")
    return "\n".join(out)


def render(found: list[Arm], show: int = 12) -> str:
    """Render the liftable arms, the locals blocking the rest, and this reader's bounds."""
    liftable = [a for a in found if a.is_liftable]
    stuck = [a for a in found if not a.is_liftable]
    total = sum(a.lines for a in found)
    out = [
        f"{len(found)} top-level statement(s), {total} line(s)",
        f"  liftable as-is: {len(liftable)}",
        f"  blocked by local state: {len(stuck)}",
        "",
    ]

    counts = blockers(found)
    out.append("locals blocking the most arms:")
    ranked = sorted((-n, name) for name, n in counts.items())
    out.extend(f"  {-neg:>4} arm(s) read  {name}" for neg, name in ranked[:show])
    if not ranked:
        out.append("  (none — every arm is liftable)")
    # ⚑ THE PLANNING CONSEQUENCE. One local turned into a parameter frees every arm reading
    # it, so the decision count is the number of LOCALS, not the number of arms.
    out.append(
        f"\n  ⚑ {len(counts)} shared local(s) gate {len(stuck)} arm(s) — the "
        f"decisions are the locals, not the arms."
    )
    # ⚑⚑ THE BOUND TRAVELS WITH THE ANSWER. A reader who takes the counts above and drops
    # this block has dropped the only statement of what those counts could be missing.
    out.append("")
    out.append(bounds())
    return "\n".join(out) + "\n"
