------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right
--
-- Generic right-inverse property:
--
--   inv-right-canonical-ex : ∀ {w} → Canonical-ex w → normalize (w ++ inv w) ≡ []
--
-- Per-position proof chain (mirrors InvCanonical.Left with +ℕ-comm to
-- swap the addends, then reuses inv-pos-add-mod).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf

open import Substrate.Groups.Coxeter.Word using ([]; _++_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
-- ⚑ THE MIRROR OF `Left`, and it needs the identical rewire (Ⓐ¹²‴):
-- `Cyclic.Inverse` and `NthPower.Concat` both dissolved (771283c8), and
-- `normalize` is `ListPresentation`'s, not `Existential`'s.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPowerEq n
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize n
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
      (trans (power-cyclic-normalize (toℕ k ℕ+ toℕ (inv-pos k)))
             (cong power (trans (cong (_mod-suc n) (+ℕ-comm (toℕ k) (toℕ (inv-pos k))))
                                (inv-pos-add-mod k)))))
