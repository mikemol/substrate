"""Eliza.Sequent — structural-rule and fixed-point sequent bricks.

Python mirror of `agda/Substrate/Pipeline/Sequent.agda`. A Sequent is
the "wire" between two bricks: a structural derivation justifying that
the upstream's D-out is acceptable as the downstream's D-in.

Two kinds:
  * Structural-rule sequents (one-shot derivations): identity, cut,
    weakening, contraction, exchange, coerce.
  * Fixed-point sequents (iterate until canonical): the
    normalize-to-canonical pattern from `FreeCyclic-Coxeter` lifted
    to the brick layer.

A Sequent is itself a Brick (pure transform, S = Unit), tagged with
its structural rule and homomorphism property.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Generic, Optional, Tuple, TypeVar

from eliza.brick import BrickType, FunctionBrick, Unit, UNIT, Witnessing

A = TypeVar("A")
B = TypeVar("B")


class SequentRule(Enum):
    IDENTITY = "identity"
    CUT = "cut"
    WEAKENING = "weakening"
    CONTRACTION = "contraction"
    EXCHANGE = "exchange"
    COERCE = "coerce"
    FIXED_POINT = "fixed-point"


@dataclass
class Sequent:
    """A pure data-to-data transform tagged with a structural rule.

    Stored as a `FunctionBrick` with explicit rule metadata. The Brick
    protocol is satisfied because `Sequent` exposes the same attributes.
    """
    rule: SequentRule
    derivation: Callable[[Any], Any]
    A_type: type
    B_type: type
    name: str = "sequent"
    homomorphism_tag: str = ""

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=self.A_type, D_out=self.B_type, S_in=Unit, S_out=Unit
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.D_TO_S  # pure transform; S = Unit

    def step(self, d_in: Any, s_in: Any) -> Tuple[Any, Any]:
        return self.derivation(d_in), UNIT

    def stats(self) -> Dict[str, Any]:
        return {}


# --- Concrete structural-rule constructors --------------------------------


def Identity(t: type) -> Sequent:
    """The trivial wire: A ⊢ A. Used when D-out and D-in are the same type."""
    return Sequent(
        rule=SequentRule.IDENTITY,
        derivation=lambda x: x,
        A_type=t,
        B_type=t,
        name=f"id[{t.__name__}]",
    )


def Coerce(A_type: type, B_type: type, f: Callable[[Any], Any]) -> Sequent:
    """Apply a named isomorphism f: A → B."""
    return Sequent(
        rule=SequentRule.COERCE,
        derivation=f,
        A_type=A_type,
        B_type=B_type,
        name=f"coerce[{A_type.__name__}→{B_type.__name__}]",
    )


def Exchange() -> Sequent:
    """Swap a tuple: A × B → B × A."""
    return Sequent(
        rule=SequentRule.EXCHANGE,
        derivation=lambda ab: (ab[1], ab[0]),
        A_type=tuple,
        B_type=tuple,
        name="exchange",
    )


def Weakening(default_b: Any, B_type: type) -> Sequent:
    """A ⊢ A × B by providing a default B-value (the "weakened" content)."""
    return Sequent(
        rule=SequentRule.WEAKENING,
        derivation=lambda a: (a, default_b),
        A_type=object,  # weakening accepts anything on the A side
        B_type=tuple,
        name=f"weaken[{B_type.__name__}]",
    )


def Contraction() -> Sequent:
    """(A × A) ⊢ A by projection to the first component (both copies are equal)."""
    return Sequent(
        rule=SequentRule.CONTRACTION,
        derivation=lambda aa: aa[0],
        A_type=tuple,
        B_type=object,
        name="contract",
    )


def Cut(s1: Sequent, s2: Sequent) -> Sequent:
    """Compose two sequents: A ⊢ B and B ⊢ C give A ⊢ C."""
    return Sequent(
        rule=SequentRule.CUT,
        derivation=lambda a: s2.derivation(s1.derivation(a)),
        A_type=s1.A_type,
        B_type=s2.B_type,
        name=f"cut[{s1.name}; {s2.name}]",
    )


# --- Fixed-point sequents (iterate-to-canonical) --------------------------


@dataclass
class CanonicalSpec(Generic[A]):
    """A canonical predicate + the fixed-point obligation."""
    is_canonical: Callable[[Any], bool]
    description: str = ""


@dataclass
class FixedPointSequent:
    """A Sequent whose derivation is iterated until canonical.

    The brick's D-in is admitted; the derivation runs in a loop, shunting
    each output back as the next input, until `spec.is_canonical(value)`
    holds. Then the canonical value is emitted on D-out and the next
    D-in is admitted.

    Iteration is bounded by `max_steps` to guarantee termination in
    Agda-spec-compliant fashion. If the bound is exceeded, the partial
    result is returned (signalling potential non-canonicalness).
    """
    derivation: Callable[[Any], Any]
    spec: CanonicalSpec
    A_type: type
    max_steps: int = 1024
    name: str = "fixed-point"
    homomorphism_tag: str = ""

    @property
    def brick_type(self) -> BrickType:
        return BrickType(
            D_in=self.A_type, D_out=self.A_type, S_in=Unit, S_out=Unit
        )

    @property
    def witnesses(self) -> Witnessing:
        return Witnessing.D_TO_S  # pure transform

    def step(self, d_in: Any, s_in: Any) -> Tuple[Any, Any]:
        value = d_in
        for _ in range(self.max_steps):
            if self.spec.is_canonical(value):
                return value, UNIT
            value = self.derivation(value)
        # Bound exceeded; return current value (non-canonical signal).
        return value, UNIT

    def stats(self) -> Dict[str, Any]:
        return {}


def FixedPoint(
    derivation: Callable[[Any], Any],
    is_canonical: Callable[[Any], bool],
    A_type: type,
    max_steps: int = 1024,
    name: str = "fixed-point",
) -> FixedPointSequent:
    """Convenience constructor for a fixed-point sequent."""
    spec = CanonicalSpec(is_canonical=is_canonical, description=name)
    return FixedPointSequent(
        derivation=derivation, spec=spec, A_type=A_type,
        max_steps=max_steps, name=name,
    )
