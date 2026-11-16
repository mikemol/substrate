#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The shebang/executable-bit agreement census (Ⓝ72a ⟡shebang-permission-census).

⚑⚑⚑ THE PROPERTY IS NOT IN THE FILE'S TEXT, WHICH IS WHY EVERY INSTRUMENT THIS REPO OWNS IS
BLIND TO IT. `module_outline`, `module_size`, `suite_gap`, `attr_reads`, the type gate and
`pycheck_show` all read SOURCE; this defect lives in the filesystem's mode bits, one `stat` away
from every one of them and reachable by none. A reader that parses cannot see it at all — not
under-report it, not mis-key it: the datum is in a different plane.

⚑⚑ FOUR INSTANCES WERE FOUND IN ONE DAY, EACH BY AN EDIT FAILING FOR AN UNRELATED REASON.
`record_migrate_selftest.py`, `module_trim_selftest.py`, `attr_reads_selftest.py` and
`module_trim.py` each carried a `#!` with no `+x`, i.e. a latent ruff `EXE001`. Under the
zero-tolerance per-file gate that refuses the NEXT edit to the file — for a finding that has
nothing to do with the edit, was introduced by whoever created the file, and is invisible until
you try to write. The discovery channel was a confusing failure, four times; that is the
definition of a property with no reader.

⚑⚑⚑ AND THE REPAIRER ALREADY EXISTED WHILE THE READER DID NOT — WHICH IS THE WHOLE FINDING.
`scripts/fix_exe_bit.py` (⟡exe-sweep, 2026-08-30) sweeps BOTH rules and was written for exactly
this failure. Its population is `_TREES = ("scripts", "scratch", "jea")`. **`substrate/` is not
in it**, and every one of today's four instances is a `substrate/` file. So the tool reported
`no shebang/mode mismatches` truthfully and the tree had four — a fact about the SCOPE read as a
fact about the SUBSTRATE, in the tool built to prevent this class. A scoped instrument's clean
answer is bounded by its scope, and nothing in its output carried that bound.

⚑⚑⚑ AND THAT DIAGNOSIS WAS WRITTEN HERE AS PROSE, THEN REPRODUCED BY THIS VERY MODULE (Ⓝ72c
⟡state-the-walk). This census reported `0 disagreement(s) in 1181 file(s) scanned` while `ruff
--select EXE001,EXE002 .` run beside it reported ONE — `.claude/agents/findings.py`, in a
dotfile directory `corpus.roots()` drops and ruff walks. Same shape, one paragraph below its own
statement of it: the paragraph named SCOPE as the failure mode and the output still printed a
denominator with no scope. `substrate.walk_scope` is the reader that closes it, and `main`
prints it beneath the census — because a bound that lives in a docstring governs only the
readers who already suspect it.

⚑ BOTH DIRECTIONS ARE DEFECTS, AND BOTH ARE RULES ruff ACTUALLY ENFORCES — verified with
`ruff rule` rather than assumed, because asserting a rule code that does not exist would make
this census cite an authority nobody can follow:

  * `EXE001` shebang-not-executable — a `#!` line with no executable bit.
  * `EXE002` shebang-missing-executable-file — an executable bit with no `#!` line.

Both are Unix-only in ruff (the mode bits do not exist elsewhere), which is a property of the
CHECK, not of the tree, and is stated so a green run on a foreign filesystem is not read as a
clean tree.

⚑ THE SHEBANG TEST READS BYTES, NOT TEXT, AND NOT AN AST. A file that does not parse still has
mode bits and still has a first line, so a syntax error must not remove it from this population —
it is precisely a file somebody is about to edit. `ast` would drop it; `read_text` on a
mis-encoded file would raise. Bytes are the whole question.

⚑⚑⚑ AND "THE FIRST TWO BYTES" WAS THE WRONG QUESTION — CAUGHT BY A DECORRELATED CHECK, NOT BY
THIS SUITE. The first cut tested `read(2) == b"#!"`, which is what a shebang IS, and ruff does
not agree: it looks for a `#!` COMMENT LINE anywhere in the leading comment block, so
`scratch/strip_using.py` — whose shebang is stranded on LINE 6 behind four lines of `sys.path`
surgery — is an `EXE001` to ruff and read as "no shebang" here. This census then scored it
`exec-no-shebang` and the repair CLEARED a bit ruff wants SET: a wrong finding in the exact
direction that breaks a file, produced by a reader that was self-consistent and confidently
wrong. It was found only by running `ruff --select EXE001,EXE002` beside this tool and comparing.

