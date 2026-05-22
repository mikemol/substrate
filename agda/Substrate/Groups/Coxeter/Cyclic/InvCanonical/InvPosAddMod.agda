------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod
--
-- The arithmetic core: position-plus-its-inverse vanishes mod (suc n).
--
--   inv-pos-add-mod : (k : Fin (suc n)) →
--                     (toℕ (inv-pos k) + toℕ k) mod-suc n ≡ 0
--
-- Case-split on k:
--   * k = zero  : inv-pos zero  = fromℕ< (mod-suc-bound (suc n) n).
--                 toℕ = (suc n) mod-suc n = 0 by suc-mod-suc-self.
--                 (0 + 0) mod-suc n = 0 definitionally.
--   * k = suc k': toℕ (inv-pos (suc k')) = (n ∸ toℕ k') mod-suc n
--                 = n ∸ toℕ k' by mod-suc-id (since n ∸ toℕ k' < suc n).
--                 (n ∸ toℕ k') + suc (toℕ k') = suc n by ∸-+-id +-suc.
--                 (suc n) mod-suc n = 0 by suc-mod-suc-self.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc)
open import Substrate.Foundation.Nat.Properties.Order
  using (<→≤; ≤-<-trans; <-suc-self)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id; ∸-≤-self)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; mod-suc-id; suc-mod-suc-self)

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Inverse n using (inv-pos)

inv-pos-add-mod : (k : Fin (suc n)) →
                  (toℕ (inv-pos k) + toℕ k) mod-suc n ≡ 0
inv-pos-add-mod zero =
  cong (λ x → (x + 0) mod-suc n)
       (trans (toℕ-fromℕ< (mod-suc-bound (suc n) n))
              (suc-mod-suc-self n))
inv-pos-add-mod (suc k') =
  trans (cong (_mod-suc n) lhs-eq) (suc-mod-suc-self n)
  where
    k'≤n : toℕ k' Substrate.Foundation.Nat.≤ n
    k'≤n = <→≤ (toℕ-bound k')

    bound : (n ∸ toℕ k') Substrate.Foundation.Nat.< suc n
    bound = ≤-<-trans (∸-≤-self n (toℕ k')) (<-suc-self n)

    inv-pos-toℕ : toℕ (fromℕ< (mod-suc-bound (n ∸ toℕ k') n)) ≡ n ∸ toℕ k'
    inv-pos-toℕ = trans (toℕ-fromℕ< (mod-suc-bound (n ∸ toℕ k') n))
                        (mod-suc-id (n ∸ toℕ k') n bound)

    lhs-eq : toℕ (fromℕ< (mod-suc-bound (n ∸ toℕ k') n)) + suc (toℕ k') ≡ suc n
    lhs-eq = trans (cong (_+ suc (toℕ k')) inv-pos-toℕ)
             (trans (+-suc (n ∸ toℕ k') (toℕ k'))
                    (cong suc (∸-+-id n (toℕ k') k'≤n)))
