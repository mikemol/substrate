"""`sqlalchemy.sql.dml` — the three write statements, declared for what a reader READS of them.

⚑⚑ DECLARED FOR ONE CONSUMER, `substrate/sql_statement.py` (W19 → W4 cut 4): `written_table`
walks a compiled builder and asks each node *are you a DML statement, and which table do you
write?*; `returned_columns` asks a DML statement what it RETURNINGs. Two attributes, read on
three classes.

⚑⚑⚑ READ FROM THE LIBRARY SOURCE. `UpdateBase` is `sql/dml.py:390`: `table: _DMLTableElement`
(an annotation, `sql/dml.py:407`) and `_returning: Tuple[_ColumnsClauseElement, ...] = ()`
(`:416`). `Insert`, `Update` and `Delete` derive from it through `ValuesBase` /
`DMLWhereBase`, neither of which this stub needs to name — the two attributes are inherited
unchanged. `_DMLTableElement` is a union over `TableClause | Join | Alias | CTE` and
`_ColumnsClauseElement` over column expressions; both are names this stub declines, so both
are `object` here and a consumer narrows with `isinstance` — which is what it must do anyway,
because a DML target can be an alias and a RETURNING element can be an expression.

⚑ `_returning` IS PRIVATE AND DECLARED ANYWAY. The origin (`query_defs.returned_columns`) read
it through `getattr`, because RETURNING has no public accessor that yields the raw tuple;
`exported_columns` re-keys it. Declaring the private attribute is what lets the reader be typed
where `getattr` gave it `Any`; stubtest compares private names only when asked, and this stub
does not lie about the name.

⚑ THE THREE `__init__`s ARE DECLARED BECAUSE STUBTEST INSISTED, not because anything here calls
them: a class stub with no constructor inherits `object.__init__`, and the gate reported each
runtime `(self, table: _DMLTableArgument)` as a contradiction. Read from `sql/dml.py:1251`
(`Insert`), `:1567` (`Update`), `:1750` (`Delete`); the argument type is declined, so `object`.

⟡declines: the module-level constructors (`insert()`/`update()`/`delete()`), the
generative surface (`values`, `where`, `returning`, `return_defaults`, `with_hint`,
`with_dialect_options`, `on_conflict_*`), `ValuesBase`, `DMLWhereBase`, `DMLState`,
`entity_description`, `returning_column_descriptions`, `exported_columns`, and every private
member other than `_returning`. Nothing here BUILDS a DML statement; the builders live in
`jea/metalanguage/query_decl.py` outside the typed package.
"""

from sqlalchemy.sql.visitors import ExternallyTraversible

class UpdateBase(ExternallyTraversible):
    """The base of `Insert`, `Update` and `Delete` — the target and the RETURNING tuple.

    ⚑ `ExternallyTraversible` IS A TRUE BASE, through `ClauseElement` (`sql/dml.py:390` lists
    it last among eight bases). It is the one declared here because it is what lets a DML
    statement be HANDED to `visitors.iterate` — the reader's whole use of it.
    """

    table: object
    _returning: tuple[object, ...]

class Insert(UpdateBase):
    def __init__(self, table: object) -> None: ...

class Update(UpdateBase):
    def __init__(self, table: object) -> None: ...

class Delete(UpdateBase):
    def __init__(self, table: object) -> None: ...
