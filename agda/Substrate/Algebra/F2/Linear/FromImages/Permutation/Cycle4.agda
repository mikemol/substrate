------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
--
-- The 4-cycle σ₄ : Fin 4 → Fin 4 lifted via basis-permutation-Linear
-- to an order-4 HasOrder instance on Vector 4.
--
-- Sibling of Cycle3. Demonstrates the basis-permutation-Linear +
-- HasOrder-from-perm machinery at a different order; no per-instance
-- proof beyond the trivial refl-per-inhabitant for σ₄^4 = id.
--
-- Per [[project-torsion-element-universal]]: order 4 is the next
-- natural torsion site after orders 2 (Hodge ★) and 3 (Cycle3).
-- Connects to potential Z₄-Coxeter and dihedral D₄ instances.
--
-- Per [[feedback-minimize-stdlib-deps]]: per-n concrete cyclic
-- instance rather than a generic cyclic-shift {n} that would require
-- Data.Fin.Permutation or Data.Nat.DivMod machinery. Each new order
-- is a small additional file (4 + 4 + 2 lines).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (basis-permutation-Linear; HasOrderPerm; HasOrder-from-perm)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)

------------------------------------------------------------------------
-- N-1: σ₄ — the 4-cycle on Fin 4 (0 → 1 → 2 → 0).
------------------------------------------------------------------------

σ₄ : Fin 4 → Fin 4
σ₄ zero                            = suc zero
σ₄ (suc zero)                      = suc (suc zero)
σ₄ (suc (suc zero))                = suc (suc (suc zero))
σ₄ (suc (suc (suc zero)))          = zero

------------------------------------------------------------------------
-- N-2: σ₄ has order 4 as a permutation — σ₄⁴ = id pointwise.
------------------------------------------------------------------------

σ₄-HasOrderPerm : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm zero                            = refl
σ₄-HasOrderPerm (suc zero)                      = refl
σ₄-HasOrderPerm (suc (suc zero))                = refl
σ₄-HasOrderPerm (suc (suc (suc zero)))          = refl

------------------------------------------------------------------------
-- N-3: cycle4-Linear — the linear endomap induced by σ₄.
------------------------------------------------------------------------

cycle4-Linear : Linear 4 4
cycle4-Linear = basis-permutation-Linear σ₄

------------------------------------------------------------------------
-- N-4: HasOrder-cycle4 — order-4 instance via the structural lift.
------------------------------------------------------------------------

HasOrder-cycle4 : HasOrder (apply cycle4-Linear) 4
HasOrder-cycle4 = HasOrder-from-perm σ₄ 4 σ₄-HasOrderPerm
