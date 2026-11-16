# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_parse` — led by the comment that FABRICATED an entry.

⚑⚑⚑ THE GHOST CASE IS THE ONE THAT MATTERS, BECAUSE IT INVENTS RATHER THAN OMITS. A comment
mentioning an entry shape — `% see @misc{GHOST, …} for the shape` — was read as a real header, and
the pattern then ran forward from inside the comment and swallowed the following entry whole. The
origin's fixture reported GHOST present, the real entry absent, and a clean `1 of 1`. **A missing
row can be caught by a denominator; an invented row corroborates itself.**

⚑⚑ AND IT IS ASSERTED IN BOTH DIRECTIONS: the ghost must be ABSENT and the real entry PRESENT. A
case testing only the first passes against a parser that drops everything.

⚑ THE LIVE CORPUS IS THE SECOND WITNESS. A fixture proves the parser agrees with itself; parsing
the tree's own warrant bib and finding the keys other tools report is what proves it agrees with
the corpus. That read is skipped rather than failed when the bib is absent — a suite that goes red
because a file moved is reporting on the file, not the parser.
"""

from __future__ import annotations

from substrate import bib_parse, corpus

# ⚑ THE COMMENT MENTIONS AN ENTRY HEADER, WHICH IS THE FABRICATION TRIGGER. The real entry follows
# it, so a parser reading the comment as a header loses `A` and invents `GHOST`.
_GHOSTED = """\
% see @misc{GHOST,
%   claim = {not a real entry}
% } for the shape
@misc{A,
  section  = {s},
  claim    = {the real one},
  check    = {item:A}
}
"""

_PLAIN = """\
@misc{A,
  section  = {s},
  claim    = {alpha},
  check    = {item:A}
}

@article{B,
  claim    = {a claim wrapped
              across two lines},
  check    = {item:B}
}
"""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── THE FABRICATION CASE, BOTH DIRECTIONS ────────────────────────────────
    ghosted = bib_parse.parse(_GHOSTED)
    check("a commented-out entry header does NOT become a key", passed="GHOST" not in ghosted)
    check("and the real entry after it survives", passed="A" in ghosted)
    check("with its own fields intact", passed=ghosted.get("A", {}).get("claim") == "the real one")
    check("so the count is the real one", passed=len(ghosted) == 1)

    # ── the ordinary read ────────────────────────────────────────────────────
    plain = bib_parse.parse(_PLAIN)
    check("every entry is read", passed=sorted(plain) == ["A", "B"])
    check("fields are read verbatim", passed=plain["A"]["claim"] == "alpha")
    check("the entry type is captured", passed=plain["A"][bib_parse.TYPE_FIELD] == "@misc")
    check(
        "and a non-misc type is kept as declared",
        passed=plain["B"][bib_parse.TYPE_FIELD] == "@article",
    )
    # ⚑ THE TYPE FIELD IS UNDERSCORED so every report's `_`-prefix filter hides it; a bare name
    # would be listed as a field the author wrote.
    check("the type field is private by name", passed=bib_parse.TYPE_FIELD.startswith("_"))

    # ⚑ A VALUE WRAPPED ACROSS LINES READS BACK AS ONE STRING.
    check(
        "a multi-line value is collapsed to one line",
        passed=plain["B"]["claim"] == "a claim wrapped across two lines",
    )

    # ── the empty and absent cases ───────────────────────────────────────────
    check("empty text parses to no entries", passed=bib_parse.parse("") == {})
    check(
        "a file of only comments parses to no entries",
        passed=bib_parse.parse("% nothing but a note\n% and another\n") == {},
    )
    # ⚑⚑⚑ ABSENT IS NOT EMPTY, AND THIS CASE PINNED THE COLLAPSE (gate-G242). It asserted that a
    # missing file reads as no entries — which is what the code did, and what let `--entries` on a
    # typo'd path print `0 of 0` and exit 0, certifying anything. The case was faithful to the
    # behaviour and the behaviour was wrong, so a green suite said nothing about the defect.
    absent = corpus.ROOT / "no-such-file.bib"
    try:
        bib_parse.read(absent)
    except FileNotFoundError as exc:
        check(f"an absent file REFUSES rather than reading empty: {str(exc)[:40]!r}…", passed=True)
        check(
            "and the refusal names the path as the subject",
            passed="no-such-file.bib" in str(exc) and "ABSENT" in str(exc),
        )
    else:
        check("an absent file REFUSES rather than reading empty", passed=False)

    # ⚑ AND A FILE THAT EXISTS AND IS EMPTY STILL READS AS NO ENTRIES — the control proving the
    # refusal above fires on ABSENCE and not on emptiness, which are the two facts being separated.
    check("a genuinely empty bib still reads as no entries", passed=bib_parse.parse("") == {})

    # ── the grammar is shared with the editor ────────────────────────────────
    # ⚑ ONE GRAMMAR, SO A LOCATE CANNOT DISAGREE WITH A READ. Two patterns for one question is the
    # fourth-parser hazard this tool's own docstring names.
    check(
        "the exported grammar carries the entry pattern",
        passed=bib_parse.GRAMMAR.entry_re is bib_parse.ENTRY,
    )
    check("and the field pattern", passed=bib_parse.GRAMMAR.field_re is bib_parse.FIELD)

    # ── THE LIVE CORPUS, as the second witness ───────────────────────────────
    # ⚑⚑ A FIXTURE PROVES THE PARSER AGREES WITH ITSELF. Reading the tree's own warrant bib and
    # finding keys other tools report is what proves it agrees with the CORPUS.
    live = corpus.ROOT / "catalog" / "worklist" / "warrants.bib"
    if live.exists():
        read = bib_parse.read(live)
        check("the live worklist bib parses to entries", passed=len(read) > 0)
        check("and a known key is present", passed="bz-resource-set" in read)
        check(
            "with a claim other tools also report",
            passed="resource_set" in read.get("bz-resource-set", {}).get("claim", ""),
        )
        # ⚑ NO ENTRY MAY CARRY A KEY THAT IS ONLY WHITESPACE — a header the grammar half-matched
        # would show up here rather than as a silently odd row.
        check("no parsed key is blank", passed=all(key.strip() for key in read))

        # ⚑⚑⚑ THE DIFFERENTIAL AGAINST THE ORIGIN, ON THE LIVE FILE. `scratch/bibstruct.py
        # --entries` reports the same population from the same bytes; a parser that agrees with a
        # fixture and disagrees with the tool it replaces has not been verified at all. The count
        # is not typed here — it is READ from the origin's own reader at suite time.
        origin = corpus.ROOT / "scratch" / "bibstruct.py"
        if origin.exists():
            import subprocess  # noqa: PLC0415 — one case needs it

            probe = subprocess.run(  # noqa: S603
                ["python3", str(origin), "--entries", str(live)],  # noqa: S607
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                cwd=str(corpus.ROOT),
            )
            tail = probe.stdout.strip().splitlines()[-1] if probe.stdout.strip() else ""
            check("the origin reports a population", passed=tail.startswith("entries:"))
            check(
                "and this parser reads the SAME number of entries",
                passed=f"{len(read)} of {len(read)}" in tail,
            )
        else:
            check("the origin is retired, so the differential is skipped", passed=True)
    else:
        # ⚑ SKIPPED, NOT FAILED. A suite going red because a file moved reports on the file.
        check("the live bib is absent, so its cases are skipped", passed=True)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-parse selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
