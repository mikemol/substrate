#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Arms for `substrate.module_size` — the size READING, and the operand it must not discard.

⚑⚑⚑ THE OPERAND ARMS ARE THE ONES THE ORIGINAL SUITE COULD NOT HAVE. Every case here passed
while `module_size <path>` returned the FULL corpus census, because none of them ever invoked the
command line with an operand — the arms measured `read_one` and `census`, which were both correct.
A defect in what `main` does with `argv` is invisible to a suite that never calls `main`.

⚑⚑ AND THE SCOPED ARM IS PAIRED WITH AN AGREEMENT ARM. A `scoped` that returned an EMPTY reading
would satisfy "the corpus census is not returned" perfectly. So the discriminator is not that the
output is smaller — it is that the scoped row for a file EQUALS that file's row in the full
census, which no degenerate implementation produces.

⚑ THE SORT KEY IS A NAMED ACCESSOR, NOT A LAMBDA, and this suite learned it the same way the
module did: `max(rows, key=lambda r: r.code)` types as `Callable[[Any], Any]` and the checker
refused the file. The rule the module's own header records applies to the cases that test it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import size_budget
from substrate.module_size import (
    SizeRow,
    UnreadableOperandError,
    census,
    main,
    over_budget,
    read_one,
    render,
    scoped,
)

#: A base budget small enough that a short fixture exceeds it deterministically.
_TINY_BASE = 3

#: The exit code a refused invocation returns.
_BAD_ARGV = 2


def _code_of(row: SizeRow) -> int:
    """Return a row's code-line count as a sort key — named and typed, never an inline lambda."""
    return row.code


def _write(directory: Path, name: str, body: str) -> Path:
    """Write `body` to `name` under `directory` and return the path."""
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


def a_passing_module_still_produces_a_row(out: list[str]) -> int:
    """⚑ THE DEFECT THIS MODULE EXISTS FOR: an empty list read as "no file was read".

    After a split, the question is *how far under did it land*, and a findings-only census
    cannot answer it — the origin's fallback was running a second mode to recover a number the
    first had already computed and discarded.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "small.py", "x = 1\n")
        row = read_one(path, "small.py")
    if row is None:
        out.append("a readable, parseable module produced no row")
        return 1
    if row.why != "":
        out.append(f"a one-line module was flagged: {row.why!r}")
        return 1
    return 0


def headroom_is_reported_for_a_passing_module(out: list[str]) -> int:
    """⚑ POSITIVE CONTROL that the passing row carries a usable number, not just a blank why."""
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "small.py", "x = 1\n")
        row = read_one(path, "small.py")
    if row is None or row.headroom != size_budget.OVERLARGE_LINES - row.code:
        out.append(f"headroom is not cap minus code: {row}")
        return 1
    if row.code <= 0:
        out.append(f"a module with a statement counted {row.code} code lines")
        return 1
    return 0


def an_over_budget_module_is_flagged_and_filtered(out: list[str]) -> int:
    """⚑ `over_budget` must be a FILTER over one body, never a second counting implementation.

    Two bodies for one count is exactly how `agda_files()` became four under one name.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "big.py", "a = 1\nb = 2\nc = 3\nd = 4\ne = 5\n")
        row = read_one(path, "big.py", base=_TINY_BASE)
    if row is None or not row.why:
        out.append(f"a 5-line module under a {_TINY_BASE}-line budget was not flagged: {row}")
        return 1
    if over_budget([row]) != [row]:
        out.append("over_budget dropped a row that carries a finding")
        return 1
    return 0


def a_docstring_heavy_module_is_not_counted_as_bulk(out: list[str]) -> int:
    """⚑ THE NAIVE COUNTER'S DEFECT, asserted at the census level rather than only the leaf.

    `strip() and not startswith("#")` reads every docstring line as code, so the modules whose
    ⚑ commentary IS the incident log score worst on the census built to find bulk.
    """
    body = '"""\n' + "prose line\n" * 20 + '"""\nx = 1\n'
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "documented.py", body)
        row = read_one(path, "documented.py")
    if row is None:
        out.append("the documented fixture produced no row")
        return 1
    if row.code > row.physical // 2:
        out.append(f"docstring counted as bulk: code={row.code} physical={row.physical}")
        return 1
    return 0


def an_unparseable_module_is_unmeasured_not_zero(out: list[str]) -> int:
    """⚑ A ROW OF ZEROS WOULD MAKE AN UNPARSEABLE FILE THE SMALLEST IN THE CORPUS.

    That is a fact about the reader reported as a fact about the file.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "broken.py", "def f(:\n")
        row = read_one(path, "broken.py")
    if row is not None:
        out.append(f"an unparseable module produced a measured row: {row}")
        return 1
    return 0


def a_second_main_guard_is_flagged_below_the_line_budget(out: list[str]) -> int:
    """⚑ REPORTED AT ANY SIZE, or it hides in exactly the large files where it hid once."""
    body = 'if __name__ == "__main__":\n    pass\nif __name__ == "__main__":\n    pass\n'
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(Path(tmp), "twoguards.py", body)
        row = read_one(path, "twoguards.py")
    if row is None or "__main__" not in row.why:
        out.append(f"two __main__ guards in a 4-line file were not reported: {row}")
        return 1
    return 0


def the_render_prints_its_denominator(out: list[str]) -> int:
    """⚑ `0 findings` and `0 findings over 998 files` are the same finding.

    Only the second lets a reader see the scan HAPPENED rather than that nothing was wrong.
    """
    text = render([], 998)
    if "998" not in text:
        out.append(f"the denominator is absent from a zero-finding render: {text!r}")
        return 1
    return 0


def the_census_reads_the_real_corpus(out: list[str]) -> int:
    """⚑ POSITIVE CONTROL against a census that reports zero because it scanned nothing."""
    rows, scanned = census()
    if scanned <= 0 or not rows:
        out.append(f"the corpus census read {scanned} file(s) and produced {len(rows)} row(s)")
        return 1
    if not all(isinstance(r, SizeRow) for r in rows):
        out.append("the census produced something other than SizeRow records")
        return 1
    return 0


def a_named_operand_scopes_the_reading(out: list[str]) -> int:
    """⚑⚑⚑ THE MEASURED DEFECT: `module_size <path>` returned the WHOLE corpus census.

    Byte-identical to the bare call, so a reader who found their file in the output believed the
    query had been scoped — a true line for the wrong reason. It was used to scope a dispatch
    wave twice before anyone noticed.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        _write(base, "one.py", "x = 1\n")
        _write(base, "two.py", "y = 2\n")
        rows, read = scoped((str(base / "one.py"),), root=base)
    if read != 1 or len(rows) != 1:
        out.append(f"one operand produced {len(rows)} row(s) over {read} file(s) read")
        bad += 1
    elif not rows[0].path.endswith("one.py"):
        out.append(f"the scoped row names {rows[0].path!r}, not the operand")
        bad += 1
    return bad


