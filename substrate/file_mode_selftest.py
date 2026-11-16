#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.file_mode` — the four mode/shebang combinations, and the boundary.

⚑⚑⚑ EVERY ARM PINS THE PROPERTY, NEVER A NAMED FILE. Arms naming a specific victim expired four
times in one day here, one of them twice in two turns — `module_trim.py` was `+x`'d between the
case being written and the case being run, so an assertion about that file measured the repair
rather than the reader. Each fixture below is BUILT in a temp tree with the mode it is testing,
so the case is about the predicate and stays true whatever the live tree does.

⚑⚑ EVERY POPULATION ARM HAS A DISCRIMINATOR. A predicate that always said `shebang-no-exec`
would pass every positive case here on its own; a predicate that always said None would pass
every negative one. Each direction is therefore paired with its opposite over the SAME reader,
so the arms fail a constant predicate rather than merely describing one.

⚑ THE FOUR COMBINATIONS ARE THE WHOLE TRUTH TABLE, and enumerating them is what makes the
`kind` property falsifiable: two disagree (one per ruff rule) and two agree (a script with both,
a library with neither). A census that flagged three of the four would name most of the tree.

⚑⚑⚑ AND THIS SUITE WAS GREEN 17/17 WHILE THE READER PRODUCED A WRONG REPAIR ON THE LIVE TREE.
Every fixture here was built by this suite, so every fixture agreed with the reader's own idea of
what a shebang is — first two bytes — and ruff's differs: it finds a `#!` line anywhere in the
leading block. `scratch/strip_using.py` (shebang on line 6) was therefore scored as the OPPOSITE
finding and its bit was cleared. **A suite whose fixtures encode the reader's assumption cannot
falsify that assumption**; only running `ruff --select EXE001,EXE002` beside the census did.
⚑ Two instruments agreeing is not coverage — two instruments DISAGREEING is the finding, and the
stranded/deep pair below is that disagreement turned into cases.

⚑ THE `unresolved` ARMS ARE THE ONES THAT MATTER MOST and are the easiest to write dishonestly.
`unresolved` returning a non-empty tuple proves nothing by itself; the arms below assert WHICH
shape is named, and one asserts a shape is ABSENT when its condition does not hold — otherwise a
function returning every string always would pass.
"""

from __future__ import annotations

import stat
import sys
import tempfile
from pathlib import Path

from substrate import file_mode

# ⚑ FIXTURE CONTENT IS IRRELEVANT EXCEPT FOR ITS FIRST TWO BYTES, and saying so in the constants
# keeps a later reader from "fixing" a fixture into a realistic module and changing what is
# tested. A shebang file and a non-shebang file, both otherwise identical.
_WITH_SHEBANG = "#!/usr/bin/env python3\nx = 1\n"
_NO_SHEBANG = "x = 1\n"

# ⚑ A FILE THAT DOES NOT PARSE. It still has mode bits and still has a first line, and it is
# exactly the file somebody is about to edit — so it must stay in the population.
_UNPARSEABLE = "#!/usr/bin/env python3\ndef broken(:\n"

# ⚑ A LATIN-1 BYTE SEQUENCE THAT IS NOT VALID UTF-8. `read_text` would raise on it; the byte
# read must not. Written as bytes, so the case tests decoding rather than describing it.
_UNDECODABLE = b"#!/usr/bin/env python3\n# \xff\xfe caf\xe9\nx = 1\n"

# ⚑⚑⚑ A SHEBANG STRANDED BEHIND STATEMENTS — the shape of `scratch/strip_using.py`, whose `#!`
# sits on LINE 6 behind four lines of `sys.path` surgery. ruff calls it EXE001; a first-two-bytes
# reader calls it "no shebang" and, seeing `+x`, reports the OPPOSITE finding. This fixture is
# here because that inversion produced a wrong REPAIR on the live tree before ruff caught it.
_STRANDED = "\n\nimport os\nimport sys\nsys.path.insert(0, '.')\n#!/usr/bin/env python3\nx = 1\n"

# ⚑ A `#!` FAR PAST THE LOOKAHEAD, inside a docstring — must NOT count. It is the discriminator
# for the stranded case: a reader that scanned the whole file would flag any module quoting a
# shebang in its documentation, which is most of the tooling in this repo.
_DEEP = "x = 1\n" * 40 + '"""\n#!/usr/bin/env python3\n"""\n'

_EXEC_MODE = 0o755
_PLAIN_MODE = 0o644

_TWO = 2
_FOUR = 4


def _entry(text: str | bytes, mode: int) -> file_mode.Entry:
    """Write one fixture with an explicit mode and read its `Entry` back."""
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "fixture.py"
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, encoding="utf-8")
        path.chmod(mode)
        got = file_mode.entries(((path, "fixture.py"),))
        return got[0]


