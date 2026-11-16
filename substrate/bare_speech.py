#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which modules can be RUN and say nothing — the false zero in the CLI surface.

⚑⚑⚑ SILENCE-AND-EXIT-0 IS INDISTINGUISHABLE FROM "YOUR QUERY MATCHED NOTHING". MEASURED on
`substrate/store_calls.py`: an operator ran it bare and with a name while looking for call sites,
and read the silence as *no matches*. It is a store-connection reader over a three-name roster,
so the capability its name suggests would return empty for most inputs even when working
perfectly — and nothing in the output said so. This repo's own agda-codemod skill records the
same defect for four tools, where the instruction *"run the tool bare to read its modes"* fails
silently on exactly the tools where it matters most.

⚑⚑ THE POPULATION IS "MODULES THAT CAN BE RUN", NOT "MODULES". A library with no `__main__`
guard — `substrate.tool_census`, `substrate.tool_decline` — also prints nothing under
`python3 <path>`, and that silence is a fact about running a library as a script, not a tool
swallowing a query. Counting them would inflate the census with files that were never asked to
speak, which is the reverse of the defect: an instrument answering where it should scope.

⚑⚑ SO THE READING IS A CLASSIFICATION, NEVER A BARE COUNT, and the classes are what a reader
acts on differently:

    SPEAKS      the bare path reaches a write or a non-zero exit — the fixed shape
    SILENT      the bare path exits 0 with nothing written — the measured defect
    LIBRARY     no `__main__` guard at all — not a CLI, so not in scope for the defect
    SUITE       a `*_selftest.py`, whose bare run IS its verdict by convention

⚑⚑⚑ AND THE FIRST CUT OF THIS CENSUS REPORTED 32 SILENT CLIs, OF WHICH MOST WERE ITS OWN
FALSE POSITIVES — including `file_mode.py`, `module_outline.py` and `attr_reads.py`, each of
which was then RUN and observed to print a usage line and exit 2. The reader stopped at
`sys.exit(main(sys.argv[1:]))` and declined to follow the delegation, so every module using the
overwhelmingly common entry-point idiom in this package read as mute. **That is a fact about the
METHOD reported as a fact about the SUBSTRATE** — the defect this module was written to find,
committed by the instrument built to find it, and caught only by running three of the accused.

⚑⚑ SO THE DELEGATION IS FOLLOWED, ONE HOP, INTO A MODULE-LEVEL FUNCTION. One hop is enough for
the idiom and stops well short of an interprocedural analysis this has no business attempting;
a helper called BY `main` is not followed, so a tool whose only speech is two calls deep still
reads SILENT. ⚑ THAT RESIDUAL IS A FALSE POSITIVE IN THE SAFE DIRECTION — it over-reports a
defect a reader can dismiss in one run, rather than under-reporting one they would never look
for. It is named here so the next reader dismisses it from the record rather than re-deriving it.

⚑ THIS IS A STATIC READING AND IT SAYS SO. It reads the entry path for a write or a non-zero
exit rather than executing hundreds of modules — running them is the other instrument, and it is
wrong in the opposite direction (an import side effect, a store connection, a slow corpus walk).
⚑ A guard whose speech is CONDITIONAL on an argument is reported as SILENT for the BARE path,
which is the path the defect lives on; that is deliberate, and it is why the class is named for
what the bare invocation does rather than for whether the module ever writes anything.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The classes a runnable module's bare invocation falls into.
SPEAKS = "SPEAKS"
SILENT = "SILENT"
LIBRARY = "LIBRARY"
SUITE = "SUITE"

# The suffix `suite_discovery` uses to name a suite. ⚑ CITED FROM THE CONVENTION, not re-spelled
# as a guess: a suite's bare run is its verdict, which is speech of a different kind.
SUITE_SUFFIX = "_selftest.py"

# The names a guard body can call to write. ⚑ A WRITE TO EITHER STREAM IS SPEECH — a refusal
# belongs on stderr and a reading on stdout, and a census that counted only stdout would report
# every correctly-refusing tool as silent.
WRITERS = frozenset({"write", "print"})


@dataclass(frozen=True, slots=True)
class Speech:
    """What one module's bare invocation does — its class, and why it was put there."""

    path: str
    kind: str
    why: str

    @property
    def in_scope(self) -> bool:
        """Report whether this module is a CLI the silence defect can apply to."""
        return self.kind in (SPEAKS, SILENT)


def _guard(tree: ast.Module) -> ast.If | None:
    """Return the module's `if __name__ == "__main__"` block, or None when it has none."""
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.dump(node.test):
            return node
    return None


def _functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    """Return the module-level functions by name — the one hop a delegation is followed into."""
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _nonzero_exit(call: ast.Call) -> bool:
    """Report whether a `sys.exit(...)` carries a non-zero literal.

    ⚑ `sys.exit(2)` IS SPEECH EVEN WITH NO TEXT, because a non-zero status is a signal a caller
    can act on — the thing exit 0 in silence denies them. `sys.exit(0)` says nothing.
    """
    if not call.args:
        return False
    first = call.args[0]
    return isinstance(first, ast.Constant) and isinstance(first.value, int) and first.value != 0


