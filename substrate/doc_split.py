#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Conservation for a markdown document split into several — every line lands exactly once.

⚑⚑⚑ THIS IS `split_lemmas`' GUARD ONE CORPUS OVER, AND THE REASON IT IS A MODULE RATHER THAN A
TURN'S REASONING IS THAT THE GUARD HAS CAUGHT SEVEN DISTINCT SILENT-DELETION BUGS IN THE AGDA
SPLITTER AND `substrate/module_trim.py` REPRODUCED IT FOR PYTHON. A mechanical splitter's
characteristic output is PLAUSIBLE AND WRONG: the parts read correctly, the headings are in place,
and a paragraph is simply absent. Nothing about the output says so, which is why the check cannot
be an inspection.

⚑⚑ BOTH DIRECTIONS ARE CHECKED, AND THE SECOND IS THE ONE A LINE COUNT CANNOT SEE.
ORIGIN minus PARTS catches a line that was DROPPED. PARTS minus ORIGIN catches a line that was
REWRITTEN in transit — a re-wrapped paragraph, a smart-quoted dash, a heading the splitter
helpfully retitled — which preserves the count exactly while changing the record. `module_trim`'s
header records the same rule for Python, arrived at independently after a one-directional check
passed over a real defect.

⚑ THE COMPARISON IS A MULTISET, NOT A SET. A document that quotes the same ⚑ line in two places
holds it twice, and a splitter that emits it once has lost content a set comparison calls present.
Multiset also catches the opposite: a line DUPLICATED across two parts, which is how a reader ends
up acting on a finding twice under two different concerns.

⚑ WHAT IS DELIBERATELY EXEMPT, AND ONLY THIS. Blank lines and the parts' own NEW scaffolding —
their titles, their back-links to the index — are content the split INVENTS by design, so they are
excluded by an explicit allowance the caller passes rather than by a rule this module invents.
An exemption admitted in both directions would swallow the check standing beside it, so the
allowance applies ONLY to lines the parts gained; a line the ORIGIN held is never excusable.

⚑⚑⚑ AND AN EMPTY ORIGIN IS REFUSED, BECAUSE THE BOTH-DIRECTIONS RULE CANNOT SEE THIS ONE.
MEASURED: a run reported CONSERVED against a reference file a failed `git show` had left empty.
The predicate was right and every arm above still held — the failure was in the OPERAND, so a
conservation guard comparing against nothing reported perfect conservation. Both multiset
differences of an empty origin are empty by construction, which is exactly the answer a faithful
split produces, and no amount of checking BOTH directions distinguishes them.

⚑⚑ SO THE DEGENERATE OPERAND IS "NO BODY LINES", NOT "ZERO BYTES", and the wider spelling is the
point. A whitespace-only origin, a file of nothing but blank lines, and a file that failed to
open are the SAME SHAPE as the empty one: `body_lines` returns `[]` for each, the comparison has
nothing to measure, and the verdict is vacuous in all four. Refusing only the byte-empty case
would fix the instance that was caught and leave its three siblings live.

⚑ WHAT IS DELIBERATELY STILL ACCEPTED, and it is the near neighbour. A ONE-LINE origin is NOT
degenerate: it holds content, so a part that drops it reads `dropped` and a part that rewrites it
reads both directions. The refusal is keyed on *the comparison having nothing to measure*, never
on the origin being small — a threshold on size would refuse honest work to catch a vacuum.
⚑ EMPTY PARTS ARE ALSO NOT REFUSED: parts holding nothing against a non-empty origin is the
guard's LOUDEST true finding (every line dropped), and refusing it would convert the sharpest
detection this tool has into an error about the invocation.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# The smallest invocation that names both an origin and one part. ⚑ NAMED BECAUSE THE GATE
# REFUSED THE BARE LITERAL, and it was right: the number is the ARITY of the usage line printed
# two lines below it, and two spellings of one fact drift.
_MIN_ARGS = 2


