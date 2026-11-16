"""`sqlalchemy.sql.functions` - the one class a Rel bridge asks "are you an aggregate?".

DECLARED FOR ONE CONSUMER, `substrate/rel_bridges.py` (W4 file 3 cut 4, tick 32): the bridge from
a `Select` to its Rel heads walks each selected column and asks whether any node is a named SQL
function whose name is an aggregate. The origin did that by `type(el).__name__ == "Function"` and
`getattr(el, "name", "")`; here it is `isinstance(el, Function)` and `el.name`.

READ FROM THE LIBRARY SOURCE. `Function(FunctionElement[_T])` is `sql/functions.py:1284`;
`name: str` is a class-level annotation at `:1325`; the constructor is `(self, name, *clauses,
type_=None, packagenames=None)` at `:1364`, with `*clauses` a `_ColumnExpressionOrLiteralArgument`
union and `type_` a `_TypeEngineArgument` - both declined, so `object`. `FunctionElement` derives
from `ColumnElement` (`:114`), which is how a function reaches `visitors.iterate`; it is not
named here because `ColumnElement[object]` is the base the reader needs.

⚑⚑ `func` AND ITS GENERATOR ARE DECLARED FOR THE W39c CLEANROOM, IN THEIR RUNTIME SHAPE. Upstream
`_FunctionGenerator` (`:861`) has `__init__(self, **opts)`, `__getattr__(self, name) ->
_FunctionGenerator` and `__call__(self, *c, **kwargs) -> Function[Any]`; `func =
_FunctionGenerator()` is module-level. Its named accessors (`coalesce`, `count`, `max`, …) exist
ONLY under `if TYPE_CHECKING:` upstream — declaring them here as methods would claim runtime
attributes the class does not have, which is exactly what stubtest refuses. So `func.coalesce(…)`
resolves through `__getattr__` then `__call__` and types as `Function`; the concrete registry
class (`coalesce`, `count`) is a `GenericFunction`, itself a `Function`, so that is accurate.

⟡declines: `FunctionElement` and its generative surface (`filter`, `within_group`, `over`,
`table_valued`, `column_valued`), every `GenericFunction` subclass by name (`count`, `max`, `sum`,
...), the typing-only accessors, `register_function`, and every private member.
"""

from sqlalchemy.sql.elements import ColumnElement

class _FunctionGenerator:
    """The `func` namespace: any attribute is a function name, and calling it builds the call."""

    def __init__(self, **opts: object) -> None: ...
    def __getattr__(self, name: str) -> _FunctionGenerator: ...
    def __call__(self, *c: object, **kwargs: object) -> Function: ...

func: _FunctionGenerator

class Function(ColumnElement[object]):
    """A named SQL function call - `name` is what an aggregate check reads."""

    name: str
    def __init__(
        self,
        name: str,
        *clauses: object,
        type_: object = None,
        packagenames: tuple[str, ...] | None = None,
    ) -> None: ...
