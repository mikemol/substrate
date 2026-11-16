#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.name_casing`: a contradiction is FOUND, and agreement is not.

⚑⚑⚑ THE DISCRIMINATOR IS THE WHOLE SUITE. A predicate that answered *contradicts* to everything
would satisfy any case that only asks "was the bad name found", and a predicate that answered
*agrees* to everything would satisfy any case that only counts the population. Every arm below
asks BOTH halves, because this census was written to size a wrapper — and a census that
over-reports sends a reader to wrap names that read correctly, while one that under-reports is
the false zero it already committed once.

⚑⚑⚑ AND IT DID COMMIT THAT FALSE ZERO, WHICH IS WHY THE RUNTIME ARM EXISTS. The first cut read
SOURCE only and reported *0 contradict, 3 module-level names* over
`sqlalchemy/dialects/postgresql/__init__.py` — with `dialect`, the name the whole exercise is
about, classified `agrees`. Two independent causes: the binding is `dialect = psycopg2.dialect`,
an ATTRIBUTE value that one-hop resolution cannot follow, and the package's ~90 other names
arrive by `from .types import …`, which the source reader never saw. The runtime arm pins the
repair against the live library, so the module cannot regress to answering zero about its own
motivating case.

⚑ THE SOURCE READER IS KEPT AND IS ALSO TESTED, because it answers a different question — what a
file DECLARES, with line numbers, without importing anything. Its limit is documented rather
than removed; an arm asserts the limit is where the docstring says it is.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import name_casing, suite_emit

# ⚑ THE FIXTURE IS SOURCE TEXT, not a file, so the arms read a shape rather than a path. Each
# binding below is one row the census must classify, and the pair is chosen so a predicate that
# answered the same thing to both would fail.
_FIXTURE = (
    "class GoodClass: ...\n"
    "class bad_class: ...\n"
    "def good_func(): ...\n"
    "def BadFunc(): ...\n"
    "GOOD_CONST = 1\n"
    "alias_of_class = GoodClass\n"
)

# The module whose surface commissioned this census, and the name it is about.
_LIVE_MODULE = "sqlalchemy.dialects.postgresql"
_LIVE_NAME = "dialect"


def _rows(src: str) -> list[name_casing.Row]:
    """Census one source fixture."""
    return name_casing.read_source(src, "<fixture>")


def _verdict(rows: list[name_casing.Row], name: str) -> str | None:
    """Return the verdict recorded for one name, or None when it was not censused."""
    return next((r.verdict for r in rows if r.name == name), None)


def a_casing_is_read_from_the_name_shape(out: list[str]) -> int:
    """Check each convention is recognised, including the one that is neither.

    ⚑ `PGDialect_psycopg2` IS THE INTERESTING CASE: it is neither `CapWords` nor `snake_case`,
    and forcing it into either would hide that it is a class spelled unlike one.
    """
    bad = 0
    want = {
        "GoodClass": name_casing.CAP,
        "good_func": name_casing.SNAKE,
        "GOOD_CONST": name_casing.UPPER,
        "PGDialect_psycopg2": name_casing.OTHER,
        "_Private": name_casing.CAP,
    }
    for nm, expected in want.items():
        got = name_casing.name_case(nm)
        if got != expected:
            out.append(f"selftest: name_case({nm!r}) is {got!r}, want {expected!r}")
            bad += 1
    return bad


def a_lowercase_class_contradicts_its_kind(out: list[str]) -> int:
    """Check the finding is reported — the population a wrapper must own."""
    bad = 0
    rows = _rows(_FIXTURE)
    for nm in ("bad_class", "BadFunc"):
        if _verdict(rows, nm) != name_casing.CONTRADICTS:
            out.append(f"selftest: {nm!r} was not reported as contradicting its kind")
            bad += 1
    return bad


def a_conventional_name_is_not_reported(out: list[str]) -> int:
    """Check that agreement is NOT a finding — the discriminator.

    ⚑ WITHOUT THIS ARM the predicate could answer `contradicts` to every name in the tree and
    the arm above would still pass, sending a reader to wrap a whole library.
    """
    bad = 0
    rows = _rows(_FIXTURE)
    for nm in ("GoodClass", "good_func", "GOOD_CONST"):
        if _verdict(rows, nm) != name_casing.AGREES:
            out.append(f"selftest: {nm!r} was wrongly reported as contradicting")
            bad += 1
    return bad


def an_alias_resolves_to_the_kind_it_names(out: list[str]) -> int:
    """Check one-hop resolution: `x = SomeClass` is judged as a CLASS binding.

    ⚑ WITHOUT THE HOP, an alias is judged against the permissive `value` expectation and a
    lowercase class alias disappears. `alias_of_class` is lowercase and binds a class, so it must
    contradict.
    """
    if _verdict(_rows(_FIXTURE), "alias_of_class") != name_casing.CONTRADICTS:
        out.append("selftest: a lowercase alias of a class was not reported")
        return 1
    return 0


