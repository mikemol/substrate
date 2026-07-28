------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left
--
-- Generic left-inverse property:
--
--   inv-left-canonical-ex : ∀ {w} → Canonical-ex w → normalize (inv w ++ w) ≡ []
--
-- Per-position proof chain (dispatched via canonical-cover-ex):
--   inv-power-eq            : inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))
--   power-concat-eq         : power j₁ ++ power j₂ ≡ power (j₁ + j₂)
--   power-cyclic-normalize  : normalize (power j) ≡ power (j mod-suc n)
--   inv-pos-add-mod         : (toℕ (inv-pos k) + toℕ k) mod-suc n ≡ 0
--   power zero              ≡ []  (definitionally)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq using (_≡_; trans; cong)

open import Substrate.Groups.Coxeter.Word using ([]; _++_)

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n using (power)
open import Substrate.Groups.Coxeter.Cyclic.Inverse n using (inv; inv-power-eq; inv-pos)
open import Substrate.Groups.Coxeter.Cyclic.Existential n using (Canonical-ex; normalize; canonical-cover-ex)
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat n
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod n
  using (inv-pos-add-mod)


inv-left-canonical-ex : ∀ {w} → Canonical-ex w → normalize (inv w ++ w) ≡ []
inv-left-canonical-ex = canonical-cover-ex
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  per-pos
  where
    per-pos : (k : Fin (suc n)) →
              normalize (inv (power (toℕ k)) ++ power (toℕ k)) ≡ []
    per-pos k =
      trans (cong (λ x → normalize (x ++ power (toℕ k))) (inv-power-eq k))
      (trans (cong normalize (power-concat-eq (toℕ (inv-pos k)) (toℕ k)))
      (trans (power-cyclic-normalize (toℕ (inv-pos k) + toℕ k))
             (cong power (inv-pos-add-mod k))))
