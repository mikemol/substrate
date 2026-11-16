#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.fixture_namespace`: names are DISTINCT, STABLE and never bare.

⚑⚑⚑ THE DISTINCTNESS ARM IS THE MEASURED DEFECT. Several fixtures collapsed onto ONE fallback
identifier, so they shared a namespace and the second one's teardown dropped the first's schema
out from under it — surfacing several frames later, naming a table rather than the collision. So
the arms drive identifiers that differ only in punctuation and assert the ANSWERS DIFFER. A
sanitiser that STRIPPED unsafe characters instead of replacing them would merge those two into
one name and pass any arm that only checked a single identifier renders safely.

⚑⚑ THE STABILITY ARM IS THE OPPOSITE CLAIM AND BOTH ARE NEEDED. Determinism is what makes the
namespace self-cleaning — a random name leaks a schema per run forever — so the same identifier
must render identically across calls. An arm asserting only distinctness would pass against a
randomised name; an arm asserting only stability would pass against a constant. The pair pins it.

⚑⚑ THE TRUNCATION ARM CHECKS A BOUND THAT EXISTS BECAUSE THE SERVER'S IS SILENT. Postgres
truncates an over-long identifier without complaint, so two long fixture names could collide
inside the catalogue while looking distinct in the source. The arm asserts the rendered name
stays under the limit — a check the server will never perform on our behalf.

⚑⚑ AND THE EMPTY IDENTIFIER IS CHECKED TO REFUSE RATHER THAN RENDER. It would produce the bare
prefix, a namespace every unnamed fixture shares, which is precisely the collapse the first arm
exists to prevent — reached by a different route, so it needs its own case.

⚑ EVERY CASE RUNS OFFLINE. The computation opens no connection, which is the property that lets
a caller qualify its statements with postgres unreachable.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import fixture_namespace, suite_emit

# Two identifiers differing ONLY in punctuation. ⚑ A SANITISER THAT STRIPPED rather than replaced
# would render these identically, which is the collision the distinctness arm hunts.
_DOTTED = "suite.alpha"
_DASHED = "suite-alpha"

# An ordinary identifier, already safe.
_PLAIN = "sppf_tree"

# An identifier carrying characters that must never reach a statement unescaped.
_HOSTILE = 'a"; DROP SCHEMA public; --'

# An identifier longer than the limit, to drive truncation.
_LONG = "x" * 200


def punctuation_variants_stay_distinct(out: list[str]) -> int:
    """Check that identifiers differing only in punctuation render to different names.

    ⚑⚑ THIS IS THE REGRESSION. Two fixtures sharing a namespace means one teardown drops the
    other's schema, and the failure names a table several frames away. A sanitiser that stripped
    unsafe characters would merge these two and pass any single-identifier arm.
    """
    bad = 0
    dotted = fixture_namespace.schema_for(_DOTTED)
    dashed = fixture_namespace.schema_for(_DASHED)
    if dotted == dashed:
        out.append(
            f"selftest: {_DOTTED!r} and {_DASHED!r} both rendered {dotted!r} — two fixtures would "
            f"share one namespace, and one teardown would drop the other's schema"
        )
        bad += 1
    if fixture_namespace.schema_for(_PLAIN) in (dotted, dashed):
        out.append("selftest: an unrelated identifier collided with a punctuation variant")
        bad += 1
    return bad


def the_same_identifier_renders_the_same_name(out: list[str]) -> int:
    """Check that the computation is deterministic across calls.

    ⚑ DETERMINISM IS WHAT MAKES THE NAMESPACE SELF-CLEANING. A randomised name leaks one schema
    per run forever, and nothing would ever drop them because nothing could name them again.
    """
    bad = 0
    first = fixture_namespace.schema_for(_PLAIN)
    if first != fixture_namespace.schema_for(_PLAIN):
        out.append("selftest: one identifier rendered two different names — the name is not stable")
        bad += 1
    if not first.startswith(fixture_namespace.PREFIX):
        out.append(f"selftest: {first!r} does not carry the disposable-namespace prefix")
        bad += 1
    return bad


