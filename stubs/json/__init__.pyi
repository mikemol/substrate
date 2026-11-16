# ⚑ TYPESHED TYPES `json.loads` AS RETURNING `Any`, AND THAT IS THE HONEST
# TYPE FOR A DYNAMIC LOAD — but `Any` is unspellable in this repo, so every
# expression downstream of a decode becomes a finding. Seven of them appeared in
# one 40-line parser, none of which was a real defect.
#
# ⚑⚑ `object` IS NOT A WEAKER `Any`; IT IS THE OPPOSITE. `Any` silences the
# checker and lets `reply["info"]["kind"]` typecheck against nothing. `object`
# admits NO attribute access or subscript at all, so a caller MUST narrow with an
# `isinstance` check before reading anything. The stub therefore makes the decode
# site stricter than typeshed does, not looser: what was unchecked becomes
# checked, and the narrowing that was implicit becomes a statement in the source.
#
# ⚑ SCOPE IS DELIBERATELY THE DECODE FUNCTIONS ONLY. `dumps`/`dump` take an input
# and are already sound; re-declaring them here would be a second spelling of
# typeshed's own signature, drifting the moment either changes. `substrate.json_reply`
# is the reader that turns the `object` this returns into typed accessors.

from _typeshed import SupportsRead
from collections.abc import Callable
from typing import IO

def loads(
    s: str | bytes | bytearray,
    *,
    cls: type | None = ...,
    object_hook: Callable[[dict[str, object]], object] | None = ...,
    parse_float: Callable[[str], object] | None = ...,
    parse_int: Callable[[str], object] | None = ...,
    parse_constant: Callable[[str], object] | None = ...,
    object_pairs_hook: Callable[[list[tuple[str, object]]], object] | None = ...,
) -> object: ...
def load(
    fp: SupportsRead[str | bytes],
    *,
    cls: type | None = ...,
    object_hook: Callable[[dict[str, object]], object] | None = ...,
    parse_float: Callable[[str], object] | None = ...,
    parse_int: Callable[[str], object] | None = ...,
    parse_constant: Callable[[str], object] | None = ...,
    object_pairs_hook: Callable[[list[tuple[str, object]]], object] | None = ...,
) -> object: ...
def dumps(
    obj: object,
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type | None = ...,
    indent: None | int | str = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[object], object] | None = ...,
    sort_keys: bool = ...,
) -> str: ...
def dump(
    obj: object,
    fp: IO[str],
    *,
    skipkeys: bool = ...,
    ensure_ascii: bool = ...,
    check_circular: bool = ...,
    allow_nan: bool = ...,
    cls: type | None = ...,
    indent: None | int | str = ...,
    separators: tuple[str, str] | None = ...,
    default: Callable[[object], object] | None = ...,
    sort_keys: bool = ...,
) -> None: ...

class JSONDecodeError(ValueError):
    msg: str
    doc: str
    pos: int
    lineno: int
    colno: int
    def __init__(self, msg: str, doc: str, pos: int) -> None: ...

# ⚑ `decode`'s SECOND PARAMETER IS DROPPED, NOT SPELLED. Typeshed gives it a
# `Callable[..., Any]` scanner default; both halves of that are unspellable here,
# and `...` in a Callable IS an `Any` (it says "some parameters, unchecked"). It is
# a private implementation hook — no caller in this tree passes it — so the honest
# stub omits it rather than inventing a signature to satisfy the checker.
class JSONDecoder:
    def __init__(self, **kwargs: object) -> None: ...
    def decode(self, s: str) -> object: ...

class JSONEncoder:
    def __init__(self, **kwargs: object) -> None: ...
    def encode(self, o: object) -> str: ...
    def default(self, o: object) -> object: ...
