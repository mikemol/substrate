"""Eliza.Transducer — per-symbol transducer interfaces.

Two flavours per the Agda contract:

  * Transducer α β  = a function α → β. Stateless. Lifts to lists by map.
  * StatefulTransducer α S β = a step (S, α) → (S, β). Stateful coalgebra.

These are Protocols rather than classes — any callable / class that
satisfies the shape is accepted. The substrate-honest reading: the
interface IS the contract; concrete instantiations are private to the
module that owns them.
"""

from __future__ import annotations

from typing import Callable, List, Protocol, Tuple, TypeVar

In = TypeVar("In")
S = TypeVar("S")
Out = TypeVar("Out")


Transducer = Callable[[In], Out]


def run(t: Transducer[In, Out], xs: List[In]) -> List[Out]:
    """Lift a stateless transducer over a Word α (Python list)."""
    return [t(x) for x in xs]


class StatefulTransducer(Protocol[In, S, Out]):
    """Stateful coalgebra step. The Manifold-walker is the canonical example."""

    @property
    def s0(self) -> S: ...

    def step(self, s: S, x: In) -> Tuple[S, Out]: ...


def run_stateful(
    t: StatefulTransducer[In, S, Out], xs: List[In]
) -> Tuple[S, List[Out]]:
    """Fold a stateful transducer over a word, returning final state + output word."""
    s = t.s0
    ys: List[Out] = []
    for x in xs:
        s, y = t.step(s, x)
        ys.append(y)
    return s, ys
