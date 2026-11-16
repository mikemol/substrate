------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Order
--
-- L-iterate + iterate-apply-as-L-iterate + HasOrder-from-perm +
-- HasOrderPerm-multiple-Linear: lift permutation order to Linear
-- order via linear-extensionality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Order where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat.Nat
-- ⚑ Ⓑ6ᵇ: `ℕ*` at :83 named an operator that exists NOWHERE. Archaeology
-- (`git show 771283c8^`) shows the original import was
--
--     open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_*_ to _ℕ*_)
--
-- so `ℕ*` was `Foundation.Nat`'s `_*_` renamed AT THE IMPORT. The ban sweep
-- stripped the `renaming` — correctly, it is banned — and SUBSTITUTED NOTHING at
-- the use site, leaving a dangling spelling. Identical to `⊕` in `V4FullCocycle`
-- (Ⓠ6ᵈ) and `ℕ+` in `TensorProductView` (Ⓑ2): one sweep, one omission, three files.
--
-- ⚑ AND UNLIKE `ℕ+`, THERE IS NO ℕ-SUFFIXED HOME TO POINT AT. `_+_` was renamed
-- at source into `Foundation.Nat.Plus`, but ℕ multiplication kept its plain
-- spelling in `Foundation.Nat.Times` — so the repair is the BARE operator, not a
-- suffixed one. Reading the census (`--provides`) rather than assuming symmetry
-- with the `ℕ+` fix is what caught that.
open import Substrate.Foundation.Nat.Times

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; HasOrder; HasOrder-multiple)

open import Substrate.Foundation.Fin.Iterate
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear
  using (basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.IterateLift
  using (basis-permutation-order-k)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- L-iterate k L = L ∘L L ∘L ... ∘L L (k times, with id-L at k=0).

L-iterate : ∀ {n} → ℕ → Linear n n → Linear n n
L-iterate zero    L = id-L
L-iterate (suc k) L = L ∘L L-iterate k L

iterate-apply-as-L-iterate :
  ∀ {n} (L : Linear n n) (k : ℕ) (v : Vector n) →
  iterate k (apply L) v ≡ apply (L-iterate k L) v
iterate-apply-as-L-iterate L zero    v = refl
iterate-apply-as-L-iterate L (suc k) v =
  cong (apply L) (iterate-apply-as-L-iterate L k v)

------------------------------------------------------------------------
-- HasOrder-from-perm — lift permutation order to Linear order.

HasOrder-from-perm :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) →
  HasOrderPerm σ k →
  HasOrder (apply (basis-permutation-Linear σ)) k
HasOrder-from-perm {n} σ k order-witness v =
  trans (iterate-apply-as-L-iterate (basis-permutation-Linear σ) k v)
        (linear-extensionality
          (L-iterate k (basis-permutation-Linear σ))
          id-L
          basis-agreement
          v)
  where
    L = basis-permutation-Linear σ

    basis-agreement :
      (i : Fin n) → apply (L-iterate k L) (basis i) ≡ apply id-L (basis i)
    basis-agreement i =
      trans (sym (iterate-apply-as-L-iterate L k (basis i)))
            (basis-permutation-order-k σ k order-witness i)

------------------------------------------------------------------------
-- HasOrderPerm-multiple-Linear — bundle HasOrder-from-perm with
-- HasOrder-multiple.

HasOrderPerm-multiple-Linear :
  ∀ {n} (σ : Fin n → Fin n) (k m : ℕ) →
  HasOrderPerm σ k →
  HasOrder (apply (basis-permutation-Linear σ)) (m * k)
HasOrderPerm-multiple-Linear σ k m hyp =
  HasOrder-multiple {γ = apply (basis-permutation-Linear σ)} {k = k}
                    (HasOrder-from-perm σ k hyp) m
