# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The two `pycodemod` modes that returned FALSE ZEROS, and the readers that replaced them.

⚑⚑⚑ WHY THIS MODULE EXISTS RATHER THAN A FIX IN THE TOOL. `scratch/pycodemod.py` carried
2145 ruff/mypy findings, and the per-file `pycheck` gate is ZERO-TOLERANCE with no
partial-credit path: any edit that leaves the file dirty is refused AND the file is
reverted, so an edit repairing one line was refused for the other 2144. Two of its modes
could not be fixed in place. The gate's own refusal text names the route:

    "Extract the one concern you need into a NEW module, written clean in one pass,
     and let the next consumer import that instead."

That is this file: the REFUSAL and its redirect, extracted so it can be written clean and
so the judgement lives in a program rather than in a tool nobody can edit.

⚑ THE TWO MODES — REPRODUCED AGAINST A POSITIVE CONTROL, which is what makes them DEFECTS
rather than absences. A census that reports 0 because its predicate cannot match is a fact
about the METHOD reported as a fact about the SUBSTRATE, and this repo DELETES on a zero.

  `--attr <Recv>.<leaf>`  documented, never implemented. `_attr_reads_one` special-cased
      only `endswith(".*")`; every other dotted operand fell to the leaf branch and was
      compared `node.attr.value == "corpus.ROOT"` — a string no attribute name can equal.
          corpus.ROOT reads       frozen origin 0    promoted reader 121 in 66 files
      SUPERSEDED BY `substrate/attr_reads.py`, which also declares its boundaries.

  `--importers <module>`  keyed on `node.module.split(".")[0]`, so inside a package every
      importer spells the dependency as the PACKAGE and any submodule query answered 0.
          substrate.corpus imports  frozen origin 0    promoted reader 68 in 68 files
      SUPERSEDED BY `substrate/module_importers.py`, which normalises path, dotted and
      bare operands and NAMES the four dynamic-import shapes it cannot resolve.

⚑ A SUPERSEDED READER THAT STILL RESPONDS IS WORSE THAN A DELETED ONE. It answers whoever
reaches the old spelling first, wrongly. So the contract here is REFUSE WITH A REDIRECT,
never answer — the `census-green-is-a-fact-about-the-census` discipline of making the
refusal name its successor.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

#: The repository root — one level above `substrate/`.
ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class Supersession:
    """One retired mode, the reader that replaced it, and the measurement that retired it.

    ⚑ A RECORD, NOT A TUPLE (⟡symbolic-reference-only). The `measured` field is what makes
    the retirement falsifiable: a reader can re-run that exact comparison and see the
    origin's zero against the successor's count, rather than trusting this docstring.
    """

    flag: str
    successor: str
    why: str
    measured: str


#: The retired modes, keyed by the flag a caller still reaches for.
#: ⚑ A TABLE, NOT TWO HAND-WRITTEN BRANCHES: the refusal text is one shape, so a third
#: supersession is a row rather than a third branch that drifts from the first two.
SUPERSEDED: dict[str, Supersession] = {
    "--attr": Supersession(
        flag="--attr",
        successor="substrate/attr_reads.py",
        why=(
            "`--attr <Recv>.<leaf>` was DOCUMENTED BUT NEVER IMPLEMENTED: only `.*` "
            "was special-cased, so a dotted operand was compared against a bare "
            "attribute name and could never match."
        ),
        measured=("corpus.ROOT: the origin said 0; the successor finds 121 in 66 files."),
    ),
    "--importers": Supersession(
        flag="--importers",
        successor="substrate/module_importers.py",
        why=(
            "`--importers` keyed on the FIRST dotted component, so inside a package "
            "every importer spells the dependency as the package and a submodule "
            "query answered 0 for a module with many importers."
        ),
        measured=("substrate.corpus: the origin said 0; the successor finds 68 in 68 files."),
    ),
}

#: The POSIX end-of-flags marker. Everything after it is an operand, never a mode.
END_OF_FLAGS = "--"

#: The file stems that NAME the frozen origin tool, however it is reached.
#:
#: ⚑ A STEM, NOT A PATH. The origin is invoked as `python3 scratch/pycodemod.py`, as
#: `./scratch/pycodemod.py`, and from other checkouts by absolute path; keying on any one
#: spelling is the `census-keyed-on-one-spelling` defect, which this repo has already paid
#: for twice. The stem is what every spelling shares.
ORIGIN_STEMS: frozenset[str] = frozenset({"pycodemod"})


