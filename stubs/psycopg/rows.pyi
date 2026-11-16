# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The row-factory surface, declared at the module psycopg defines it in.

⚑⚑ A STUB IS FOUND BY IMPORT PATH, AND `stubtest` CHECKS A NAME AT THAT PATH — both halves
measured rather than assumed. Declaring `dict_row` only at the package root left
`from psycopg.rows import dict_row` resolving to the LIBRARY: the stub was present, correct,
and silently not consulted, so the `Any` it exists to remove came straight back. Moving it here
fixed that AND the mirror-image fault, where the root declaration was reported *"not present at
runtime"* because `psycopg.dict_row` does not exist. A package stub must mirror the MODULE
STRUCTURE of what it shadows.

⚑ THE ROW TYPE IS A PARAMETER ON EVERY NAME HERE. That parameter carries the answer from a row
factory through `Connection` to `Cursor.fetchall`, and dropping it — the move this stub was
commissioned to not repeat — would hand every caller a list of unknowns.

⚑⚑⚑ THE THREE `__call__` SIGNATURES CARRY THE ONE UNRESOLVABLE RESIDUE IN THIS STUB, AND IT IS
RECORDED RATHER THAN NARROWED AWAY. psycopg writes these parameters as leading-dunder names —
the pre-PEP-570 way to spell positional-only — so Python name-mangles them and the runtime
parameter really is called `_RowFactory__cursor`. Two consumers of that fact disagree, and
neither is wrong:

  * `stubtest` compares against the runtime and demands the MANGLED NAME and NO `/`, because
    the mangled name is observable and a caller could pass it by keyword.
  * MYPY's protocol matching demands `/`. Without it, an ordinary function whose parameter is
    named `cursor` — which is what `dict_row` IS — does not satisfy the protocol, and every
    `row_factory=dict_row` call is refused.

⚑ ALL FOUR SPELLINGS WERE TRIED AND MEASURED, not reasoned about: mangled+`/` (3 stubtest
findings, callers work), mangled alone (0 findings, callers REFUSED), plain+`/` (6 findings,
callers work), plain alone (6 findings, callers refused). The stub keeps **mangled + `/`** —
the form under which the type system is correct for every caller, at the cost of three
`stubtest` findings that all say the same thing about the same construct.

⚑⚑ THAT COST IS NAMED HERE BECAUSE A STUB WHOSE GATE IS PARTLY RED MUST SAY SO. The temptation
was to drop these protocols and type the factories as bare callables — which would pass the gate
by removing the claim, i.e. exactly the withdrawal this stub was commissioned to not repeat. The
finding is real, it is the library's own pre-PEP-570 spelling meeting a modern checker, and it
belongs in the record rather than in a deletion.

⚑⚑⚑ RE-MEASURED 2026-09-02 BEFORE GRANTING THE RELIEF BELOW, because a documented residue is a
CLAIM and inherits no credit from being written down. Removing the `/` — the "0 findings"
option — was applied to all three protocols and `substrate/sandbox_connect.py` was typechecked
against it. It fails with three errors: `No overload variant of "connect" matches` for
`row_factory=dict_row`, and the connection's row type collapsing to `Any`. **The zero-finding
spelling reintroduces exactly the `Any` this stub exists to remove.** The prior agent's reading
holds, and the residue stays.

⚑⚑ SO THE RELIEF IS THREE NAMED ENTRIES, NOT A FLAG. `stubtest --ignore-positional-only` makes
this whole package green in one word — and would silence that finding class across all 83
psycopg modules, including a contradiction nobody has looked at. These three entries name the
three findings, so the exemption is exactly as narrow as the residue and is reviewed with it.
The gate passes NO `--ignore-unused-allowlist`, so if psycopg ever adopts PEP 570 these entries
stop matching and become findings in their own right — the exemption cannot outlive its cause.

⟡declines-signature: psycopg.rows.RowMaker.__call__, psycopg.rows.RowFactory.__call__,
    psycopg.rows.BaseRowFactory.__call__
"""

from collections.abc import Sequence
from typing import Protocol

from psycopg._cursor_base import BaseCursor

#: A row rendered as a mapping from column name to its adapted value.
#:
#: ⚑ `object`, NOT `Any` — psycopg spells this `dict[str, Any]`. A column's adapted type is
#: genuinely the adapter's choice, so the dynamism is real; `object` accepts exactly the same
#: VALUES and refuses exactly the USES that were never checked. A caller who knows a column is
#: an `int` narrows with an `isinstance` the checker verifies.
type DictRow = dict[str, object]

#: A row rendered as a tuple of adapted values, in column order.
type TupleRow = tuple[object, ...]

class RowMaker[Row](Protocol):
    """Build one row object from the adapted column values of one record."""

    def __call__(self, _RowMaker__values: Sequence[object], /) -> Row: ...

class RowFactory[Row](Protocol):
    """Inspect a cursor's result description and return the maker for its rows."""

    def __call__(
        self, _RowFactory__cursor: BaseCursor[object, object], /
    ) -> RowMaker[Row]: ...

class BaseRowFactory[Row](Protocol):
    """A row factory accepting either cursor kind."""

    def __call__(
        self, _BaseRowFactory__cursor: BaseCursor[object, object], /
    ) -> RowMaker[Row]: ...

def dict_row(cursor: BaseCursor[object, object]) -> RowMaker[DictRow]:
    """Row factory rendering each record as a `{column: value}` mapping."""
    ...

def tuple_row(cursor: BaseCursor[object, object]) -> RowMaker[TupleRow]:
    """Row factory rendering each record as a tuple — psycopg's default."""
    ...
