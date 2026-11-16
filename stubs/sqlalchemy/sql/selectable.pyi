"""`sqlalchemy.sql.selectable` — what a statement RETURNS, and what an alias WRAPS.

⚑⚑ DECLARED FOR ONE CONSUMER, `substrate/sql_statement.py` (W19 → W4 cut 4): `returned_columns`
asks a `Select` for `selected_columns.keys()`; `columns_of` unwraps a column's `.table` through
alias layers with `.element` until it reaches the declared `Table` — the correction that
recovered the RETIRE LICENCE among `terms`' per-column readers, which an `isinstance(t, Table)`
on an aliased `Column.table` had silently dropped.

⚑⚑⚑ READ FROM THE LIBRARY SOURCE. `SelectBase.selected_columns` is `sql/selectable.py:3559`, a
`@util.ro_non_memoized_property` returning `ColumnCollection[str, ColumnElement[Any]]`;
`Select` overrides it at `:6464` as a `@HasMemoized_ro_memoized_attribute` with the same type.
`AliasedReturnsRows.element: ReturnsRows` is `:1696`; `Alias`, `Subquery` and `CTE` inherit it
and are `NoInit` — constructed by `_construct`, never by `__init__` — so no constructor is
declared for them. `ReturnsRows` is a name this stub declines; `element` is `object`, and the
consumer narrows with `isinstance(_, Table)`, which is the only reading it makes.

⚑ `Select.selected_columns` IS A MEMOIZED-ATTRIBUTE DESCRIPTOR, the `Table.c` situation exactly:
stubtest cannot reconcile `HasMemoized_ro_memoized_attribute` with `@property`, and the return
type is the whole reason the name is declared, so the exemption is on the descriptor KIND,
named per attribute, and the type it yields is still checked wherever a consumer reads it.

`SelectBase.selected_columns` is the same descriptor class one level up (`_non_memoized_property`),
so both are named. `Select.__init__` is DECLARED because stubtest insisted (a class stub with
no constructor inherits `object`'s): `(self, *entities: _ColumnsClauseArgument[Any],
**dialect_kw: Any)` at `sql/selectable.py:5379`, both argument types declined, so `object`.

⚑⚑ WIDENED FOR A SECOND CONSUMER, `substrate/rel_bridges.py` (W4 file 3 cut 4, tick 32): the
bridge from a `Select` to its Rel head-set reads the clause STATE the origin reached through
`getattr` - which under this gate is `Any`. Each is transcribed from the library: `_distinct`
and `_where_criteria` are class-level on `Select` (`selectable.py:5314`, `:5318`);
`_order_by_clauses`, `_group_by_clauses` and `_limit_clause` are on `GenerativeSelect`
(`:3987-3989`), a base this stub does not name, so they are declared on `Select` where they are
read; `get_final_froms() -> Sequence[FromClause]` is `:5755`; `NamedFromClause.name: str` is
`:1072` and `AliasedReturnsRows` derives from it (`:1696`); `CTE.recursive` is an INSTANCE
attribute bound in `_init` (`:2189`) and is declared here because the reader narrows on it after
`isinstance(f, CTE)`; `Join(roles.DMLTableRole, FromClause)` is `:1233`. Every element type is
`ColumnElement[Any]` upstream and `ColumnElement[object]` here - the same substitution the
top-level stub records.

⟡declines-signature: sqlalchemy.sql.selectable.Select.selected_columns,
    sqlalchemy.sql.selectable.SelectBase.selected_columns,
    sqlalchemy.sql.selectable.FromClause.c

`FromClause.c` (W39c) is a `_memoized_property` descriptor at runtime, the `Table.c` situation
exactly: the exemption is on the DESCRIPTOR KIND and the collection type is still checked.

⟡declines: the module-level constructor `select()`, the generative surface (`where`,
`join`, `group_by`, `order_by`, `limit`, `cte`, `subquery`, `alias`, `union*`, `with_only_columns`
and the rest), `CompoundSelect`, `TextualSelect`, `Lateral`, `TableSample`, `Values`,
`ReturnsRows`/`GenerativeSelect` and every other base not named below, and every private
member other than the five clause-state attributes. Nothing here BUILDS a select; the builders
live in `jea/metalanguage/query_decl.py`.
"""

from collections.abc import Sequence
from typing import Self

from sqlalchemy.sql.base import ColumnCollection, ReadOnlyColumnCollection
from sqlalchemy.sql.elements import ColumnElement, KeyedColumnElement
from sqlalchemy.sql.visitors import ExternallyTraversible

