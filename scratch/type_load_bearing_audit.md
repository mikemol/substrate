# Type load-bearing audit (2026-06-03)

Answers: which types are load-bearing (to what), which aren't at all, and where
a type isn't *unique* — and how the non-unique ones relate. Tool:
`scripts/audit_type_load_bearing.py` (comment-stripped cross-reference census;
493 top-level `data`/`record` types). Structural clustering:
`scripts/agda_similarity.py --cluster`.

## Not load-bearing at all

**Truly dead** — declared, referenced in *no code* anywhere (incl. own module):

| type | module | note |
|---|---|---|
| `Fibration` | `Category/GrothendieckConstruction.agda` | |
| `LensFunctoriality` | `Category/StochasticLens.agda` | speculative |
| `MultiLayerRotation` | `Category/CoxeterPermutationGroup.agda` | |
| `QFreeLinearizationSketch` | `Category/FreeLinearizationR/QInstance.agda` | a *Sketch* |
| `SufficientStatisticInfoTheory` | `Probability/BaezFritzLeinster.agda` | speculative |
| `_≤ℤ_` | `Algebra/Q/Order.agda` | no infix use either — leftover |
| `Image-Equivalent` | `Algebra/F2/Code/Universal.agda` | code-dead; only **comment** mentions elsewhere |

Several are named `*Sketch` / speculative — abandoned scaffolding. Safe to
delete (nothing depends on them) or to wire to a real consumer.

**Catalog-only** — load-bearing to no proof, only re-exported:

- `LeftKanExtension` (`Category/KanExtension.agda`) — appears solely in the
  `Generators` catalog. Either give it a consumer or accept it as catalogued-API.

## Not unique (17 duplicate names) — and how they relate

- **Related variants (legit, keep — note the relation):**
  - `Linear` — `Algebra/F2/Linear` vs `Algebra/Q/Linear`: linear maps over F₂
    vs ℚ (different field).
  - `Action` — `Algebra/GroupAction` vs `SetoidGroup/Action`: plain vs setoid.
  - `IsTorsor` — `Algebra/Torsor` (over `Group`) vs `Cocycle` (over
    `SetoidGroup`): same concept, two group notions.
  - `Wedge` — `Algebra/Wedge` (generic, mine) vs `Algebra/Nat/GCD/Wedge` (ℕ):
    the generic *generalises* the ℕ one; bridged by `fromℕ-Wedge`. Documented.
  - `⊤` / `⊥` / `⊤₁` — `Foundation/Unit`,`Empty` + their `Polymorphic`
    variants: level-polymorphic siblings.

- **Per-instance families subsumable by a generic:**
  - `Canonical`, `Gen` — declared per Coxeter group (`FreeCyclic-Coxeter`,
    `V4-Coxeter`, `Coxeter/Cyclic/Base`). The generic `Coxeter.Cyclic` already
    exists; the per-group copies are candidates to route through it.

- **Genuine redundancy (consolidate):**
  - `IsomorphicCocycleStructure` — `Algebra/IsomorphicCocycle` is a
    substrate-native *rebuild* of `Cocycle.agda`'s record; neither imports the
    other. Two definitions of one concept. → make one re-export the other (or
    retire the original).

- **Same name, different meaning (namespace collisions — rename for clarity,
  not redundancy):** `Axis` (geometry vs pipeline brick), `Crumb`, `Line`
  (Fano plane vs grammar), `Step` (Charter vs Loop), `Section` (discipline /
  pedagogy / F₂ transfer), `V4` (two site contexts).

- **`V₄` declared in 4 places** (`V4/Bijection`, `ResidueCompensation`,
  `RuleAction/V4`, `ComposedReference/V4`) — the canonical Klein group is
  `Groups/V4`; these should route through it rather than re-declare.

## Structural redundancy (shape-equal, different names)

One cluster from the similarity tool (token-scale, ≥0.85): the **Zₙ-Coxeter
family** — `Z2/Z4/Z5/Z7-Coxeter` (mean 0.85). Per-n instances of one
construction; candidates for the generic `Coxeter.Cyclic` treatment (Z3 differs
enough to stay separate).

## The load-bearing spine (top degree = # modules depending on it)

`_≡_` (630), `ℕ` (368), `Fin` (297), `Vec` (137), `Word` (133), `Linear` (121),
`V4`/`V₄`, `Σ`, `Permutation`, `UPArrow` (73), `Canonical`, `List`, `Gen`,
`CategoryOf`. 326 of 493 types are cross-module load-bearing; ~166 are
module-local (load-bearing only to their own proofs).

## Recommended actions (in order of safety)

1. Delete the 7 dead + decide `LeftKanExtension` (zero risk — nothing depends).
2. Consolidate `IsomorphicCocycleStructure` (one re-exports the other).
3. Route the per-instance `Canonical`/`Gen`/`V₄` through their generics.
4. Rename the same-name-different-meaning collisions for navigability.
5. (Optional) generic-ize the Zₙ-Coxeter cluster.
