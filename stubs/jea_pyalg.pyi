"""`jea_pyalg` - the hash-cons interner, narrowed to what the `sql_lift` shim reaches.

DECLARED FOR ONE CONSUMER, the `jea/metalanguage/sql_lift.py` shim (W4 file 3 swap, tick 35):
it interns `RelTerm` lowerings into the shared carrier and asks `CrossMix.coherent` whether two
interned ids are one canonical node. Three names, read from `jea/metalanguage/jea_pyalg.py`:
`IR` is a frozen dataclass at `:41` whose key is `(kind, role, op, lit, children)` with `payload`
as residue; `Intern` at `:62` holds `nodes` (id -> IR) and `intern(node, span=None) -> int` at
`:69` and `size() -> int` at `:82` (the carrier node count the report and the census print);
`CrossMix(intern)` at `:649` with `coherent(a_id, b_id) -> bool` at `:699`.

THE ELEMENT TYPES ARE NARROWED WHERE UPSTREAM LEAVES THEM BARE. `children: tuple = ()` upstream
is `tuple[int, ...]` here because the docstring beside it says "tuple of child IR ids (ints into
the intern table)", and `payload: tuple = ()` is `tuple[object, ...]` because it is residue this
stub does not describe. `span` is `Optional[tuple]` upstream and `object | None` here.

⟡declines: `Wedge`, `Trace`, `PyDivStr`, `Lowerer`, `CstLowerer`, `CrossTerm`, `lower_source`,
`lower_source_cst`, `trace_fold`, `trace_fold_lazy`, `collapse`, `grade`, `head_spine`,
`full_skeleton`, `full_skeleton_steps`, `Intern.table`/`fanin`/`src`, `CrossMix.cross_term` and
every private member. Nothing in the shim lowers python source through this module; the four
package modules it composes take the interner as a callable.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class IR:
    kind: str
    role: str = ""
    op: str = ""
    lit: str = ""
    children: tuple[int, ...] = ()
    payload: tuple[object, ...] = ()
    def key(self) -> tuple[str, str, str, str, tuple[int, ...]]: ...

class Intern:
    nodes: list[IR]
    def __init__(self) -> None: ...
    def intern(self, node: IR, span: object | None = None) -> int: ...
    def size(self) -> int: ...

class CrossMix:
    I: Intern
    def __init__(self, intern: Intern) -> None: ...
    def coherent(self, a_id: int, b_id: int) -> bool: ...
