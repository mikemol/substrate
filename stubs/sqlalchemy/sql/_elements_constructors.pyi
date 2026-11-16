"""`sqlalchemy.sql._elements_constructors` — the `bindparam()` constructor, and nothing else.

⚑⚑ DECLARED FOR THE W39c CLEANROOM: builders bind named parameters (`core_id`, `min_fanin`, …)
that the cached runtime supplies at execution. Declared in the module that DEFINES it; the package
root re-exports it because the runtime does (`sqlalchemy.bindparam`).

⚑ READ FROM THE LIBRARY SOURCE (`:465`): `bindparam(key, value=_NoArg.NO_ARG, type_=None,
unique=False, required=_NoArg.NO_ARG, quote=None, callable_=None, expanding=False,
isoutparam=False, literal_execute=False) -> BindParameter[_T]`. The value's `Any`, the
`_TypeEngineArgument`, the `_NoArg` sentinel and the callable are declined, so each is `object`;
the element type is `object` for the same reason.

⟡declines: every other constructor in this module (`and_`, `or_`, `case`, `cast`, `column`,
`distinct`, `extract`, `false`, `null`, `nulls_first`, `over`, `text`, `true`, `tuple_`,
`type_coerce`, `within_group`, …) until a cleanroomed builder calls it.
"""

from sqlalchemy.sql.elements import BindParameter

def bindparam(
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
) -> BindParameter[object]: ...
