---
name: stdlib-audit-progress
description: Stdlib audit COMPLETE. All Data.* / Induction.* / Level migrated to Substrate.Foundation/Algebra.Nat. Zero HIGH violations remaining.
metadata: 
  node_type: memory
  type: project
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

Per [[feedback_minimize_stdlib_deps]], the substrate has fully
migrated off stdlib dependencies. Status:

## ALL CATEGORIES: DONE

- ✅ `Data.Nat.DivMod` / `Data.Nat.Divisibility` / `Data.Nat.Induction` /
  `Induction.WellFounded` (1 file, the final HIGH violation):
  `Algebra.Nat.GCD.agda` migrated to substrate-native. The Foundation
  primitive `WellFounded` (Acc + acc) and Algebra.Nat sub-modules
  `Divides`, `DivMod`, `WellFounded` replace them. GCD now file-per-lemma
  (1 → 12 modules); all 7 downstream consumers (Bezout, ModEquiv,
  Q/Reduction, F2.Polynomial, F2.Polynomial.Wedge, V-Arc.Capstone)
  pass cleanly through the shim.

- ✅ `Data.Maybe` (5 of 5):
  Wedge, Utilities, ComposedReference (decomposed file-per-lemma);
  RuleAction, Pipeline.Sequent (import-only).

- ✅ `Data.List` (30 of 30): mass-mechanized via the migrator script.

- ✅ `Data.Unit.Polymorphic` / `Data.Empty.Polymorphic` (3 of 3):
  Category.Poly + Connections migrated.

- ✅ `Level` (196 of 196): mass-mechanized.

## Foundation primitives added during the audit

- `Substrate.Foundation.Maybe` — mono-universe Maybe.
- `Substrate.Foundation.List` + `List.Length` — universe-polymorphic.
- `Substrate.Foundation.Unit.Polymorphic` — ⊤ {ℓ} : Set ℓ.
- `Substrate.Foundation.Empty.Polymorphic` — ⊥ {ℓ} : Set ℓ + ⊥-elim.
- `Substrate.Foundation.Sum` — upgraded to universe-polymorphic.
- `Substrate.Foundation.Level` — added `0ℓ` alias.
- `Substrate.Foundation.WellFounded` — Acc + acc + WellFounded predicate.

## Algebra.Nat primitives added

- `Substrate.Algebra.Nat.WellFounded` — `<-wellFounded` for ℕ.
- `Substrate.Algebra.Nat.Divides` (file-per-lemma):
  Type, Refl, Trans, Mul, Sum, Zero.
- `Substrate.Algebra.Nat.DivMod` (file-per-lemma):
  DivSuc (structurally-recursive `_div-suc_`),
  Reconstruction (`div-mod-eq : a ≡ (a mod-suc b) + (a div-suc b) * (suc b)`).
- `Substrate.Algebra.Nat.GCD` (file-per-lemma, 1 → 12 modules):
  Wedge, ConstructWedge, EEATrace, ComputeTrace, GcdN, TraceDivides,
  GcdDividesLeft/Right, LcmN, ADividesLcm, BDividesLcm.

## Foundation.Fin combinatorics added (combine/remQuot arc)

- `Foundation.Fin.{Inject, Raise}` — `inject+` (Fin n → Fin (n + k))
  and `raise n` (Fin k → Fin (n + k)) embeddings.
- `Foundation.Fin.SplitAt` + `SplitAt/{InjectIdentity, RaiseIdentity, View}`
  — partition Fin (a + b) into Fin a ⊎ Fin b; SplitAtView provides
  the structural witness for inverse reasoning.
- `Foundation.Fin.{Combine, RemQuot}` — `combine : Fin m → Fin n → Fin (m * n)`
  (row-major pack) and its inverse.
- `Foundation.Fin.Combine.{RemQuotInverse, CombineRemQuotInverse}` —
  the two round-trip lemmas.
- `Foundation.Fin.Combine.Bijection` — `*↔× : Fin (m * n) ↔ (Fin m × Fin n)`,
  replacing the stdlib `Function.Bundles` bridge in
  `Cardinality.Product` (the previously-deferred "combine/divide arc").

## Foundation.Nat.Properties additions

- `Mul.*-assoc`
- `Order.≤-tight : suc m ≤ suc b → ¬ (suc m ≤ b) → m ≡ b`
- `Order.<→≤`, `Order.≤-trans`, `Order.≤-<-trans`
- `Sub.∸-+-id`, `Sub.∸-≤-self`, `Sub.m∸m≡0`, `Sub.∸-suc-l`, `Sub.∸-∸-cancel`

## Mechanization

`scripts/agda_stdlib_migrator.py` performs sed-style import rewriting
for routine stdlib → substrate migrations. Used to mechanize ~230 file
import changes in 2 mass commits. Does NOT decompose multi-lemma files
— that remains manual per the file-per-lemma discipline.

## How to apply

- New code: never `open import Data.{List,Maybe,Sum,Empty,Unit}`,
  `Data.{Empty,Unit}.Polymorphic`, `Data.Nat.*` (beyond what Foundation
  already provides), or `Level`. Use the substrate Foundation
  equivalents.
- For nat-arithmetic mod/div: use `Algebra.Nat.Mod._mod-suc_` and
  `Algebra.Nat.DivMod._div-suc_` (structurally-recursive on the first
  argument; divisor is `suc b`).
- For divisibility: use `Algebra.Nat.Divides`.
- For well-founded recursion: use `Foundation.WellFounded.Acc` +
  `Algebra.Nat.WellFounded.<-wellFounded`.
- Run the migrator (`python3 scripts/agda_stdlib_migrator.py --write
  --verify <file>`) for routine import migrations.
