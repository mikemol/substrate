#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Who has NOT reached the argv center — the modules still claiming to own the process.

⚑⚑⚑ THE RULING, AND THE TWO CLAIMS IT NAMES. On `sys.exit(main(sys.argv[1:]))`, the operator:
*"Yeah, that has to stop. No code should assume it is The Owner of the PID."* One line makes two
ownership claims, and both are false for anything importable:

    `sys.argv`  — "the process's arguments are MINE".  A caller cannot invoke the capability
                  with different arguments; the parameter has become a global READ, so the
                  function's inputs are not in its signature.
    `sys.exit`  — "the process's lifetime is MINE".  A caller cannot COMPOSE the capability;
                  control of the PID is taken rather than returned, so there is no way to run
                  it and then do something else.

⚑⚑ THE POPULATION IS "WHO HAS NOT REACHED THE CENTER", NOT "WHO TOUCHES sys.argv". The second is
undifferentiated (an `attr_reads sys.argv` over this corpus is tens of thousands of lines, and
reading it by eye is the judgement-in-the-turn this repo forbids); the first is a WORK LIST whose
destination is already built. `substrate.ratchet_flags.check_argv` is the center — one definition,
reached by every ratchet gate, `gate_census`, `run_selftests`, `worklist_gate`, and out as far as
`jea/metalanguage/sorted_stream.py` — and its refusals are the right shape:

    unknown flag(s) --queit — known: --dry-run --quiet
    neither --apply nor --dry-run was given ... State one.
    BOTH --sandbox and --live given — mutually exclusive. Refusing rather than picking one.

⚑⚑⚑ SO EVERY ROW HERE IS A DELETION, NOT AN ADDITION. The operator's reading is the load-bearing
one: *"centralizing sys.argv processing is GOOD modularity and reuse promotion."* A large
population of one pattern is the argument FOR a shared reader, not a burden — a conversion removes
local parsing and inherits the center's refusals for free. `main` below is the worked example.

⚑⚑ AND THE KINDS ARE WHAT A READER ACTS ON, because a bare count would be a fact about this
instrument. `bare_speech` established the shape (SPEAKS / SILENT / LIBRARY / SUITE) precisely
because ~100 guard-less libraries print nothing for a reason that is NOT the defect; collapsing
them would have shipped a list of non-problems. The kinds here were settled the same way — each is
a different NEXT ACTION:

    ENTRY      a `__main__` guard reading `sys.argv` and handing it to a function.  ⚑ THE ONE
               PLACE A PROCESS MAY LEGITIMATELY CLAIM ARGV — this is a process entry point, not
               a module capability, and `sys.argv` is exactly what it is for.  NOT a defect; it
               is the boundary the other kinds are measured against.
    REACHED    the guard's callee reaches `check_argv`.  Done — the center is already in hand.
    UNREACHED  the guard's callee parses flags itself and never reaches the center.  THE WORK
               LIST, and the kind whose every row is a deletion of local parsing.
    CAPTIVE    a `sys.argv` READ inside a module-level function that is not the entry callee — a
               capability whose input is a global.  A caller cannot pass different arguments, so
               this is the argv half of the ruling with no entry point to excuse it.
    FATAL      a `sys.exit` on a LIBRARY path — a module with no `__main__` guard at all, so no
               invocation of it is ever the process's own.  The lifetime half of the ruling, and
               the kind with no legitimate instance.
    SUITE      a `*_selftest.py`.  ⚑ ENTANGLED WITH A MIGRATION ALREADY DECIDED — see below.
    CLEAR      neither claim: no `sys.argv` read and no `sys.exit` outside a guard.

⚑⚑⚑ THE SUITE KIND IS HELD SEPARATE BECAUSE CONVERTING IT WOULD BE WASTED WORK. The
selftest-discovery contract keys on the literal `--selftest` appearing in a file, so EVERY suite in
this tree reads `sys.argv` to honour it — the read is not a defect, it is compliance. The pytest
migration item scopes retiring collection and invocation wholesale, taking that reader with it. A
row converted here would be deleted there. Suites are counted, named as a class, and NOT put on the
work list; `suites()` exposes them so the pytest item can size its own overlap against this reading.

