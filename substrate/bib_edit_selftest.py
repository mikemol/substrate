# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_edit` — led by the write that erased 533 comment lines.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT COMMENTS SURVIVE AN EDIT, AND IT IS THE ONE THE ORIGIN PAID FOR.
Masking comments to an empty string preserves the LINE count and shrinks the file, so every offset
after the first comment shifts — and a span computed on the masked text then slices the wrong place
in the raw text. MEASURED on the live bib as a diff that erased all 533 comment lines: the whole
adjudication record, deleted by an edit to one field.

⚑⚑ AND THE ONLY WAY TO SEE IT IS TO PUT A COMMENT BEFORE THE EDIT. A fixture whose comments come
after the edited field passes against the broken code, because nothing downstream of the shift is
touched. Every fixture here leads with a comment for that reason.

⚑ THE THREE REFUSALS ARE THREE DIFFERENT OPERATIONS, NOT THREE ERRORS. Editing is not creating, is
not adding a field — and collapsing any pair would make a typo silently succeed as the other verb.
"""

from __future__ import annotations

import re

from substrate import bib_edit

# ⚑ THE GRAMMAR IS THE READER'S. Group 2 of the entry pattern is the key and group 3 the body;
# group 1 of the field pattern is the name and group 2 the value. These mirror the origin's own
# `_ENTRY`/`_FIELD` so a locate cannot disagree with a read.
_GRAMMAR = bib_edit.Grammar(
    entry_re=re.compile(r"(@\w+)\{([^,]+),(.*?)\n\}", re.DOTALL),
    field_re=re.compile(r"(\w[\w-]*)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}"),
)

# ⚑⚑ THE COMMENT COMES FIRST, DELIBERATELY. A fixture with its comments after the edited field
# passes against the length-shrinking mask, because nothing after the shift is touched.
_TEXT = """\
% an adjudication note that must survive
% a second line of it
@misc{A,
  section  = {s},
  claim    = {the original claim},
  check    = {item:A}
}

