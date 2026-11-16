#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.header_write` — a licence header added without moving a shebang.

⚑⚑⚑ THE SHEBANG ARM IS THE ITEM, AND IT FAILS SILENTLY WHEN WRONG. Prepending the two lines at
byte zero produces a file the reader calls CONFORMING while the `#!` has moved to line three,
where it is an ordinary comment. Nothing about the result looks wrong: the census goes green, the
file still parses, and the executable bit now asserts a property the file no longer has. So the
arm asserts the shebang is STILL ON LINE ONE, not merely that the header is present.

⚑⚑ THE ROUND-TRIP ARM IS WHAT MAKES THE OTHERS MEAN ANYTHING. Every case below could pass against
a writer that emits text `file_header` rejects — a repair that leaves the blocker exactly where it
was while reporting success. Feeding the output back through the owning reader is the only arm
that checks the writer and the reader agree, and it is the one a fixture cannot fake.

⚑⚑ IDEMPOTENCE IS CASED IN BOTH DIRECTIONS. A second run must add nothing, and the arm that
proves it must also show the FIRST run added something — otherwise a writer that never writes at
all passes the idempotence check perfectly.

⚑ THE FIXTURES ARE SOURCE STRINGS. An arm writing into the live corpus would measure today's tree
and go red the moment the blocker is PAID — reporting finished work as a defect. Exactly one arm
touches the corpus, and it asserts a RELATION rather than a count.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import file_header, header_write

# A module with no header at all — the ordinary member of the 87.
_BARE = '''"""A module with no licence header."""


def main() -> int:
    """Return."""
    return 0
'''

# ⚑ THE HARD CASE: a shebang on line one, which is a COMMENT and therefore inside the prologue.
_SHEBANG = '''#!/usr/bin/env python3
"""A module with a shebang and no licence header."""


def main() -> int:
    """Return."""
    return 0
'''

# Already conforming — must be left exactly alone.
_COMPLETE = f'''{file_header.SPDX_PREFIX}Apache-2.0
{file_header.COPYRIGHT_PREFIX} 2026 Mike Mol
"""A module that already conforms."""


def main() -> int:
    """Return."""
    return 0
'''


def a_bare_module_gets_the_header(out: list[str]) -> int:
    """Check a module with no header is repaired at the top."""
    found = header_write.repair(_BARE, "bare.py")
    if found is None:
        out.append("selftest: a bare module read as needing no repair")
        return 1
    if found.at:
        out.append(f"selftest: the bare insert point is {found.at!r}, not the top")
        return 1
    return 0


def the_shebang_stays_on_line_one(out: list[str]) -> int:
    """Check the header lands AFTER a shebang — THE WHOLE ITEM.

    ⚑⚑⚑ THE NAIVE REPAIR PASSES EVERY OTHER ARM. Prepending at byte zero makes the file conform by
    the reader's own predicate while moving the `#!` to line three, where it stops being a shebang.
    The defect is invisible to the census that motivated the repair, so it must be asserted here or
    nowhere.
    """
    found = header_write.repair(_SHEBANG, "sheb.py")
    if found is None:
        out.append("selftest: a shebanged module read as needing no repair")
        return 1
    got = header_write.applied(_SHEBANG, found)
    first = got.splitlines()[0]
    if not first.startswith(header_write.SHEBANG):
        out.append(f"selftest: the first line is now {first!r}")
        return 1
    return 0


def a_conforming_module_is_skipped(out: list[str]) -> int:
    """Check a file carrying both lines needs no repair — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS a writer repairing EVERY file passes both arms above and doubles the header on
    709 conforming files. The skip is what makes the operation safe to run over the whole corpus.
    """
    if header_write.repair(_COMPLETE, "done.py") is not None:
        out.append("selftest: a conforming module was offered a repair")
        return 1
    return 0


def the_repair_satisfies_the_reader(out: list[str]) -> int:
    """Check the written text is CONFORMING by the owning reader — the round-trip.

    ⚑⚑⚑ A WRITER THAT EMITS TEXT ITS OWN READER REJECTS reports success and leaves the blocker in
    place, and every other arm here would still pass. This is the only arm that checks the two
    modules agree about what a header IS, rather than checking the writer agrees with itself.
    """
    for label, text in (("bare.py", _BARE), ("sheb.py", _SHEBANG)):
        found = header_write.repair(text, label)
        if found is None:
            out.append(f"selftest: {label} read as needing no repair")
            return 1
        got = header_write.applied(text, found)
        if not file_header.read(got, label).complete:
            out.append(f"selftest: the reader rejects the repaired {label}")
            return 1
    return 0


def the_repair_is_idempotent(out: list[str]) -> int:
    """Check a second repair adds nothing, and that the FIRST one added something.

    ⚑⚑ BOTH HALVES OR NEITHER. A writer that never writes is perfectly idempotent, so asserting
    only the no-op would certify doing nothing as correct.
    """
    found = header_write.repair(_BARE, "bare.py")
    if found is None:
        out.append("selftest: no first repair to be idempotent about")
        return 1
    once = header_write.applied(_BARE, found)
    if once == _BARE:
        out.append("selftest: the first repair changed nothing")
        return 1
    if header_write.repair(once, "bare.py") is not None:
        out.append("selftest: a repaired module was offered a second repair")
        return 1
    return 0