⚑ THIS IS A STATIC READING AND SAYS SO. It follows the `sys.exit(main(...))` delegation ONE hop
into a module-level function, the same bound `bare_speech` argues: enough for the idiom that
dominates this package, and well short of an interprocedural analysis. A module that reaches
`check_argv` two calls deep therefore reads UNREACHED. ⚑ THAT RESIDUAL IS A FALSE POSITIVE IN THE
SAFE DIRECTION — it over-reports work a reader dismisses in one open, rather than under-reporting a
claim nobody looks for. It is named so the next reader dismisses it from the record instead of
re-deriving it.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from mikemol.corpus import tree_root

from substrate import corpus, walk_scope
from substrate.ratchet_flags import check_argv

# The kinds one module's relationship to the argv center falls into. ⚑ NAMED FOR THE NEXT ACTION,
# not for the syntax that produced them — `CAPTIVE` and `UNREACHED` are both `sys.argv` reads and
# are entirely different work.
ENTRY = "ENTRY"
REACHED = "REACHED"
UNREACHED = "UNREACHED"
CAPTIVE = "CAPTIVE"
FATAL = "FATAL"
SUITE = "SUITE"
CLEAR = "CLEAR"

# The kinds that constitute the work list — a module still claiming what it does not own.
WORK = (UNREACHED, CAPTIVE, FATAL)

# Every kind, in render order. ⚑ ONE TUPLE, so a kind added to the classifier and forgotten in the
# render cannot silently vanish from the denominator.
KINDS = (ENTRY, REACHED, UNREACHED, CAPTIVE, FATAL, SUITE, CLEAR)

# The center. ⚑ THE NAME IS THE AUTHORITY'S OWN SPELLING; a reader matching on a paraphrase would
# report the whole population as unreached the day the center is renamed, which is the
# `census-keyed-on-one-spelling` defect one level down.
CENTER = "check_argv"

# The module the center lives in, for the render's pointer.
CENTER_MODULE = "substrate.ratchet_flags"

# The suffix the suite-discovery convention uses to name a suite. ⚑ CITED FROM THE CONVENTION
# rather than re-spelled as a guess, for the same reason `bare_speech` cites it.
SUITE_SUFFIX = "_selftest.py"

# The literal selftest-discovery keys on — why every suite reads argv, and what pytest retires.
DISCOVERY_LITERAL = "--selftest"

# This tool's one flag, declared once. ⚑ NAMED SO THE CENTER AND THE DISPATCH CANNOT DISAGREE —
# a `known` set listing a flag the body then tests by a different literal is a gate that refuses
# nothing and accepts nothing, which is the shape `check_argv` exists to prevent one level up.
_SUITES_FLAG = "--suites"

# How many callee names the UNREACHED detail may print. ⚑ A DISPATCH GUARD HANDS OFF TO MANY, and
# a detail line naming twenty of them is a row a reader skips — which costs the work list the one
# thing it is for.
_DETAIL_CALLEES = 3

# Why each kind is where it is. ⚑ ONE REASON PER KIND, NOT PER ROW — `walk_scope.render` measured
# that stapling a justification to every member turns it into a false claim about each one, and
# teaches a reader to skip the block.
_WHY = {
    ENTRY: "a `__main__` guard's own body — the ONE place a process may claim its own argv; "
    "this is the boundary, not a defect",
    REACHED: f"already reaches `{CENTER_MODULE}.{CENTER}` — the center is in hand",
    UNREACHED: f"parses flags itself and never reaches `{CENTER}` — THE WORK LIST; each "
    "conversion DELETES local parsing and inherits the center's refusals",
    CAPTIVE: "reads `sys.argv` inside a function that is not the entry callee — the capability's "
    "input is a global, so a caller cannot invoke it with different arguments",
    FATAL: "calls `sys.exit` with no `__main__` guard anywhere in the module — a library taking "
    "the process's lifetime, which no import ever authorises",
    SUITE: f"a `*{SUITE_SUFFIX}` — it reads argv to honour the `{DISCOVERY_LITERAL}` discovery "
    "contract, which the pytest migration retires wholesale (NOT work owed here)",
    CLEAR: "claims neither the arguments nor the lifetime",
}

# The bounds of this reading — what the PREDICATE could not decide about a file it DID read.
# ⚑⚑ A DIFFERENT BOUNDARY FROM `walk_scope`'s, which states what the WALK never reached. Both are
# printed, because a census reporting a small work list is only readable if a reader can tell
# *few* from *could not see*.
_BLIND = (
    (
        f"one-hop — a module reaching `{CENTER}` two calls deep (a helper called BY the entry "
        "callee) reads UNREACHED; a false positive in the safe direction"
    ),
    (
        "dynamic-dispatch — a callee resolved through a table, a getattr or a class method is not "
        "a module-level function, so its argv handling is invisible to this reader"
    ),
    (
        f"re-export — a module importing `{CENTER}` through an intermediate that re-exports it "
        "still matches by NAME, but one wrapping it under a different name does not"
    ),
    (
        "nested-def — an argv read inside a class method or a nested function is not a "
        "module-level def, so CAPTIVE under-reports by exactly that shape"
    ),
)

