"""`sqlalchemy.sql._selectable_constructors` — the `select()` constructor, and nothing else.

⚑⚑ DECLARED FOR THE W39c CLEANROOM (`substrate/query_tables` and the builders that will follow it):
a clean module rebuilding `query_decl`'s builders must be able to CALL `select()`, and this stub
package declined it. Declared here because this is the module that DEFINES it; the package root
re-exports it because the runtime does (`sqlalchemy.select`).

⚑ READ FROM THE LIBRARY SOURCE. The runtime definition is
`def select(*entities: _ColumnsClauseArgument[Any], **__kw: Any) -> Select[Any]` (`:497`); the
twelve `@overload`s above it are typing-only arities that infer a row tuple, and this stub does
not model row types, so the single runtime signature is declared. `_ColumnsClauseArgument` is
declined, so the entities are `object`; `**__kw` exists only to raise on any keyword (`_no_kw()`),
and is declared with the runtime's name so stubtest can match it.

⟡declines: every other constructor in this module (`exists`, `union`, `union_all`, `except_`,
`intersect`, `lateral`, `tablesample`, `values`, `alias`, `cte`, `join`, `outerjoin`, `table`)
until a cleanroomed builder calls it.
"""

from sqlalchemy.sql.selectable import Select

def select(*entities: object, **__kw: object) -> Select: ...
