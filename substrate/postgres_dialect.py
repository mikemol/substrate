#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Own the ONE awkward external fact that sqlalchemy binds a CLASS to a lowercase name.

⚑⚑⚑ THE OPERATOR'S RULING, VERBATIM: *"SQLAlchemy's choice of symbol casing violates every
possible standard mypy and ruff know how to enforce. So we wrap them."* `dialect` is bound to
`PGDialect_psycopg2` — a class — and every static tool and every human reader sees a lowercase
name and reads a variable. Propagating that spelling into `substrate/` would trip the naming
rules at each call site and mislead at every one of them.

⚑ SO THE ODD SPELLING IS CONFINED TO THIS FILE, which is the same shape as
`substrate/sandbox_target.py` and `store_target.py`: one module owns one external irregularity,
declares it, explains it, and every consumer downstream sees a correctly-cased class.

⚑⚑ THE CENSUS WAS RUN RATHER THAN ASSUMED, AND IT OVERTURNED THE PREMISE THAT `dialect` IS
ALONE. `substrate/name_casing.py --module sqlalchemy.dialects.postgresql` reports 55 of 65
exported names contradicting their kind. But they are TWO POPULATIONS, and reporting them as one
would be the collapse this repo keeps recording:

  * ~50 are SQL TYPE NAMES IN `UPPER_SNAKE` — `JSONB`, `TSVECTOR`, `INT4RANGE`, `TIMESTAMP`.
    These are classes spelled like SQL keywords, deliberately, and `ruff` does NOT flag them:
    measured, binding `Payload = JSONB` in our source produces no naming finding. They read
    correctly to anyone who knows SQL, and renaming them would obscure rather than clarify.
  * 4 are LOWERCASE CLASSES — `dialect`, `array`, `hstore`, `aggregate_order_by`. These are the
    ones that actively mislead: a lowercase name asserts *value*, and the reader must already
    know otherwise. Of these, THIS REPO IMPORTS ONLY `dialect`; the other three belong to the
    array and aggregate surface the stub declines.

⚑⚑ SO THE HONEST ANSWER IS THAT `dialect` IS NOT UNIQUE IN THE LIBRARY BUT IS UNIQUE IN OUR
SURFACE, AND A SINGLE ALIAS SUFFICES — reached by measuring, not by assuming. The census mode is
kept precisely so the next name that arrives is found rather than remembered; this module is
written to hold more than one alias without restructuring.

⚑⚑⚑ AND THE ALIAS IS NOT THE WHOLE JOB — THE STUB MUST STILL DECLARE `dialect` UNDER ITS REAL
NAME. `stubs/sqlalchemy/dialects/postgresql/__init__.pyi` spells it lowercase because that is
what `stubtest` compares against the runtime; this module spells it `PostgresDialect` because
that is what a reader should see. Two layers, both required, neither substituting for the other.

⚑⚑ IT IS A CLASS, NOT AN INSTANCE, AND THAT IS THE HALF A CASUAL READING LOSES. `dialect` is
bound to the class object itself (`psycopg2.py:866`), so its type is `type[PGDialect_psycopg2]`.
A consumer INSTANTIATES it to get a dialect to compile against. Typing it as the instance would
make that call an error and every attribute read silently wrong.

⚑⚑⚑ AND THE NAME MUST BE PROVEN TO RESOLVE AT RUNTIME, WHICH IS WHY THE SUITE IMPORTS IT RATHER
THAN MERELY ANNOTATING IT. A wrapper over a name that does not exist type-checks perfectly: that
is exactly how `Dialect` and then `PGDialect_psycopg2` were each declared, checked green, and
raised `ImportError` — twice, in this arc, before the stub existed. `postgres_dialect_selftest`
imports and instantiates.

Usage: python3 -m substrate.postgres_dialect
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import dialect as _lowercase_dialect

if TYPE_CHECKING:
    from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2

#: The psycopg2 PostgreSQL dialect CLASS, under a name that says it is one.
#:
#: ⚑ THE ALIAS IS THE WHOLE MECHANISM. `dialect` is imported once, here, under a private name
#: that says what is wrong with it, and re-exported under the correct spelling. Nothing else in
#: `substrate/` names the lowercase form, so nothing else has to explain it.
PostgresDialect: type[PGDialect_psycopg2] = _lowercase_dialect


def dialect_instance() -> PGDialect_psycopg2:
    """Construct a dialect INSTANCE — what `statement.compile(dialect=...)` consumes.

    ⚑ THE DISTINCTION THIS FUNCTION MAKES EXISTS BECAUSE THE LOWERCASE NAME HIDES IT. Reading
    `dialect` as a value invites passing the CLASS where an instance is wanted; sqlalchemy
    accepts the class in some paths and not others, so the mistake is intermittent rather than
    immediate. Naming the construction makes the two states separate at every call site.
    """
    return PostgresDialect()


def main(argv: list[str]) -> int:
    """Report what the wrapped name resolves to — the class, and its real spelling."""
    if argv:
        sys.stderr.write("usage: python3 -m substrate.postgres_dialect\n")
        return 2
    sys.stdout.write(
        f"wrapped  : PostgresDialect\n"
        f"upstream : sqlalchemy.dialects.postgresql.dialect\n"
        f"resolves : {PostgresDialect.__name__}\n"
        f"kind     : class (instantiate it; it is not a dialect instance)\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
