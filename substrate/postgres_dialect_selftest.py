#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.postgres_dialect`: the wrapped name RESOLVES, and it is a class.

⚑⚑⚑ THE FIRST ARM IS THE FAILURE TYPING MISSED TWICE, PINNED AS A CASE. In this arc a stub
declared `Dialect`, type-checked green, and raised `ImportError`; it was then "corrected" to
`PGDialect_psycopg2` after reading the line where that class genuinely IS defined, type-checked
green, and raised `ImportError` again. Both of the interpreter's *"Did you mean"* suggestions
were wrong. A wrapper over a name that does not exist is INVISIBLE to mypy — the alias, the
annotation and every consumer all check perfectly — so the only thing that can catch it is
IMPORTING AND USING the name, which is what these arms do.

⚑⚑ SO THE ARMS TOUCH THE OBJECT, NEVER JUST ITS ANNOTATION. An arm asserting
`PostgresDialect is not None` would pass on a module that never resolved anything; the arms
below read `__name__` off it and INSTANTIATE it, both of which fail loudly on a name that is
absent or is not what it claims.

⚑⚑⚑ AND THE CLASS-VERSUS-INSTANCE CHECK CANNOT BE WRITTEN AS `isinstance(..., type)` HERE —
MYPY CALLS THAT BRANCH UNREACHABLE, WHICH IS THE STUB DOING ITS JOB. Now that
`stubs/sqlalchemy/dialects/postgresql/__init__.pyi` types `dialect` as
`type[PGDialect_psycopg2]`, the checker KNOWS statically that the alias is a class and refuses
the dead branch. That is a green signal, not an obstacle: before the stub, the same expression
was `Any` and the check was meaningful only at runtime. The RUNTIME half still matters — the
stub is a claim — so the arm asserts what the checker cannot see: that INSTANTIATING it yields
something which is not a class and which is an instance of the alias.

⚑ AND ONE ARM CHECKS THE ALIAS IS THE SAME OBJECT AS UPSTREAM, not merely a similar one. A
wrapper that constructed its own class would satisfy every other arm here while silently
diverging from the library on the next release — the drift a wrapper exists to prevent, arriving
through the wrapper.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family
from sqlalchemy.dialects.postgresql import dialect as _upstream

from substrate import postgres_dialect, suite_emit

# The class the alias must resolve to. ⚑ SPELLED HERE BECAUSE IT IS THE ANSWER, and read from
# the runtime rather than from the wrapper — a case that asked the wrapper for its own expected
# value would agree with itself no matter what it resolved to.
_WANT_CLASS_NAME = "PGDialect_psycopg2"

# The exit code a mode returns when refusing a usage it does not implement.
_REFUSED = 2


def the_wrapped_name_resolves_at_runtime(out: list[str]) -> int:
    """Check that `PostgresDialect` names a real object with the expected identity.

    ⚑⚑ THIS IS THE CASE THAT STUBTEST-LESS TYPING MISSED TWICE. Reading `__name__` forces the
    object to exist; a name that did not would have raised `ImportError` at module import, which
    is itself the assertion — the arm makes the identity explicit rather than incidental.
    """
    name = postgres_dialect.PostgresDialect.__name__
    if name != _WANT_CLASS_NAME:
        out.append(f"selftest: PostgresDialect resolves to {name!r}, want {_WANT_CLASS_NAME!r}")
        return 1
    return 0


def the_alias_is_the_upstream_object_itself(out: list[str]) -> int:
    """Check the alias IS upstream's `dialect`, not a lookalike the wrapper built.

    ⚑ IDENTITY, NOT EQUALITY. A wrapper that defined its own class would pass every other arm
    here and diverge from the library on its next release — which is the drift a wrapper exists
    to prevent, reintroduced through the wrapper.
    """
    if postgres_dialect.PostgresDialect is not _upstream:
        out.append("selftest: PostgresDialect is not the upstream `dialect` object")
        return 1
    return 0


def instantiating_the_alias_yields_an_instance(out: list[str]) -> int:
    """Check that the alias CONSTRUCTS — the half the lowercase spelling hides.

    ⚑⚑ THE DISCRIMINATOR. `dialect` reads as a value, so a reader may pass the class where an
    instance is wanted; sqlalchemy accepts that on some paths and not others, which makes the
    mistake intermittent rather than immediate. Asserting the result is an INSTANCE of the alias
    separates the two states the spelling conflates — and it is the half mypy cannot check, since
    the stub already tells it the alias is a class.
    """
    made = postgres_dialect.dialect_instance()
    if not isinstance(made, postgres_dialect.PostgresDialect):
        out.append("selftest: dialect_instance() is not an instance of PostgresDialect")
        return 1
    return 0


def the_reporter_runs(out: list[str]) -> int:
    """Check that `main` runs and exits zero.

    ⚑ THE POINT OF THE FOOTER IS THAT A READER SEES WHICH CLASS THE ODD UPSTREAM NAME REACHED,
    without opening the library. Running it here exercises the `__name__` read one more way.
    """
    if postgres_dialect.main([]) != 0:
        out.append("selftest: the reporter exited non-zero")
        return 1
    return 0


def the_reporter_refuses_arguments(out: list[str]) -> int:
    """Check that the reporter refuses an argument rather than ignoring it.

    ⚑ IGNORING A FLAG IS THE `--sandbox` DEFECT THIS TREE HAS ALREADY RECORDED: a mode that
    accepts a flag and silently disregards it reports a confident wrong answer. This module has
    one mode, so any argument is a misunderstanding and is refused.
    """
    if postgres_dialect.main(["--anything"]) != _REFUSED:
        out.append("selftest: the reporter accepted an argument it does not implement")
        return 1
    return 0


FAMILY = witness_family.of(
    key="postgres_dialect",
    apex="the lowercase upstream `dialect` is re-exported under a correctly-cased name that "
    "RESOLVES at runtime, is the upstream object itself, and constructs an instance",
    subject="the alias `substrate.postgres_dialect` owns, exercised against the live library",
    members=(
        witness_family.Member(
            name="the_wrapped_name_resolves_at_runtime",
            claim="PostgresDialect names a real importable object with the expected identity",
        ),
        witness_family.Member(
            name="the_alias_is_the_upstream_object_itself",
            claim="the alias IS upstream's `dialect`, not a lookalike",
            premises=("the_wrapped_name_resolves_at_runtime",),
        ),
        witness_family.Member(
            name="instantiating_the_alias_yields_an_instance",
            claim="calling the alias returns an instance of it, not a class",
            premises=("the_wrapped_name_resolves_at_runtime",),
        ),
        witness_family.Member(
            name="the_reporter_runs",
            claim="the reporter runs and exits zero",
        ),
        witness_family.Member(
            name="the_reporter_refuses_arguments",
            claim="an argument is refused rather than silently ignored",
        ),
    ),
)

_ARMS = (
    the_wrapped_name_resolves_at_runtime,
    the_alias_is_the_upstream_object_itself,
    instantiating_the_alias_yields_an_instance,
    the_reporter_runs,
    the_reporter_refuses_arguments,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/postgres_dialect_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
