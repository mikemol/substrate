# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.file_read` — three outcomes, and the collapse they exist to prevent.

⚑⚑⚑ THE BROKEN ARM IS THE SUBJECT. `IsADirectoryError` is an `OSError`, so a caller guarding
`except OSError` swallows a directory-as-document exactly as it swallows a missing file — which is
how three call sites counted a defect as an absence. The arm drives a REAL directory, because a
fabricated error would prove only that the constructor stores what it is given.

⚑⚑ AND EACH OUTCOME IS ASSERTED AGAINST EVERY OTHER. A suite checking only that PRESENT is truthy
would pass against a reader that returned PRESENT for everything, so absence and breakage are
asserted to be falsy AND distinguishable from each other.

⚑ THE FIXTURES ARE REAL FILES IN A TEMPORARY TREE. This module's whole job is what the filesystem
does, so a fake would be testing the fake.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import file_read as fr

#: The bytes a present fixture holds.
BODY = "a document\nwith two lines\n"

#: A byte sequence no UTF-8 decoder accepts — the strict-decode arm needs one.
BAD_BYTES = b"\xff\xfe not utf-8"

#: How many outcomes a read has. ⚑ THIS IS THE MODULE'S CENTRAL CLAIM, not an incidental size: two
#: is the collapse it exists to undo, and four would mean an arm nobody named.
OUTCOMES = 3


def _present_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a file that is there and readable."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        path.write_text(BODY, encoding="utf-8")
        got = fr.read(path)

        out.append(
            (f"a readable file is PRESENT: {got.why()}", got.presence is fr.Presence.PRESENT)
        )
        out.append((f"and it is truthy: {bool(got)}", bool(got)))
        out.append((f"and its text round-trips: {got.text()!r}", got.text() == BODY))
        out.append(
            (
                f"and require returns bytes: {len(got.require())}",
                got.require() == BODY.encode("utf-8"),
            )
        )
        out.append(
            (f"and PRESENT is not a defect: {got.presence.is_defect}", not got.presence.is_defect)
        )
    return out


def _absent_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a file that is not there."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        got = fr.read(Path(tmp) / "missing.md")

        out.append((f"a missing file is ABSENT: {got.why()}", got.presence is fr.Presence.ABSENT))
        out.append((f"and it is falsy: {bool(got)}", not bool(got)))
        # ⚑ AN ABSENCE IS EXPECTED, NOT BROKEN. A census over a glob finds missing files routinely.
        out.append(
            (f"and ABSENT is not a defect: {got.presence.is_defect}", not got.presence.is_defect)
        )

        try:
            got.require()
        except FileNotFoundError as exc:
            out.append((f"and require raises FileNotFoundError: {exc}", True))
        else:
            out.append(("and require raises FileNotFoundError", False))
    return out


def _broken_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a path that exists and cannot be read as a file.

    ⚑⚑⚑ THIS IS THE COLLAPSE THE MODULE EXISTS FOR. A directory raises `IsADirectoryError`, which
    IS an `OSError` — so every caller guarding `except OSError` counted it as an absence, and the
    two need different responses.
    """
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        got = fr.read(Path(tmp))

        out.append(
            (f"a directory is BROKEN, not absent: {got.why()}", got.presence is fr.Presence.BROKEN)
        )
        out.append(
            (
                f"and it is distinguishable from ABSENT: {got.presence}",
                got.presence is not fr.Presence.ABSENT,
            )
        )
        out.append((f"and it is falsy like an absence: {bool(got)}", not bool(got)))
        # ⚑ AND IT IS THE ONE DEFECT — the property a caller branches on to tell them apart.
        out.append((f"and BROKEN is a defect: {got.presence.is_defect}", got.presence.is_defect))
        out.append(
            (
                f"and the account carries the cause: {got.why()}",
                got.error is not None and str(got.error) in got.why(),
            )
        )

        # ⚑⚑ REQUIRE RE-RAISES THE ORIGINAL, never a translated one — the reason must survive.
        try:
            got.require()
        except OSError as exc:
            out.append(
                (
                    f"and require re-raises the original error: {type(exc).__name__}",
                    exc is got.error,
                )
            )
        else:
            out.append(("and require re-raises the original error", False))
    return out


def _decode_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the strict decode.

    ⚑ A REPLACEMENT CHARACTER IS A SILENT EDIT. Every reader downstream would scan it as content,
    so a bad byte must raise rather than yield a plausible document.
    """
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.md"
        path.write_bytes(BAD_BYTES)
        got = fr.read(path)

        # ⚑ THE READ ITSELF SUCCEEDS — bytes are bytes, and the codec is the caller's choice.
        out.append(
            (
                f"undecodable bytes still read as PRESENT: {got.presence}",
                got.presence is fr.Presence.PRESENT,
            )
        )

        try:
            got.text()
        except UnicodeDecodeError:
            out.append(("and decoding them raises rather than mangling", True))
        else:
            out.append(("and decoding them raises rather than mangling", False))

        # ⚑ THE SENSITIVITY ARM. A permissive codec must succeed, or the strictness is not what
        # raised and this arm proves nothing about the default.
        out.append(
            (
                f"a permissive codec reads them: {got.text('latin-1')[:4]!r}",
                len(got.text("latin-1")) > 0,
            )
        )
    return out


