------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Iterate
--
-- σ-iterate, HasOrderPerm, σ-iterate-add, HasOrderPerm-multiple — the Fin
-- specialization of the generic nth-iterate combinator (Foundation.Function.
-- Iterate), for order-k basis-permutation work.
--
-- Ⓖ.tower-basis-phase3 (2026-07-05): this WAS
-- Algebra.F2.Linear.FromImages.Permutation.Iterate — but nothing here is Fin-
-- (or F2-) specific beyond the Fin instantiation, and NOTHING it imports is
-- F₂: it is purely the generic iterate restricted to `Fin n → Fin n`. It was
-- the residue of Ⓖ.iterate-to-foundation (which moved the generic combinator
-- to Foundation.Function.Iterate but left this Fin-shim misfiled under the
-- F2.Linear path, so F₂-free consumers — Coxeter, CoxeterFin, the witness-tower
-- cyclic bridge — that imported HasOrderPerm still transitively dragged the
-- F2.Linear.Permutation barrel). Relocated to its true F₂-free home. The
-- Linear-lift layer (Permutation.Compose/Order/IterateLift) and the genuinely-
-- F2 consumers now import it from here too; the tower's Perm-power bridges to
-- it via WitnessTower.CyclicCollapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Iterate where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ) renaming (_+_ to _ℕ+_; _*_ to _ℕ*_)
open import Substrate.Foundation.Eq using (_≡_)
import Substrate.Foundation.Function.Iterate as F

σ-iterate : ∀ {n} → ℕ → (Fin n → Fin n) → (Fin n → Fin n)
σ-iterate {n} = F.iterate {Fin n}

HasOrderPerm : ∀ {n} → (Fin n → Fin n) → ℕ → Set
HasOrderPerm {n} = F.HasFixedOrder {Fin n}

-- ⟡cap-384 ELABORATION HASH-CONS. `HasOrderPerm σ k = ∀ x → iterate k σ x ≡ x`
-- REDUCES: at a CONCRETE σ it normalizes the k-fold permutation power. A record
-- field typed `HasOrderPerm σ n` therefore re-normalizes that power at EVERY site
-- that builds the record at a concrete σ (measured: an order-7 capability record
-- costs ~307 MB, though the proof itself is ~82 MB at abstract σ). `OrderOf` is an
-- OPAQUE alias: outside this block it does NOT unfold, so a field typed `OrderOf σ n`
-- is a non-reducing token (the cross-module elaboration memo). `seal-order`/
-- `unseal-order` convert (they live in the block, so they see OrderOf = HasOrderPerm)
-- — no `unfolding` needed downstream. Wrap the proof at ABSTRACT σ (cheap), hand
-- consumers the sealed token. (Same seal idiom as Permutation.Cyclic's cyclic-Linear.)
opaque
  OrderOf : ∀ {n} → (Fin n → Fin n) → ℕ → Set
  OrderOf f k = HasOrderPerm f k

  seal-order : ∀ {n} {f : Fin n → Fin n} {k} → HasOrderPerm f k → OrderOf f k
  seal-order p = p

  unseal-order : ∀ {n} {f : Fin n → Fin n} {k} → OrderOf f k → HasOrderPerm f k
  unseal-order p = p

σ-iterate-add :
  ∀ {n} (σ : Fin n → Fin n) (a b : ℕ) (i : Fin n) →
  σ-iterate (a ℕ+ b) σ i ≡ σ-iterate a σ (σ-iterate b σ i)
σ-iterate-add {n} = F.iterate-add {Fin n}

HasOrderPerm-multiple :
  ∀ {n} (σ : Fin n → Fin n) (k m : ℕ) →
  HasOrderPerm σ k → HasOrderPerm σ (m ℕ* k)
HasOrderPerm-multiple {n} = F.HasFixedOrder-multiple {Fin n}
