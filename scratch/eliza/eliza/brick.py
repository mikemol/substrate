"""Eliza.Brick — typed 2-cell in the substrate's three-axis structure.

Python mirror of `agda/Substrate/Pipeline/Brick.agda`. Each brick has
three edges (Data, State, Compute) and witnesses one of six morphisms
among the sorts, with the third axis serving as the witness.

The Agda is the spec; this module is the runtime witness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generic, Protocol, TypeVar, runtime_checkable

D = TypeVar("D")        # Data type
S = TypeVar("S")        # State type
D2 = TypeVar("D2")
S2 = TypeVar("S2")


class Witnessing(Enum):
    """The six oriented morphisms among (D, S, C).

    Each brick instantiates one; the third axis serves as the witness.
    Mirror of `agda/Substrate/Pipeline/Brick.agda::Witnessing`.
    """
    D_TO_S = "D⇒S"      # write: C witnesses
    S_TO_D = "S⇒D"      # read: C witnesses
    D_TO_C = "D⇒C"      # data selects compute: S witnesses
    C_TO_D = "C⇒D"      # compute produces data: S witnesses
    S_TO_C = "S⇒C"      # state dispatches compute: D witnesses
    C_TO_S = "C⇒S"      # parameterised mutation: D witnesses


class Axis(Enum):
    """The witnessing axis for each morphism."""
    DATA = "𝔻"
    STATE = "𝕊"
    COMPUTE = "ℂ"


_WITNESS_AXIS: Dict[Witnessing, Axis] = {
    Witnessing.D_TO_S: Axis.COMPUTE,
    Witnessing.S_TO_D: Axis.COMPUTE,
    Witnessing.D_TO_C: Axis.STATE,
    Witnessing.C_TO_D: Axis.STATE,
    Witnessing.S_TO_C: Axis.DATA,
    Witnessing.C_TO_S: Axis.DATA,
}


def witness_axis(w: Witnessing) -> Axis:
    return _WITNESS_AXIS[w]


@dataclass(frozen=True)
class BrickType:
    """The four-edge type signature of a brick.

    Mirror of `BrickType` record in the Agda.
    """
    D_in: type
    D_out: type
    S_in: type
    S_out: type


@runtime_checkable
class Brick(Protocol[D, S, D2, S2]):
    """A typed step + metadata.

    Concrete bricks implement step (the C axis), declare a witnessing,
    and emit per-brick stats. The protocol is parameterised over the
    edge types; static type-checking via `BrickType` is structural.
    """
    brick_type: BrickType
    witnesses: Witnessing
    name: str
    homomorphism_tag: str

    def step(self, d_in: D, s_in: S) -> "tuple[D2, S2]":
        ...

    def stats(self) -> Dict[str, Any]:
        ...


@dataclass
class FunctionBrick(Generic[D, S, D2, S2]):
    """A Brick whose step is a plain Python function.

    Used by the `Lift` combinator to promote pure transforms and as a
    base class for ad-hoc bricks.
    """
    brick_type: BrickType
    witnesses: Witnessing
    fn: Callable[[D, S], "tuple[D2, S2]"]
    name: str = "anonymous"
    homomorphism_tag: str = ""
    _stats_emit: Callable[[], Dict[str, Any]] = field(default=lambda: {})

    def step(self, d_in: D, s_in: S) -> "tuple[D2, S2]":
        return self.fn(d_in, s_in)

    def stats(self) -> Dict[str, Any]:
        return self._stats_emit()


# --- Pure transforms (state = Unit) ----------------------------------------


class Unit:
    """The unit type. Used as both S_in and S_out for pure transforms."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "()"


UNIT = Unit()


def Lift(
    fn: Callable[[D], D2],
    D_in: type,
    D_out: type,
    name: str = "lift",
    homomorphism_tag: str = "",
) -> FunctionBrick:
    """Promote a pure D-only function into a Brick with trivial S edges.

    Mirror of `pure-as-brick` in the Agda.
    """
    return FunctionBrick(
        brick_type=BrickType(D_in=D_in, D_out=D_out, S_in=Unit, S_out=Unit),
        witnesses=Witnessing.D_TO_S,  # trivial since S = Unit
        fn=lambda d, _: (fn(d), UNIT),
        name=name,
        homomorphism_tag=homomorphism_tag,
    )
