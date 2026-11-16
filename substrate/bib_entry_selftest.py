# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_entry` — and the two-population case is the one that was measured.

⚑⚑⚑ THE LOAD-BEARING PAIR IS THE SAME EDGE, TWO VERDICTS, DECIDED BY WHICH POPULATION IS ASKED. A
peer split a 242-entry monolith into five per-genre bibs and the very next write was REFUSED as
dangling when its target existed in a sibling file. The duplicate test must read the TARGET and the
edge test must read the CORPUS, so both directions are cased: an edge resolving only in a sibling is
accepted, and a key existing only in a sibling is still writable.

⚑⚑ THE BRACE CASE IS NOT COSMETIC. An unbalanced field swallows every entry after it, so the file
still PARSES and reports fewer entries — a silent loss, which is why it is refused at write time
rather than found by the round-trip probe afterwards.

⚑ AND THE RENDER CASES PIN THE ORDER because the projection's diff readability depends on it. A
field name nobody declared must not reshuffle the entries that came before it.
"""

from __future__ import annotations

from substrate import bib_entry

# The population the write target already holds.
_TARGET = frozenset({"A", "B"})

# The population the corpus holds — the target's keys PLUS a sibling bib's.
# ⚑ `SIB` EXISTS ONLY IN THE SIBLING, which is exactly the case the peer measured.
_CORPUS = _TARGET | {"SIB"}

_OK = {"claim": "a claim", "check": "item:K"}


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def refusal(key: str, fields: dict[str, str]) -> bib_entry.Refusal | None:
        return bib_entry.validate(key, fields, target_keys=_TARGET, corpus_keys=_CORPUS)

    # ── a clean entry is accepted ────────────────────────────────────────────
    check("a new key with claim and check is accepted", passed=refusal("NEW", _OK) is None)

    # ── the duplicate test reads the TARGET ──────────────────────────────────
    dup = refusal("A", _OK)
    check("a key the target already holds is refused", passed=dup is not None)
    check(
        "and the refusal names --set as the editing verb",
        passed=dup is not None and "--set" in dup.message,
    )

    # ⚑⚑ A KEY EXISTING ONLY IN A SIBLING IS STILL WRITABLE HERE. Widening the duplicate test to
    # the corpus would refuse a key that legitimately appears in another genre's bib.
    check("a key existing only in a SIBLING is not a duplicate", passed=refusal("SIB", _OK) is None)

    # ── the edge test reads the CORPUS ───────────────────────────────────────
    # ⚑⚑⚑ THE MEASURED FALSE REFUSAL. A corroboration resting on a use-case in a sibling bib was
    # refused as dangling when it is not, and the entry shipped with its edge demoted to prose.
    check(
        "an edge into a SIBLING's key resolves",
        passed=refusal("NEW", {**_OK, "rests-on": "SIB"}) is None,
    )
    check(
        "an edge into the target's own key resolves",
        passed=refusal("NEW", {**_OK, "from": "A"}) is None,
    )

    dangling = refusal("NEW", {**_OK, "from": "GONE"})
    check("an edge into a key nobody declares is refused", passed=dangling is not None)
    check(
        "and the refusal names the field and the target",
        passed=dangling is not None and "from" in dangling.message and "GONE" in dangling.message,
    )
    # ⚑ THE REFUSAL MUST NAME `--corpus`, because 'not in the population' is NOT 'does not exist'
    # and the remedy is to state the scope rather than to delete the edge.
    check(
        "and it names --corpus as the remedy",
        passed=dangling is not None and "--corpus" in dangling.message,
    )

    # ⚑ A SELF-EDGE IS NOT DANGLING — the entry being written is not yet in either population.
    check(
        "an edge to the entry's own key is allowed",
        passed=refusal("NEW", {**_OK, "from": "NEW"}) is None,
    )

    # ── the required fields ──────────────────────────────────────────────────
    for name in bib_entry.REQUIRED:
        partial = {k: v for k, v in _OK.items() if k != name}
        got = refusal("NEW", partial)
        check(f"an entry with no {name} is refused", passed=got is not None)
        check(
            f"...and the refusal says what it got instead of {name}",
            passed=got is not None and "got:" in got.message,
        )

    empty = refusal("NEW", {})
    check(
        "an entry with no fields says it got none",
        passed=empty is not None and "none" in empty.message,
    )

    # ── unbalanced braces ────────────────────────────────────────────────────
    brace = refusal("NEW", {**_OK, "claim": "an {unclosed value"})
    check("an unbalanced field is refused", passed=brace is not None)
    check("and the refusal names the field", passed=brace is not None and "claim" in brace.message)
    check(
        "a balanced nested value is accepted",
        passed=refusal("NEW", {**_OK, "claim": "a {nested} value"}) is None,
    )

    # ── edge targets are split on commas AND whitespace ──────────────────────
    both = dict(bib_entry.edge_targets({"enables": "A, SIB"}))
    check(
        "a comma-separated edge field yields every target",
        passed=set(bib_entry.edge_targets({"enables": "A, SIB"}))
        == {("enables", "A"), ("enables", "SIB")},
    )
    check(
        "and an absent edge field yields none",
        passed=bib_entry.edge_targets({"claim": "no edges here"}) == (),
    )
    del both

    # ── the witness key is read from the check ───────────────────────────────
    check(
        "an item check names its witness key",
        passed=bib_entry.witness_key("item:T28-edges") == "T28-edges",
    )
    check(
        "a traces check names no item witness",
        passed=bib_entry.witness_key("traces:some/path.py#needle") is None,
    )
    check(
        "and whitespace around the check is ignored",
        passed=bib_entry.witness_key("  item:K  ") == "K",
    )

    # ── rendering keeps the file's field order ───────────────────────────────
    text = bib_entry.render("K", {"check": "item:K", "claim": "c", "section": "s"})
    check("the rendered entry opens with its key", passed=text.startswith("\n@misc{K,"))
    check(
        "section precedes claim, which precedes check",
        passed=text.index("section") < text.index("claim") < text.index("check"),
    )
    check("the last field carries no trailing comma", passed="},\n}" not in text)
    check("and the entry closes", passed=text.rstrip().endswith("}"))

    # ⚑ AN UNDECLARED FIELD FOLLOWS THE DECLARED ONES rather than reshuffling them.
    extra = bib_entry.render("K", {"check": "item:K", "claim": "c", "zzz": "later"})
    check(
        "an undeclared field renders after the declared ones",
        passed=extra.index("claim") < extra.index("zzz"),
    )

    # ── the rendered shape is the ORIGIN'S, byte for byte ────────────────────
    # ⚑⚑⚑ CAPTURED FROM A LIVE DRY RUN OF `scratch/bibstruct.py --add`, not transcribed from its
    # source. The swap must not change how an entry renders: every future diff in every warrant
    # bib is measured against this shape, so a one-space difference would rewrite the appearance
    # of every subsequent write. `check` carries a `traces:` verb because the origin's `item:`
    # guard REFUSES before it renders — the defect this drain exists to remove, blocking the
    # comparison it is being compared against.
    origin_shape = (
        "\n@misc{ZZ-render-probe,\n"
        "  section  = {finding},\n"
        "  claim    = {a probe of the rendered shape},\n"
        "  check    = {traces:substrate/bib_entry.py#FIELD_ORDER}\n"
        "}\n"
    )
    mine = bib_entry.render(
        "ZZ-render-probe",
        {
            "section": "finding",
            "claim": "a probe of the rendered shape",
            "check": "traces:substrate/bib_entry.py#FIELD_ORDER",
        },
    )
    check("the rendered entry is byte-identical to the origin's", passed=mine == origin_shape)

    # ── append is pure ───────────────────────────────────────────────────────
    before = "@misc{OLD,\n  claim = {x},\n}\n"
    after = bib_entry.append(before, "K", _OK)
    check("appending keeps what was there", passed=after.startswith("@misc{OLD,"))
    check("and adds the new entry", passed="@misc{K," in after)
    check("and the original text is unchanged", passed=before == "@misc{OLD,\n  claim = {x},\n}\n")

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-entry selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