def a_shebang_without_the_bit_is_the_latent_exe001(out: list[str]) -> int:
    """Check `#!` with no `+x` is reported as `shebang-no-exec` / EXE001.

    ⚑⚑⚑ THE MEASURED DEFECT. Four files in this package carried exactly this and each was
    discovered only by an unrelated edit being refused, because no instrument in the repo reads
    a mode bit. This is the arm that would have found them.
    """
    got = _entry(_WITH_SHEBANG, _PLAIN_MODE)
    if got.kind != file_mode.SHEBANG_NO_EXEC or got.rule != "EXE001":
        out.append(f"selftest: a shebang without the bit was not flagged: {got!r}")
        return 1
    return 0


def a_bit_without_a_shebang_is_the_latent_exe002(out: list[str]) -> int:
    """Check `+x` with no `#!` is reported as `exec-no-shebang` / EXE002.

    ⚑ THE OTHER DIRECTION IS A REAL RULE, VERIFIED WITH `ruff rule EXE002` BEFORE BEING
    ASSERTED — a census citing a rule code that does not exist points its reader nowhere. It
    is also the arm that DISCRIMINATES the one above: a reader that flagged every file as
    EXE001 would fail here.
    """
    got = _entry(_NO_SHEBANG, _EXEC_MODE)
    if got.kind != file_mode.EXEC_NO_SHEBANG or got.rule != "EXE002":
        out.append(f"selftest: an executable bit without a shebang was not flagged: {got!r}")
        return 1
    return 0


def a_script_with_both_agrees(out: list[str]) -> int:
    """Check `#!` WITH `+x` is not a finding.

    ⚑ THE DISCRIMINATOR FOR EXE001. A predicate that always returned `shebang-no-exec` passes
    the first arm and fails here, which is the only reason that arm means anything.
    """
    got = _entry(_WITH_SHEBANG, _EXEC_MODE)
    if got.kind is not None or got.rule is not None:
        out.append(f"selftest: a correct script was flagged: {got!r}")
        return 1
    return 0


def a_library_with_neither_agrees(out: list[str]) -> int:
    """Check no `#!` and no `+x` is not a finding.

    ⚑ THE DISCRIMINATOR FOR EXE002, and the arm that keeps the census USABLE. Most of this tree
    is import-only modules with neither; a reader flagging them would name ~1100 files and be
    ignored, which is the same outcome as reporting nothing.
    """
    got = _entry(_NO_SHEBANG, _PLAIN_MODE)
    if got.kind is not None:
        out.append(f"selftest: a plain library module was flagged: {got!r}")
        return 1
    return 0


def the_two_facts_are_read_independently(out: list[str]) -> int:
    """Check `shebang` and `executable` are separate observations, not one derived from the other.

    ⚑ THE FOUR COMBINATIONS MUST BE FOUR. A reader that derived the mode from the content — which
    is precisely what `hook_pycheck`'s tempfile does, and why the gate cannot see this class —
    would collapse the table to two rows and never report a disagreement at all.
    """
    seen = {
        (_entry(text, mode).shebang, _entry(text, mode).executable)
        for text in (_WITH_SHEBANG, _NO_SHEBANG)
        for mode in (_EXEC_MODE, _PLAIN_MODE)
    }
    if len(seen) != _FOUR:
        out.append(
            f"selftest: the two facts are not independent — {len(seen)} of 4 combos: "
            f"{sorted(seen)!r}"
        )
        return 1
    return 0


def an_unparseable_file_stays_in_the_population(out: list[str]) -> int:
    """Check a syntax error does not remove a file from the census.

    ⚑⚑ IT IS EXACTLY THE FILE SOMEBODY IS ABOUT TO EDIT, so dropping it would blind the census
    at the moment it is needed. Every other reader in this toolkit skips an unparseable file and
    is right to; this one must not, and that difference is the reason it reads bytes.
    """
    got = _entry(_UNPARSEABLE, _PLAIN_MODE)
    if got.kind != file_mode.SHEBANG_NO_EXEC:
        out.append(f"selftest: an unparseable file left the population: {got!r}")
        return 1
    return 0


def an_undecodable_file_still_answers(out: list[str]) -> int:
    """Check a file that is not valid UTF-8 still reports its shebang.

    ⚑ `read_text` WOULD RAISE AND `errors="replace"` WOULD BE A GUESS. The question is the first
    two BYTES, which have an answer regardless of the encoding of everything after them.
    """
    got = _entry(_UNDECODABLE, _PLAIN_MODE)
    if not got.shebang:
        out.append(f"selftest: an undecodable file lost its shebang: {got!r}")
        return 1
    return 0


