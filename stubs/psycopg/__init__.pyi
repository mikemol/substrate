# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Types for the `psycopg` surface this repo's store chain opens a connection with.

⚑⚑⚑ PSYCOPG SHIPS `py.typed` AND IS A TYPED DEPENDENCY, so this is NOT the "stub an untyped
dep" case at all — and saying so up front matters, because the neighbouring `networkx` stub was
justified by that rule and the justification did not hold. What psycopg's own types cannot
express is narrower and REAL: a database column holds whatever the adapter produced, so a row
value is `Any` at the library's boundary and stays `Any` all the way to the caller. Under
`disallow_any_expr` that makes two specific expressions unusable, both MEASURED before this
stub was written rather than predicted from the shape of the library:

    row_factory=dict_row  →  Expression type contains "Any"
                             (Callable[[BaseCursor[Any, Any]], RowMaker[dict[str, Any]]])
    except psycopg.Error  →  Expression type contains "Any" (type[Error])

⚑⚑ THE SECOND ONE IS NOT ABOUT ROWS AND IT IS THE ONE WORTH READING. `type[Error]` is an `Any`
expression because `Error.__init__` is `*args: Sequence[Any]` and `__reduce__` returns
`tuple[Any, ...]`; referring to the CLASS drags its constructor along. The exception hierarchy
is otherwise entirely concrete — the `Any` is in pickling and varargs machinery that a caller
catching an error never touches.

⚑⚑⚑ SO THIS STUB PARAMETERISES; IT DOES NOT WITHDRAW. The correction that commissioned it:
dropping a type parameter because "this repo never uses it" encodes the CALLER's habits as the
library's contract, and a propagation reaching further than expected is the gate WORKING, not a
reason to retreat. Every generic here keeps its parameter — `Connection[Row]`, `Cursor[Row]`,
`RowFactory[Row]` — and `connect`'s `context` and `cursor_factory` are declared though this
repo passes neither. Nothing is dropped to make a call site pass.

⚑⚑ THE ONE SUBSTITUTION IS `Any` → `object` IN A ROW VALUE, AND IT IS A STRICTLY STRONGER
CLAIM, NOT A NARROWER SURFACE. `dict[str, Any]` lets a caller do arithmetic on a column without
saying what it is; `dict[str, object]` accepts exactly the same VALUES and refuses exactly the
uses that were never checked. A caller who knows a column is an `int` says so, with an
`isinstance` that is verified rather than an `Any` that is assumed. `substrate/
sandbox_connect.py` is the worked case: its `descriptor` narrowing guards values that flow into
a formatted `DROP ... CASCADE`, and under the library's own types that check would have read as
superstition.

⚑⚑⚑ THE FILE LAYOUT IS NOT COSMETIC AND IT COST TWO MEASURED FAILURES TO GET RIGHT. A stub is
resolved BY IMPORT PATH and `stubtest` checks a name AT that path, so a package stub must mirror
the MODULE STRUCTURE of what it shadows. Declaring `dict_row` only here left
`from psycopg.rows import dict_row` resolving to the LIBRARY — present, correct, silently not
consulted. Moving it to `rows.pyi` fixed that and the mirror-image fault, where the root
declaration was reported *"not present at runtime"* because `psycopg.dict_row` does not exist.
Hence: `abc.pyi`, `rows.pyi`, `errors.pyi`, `connection.pyi`, `cursor.pyi`, `_cursor_base.pyi`,
and this file re-exporting what the package root genuinely re-exports.

⚑ WHAT THIS DELIBERATELY DOES NOT TYPE, said rather than quietly omitted. There is no
`AsyncConnection`, no `Copy`, no `Pipeline`, no `ServerCursor`, no `ClientCursor`, no
`Transaction`, no `sql` composition module, and no adapter, `pq` or `AdaptContext` surface. The
row-factory family is `dict_row` and `tuple_row` only: `class_row` and `kwargs_row` are generic
over a caller-supplied class and need the adapter surface to type honestly. These are ABSENT
NAMES, not narrowed ones — a caller reaching for one gets an honest import error at the point
of need, never a silent `Any`.

⚑⚑⚑ AND THE GATE COULD NOT SEE THIS FILE, WHICH WAS A FINDING AND NOT A PASS — NOW FIXED.
`scripts/check_stub_authority.py` discovered its population with `STUBS.glob("*.pyi")`, so every
stub that is a package DIRECTORY was invisible to it — this one, `networkx`, `panflute` and
`paperkit`. Its green line read *"clean (5 stub(s) match)"*, which was true and was a fact about
the CENSUS rather than the tree. The discovery now walks directories, and this stub is checked.

⚑ SO `stubtest` WAS RUN AGAINST THIS STUB BY HAND, AND ITS VERDICT IS RECORDED RATHER THAN
ASSUMED. With `--ignore-missing-stub` the declared surface matches the library except for three
findings, all of one construct, all documented at the site: `rows.pyi`'s protocol `__call__`
signatures, where `stubtest` and mypy's protocol matching make incompatible demands about
psycopg's pre-PEP-570 positional-only spelling. The stub keeps the form under which CALLERS are
correct and carries the three findings openly. Without that flag it additionally reports every
psycopg name this stub does not declare, because a package stub SHADOWS the whole package —
which is the honest cost of a partial stub over a typed package, and why the omissions are
enumerated above rather than merely absent.