@dataclass(frozen=True, slots=True)
class Loss:
    """One line the split failed to conserve, with the direction that accuses it.

    ⚑ THE DIRECTION IS PART OF THE FINDING, NOT METADATA. A `dropped` line is content the split
    destroyed; a `gained` line is content it invented or rewrote. They send a reader to different
    places — the first to whichever part should have held it, the second to the transform — and a
    report that merges them into "N lines differ" makes the reader re-derive the distinction.
    """

    direction: str
    line: str
    count: int

    def rank(self) -> tuple[str, str]:
        """Return this loss's sort key — direction first, then the line itself.

        ⚑ A NAMED KEY RATHER THAN A KEYLESS `sorted`, which under a slotted dataclass is a static
        error and under a `NamedTuple` was an ordering by field DECLARATION POSITION that nobody
        chose. `count` is deliberately absent from the key: two losses of the same line in the
        same direction cannot both exist, so including it would order nothing.
        """
        return (self.direction, self.line)


@dataclass(frozen=True, slots=True)
class Report:
    """What a split conserved and what it did not.

    ⚑ `ok` IS DERIVED FROM THE LOSSES RATHER THAN STORED BESIDE THEM, so a caller cannot be handed
    a report whose verdict disagrees with its own rows — the shape this repo has watched collapse
    wherever a summary field is written by hand next to the data it summarises.
    """

    origin: str
    parts: tuple[str, ...]
    losses: tuple[Loss, ...]

    @property
    def ok(self) -> bool:
        """Report whether every line of the origin landed in exactly one part."""
        return not self.losses


def body_lines(text: str) -> list[str]:
    """Return the non-blank lines of `text`, stripped — the unit conservation is measured in.

    ⚑ STRIPPED, BECAUSE INDENTATION IS THE ONE THING A SPLIT LEGITIMATELY CHANGES. A bullet moved
    out of a section becomes a top-level bullet, and refusing that would make every honest split
    fail. Everything else about the line — its words, its ⚑ markers, its numbers — must survive
    byte-for-byte, which is what the comparison then enforces.
    """
    return [stripped for line in text.split("\n") if (stripped := line.strip())]


class VacuousOriginError(ValueError):
    """The origin has no body lines, so `conserved` would report a vacuous CONSERVED.

    ⚑ A DISTINCT TYPE RATHER THAN A BARE `ValueError`, because a caller that means to tolerate a
    missing origin must be able to say so without also swallowing a malformed span. The two are
    already separate refusals; giving them one exception type would merge them at the only place
    a caller can tell them apart.
    """


def refuse_vacuous_origin(origin: str, where: str) -> None:
    """Raise when `origin` carries no body line — the operand a conservation check cannot measure.

    ⚑ THE GUARD IS ON THE MEASURED UNIT, NOT ON THE BYTES. `body_lines` is what the comparison
    actually consumes, so asking IT whether there is anything to compare keeps the refusal and the
    check reading the same document. A separate `if not origin.strip()` would be a second spelling
    of one fact, drifting the day `body_lines` changes what it counts.
    """
    if not body_lines(origin):
        msg = (
            f"{where}: the origin has no content to conserve — refusing to report CONSERVED. "
            "An empty, whitespace-only or unreadable origin makes both multiset differences "
            "empty, which is indistinguishable from a faithful split."
        )
        raise VacuousOriginError(msg)


def conserved(
    origin: str, parts: tuple[str, ...], allowed: frozenset[str] = frozenset()
) -> tuple[Loss, ...]:
    """Return the lines this split lost or invented — empty when it conserved everything.

    ⚑ THE MULTISET DIFFERENCE IS TAKEN BOTH WAYS AND THE TWO ARE NOT SYMMETRIC IN TREATMENT.
    `allowed` excuses only the GAINED side, because a part legitimately carries a title and a
    back-link the origin never held. Nothing excuses a line the origin held and no part carries.

    ⚑⚑ THE REFUSAL IS HERE, AT THE PREDICATE, NOT ONLY AT THE CLI. Every caller reaches
    conservation through this function, so guarding the entry point above it would leave the
    library's own callers — the suites and `consider` included — able to obtain the vacuous green
    the CLI can no longer print.
    """
    refuse_vacuous_origin(origin, "conserved")
    have = Counter(body_lines(origin))
    got: Counter[str] = Counter()
    for part in parts:
        got.update(body_lines(part))
    losses = [Loss("dropped", line, n) for line, n in (have - got).items()]
    losses += [Loss("gained", line, n) for line, n in (got - have).items() if line not in allowed]
    return tuple(sorted(losses, key=Loss.rank))