# The bound that exists only when suites are present — the overlap with the pytest migration.
_BLIND_SUITE = (
    f"suite-entanglement — every `*{SUITE_SUFFIX}` reads argv to honour "
    f"`{DISCOVERY_LITERAL}`; that population belongs to the pytest migration, and "
    "its size here is a reading of the OVERLAP, not of work owed"
)


@dataclass(frozen=True, slots=True)
class Claim:
    """What one module claims about the process it runs in, and why it was put there."""

    path: str
    kind: str
    detail: str

    @property
    def is_work(self) -> bool:
        """Report whether this row belongs on the conversion work list."""
        return self.kind in WORK

    @property
    def why(self) -> str:
        """Return the reason this module's kind carries, from the one place it is written."""
        return _WHY[self.kind]


def _guard(tree: ast.Module) -> ast.If | None:
    """Return the module's `if __name__ == "__main__"` block, or None when it has none."""
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.dump(node.test):
            return node
    return None


def _functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """Return the module-level functions by name — the one hop a delegation is followed into."""
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _reads_argv(node: ast.AST) -> bool:
    """Report whether any `sys.argv` read occurs anywhere under `node`.

    ⚑ IT MATCHES THE NAME, NOT THE RECEIVER SPELLING. `sys.argv` and a `from sys import argv` bare
    name are the same claim; matching only the dotted form would make this census keyed on one
    spelling, which is the defect it is measuring one level up.
    """
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr == "argv":
            return True
        if isinstance(sub, ast.Name) and sub.id == "argv":
            return True
    return False


def _calls(node: ast.AST, name: str) -> bool:
    """Report whether `name` is called anywhere under `node`, by either spelling.

    ⚑ BOTH SPELLINGS, DELIBERATELY. A gate reaching the center writes `check_argv(...)` after a
    `from substrate.ratchet_flags import check_argv`; another writes `ratchet_flags.check_argv`.
    Reading only one would report half the adopters as unreached.
    """
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Name) and func.id == name:
            return True
        if isinstance(func, ast.Attribute) and func.attr == name:
            return True
    return False


def _exits(node: ast.AST) -> bool:
    """Report whether `sys.exit` is called anywhere under `node`."""
    return any(
        isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == "exit"
        for sub in ast.walk(node)
    )


def _handed_to(call: ast.Call) -> str | None:
    """Return the bare name this call hands control to, direct or through a `sys.exit(f(...))`."""
    if isinstance(call.func, ast.Attribute) and call.func.attr == "exit" and call.args:
        inner = call.args[0]
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
            return inner.func.id
        return None
    if isinstance(call.func, ast.Name):
        return call.func.id
    return None


def _delegates(guard: ast.If, known: frozenset[str]) -> tuple[str, ...]:
    """Return the module-level functions the guard hands control to, in source order.

    ⚑ THE IDIOM IS `sys.exit(main(sys.argv[1:]))` AND IT IS THE WHOLE POINT. The guard reads argv
    legitimately; the question this census asks is what it hands that argv TO, and whether THAT
    function reached the center. Stopping at the guard would classify every CLI in the package as
    an ENTRY and report zero work — a reader answering about itself.

    ⚑⚑ IT IS FILTERED BY `known`, AND THE FIRST CUT WAS NOT — WHICH BROKE IT IN BOTH DIRECTIONS.
    Collecting every bare-name call under a guard swept up `print`, `len` and `sorted`, so a
    dispatch guard reported a twenty-name callee list; that is merely unreadable. The damage was
    that `callees` is ALSO what excuses a function from CAPTIVE, so an unrelated module-level name
    called in the guard silently exempted itself — a census suppressing its own findings through a
    detail nobody would read as load-bearing. MEASURED on this file's own first run.
    """
    names: list[str] = []
    for sub in ast.walk(guard):
        if not isinstance(sub, ast.Call):
            continue
        handed = _handed_to(sub)
        if handed is not None and handed in known and handed not in names:
            names.append(handed)
    return tuple(names)


