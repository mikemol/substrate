------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate
--
-- σ-iterate, HasOrderPerm, σ-iterate-add, HasOrderPerm-multiple — the Fin
-- specialization of the generic nth-iterate combinator, for order-k basis-
-- permutation work.
--
-- Ⓖ.iterate-to-foundation (2026-07-05): these WERE defined here, but nothing is
-- Fin- (or F2-) specific — σ-iterate is the nth-iterate of ANY endofunction.
-- The generic combinator now lives at its true home, Substrate.Foundation.
-- Function.Iterate; this module is its Fin-specialized RE-EXPORT (signatures
-- preserved verbatim, so the 37 dependents are untouched). Collapses the
-- misfiling under F2.Linear (the tower-as-combinatorial-basis principle). The
-- tower's Perm-power bridges to it via WitnessTower.CyclicCollapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ) renaming (_+_ to _ℕ+_; _*_ to _ℕ*_)
open import Substrate.Foundation.Eq using (_≡_)
import Substrate.Foundation.Function.Iterate as F

σ-iterate : ∀ {n} → ℕ → (Fin n → Fin n) → (Fin n → Fin n)
σ-iterate {n} = F.iterate {Fin n}

HasOrderPerm : ∀ {n} → (Fin n → Fin n) → ℕ → Set
HasOrderPerm {n} = F.HasFixedOrder {Fin n}

σ-iterate-add :
  ∀ {n} (σ : Fin n → Fin n) (a b : ℕ) (i : Fin n) →
  σ-iterate (a ℕ+ b) σ i ≡ σ-iterate a σ (σ-iterate b σ i)
σ-iterate-add {n} = F.iterate-add {Fin n}

HasOrderPerm-multiple :
  ∀ {n} (σ : Fin n → Fin n) (k m : ℕ) →
  HasOrderPerm σ k → HasOrderPerm σ (m ℕ* k)
HasOrderPerm-multiple {n} = F.HasFixedOrder-multiple {Fin n}