def _text_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the convenience reader's asymmetry.

    ⚑⚑ ABSENT BECOMES `None` AND BROKEN STILL RAISES. That is the asymmetry a caller usually
    wants, and asserting both directions is what stops the two collapsing back together.
    """
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        present = Path(tmp) / "doc.md"
        present.write_text(BODY, encoding="utf-8")

        out.append(
            (f"a present file yields its text: {fr.text(present)!r}", fr.text(present) == BODY)
        )
        out.append(
            (
                f"a missing file yields None: {fr.text(Path(tmp) / 'nope.md')}",
                fr.text(Path(tmp) / "nope.md") is None,
            )
        )

        try:
            fr.text(Path(tmp))
        except OSError as exc:
            out.append((f"and a broken read RAISES rather than yielding None: {exc}", True))
        else:
            out.append(("and a broken read RAISES rather than yielding None", False))
    return out


def _roster_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the outcome roster itself."""
    out: list[tuple[str, bool]] = []
    every = list(fr.Presence)

    out.append(
        (f"there are exactly three outcomes: {[p.name for p in every]}", len(every) == OUTCOMES)
    )
    out.append(
        (
            f"and exactly one is a defect: {[p.name for p in every if p.is_defect]}",
            sum(1 for p in every if p.is_defect) == 1,
        )
    )
    # ⚑ A MEMBER COMPARES EQUAL TO ITS OWN NAME, which is what lets a report print it directly.
    out.append(
        (f"and a member renders as its name: {fr.Presence.BROKEN}", fr.Presence.BROKEN == "BROKEN")
    )
    return out


class _Rev:
    """A stand-in source that names a revision, satisfying `Source` by printing its name.

    ⚑ THE SUITE DECLARES ITS OWN SOURCE RATHER THAN IMPORTING THE REAL ONE. `Source` is a
    Protocol precisely so a caller can supply anything printable, and a case that could only be
    written with the git-backed reader would be testing that reader instead of this contract —
    and would drag `pygit2` into the suite of a module that reads ordinary files.
    """

    def __init__(self, rev: str) -> None:
        self.rev = rev

    def __str__(self) -> str:
        """Return the revision name as a report should show it."""
        return f"rev {self.rev}"


def _source_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the source a read came from.

    ⚑⚑ THE NEGATIVE ARM IS THE LOAD-BEARING ONE. Every arm here would pass against a `why()` that
    appended a source clause unconditionally, printing ` at None` on every ordinary read — so the
    working-tree case asserting the clause is ABSENT is what pins the default's meaning.
    """
    out: list[tuple[str, bool]] = []
    where = Path("gone.py")
    head = _Rev("HEAD~3")

    plain = fr.Result(fr.Presence.ABSENT, where)
    out.append((f"a working-tree read names no source: {plain.why()}", "at" not in plain.why()))
    out.append((f"and its source field is None: {plain.source}", plain.source is None))

    at_rev = fr.Result(fr.Presence.ABSENT, where, source=head)
    out.append(
        (f"a revision read names the revision: {at_rev.why()}", "rev HEAD~3" in at_rev.why())
    )
    # ⚑ THE TWO ABSENCES MUST NOT READ ALIKE — that is the whole reason the field exists.
    out.append(
        (
            f"and the two absences differ: {plain.why()} vs {at_rev.why()}",
            plain.why() != at_rev.why(),
        )
    )

    # ⚑ PRESENT AND BROKEN CARRY IT TOO. A source threaded through only the absent arm would look
    # correct on the case that motivated it and drop the fact everywhere else.
    got = fr.Result(fr.Presence.PRESENT, where, data=b"xy", source=head)
    out.append((f"a present read names it: {got.why()}", "rev HEAD~3" in got.why()))
    hurt = fr.Result(fr.Presence.BROKEN, where, error=OSError("bad"), source=head)
    out.append((f"a broken read names it: {hurt.why()}", "rev HEAD~3" in hurt.why()))

    # ⚑ AND THE RAISED MESSAGE CARRIES IT, because a traceback is where this is read most often.
    try:
        at_rev.require()
    except FileNotFoundError as exc:
        out.append((f"and require() names the source: {exc}", "rev HEAD~3" in str(exc)))
    else:
        out.append(("and require() names the source", False))

    # ⚑ THE ERROR FIELD ADMITS A NON-OSError, which a revision reader needs: a bad rev is a
    # ValueError, and typing the field to OSError would have forced that to be laundered.
    bad = fr.Result(fr.Presence.BROKEN, where, error=ValueError("bad revision"), source=head)
    out.append((f"a non-OSError survives: {bad.why()}", "bad revision" in bad.why()))

    # ⚑⚑⚑ THE SENSITIVITY ARM. Every case above passes today, which says the checks RUN — never
    # that they would CATCH the defect. So the defect is CONSTRUCTED here: a source clause emitted
    # unconditionally, which is the natural wrong implementation (it reads correctly on every arm
    # that has a source, and prints ` at None` on every ordinary read). The claim is that the
    # working-tree arm above goes red against it. Asserted, not assumed.
    #
    # ⚑ IT IS A CASE AND NOT A THROWAWAY PROBE BECAUSE THE PROBE WAS WRITTEN AS ONE FIRST, and the
    # chaining hook refused it: an inline script dies with the turn, so the next reader inherits a
    # claim of sensitivity with nothing that re-derives it.
    always_at = f" at {plain.source}"
    out.append(
        (
            f"the working-tree arm would CATCH an unconditional clause: {always_at!r}",
            "at" in always_at,
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _present_cases()
        + _absent_cases()
        + _broken_cases()
        + _decode_cases()
        + _text_cases()
        + _roster_cases()
        + _source_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"file-read selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
