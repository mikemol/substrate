# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bib_pairs` — led by the origin's own measured failure.

⚑⚑⚑ THE FIRST CASE IS THE ORIGIN'S DEFECT, TYPED AS IT WAS MEASURED. `claim=the bib reader has…`
arrived as `claim={the}` with `[tag=0]` parsed as a FIELD NAMED `[bib-kernel-unwitnessed`. A
splitter that silently truncates a claim to its first word and invents a field is worse than one
that refuses: the entry was written, looked plausible, and said something the author never wrote.

⚑⚑ SO THE CASES ASSERT THE VALUE, NOT THE FIELD COUNT. Counting fields would pass on the defect —
two pairs went in and two came out. Only reading the VALUE back sees the truncation.

⚑ AND THE LAST CASE IS A DIFFERENTIAL ONE. A drain is faithful only if the replacement AGREES with
the origin, and asserting that from my reading of its comments is the infer-don't-read shape this
whole arc keeps recording. The origin's algorithm is transcribed below and run beside the module on
every case, so the agreement is checked by a program rather than believed.
"""

from __future__ import annotations

import re

from substrate import bib_pairs

# The origin's splitter, transcribed from `scratch/bibstruct.py`'s `--add` arm. ⚑ IT IS A COPY ON
# PURPOSE, AND IT IS NOT A SECOND AUTHORITY: it exists to be DIFFERENCED against the module, and
# the day the origin is replaced by that module this case retires with it. A copy kept to prove
# equality is the opposite of a copy kept to be used.
_ORIGIN_START = re.compile(r"^[\w-]+=")


def _origin(operands: list[str]) -> tuple[str | None, dict[str, str]]:
    """Return what `scratch/bibstruct.py`'s `--add` arm would parse from these operands."""
    akey = next((a for a in operands if "=" not in a), None)
    pairs: list[str] = []
    cur: str | None = None
    for a in operands:
        if a == akey and cur is None:
            continue
        if _ORIGIN_START.match(a):
            if cur is not None:
                pairs.append(cur)
            cur = a
        elif cur is not None:
            cur += " " + a
    if cur is not None:
        pairs.append(cur)
    fields: dict[str, str] = {}
    for pair in pairs:
        name, _eq, value = pair.partition("=")
        fields[name.strip()] = value.strip()
    return akey, fields


# Every operand sequence both implementations are differenced over.
_CORPUS: tuple[tuple[str, ...], ...] = (
    ("K", "claim=the", "bib", "reader", "has", "[tag=0]"),
    ("K", "claim=a claim", "check=item:X"),
    ("K", "claim=c", "rests-on=P", "from=Q"),
    ("K", "claim=the K case", "check=item:X"),
    ("K", "claim= spaced "),
    ("K", "claim="),
    ("K",),
    (),
    ("claim=c",),
)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the origin's measured failure, reproduced ────────────────────────────
    # ⚑ ARGV AS THE SHELL WOULD DELIVER IT: the quoted value arrives as separate words.
    got = bib_pairs.split(["K", "claim=the", "bib", "reader", "has", "[tag=0]"])
    check("the entry key is the first =-free token", passed=got.key == "K")
    check(
        "a multi-word value is rejoined whole",
        passed=got.fields.get("claim") == "the bib reader has [tag=0]",
    )
    check(
        "and `[tag=0]` did NOT become a field",
        passed=not any(name.startswith("[") for name in got.fields),
    )
    check(
        "so the claim is not truncated to its first word", passed=got.fields.get("claim") != "the"
    )

    # ── a bare name followed by `=` DOES start a field ───────────────────────
    # ⚑ THE OTHER DIRECTION. If the start rule were tightened until nothing matched, every case
    # above would pass and the splitter would produce one giant field.
    two = bib_pairs.split(["K", "claim=a claim", "check=item:X"])
    check("a second bare-name pair starts a new field", passed=two.fields.get("check") == "item:X")
    check("and does not continue the first", passed=two.fields.get("claim") == "a claim")

    # ⚑ A HYPHENATED FIELD NAME IS A BARE NAME — `rests-on` is a live field, so a start rule
    # spelled `\w+` alone would silently fold it into the previous value.
    edges = bib_pairs.split(["K", "claim=c", "rests-on=P", "from=Q"])
    check("a hyphenated field name starts a pair", passed=edges.fields.get("rests-on") == "P")
    check("and so does the one after it", passed=edges.fields.get("from") == "Q")

    # ── the key is skipped ONCE, and only before a field starts ──────────────
    # ⚑⚑ A WORD IN A VALUE THAT REPEATS THE KEY MUST SURVIVE. Skipping every occurrence would
    # silently delete a word from the middle of a sentence — the same silent-truncation class as
    # the case above, arriving through the fix rather than the defect.
    echo = bib_pairs.split(["K", "claim=the K case", "check=item:X"])
    check("a value word matching the key is kept", passed=echo.fields.get("claim") == "the K case")

    # ── the degenerate inputs ────────────────────────────────────────────────
    # ⚑ NEITHER IS AN ERROR HERE. The caller decides what an unusable parse means; this module
    # reports what it found, and `usable` is the predicate it offers.
    check("no operands parses to nothing usable", passed=not bib_pairs.split([]).usable)
    check("a key with no fields is not usable", passed=not bib_pairs.split(["K"]).usable)
    check("fields with no key are not usable", passed=not bib_pairs.split(["claim=c"]).usable)
    check("a key with one field IS usable", passed=bib_pairs.split(["K", "claim=c"]).usable)

    # ── whitespace around the name and value is stripped ─────────────────────
    check(
        "the field name and value are stripped",
        passed=bib_pairs.split(["K", "claim= spaced "]).fields.get("claim") == "spaced",
    )

    # ── an empty value is preserved, not dropped ─────────────────────────────
    # ⚑ AN EMPTY FIELD IS A STATEMENT — the caller's required-field check must SEE it to refuse
    # it. Dropping it here would turn a refusable entry into a silently absent field.
    check(
        "an empty value is kept as an empty field",
        passed=bib_pairs.split(["K", "claim="]).fields == {"claim": ""},
    )

    # ── the usage text names the required fields ─────────────────────────────
    check(
        "the usage names both required fields",
        passed="claim" in bib_pairs.USAGE and "check" in bib_pairs.USAGE,
    )
    check("and says editing an existing field is --set", passed="--set" in bib_pairs.USAGE)

    # ── the differential: the module AGREES with the origin, case by case ────
    # ⚑⚑ THIS IS THE CASE THAT MAKES THE DRAIN FAITHFUL RATHER THAN PLAUSIBLE. Every case above
    # asserts what I believe the behaviour should be; this one asserts that the behaviour is the
    # ORIGIN'S, which is a different claim and the one a replacement actually owes.
    for operands in _CORPUS:
        want_key, want_fields = _origin(list(operands))
        got = bib_pairs.split(list(operands))
        check(
            f"agrees with the origin on {list(operands)}",
            passed=got.key == want_key and got.fields == want_fields,
        )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-pairs selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
