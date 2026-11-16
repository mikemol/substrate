# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which declared flags a tool's modes actually READ — the per-tool set against per-mode use.

⚑⚑⚑ A FLAG SET DECLARED PER TOOL ADMITS A MODE-OWNED FLAG ON EVERY MODE. `check_argv` takes
one flat `known` set, so a modifier that means something to one branch passes validation on
every other and is then silently ignored. Measured: `check_mode_contracts --where --quiet`
prints in full and exits 0, and `check_sorted_order --list --quiet` prints 130 rows — both for
a caller who asked for silence (gate-G312). **The refusal's own docstring names this defect —
*a silently ignored `--quiet` is a gate that looks like it ran* — and it is what the same
function now produces for a flag it admitted.**

⚑⚑ THE DISCRIMINATOR IS BORROWED RATHER THAN INVENTED, and it is what keeps this from
reporting every gate as broken. `pycodemod.opt_key_collisions` answers an adjacent question
(a spelling that is both a mode key and an opt inside ONE declared roster) and its harm test
transfers: **a collision is a defect only when the two roles MEAN different things.** A flag
read by no branch at all is a phantom; a flag read by SOME branch and not others is the real
finding, because it is a live capability on one mode and a no-op on another.

⚑ SO THE THREE OUTCOMES ARE DELIBERATE. `UNIVERSAL` — every branch reads it, or it is read
before any dispatch, so admitting it everywhere is honest. `PARTIAL` — read by some branch and
not others, which is the shape that produced both measured instances. `PHANTOM` — declared and
read nowhere, a promise the CLI cannot keep.

⚑⚑ AND THIS IS A READ, NOT A GATE. It reports which flags are partial; whether a partial flag
is worth repairing depends on what the unreading mode is FOR, which no reader can decide. A
census that refused on every PARTIAL row would demand that `--quiet` be wired into a mode whose
entire output is one line.

⚑ THE READER'S BOUND, STATED: a branch "reads" a flag when the flag's spelling appears as a
literal inside that branch's own source span. A mode that reads its flag through a helper, or
through a variable bound earlier, reads as NOT reading it — so PHANTOM and PARTIAL are both
FLOORS on the defect and over-report is the direction this errs in. Open a site before acting.