⚑⚑ THE LESSON IS THE CONTRACT, NOT THE OFF-BY-FIVE-LINES. This module PREDICTS a linter's
finding, so the linter's definition is the specification and any independent re-derivation of it
is a second definition that will drift. `_LOOKAHEAD` below scans the leading lines the way ruff
does; the cross-check against ruff is what keeps the two honest, and it belongs in the suite as
much as any fixture. ⚑ Two instruments agreeing is not coverage — but two instruments DISAGREEING
is a finding, and this one was. TWICE: once on the predicate (the line-6 shebang) and once on
the population (the dotfile directory), which are the two independent ways this census can be
bounded and are now both disclosed.

⚑ THIS IS THE READER; `fix_exe_bit` IS THE WRITER, AND THEY ARE DELIBERATELY NOT MERGED. That
tool derives its population from ruff itself, which is the right authority for a REPAIR — it
cannot drift from the rule it pays down. This module answers the question WITHOUT invoking ruff,
which is what lets it run over the whole corpus, name what it cannot see, and be imported by
another reader. Two instruments, one rule, different failure modes: use both.

⚑ WHAT THIS READER CANNOT SEE IS NAMED, NOT COUNTED AS ZERO (`unresolved`) — the discipline
`attr_reads.unresolved` established and the thing a promoted reader keeps failing to inherit.
"""

from __future__ import annotations

import os
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.corpus import tree_root

from substrate import corpus, walk_scope

if TYPE_CHECKING:
    from collections.abc import Iterable

# The two disagreements, named once. ⚑ THE READER, THE RENDER AND THE CASES CITE THESE rather
# than respelling the strings — and each carries the ruff rule it is a latent instance of, so a
# row is actionable without a second lookup.
SHEBANG_NO_EXEC, EXEC_NO_SHEBANG = "shebang-no-exec", "exec-no-shebang"

# ⚑ VERIFIED AGAINST `ruff rule <code>`, NOT RECALLED. EXE002 was checked before this module
# asserted it exists; a fabricated rule code is a citation that cannot be followed.
RULE = {SHEBANG_NO_EXEC: "EXE001", EXEC_NO_SHEBANG: "EXE002"}

# The two bytes that make a shebang. Read as BYTES so an undecodable file still answers.
SHEBANG = b"#!"

# ⚑⚑ HOW FAR IN A SHEBANG LINE MAY SIT. ruff finds a `#!` comment line anywhere in the leading
# comment block, not only at offset 0 — MEASURED against `scratch/strip_using.py`, whose shebang
# is on line 6 and which this reader originally scored as the OPPOSITE finding. A bounded
# lookahead is what makes the two agree without re-implementing ruff's tokenizer; it is generous
# enough for every real instance and cannot turn a `#!` deep in a docstring into a finding.
_LOOKAHEAD = 16

# The mode bits ruff itself tests: "permissions mode intersects with 0o111".
EXEC_BITS = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

# Shapes this reader cannot resolve from the worktree alone; reported as themselves, never
# folded into a zero. ⚑ EACH IS A SHAPE THAT COULD HIDE A DISAGREEMENT, not a caveat.
INDEX_MODE, UNREADABLE, NO_PERM_BITS = "git-index-mode", "unreadable-file", "no-permission-bits"

# ⚑⚑ THE INDEX MODE IS A SECOND, INDEPENDENT COPY OF THIS BIT — AND IT IS THE ONE THAT TRAVELS.
# `chmod +x` leaves git's index at `100644` until the change is staged, so a worktree this reader
# calls clean can still ship the defect to every other checkout. It is DECLARED here rather than
# READ because reading it needs a subprocess, and this repo grants `S603` only per RESPONSIBILITY:
# a git read is a second responsibility, and `pyproject.toml`'s own entry for `collapse_check.py`
# already names the move that would be required — *"IF A SECOND GIT-READING TOOL APPEARS, THAT is
# the extraction to make: one module owning 'what does git say about the worktree'."* Declaring
# the blind spot is honest; growing a second responsibility here to close it is not.
_INDEX_NOTE = (
    "the git INDEX mode is not read here — a staged `100644` on a file this reader "
    "calls executable still ships the defect (needs the git-read extraction)"
)


@dataclass(frozen=True, slots=True)
class Entry:
    """One file's two independent facts: does it start with `#!`, is it executable."""

    path: str
    shebang: bool
    executable: bool

    @property
    def kind(self) -> str | None:
        """Return the disagreement this file exhibits, or None when the two agree.

        ⚑ AGREEMENT IS EITHER-BOTH-OR-NEITHER. A plain library module with no `#!` and no `+x`
        is as correct as a script with both; a census reporting only the second as healthy would
        name most of the tree as defective and be ignored accordingly.
        """
        if self.shebang and not self.executable:
            return SHEBANG_NO_EXEC
        if self.executable and not self.shebang:
            return EXEC_NO_SHEBANG
        return None

    @property
    def rule(self) -> str | None:
        """Return the ruff rule this file is a latent instance of, or None."""
        kind = self.kind
        return RULE[kind] if kind is not None else None