@misc{B,
  claim    = {beta},
  check    = {item:B}
}
"""

_ENTRIES = {
    "A": {"section": "s", "claim": "the original claim", "check": "item:A"},
    "B": {"claim": "beta", "check": "item:B"},
}


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def edit(key: str, field: str, value: str) -> str | bib_edit.Refusal:
        return bib_edit.set_field(_TEXT, (key, field, value), _ENTRIES, _GRAMMAR)

    # ── the mask preserves length, which is what makes a span portable ───────
    masked = bib_edit.mask_comments(_TEXT)
    check("masking preserves the total length", passed=len(masked) == len(_TEXT))
    check("and the line count", passed=masked.count("\n") == _TEXT.count("\n"))
    check("the comment text is gone from the masked copy", passed="adjudication" not in masked)
    check("but non-comment lines are untouched", passed="@misc{A," in masked)

    # ── THE CORRUPTING-WRITE CASE ────────────────────────────────────────────
    # ⚑⚑⚑ THE EDIT MUST NOT TOUCH THE COMMENTS. This is the case that fails loudly against the
    # shrinking mask, because the span lands earlier than intended by exactly the bytes removed.
    done = edit("A", "claim", "a replaced claim")
    check("editing a field succeeds", passed=isinstance(done, str))
    check(
        "and BOTH leading comments survive verbatim",
        passed=isinstance(done, str)
        and "% an adjudication note that must survive" in done
        and "% a second line of it" in done,
    )
    check("the new value is written", passed=isinstance(done, str) and "a replaced claim" in done)
    check(
        "and the old value is gone",
        passed=isinstance(done, str) and "the original claim" not in done,
    )
    # ⚑ THE REST OF THE FILE IS UNTOUCHED — a shifted span corrupts what follows, not only what it
    # replaces, so a sibling entry is the second witness.
    check(
        "a sibling entry is unchanged",
        passed=isinstance(done, str) and "@misc{B,\n  claim    = {beta}," in done,
    )
    check(
        "and the edit changes length by exactly the value delta",
        passed=isinstance(done, str)
        and len(done) - len(_TEXT) == len("a replaced claim") - len("the original claim"),
    )

    # ── the three refusals, each a different operation ───────────────────────
    unknown = edit("NOSUCH", "claim", "x")
    check("an unknown key refuses", passed=isinstance(unknown, bib_edit.Refusal))
    check(
        "and says adding an entry is a different operation",
        passed=isinstance(unknown, bib_edit.Refusal) and "different operation" in unknown.message,
    )

    absent = edit("B", "section", "x")
    check("a field the entry does not carry refuses", passed=isinstance(absent, bib_edit.Refusal))
    check(
        "and lists what the entry DOES carry",
        passed=isinstance(absent, bib_edit.Refusal) and "claim" in absent.message,
    )

    unbalanced = edit("A", "claim", "an {unclosed value")
    check("an unbalanced value refuses", passed=isinstance(unbalanced, bib_edit.Refusal))
    check(
        "and says the grammar would truncate it",
        passed=isinstance(unbalanced, bib_edit.Refusal) and "truncate" in unbalanced.message,
    )

    # ⚑ A BALANCED NESTED VALUE IS ACCEPTED — the refusal must not be a blanket brace ban.
    check(
        "a balanced nested value is accepted",
        passed=isinstance(edit("A", "claim", "a {nested} value"), str),
    )

    # ── locate finds the value span, not the whole field ─────────────────────
    span = bib_edit.locate(_TEXT, "A", "claim", _GRAMMAR)
    check("the span is located", passed=span is not None)
    check(
        "and it covers exactly the value",
        passed=span is not None and _TEXT[span[0] : span[1]] == "the original claim",
    )
    check(
        "a field that is not there locates nothing",
        passed=bib_edit.locate(_TEXT, "A", "nosuch", _GRAMMAR) is None,
    )
    check(
        "and neither does an entry that is not there",
        passed=bib_edit.locate(_TEXT, "NOSUCH", "claim", _GRAMMAR) is None,
    )

    # ── add_field WIDENS an entry, and the three verbs partition ─────────────
    # ⚑⚑⚑ THIS VERB EXISTS BECAUSE THE OTHER TWO LEFT A GAP NEITHER COULD REACH: `set_field`
    # refuses a field the entry lacks and the entry writer refuses a key that exists, so an entry
    # filed WITHOUT a field was fixable by neither. Measured on a peer's live floor, where a
    # corroboration missing `note` read back as `kind ? by ?`.
    def widen(key: str, field: str, value: str) -> str | bib_edit.Refusal:
        return bib_edit.add_field(_TEXT, (key, field, value), _ENTRIES, _GRAMMAR)

    added = widen("B", "section", "s")
    check("adding a field an entry lacks succeeds", passed=isinstance(added, str))
    check(
        "and the new field is present", passed=isinstance(added, str) and "section  = {s}" in added
    )
    check(
        "and the comments survive",
        passed=isinstance(added, str) and added.startswith("% an adjudication note"),
    )
    # ⚑ AFTER THE LAST FIELD, NOT BEFORE THE FIRST — prepending changes the entry's SHAPE.
    # ⚑⚑ THE POSITION IS TESTED INSIDE `B`'s ENTRY, AND MY FIRST CUT TESTED IT FILE-WIDE. It
    # compared `.index("check…")` against `.index("section…")` over the whole text — but entry `A`
    # carries both fields and comes FIRST, so the assertion measured A's layout while claiming to
    # measure B's. A whole-file index answering a per-entry question is the same population defect
    # this drain keeps recording, arriving in an assertion.
    b_entry = added[added.index("@misc{B,") :] if isinstance(added, str) else ""
    check(
        "the field lands after the entry's existing fields",
        passed=b_entry.index("check") < b_entry.index("section"),
    )
    check(
        "and the entry still closes", passed=isinstance(added, str) and added.rstrip().endswith("}")
    )
    check(
        "a sibling entry is untouched",
        passed=isinstance(added, str) and "claim    = {the original claim}" in added,
    )

    # ⚑⚑ THE PARTITION IS ASSERTED IN BOTH DIRECTIONS. A field that EXISTS is `--set`'s job, and
    # an entry that does not exist is `--add`'s.
    exists = widen("A", "claim", "x")
    check("adding a field that already exists refuses", passed=isinstance(exists, bib_edit.Refusal))
    check(
        "and points at --set",
        passed=isinstance(exists, bib_edit.Refusal) and "--set" in exists.message,
    )

    absent_key = widen("NOSUCH", "claim", "x")
    check(
        "adding a field to an unknown entry refuses",
        passed=isinstance(absent_key, bib_edit.Refusal),
    )
    check(
        "and points at --add",
        passed=isinstance(absent_key, bib_edit.Refusal) and "--add" in absent_key.message,
    )

    check(
        "an unbalanced value refuses on addfield too",
        passed=isinstance(widen("B", "note", "an {unclosed"), bib_edit.Refusal),
    )

    # ── the source text is never mutated ─────────────────────────────────────
    # ⚑ DECIDE, THEN APPLY. A dry run and a real run share this path, so a function that mutated
    # its input would make the preview and the write disagree.
    check(
        "the input text is unchanged after an edit",
        passed=_TEXT.startswith("% an adjudication note"),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-edit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