def a_hostile_identifier_yields_a_safe_one(out: list[str]) -> int:
    """Check that quotes, semicolons and whitespace cannot survive into an identifier.

    ⚑ A SCHEMA NAME REACHES A STATEMENT AS AN IDENTIFIER, and one assembled from an arbitrary
    string is where an injection lives. The arm asserts the rendering is alphanumeric-or-
    replacement throughout, which is a claim about EVERY character rather than the few a sampled
    check would look for.
    """
    bad = 0
    rendered = fixture_namespace.schema_for(_HOSTILE)
    body = rendered[len(fixture_namespace.PREFIX) :]
    unsafe = [c for c in body if not c.isalnum() and c != fixture_namespace.REPLACEMENT]
    if unsafe:
        out.append(f"selftest: {rendered!r} carries unsafe character(s) {unsafe!r}")
        bad += 1
    if rendered == _HOSTILE:
        out.append("selftest: a hostile identifier passed through unchanged")
        bad += 1
    return bad


def an_over_long_identifier_is_bounded(out: list[str]) -> int:
    """Check that the rendered name stays within the bound the server would apply silently.

    ⚑ POSTGRES TRUNCATES WITHOUT COMPLAINT, so two long names could collide in the catalogue
    while reading as distinct in the source. Bounding here makes that collision visible to a case
    rather than to whoever eventually notices the wrong schema was dropped.
    """
    bad = 0
    rendered = fixture_namespace.schema_for(_LONG)
    budget = len(fixture_namespace.PREFIX) + fixture_namespace.LIMIT
    if len(rendered) > budget:
        out.append(f"selftest: {len(rendered)} characters rendered, over the {budget} budget")
        bad += 1
    if len(_LONG) <= fixture_namespace.LIMIT:
        out.append("selftest: the fixture identifier is not longer than the limit it tests")
        bad += 1
    return bad


def an_empty_identifier_refuses_rather_than_rendering_the_bare_prefix(out: list[str]) -> int:
    """Check that an empty identifier raises instead of producing a shared namespace.

    ⚑ THE BARE PREFIX IS A NAMESPACE EVERY UNNAMED FIXTURE WOULD SHARE — the same collapse the
    distinctness arm hunts, reached by a different route, which is why it needs its own case
    rather than being assumed covered.
    """
    try:
        rendered = fixture_namespace.schema_for("")
    except ValueError:
        return 0
    out.append(
        f"selftest: an empty identifier rendered {rendered!r} instead of refusing — every unnamed "
        f"fixture would share that namespace"
    )
    return 1


FAMILY = witness_family.of(
    key="fixture_namespace",
    apex="a fixture's schema name is computed in exactly one place: deterministic so the "
    "namespace is self-cleaning, distinct across identifiers that differ only in "
    "punctuation, safe as an identifier, bounded below the server's silent truncation, and "
    "refused when no identifier was given",
    subject="the schema names `substrate.fixture_namespace` computes, offline",
    members=(
        witness_family.Member(
            name="punctuation_variants_stay_distinct",
            claim="identifiers differing only in punctuation render to different names",
            cases=2,
        ),
        witness_family.Member(
            name="the_same_identifier_renders_the_same_name",
            claim="the computation is deterministic and carries the disposable prefix",
            cases=2,
        ),
        witness_family.Member(
            name="a_hostile_identifier_yields_a_safe_one",
            claim="quotes, semicolons and whitespace cannot survive into an identifier",
            cases=2,
        ),
        witness_family.Member(
            name="an_over_long_identifier_is_bounded",
            claim="the rendered name stays within the bound the server would apply silently",
            cases=2,
        ),
        witness_family.Member(
            name="an_empty_identifier_refuses_rather_than_rendering_the_bare_prefix",
            claim="an empty identifier raises instead of producing a shared namespace",
            premises=("punctuation_variants_stay_distinct",),
        ),
    ),
)

_ARMS = (
    punctuation_variants_stay_distinct,
    the_same_identifier_renders_the_same_name,
    a_hostile_identifier_yields_a_safe_one,
    an_over_long_identifier_is_bounded,
    an_empty_identifier_refuses_rather_than_rendering_the_bare_prefix,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/fixture_namespace_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