def a_dunder_is_not_judged(out: list[str]) -> int:
    """Check that interpreter protocol slots are excluded from the population.

    ⚑ JUDGING `__all__` WOULD REPORT THE LANGUAGE'S OWN CONVENTION as a finding against the
    library, which is noise a reader must then learn to ignore.
    """
    if _verdict(_rows("__all__ = ('x',)\n"), "__all__") is not None:
        out.append("selftest: a dunder was censused")
        return 1
    return 0


def the_source_reader_cannot_see_an_attribute_binding(out: list[str]) -> int:
    """Check the DOCUMENTED LIMIT of the source reader is exactly where it is claimed.

    ⚑⚑ THIS ARM ASSERTS A WEAKNESS, DELIBERATELY. `x = mod.thing` binds whatever `mod.thing` is,
    and no amount of parsing this file can say what that is — which is why `dialect` read as
    `agrees` and why the runtime reader exists. Pinning the limit means a future change that
    silently widened it would be noticed, and that the docstring's claim stays true.
    """
    if _verdict(_rows("import m\nlow = m.SomeClass\n"), "low") != name_casing.AGREES:
        out.append("selftest: the source reader's documented limit has moved")
        return 1
    return 0


def the_runtime_reader_finds_the_lowercase_class(out: list[str]) -> int:
    """Check the live census reports `dialect` — the case the source reader got wrong.

    ⚑⚑⚑ THE REGRESSION ARM. This is the exact query that returned zero before the runtime reader
    existed. It runs against the installed library, so it also proves the census can reach a
    third-party surface at all.
    """
    bad = 0
    rows, read = name_casing.census_module(_LIVE_MODULE)
    if not read:
        out.append("selftest: the runtime census read nothing")
        return 1
    if _verdict(rows, _LIVE_NAME) != name_casing.CONTRADICTS:
        out.append(f"selftest: {_LIVE_NAME!r} was not reported — the false zero has returned")
        bad += 1
    if not any(r.verdict == name_casing.AGREES for r in rows):
        out.append("selftest: the live census reported NOTHING as agreeing — over-reporting")
        bad += 1
    return bad


def the_runtime_reader_resolves_kind_from_the_object(out: list[str]) -> int:
    """Check that kind comes from the live object, which is what the source reader cannot do."""
    bad = 0
    want = {name_casing.name_case: name_casing.FUNC, name_casing.Row: name_casing.CLASS}
    for obj, expected in want.items():
        got = name_casing.runtime_kind(obj)
        if got != expected:
            out.append(f"selftest: runtime_kind gave {got!r}, want {expected!r}")
            bad += 1
    if name_casing.runtime_kind(42) != name_casing.VALUE:
        out.append("selftest: a plain value was not classified as a value")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="name_casing",
    apex="a name whose casing contradicts its kind is reported, a conventional one is not, and "
    "the kind is resolved from the live object where source alone cannot see it",
    subject="the census `substrate.name_casing` runs over source and over live modules",
    members=(
        witness_family.Member(
            name="a_casing_is_read_from_the_name_shape",
            claim="each convention is recognised, including the one that is neither",
            cases=5,
        ),
        witness_family.Member(
            name="a_lowercase_class_contradicts_its_kind",
            claim="a lowercase class and a CapWords function are both reported",
            cases=2,
        ),
        witness_family.Member(
            name="a_conventional_name_is_not_reported",
            claim="a name agreeing with its kind is NOT a finding",
            cases=3,
        ),
        witness_family.Member(
            name="an_alias_resolves_to_the_kind_it_names",
            claim="a lowercase alias of a class is judged as a class binding",
        ),
        witness_family.Member(
            name="a_dunder_is_not_judged",
            claim="interpreter protocol slots are excluded from the population",
        ),
        witness_family.Member(
            name="the_source_reader_cannot_see_an_attribute_binding",
            claim="the source reader's documented limit is where the docstring claims",
        ),
        witness_family.Member(
            name="the_runtime_reader_finds_the_lowercase_class",
            claim="the live census reports `dialect` and still reports agreement elsewhere",
            cases=2,
        ),
        witness_family.Member(
            name="the_runtime_reader_resolves_kind_from_the_object",
            claim="kind is read off the live object for classes, functions and values",
            cases=3,
        ),
    ),
)

_ARMS = (
    a_casing_is_read_from_the_name_shape,
    a_lowercase_class_contradicts_its_kind,
    a_conventional_name_is_not_reported,
    an_alias_resolves_to_the_kind_it_names,
    a_dunder_is_not_judged,
    the_source_reader_cannot_see_an_attribute_binding,
    the_runtime_reader_finds_the_lowercase_class,
    the_runtime_reader_resolves_kind_from_the_object,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/name_casing_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