def a_stranded_shebang_is_still_a_shebang(out: list[str]) -> int:
    """Check a `#!` behind a few statements is seen, as ruff sees it.

    ⚑⚑⚑ THE MEASURED INVERSION. `scratch/strip_using.py` carries its shebang on line 6; the first
    cut of this reader tested the first two bytes, called it "no shebang", saw `+x` and reported
    `exec-no-shebang` — so the repair CLEARED a bit ruff wants SET. A wrong finding in the
    direction that breaks a file, from a reader that was entirely self-consistent.
    """
    got = _entry(_STRANDED, _PLAIN_MODE)
    if not got.shebang or got.kind != file_mode.SHEBANG_NO_EXEC:
        out.append(f"selftest: a stranded shebang was missed: {got!r}")
        return 1
    return 0


def a_shebang_past_the_lookahead_is_not_one(out: list[str]) -> int:
    """Check a `#!` deep inside the file — e.g. quoted in a docstring — is NOT a shebang.

    ⚑⚑ THE DISCRIMINATOR FOR THE ARM ABOVE, and the reason the lookahead is BOUNDED. A reader
    that scanned the whole file would fix the stranded case by flagging every module that
    documents a shebang, which in this repo is most of the tooling — trading a rare wrong finding
    for a common one.
    """
    got = _entry(_DEEP, _PLAIN_MODE)
    if got.shebang or got.kind is not None:
        out.append(f"selftest: a docstring shebang was counted: {got!r}")
        return 1
    return 0


def only_the_owner_bit_is_enough(out: list[str]) -> int:
    """Check a group- or other-only executable bit counts as executable.

    ⚑ ruff TESTS `mode & 0o111`, SO THIS TESTS `mode & 0o111`. Reading only `S_IXUSR` would
    disagree with the linter on a file whose owner bit is clear — a census that is right about
    the rule it names and wrong about the finding the gate will produce.
    """
    got = _entry(_NO_SHEBANG, 0o645)
    if not got.executable or got.kind != file_mode.EXEC_NO_SHEBANG:
        out.append(f"selftest: a non-owner executable bit was not seen: {got!r}")
        return 1
    return 0


def offenders_drops_the_agreeing_files(out: list[str]) -> int:
    """Check `offenders` filters to disagreements while `entries` keeps everyone.

    ⚑ THE DENOMINATOR AND THE NUMERATOR COME FROM THE SAME SCAN. If `entries` filtered, a reader
    could not tell a clean tree from an unrun one — the collapse this whole module is about.
    """
    with tempfile.TemporaryDirectory() as where:
        pairs = []
        for name, text, mode in (
            ("bad.py", _WITH_SHEBANG, _PLAIN_MODE),
            ("good.py", _NO_SHEBANG, _PLAIN_MODE),
        ):
            path = Path(where) / name
            path.write_text(text, encoding="utf-8")
            path.chmod(mode)
            pairs.append((path, name))
        rows = file_mode.entries(pairs)
    if len(rows) != _TWO or len(file_mode.offenders(rows)) != 1:
        out.append(f"selftest: offenders/entries disagree on the population: {rows!r}")
        return 1
    return 0


def the_render_prints_its_denominator_on_zero(out: list[str]) -> int:
    """Check a clean census still names how many files were scanned.

    ⚑⚑ `0 disagreements` AND `0 OF 1159 FILES` ARE THE SAME FINDING and only the second lets a
    reader see the scan happened — the line that would have made `fix_exe_bit`'s truthful
    `no mismatches` legible as a statement about its three-tree scope.
    """
    text = file_mode.render((), ())
    if "in 0 file(s) scanned" not in text:
        out.append(f"selftest: an empty census omits its denominator:\n{text}")
        return 1
    return 0


def the_render_names_the_rule_for_each_row(out: list[str]) -> int:
    """Check a reported row carries its ruff code, so it is actionable without a second lookup."""
    rows = (file_mode.Entry(path="a.py", shebang=True, executable=False),)
    text = file_mode.render(rows, ())
    if "EXE001" not in text or "a.py" not in text:
        out.append(f"selftest: the render omits the rule or the path:\n{text}")
        return 1
    return 0


def the_index_boundary_is_always_declared(out: list[str]) -> int:
    """Check `unresolved` names the unread git index mode on every call.

    ⚑⚑ A ZERO MUST CARRY WHAT IT COULD NOT RESOLVE. The staged mode is a second copy of this bit
    and this reader does not read it, so a clean worktree can still ship the defect. That is
    UNCONDITIONALLY true, so it is unconditionally said — a boundary declared only sometimes is
    one a reader learns to skip.
    """
    got = file_mode.unresolved(())
    if not any(b.startswith(file_mode.INDEX_MODE) for b in got):
        out.append(f"selftest: the git-index boundary was not declared: {got!r}")
        return 1
    return 0


