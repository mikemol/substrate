------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv
--
-- Generic double-inverse property:
--
--   inv-inv-canonical-ex : ∀ {w} → Canonical-ex w → inv (inv w) ≡ w
--
-- Per-position proof requires `toℕ (inv-pos (inv-pos k)) ≡ toℕ k`.
-- Case-split on k : Fin (suc n):
--   k = zero    : both sides reduce to (suc n) mod-suc n = 0.
--   k = suc k'  : (suc n ∸ (n ∸ toℕ k')) mod-suc n
--                 ≡ (suc (toℕ k')) mod-suc n by ∸-suc-l + ∸-∸-cancel
--                 ≡ suc (toℕ k') = toℕ k    by mod-suc-id + toℕ-bound.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _∸_; _<_; _≤_)
open import Substrate.Foundation.Nat.Properties.Order
  using (<→≤; ≤-<-trans; <-suc-self)
open import Substrate.Foundation.Nat.Properties.Sub
  using (∸-≤-self; ∸-suc-l; ∸-∸-cancel)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong-trans)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; mod-suc-id; suc-mod-suc-self)

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat n

------------------------------------------------------------------------
-- 1. toℕ-inv-pos-inv-pos: the Fin-level involution at the toℕ image.
------------------------------------------------------------------------

private
  -- toℕ (inv-pos k) ≡ (suc n ∸ toℕ k) mod-suc n.
  toℕ-inv-pos : (k : Fin (suc n)) →
                toℕ (inv-pos k) ≡ (suc n ∸ toℕ k) mod-suc n
  toℕ-inv-pos k = toℕ-fromℕ< (mod-suc-bound (suc n ∸ toℕ k) n)

  -- For k > 0 (toℕ k = suc k'), toℕ (inv-pos k) ≡ n ∸ toℕ k' (mod-suc-id kicks in).
  toℕ-inv-pos-suc : (k' : Fin n) →
                    toℕ (inv-pos (suc k')) ≡ n ∸ toℕ k'
  toℕ-inv-pos-suc k' =
    trans (toℕ-inv-pos (suc k'))
          (mod-suc-id (n ∸ toℕ k') n
                      (≤-<-trans (∸-≤-self n (toℕ k')) (<-suc-self n)))

  -- For k = 0, toℕ (inv-pos zero) ≡ 0.
  toℕ-inv-pos-zero : toℕ (inv-pos (zero {n})) ≡ 0
  toℕ-inv-pos-zero =
    trans (toℕ-inv-pos zero) (suc-mod-suc-self n)

toℕ-inv-pos-inv-pos : (k : Fin (suc n)) →
                      toℕ (inv-pos (inv-pos k)) ≡ toℕ k
toℕ-inv-pos-inv-pos zero =
  trans (toℕ-inv-pos (inv-pos zero))
  (cong-trans (λ x → (suc n ∸ x) mod-suc n) toℕ-inv-pos-zero
         (suc-mod-suc-self n))
toℕ-inv-pos-inv-pos (suc k') =
  trans (toℕ-inv-pos (inv-pos (suc k')))
  (cong-trans (λ x → (suc n ∸ x) mod-suc n) (toℕ-inv-pos-suc k')
  (cong-trans (_mod-suc n) (∸-suc-l n (n ∸ toℕ k') (∸-≤-self n (toℕ k')))
  (cong-trans (λ x → (suc x) mod-suc n) (∸-∸-cancel n (toℕ k') (<→≤ (toℕ-bound k')))
         (mod-suc-id (suc (toℕ k')) n (toℕ-bound (suc k'))))))

------------------------------------------------------------------------
-- 2. inv-inv-canonical-ex: the generic double-inverse property.
------------------------------------------------------------------------

inv-inv-canonical-ex : ∀ {w} → Canonical-ex w → inv (inv w) ≡ w
inv-inv-canonical-ex = canonical-cover-ex
  (λ {w} _ → inv (inv w) ≡ w)
  per-pos
  where
    per-pos : (k : Fin (suc n)) →
              inv (inv (power (toℕ k))) ≡ power (toℕ k)
    per-pos k =
      cong-trans inv (inv-power-eq k)
      (trans (inv-power-eq (inv-pos k))
             (cong power (toℕ-inv-pos-inv-pos k)))