def names_origin(words: list[str]) -> bool:
    """Report whether `words` names the frozen origin tool.

    ⚑ THE SCRIPT PATH IS AN ARGUMENT, NOT THE PROGRAM. A command parser reports
    `python3 scratch/pycodemod.py --attr X` as the program `python3` with the script
    among its arguments, so a test against the program name alone sees nothing. The
    stem is looked for across the whole word list for that reason.
    """
    for word in words:
        if word == END_OF_FLAGS:
            return False
        if Path(word.strip("'\"")).stem in ORIGIN_STEMS:
            return True
    return False


def retired_in_command(words: list[str]) -> Supersession | None:
    """Return the retired mode this COMMAND invokes on the origin tool, or None.

    ⚑ BOTH HALVES ARE REQUIRED, AND THE SECOND IS THE HAZARD GUARD. A verdict keyed on
    the flag alone would refuse `attr_reads.py --attr` — the SUCCESSOR — and a verdict
    keyed on the tool alone would refuse `pycodemod --calls`, which WORKS. Worse, the
    gate that recommends this tool would then refuse it, turning every refusal it issues
    into a dead end. The conjunction is what keeps the recommendation live.
    """
    if not names_origin(words):
        return None
    return superseded_in(words)


def superseded_in(argv: list[str]) -> Supersession | None:
    """Return the retired mode named in `argv`, or None if none is.

    ⚑ IT STOPS AT `--`, because everything after the end-of-flags marker is an OPERAND.
    `--literal -- --attr` asks about the STRING `--attr` and must not be refused as an
    invocation of it — the same slice discipline the tool's `flagged_argv` records after
    `--literal -- --selftest` ran the suite instead of searching for the string.
    """
    for word in argv:
        if word == END_OF_FLAGS:
            return None
        found = SUPERSEDED.get(word)
        if found is not None:
            return found
    return None


def refusal(mode: Supersession) -> str:
    """Render the refusal a caller of a retired mode should see.

    ⚑⚑⚑ THE ROUTE NAMES THE DIRECTORY IT ASSUMES (gate-G381). A peer took this redirect from
    `~/github`, where the first path component is itself the repo directory, and reported both
    successors as one component short — `substrate/substrate/module_importers.py` reaches the
    file from there. Measured from the repo root, the spelling as written resolves and runs.
    NEITHER SPELLING IS WRONG: they differ only in the reader's position.

    ⚑⚑ SO A BARE RELATIVE ROUTE IS A CLAIM ABOUT THE READER REPORTED AS A CLAIM ABOUT THE
    ARTEFACT, and the cost is specific rather than cosmetic. A block WITH a route beats a block
    without one; a block with a route that fails from where the reader stands is worse than
    both, because they now have a failure to debug instead of a decision to make. The peer's
    proposed repair — rewrite the four literals — would have INVERTED it, breaking the route for
    every reader following the convention and reddening this module's own selftest.

    ⚑ NAMING THE ROOT IS THE FIX FOR THE CLASS, NOT THE INSTANCE. The convention lives in tool
    docstrings rather than in CLAUDE.md — a literal census finds it in seven files, and
    `substrate/tree_root.py` owns the question programmatically where the rest state it in prose.
    `ROOT` is already resolved here, so the route can be taken from anywhere without the reader
    having to know which directory the relative spelling assumed.
    """
    return "\n".join(
        (
            f"pycodemod: {mode.flag} is RETIRED — it returned FALSE ZEROS.",
            f"  why:      {mode.why}",
            f"  measured: {mode.measured}",
            f"  use:      python3 {mode.successor} <operand>",
            f"     from:  {ROOT}   (the route is REPO-RELATIVE — from elsewhere, spell it absolute)",
            "  ⚑ REFUSING rather than answering. A superseded reader that still",
            "     RESPONDS is worse than a deleted one: it answers whoever reaches",
            "     the old spelling first, wrongly — and this repo DELETES on a zero.",
        )
    )


def refuse(mode: Supersession) -> int:
    """Print the refusal and return the non-zero status a retired mode must exit with."""
    sys.stdout.write(refusal(mode) + "\n")
    return 2


# ⚑ THE CASES LIVE IN `pycodemod_retired_selftest.py`, NOT HERE. `suite_gap` reads a
# `--selftest` dispatch in a module as an owed suite; the arms are the suite's, so this
# module carries none and the reader that checks it is a separate file.