⚑⚑ THE `⟡declines:` LINE BELOW IS THAT ENUMERATION MADE MACHINE-READABLE, and it is the ONLY
thing that grants this stub `--ignore-missing-stub` in the gate. It restates the paragraph
above deliberately: the prose is for a reader, the marker is what the gate reads, and a stub
that stopped meaning it would have to delete the marker rather than let it rot. Note what the
marker does NOT buy — the three `rows.pyi` findings are signature CONTRADICTIONS, not absent
names, so they survive the relief and this stub's gate line is red until they are resolved or
the residue is accepted where it is documented.

⟡declines: AsyncConnection and the whole async surface, Copy, Pipeline, ServerCursor,
    ClientCursor, Transaction, the `sql` composition module, and the adapter / `pq` /
    AdaptContext layer. The row-factory family is `dict_row` and `tuple_row` only —
    `class_row` and `kwargs_row` need the adapter surface to type honestly.
"""

# ⚑⚑⚑ EIGHT OF THESE WERE FALSE RE-EXPORTS UNTIL Ⓝ128c (2026-09-03), AND THE PARAGRAPH ABOVE
# CLAIMED OTHERWISE — it says this file re-exports "what the package root genuinely re-exports",
# and `ConnDict`, `ConnParam`, `Params`, `Query`, `ConnectionTimeout`, `DictRow`, `RowFactory` and
# `TupleRow` are not on `psycopg`'s runtime root at all. `stubtest` passed the whole time: it
# walks RUNTIME to STUB, so a name the stub invents is never in the population it iterates.
#
# ⚑⚑⚑ AND ONE HAD A LIVE CONSUMER. `substrate/sandbox_connect.py:67` writes
# `from psycopg import Connection, DictRow` inside `if TYPE_CHECKING:` — which never executes, so
# the `ImportError` was LATENT rather than absent. `Connection` is genuinely exported and
# `DictRow` is not; the two sat in one import statement, indistinguishable to every instrument
# that had been pointed at this file. Moving it under runtime (a `typing.get_type_hints` call, a
# dropped guard) would have raised.
#
# ⚑ THE PLAIN FORM KEEPS THE NAME USABLE HERE WITHOUT CLAIMING THE RUNTIME FORWARDS IT — the
# `connect` overloads below annotate with `ConnParam`, `TupleRow` and `RowFactory`. Verified by
# `substrate/stub_reexport`, the only instrument that answers EXPORTED-FROM.
from psycopg.abc import ConnDict, ConnParam, Params, Query
from psycopg.connection import Connection as Connection
from psycopg.cursor import Cursor as Cursor
from psycopg.errors import ConnectionTimeout
from psycopg.errors import DatabaseError as DatabaseError
from psycopg.errors import DataError as DataError
from psycopg.errors import Error as Error
from psycopg.errors import IntegrityError as IntegrityError
from psycopg.errors import InterfaceError as InterfaceError
from psycopg.errors import InternalError as InternalError
from psycopg.errors import NotSupportedError as NotSupportedError
from psycopg.errors import OperationalError as OperationalError
from psycopg.errors import ProgrammingError as ProgrammingError
from psycopg.errors import Warning as Warning
from psycopg.rows import DictRow, RowFactory, TupleRow

from typing import overload

__version__: str

#: DBAPI level this driver implements.
apilevel: str

#: DBAPI thread-safety level.
threadsafety: int

#: DBAPI parameter marker style.
paramstyle: str

# ⚑⚑⚑ `connect` IS DECLARED AS ITS OWN OVERLOAD PAIR, THOUGH AT RUNTIME IT IS THE ALIAS
# `connect = Connection.connect`. Writing it as that alias is the obvious move and it is WRONG
# here — measured, not reasoned. The alias carries the CLASS's own `Row` parameter into the free
# function, so mypy renders the variants as `def [Row, R] (...)` with `Row` bound by nothing a
# caller supplies, and every call fails to match with the return falling back to `Any`. The
# consumer that proves this stub was refused by exactly that until the two were separated.
#
# ⚑ SO THIS IS THE ONE PLACE A SIGNATURE IS DELIBERATELY WRITTEN TWICE, against the standing
# preference for a single spelling — and it is recorded rather than left for a reader to
# discover, since the deduplicated form is the one that looks correct. `stubtest` checks both
# against the same runtime object, so the two cannot silently drift apart: the gate is what
# makes the duplication safe.
@overload
def connect(
    conninfo: str = "",
    *,
    autocommit: bool = False,
    prepare_threshold: int | None = 5,
    context: object | None = None,
    row_factory: None = None,
    cursor_factory: type[Cursor[TupleRow]] | None = None,
    **kwargs: ConnParam,
) -> Connection[TupleRow]: ...
@overload
def connect[R](
    conninfo: str = "",
    *,
    autocommit: bool = False,
    prepare_threshold: int | None = 5,
    context: object | None = None,
    row_factory: RowFactory[R],
    cursor_factory: type[Cursor[R]] | None = None,
    **kwargs: ConnParam,
) -> Connection[R]: ...
