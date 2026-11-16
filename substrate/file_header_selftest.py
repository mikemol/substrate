#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the header census, including the case that would have caught its predecessor.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE LIVE ONE, because the reader this replaces failed against
the real tree and not against a fixture. `pycodemod --literal` reported zero SPDX lines in
`scripts/` while `scripts/fix_exe_bit.py` carries one at line 2 — a reader searching STRING
CONSTANTS answering a question about COMMENTS. So the differential arm reads that exact file
and asserts both lines are found, which is the assertion the old reader failed.

⚑⚑ AND THE PROSE CASE IS THE MIRROR OF IT. `file_header`'s own module docstring quotes the
SPDX token while explaining the convention, so a reader scanning the whole file would count
every module that DOCUMENTS the rule as CONFORMING to it. A case asserts a docstring mention
does not register, which is the false-positive direction the prefix-in-prologue rule exists
to close.

⚑ THE TWO LINES ARE ASSERTED SEPARATELY THROUGHOUT. A peer measured two repos as mirror
images — one gating SPDX only, one Copyright only, each having run the arm its own config
would pass. Every case here that could be satisfied by one line names which.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import file_header

ROOT = Path(__file__).resolve().parent.parent

_BOTH = (
    "#!/usr/bin/env python3\n"
    "# SPDX-License-Identifier: Apache-2.0\n"
    "# Copyright (c) 2026 Mike Mol\n"
    '"""A module."""\n'
)
_SPDX_ONLY = "#!/usr/bin/env python3\n# SPDX-License-Identifier: Apache-2.0\n"
_COPYRIGHT_ONLY = "#!/usr/bin/env python3\n# Copyright (c) 2026 Mike Mol\n"
_NEITHER = '#!/usr/bin/env python3\n"""A module with no header."""\n'
_IN_PROSE = '"""Docs.\n\n# SPDX-License-Identifier: Apache-2.0\n# Copyright (c) 2026 X\n"""\n'
_AFTER_BODY = "import os\n\n# SPDX-License-Identifier: Apache-2.0\n# Copyright (c) 2026 X\n"

# The two incomplete rows the population fixture carries: one partial, one bare.
_INCOMPLETE = 2

Case = tuple[str, bool]


def _complete_cases() -> list[Case]:
    """Return the cases where both header lines are present."""
    got = file_header.read(_BOTH, "both.py")
    return [
        ("a full header reports spdx", got.spdx),
        ("a full header reports copyright", got.copyright),
        ("a full header is complete", got.complete),
        ("a full header is NOT partial", not got.partial),
    ]


def _partial_cases() -> list[Case]:
    """Return the cases distinguishing WHICH line is missing.

    ⚑ A SINGLE BOOLEAN WOULD COLLAPSE THESE TWO, and that collapse is the measured defect:
    a gate armed on one line goes green on a file carrying only the other.
    """
    spdx = file_header.read(_SPDX_ONLY, "spdx.py")
    copy = file_header.read(_COPYRIGHT_ONLY, "copy.py")
    none = file_header.read(_NEITHER, "none.py")
    return [
        ("spdx-only reports spdx", spdx.spdx),
        ("spdx-only does NOT report copyright", not spdx.copyright),
        ("spdx-only is partial, not complete", spdx.partial and not spdx.complete),
        ("copyright-only reports copyright", copy.copyright),
        ("copyright-only does NOT report spdx", not copy.spdx),
        ("copyright-only is partial, not complete", copy.partial and not copy.complete),
        ("neither reports nothing", not none.spdx and not none.copyright),
        # ⚑ ABSENT IS NOT PARTIAL. A file with no header at all is a different row from one
        #   with half a header, and a gate reporting them together cannot be paid down.
        ("neither is NOT partial", not none.partial),
        ("neither is not complete", not none.complete),
    ]


def _false_positive_cases() -> list[Case]:
    """Return the cases pinning that a mention is not a header."""
    prose = file_header.read(_IN_PROSE, "prose.py")
    after = file_header.read(_AFTER_BODY, "after.py")
    return [
        # ⚑ THIS MODULE'S OWN DOCSTRING QUOTES THE TOKEN. A whole-file scan would count
        #   every module documenting the convention as conforming to it.
        ("a header quoted in a docstring does NOT count", not prose.spdx and not prose.copyright),
        # ⚑ A COMMENT AFTER THE FIRST STATEMENT IS NOT A PROLOGUE.
        ("a header comment after real code does NOT count", not after.spdx and not after.copyright),
        ("the prologue stops at the first statement", file_header.prologue(_AFTER_BODY) == []),
    ]


def _live_cases() -> list[Case]:
    """Read the real file whose header the previous reader could not see."""
    probe = ROOT / "scripts" / "fix_exe_bit.py"
    if not probe.is_file():
        return [("scripts/fix_exe_bit.py is present to read", False)]
    got = file_header.entry(probe, "scripts/fix_exe_bit.py")
    mine = file_header.entry(Path(__file__), "self")
    return [
        ("scripts/fix_exe_bit.py is present to read", True),
        # ⚑ THE ASSERTION THE OLD READER FAILED. --literal reported 0 of 131 for this token
        #   while this exact file carries it at line 2.
        ("the live file's SPDX line IS found", got is not None and got.spdx),
        ("the live file's copyright line IS found", got is not None and got.copyright),
        ("the live file is complete", got is not None and got.complete),
        # This suite carries a header too, so the reader finds itself.
        ("this suite's own header is found", mine is not None and mine.complete),
        (
            "an unreadable path yields None",
            file_header.entry(ROOT / "no-such-file-at-all.py", "absent") is None,
        ),
    ]


def _population_cases() -> list[Case]:
    """Return the cases pinning the roll-up over several files."""
    files = [(Path("a.py"), "a.py"), (Path("b.py"), "b.py")]
    got = file_header.entries(files)
    made = (
        file_header.read(_BOTH, "ok.py"),
        file_header.read(_SPDX_ONLY, "half.py"),
        file_header.read(_NEITHER, "none.py"),
    )
    gaps = file_header.missing(made)
    return [
        # Absent files drop out rather than counting as offenders — the reader must not
        # report a file it could not read as a file lacking a header.
        ("unreadable files are dropped, not counted", got == ()),
        ("missing() returns the two incomplete rows", len(gaps) == _INCOMPLETE),
        ("missing() excludes the complete row", all(e.label != "ok.py" for e in gaps)),
        (
            "missing() includes the PARTIAL row, not only the empty one",
            any(e.label == "half.py" for e in gaps),
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _complete_cases()
        + _partial_cases()
        + _false_positive_cases()
        + _live_cases()
        + _population_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"file_header: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
