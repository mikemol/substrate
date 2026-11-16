#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What the corpus walk did NOT look at (Ⓝ72c ⟡state-the-walk).

⚑⚑⚑ "1181 FILES" IS A NUMBER, NOT A SCOPE — AND THE DIFFERENCE WAS MEASURED, NOT ANTICIPATED.
`file_mode.py` reported `0 disagreement(s) in 1181 file(s) scanned`; `ruff --select
EXE001,EXE002 .` run beside it reported **1 error**, `.claude/agents/findings.py`. Both readings
were honest. The predicate agreed on every file BOTH instruments saw; the whole difference is
that ruff walks dotfile directories and `corpus.roots()` does not. A reader handed the census
line could not have derived that, because a denominator says how many files were visited and
NOTHING about which ones were reachable.

⚑⚑ THE TWO BOUNDARIES ARE DIFFERENT KINDS AND CONFLATING THEM IS THE WHOLE DEFECT.
`attr_reads.unresolved` / `module_importers.unresolved` / `file_mode.unresolved` name what the
PREDICATE could not decide about a file it HELD — a dynamic import, an unreadable file, the git
index mode. That discipline is established and works. Nothing names what the POPULATION never
handed the predicate at all. An unresolved shape is a file in the denominator that the reader
could not answer for; an unwalked tree is a file that never entered the denominator, so it
cannot appear as a caveat about a file — there is no file to caveat.

⚑ SO A ZERO HAS TWO WAYS TO BE A FACT ABOUT THE INSTRUMENT, AND ONLY ONE HAD A READER. This
repo already records `census-green-is-a-fact-about-the-census` and `report presence, never
absence`; `unresolved` paid down the predicate half. This is the population half, and it is the
half the `fix_exe_bit` incident recorded in `file_mode`'s own docstring — *"its population is
`_TREES = ("scripts", "scratch", "jea")`, `substrate/` is not in it, so the tool reported `no
mismatches` truthfully and the tree had four"* — diagnosed there as a fact about SCOPE, with the
remedy written as prose and never as a reader.

⚑⚑ THE EXCLUSIONS ARE DERIVED FROM `corpus`, NEVER RESTATED. The vocabulary lives in
`corpus.roots()` and `corpus.excluded()`; a second copy here would be the `MEM_CAP` shape — a
figure restated beside its authority, drifting silently the first time the authority moves. This
module walks the root and asks `corpus` which entries it would have taken, so the answer is
correct BY CONSTRUCTION rather than by a list somebody maintains.

⚑⚑⚑ AND THE ROOT-LEVEL `.py` FILES ARE THE FINDING NOBODY WAS LOOKING FOR. `corpus.roots()`
yields DIRECTORIES (`d.is_dir()`), and `py_files` walks those roots — so a `.py` file sitting at
the repo root is in no root at all and is invisible to every census built on this walk. Measured:
`applied_grammar.py`, `s4_structure.py` and `verify_applied_grammar.py` are in the tree and in NO
census. That is not an excluded tree a reader could have guessed at; it is a hole with no name,
and it took enumerating the root to see it. A scope reader that listed only the skipped
DIRECTORIES would have reported a clean scope over it.

⚑ THIS NAMES THE BOUNDARY; IT DOES NOT MOVE IT. Widening the corpus is a separate decision with
consumers — every ratchet baseline is keyed on the current population, so admitting a tree mints
new keys in the zero-tolerance censuses at once. The honest first move is to make the bound
READABLE — the same order `unresolved` took, and the same reason `file_mode` declares the git
index mode rather than growing a second responsibility to read it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus

# The three ways an entry at the repo root fails to enter the population. ⚑ EACH IS A DISTINCT
# NEXT ACTION, which is why they are not one "skipped" bucket: a dotfile tree may hold real tools
# (it did — `.claude/agents/findings.py`), a declared skip is policy, and a loose file at the root
# is an unnamed HOLE rather than a decision anybody made.
DOTFILE, DECLARED, LOOSE_FILE = "dotfile-dir", "declared-skip", "root-level-file"

