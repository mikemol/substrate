------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod
--
-- The arithmetic core: position-plus-its-inverse vanishes mod (suc n).
--
--   inv-pos-add-mod : (k : Fin (suc n)) →
--                     (toℕ (inv-pos k) ℕ+ toℕ k) mod-suc n ≡ 0
--
-- Case-split on k:
--   * k = zero  : inv-pos zero  = fromℕ< (mod-suc-bound (suc n) n).
--                 toℕ = (suc n) mod-suc n = 0 by suc-mod-suc-self.
--                 (0 ℕ+ 0) mod-suc n = 0 definitionally.
--   * k = suc k': toℕ (inv-pos (suc k')) = (n ∸ toℕ k') mod-suc n
--                 = n ∸ toℕ k' by mod-suc-id (since n ∸ toℕ k' < suc n).
--                 (n ∸ toℕ k') ℕ+ suc (toℕ k') = suc n by ∸-+-id +-suc.
--                 (suc n) mod-suc n = 0 by suc-mod-suc-self.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
-- ⚑ `Nat.Le`/`Nat.Lt` ADDED: dropping the `Substrate.Foundation.Nat.` qualifier
-- (Ⓐ¹²′) means the bare `≤`/`<` must now be bound, and `Properties.Order` carries
-- the LEMMAS, not the relations themselves.
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Properties.Order
  using (<→≤; ≤-<-trans; <-suc-self)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id; ∸-≤-self)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Category.BWTEmergence

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod (n : ℕ) where

-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) into one leaf per theorem; `inv-pos`
-- is `Inverse.InvPos`'s (Ⓐ¹²).
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n

inv-pos-add-mod : (k : Fin (suc n)) →
                  (toℕ (inv-pos k) ℕ+ toℕ k) mod-suc n ≡ 0
inv-pos-add-mod zero =
  cong (λ x → (x ℕ+ 0) mod-suc n)
       (trans (toℕ-fromℕ< (mod-suc-bound (suc n) n))
              (suc-mod-suc-self n))
inv-pos-add-mod (suc k') =
  trans (cong (_mod-suc n) lhs-eq) (suc-mod-suc-self n)
  where
    -- ⚑ WAS `toℕ k' Substrate.Foundation.Nat.≤ n` — a FULLY-QUALIFIED reference
    -- to the undecomposed `Foundation.Nat`, written to disambiguate ℕ's `≤`/`<`
    -- from Fin's same-named operators.  That module was split into leaves
    -- (`Nat.Le`, `Nat.Lt`) by the ban-decompose commit, so the qualifier names
    -- nothing (Ⓐ¹²′).  ⚑ AND THE DISAMBIGUATION IS NOW STRUCTURAL: the leaves are
    -- imported by name above, so the bare operator resolves without a qualifier —
    -- which is the decomposition doing the work the qualifier was doing by hand.
    k'≤n : toℕ k' ≤ n
    k'≤n = <→≤ (toℕ-bound k')

    bound : (n ∸ toℕ k') < suc n
    bound = ≤-<-trans (∸-≤-self n (toℕ k')) (<-suc-self n)

    inv-pos-toℕ : toℕ (fromℕ< (mod-suc-bound (n ∸ toℕ k') n)) ≡ n ∸ toℕ k'
    inv-pos-toℕ = trans (toℕ-fromℕ< (mod-suc-bound (n ∸ toℕ k') n))
                        (mod-suc-id (n ∸ toℕ k') n bound)

    lhs-eq : toℕ (fromℕ< (mod-suc-bound (n ∸ toℕ k') n)) ℕ+ suc (toℕ k') ≡ suc n
    lhs-eq = trans (cong (_ℕ+ suc (toℕ k')) inv-pos-toℕ)
             (trans (+ℕ-suc (n ∸ toℕ k') (toℕ k'))
                    (cong suc (∸-+-id n (toℕ k') k'≤n)))
