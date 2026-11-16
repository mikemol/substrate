"""`PGDialect_psycopg2` — the dialect class, in the module that actually holds it.

⚑⚑⚑ IT LIVES HERE BECAUSE `stubtest` CAUGHT IT LIVE IN THE OTHER FILE. A draft declared
`PGDialect_psycopg2` in `dialects/postgresql/__init__.pyi`, where `dialect`'s annotation names
it, and the gate replied *`sqlalchemy.dialects.postgresql.PGDialect_psycopg2` is not present at
runtime — MISSING*. The class is DEFINED in `postgresql/psycopg2.py` and is NOT re-exported by
the package `__init__`; only the lowercase `dialect` alias crosses that boundary.

⚑⚑ WHICH IS THE THIRD INSTANCE OF ONE MISTAKE IN THIS ARC. The commissioning brief records two:
`Dialect` invented outright, then "corrected" to `PGDialect_psycopg2` after reading the line
where the class genuinely IS defined — both green under mypy, both `ImportError` at runtime, and
both of the interpreter's *"Did you mean"* suggestions wrong. This was the third, made by the
same reasoning (the class is defined in this package, so it must be importable from it) and
caught by the same instrument. **DEFINED-IN and EXPORTED-FROM are different questions, and a
green typecheck answers neither.**

⚑ THE CLASS BODY IS EMPTY ON PURPOSE. Nothing in this repo calls a method on the dialect — it is
passed whole to `statement.compile(dialect=...)`. Declaring methods would assert a surface no
consumer has read, which is the `agda_lex.pyi` failure; the class is declared because `dialect`'s
type must name something real.

⟡declines: every member of the dialect class — its ~40 inherited compiler hooks, type
descriptors, DBAPI adapters and connection-argument machinery. This repo names the class and
never reaches inside it.
"""

class PGDialect_psycopg2:
    # ⚑ THE CONSTRUCTOR IS UNANNOTATED UPSTREAM (`psycopg2.py:643`), so these types are a
    # READING of the defaults rather than a transcription — the limit `check_stub_authority`
    # names in its own docstring. Declared rather than declined because it is two parameters
    # and stubtest checks the names and arity regardless.
    def __init__(
        self,
        executemany_mode: str = "values_only",
        executemany_batch_page_size: int = 100,
        **kwargs: object,
    ) -> None: ...

# ⚑ THE LOWERCASE ALIAS AS THE MODULE REALLY BINDS IT (`psycopg2.py:866`, `dialect =
# PGDialect_psycopg2`). It is the CLASS, not an instance — see `substrate/postgres_dialect.py`,
# which is what consumers import under a correctly-cased name.
dialect: type[PGDialect_psycopg2]
