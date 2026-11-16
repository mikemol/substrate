# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Emit the root makefile's gate section FROM the declared roster.

⚑⚑⚑ THIS IS WHAT MAKES THE EXTRACTION LOAD-BEARING RATHER THAN PARALLEL. `build_targets`
declares the gates once; until something EMITS from it, the generator's three hand-maintained
lists are still the authority and the roster is a second opinion nobody consults — a
built-then-orphaned rung. The emitter is the half that retires the restatement.

⚑⚑ AND THE TWO ORDERS IN THE ORIGIN ALREADY DISAGREE, which is the drift arriving on schedule.
`root_text` emits the recipe blocks starting with `check-makefiles`, while its `check:` aggregate
lists `check-defproof` first. Nothing reconciles them because nothing can: they are two literals.
Derived from one roster, the question does not arise.

⚑ THE SPLIT IS SYNTAX-VS-POLICY, AND THAT IS THE MIGRATION SEAM. Everything here is make
grammar — tab-prefixed recipes, `.PHONY`, prerequisite lists. Nothing here decides WHICH gates
exist or what they run; that is `build_targets`, which a bazel emitter reads unchanged while
this module is replaced wholesale.

⚑ A RECIPE LINE IS BUILT FROM ARGV, so the roster never carries shell text. Joining is this
module's job precisely because the joining rule is backend-specific.
"""

from __future__ import annotations

from substrate import build_targets

# make's recipe prefix. ⚑ A LITERAL TAB IS LOAD-BEARING IN MAKE — spaces are a syntax error, and
# naming it is what keeps an editor's whitespace policy from silently breaking the build.
TAB = "\t"

# The aggregate target every blocking gate hangs from.
CHECK = "check"

# What the aggregate prints when every gate passed.
CHECK_DONE = "all invariant checks passed."


def recipe(target: build_targets.Target) -> list[str]:
    """Render one target: its rationale comment, its name, and its argv as a recipe line.

    ⚑ THE `@` PREFIX SUPPRESSES make's ECHO, so a passing gate is silent and a failing one
    shows only its own output. A build whose every gate narrates itself buries the one that
    matters.
    """
    out = [f"# {line}" for line in target.why]
    out.append(f"{target.name}:")
    out.append(f"{TAB}@{' '.join(target.command)}")
    return out


def phony_line(extra: tuple[str, ...] = ()) -> str:
    """Render the `.PHONY` declaration covering every gate plus `extra` targets.

    ⚑ THE GATES COME FROM THE ROSTER AND THE REST IS PASSED IN. A phony list that tried to own
    both would need to know about `all`/`clean`/`catalog`, which are the emitter's business and
    not the gate policy's.
    """
    names = (*extra, CHECK, *build_targets.names(), build_targets.ADVISE)
    return f".PHONY: {' '.join(names)}"


def aggregate() -> list[str]:
    """Render the `check:` target that depends on every blocking gate.

    ⚑⚑ THE PREREQUISITE ORDER IS THE ROSTER ORDER, which is the whole point. The origin's
    aggregate and its recipe blocks listed the same gates in DIFFERENT orders — two literals
    that had already drifted — and a derived list cannot.
    """
    return [
        "# Aggregate invariant GATE (same checks the pre-commit hook runs). Blocking.",
        f"{CHECK}: {' '.join(build_targets.names())}",
        f"{TAB}@echo '{CHECK_DONE}'",
    ]


def gate_section() -> list[str]:
    """Render the aggregate plus every gate recipe, in roster order."""
    out = aggregate()
    for target in build_targets.CHECKS:
        out.extend(recipe(target))
    out.extend(recipe(build_targets.ADVISORY))
    return out


def text() -> str:
    """Render the gate section as makefile text."""
    return "\n".join(gate_section()) + "\n"


def phony_text() -> str:
    """Render the `.PHONY` line for the standard root targets.

    ⚑ A NAMED FUNCTION RATHER THAN A LAMBDA IN THE DISPATCH TABLE. A bare lambda is untyped, so
    mypy reads the route as a call into unknown and the zero-tolerance gate refuses — correctly,
    since an untyped route degrades every caller's return type to `Any`.
    """
    return phony_line(("all", "clean")) + "\n"


USAGE = """\
make_emit.py — emit the root makefile's gate section from the declared roster.

  make_emit.py --text       the gate section as makefile text
  make_emit.py --phony      the .PHONY line the gates require
  make_emit.py --selftest   the cases

⚑ THE ROSTER IS `substrate/build_targets.py`, and it is the only place a gate is declared.
  This module owns make GRAMMAR — tabs, prerequisites, `.PHONY` — and decides nothing about
  which gates exist. A bazel emitter reads the same roster and replaces this wholesale.
"""

# ⚑ A DISPATCH TABLE, matching the other readers in this package.
#
# ⚑⚑ AND THE FIRST CUT OF THIS MODULE HAD NO CLI AT ALL — writing it to a file produced an EMPTY
# file and exit 0. That is the silent-success shape recorded as gate-F21, reproduced here by
# omission ONE TURN after fixing it elsewhere: a module written as a library reads as a working
# tool right up until someone runs it.
MODES = {
    "--text": text,
    "--phony": phony_text,
}


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code."""
    import sys  # noqa: PLC0415 — kept local so importing this module costs nothing

    if "--selftest" in argv:
        from substrate import make_emit_selftest  # noqa: PLC0415

        return 0 if make_emit_selftest.selftest() else 1

    flags = [a for a in argv[1:] if a.startswith("--")]
    mode = MODES.get(flags[0]) if flags else None
    if mode is None:
        sys.stdout.write(USAGE)
        return 2

    sys.stdout.write(mode())
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