def _captive(tree: ast.Module, callees: frozenset[str]) -> str | None:
    """Return the first module-level function reading argv that is not an entry callee.

    ⚑⚑ THE ENTRY CALLEE IS EXCLUDED AND THAT IS NOT A LOOPHOLE. A `main(argv)` that the guard
    hands `sys.argv[1:]` takes its arguments as a PARAMETER — the shape the ruling asks for — and
    would be a false CAPTIVE if the exclusion were dropped. What remains is a function reading the
    global with no entry point standing behind it, which is the claim with no excuse.
    """
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name in callees:
            continue
        if _reads_argv(node):
            return node.name
    return None


def _read_library(tree: ast.Module, label: str) -> Claim:
    """Classify a module with NO `__main__` guard — nothing here is ever a process entry point.

    ⚑ THIS IS THE ARM WHERE `sys.exit` HAS NO DEFENCE. Every other kind can point at a guard and
    say the process was its own; a module with no guard is only ever imported, so ending the
    process is a claim over a lifetime it was never handed.
    """
    if _exits(tree):
        return Claim(label, FATAL, "sys.exit on a library path")
    captive = _captive(tree, frozenset())
    if captive is not None:
        return Claim(label, CAPTIVE, f"{captive}() reads argv")
    return Claim(label, CLEAR, "no claim")


def _named(callees: tuple[str, ...]) -> str:
    """Return the callee list a detail line prints, truncated with its own count."""
    shown = "/".join(callees[:_DETAIL_CALLEES])
    extra = len(callees) - _DETAIL_CALLEES
    return f"{shown} (+{extra} more)" if extra > 0 else shown


def _read_guarded(tree: ast.Module, guard: ast.If, label: str) -> Claim:
    """Classify a module WITH a `__main__` guard, by what its entry callee does with argv."""
    functions = _functions(tree)
    callees = _delegates(guard, frozenset(functions))
    bodies = [functions[n] for n in callees]
    if any(_calls(body, CENTER) for body in bodies) or _calls(guard, CENTER):
        return Claim(label, REACHED, f"{CENTER} reached")
    captive = _captive(tree, frozenset(callees))
    if captive is not None:
        return Claim(label, CAPTIVE, f"{captive}() reads argv")
    if bodies and any(_reads_argv(body) for body in bodies):
        return Claim(label, UNREACHED, f"{_named(callees)} parses argv without {CENTER}")
    return Claim(label, ENTRY, "guard delegates its argv")


def read_one(path: Path, label: str) -> Claim | None:
    """Return what `path` claims about the process, or None when it cannot be parsed."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None
    if label.endswith(SUITE_SUFFIX):
        return Claim(label, SUITE, f"honours `{DISCOVERY_LITERAL}`")
    guard = _guard(tree)
    if guard is None:
        return _read_library(tree, label)
    return _read_guarded(tree, guard, label)


def _path_of(row: Claim) -> str:
    """Return a row's path — the sort key, named so the sort carries no untyped lambda."""
    return row.path


def census(root: Path | None = None) -> tuple[Claim, ...]:
    """Return one reading per module in the corpus, in path order.

    ⚑ THE WALK IS `corpus.py_files`, NOT A LOCAL `rglob`. It is the repo's one enumeration, so this
    census shares its denominator — and its exclusions — with every sibling reader, which is what
    makes `walk_scope.render` an honest statement of THIS census's boundary rather than a generic
    one pasted beneath it.

    ⚑⚑ AND SHARING THE WALK IS WHAT MADE THE LABEL RAISE (gate-G245 / gate-G249 / gate-G252).
    `corpus.resolve_root` resolves the caller's CWD FIRST — deliberately, so a peer gets THEIR
    tree — while `Path.relative_to` measured against SUBSTRATE's, and the census died on the
    first foreign row. `tree_root` carries one root and does both.
    """
    where = root if root is not None else corpus.ROOT
    tree = tree_root.of(where)
    out: list[Claim] = []
    for name in corpus.py_files(root=where):
        path = Path(name)
        row = read_one(path, tree.label(path))
        if row is not None:
            out.append(row)
    return tuple(sorted(out, key=_path_of))


def suites(rows: tuple[Claim, ...]) -> tuple[Claim, ...]:
    """Return the suite rows — the population the pytest migration overlaps.

    ⚑ EXPOSED AS ITS OWN QUERY BECAUSE THE OVERLAP IS THE DELIVERABLE, not a footnote. The pytest
    item needs the SIZE of the set it retires; a census that folded suites into the work list would
    hand it a number that double-counts, and one that dropped them silently would hand it nothing.
    """
    return tuple(r for r in rows if r.kind == SUITE)