# ⚑ THE REASONS ARE PROSE, NOT CODES, BECAUSE THE OUTPUT IS THE INTERFACE. The acceptance for this
# item is that a reader can tell what was not looked at WITHOUT reading the source, so a bare
# `dotfile-dir .claude` would fail it — the reader would still have to come here to learn that a
# dotfile directory can hold ordinary Python.
_WHY = {
    DOTFILE: (
        "a dotfile directory — `corpus.roots()` drops every entry starting with `.`, and one "
        "of them holds real tools (`.claude/agents/`, measured as a live EXE001 this walk "
        "cannot see and ruff can)"
    ),
    DECLARED: (
        "named in `corpus.SKIP_DIRS` or excluded by `corpus.excluded()` — a deliberate "
        "exclusion, so a finding in here is out of scope by policy rather than by accident"
    ),
    LOOSE_FILE: (
        "a `.py` file at the repo ROOT — `corpus.roots()` yields DIRECTORIES only, so this "
        "file is under no root and enters NO census built on this walk"
    ),
}


@dataclass(frozen=True, slots=True)
class Skipped:
    """One thing at the repo root that the corpus walk never handed to a predicate."""

    name: str
    kind: str

    @property
    def why(self) -> str:
        """Return the reader-facing reason this entry is outside the population."""
        return _WHY[self.kind]


def _name_of(entry: Path) -> str:
    """Return a path's basename as a sort key.

    ⚑ NAMED, NOT A LAMBDA — an untyped lambda is an `Any` under this repo's type gate, which
    `file_mode._label` already records paying for.
    """
    return entry.name


def classify(entry: Path) -> str | None:
    """Return why `entry` is outside the corpus, or None when the walk takes it.

    ⚑ THE ORDER IS NOT ARBITRARY. A dotfile directory is ALSO not in `SKIP_DIRS`, and reporting
    it as a declared skip would credit a policy nobody wrote — the dotfile rule is a blanket
    `startswith(".")`, which is exactly why it swallowed a tree holding real tools.

    ⚑ THE DECLARED ARM ASKS `corpus.excluded`, WHICH IS THE PUBLIC CONTRACT. Its own docstring
    says so: *"PUBLIC, BECAUSE THE EXCLUSION RULE IS THE CONTRACT."* Restating `GENERATED_DIRS`
    or the bazel-link prefix here would be a second spelling of one rule.
    """
    if entry.is_dir():
        if entry.name.startswith("."):
            return DOTFILE
        if entry.name in corpus.SKIP_DIRS or corpus.excluded(Path(entry.name)):
            return DECLARED
        return None
    return LOOSE_FILE if entry.suffix == ".py" else None


def skipped(root: Path | None = None) -> tuple[Skipped, ...]:
    """Return every root entry the corpus walk excludes, with the reason it excludes it.

    ⚑ IT ASKS `corpus`, IT DOES NOT REIMPLEMENT IT. The taken set is `corpus.roots()`; anything
    at the root that is not in it and could have held Python is reported. A second copy of the
    exclusion vocabulary here would drift from the authority the moment the authority moved,
    which is the failure this repo has paid for by a factor of two in a memory cap.
    """
    where = root if root is not None else corpus.ROOT
    taken = frozenset(corpus.roots(where))
    out: list[Skipped] = []
    for entry in sorted(where.iterdir(), key=_name_of):
        if entry.name in taken:
            continue
        kind = classify(entry)
        if kind is not None:
            out.append(Skipped(name=entry.name, kind=kind))
    return tuple(out)


def unwalked_python(root: Path | None = None) -> tuple[str, ...]:
    """Return the `.py` files under the skipped entries — the population's actual shadow.

    ⚑⚑ A COUNT OF SKIPPED DIRECTORIES IS NOT A COUNT OF UNSEEN CODE, and reporting only the
    former would be the same collapse one level up. `docs/` being excluded is unremarkable if it
    holds no Python and is a real gap if it holds forty modules — and a reader cannot tell which
    from the directory name. This walks them, so the shadow is a number a reader can weigh
    against the denominator rather than a list they must go and check.

    ⚑ IT DOES NOT REUSE `corpus.py_files`, AND THAT IS DELIBERATE. That function applies
    `excluded()` to everything it walks, which is the very filter under examination here — using
    it would make this reader inherit the blind spot it exists to measure.
    """
    where = root if root is not None else corpus.ROOT
    out: list[str] = []
    for item in skipped(where):
        out.extend(shadow_of(item, where))
    return tuple(out)


