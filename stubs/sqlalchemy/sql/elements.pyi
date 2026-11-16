"""`ColumnElement`, `KeyedColumnElement` and `Column` — the expression classes, where they live.

⚑⚑ THE CLASS DEFINITIONS SIT HERE RATHER THAN IN THE TOP-LEVEL STUB, AND THAT IS A REPAIR OF A
MEASURED FAILURE, NOT A TIDINESS PREFERENCE. A first draft defined `ColumnElement` and `Column`
in `sqlalchemy/__init__.pyi` while importing `ReadOnlyColumnCollection` from the UNSTUBBED
`sqlalchemy.sql.base`. mypy then compared this stub's `Column` against the REAL
`ColumnElement[Any]` bound in the installed library — two different classes of the same name —
and refused every collection return with *type argument must be a subtype of ColumnElement*,
three times. A stub graph that reaches outside itself for a bound is not self-consistent, and
the error it produces points at the annotation rather than at the missing file.

⚑ SO THE LAYOUT MIRRORS THE LIBRARY'S OWN: each name is DEFINED in the module that defines it
upstream, and the top-level stub RE-EXPORTS the subset `sqlalchemy/__init__.py` re-exports.
That makes DEFINED-IN and EXPORTED-FROM separately answerable in the stub, which is exactly the
distinction the whole exercise turns on.

⚑ `KeyedColumnElement` IS `ColumnElement` WITH A NON-NULL `.key`, which is its entire upstream
body. It matters here because pg's `excluded` collection is keyed on it rather than on `Column`.

⚑ `Label.primary_key` (W39c) IS A READ-ONLY PROPERTY UPSTREAM, forwarding to the labelled element,
while `ColumnElement` binds `primary_key: bool` as a writable class attribute. A stub cannot say
both — mypy refuses a read-only property overriding a writable attribute — so the upstream
override is named here rather than papered over, and its type (`bool`) is unchanged either way.

⟡declines-signature: sqlalchemy.sql.elements.Label.primary_key
"""

from typing import Generic, TypeVar

from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.sql.visitors import ExternallyTraversible

_T = TypeVar("_T")

class ColumnElement(ExternallyTraversible, Generic[_T]):
    """A column-valued expression.

    ⚑ `ExternallyTraversible` IS A TRUE BASE (tick 33): `ColumnElement` (`sql/elements.py:1223`)
    lists `DQLDMLClauseElement` last among its bases, which derives from `ClauseElement` (`:330`),
    which derives from `ExternallyTraversible`. It is declared because
    `substrate/rel_bridges.has_aggregate` hands each selected column to `visitors.iterate` — the
    same reason the two statement bases carry it.
    """

    type: TypeEngine[_T]
    key: str | None
    primary_key: bool
    # ⚑ `is_distinct_from` IS INHERITED UPSTREAM, from `ColumnOperators` in `sql/operators.py`,
    # reaching `ColumnElement` through the role hierarchy. It is declared on this class because
    # that is where a consumer REACHES it; hosting it on four intermediate role classes nobody
    # imports would add names to the stub that no call site names.
    def is_distinct_from(self, other: object) -> ColumnElement[bool]: ...
    # ⚑ W39c, read from the library: `ColumnElement.label(self, name: Optional[str]) -> Label[_T]`
    # (`sql/elements.py:1718`). `__ge__` is `ColumnOperators.__ge__(self, other: Any) ->
    # ColumnOperators` (`sql/operators.py:633`), narrowed on `ColumnElement` to `ColumnElement[bool]`
    # under `TYPE_CHECKING` — the type a column expression actually sees. `__eq__` is deliberately
    # NOT declared: it would override `object.__eq__` with an incompatible return, which upstream
    # silences with a line-level ignore this repo refuses; a builder's `a == b` flows into an
    # `object`-typed `onclause`/`where`, so the plain `bool` reading type-checks without it.
    def label(self, name: str | None) -> Label[_T]: ...
    def __ge__(self, other: object) -> ColumnElement[bool]: ...
    # ⚑ `desc()` is `ColumnOperators.desc(self) -> ColumnOperators` (`sql/operators.py:1739`),
    # narrowed on `ColumnElement` to `UnaryExpression[_T_co]` (`sql/elements.py:1042`).
    # `UnaryExpression` is declined here; it IS a `ColumnElement`, the nearest declared ancestor.
    def desc(self) -> ColumnElement[_T]: ...

class Label(ColumnElement[_T]):
    """A labelled column expression — what `ColumnElement.label` returns (`sql/elements.py:4742`).

    Upstream's bases are `roles.LabeledColumnExprRole[_T]` and `NamedColumn[_T]`, both declined;
    `ColumnElement` is the nearest declared ancestor. The constructor is transcribed; `element` is
    a `_ColumnExpressionArgument` union this stub declines, so `object`.
    """

    name: str
    def __init__(
        self, name: str | None, element: object, type_: TypeEngine[_T] | None = None
    ) -> None: ...

class KeyedColumnElement(ColumnElement[_T]):
    """`ColumnElement` whose `.key` is non-None — the element type of `Insert.excluded`.

    ⚑ `key` IS NOT RE-DECLARED HERE, AND STUBTEST EXPLAINED WHY. A draft wrote `key: str` on
    this class, reading upstream's annotation; the gate replied *variable differs from runtime
    type None* — the class-level VALUE inherited from `ColumnElement` is `None`, and upstream's
    `key: str` is a pure annotation that narrows the type without rebinding it. Restating it as
    a stub-level variable makes a claim about the runtime attribute that the runtime contradicts.
    """

class BindParameter(KeyedColumnElement[_T]):
    """A bound parameter — what `literal()` returns (`sql/elements.py`, ctor at `:1974`).

    ⚑ W39c. The constructor is transcribed from the runtime; `_TypeEngineArgument`, the `value`'s
    `Any`, the operator type and the `_NoArg` sentinel are declined, so each is `object`.
    """

    def __init__(
        self,
        key: str | None,
        value: object = ...,
        type_: object = None,
        unique: bool = False,
        required: object = ...,
        quote: bool | None = None,
        callable_: object = None,
        expanding: bool = False,
        isoutparam: bool = False,
        literal_execute: bool = False,
        _compared_to_operator: object = None,
        _compared_to_type: object = None,
        _is_crud: bool = False,
    ) -> None: ...

# ⚑ W39c: `literal(value, type_=None, literal_execute=False) -> BindParameter[Any]` — the RUNTIME
# signature (`sql/elements.py:158`); the three overloads above it are typing-only. `value` is the
# library's `Any`, so `object`; the element parameter is `object` for the same reason.
def literal(
    value: object, type_: object = None, literal_execute: bool = False
) -> BindParameter[object]: ...

# ⚑⚑⚑ `Column` IS DELIBERATELY NOT DECLARED HERE, AND A DRAFT OF THIS FILE DECLARED IT.
# stubtest replied *`sqlalchemy.sql.elements.Column` is not present at runtime — MISSING*.
# `Column` is a `SchemaItem`: it lives with `Table` and `MetaData` in `sql/schema.py:1497`, and
# is declared in `schema.pyi` beside them. Grouping it here was inference from the fact that it
# IS a `ColumnElement` subclass — true, and not where the module boundary falls.
#
# ⚑⚑ THAT IS THE FOURTH DEFINED-IN/EXPORTED-FROM ERROR IN THIS ARC and the second I made myself,
# after `PGDialect_psycopg2`. Both were green under mypy and both were caught only by comparison
# against the live module. The brief said read every signature FROM THE LIBRARY SOURCE; I read
# the signature and INFERRED THE HOME, which is the same guess one level up.

