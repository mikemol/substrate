# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.file_write` — atomicity under failure, and the preview that refuses.

⚑⚑⚑ THE ATOMICITY ARM DRIVES A REAL FAILURE. Asserting that a successful write leaves the right
bytes says nothing about the property that matters: a truncating open destroys the source BEFORE it
writes, so a crash mid-write loses the file. The arm makes the write fail and asserts the ORIGINAL
survives — which is the only way to tell an atomic writer from a lucky one.

⚑⚑ AND THE PREVIEW ARM ASSERTS THE TREE IS UNTOUCHED, not merely that a value came back. A dry run
that returned a plausible report while writing anyway is precisely the false-green a byte-level
seam under a `--dry-run` tool can produce, and only reading the file back catches it.

⚑ THE ENCODING ARM USES GLYPHS THAT ACTUALLY BROKE. A locale-default encode mangled mathematical
and Agda characters once, costing four wrong cause hypotheses — so the fixture carries those rather
than ASCII that every codec agrees on. They are written as NAMED ESCAPES because the literals are
confusable with Latin letters and this repo's linter says so.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import file_write as fw

#: ⚑ THE GLYPHS THAT BROKE UNDER A LOCALE DEFAULT. ASCII would pass under every codec and prove
#: nothing about the seam.
GLYPHS = (
    "\N{MATHEMATICAL DOUBLE-STRUCK DIGIT ONE} and "
    "\N{MATHEMATICAL DOUBLE-STRUCK DIGIT ZERO} joined by "
    "\N{PROPORTION} — a document"
)

#: What a file holds before an overwrite is attempted.
ORIGINAL = "the original content\n"


def _write_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for an ordinary applied write."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        got = fw.write(path, GLYPHS)

        out.append((f"the write reports what it did: {got.why()}", got.written))
        out.append(
            (
                f"and the bytes land: {path.read_text(encoding='utf-8') == GLYPHS}",
                path.read_text(encoding="utf-8") == GLYPHS,
            )
        )
        out.append(
            (
                f"and the size is the encoded length: {got.size}",
                got.size == len(GLYPHS.encode("utf-8")),
            )
        )
        # ⚑ THE SIZE IS BYTES, NOT CHARACTERS — a multi-byte glyph makes those differ, which is
        # what a caller checking a written length needs to agree on.
        out.append(
            (f"and bytes exceed characters for these glyphs: {got.size}", got.size > len(GLYPHS))
        )
    return out


def _encoding_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the stated codec.

    ⚑⚑ THE CODEC IS A PARAMETER, NOT THE ENVIRONMENT'S. A locale-default encode is a different
    function on a different machine, and the document it mangles reads as plausible wherever the
    locale happens to match.
    """
    out: list[tuple[str, bool]] = []

    out.append((f"the default codec is utf-8: {fw.ENCODING}", fw.ENCODING == "utf-8"))
    out.append(
        (
            f"and glyphs survive it: {len(fw.encode(GLYPHS))}",
            fw.encode(GLYPHS).decode("utf-8") == GLYPHS,
        )
    )
    out.append(
        (f"and bytes pass through unchanged: {fw.encode(b'raw')!r}", fw.encode(b"raw") == b"raw")
    )

    # ⚑ THE SENSITIVITY ARM. A codec that cannot carry these glyphs must FAIL rather than
    # substitute — otherwise the encode is not what preserved them.
    try:
        fw.encode(GLYPHS, "ascii")
    except UnicodeEncodeError:
        out.append(("and a codec that cannot carry them raises", True))
    else:
        out.append(("and a codec that cannot carry them raises", False))
    return out


def _preview_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the dry run, asserted against the filesystem.

    ⚑⚑⚑ THE TREE IS READ BACK. A preview that returned a plausible report while writing anyway is
    exactly the false-green a byte-level seam under a `--dry-run` tool produces, and only reading
    the file catches it.
    """
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        path.write_text(ORIGINAL, encoding="utf-8")

        got = fw.preview(path, GLYPHS)
        out.append((f"a preview reports what it would do: {got.why()}", not got.written))
        out.append(
            (
                f"and the file is UNCHANGED: {path.read_text(encoding='utf-8')!r}",
                path.read_text(encoding="utf-8") == ORIGINAL,
            )
        )
        # ⚑ AND THE SIZE MATCHES WHAT THE REAL WRITE WOULD PRODUCE, or the dry run is evidence
        # about the preview rather than about the write.
        out.append(
            (
                f"and its size matches the real write: {got.size}",
                got.size == len(GLYPHS.encode("utf-8")),
            )
        )

        # ⚑⚑ REACHING `write` UNDER A PREVIEW MODE IS A BUG AND MUST RAISE. Returning quietly
        # would let a caller report a dry run as a completed edit.
        try:
            fw.write(path, GLYPHS, fw.Mode.PREVIEW)
        except fw.RefusedError as exc:
            out.append((f"and write under PREVIEW refuses: {str(exc)[:40]}", True))
        else:
            out.append(("and write under PREVIEW refuses", False))

        out.append(
            (
                f"and the refusal left the file alone: {path.read_text(encoding='utf-8')!r}",
                path.read_text(encoding="utf-8") == ORIGINAL,
            )
        )
    return out


def _atomic_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving a failed write leaves the ORIGINAL.

    ⚑⚑⚑ THIS IS THE PROPERTY A SUCCESSFUL-WRITE ARM CANNOT SHOW. A truncating open destroys the
    source before writing, so the difference between an atomic writer and a lucky one is only
    visible when the write fails.

    ⚑ THE FAILURE IS AN UNWRITABLE DIRECTORY rather than a doctored payload, because the temp file
    is created BESIDE the target — so making that directory read-only fails the write at exactly
    the step atomicity is about, using the real filesystem rather than a stand-in.
    """
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "locked"
        home.mkdir()
        path = home / "doc.md"
        path.write_text(ORIGINAL, encoding="utf-8")
        home.chmod(0o500)

        try:
            fw.write(path, "replacement content")
        except OSError:
            out.append(("a failing write raises rather than silently succeeding", True))
        else:
            out.append(("a failing write raises rather than silently succeeding", False))
        finally:
            home.chmod(0o700)

        out.append(
            (
                f"and the ORIGINAL survives: {path.read_text(encoding='utf-8')!r}",
                path.read_text(encoding="utf-8") == ORIGINAL,
            )
        )

        # ⚑ AND NO TEMP SIBLING IS LEFT BEHIND — a cancelled run must not leave a file the next
        # glob counts as a document.
        siblings = [p.name for p in home.iterdir() if fw.TEMP_SUFFIX in p.name]
        out.append((f"and no temp sibling remains: {siblings}", siblings == []))
    return out


def _mkdirs_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the directory-creating opt-in."""
    out: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as tmp:
        nested = Path(tmp) / "a" / "b" / "doc.md"

        # ⚑ THE DEFAULT REFUSES. Creating a tree silently is how a typo becomes a new directory
        # rather than an error.
        try:
            fw.write(nested, "body")
        except OSError:
            out.append(("a missing parent refuses by default", True))
        else:
            out.append(("a missing parent refuses by default", False))

        got = fw.write(nested, "body", mkdirs=True)
        out.append((f"and mkdirs creates it: {got.why()}", nested.exists()))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _write_cases() + _encoding_cases() + _preview_cases() + _atomic_cases() + _mkdirs_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"file-write selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