class FromClause(ExternallyTraversible):
    """An element usable in FROM - the base of tables, joins, aliases and CTEs (`:606`).

    ⚑ W39c: the join/alias surface a cleanroomed builder composes FROM clauses with, each read
    from the library — `join(self, right, onclause=None, isouter=False, full=False) -> Join`
    (`:669`), `outerjoin(self, right, onclause=None, full=False) -> Join` (`:722`) and
    `alias(self, name=None, flat=False) -> NamedFromClause` (`:771`). `_FromClauseArgument` and
    `_ColumnExpressionArgument` are declined, so both are `object`. `c` is the column collection
    every FROM element exposes; upstream it is `ReadOnlyColumnCollection[str,
    KeyedColumnElement[Any]]`, with the `Any` parameter substituted by `object` as elsewhere.
    """

    @property
    def c(self) -> ReadOnlyColumnCollection[str, KeyedColumnElement[object]]: ...
    def join(
        self, right: object, onclause: object = None, isouter: bool = False, full: bool = False
    ) -> Join: ...
    def outerjoin(self, right: object, onclause: object = None, full: bool = False) -> Join: ...
    def alias(self, name: str | None = None, flat: bool = False) -> NamedFromClause: ...

class NamedFromClause(FromClause):
    """A FROM element with a name (`:1061`) - tables, subqueries, CTEs, aliases."""

    name: str

class Join(FromClause):
    """A JOIN between two FROM elements (`:1233`) - read only by `isinstance`.

    The constructor is declared because stubtest insisted (a class stub with no constructor
    inherits `object`'s): `(self, left, right, onclause=None, isouter=False, full=False)` at
    `:1271`; the argument types `_FromClauseArgument` / `_OnClauseArgument` are declined, so
    `object`. Nothing here constructs a Join.
    """

    def __init__(
        self,
        left: object,
        right: object,
        onclause: object = None,
        isouter: bool = False,
        full: bool = False,
    ) -> None: ...

class SelectBase(ExternallyTraversible):
    """The base every SELECT-shaped statement shares — declared for `selected_columns` alone.

    ⚑ `ExternallyTraversible` IS A TRUE BASE: `SelectBase(…, Selectable)` at `sql/selectable.py:
    3531`, and `Selectable` derives from `ReturnsRows` → `ClauseElement` → `ExternallyTraversible`.
    It is the one base declared here because it is what lets a SELECT be HANDED to
    `visitors.iterate`, which is the reader's whole use of the class.
    """

    @property
    def selected_columns(self) -> ColumnCollection[str, ColumnElement[object]]: ...
    # ⚑ W39c (`substrate/query_tables` cleanroom): `SelectBase.subquery(self, name: Optional[str]
    # = None) -> Subquery` at `sql/selectable.py:3785`, transcribed. It is what turns a
    # `schema_decl` fragment into the named FROM element a builder joins (`node_v`, `unit_v`).
    def subquery(self, name: str | None = None) -> Subquery: ...

class Select(SelectBase):
    """A SELECT statement — the one class a compiled read builder is."""

    _distinct: bool
    _where_criteria: tuple[ColumnElement[object], ...]
    _order_by_clauses: tuple[ColumnElement[object], ...]
    _group_by_clauses: tuple[ColumnElement[object], ...]
    _limit_clause: ColumnElement[object] | None
    def __init__(self, *entities: object, **dialect_kw: object) -> None: ...
    @property
    def selected_columns(self) -> ColumnCollection[str, ColumnElement[object]]: ...
    def get_final_froms(self) -> Sequence[FromClause]: ...
    # ⚑ FIVE GENERATIVE METHODS, DECLARED SO A FIXTURE CAN BUILD A CLAUSED SELECT (tick 33).
    # `where` (`:6227`) and `distinct` (`:6259`) are on `Select`; `order_by` (`:4386`),
    # `group_by` and `limit` (`:4217`) are on `GenerativeSelect` and declared here where they
    # are reached. `order_by`/`group_by` lead with a `__first` parameter that MANGLES to
    # `_GenerativeSelect__first` at runtime — the same fact `schema.pyi` records for `Column`.
    # Argument types are `_ColumnExpressionArgument` unions this stub declines, so `object`.
    def where(self, *whereclause: object) -> Self: ...
    def distinct(self, *expr: object) -> Self: ...
    def order_by(self, _GenerativeSelect__first: object = ..., *clauses: object) -> Self: ...
    def group_by(self, _GenerativeSelect__first: object = ..., *clauses: object) -> Self: ...
    def limit(self, limit: object) -> Self: ...
    # ⚑ W39c: `Select.select_from(self, *froms: _FromClauseArgument) -> Self` at `:6300`; the
    # argument union is declined, so `object`, as for the five methods above.
    def select_from(self, *froms: object) -> Self: ...

class AliasedReturnsRows(NamedFromClause):
    """The base of `Alias`, `Subquery` and `CTE` — the wrapped element is what a reader unwraps."""

    element: object

class Alias(AliasedReturnsRows): ...
class Subquery(AliasedReturnsRows): ...

class CTE(AliasedReturnsRows):
    """A common table expression; `recursive` is what marks a WITH RECURSIVE closure."""

    recursive: bool