def the_no_perm_bits_shape_is_conditional(out: list[str]) -> int:
    """Check `no-permission-bits` is reported for an all-unexecutable population and NOT otherwise.

    ⚑⚑⚑ THE DISCRIMINATOR FOR `unresolved` ITSELF, and without it the whole boundary half is
    unfalsifiable: a function returning every shape name on every call would satisfy every other
    `unresolved` arm here. This one fails it, because it asserts a shape is ABSENT when its
    condition does not hold.
    """
    quiet = (file_mode.Entry(path="a.py", shebang=False, executable=False),)
    loud = (file_mode.Entry(path="a.py", shebang=True, executable=True),)
    saw_quiet = any(b.startswith(file_mode.NO_PERM_BITS) for b in file_mode.unresolved(quiet))
    saw_loud = any(b.startswith(file_mode.NO_PERM_BITS) for b in file_mode.unresolved(loud))
    if not saw_quiet or saw_loud:
        out.append(
            f"selftest: no-permission-bits is not conditional "
            f"(all-unexecutable={saw_quiet}, has-executable={saw_loud})"
        )
        return 1
    return 0


def the_render_carries_the_boundary_into_the_report(out: list[str]) -> int:
    """Check the unresolved shapes reach the printed census, not just the accessor.

    ⚑ A BOUNDARY THE CLI DOES NOT PRINT IS ONE NOBODY READS. `attr_reads` established the shape;
    the thing a promoted reader keeps dropping is not the function but its route to the reader.
    """
    text = file_mode.render((), ("git-index-mode: something",))
    if "CANNOT resolve" not in text or "git-index-mode" not in text:
        out.append(f"selftest: the render drops the boundary:\n{text}")
        return 1
    return 0


def the_rule_map_covers_every_kind(out: list[str]) -> int:
    """Check every disagreement this reader can report has a ruff code.

    ⚑ A `KeyError` IN `rule` WOULD BE A CRASH IN THE RENDER, not a missing row — and adding a
    third kind without its code is exactly how that would arrive.
    """
    kinds = {file_mode.SHEBANG_NO_EXEC, file_mode.EXEC_NO_SHEBANG}
    if set(file_mode.RULE) != kinds:
        out.append(f"selftest: RULE does not cover every kind: {file_mode.RULE!r}")
        return 1
    return 0


def a_missing_file_does_not_raise(out: list[str]) -> int:
    """Check a path that vanished between enumeration and stat is absorbed.

    ⚑ THE CENSUS WALKS A LIVE TREE, so a file can be deleted mid-scan. Raising would report
    nothing about the other 1158 — a far larger error than the one file it misses.
    """
    with tempfile.TemporaryDirectory() as where:
        gone = Path(where) / "gone.py"
        got = file_mode.entries(((gone, "gone.py"),))
    if len(got) != 1 or got[0].kind is not None:
        out.append(f"selftest: a missing file did not absorb cleanly: {got!r}")
        return 1
    return 0


def the_exec_bits_constant_is_ruffs(out: list[str]) -> int:
    """Check `EXEC_BITS` is exactly `0o111`, the mask ruff documents.

    ⚑ THE CONSTANT IS THE CONTRACT WITH THE LINTER. Any other mask makes this census disagree
    with the gate it predicts, in one direction or the other, silently.
    """
    if file_mode.EXEC_BITS != stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH:
        out.append(f"selftest: EXEC_BITS is not 0o111: {file_mode.EXEC_BITS:o}")
        return 1
    return 0


_ARMS = (
    a_shebang_without_the_bit_is_the_latent_exe001,
    a_bit_without_a_shebang_is_the_latent_exe002,
    a_script_with_both_agrees,
    a_library_with_neither_agrees,
    the_two_facts_are_read_independently,
    an_unparseable_file_stays_in_the_population,
    an_undecodable_file_still_answers,
    a_stranded_shebang_is_still_a_shebang,
    a_shebang_past_the_lookahead_is_not_one,
    only_the_owner_bit_is_enough,
    offenders_drops_the_agreeing_files,
    the_render_prints_its_denominator_on_zero,
    the_render_names_the_rule_for_each_row,
    the_index_boundary_is_always_declared,
    the_no_perm_bits_shape_is_conditional,
    the_render_carries_the_boundary_into_the_report,
    the_rule_map_covers_every_kind,
    a_missing_file_does_not_raise,
    the_exec_bits_constant_is_ruffs,
)

_CASE_COUNT = 19


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"file-mode selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"file-mode selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
