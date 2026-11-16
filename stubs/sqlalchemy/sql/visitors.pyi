"""`sqlalchemy.sql.visitors` — the tree walk the statement readers rest on.

⚑⚑ DECLARED FOR ONE CONSUMER, `substrate/sql_statement.py` (W19 → W4 cut 4), which walks a
compiled builder with `iterate` to find every `Table`, `Column` and DML node the statement
reaches — the accessor that replaced `get_final_froms()`, which answered about the OUTERMOST
froms only and hid four builders reading `obs` through CTEs.

⚑⚑⚑ READ FROM THE LIBRARY SOURCE, NOT FROM THE CALL SITE. `iterate` is
`sql/visitors.py:813-851`: `(obj: Optional[ExternallyTraversible], opts: Mapping[str, Any] =
util.EMPTY_DICT) -> Iterator[ExternallyTraversible]`, a breadth-first walk over
`get_children()`. The library spells `opts` with `Any`; this stub's convention is `object` for
a genuinely unconstrained parameter, and the parameter is exactly that (*"usually empty in
modern usage"*). `ExternallyTraversible` is `sql/visitors.py:592`; only `get_children` is
declared, because it is the one member the walk and this consumer read — the class's
`_annotate`/`_clone`/`_copy_internals` are the traversal machinery nobody here calls.

⟡declines: every visitor class (`Visitable`, `HasTraverseInternals`, `InternalTraversal`,
`ExtendedInternalTraversal`, the `Traversible*` family), the `traverse`/`cloned_traverse`/
`replacement_traverse` functions, `traverse_using`, `iterate`'s sibling `traverse_depthfirst`
if present, and every private member of `ExternallyTraversible`. A stub declaring the visitor
protocol would be asserting a traversal contract this repo never invokes.
"""

from collections.abc import Iterable, Iterator, Mapping

class ExternallyTraversible:
    """A node the tree walk can reach — the one method `iterate` calls on it."""

    def get_children(
        self, *, omit_attrs: tuple[str, ...] = (), **kw: object
    ) -> Iterable[ExternallyTraversible]: ...

def iterate(
    obj: ExternallyTraversible | None,
    opts: Mapping[str, object] = ...,
) -> Iterator[ExternallyTraversible]: ...
