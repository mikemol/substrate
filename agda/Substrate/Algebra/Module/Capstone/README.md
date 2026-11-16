# Capstone — Substrate.Algebra.Module.Capstone

A capstone is a **directory with a README**, not a module. It ATTESTS a
roster; it does not import one. The former `Capstone.agda` was a pure barrel —
prose and imports, no definitions of its own — so the attestation is prose
and the roster is a table. A consumer that wants one of these names binds
it at its OWNER, directly.

```
Substrate.Algebra.Module.Capstone

Mod10 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].

Re-exports the M-arc + Mod-arc + summarises the gap-closure /
retrofit map.

=====================================================================
TOWER SUMMARY
=====================================================================

ALGEBRA LADDER (M1-M10)
  M1  Magma           — single binary op
  M2  Semigroup       — Magma + assoc
  M3  Monoid          — Semigroup + identity (F₁ included as ⊤)
  M4  Group           — Monoid + inverse
  M5  AbelianGroup    — Group + commutativity
  M6  Semiring        — additive CommMonoid + mult Monoid + distrib
  M7  Ring            — Semiring with additive AbelianGroup
  M8  Field           — Ring + multiplicative inverse on non-zero
  M9  F2 as Field     — F₂'s ring/field laws as accessor projections
  M10 Q as Field      — ℚ's Magma scaffolding + Field obligation rec

MODULE TOWER (Mod1-Mod10)
  Mod1 Module           — R-Module record (4 module axioms)
  Mod2 ModuleHom        — structure-preserving map
  Mod3 ModuleHom.Compose — identity + composition (category laws)
  Mod4 Module.Free      — FreeCarrier A n = Vec A n + componentwise ops
  Mod5 Module.Free.Basis — basis embedding + FreeBasisUniversal
  Mod6 F2.AsModule      — F₂ⁿ as Module F₂-Ring
  Mod7 Q.AsModule       — ℚⁿ as Module from ℚ-Field-Obligation
  Mod8 Module.Free.UniqueExtension — generic linear-extensionality
  Mod9 FreeLinearizationR.AsModule — FLR bridge to FreeBasisUniversal
  Mod10 (this file)     — capstone + summary

=====================================================================
GAP-CLOSURE MAPPING
=====================================================================

| Audit gap                                  | Closed at | How             |
|--------------------------------------------|-----------|-----------------|
| ℚ-ring-laws (Q-arc deferreds)              | M10 + Mod7| Obligation rec  |
| ℚ-vector +-identity (TPQ inherits)         | Mod7      | Mod7 lifter     |
| ℚ-bilinearity (modify-Q-prod)              | M7 + Mod7 | Ring distrib    |
| ℚ-linear-extensionality (FLQ7/TPQ7)        | Mod8      | from-universal  |
| F₂-vector arithmetic                       | Mod6      | F₂-FreeModule   |
| FreeLinearizationR universal property      | Mod9      | Bridge record   |
| F₁ as base case                            | M3        | trivial Monoid  |
| RuleAction operad assoc + identity         | M3        | (mechanical)    |
| GeneratorOperad right-identity             | M3        | Monoid right-id |

Two sibling-tower gaps remain (B-arc respect-≈M, Conway add/trans);
closed by Set1-Set5 (Setoid) and G1-G10 (game-induction) arcs.
```

M-arc (algebra ladder)

F₂ / ℚ as Field instances

Module tower

Module instances

M-arc + Mod-arc closure. The substrate's algebraic foundation is
now a unified two-tower: every per-R / per-Vector law derives as
a tower-accessor projection. Sibling towers (Setoid, Conway)
launch from here.

## Roster

| name | owner |
|---|---|
| `Magma` | `Substrate.Algebra.Magma` |
| `Semigroup` | `Substrate.Algebra.Semigroup` |
| `Monoid` | `Substrate.Algebra.Monoid` |
| `F₁-Monoid` | `Substrate.Algebra.Monoid` |
| `Group` | `Substrate.Algebra.Group` |
| `AbelianGroup` | `Substrate.Algebra.AbelianGroup` |
| `Semiring` | `Substrate.Algebra.Semiring` |
| `Ring` | `Substrate.Algebra.Ring` |
| `Field` | `Substrate.Algebra.Field` |
| `F₂-Field` | `Substrate.Algebra.F2.AsField` |
| `F₂-Ring` | `Substrate.Algebra.F2.AsField` |
| `ℚ-+-Magma` | `Substrate.Algebra.Q.AsField` |
| `ℚ-·-Magma` | `Substrate.Algebra.Q.AsField` |
| `ℚ-Field-Obligation` | `Substrate.Algebra.Q.AsField` |
| `Module` | `Substrate.Algebra.Module` |
| `ModuleHom` | `Substrate.Algebra.Module.Hom` |
| `id-ModHom` | `Substrate.Algebra.Module.Hom.Compose` |
| `compose-ModHom` | `Substrate.Algebra.Module.Hom.Compose` |
| `FreeCarrier` | `Substrate.Algebra.Module.Free` |
| `free-zero` | `Substrate.Algebra.Module.Free` |
| `free-+` | `Substrate.Algebra.Module.Free` |
| `free-scalar` | `Substrate.Algebra.Module.Free` |
| `basis-vec` | `Substrate.Algebra.Module.Free.Basis` |
| `free-basis` | `Substrate.Algebra.Module.Free.Basis` |
| `FreeBasisUniversal` | `Substrate.Algebra.Module.Free.Basis` |
| `FreeModuleExtensionality` | `Substrate.Algebra.Module.Free.UniqueExtension` |
| `FreeBasisUniversalAt` | `Substrate.Algebra.Module.Free.UniqueExtension` |
| `extensionality-from-universal` | `Substrate.Algebra.Module.Free.UniqueExtension` |
| `F₂-FreeModule` | `Substrate.Algebra.F2.AsModule` |
| `F₂-FreeModule-on-FreeCarrier` | `Substrate.Algebra.F2.AsModule` |
| `module Lifters` | `Substrate.Algebra.Q.AsModule` |
