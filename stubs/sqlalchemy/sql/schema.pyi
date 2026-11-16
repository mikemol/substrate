"""`Column` — the schema item, in the module that really defines it.

⚑⚑⚑ IT IS HERE AND NOT IN `elements.pyi` BECAUSE STUBTEST SAID SO. A draft grouped `Column`
with `ColumnElement` and `KeyedColumnElement`, reasoning from the true fact that it subclasses
them; the gate replied *`sqlalchemy.sql.elements.Column` is not present at runtime — MISSING*.
`Column` is a `SchemaItem` and lives at `sql/schema.py:1497`, beside `Table` and `MetaData`.
Being a subclass of something is not the same as living where that something lives.

⚑⚑ THE FOURTH INSTANCE OF ONE ERROR IN THIS ARC, AND THE SECOND OF MINE. The brief records two
(`Dialect`, then `PGDialect_psycopg2`); I added `PGDialect_psycopg2` in the wrong package and
then `Column` in the wrong module. Every one was green under mypy and every one was caught by
comparison against the live module. The instruction was to read signatures FROM THE LIBRARY
SOURCE — and in both of mine I read the SIGNATURE correctly and INFERRED THE HOME, which is the
same guess displaced one level up and invisible to the same checker.

⚑⚑⚑ THE TWO LEADING PARAMETERS ARE SPELLED `_Column__name_pos` / `_Column__type_pos`, AND IT
TOOK TWO WRONG READINGS TO GET THERE. Upstream writes `__name_pos` inside a class body. First I
read that as the positional-only idiom and rendered it `name, type_, /`; stubtest refused —
*"should be positional or keyword (remove `/`)"*, and the runtime parameter is named
`_Column__name_pos`. Then I wrote `__name_pos` literally, which MANGLES IDENTICALLY inside this
stub's own class body and so could never match either. The mangled form is the only spelling
that names the parameter the runtime actually has.

⚑ THE DOUBLE UNDERSCORE MANGLES; IT DOES NOT MAKE A PARAMETER POSITIONAL-ONLY. That is the fact
both wrong readings missed, and it is a fact about the LANGUAGE rather than about sqlalchemy —
which is exactly the kind a reader reconstructs from a convention instead of checking.

⚑ SO THE PSEUDO-POSITIONAL PAIR IS DUPLICATED BY DESIGN UPSTREAM: `__name_pos`/`__type_pos` for
positional callers and `name`/`type_` as real keywords, which is how both `Column("id",
Integer)` and `Column(name="id", type_=Integer)` work. Both pairs are declared.

⚑ THE TWO PRIVATE PARAMETERS (`_omit_from_statements`, `_proxies`) ARE DECLARED TOO. They are
upstream internals no consumer here passes, but stubtest compares the whole signature, and a
parameter omitted from a stub is a parameter a caller is told does not exist.
"""

from typing import TypeVar

from sqlalchemy.sql.elements import KeyedColumnElement
from sqlalchemy.sql.type_api import TypeEngine

_T = TypeVar("_T")

class Column(KeyedColumnElement[_T]):
    """A column in a database table.

    ⚑ `key` AND `server_default` ARE PURE ANNOTATIONS UPSTREAM (`schema.py:1503`, `:1505`),
    narrowing what `ColumnElement` binds without rebinding it. `key` is therefore NOT restated
    here — the same finding stubtest reported against `KeyedColumnElement`, where a stub-level
    `key: str` contradicted the runtime value of `None`.

    ⚑ `server_default` IS `Optional[FetchedValue]` UPSTREAM; `FetchedValue` is not a name this
    stub declares, so it is `object` here — honest about not describing it, rather than absent.
    """

    name: str
    # ⚑⚑ THE TWO ATTRIBUTES A DECLARATION-DRIVEN WRITER READS, AND THEY WERE MISSING WHILE THE
    # CONSTRUCTOR PARAMETERS OF THE SAME NAME WERE PRESENT. That asymmetry is easy to miss and
    # cost a refusal: a stub can describe exactly how a column is BUILT and say nothing about how
    # it is INTERROGATED, and only a consumer that asks "is this column required?" finds out.
    #
    # ⚑ `nullable` IS BOUND IN `__init__` (`schema.py`), not annotated at class level like
    # `server_default` (`schema.py:1505`) — so this one is a READING of the assignment rather than
    # a transcription of an annotation, the limit `check_stub_authority` names in its own
    # docstring. It is `bool` at runtime after construction: the constructor's `None` default is
    # resolved to a real boolean (primary-key columns to False, others to True) before it lands.
    nullable: bool
    # ⚑ `Optional[FetchedValue]` UPSTREAM; `FetchedValue` is not a name this stub declares, so the
    # element is `object` — honest about not describing it rather than claiming a class. The
    # `| None` half IS load-bearing and is kept: "has no server default" is exactly the `None`,
    # and it is half of the required-column predicate.
    server_default: object | None
    # ⚑ `table` IS ANNOTATED UPSTREAM ON `ColumnClause` (`sql/elements.py:4905`,
    # `table: Optional[FromClause]`), and is declared HERE because `Column` is the class a
    # consumer reaches it through — the same placement `PrimaryKeyConstraint.columns` records.
    # `FromClause` is a name this stub declines, so the element is `object`: a reader narrows
    # with `isinstance(col.table, Table)`, which is what `substrate/sql_statement.py` does to
    # unwrap an alias down to the declared relation. The `| None` half is load-bearing: a
    # column with no table is a free `column("x")`, and that is exactly the case the unwrap
    # must stop on.
    table: object | None
    def __init__(
        self,
        _Column__name_pos: str | TypeEngine[_T] | None = None,
        _Column__type_pos: TypeEngine[_T] | None = None,
        *args: object,
        name: str | None = None,
        type_: TypeEngine[_T] | None = None,
        autoincrement: bool | str = "auto",
        default: object = ...,
        insert_default: object = ...,
        doc: str | None = None,
        key: str | None = None,
        index: bool | None = None,
        unique: bool | None = None,
        info: dict[str, object] | None = None,
        nullable: bool | None = ...,
        onupdate: object = None,
        primary_key: bool = False,
        server_default: object = None,
        server_onupdate: object = None,
        quote: bool | None = None,
        system: bool = False,
        comment: str | None = None,
        insert_sentinel: bool = False,
        _omit_from_statements: bool = False,
        _proxies: object = None,
        **dialect_kwargs: object,
    ) -> None: ...