def _delegate(call: ast.Call) -> str | None:
    """Return the module-level function a `sys.exit(f(...))` hands off to, if it is one.

    ⚑ THE IDIOM THIS EXISTS FOR IS `sys.exit(main(sys.argv[1:]))`, which the first cut read as
    silence and which nearly every CLI in this package uses. Not following it made the census
    report its own blind spot as a corpus-wide defect.
    """
    if not (isinstance(call.func, ast.Attribute) and call.func.attr == "exit"):
        return None
    if not call.args:
        return None
    inner = call.args[0]
    if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name):
        return inner.func.id
    return None


def _speaks(node: ast.stmt, functions: dict[str, ast.FunctionDef], *, follow: bool) -> bool:
    """Report whether one statement writes, exits non-zero, or delegates to something that does.

    ⚑ `follow` IS SPENT, NOT PASSED THROUGH. It permits exactly one hop into a module-level
    function; inside that function it is False, so a helper called by `main` is not pursued. The
    bound is what keeps this a reading of an idiom rather than an interprocedural analysis.
    """
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        func = sub.func
        if isinstance(func, ast.Attribute) and func.attr in WRITERS:
            return True
        if isinstance(func, ast.Name) and func.id in WRITERS:
            return True
        if isinstance(func, ast.Attribute) and func.attr == "exit" and _nonzero_exit(sub):
            return True
        target = _delegate(sub) if follow else None
        if target is not None and target in functions:
            body = functions[target].body
            if any(_speaks(stmt, functions, follow=False) for stmt in body):
                return True
    return False


def _writes_unconditionally(guard: ast.If, functions: dict[str, ast.FunctionDef]) -> bool:
    """Report whether the bare path — taking no argument — writes or exits non-zero.

    ⚑ A WRITE NESTED INSIDE `if "--mode" in sys.argv` IS SPEECH FOR THAT MODE, not for the bare
    call, so it is not counted; `store_calls` had exactly that shape, speaking under `--selftest`
    and silent bare. The `else` of such a branch IS the bare path and is counted.
    """
    for node in guard.body:
        if isinstance(node, ast.If):
            if node.orelse and any(_speaks(sub, functions, follow=True) for sub in node.orelse):
                return True
            continue
        if _speaks(node, functions, follow=True):
            return True
    return False


def read_one(path: Path, label: str) -> Speech | None:
    """Return what `path`'s bare invocation does, or None when it cannot be parsed."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return None
    if label.endswith(SUITE_SUFFIX):
        return Speech(label, SUITE, "a suite — its bare run is its verdict by convention")
    guard = _guard(tree)
    if guard is None:
        return Speech(label, LIBRARY, "no __main__ guard — not a CLI")
    if _writes_unconditionally(guard, _functions(tree)):
        return Speech(label, SPEAKS, "the bare path writes or refuses")
    return Speech(
        label,
        SILENT,
        "⚑ the bare path exits 0 with nothing written — indistinguishable from "
        "'your query matched nothing'",
    )


def census(root: Path | None = None) -> tuple[Speech, ...]:
    """Return one reading per module under `substrate/`, in path order."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    out = []
    for path in sorted(where.glob("*.py")):
        row = read_one(path, path.name)
        if row is not None:
            out.append(row)
    return tuple(out)


def render(rows: tuple[Speech, ...]) -> str:
    """Return the census: every silent CLI named, then the denominators by class."""
    silent = [r for r in rows if r.kind == SILENT]
    lines = [f"  {r.path}: {r.why}" for r in silent]
    counts = {
        kind: sum(1 for r in rows if r.kind == kind) for kind in (SPEAKS, SILENT, LIBRARY, SUITE)
    }
    lines.append(
        f"{counts[SILENT]} silent CLI(s) of {counts[SPEAKS] + counts[SILENT]} runnable "
        f"({len(rows)} module(s) read: {counts[LIBRARY]} librar(ies), "
        f"{counts[SUITE]} suite(s))"
    )
    lines.append(
        "  ⚑ a LIBRARY prints nothing because it is not a CLI — that silence is a fact "
        "about running a library as a script, not a swallowed query"
    )
    lines.append(
        "  ⚑ STATIC, and it follows a `sys.exit(main(...))` delegation ONE hop; speech "
        "two calls deep still reads SILENT, so confirm a row by RUNNING it"
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Print the bare-invocation census, exiting 1 when any runnable module is silent."""
    if argv:
        sys.stderr.write(
            "bare_speech.py takes no operand — it reads all of substrate/.\nusage: bare_speech.py\n"
        )
        return 2
    rows = census()
    sys.stdout.write(render(rows))
    return 1 if any(r.kind == SILENT for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
