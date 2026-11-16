------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left
--
-- Generic left-inverse property:
--
--   inv-left-canonical-ex : ∀ {w} → Canonical-ex w → normalize (inv w ++ w) ≡ []
--
-- Per-position proof chain (dispatched via canonical-cover-ex):
--   inv-power-eq            : inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))
--   power-concat-eq         : power j₁ ++ power j₂ ≡ power (j₁ ℕ+ j₂)
--   power-cyclic-normalize  : normalize (power j) ≡ power (j mod-suc n)
--   inv-pos-add-mod         : (toℕ (inv-pos k) ℕ+ toℕ k) mod-suc n ≡ 0
--   power zero              ≡ []  (definitionally)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To

open import Substrate.Groups.Coxeter.Word using ([]; _++_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) — three leaves used here (Ⓐ¹²‴).
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq n
-- ⚑ `normalize` IS NOT `Existential`'s — it belongs to `ListPresentation`, which
-- Existential merely opened.  Applied to the same five arguments every other
-- consumer uses, so all see ONE instance.
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
-- ⚑ `NthPower.Concat` DISSOLVED too — the two facts this proof composes.
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize n
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
      (trans (power-cyclic-normalize (toℕ (inv-pos k) ℕ+ toℕ k))
             (cong power (inv-pos-add-mod k))))
