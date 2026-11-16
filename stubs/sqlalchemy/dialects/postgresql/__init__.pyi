"""The PostgreSQL dialect surface this repo imports — `JSONB`, upsert, and the dialect class.

⚑⚑ THE SECOND OF THE TWO HAND-WRITTEN `Any`s LIVES HERE, and it is NOT the shape the
commissioning brief predicted. `dialects/postgresql/dml.py:77` returns
`ReadOnlyColumnCollection[str, KeyedColumnElement[Any]]` — the element is `KeyedColumnElement`,
not `Column`. The brief named the substitution as `Column[Any] -> Column` "identically" at both
sites; at this one the correct substitution is `KeyedColumnElement`. Reading the second site as
a copy of the first would have declared a narrower element type than the library returns, and
`.excluded[...]` would then have type-checked as something it is not.

⚑ THE `excluded` NAMESPACE IS WHY THIS FILE EXISTS AT ALL. It is how an `ON CONFLICT DO UPDATE`
names the row that would have been inserted, so it is on the path of every upsert this repo
writes — and it was the accessor whose `Any` propagated furthest.

⚑⚑⚑ `dialect` IS DECLARED UNDER ITS REAL, LOWERCASE NAME BECAUSE THAT IS WHAT `stubtest`
COMPARES AGAINST. The runtime binds `dialect = PGDialect_psycopg2` (`postgresql/__init__.py:97`,
a chained assignment through `base.dialect`), so a stub spelling it any other way describes a
module that does not exist. The correctly-cased name that consumers import is a SEPARATE layer:
`substrate/postgres_dialect.py` owns the alias, and every call site sees `PostgresDialect`.
Those two layers are both required and neither substitutes for the other — the stub answers to
the runtime, the wrapper answers to the reader.

⚑⚑ AND IT IS A CLASS, NOT AN INSTANCE, WHICH IS THE HALF A CASUAL READING LOSES. `dialect` is
bound to the class object itself (`psycopg2.py:866`), so its type is `type[PGDialect_psycopg2]`.
Typing it as the instance would make `dialect()` an error and attribute reads silently wrong.

⚑ `PGDialect_psycopg2` IS DECLARED HERE TOO, AND ONLY BECAUSE `dialect`'s TYPE NAMES IT. It is
not part of the surface this repo imports; it is the referent the annotation requires. Omitting
it would leave `dialect` typed as something unspellable.

⟡declines: the PostgreSQL type surface this repo does not use — `ARRAY`, `HSTORE`, `TSVECTOR`,
the range and multirange types (`INT4RANGE`, `DATERANGE`, `TSTZRANGE` and siblings), `ENUM`,
`DOMAIN`, `INET`/`CIDR`/`MACADDR`, `MONEY`, `OID`, `REGCLASS`, `JSONPATH`, `CITEXT`; the
aggregate helpers (`aggregate_order_by`, `array`, `array_agg`, `hstore`); and every dialect
driver module other than the psycopg2 one named above (`asyncpg`, `psycopg`, `pg8000`).
"""

# ⚑⚑ `TypeEngine` MOVED TO `sqlalchemy.sql.type_api` IN Ⓝ128c. It was spelled
# `from sqlalchemy import ... TypeEngine`, which resolved ONLY because the top-level stub falsely
# re-exported it; the runtime `sqlalchemy` has no such attribute. Its two siblings on the lines
# below were already spelled against their real homes, so this was the odd one out — a
# second-order consumer of a false export, reachable only once the export was withdrawn.
from sqlalchemy import Insert as StandardInsert
from sqlalchemy import Table
from sqlalchemy.sql.base import ReadOnlyColumnCollection
from sqlalchemy.sql.elements import KeyedColumnElement
from sqlalchemy.sql.type_api import TypeEngine

# ⚑ `Any` IS NOT IMPORTED HERE EITHER — see the top-level stub, where a first draft reproduced
# the very annotation it exists to remove and the gate refused it on four lines.
class JSONB(TypeEngine[object]): ...

class Insert(StandardInsert):
    """A PostgreSQL INSERT, carrying the ON CONFLICT clauses.

    ⚑ `excluded` IS A `_memoized_property` DESCRIPTOR AT RUNTIME, not a plain `@property`, and
    stubtest cannot reconcile the two kinds. The exemption is on the DESCRIPTOR KIND and is
    named for this one attribute; the RETURN TYPE — the whole reason this stub exists, since
    this is the second of the library's two `Any` sites — is still checked wherever a consumer
    reads it. The same shape as `Table.c`, declined the same way, for the same reason.

    ⟡declines-signature: sqlalchemy.dialects.postgresql.Insert.excluded
    """

    # ⚑ THE SUBSTITUTION AT THIS SITE: `KeyedColumnElement[Any]` upstream keeps its element
    # class and drops only the `Any` PARAMETER. See this module's docstring for why the element
    # is NOT `Column` here.
    @property
    def excluded(self) -> ReadOnlyColumnCollection[str, KeyedColumnElement[object]]: ...
    # ⚑ BOTH RETURN `Insert` RATHER THAN `Self`. Upstream spells it `Self` (via
    # `sqlalchemy.util.typing`), which is the more precise type for a subclass; this stub does
    # not re-export that alias, and `Insert` is exact for every call site here because nothing
    # subclasses the pg `Insert`. Stated because it IS a narrowing of upstream's intent, not an
    # accident.
    def on_conflict_do_update(
        self,
        constraint: object = ...,
        index_elements: object = ...,
        index_where: object = ...,
        set_: object = ...,
        where: object = ...,
    ) -> Insert: ...
    def on_conflict_do_nothing(
        self,
        constraint: object = ...,
        index_elements: object = ...,
        index_where: object = ...,
    ) -> Insert: ...

def insert(table: Table) -> Insert: ...

# ⚑⚑ IMPORTED, NOT DECLARED HERE — AND STUBTEST IS WHY. A draft declared `PGDialect_psycopg2`
# in this file, because `dialect`'s annotation names it; the gate replied *not present at
# runtime — MISSING*. The class is defined in `postgresql/psycopg2.py` and never re-exported by
# this package, so only the lowercase alias crosses the boundary. See that stub's docstring:
# this was the THIRD instance of the defined-in/exported-from confusion in this arc.
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2

# ⚑ A CLASS BOUND TO A LOWERCASE NAME — declared as the runtime spells it, so `stubtest` can
# agree with the module. `substrate/postgres_dialect.py` is what consumers import.
dialect: type[PGDialect_psycopg2]
