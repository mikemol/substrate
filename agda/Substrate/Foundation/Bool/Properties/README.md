# `Bool.Properties` — substrate-native Bool laws

Replaces stdlib `Data.Bool.Properties` for the lemmas used downstream (the F₂³
group, the F₂ structures, the dual-rail evidence connectives). Every proof is a
case analysis; `_∧_` and `_∨_` match on their FIRST argument, so `assoc` and
`identityʳ` need only split that one.

Three families live here:

- **xor** — `XorIdentityL/R`, `XorSame`, `XorComm`, `XorAssoc`: the F₂ additive group.
- **∧ / ∨ semilattice** — comm / assoc / idem / identity / distrib / zero. Added
  for `Logic.Evidence.Verdict.Connectives`, which lifts each rail's Bool ops;
  reusable for any F₂ or Boolean lattice structure.
- **the bridge + eliminators** — `OrXorAnd` is the ANF of OR (`OR = XOR ⊕ AND`),
  the canonical foundational home read by `CayleyDickson.Grade.OrAnf` and derived
  from by `Algebra.F2.FromBool`. `AndElimL/R` are the ∧-reflection eliminators.

Ⓓ: `identityˡ`, the distributivity pair and the annihilators were RELOCATED here
from `Algebra.Semiring.Instances` (proven there "for lack of a prior home"), and
`AndElimL/R` from `Realizability.Charter` + `…Wedge.GUnit` (both had re-proved
them). The carrier home is Bool's properties.
