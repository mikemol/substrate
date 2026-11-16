# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census the readers that crash when run from a BORROWING checkout.

⚑⚑⚑ THE DEFECT IS A COMPOSITION, NOT A LINE, WHICH IS WHY A TEXT SEARCH CANNOT FIND IT. Two
correct functions produce it: `corpus.resolve_root` resolves CWD FIRST — deliberately, so a peer
running a symlinked tool gets THEIR tree rather than substrate's — and a labeller then measures the
returned paths against SUBSTRATE's root. From another checkout the walk is right, the label is
wrong, and `relative_to` raises. Neither function is at fault and neither can be fixed alone.

⚑⚑⚑ AND THE FIRST PREDICATE WAS WRONG IN BOTH DIRECTIONS, MEASURED (gate-G252, gate-G255). It
asked whether a ROOT-SHAPED PARAMETER CARRIES A DEFAULT. Executing all thirteen sites it reported
LIVE confirmed six and refuted five — and worse, it could not see `type_census_summary.census`,
which takes NO root parameter at all, reaches `corpus.ROOT` as a module global, and crashes exactly
like the confirmed six. A predicate keyed on a parameter list cannot express a function that never
had a parameter.

⚑⚑ SO THE PREDICATE NOW READS THE ARGUMENT OF THE CALL, WHICH IS WHERE THE DEFECT ACTUALLY LIVES.
The question is not *what does this function accept* but **where does the root it measures against
COME FROM**. Three answers, and they are three different facts:

  GLOBAL    — the label measures against a module-level constant (`corpus.ROOT`) that no caller can
              influence, while the walk follows the caller's cwd. This is the LIVE crash: the two
              roots are independent, so a borrowing checkout makes them disagree.
  DEFAULTED — the root is a parameter defaulting to that same constant. Live when defaulted, and
              the caller can rescue it by passing one.
  RECEIVED  — the root is a parameter with no default, so every caller states its tree. Latent: the
              identical body, protected only by the calling discipline.

⚑ AND A FOURTH ANSWER IS NOT A VERDICT. A `relative_to` whose argument this reader cannot trace to
any of the three is reported UNTRACED rather than assumed safe — the third outcome, because the
population this census exists to bound is precisely the one nobody had enumerated.

⚑⚑ A SITE THAT ALREADY HANDLES THE FAILURE IS NOT A CRASH AND IS STILL A COPY (gate-G255). Repairing
`module_size` found a hand-written `try/except ValueError` implementing the tolerant rule — correct,
and INVISIBLE to any census keyed on crashing, precisely because it does not crash. Those are
reported as GUARDED: not work to repair urgently, but a spelling to retire, and a census that
omitted them would report the rule as having fewer homes than it has.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

#: The call whose failure mode this census is about.
RELATIVE_TO = "relative_to"

#: Parameter names a reader uses for the tree it measures against.
ROOT_NAMES = ("root", "where", "base", "tree")

#: Module-level names that denote SUBSTRATE's own tree. A label measured against one of these while
#: the walk follows the caller's cwd is the composition this census is about.
GLOBAL_ROOTS = ("ROOT", "corpus.ROOT")


class Site(NamedTuple):
    """One `relative_to` call, and where the root it measures against came from.

    ⚑ THE THREE ORIGINS ARE DIFFERENT FACTS, NOT DEGREES OF ONE. A GLOBAL root cannot be rescued by
    any caller and crashes today. A DEFAULTED one crashes only when the default is taken. A RECEIVED
    one is protected by every caller stating its tree. Collapsing them either overstates today's
    breakage or hides the copies one edit away from it.
    """

    module: str
    func: str
    line: int
    origin: str

    @property
    def live(self) -> bool:
        """Report whether this site can measure against a root the walk did not follow."""
        return self.origin in {"global", "defaulted"}

    def why(self) -> str:
        """Return a one-line account naming the site and what decided its verdict."""
        said = {
            "global": "LIVE — labels against a module global no caller can set",
            "defaulted": "LIVE — labels against a defaulted root",
            "received": "latent — the root is always passed",
            "guarded": "guarded — catches ValueError by hand, a copy of the rule",
            "untraced": "UNTRACED — the root's origin is not decidable here",
        }[self.origin]
        return f"{self.module}:{self.line} {self.func}() — {said}"


