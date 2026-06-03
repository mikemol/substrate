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

## The load-bearing spine — individual vs transitive

The first census counts **individual / direct** load (degree-1: files that
literally name the type). `scripts/audit_import_reach.py` adds the
**transitive** reach via the import graph (modules that transitively import a
direct user) + degrees-of-separation. They diverge:

| type | direct | transitive-downstream | total | max-sep |
|---|---|---|---|---|
| `_≡_` | 576 | 468 | 1044 | 5 |
| `ℕ` | 336 | 467 | 803 | 7 |
| `Fin` | 272 | 330 | 602 | 6 |
| `Σ` | 72 | **414** | 486 | 5 |
| `Vec` | 135 | 253 | 388 | 4 |
| `Word` | 92 | 209 | 301 | 6 |
| `Gen` | 46 | 249 | 295 | 6 |
| `Linear` | 112 | 135 | 247 | 4 |
| `Canonical` | 39 | 183 | 222 | 6 |
| `Permutation` | 73 | 62 | 135 | 3 |
| `UPArrow` | 75 | 28 | 103 | 3 |
| `Wedge` | 27 | 13 | 40 | 3 |
| `DivStr` | 11 | 1 | 12 | 1 |

Key shift: **`Σ` is rank-9 by direct use but rank-4 by transitive reach** — few
modules name it, but it sits under `Product`, which ~half the tree imports. So
"individual" undercounts foundation types and overcounts leaf types
(`Linear`/`Permutation`/`UPArrow` are more leaf-like — high direct, low
downstream). The honest load-bearing order is the transitive one.

Degrees of separation: cones are **shallow-and-wide** — most transitive
importers are 1–2 hops from a direct user, with thin tails to depth 5–7 (`ℕ`
reaches 7). The import graph's longest dependency chain is **depth 11**.
Highest direct fan-in (the import-spine): `Foundation.Eq` (595),
`Foundation.Nat` (342), `Foundation.Fin` (264), `Foundation.Product` (239),
`Foundation.Level` (160), `Algebra.F2.Vector` (142), `Foundation.Vec` (131).

326 of 493 types are cross-module load-bearing; ~166 are module-local.

## The inverse: least fan-in (the canopy)

Type fan-in distribution (external modules naming it): 166 at 0 (module-local),
**91 at exactly 1**, 44 at 2, 31 at 3, tapering. The 91 single-consumer types
are overwhelmingly **feeder → aggregator** pairs: a type in its own module,
consumed by exactly one collector (`Capstone`, `Phase{1,2,3}`, `PrimitivesAll`,
`PrimitiveInstances`, `TermAlgebraBridges`). Not redundancy — the file-per-lemma
discipline (build once, collect once). The young wedge arc shows the same youth
signature (`Interop`→`Registry`, `MulDivStr`/`Two`→`CrossMul`, `WedgeIso`→`Registry`).

Module fan-in: 31 at 0 (capstones / `All` / entry points), **516 at exactly 1**
(44% of the tree — the decomposition's leaves, each feeding one parent), 250 at
2, 101 at 3.

**Shape of the repo:** strongly bimodal — a tiny deeply-shared foundation (the
spine, ~90% transitive reach) under a wide shallow canopy of single-consumer
leaves (44% fan-in-1 modules), with little in the moderately-shared middle.
That is the signature of aggressive decomposition over a minimal core — the
canopy is load-bearing-by-one *on purpose*, NOT debt. (Tool:
`scripts/audit_import_reach.py`; inverse via the fan-in distribution.)

## Recommended actions (in order of safety)

1. Delete the 7 dead + decide `LeftKanExtension` (zero risk — nothing depends).
2. Consolidate `IsomorphicCocycleStructure` (one re-exports the other).
3. Route the per-instance `Canonical`/`Gen`/`V₄` through their generics.
4. Rename the same-name-different-meaning collisions for navigability.
5. (Optional) generic-ize the Zₙ-Coxeter cluster.
