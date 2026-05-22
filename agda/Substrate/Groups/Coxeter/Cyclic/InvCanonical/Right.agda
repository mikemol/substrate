------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right
--
-- Generic right-inverse property:
--
--   inv-right-canonical-ex : ∀ {w} → Canonical-ex w → normalize (w ++ inv w) ≡ []
--
-- Per-position proof chain (mirrors InvCanonical.Left with +-comm to
-- swap the addends, then reuses inv-pos-add-mod).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)

open import Substrate.Groups.Coxeter.Word using ([]; _++_)

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod n
  using (inv-pos-add-mod)

inv-right-canonical-ex : ∀ {w} → Canonical-ex w → normalize (w ++ inv w) ≡ []
inv-right-canonical-ex = canonical-cover-ex
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  per-pos
  where
    per-pos : (k : Fin (suc n)) →
              normalize (power (toℕ k) ++ inv (power (toℕ k))) ≡ []
    per-pos k =
      trans (cong (λ x → normalize (power (toℕ k) ++ x)) (inv-power-eq k))
      (trans (cong normalize (power-concat-eq (toℕ k) (toℕ (inv-pos k))))
      (trans (power-cyclic-normalize (toℕ k + toℕ (inv-pos k)))
             (cong power (trans (cong (_mod-suc n) (+-comm (toℕ k) (toℕ (inv-pos k))))
                                (inv-pos-add-mod k)))))