def worklist(rows: tuple[Claim, ...]) -> tuple[Claim, ...]:
    """Return the rows a conversion is owed, in path order."""
    return tuple(r for r in rows if r.is_work)


def unresolved(rows: tuple[Claim, ...]) -> tuple[str, ...]:
    """Return the shapes that could hide a claim this reader cannot decide.

    ⚑⚑ THIS IS THE HALF THAT MAKES THE ZERO HONEST. A count alone cannot distinguish *none* from
    *could not see*, and that collapse is the defect this whole census exists to name one level up
    — so re-introducing it here would be the same error wearing the fix's clothes.
    """
    if any(r.kind == SUITE for r in rows):
        return (*_BLIND, _BLIND_SUITE)
    return _BLIND


def render(rows: tuple[Claim, ...]) -> str:
    """Return the work list, then the denominators by kind, then both boundaries."""
    lines = [f"  {r.kind:<10} {r.path}  — {r.detail}" for r in worklist(rows)]
    counts = {kind: sum(1 for r in rows if r.kind == kind) for kind in KINDS}
    owed = sum(counts[k] for k in WORK)
    lines.append(
        f"{owed} module(s) owed a conversion to {CENTER_MODULE}.{CENTER}, of {len(rows)} read"
    )
    lines.extend(f"  {counts[kind]:>5}  {kind:<10} {_WHY[kind]}" for kind in KINDS)
    lines.append("  ⚑ what this reading cannot decide:")
    lines.extend(f"     {shape}" for shape in unresolved(rows))
    return "\n".join(lines) + "\n" + walk_scope.render()


def main(argv: list[str]) -> int:
    """Print the argv-center census; return 0 always — this is a reading, not a gate.

    ⚑⚑ IT DOES NOT REFUSE ON A NON-EMPTY WORK LIST, DELIBERATELY, AND THAT IS NOT TIMIDITY. The
    deliverable is a census; a gate over it is a RATCHET, which needs a baseline and a paydown
    policy nobody has set. Exiting 1 today would make every commit in the tree red over a
    population nobody agreed to freeze — a gate asserting a decision it was not given.

    ⚑⚑⚑ THIS FUNCTION IS THE WORKED CONVERSION, WHICH IS WHY THE COST IS QUOTED FROM A FILE
    RATHER THAN ESTIMATED. The first cut hand-rolled `if argv and argv != ["--suites"]: usage` —
    the exact UNREACHED shape this census names, and it read UNREACHED in its own first run.
    Routing it through the center DELETED that comparison and bought three things the local check
    never had: an unknown flag is REFUSED and named alongside the known set (verified by running
    `--suties`), whatever `ratchet_flags.UNIVERSAL_FLAGS` declares is admitted here without this
    file re-listing it, and the invocation is recorded in the fallthrough census. The whole edit
    is an import, a flag constant, and a two-line replacement — but it touches three regions of
    the file, so under this repo's per-file gate it is ONE `Write`, not a three-line patch. That
    is the real unit of the work list this module renders.
    """
    if (rc := check_argv(argv, (_SUITES_FLAG,), "pid_ownership")) is not None:
        return rc
    rows = census()
    if _SUITES_FLAG in argv:
        found = suites(rows)
        for row in found:
            sys.stdout.write(f"  {SUITE}  {row.path}\n")
        sys.stdout.write(
            f"{len(found)} suite(s) — the pytest migration's population, not this work list\n"
        )
        return 0
    sys.stdout.write(render(rows))
    return 0


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (the selftest-discovery convention). A bare `0`
# here would make this a roster member asserting NOTHING — reported `silent (0/0)` by the very
# runner it is meant to be read by.
# ⚑⚑ AND THE GUARD IS THE ONE `sys.exit(main(sys.argv[1:]))` THIS MODULE IS ALLOWED — it IS the
# `__main__` guard, the one place the ruling exempts, and writing it any other way would make the
# census unable to classify its own author under the kind it defines as the boundary.
if __name__ == "__main__":
    if DISCOVERY_LITERAL in sys.argv:
        from substrate import pid_ownership_selftest

        sys.exit(pid_ownership_selftest.selftest())
    sys.exit(main(sys.argv[1:]))