def a_scoped_row_equals_its_full_census_row(out: list[str]) -> int:
    """⚑⚑⚑ THE DISCRIMINATOR — scoping must be the SAME statistic over fewer files.

    A `scoped` returning nothing, or zeros, would satisfy "the corpus census is not returned"
    perfectly. What no degenerate implementation produces is a row EQUAL to that file's row in
    the full census, which is also the claim that makes scoping honest here at all: every column
    is file-local, so `substrate.tool_cli`'s refusal — right for a corpus-relative statistic —
    would be wrong for this one.
    """
    rows, _ = census()
    if not rows:
        out.append("the corpus census produced no rows, so this arm asserts nothing")
        return 1
    want = max(rows, key=_code_of)
    got, _read = scoped((want.path,))
    if len(got) != 1 or got[0] != want:
        out.append(f"the scoped row for {want.path!r} is {got!r}, not its census row {want!r}")
        return 1
    return 0


def several_operands_are_all_read(out: list[str]) -> int:
    """⚑ THE ROSTER IS HONOURED WHOLE, not truncated to its first member.

    A body that read `argv[0]` and stopped would pass the single-operand arm above.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        names = ("one.py", "two.py", "three.py")
        for name in names:
            _write(base, name, "x = 1\n")
        rows, read = scoped(tuple(str(base / n) for n in names), root=base)
    if len(rows) != len(names) or read != len(names):
        out.append(f"{len(names)} operands produced {len(rows)} row(s) over {read} read")
        return 1
    return 0


def an_unreadable_operand_refuses_rather_than_thinning(out: list[str]) -> int:
    """⚑⚑ A ROSTER THAT SHRINKS IN SILENCE IS THE DISCARDED OPERAND ONE LAYER DOWN.

    The caller named N paths and would get fewer rows with nothing saying which vanished or why —
    the same shape as the corpus census returned for a scoped query, at a smaller scale.
    """
    try:
        scoped(("/nonexistent/definitely-absent.py",))
    except UnreadableOperandError:
        return 0
    out.append("an unreadable operand did not refuse")
    return 1


def a_bare_call_still_reads_the_corpus(out: list[str]) -> int:
    """⚑⚑ THE PAIR FOR THE SCOPING ARMS — the bare reading must NOT have become a refusal.

    A `main` that refused every invocation would satisfy the operand arms and read as fixed. The
    corpus reading is the tool's other legitimate question and it stays answerable.
    """
    if main([]) != 0:
        out.append("a bare invocation did not exit 0")
        return 1
    return 0


def an_unknown_flag_is_refused_not_ignored(out: list[str]) -> int:
    """⚑ A FLAG ACCEPTED AND IGNORED IS THE DISCARDED OPERAND SPELLED WITH A DASH.

    `--top` belongs to another tool; silently ignoring it here would return a reading that looks
    like it honoured a bound it never read.
    """
    if main(["--top"]) != _BAD_ARGV:
        out.append("an unknown flag did not exit 2")
        return 1
    return 0


def the_render_says_it_is_a_reading_not_a_verdict(out: list[str]) -> int:
    """⚑ Ⓝ80: THE SIZE BUDGET IS RETIRED, so the output must not read as an obligation.

    The numbers are unchanged; what changed is the claim the summary line makes about what the
    reader must now do. Pinned so a later edit does not quietly restore the verdict wording.
    """
    text = render([], 1)
    if "reading" not in text.lower() or "verdict" not in text.lower():
        out.append(f"the summary does not state it is a reading rather than a verdict: {text!r}")
        return 1
    return 0


_ARMS = (
    a_passing_module_still_produces_a_row,
    headroom_is_reported_for_a_passing_module,
    an_over_budget_module_is_flagged_and_filtered,
    a_docstring_heavy_module_is_not_counted_as_bulk,
    an_unparseable_module_is_unmeasured_not_zero,
    a_second_main_guard_is_flagged_below_the_line_budget,
    the_render_prints_its_denominator,
    the_census_reads_the_real_corpus,
    a_named_operand_scopes_the_reading,
    a_scoped_row_equals_its_full_census_row,
    several_operands_are_all_read,
    an_unreadable_operand_refuses_rather_than_thinning,
    a_bare_call_still_reads_the_corpus,
    an_unknown_flag_is_refused_not_ignored,
    the_render_says_it_is_a_reading_not_a_verdict,
)

_CASE_COUNT = 2 + 2 + 2 + 2 + 1 + 1 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"module-size selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"module-size selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
