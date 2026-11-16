# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bib_roundtrip` — led by the field the probe could not SEE.

⚑⚑⚑ THE QUOTED-FIELD CASE IS THE INSTRUMENT'S OWN FAILURE, REPRODUCED. The origin's probe scanned
with the PARSER'S character class, so it could only ever see what the parser sees — and a fixture
holding `'rests-on' = {A}`, quoted and well-formed, read back as *"0 unaccounted-for constructs —
this read is TOTAL"* while the bytes held four fields and the parse listed three. On a peer's live
floor that hid 56 edges: 19 of 20 workarounds had their grounding edge invisible, and unquoting
moved the count from 39 to 98 with every surface green throughout.

⚑⚑ SO THIS CASE FAILS AGAINST A PROBE THAT RE-DERIVES THE GRAMMAR IT AUDITS, which is exactly what
a totality check must not do. It is the reason `ASSIGN` is looser than the field pattern.

⚑ AND THE FALSE-POSITIVE CONTROL IS EQUALLY LOAD-BEARING. A claim discussing `p+q+r = 0 over F2`
was reported as an unparsed field — use-versus-mention, committed by the instrument built to catch
it. A probe that flags prose is as useless as one that flags nothing, so both directions are cased.
"""

from __future__ import annotations

from substrate import bib_parse, bib_roundtrip, corpus

# A file the parser accounts for completely.
_CLEAN = """\
% a note the probe must not read as content
@misc{A,
  section  = {s},
  claim    = {alpha},
  check    = {item:A}
}
"""

# ⚑⚑⚑ THE QUOTED FIELD. Well-formed BibTeX the field grammar cannot see — so the parse lists three
# fields where the bytes assign four, and only a LOOSER scan can report the difference.
_QUOTED = """\
@misc{A,
  section  = {s},
  'rests-on' = {B},
  claim    = {alpha},
  check    = {item:A}
}
"""

# ⚑ THE USE-VERSUS-MENTION CONTROL: an `=` inside a parsed VALUE is not an assignment.
_PROSE = """\
@misc{A,
  section  = {s},
  claim    = {a Fano line where p+q+r = 0 over F2},
  check    = {item:A}
}
"""

# A header the parse cannot reach: the closing brace is indented, so the entry grammar misses it.
_VANISHED = """\
@misc{A,
  claim    = {alpha},
  check    = {item:A}
  }
"""

_DUPLICATE = """\
@misc{A,
  claim    = {first},
  check    = {item:A}
}

@misc{A,
  claim    = {second},
  check    = {item:A}
}
"""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def probe(text: str) -> tuple[bib_roundtrip.Loss, ...]:
        return bib_roundtrip.probe(text, bib_parse.parse(text))

    # ── a clean file is TOTAL ────────────────────────────────────────────────
    clean = probe(_CLEAN)
    check("a file the parse accounts for reports no losses", passed=clean == ())
    check("and reads as total", passed=bib_roundtrip.total(clean))
    # ⚑ THE COMMENT IS NOT CONTENT. A probe masking differently from the parse measures a
    # different file and reports the difference as a defect.
    check(
        "a comment is not reported as an unparsed construct",
        passed=not any("note" in loss.what for loss in clean),
    )

    # ── THE QUOTED FIELD: the case that fails against a self-derived grammar ─
    quoted = probe(_QUOTED)
    check(
        "a quoted field name is REPORTED as unaccounted for",
        passed=any(loss.kind == "field-unparsed" for loss in quoted),
    )
    check(
        "and the raw spelling is named, quotes included",
        passed=any("'rests-on'" in loss.what for loss in quoted),
    )
    check("so the read is NOT total", passed=not bib_roundtrip.total(quoted))
    # ⚑ THE PARSE GENUINELY MISSES IT — the case is about a real blind spot, not a probe artifact.
    check(
        "...and the parser indeed did not produce that field",
        passed="rests-on" not in bib_parse.parse(_QUOTED).get("A", {}),
    )
    check("the loss names its line", passed=any("line " in loss.detail for loss in quoted))

    # ── the use-versus-mention control ───────────────────────────────────────
    # ⚑⚑ A PROBE THAT FLAGS PROSE IS AS USELESS AS ONE THAT FLAGS NOTHING.
    prose = probe(_PROSE)
    check("an `=` inside a parsed value is not an assignment", passed=prose == ())
    check("so a claim discussing an equation reads as total", passed=bib_roundtrip.total(prose))

    # ── a header the parse cannot reach ──────────────────────────────────────
    vanished = probe(_VANISHED)
    check(
        "a header the parse misses is reported",
        passed=any(loss.kind == "entry-vanished" for loss in vanished),
    )
    check("and the key is named", passed=any(loss.what == "A" for loss in vanished))

    # ── a duplicate key is a SILENT LOSS, not a duplicate ────────────────────
    # ⚑ THE PARSE KEEPS THE LAST, so an earlier declaration is discarded with no signal. The entry
    # map cannot show what it overwrote; only this probe can.
    duplicate = probe(_DUPLICATE)
    check(
        "a repeated header is reported",
        passed=any(loss.kind == "duplicate-key" for loss in duplicate),
    )
    check(
        "and the report says the parse keeps one",
        passed=any("keeps 1" in loss.detail for loss in duplicate),
    )

    # ── the live corpus ──────────────────────────────────────────────────────
    # ⚑⚑ A GREEN HERE IS AN ALGEBRA RESULT ABOUT THIS INPUT, NOT A CLAIM THE KERNEL IS EMPTY. The
    # case asserts the probe RUNS over the real file and reports something legible either way.
    live = corpus.ROOT / "catalog" / "worklist" / "warrants.bib"
    if live.exists():
        text = live.read_text(encoding="utf-8")
        losses = bib_roundtrip.probe(text, bib_parse.parse(text))
        check("the live worklist bib reads as total", passed=bib_roundtrip.total(losses))
        check(
            "and every loss, if any, carries a kind and a detail",
            passed=all(loss.kind and loss.detail for loss in losses),
        )
    else:
        check("the live bib is absent, so its cases are skipped", passed=True)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-roundtrip selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