def has_shebang(path: Path) -> bool:
    """Report whether `path` carries a `#!` line ruff would see, reading BYTES.

    ⚑ AN UNPARSEABLE OR MIS-ENCODED FILE STILL HAS MODE BITS AND STILL HAS LINES. Routing this
    through `ast` or `read_text` would drop exactly the files most likely to be edited next,
    which is the population this census exists to protect.

    ⚑⚑ NOT JUST LINE 1 — THAT ASSUMPTION PRODUCED A WRONG REPAIR. ruff scans the leading comment
    block, so a shebang stranded behind a few statements still fires `EXE001`. Scanning
    `_LOOKAHEAD` lines matches it on every measured instance; scanning only the first inverted the
    finding on `scratch/strip_using.py` and cleared a bit that should have been set.
    """
    try:
        with path.open("rb") as fh:
            return any(
                line.lstrip().startswith(SHEBANG)
                for _, line in zip(range(_LOOKAHEAD), fh, strict=False)
            )
    except OSError:
        return False


def is_executable(path: Path) -> bool:
    """Report whether any of `path`'s executable bits are set.

    ⚑ `os.access(X_OK)` IS THE WRONG TEST AND WOULD HAVE ANSWERED DIFFERENTLY. It asks whether
    THIS process may execute the file — it consults the caller's uid and returns True for root
    on a file with no `+x` at all. ruff tests the MODE, so this tests the mode.
    """
    try:
        return bool(path.stat().st_mode & EXEC_BITS)
    except OSError:
        return False


def _label(entry: Entry) -> str:
    """Return an entry's sort key. ⚑ NAMED, NOT A LAMBDA — an untyped lambda is an `Any`."""
    return entry.path


def entries(files: Iterable[tuple[Path, str]]) -> tuple[Entry, ...]:
    """Return one `Entry` per file — the whole population, agreeing and disagreeing alike.

    ⚑ THE DENOMINATOR IS PART OF THE ANSWER, so the healthy files are carried rather than
    filtered here. A reader handed only the offenders cannot tell a clean tree from an unrun
    scan, which is the collapse this whole item is about.
    """
    return tuple(
        sorted(
            (
                Entry(path=label, shebang=has_shebang(path), executable=is_executable(path))
                for path, label in files
            ),
            key=_label,
        )
    )


def offenders(found: Iterable[Entry]) -> tuple[Entry, ...]:
    """Return only the entries whose shebang and mode bit disagree."""
    return tuple(e for e in found if e.kind is not None)