def consider(
    origin: Path, parts: tuple[Path, ...], allowed: frozenset[str] = frozenset()
) -> Report:
    """Return the conservation report for a split already written to disk.

    ⚑ READ FROM DISK, NOT FROM WHAT THE SPLITTER BELIEVES IT WROTE. A cleanup verified against its
    own record of what it created cannot see what actually landed — the same read-your-write
    discipline the codemod arc arrived at after a `--dry-run` verdict described a different
    document than the one that would have been written.

    ⚑⚑ AN UNREADABLE ORIGIN IS REFUSED IN ITS OWN WORDS RATHER THAN BECOMING AN EMPTY STRING.
    Letting the `OSError` reach `conserved` as `""` would land on the vacuous-origin refusal and
    report the right verdict for the wrong reason — the reader would go looking for a file that is
    empty when the file is in fact ABSENT, which is a different repair. The failed `git show` that
    produced the measured vacuous green is exactly this case.
    """
    try:
        text = origin.read_text(encoding="utf-8")
    except OSError as unreadable:
        msg = f"consider: the origin {str(origin)!r} could not be read: {unreadable}"
        raise VacuousOriginError(msg) from unreadable
    refuse_vacuous_origin(text, f"consider: {origin}")
    return Report(
        origin=str(origin),
        parts=tuple(str(part) for part in parts),
        losses=conserved(text, tuple(part.read_text(encoding="utf-8") for part in parts), allowed),
    )


def render(report: Report) -> str:
    """Render a conservation report — the verdict, then every line that failed to conserve.

    ⚑ THE LOSSES ARE PRINTED IN FULL RATHER THAN COUNTED. A count tells a reader that something
    went wrong and leaves them to find it in two documents; the line itself is what locates the
    defect, and there is never a useful number of them to hide behind a summary.
    """
    head = (
        f"{report.origin} -> {len(report.parts)} part(s): "
        f"{'CONSERVED' if report.ok else 'NOT CONSERVED'}"
    )
    rows = [f"   {loss.direction} x{loss.count}  {loss.line[:150]}" for loss in report.losses]
    return "\n".join([head, *rows])


def slice_lines(text: str, spans: tuple[tuple[int, int], ...]) -> str:
    """Return the named 1-indexed INCLUSIVE line spans of `text`, in the order given.

    ⚑⚑ THIS IS THE WRITE HALF OF THE SAME TOOL, AND IT LIVES HERE ON PURPOSE. A split performed by
    hand and checked by `conserved` has two authors, and the checker cannot see a range the author
    mis-transcribed — it only reports that content went missing, after the fact. Slicing from the
    ranges the author actually names makes the transcription itself mechanical, so the guard is
    checking a machine's output rather than adjudicating between two hand copies.

    ⚑ SPANS ARE INCLUSIVE AND 1-INDEXED BECAUSE THAT IS WHAT `mdstruct --headers` PRINTS. Every
    range a caller has in hand comes from that reader, and translating at the call site is exactly
    the off-by-one this repo pays for elsewhere; the conversion belongs in one place.
    """
    lines = text.split("\n")
    return "\n".join("\n".join(lines[start - 1 : end]) for start, end in spans)


def _parse_span(text: str) -> tuple[int, int]:
    """Parse one `START-END` span, refusing anything that is not two positive line numbers.

    ⚑ A REFUSAL, NEVER A BEST EFFORT. A mis-typed span that silently yields an empty slice loses
    content and reports success — the plausible-and-wrong output a mechanical splitter produces
    best, arriving through the operand rather than through the transform.
    """
    start, _, end = text.partition("-")
    if not (start.isdigit() and end.isdigit() and 0 < int(start) <= int(end)):
        msg = f"not a 1-indexed inclusive span: {text!r}"
        raise ValueError(msg)
    return (int(start), int(end))


