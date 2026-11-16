# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.census_call` — the census-calling boundary.

⚑ EVERY CASE HERE IS A FAILURE MODE, and that is the point. The one thing this boundary
must never do is let an unmeasurable gate read as clean, so each way of failing has to
produce a REASON rather than an empty set. A suite that only checked the happy path would
pass on a boundary that silently swallowed all four.

⚑⚑ THE FIXTURES ARE MODULE OBJECTS BUILT HERE, not gates loaded from the tree. A case
loading a real gate would change verdict whenever that gate changed, which makes it a
measurement rather than a case — and would run a corpus-scale census to assert a
three-line contract.
"""

from __future__ import annotations

from types import ModuleType

from substrate import census_call


def _module(name: str, census: object) -> ModuleType:
    """Build a module carrying `census` as its attribute, or nothing when None."""
    mod = ModuleType(name)
    if census is not None:
        mod.census = census  # type: ignore[attr-defined]
    return mod


def _raises() -> set[str]:
    """Fail the way a gate with a deleted dependency fails."""
    msg = "no module named 'gone'"
    raise ImportError(msg)


def _names(lines: list[str]) -> set[str]:
    """Stand in for a declaration scanner: a name set derived from its argument."""
    return {f"n{len(lines)}"}


def _mask(text: str) -> str:
    """Stand in for a comment masker: TEXT in, TEXT out."""
    return text.upper()


def _scanner() -> ModuleType:
    """Build a module carrying both argument-taking shapes."""
    mod = ModuleType("scanner")
    mod.names = _names  # type: ignore[attr-defined]
    mod.mask = _mask  # type: ignore[attr-defined]
    return mod


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the ARGUMENT-TAKING boundaries, typed by RETURN SHAPE ────────────────
    # ⚑⚑⚑ THE STRING/SET CONFUSION IS THE BUG THESE TWO EXIST TO PREVENT, and it is why
    # they are separate functions rather than one. A comment masker returns TEXT; run it
    # through the key-set narrower and the string iterates into single CHARACTERS — a
    # plausible-looking value that is not the answer, and one no count would catch.
    scanner = _scanner()

    got, why = census_call.str_set_call(scanner, "names", ["a", "b"], "scanner")
    check("a scanner call narrows to a key set", passed=got == {"n2"} and why is None)

    text, why = census_call.text_call(scanner, "mask", "abc", "scanner")
    check("a text call returns text", passed=text == "ABC" and why is None)

    # ⚑ TEXT THROUGH THE TEXT BOUNDARY STAYS WHOLE. Asserted directly, because the failure
    # is silent: `{"A", "B", "C"}` is a set of strings and passes every type check.
    check("and text is NOT shattered into characters", passed=len(text) == 3)  # noqa: PLR2004

    # ⚑ A SET RETURNED WHERE TEXT IS EXPECTED REFUSES rather than being coerced. Coercion
    # here would invent a document out of a name set.
    _text, why = census_call.text_call(scanner, "names", ["a"], "scanner")
    check("a non-text result reports why", passed=why is not None and "not text" in why)

    # ⚑ AND A MISSING SCANNER REPORTS WHY through the same contract as a missing census.
    got, why = census_call.str_set_call(scanner, "absent", ["a"], "scanner")
    check("an absent scanner function reports why", passed=got == set() and why is not None)

    # ── the shapes a census may legitimately return ──────────────────────────
    got, why = census_call.census_of(_module("m", lambda: {"a", "b"}), "m")
    check("a set census is returned", passed=got == {"a", "b"} and why is None)

    got, why = census_call.census_of(_module("m", lambda: ["a", "a", "b"]), "m")
    check("a list census is de-duplicated into a set", passed=got == {"a", "b"})

    # ⚑ A DICT CENSUS IS ITS KEYS. One declared gate returns a dict of key to detail, and
    # a caller iterating it would get the keys by accident — right until a census returns
    # something else.
    got, why = census_call.census_of(_module("m", lambda: {"a": "detail", "b": "detail"}), "m")
    check("a dict census yields its KEYS", passed=got == {"a", "b"} and why is None)

    got, why = census_call.census_of(_module("m", set), "m")
    check(
        "an empty census is empty WITH NO REASON — it is clean, not unmeasured",
        passed=got == set() and why is None,
    )

    # ── THE FOUR FAILURE MODES, each a reason rather than an empty set ───────
    got, why = census_call.census_of(_module("m", None), "m")
    check("a module with no census reports why", passed=got == set() and why is not None)
    check("and names the module in its reason", passed=why is not None and "m" in why)

    got, why = census_call.census_of(_module("m", "not-callable"), "m")
    check(
        "a non-callable census reports why",
        passed=got == set() and why is not None and "not callable" in why,
    )

    got, why = census_call.census_of(_module("m", _raises), "m")
    check(
        "a raising census reports why rather than propagating",
        passed=got == set() and why is not None,
    )
    # ⚑ The exception TYPE and message survive, because a gate whose dependency vanished
    # and one whose census has a bug need different fixes.
    check(
        "and carries the exception type and message",
        passed=why is not None and "ImportError" in why and "gone" in why,
    )

    got, why = census_call.census_of(_module("m", lambda: 42), "m")
    check(
        "a non-collection census reports why",
        passed=got == set() and why is not None and "not a collection" in why,
    )
    check("and names the type it got", passed=why is not None and "int" in why)

    # ⚑ THE DISCRIMINATOR THAT MATTERS: an empty census and every failure both yield an
    # empty set, so ONLY the reason tells them apart. If a failure ever returned None for
    # `why`, an unmeasurable gate would read exactly like a clean one.
    _, clean_why = census_call.census_of(_module("m", set), "m")
    _, broken_why = census_call.census_of(_module("m", None), "m")
    check(
        "clean and unmeasurable differ ONLY by the reason",
        passed=clean_why is None and broken_why is not None,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