def the_original_lines_survive(out: list[str]) -> int:
    """Check the repair only INSERTS — every original line is still present, in order.

    ⚑ A WRITER THAT REFLOWS what it did not come to change turns each repair into a review of the
    whole file, and across 87 files that is 87 diffs nobody reads.
    """
    found = header_write.repair(_SHEBANG, "sheb.py")
    if found is None:
        out.append("selftest: no repair to check for preservation")
        return 1
    got = header_write.applied(_SHEBANG, found).splitlines()
    for line in _SHEBANG.splitlines():
        if line not in got:
            out.append(f"selftest: the repair dropped {line!r}")
            return 1
    return 0


def the_header_uses_the_readers_prefixes(out: list[str]) -> int:
    """Check the emitted lines are built from the reader's constants, not retyped.

    ⚑ A SECOND SPELLING passes this module's cases and fails the census — the writer would produce
    text its own reader does not recognise, which is the shape that leaves a blocker unpaid while
    reporting it paid.
    """
    got = header_write.header_lines()
    if not any(line.startswith(file_header.SPDX_PREFIX) for line in got):
        out.append(f"selftest: no SPDX line among {got!r}")
        return 1
    if not any(line.startswith(file_header.COPYRIGHT_PREFIX) for line in got):
        out.append(f"selftest: no copyright line among {got!r}")
        return 1
    return 0


def an_empty_file_is_repaired_at_the_top(out: list[str]) -> int:
    """Check a zero-length file does not crash the insert-point reader."""
    if header_write.insert_at("") != 0:
        out.append("selftest: an empty file yielded a non-zero insert point")
        return 1
    return 0


def a_preview_writes_nothing(out: list[str]) -> int:
    """Check the census without `--apply` leaves the file untouched — THE SAFETY ARM.

    ⚑⚑ THE OPERATION IS UNIFORM AND THEREFORE EASY TO AIM AT THE WRONG POPULATION. A preview that
    silently wrote would be discovered only by reading a diff nobody expected to exist.
    """
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "bare.py"
        path.write_text(_BARE, encoding="utf-8")
        found = header_write.repair(path.read_text(encoding="utf-8"), "bare.py")
        if found is None:
            out.append("selftest: the fixture read as conforming")
            return 1
        if path.read_text(encoding="utf-8") != _BARE:
            out.append("selftest: reading a repair mutated the file")
            return 1
    return 0


def a_preview_census_says_it_is_a_preview(out: list[str]) -> int:
    """Check a non-applied run with findings states that nothing was written."""
    found = header_write.Repair("a.py", 0, header_write.header_lines())
    text = "\n".join(header_write.Census((found,), 1, wrote=False).lines())
    if "PREVIEW" not in text:
        out.append(f"selftest: a preview renders as {text!r}")
        return 1
    return 0


def an_applied_census_does_not_claim_preview(out: list[str]) -> int:
    """Check an applied run does NOT print the preview notice.

    ⚑ THE MIRROR OF THE ARM ABOVE. A notice printed unconditionally passes the preview case and
    tells a caller who just rewrote 87 files that nothing happened.
    """
    found = header_write.Repair("a.py", 0, header_write.header_lines())
    text = "\n".join(header_write.Census((found,), 1, wrote=True).lines())
    if "PREVIEW" in text:
        out.append(f"selftest: an applied run renders as {text!r}")
        return 1
    if "repaired" not in text:
        out.append(f"selftest: an applied run omits its verb: {text!r}")
        return 1
    return 0


def an_empty_scan_is_not_a_clean_bill(out: list[str]) -> int:
    """Check a zero over zero says so rather than reading as a conforming corpus."""
    text = "\n".join(header_write.Census((), 0, wrote=False).lines())
    if "NOTHING WAS SCANNED" not in text:
        out.append(f"selftest: an unscanned census renders as {text!r}")
        return 1
    return 0


def every_repair_targets_a_non_conforming_file(out: list[str]) -> int:
    """Check the live preview offers a repair ONLY where the reader reports a gap.

    ⚑⚑⚑ A RELATION, NEVER A COUNT. Pinning the number here would go red the day the blocker is
    PAID — a suite reporting finished work as a defect, which is the census-keyed-on-today shape.
    The invariant that survives the repair is that the writer and the reader name the same files.

    ⚑ AND IT RUNS AS A PREVIEW. A suite that wrote to the corpus to test the writer would be the
    population-polluting arm the census kit names.
    """
    found = header_write.census(apply=False)
    if not found.scanned:
        out.append("selftest: the live preview scanned nothing")
        return 1
    gaps = {
        entry.label for entry in file_header.missing(file_header.entries(file_header.population()))
    }
    offered = {found_one.label for found_one in found.repairs}
    if not offered <= gaps:
        out.append(f"selftest: repairs offered for conforming file(s): {sorted(offered - gaps)!r}")
        return 1
    return 0


_ARMS = (
    a_bare_module_gets_the_header,
    the_shebang_stays_on_line_one,
    a_conforming_module_is_skipped,
    the_repair_satisfies_the_reader,
    the_repair_is_idempotent,
    the_original_lines_survive,
    the_header_uses_the_readers_prefixes,
    an_empty_file_is_repaired_at_the_top,
    a_preview_writes_nothing,
    a_preview_census_says_it_is_a_preview,
    an_applied_census_does_not_claim_preview,
    an_empty_scan_is_not_a_clean_bill,
    every_repair_targets_a_non_conforming_file,
)

_CASE_COUNT = 2 + 2 + 1 + 2 + 2 + 1 + 2 + 1 + 2 + 1 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"header-write selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"header-write selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
