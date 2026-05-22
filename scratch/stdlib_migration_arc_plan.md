# Stdlib → in-tree migration arc plan

Audit identified ~29 stdlib import sites across ~16 files as candidates
for in-tree replacement. This file plans the slices.

## Constraints discovered

- Stdlib `Algebra.Bundles.Group c ℓ` is **Setoid-parameterised** (carries
  an explicit `_≈_`). Substrate's `Substrate.Algebra.Group A` is fixed to
  `_≡_` propositional equality. **Not a 1:1 record swap.** Each
  definer-file needs a new in-tree value built; each consumer-file then
  switches to consuming the new value.

- V4.agda, S3.agda, S4.agda etc. EXPORT stdlib `Group 0ℓ 0ℓ` values
  (`V₄-Group`, `S₃-Group`, `S₄-Group`) whose `_≈_` is fixed to `_≡_`. So
  they ARE compatible in shape with substrate group; the migration is
  re-export plus consumer update.

- Cocycle.agda parameterises `Action`/`IsTorsor` on stdlib `Group ℓg ℓg`.
  Migrating Cocycle requires migrating every consumer of Action/IsTorsor.
  Coupled — bigger slice.

## Slice protocol

Each slice:
1. Touches ≤ 1 file (≤ 2 for tightly-coupled definer+consumer pairs).
2. Verified by `agda --safe <file>` to typecheck.
3. Monotonic: stdlib import count strictly decreases OR an in-tree
   adapter has been added that enables the next slice's decrement.

## Inventory of slices (planned)

| # | File | Action | Notes |
|---|---|---|---|
| 1 | (audit setup) | Verify baseline batch typecheck of all 12+4+1 candidate files | precursor |
| 2 | `Substrate/Algebra/Bijection.agda` (NEW) | Create in-tree `_↔_` record with `to/from/left-inv/right-inv` + `sym` | shadow for Tier 3 |
| 3 | `Substrate/Groups/V4.agda` | Add `V₄-Group-substrate : Substrate.Algebra.Group V₄` alongside stdlib | additive |
| 4 | `Substrate/Groups/S3.agda` | Same pattern | additive |
| 5 | `Substrate/Groups/S4.agda` | Same pattern | additive |
| 6 | `Substrate/Groups/F2Cubed.agda` | Same pattern | additive |
| 7 | `Substrate/Groups/SFin.agda` | Same pattern | additive |
| 8 | `Substrate/Groups/Symmetric.agda` | Same pattern | additive |
| 9 | `Substrate/Algebra/GL3F2/Characters.agda` | Swap `Data.Integer` → `Substrate.Algebra.Z` | swap |
| 10 | `Substrate/Cardinality.agda` | Use `Substrate.Algebra.Bijection` for one site | swap |
| 11 | `Substrate/Cardinality/Product.agda` | Same | swap |
| 12 | `Substrate/Cocycles/V4Signature/Codeword.agda` | Same | swap |
| 13 | `Substrate/Cocycles/V4Signature/Codeword/Live.agda` | Same | swap |
| 14 | `Substrate/Groups/Coxeter/GroupAdapter.agda` | Drop stdlib if pure adapter; otherwise rebuild on substrate Group | investigate |
| 15 | `Substrate/Groups/Coxeter/SemidirectProductGroup.agda` | Same | investigate |
| 16 | `Substrate/Cocycle.agda` | Reparameterise Action/IsTorsor over Substrate.Algebra.Group | breaking |
| 17 | `Substrate/Discipline.agda` | Use Substrate.Algebra.Group as gauge type | breaking-consumer of #16 |
| 18 | `Substrate/Groups/V4-Embedding.agda` | Consume V₄-Group-substrate / S₄-Group-substrate | consumer |
| 19 | `Substrate/Groups/S4-Composed.agda` | Same | consumer |
| 20 | `Substrate/Cocycles/V4Signature.agda` | Same | consumer |
| 21 | `Substrate/Cocycles/V4Signature/S4GroupIso.agda` | Reparameterise iso | uses Algebra.Morphism.Structures too |
| 22-30 | Remove stdlib aliases | After every consumer migrated, drop the stdlib `V₄-Group`, `S₃-Group`, etc. exports; drop `open import Algebra.{Bundles,Structures,Definitions,Morphism.Structures,Properties.Group}` lines | cleanup |

Slices 22-30 are intentionally separated cleanup. After all consumers
are migrated, dropping each stdlib export is independent and verifiable.

## Risks

- Cocycle.agda reparam (#16) is the largest single change; if it
  breaks, fall back to dual-parameterised Action.
- Some in-tree files may transitively expect stdlib Group through
  the consumer chain (e.g., F2Cubed consumes from Coxeter); check
  before migrating.

## Status

Plan written. Execution begins from Slice 1.