def _spans_or_refuse(mode: str, args: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    """Parse every span operand, refusing an empty roster as loudly as a malformed one.

    ⚑ NO SPANS AND A BAD SPAN ARE BOTH REFUSALS, because both produce an empty part and an empty
    part is content silently lost. A mode that emitted nothing on an empty roster would report
    success for the one outcome this tool exists to make impossible.
    """
    spans = tuple(_parse_span(arg) for arg in args)
    if not spans:
        msg = f"{mode}: no span given — refusing to produce nothing"
        raise ValueError(msg)
    return spans


def _mode_slice(argv: tuple[str, ...]) -> int:
    """Emit the named line spans of one document to stdout."""
    spans = _spans_or_refuse("--slice", argv[2:])
    sys.stdout.write(slice_lines(Path(argv[1]).read_text(encoding="utf-8"), spans) + "\n")
    return 0


def _mode_part(argv: tuple[str, ...]) -> int:
    """Write one part: a header file, then the origin's named spans, to a destination path.

    ⚑⚑ THE HEADER IS A FILE RATHER THAN A STRING ARGUMENT SO THE PART IS ASSEMBLED, NEVER RETYPED.
    A part whose body is hand-copied out of the origin is a transcription, and the conservation
    guard would then be adjudicating between two hand copies instead of checking a machine's
    output — which is the whole reason the slice half lives in this module.
    """
    spans = _spans_or_refuse("--part", argv[4:])
    body = slice_lines(Path(argv[1]).read_text(encoding="utf-8"), spans)
    head = Path(argv[2]).read_text(encoding="utf-8")
    Path(argv[3]).write_text(head.rstrip("\n") + "\n\n" + body.strip("\n") + "\n", encoding="utf-8")
    return 0


def _mode_verify(argv: tuple[str, ...]) -> int:
    """Report whether the named parts conserve the origin, exiting 1 when they do not."""
    report = consider(Path(argv[0]), tuple(Path(arg) for arg in argv[1:]))
    sys.stdout.write(render(report) + "\n")
    return 0 if report.ok else 1


def only_dropped(report: Report) -> Report:
    """Return `report` with the gained losses removed — the unexcusable direction alone.

    ⚑⚑ THIS IS NOT A WEAKER VERDICT, IT IS A DIFFERENT QUESTION, AND THE ASYMMETRY IS THE POINT.
    A split legitimately GAINS content — each part's title, its concern statement, its back-link to
    the index — so the gained side is expected to be non-empty, and reading it means scanning known
    scaffolding for an unknown rewrite. The DROPPED side has no legitimate non-empty state at all:
    a line the origin held and no part carries is content destroyed, always. Asking for it alone is
    asking the question whose right answer is zero.

    ⚑ IT DOES NOT REPLACE THE FULL REPORT, WHICH STILL CATCHES THE SILENT REWRITE. A caller
    reaching for this because the gained list is noisy has traded the rewrite check for
    readability, and that trade must be made deliberately — which is why it is a separate mode
    rather than a quieter default.
    """
    return Report(
        report.origin,
        report.parts,
        tuple(loss for loss in report.losses if loss.direction == "dropped"),
    )


def _mode_dropped(argv: tuple[str, ...]) -> int:
    """Report ONLY the lines the origin held and no part carries."""
    report = only_dropped(consider(Path(argv[1]), tuple(Path(arg) for arg in argv[2:])))
    sys.stdout.write(render(report) + "\n")
    return 0 if report.ok else 1


# ⚑ A TABLE, NOT AN IF-CHAIN — the per-file gate refused the chain at eight returns and was
# reading the shape correctly. The same correction the ⟡retire-toolmodes dispatch arrived at.
_MODES = {"--slice": _mode_slice, "--part": _mode_part, "--dropped": _mode_dropped}

_USAGE = (
    "usage: doc_split.py <origin.md> <part.md> [<part.md> ...]\n"
    "       doc_split.py --dropped <origin.md> <part.md> [<part.md> ...]\n"
    "       doc_split.py --slice <origin.md> START-END [START-END ...]\n"
    "       doc_split.py --part <origin.md> <header.md> <out.md> START-END [...]\n"
)


def main(argv: tuple[str, ...]) -> int:
    """Verify a split conserved its origin, slice its line spans, or assemble one part.

    ⚑ EXIT 1 ON A LOSS AND 2 ON A BAD INVOCATION, kept distinct because they are fixed in
    different places: a loss is repaired in the documents, a bad invocation at the call site.
    Collapsing them sends a reader hunting for missing content that was never measured.
    """
    if len(argv) < _MIN_ARGS:
        sys.stderr.write(_USAGE)
        return 2
    try:
        return _MODES.get(argv[0], _mode_verify)(argv)
    except ValueError as bad:
        sys.stderr.write(f"doc_split: {bad}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(tuple(sys.argv[1:])))