def unresolved(found: Iterable[Entry], root: Path | None = None) -> tuple[str, ...]:
    """Return the shapes that could hide a disagreement this reader cannot see.

    ⚑⚑ THIS IS THE HALF THAT MAKES A ZERO HONEST, and it is the half a promoted reader keeps
    dropping: each promotion inherits the QUESTION and leaves the BOUNDARY behind, because the
    origin recorded only its symptom. A count alone cannot separate *none* from *could not
    look*, and this repo deletes on zeros.

    ⚑⚑ AND IT IS ONLY THE PREDICATE HALF OF THE BOUNDARY. Everything named here is a shape of a
    file this reader HELD and could not decide. What it never received at all — a whole tree the
    walk does not enter — cannot appear as a caveat about a file, because there is no file to
    caveat. `substrate.walk_scope` answers that half, and `main` prints both.

    Three shapes are named:
      * `git-index-mode` — always, unconditionally. The staged mode is a second copy of this bit
        that this reader does not read, so it can disagree with a clean worktree silently.
      * `unreadable-file` — the first bytes could not be read, so the shebang answer DEFAULTED to
        False and the file may be a `shebang-no-exec` this census scored as healthy.
      * `no-permission-bits` — nothing in the population is executable at all, which on a
        filesystem that does not carry mode bits is indistinguishable from a tree of libraries.
    """
    where = root if root is not None else corpus.ROOT
    rows = tuple(found)
    out = [f"{INDEX_MODE}: {_INDEX_NOTE}"]
    out.extend(
        f"{UNREADABLE}: {e.path} could not be read; its shebang answer defaulted"
        for e in rows
        if (where / e.path).is_file() and not os.access(where / e.path, os.R_OK)
    )
    if rows and not any(e.executable for e in rows):
        out.append(
            f"{NO_PERM_BITS}: nothing in {len(rows)} file(s) is executable — a filesystem "
            f"without mode bits reads identically to a tree with no scripts"
        )
    return tuple(sorted(set(out)))


def population(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs.

    ⚑⚑ THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G252 / gate-G257).
    `corpus.resolve_root` resolves the caller's CWD FIRST — deliberately, so a peer running this
    from their own tree gets THEIR files — while `Path.relative_to` measured against SUBSTRATE's
    root, so the census died on its first foreign row. `tree_root.of(where).label` carries one root
    and does both, so the tree that was walked is the tree that labels.
    """
    where = root if root is not None else corpus.ROOT
    tree = tree_root.of(where)
    return tuple((Path(p), tree.label(p)) for p in corpus.py_files(root=where))


def render(found: tuple[Entry, ...], blind: tuple[str, ...] = ()) -> str:
    """Return the census — one line per disagreement, the denominator, and what stayed invisible.

    ⚑⚑ THE DENOMINATOR IS PRINTED EVEN WHEN THE ANSWER IS ZERO. `0 disagreements` and
    `0 of 1158 file(s)` are the same finding; only the second lets a reader see the scan ran.

    ⚑ IT REPORTS ON THE POPULATION IT WAS GIVEN AND MAKES NO CLAIM ABOUT WHICH ONE THAT IS. The
    walk's own boundary is the CALLER's disclosure — see `main` — because this function is driven
    by cases over fixture populations and must stay answerable about any of them.
    """
    bad = offenders(found)
    lines = [f"  {e.kind:<16} {e.rule}  {e.path}" for e in bad]
    lines.append(f"file-mode: {len(bad)} disagreement(s) in {len(found)} file(s) scanned")
    if blind:
        lines.append(
            f"   ⚑ {len(blind)} shape(s) this reader CANNOT resolve — a zero above is "
            f"not yet an absence:"
        )
        lines.extend(f"     {b}" for b in blind)
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Print the shebang/executable-bit census for the corpus, and the walk's own bound.

    ⚑⚑⚑ THE SCOPE STATEMENT IS APPENDED HERE, NOT INSIDE `render` — AND THE SPLIT IS THE POINT.
    `render` takes the population it was GIVEN and reports on it; it is driven by cases with
    fixture entries and must stay answerable about any population. The walk's boundary is a fact
    about the DEFAULT corpus this `main` chose, so it is the caller's disclosure to make. Folding
    it into `render` would make every fixture-driven case assert something about the real repo.

    ⚑⚑ AND IT IS THE POPULATION HALF OF A BOUND WHOSE PREDICATE HALF WAS ALREADY HERE.
    `unresolved` names what this reader could not DECIDE about a file it held; `walk_scope` names
    what it was never HANDED. Both print, because a zero needs both to be an absence — measured:
    this census read `0 disagreement(s) in 1181 file(s)` while ruff, walking dotfile directories,
    read one real EXE001 in `.claude/agents/findings.py`.
    """
    if argv:
        sys.stderr.write("usage: file_mode.py\n")
        return 2
    found = entries(population())
    sys.stdout.write(render(found, unresolved(found)))
    sys.stdout.write(walk_scope.render())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