def _guards_value_error(node: ast.FunctionDef) -> bool:
    """Report whether the body catches `ValueError` around its own work."""
    return any(
        isinstance(handler.type, ast.Name) and handler.type.id == "ValueError"
        for sub in ast.walk(node)
        if isinstance(sub, ast.Try)
        for handler in sub.handlers
    )


def _spelled(node: ast.expr) -> str:
    """Return the dotted spelling of a name or attribute, or the empty string."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = _spelled(node.value)
        return f"{head}.{node.attr}" if head else ""
    return ""


def _root_args(node: ast.FunctionDef) -> list[str]:
    """Return every expression a `relative_to` in this body measures against."""
    return [
        _spelled(sub.args[0])
        for sub in ast.walk(node)
        if isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == RELATIVE_TO
        and sub.args
    ]


def _params(node: ast.FunctionDef) -> tuple[set[str], set[str]]:
    """Return `(every parameter, those carrying a default)`."""
    args = node.args
    named = [a.arg for a in (*args.posonlyargs, *args.args)]
    kwonly = [a.arg for a in args.kwonlyargs]
    tail = named[len(named) - len(args.defaults) :] if args.defaults else []
    kw = [a.arg for a, d in zip(args.kwonlyargs, args.kw_defaults, strict=True) if d is not None]
    return set(named) | set(kwonly), set(tail) | set(kw)


def _walk_reaches(node: ast.FunctionDef, root: str) -> bool:
    """Report whether some call in this body is handed an expression built from `root`.

    ⚑⚑⚑ THIS IS THE ACQUITTING FACT, AND WITHOUT IT THE CENSUS REPORTED A WHOLE CLASS OF CLEAN
    SITES (gate-G262). `public_census.census_or_why` labels against `corpus.ROOT` — a genuine
    global, the exact shape that crashes elsewhere — and never crashes, because it walks
    `agda_files(str(root / "agda"))`. Every path it labels is under the labelling root BY
    CONSTRUCTION, since the WALK was rooted there too.

    ⚑ SO THE DEFECT WAS NEVER "labels against a global". It is *labels against a root the walk did
    not use*. Two independently-derived roots can disagree; one root used twice cannot. Reading
    only the labelling side reports the first as the second, which is how fifteen rows read LIVE
    and every executable one ran clean.
    """
    for call in ast.walk(node):
        if not isinstance(call, ast.Call):
            continue
        # ⚑⚑⚑ THREE WRONG CUTS BEFORE READING THE TREE, AND THE PROBE SETTLED IT IN ONE RUN. The
        # labelling call is `Path(f).relative_to(corpus.ROOT)`, whose ARGS are `['corpus.ROOT']`
        # and whose `relative_to` lives on its FUNC — so a filter scanning the argument subtree for
        # `relative_to` never saw it, and the census acquitted the one shape it exists to find.
        # Excluded here by the func, and the ENCLOSING `str(...)` by its argument subtree.
        if isinstance(call.func, ast.Attribute) and call.func.attr == RELATIVE_TO:
            continue
        for arg in call.args:
            parts = list(ast.walk(arg))
            if any(isinstance(p, ast.Attribute) and p.attr == RELATIVE_TO for p in parts):
                continue
            if any(isinstance(p, (ast.Name, ast.Attribute)) and _spelled(p) == root for p in parts):
                return True
    return False


def _bound_to(node: ast.FunctionDef, name: str) -> set[str]:
    """Return every spelling assigned to `name` anywhere in this body.

    ⚑ THE MEASURED ROOT IS USUALLY A LOCAL, and which local decides everything. `where = root if
    root is not None else corpus.ROOT` binds a global; `base = resolve_root(r, root)` binds a CALL
    whose own argument is the walked root. Reading only the name would call both untraced; reading
    only the body would call both global.
    """
    out: set[str] = set()
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == name for t in sub.targets):
            continue
        out.update(
            _spelled(part)
            for part in ast.walk(sub.value)
            if isinstance(part, (ast.Name, ast.Attribute))
        )
        out.update("()" for part in ast.walk(sub.value) if isinstance(part, ast.Call))
    return out - {""}


def _global_verdict(node: ast.FunctionDef, name: str, via: set[str], *, rescuable: bool) -> str:
    """Return the verdict for a label measured against a module global.

    ⚑⚑⚑ THE WALK'S OWN ROOT ACQUITS IT (gate-G262, operator-ruled). If some call in this body was
    handed an expression built from the SAME global, the paths being labelled were enumerated from
    under it and cannot fall outside — one root used twice, not two roots that might disagree.
    Without this, `public_census.census_or_why` reads LIVE forever: it labels against `corpus.ROOT`
    and walks `agda_files(str(root / "agda"))`, so it is clean BY CONSTRUCTION.
    """
    # ⚑⚑⚑ ASK ABOUT THE NAME ACTUALLY MEASURED, NOT THE GLOBAL IT CAME FROM (gate-G263). The probe
    # settled this in one run where three guesses had not: in `public_census.census_or_why` the
    # measured root is the LOCAL `root` (bound from `corpus.ROOT`), and the walk is handed
    # `str(root / 'agda')` — so `_walk_reaches(node, "root")` is True while
    # `_walk_reaches(node, "corpus.ROOT")` is False. Asking under the global's spelling could
    # never find the acquitting evidence, because the body stopped spelling it that way at line one.
    if _walk_reaches(node, name) or any(_walk_reaches(node, g) for g in GLOBAL_ROOTS if g in via):
        return "received"
    return "defaulted" if rescuable else "global"


def _origin(node: ast.FunctionDef, measured: list[str]) -> str:
    """Return where the root this function labels against came from.

    ⚑⚑⚑ THE GLOBAL TEST MUST BE ABOUT THE MEASURED ROOT, NOT ABOUT THE BODY (gate-G260). The first
    cut asked whether a global root name appeared ANYWHERE in the function and whether a
    `relative_to` appeared anywhere — never whether the two were the same root. So `corpus.py_files`
    was reported LIVE while its `relative_to(base)` measures against `base = resolve_root(r, root)`,
    the SAME call that produced the walk: two roots that cannot disagree, flagged as two roots that
    might. Ten of ten executed rows refuted on exactly this shape.

    ⚑⚑ SO THE TRACE RUNS FROM THE MEASURED NAME OUTWARD. A measured name bound from a CALL is
    co-derived with whatever that call was given — not a global standing beside the walk — and is
    reported `received`. Only a measured root that resolves to a module global with no such
    derivation is `global`, which is the shape that actually crashes.

    ⚑ A LOCAL BOUND FROM A DEFAULTED PARAMETER IS STILL DEFAULTED, and that is why the parameter
    list is still consulted: the fallback `else corpus.ROOT` makes the default reachable.
    """
    if _guards_value_error(node):
        return "guarded"

    every, defaulted = _params(node)
    roots = set(ROOT_NAMES)

    for name in measured:
        via = _bound_to(node, name) if name not in every else set()
        reaches_global = any(g in via for g in GLOBAL_ROOTS) or name in GLOBAL_ROOTS
        # ⚑⚑⚑ A CALL IN THE BINDING IS THE UNDECIDABLE CASE, NOT A SAFE ONE — operator ruling.
        # `base = resolve_root(r, root)` derives from the walked root AND `resolve_root` prefers
        # the caller's cwd, so the shape ADMITS divergence while every observed run denied it
        # (`walk_scope` clean from a borrowing checkout). Neither instrument overrules the other:
        # reporting LIVE banks a false positive, reporting latent banks a false negative, and the
        # honest answer is that the two disagree. UNTRACED carries that disagreement.
        if "()" in via:
            return "untraced"
        if reaches_global:
            return _global_verdict(node, name, via, rescuable=bool(defaulted & roots))
        if name in defaulted or (via & defaulted & roots):
            return "defaulted"
        if name in every or via & every:
            return "received"
    return "untraced"


def sites(source: str, module: str) -> list[Site]:
    """Return every `relative_to` site in `source`, classified by its root's origin."""
    out: list[Site] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.FunctionDef):
            continue
        measured = _root_args(node)
        if not measured:
            continue
        out.append(Site(module, node.name, node.lineno, _origin(node, measured)))
    return out


def census(files: Iterable[tuple[Path, str]]) -> list[Site]:
    """Return every root-measuring site across `files`, as `(path, label)` pairs.

    ⚑ A FILE THAT WILL NOT PARSE IS SKIPPED RATHER THAN COUNTED CLEAN, and the caller sees the
    shortfall in the denominator. Swallowing it would report a smaller population as a complete
    one — the census-green shape this whole class is about.
    """
    out: list[Site] = []
    for path, label in files:
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            out.extend(sites(source, label))
        except (SyntaxError, ValueError):
            continue
    return out