⚑⚑⚑ AND THE SECOND BOUND WAS MEASURED, NOT ANTICIPATED — A PHANTOM THAT RUNS. The population is
`main`'s top-level branches, so a mode dispatched ANYWHERE ELSE is invisible. `check_mode_contracts
--selftest` reads PHANTOM here and answers `14/14` when run: it is dispatched in the `if __name__`
tail, outside `main` entirely. **A phantom row is a QUESTION to open, never a verdict that a mode
is missing** — the first one checked was the reader's blind spot rather than the tool's defect.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple

#: The mode this module has, named so a bare run prints the spelling a reader needs next.
MODE = "--ownership"

#: What a bare or unknown invocation exits with — usage, not a verdict about the tree.
USAGE_EXIT = 2

#: The refusal every gate is supposed to call first, and whose second positional is the set
#: this module reads. Named rather than spelled inline so a rename is one edit.
REFUSAL = "check_argv"

#: Flags the refusal admits for every caller by construction, so a gate not reading one of
#: these is not a finding about that gate. ⚑ READ FROM THE AUTHORITY rather than retyped: a
#: second roster beside `ratchet_flags.UNIVERSAL_FLAGS` would drift the first time one is added.
UNIVERSAL_BY_CONSTRUCTION = frozenset({"--help", "-h"})


class Flag(NamedTuple):
    """One declared flag and which of its tool's branches actually read it."""

    flag: str
    readers: tuple[str, ...]
    branches: tuple[str, ...]

    def verdict(self) -> str:
        """Return UNIVERSAL, PARTIAL or PHANTOM — three outcomes, and the middle one is the find.

        ⚑ PHANTOM AND UNIVERSAL ARE BOTH FINE-OR-OBVIOUS; PARTIAL IS THE DEFECT. A flag no
        branch reads is a promise the CLI cannot keep and shows up as its own row; a flag every
        branch reads is correctly global. The one that hides is the flag that WORKS somewhere,
        because a caller who saw it work once reasonably expects it to work again.
        """
        if not self.readers:
            return "PHANTOM"
        return "UNIVERSAL" if len(self.readers) == len(self.branches) else "PARTIAL"

    def why(self) -> str:
        """Return a one-line account naming the flag, its verdict and who ignores it."""
        if self.verdict() == "PHANTOM":
            return f"{self.flag}  PHANTOM — declared, read by no branch"
        if self.verdict() == "UNIVERSAL":
            return f"{self.flag}  universal — every branch reads it"
        deaf = [b for b in self.branches if b not in self.readers]
        return (
            f"{self.flag}  PARTIAL — read by {', '.join(self.readers)}; "
            f"SILENTLY IGNORED by {', '.join(deaf)}"
        )


class Tool(NamedTuple):
    """One tool's declared flag set, measured against what its branches read."""

    path: str
    flags: tuple[Flag, ...]

    def partial(self) -> tuple[Flag, ...]:
        """Return only the flags read by some branch and not others."""
        return tuple(f for f in self.flags if f.verdict() == "PARTIAL")

    def lines(self) -> list[str]:
        """Return this tool's rows, the partial ones first because they are the finding."""
        rows = sorted(self.flags, key=_order)
        return [f"  {f.why()}" for f in rows]


def _order(flag: Flag) -> tuple[int, str]:
    """Return the sort key — PARTIAL first, then PHANTOM, then universal, each alphabetical."""
    rank = {"PARTIAL": 0, "PHANTOM": 1, "UNIVERSAL": 2}
    return (rank[flag.verdict()], flag.flag)


def declared(tree: ast.AST) -> tuple[str, ...]:
    """Return the flag spellings passed to the refusal as its second positional.

    ⚑ THE SET IS A LITERAL AT EVERY CALL SITE TODAY, and a computed one reads as EMPTY here
    rather than as an error — which makes this a floor. A gate building its flag set
    dynamically would report every flag as phantom, so an empty declaration is reported as
    unreadable rather than as a clean bill.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else None
        if name != REFUSAL or len(node.args) < 2:  # noqa: PLR2004 - argv and the flag set
            continue
        found = node.args[1]
        if isinstance(found, (ast.Set, ast.List, ast.Tuple)):
            return tuple(
                sorted(
                    e.value
                    for e in found.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                )
            )
    return ()


def branches(tree: ast.AST, src: str) -> dict[str, str]:
    """Return `{branch-label: source}` for each top-level `if` inside the entry point.

    ⚑⚑ A BRANCH IS AN `if` IN `main`, WHICH IS THE SHAPE THESE GATES ACTUALLY HAVE. They are
    not argparse subcommands — the convention is a chain of `if "--flag" in sys.argv`, and the
    refusal's own docstring records why: these are invoked positionally from a shell hook, so
    swapping in a parser would change every call site to fix a typo problem.

    ⚑ THE FALLTHROUGH IS A BRANCH TOO, named `<default>`, because it is where a gate does its
    actual work — and a flag the default path reads while a mode ignores it is precisely the
    measured instance.
    """
    lines = src.splitlines()
    out: dict[str, str] = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "main"):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.If) and stmt.end_lineno and _is_mode(stmt, lines):
                out[_label(stmt, lines)] = "\n".join(lines[stmt.lineno - 1 : stmt.end_lineno])
        out["<default>"] = "\n".join(lines[node.lineno - 1 : (node.end_lineno or node.lineno)])
    return out


def _is_mode(stmt: ast.If, lines: list[str]) -> bool:
    """Report whether this `if` is a MODE branch rather than the refusal's own early exit.

    ⚑⚑ THE FIRST CUT TREATED EVERY TOP-LEVEL `if` AS A MODE, AND THE CENSUS INFLATED. Every
    gate opens with `rc = check_argv(...)` then `if rc is not None: return rc` — a guard, not a
    mode — and counting it as a branch that "ignores" `--quiet` added a phantom row to almost
    every tool. The figure was wrong in the direction that manufactures work.

    ⚑ THE DISCRIMINATOR IS THAT A MODE BRANCH TESTS A FLAG. A guard tests a return code, so
    requiring a `--`-spelling in the test separates them without naming the guard's shape —
    which would break the moment a gate spelled its early exit differently.
    """
    head = lines[stmt.lineno - 1] if stmt.lineno <= len(lines) else ""
    return "--" in head


def _label(stmt: ast.If, lines: list[str]) -> str:
    """Return a branch's name — the first flag its test mentions, else its line."""
    head = lines[stmt.lineno - 1] if stmt.lineno <= len(lines) else ""
    for token in head.replace('"', " ").replace("'", " ").split():
        if token.startswith("--"):
            return token
    return f"line {stmt.lineno}"


def _without_declaration(rest: str, tree: ast.AST, src: str) -> str:
    """Return the default span with the refusal's own flag-set call removed.

    ⚑⚑⚑ THE DECLARATION IS NOT A READ, AND CONFLATING THEM MAKES `PHANTOM` UNREACHABLE. Every flag
    is spelled once in `check_argv(argv, {"--a", "--b"})`, and that call sits in `main` — so it is
    inside the `<default>` span. A flag no branch dispatches on still matches its own declaring
    line, `readers` is never empty, and the census reports every phantom as PARTIAL.

    ⚑⚑ THE SPAN IS CUT BY THE CALL'S OWN LINE RANGE, NOT BY MATCHING FLAG TEXT. Removing each
    spelling wherever it appeared would also delete a genuine read that happens to share the line,
    which is the over-correction that turns a mislabel into a false PHANTOM.
    """
    lines = src.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else None
        if name != REFUSAL or not node.end_lineno:
            continue
        span = "\n".join(lines[node.lineno - 1 : node.end_lineno])
        if span:
            rest = rest.replace(span, "")
    return rest


def read_tool(path: Path, label: str) -> Tool | None:
    """Return one tool's flag ownership, or None when it declares no flag set."""
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return None
    names = declared(tree)
    if not names:
        return None

    spans = branches(tree, src)
    # ⚑ THE DEFAULT SPAN CONTAINS EVERY OTHER, so a flag read only inside a mode branch would
    # also read as read-by-default. Subtracting the mode spans is what keeps `<default>` an
    # honest branch rather than a superset that reads everything.
    modes = {k: v for k, v in spans.items() if k != "<default>"}
    rest = spans.get("<default>", "")
    for body in modes.values():
        rest = rest.replace(body, "")
    # ⚑⚑ THE FINDING WAS RIGHT AND THE CAUSE I RECORDED WAS WRONG. gate-G314 says the default span
    # still contained the MODE spans. It does not — they are subtracted directly above. The
    # uncounted text was the DECLARATION, which no subtraction touched. A cause diagnosed by
    # reasoning rather than by reading, inside the census built to stop exactly that, and caught
    # only when a fixture forced the state where it must fail.
    rest = _without_declaration(rest, tree, src)
    spans = {**modes, "<default>": rest}

    every = tuple(sorted(spans))
    flags = tuple(
        Flag(name, tuple(b for b, body in sorted(spans.items()) if name in body), every)
        for name in names
        if name not in UNIVERSAL_BY_CONSTRUCTION
    )
    return Tool(label, flags)


class Census(NamedTuple):
    """The flag-ownership population, with the denominator that makes a zero readable."""

    tools: tuple[Tool, ...]
    scanned: int

    def lines(self) -> list[str]:
        """Return the report: every tool with a partial flag, then the denominator."""
        out: list[str] = []
        for tool in self.tools:
            if tool.partial():
                out.append(tool.path)
                out.extend(tool.lines())
                out.append("")
        partial = sum(len(t.partial()) for t in self.tools)
        out.append(
            f"{partial} partial flag(s) over {len(self.tools)} declaring tool(s), "
            f"{self.scanned} file(s) scanned"
        )
        # ⚑⚑ A PARTIAL FLAG IS A QUESTION, NOT A DELETION ORDER. Whether wiring it is worth
        # doing depends on what the unreading mode is FOR — a one-line mode has nothing to
        # quieten — so this reports and does not refuse.
        out.append(
            "⚑ PARTIAL is a QUESTION — a flag that works on one mode and is silently "
            "ignored on another — never a verdict that the gate is broken."
        )
        if not self.scanned:
            out.append("⚑ NOTHING WAS SCANNED — this zero is a fact about the invocation.")
        return out


def census(root: Path) -> Census:
    """Return the flag-ownership census over every tool under `root` declaring a flag set."""
    found: list[Tool] = []
    paths = sorted(root.rglob("*.py")) if root.is_dir() else [root]
    for path in paths:
        tool = read_tool(path, str(path))
        if tool is not None:
            found.append(tool)
    return Census(tuple(found), len(paths))


def run(argv: list[str]) -> int:
    """Print the ownership census over the named root, or the usage."""
    if not argv or argv[0] != MODE:
        print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
        print(
            f"    flag_ownership.py {MODE} <root>   "  # noqa: T201
            f"# which declared flags each mode actually reads"
        )
        return USAGE_EXIT
    found = census(Path(argv[1]) if len(argv) > 1 else Path("scripts"))
    for line in found.lines():
        print(line)  # noqa: T201 - this module IS the report
    if not found.scanned:
        return USAGE_EXIT
    return 1 if any(t.partial() for t in found.tools) else 0


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