def shadow_of(item: Skipped, root: Path | None = None) -> tuple[str, ...]:
    """Return the `.py` files ONE skipped entry hides.

    ⚑⚑ PER-ENTRY, BECAUSE A TOTAL CANNOT BE WEIGHED. `19 entries holding 7999 .py files` is
    dominated by `.venv` and `.mypy_cache` — vendored and generated, correctly excluded — and
    reading that total, a reader concludes the walk has an enormous blind spot when the
    actionable part of it is a handful of files in `.claude/` and `.githooks/`. The aggregate is
    the number that MISLEADS here; the per-entry split is the one that ranks.
    """
    where = root if root is not None else corpus.ROOT
    target = where / item.name
    if target.is_file():
        return (item.name,)
    return tuple(str(p.relative_to(where)) for p in sorted(target.rglob("*.py")) if p.is_file())


def render(root: Path | None = None) -> str:
    """Return the scope statement a census appends beneath its denominator.

    ⚑⚑ IT IS INDENTED AND FLAGGED LIKE `unresolved`, ON PURPOSE. The two are the same KIND of
    disclosure — a bound on what the number above means — and giving them one visual form is what
    lets a reader learn to look for the boundary once rather than per tool. They stay SEPARATE
    functions because they answer different questions; they share a shape because they serve one.

    ⚑⚑⚑ THE REASON IS PRINTED ONCE PER KIND, NOT ONCE PER ROW — AND THE FIRST CUT GOT THIS
    WRONG IN A WAY WORTH RECORDING. Repeating the reason on every row put the sentence *"one of
    them holds real tools (`.claude/agents/`)"* beside `.git`, `.venv` and `.mypy_cache`, where
    it is simply false. A justification that travels with a KIND becomes a claim about each
    MEMBER when it is stapled to every one of them, and eleven rows of identical prose is also
    the fastest way to teach a reader to skip the block — which would defeat the disclosure.

    ⚑⚑ AND EACH ROW CARRIES ITS OWN SHADOW COUNT, WHICH IS WHAT MAKES THE BLOCK RANK — MEASURED,
    AND THE MEASUREMENT INVERTED THE HEADLINE. The aggregate reads `7999 .py file(s)`, which
    sounds like a catastrophic blind spot; the split says 7,995 of them are `.venv` (vendored,
    correctly out) and the entire actionable shadow is FOUR files — `.claude/agents/findings.py`
    plus three loose `.py` at the root. A reader given only the total would draw the opposite
    conclusion from a true number, which is the same collapse this module exists to name one
    level up.
    """
    items = skipped(root)
    if not items:
        return ""
    total = len(unwalked_python(root))
    head = (
        f"   ⚑ the walk did NOT look at {len(items)} root entr(ies), holding {total} "
        f".py file(s) — the denominator above is bounded by this:"
    )
    lines = [head]
    for kind in (DOTFILE, DECLARED, LOOSE_FILE):
        here = [i for i in items if i.kind == kind]
        if not here:
            continue
        lines.append(f"     {kind} — {_WHY[kind]}")
        lines.extend(f"       {len(shadow_of(i, root)):>6} .py  {i.name}" for i in here)
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Print what the corpus walk excludes, and the Python it therefore never reads."""
    if argv and argv != ["--files"]:
        sys.stderr.write("usage: walk_scope.py [--files]\n")
        return 2
    sys.stdout.write(render())
    if argv == ["--files"]:
        for path in unwalked_python():
            sys.stdout.write(f"  unwalked  {path}\n")
    return 0


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery, ⟡silent-nine). A bare `0`
# here would make this a roster member asserting NOTHING — reported `silent (0/0)` by the very
# runner it is meant to be read by.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import walk_scope_selftest

        sys.exit(walk_scope_selftest.selftest())
    sys.exit(main(sys.argv[1:]))
