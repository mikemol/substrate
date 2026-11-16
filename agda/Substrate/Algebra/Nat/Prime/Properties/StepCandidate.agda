------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.StepCandidate
--
-- Defines: step-candidate
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.StepCandidate where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.Dividessuc
open import Substrate.Algebra.Nat.Prime.Properties.TwoLeToNotLt2
open import Substrate.Algebra.Nat.Prime.Properties.LeToLtSumEq



-- given no divisor in [2,c) and c < n, either c ∣ n (a proper divisor found)
-- or the no-divisor certificate extends to [2, suc c).
step-candidate : (n c : ℕ) → c < n →
  ((d : ℕ) → 2 ≤ d → d < c → ¬ (d ∣ n)) →
  (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n))) ⊎
  ((d : ℕ) → 2 ≤ d → d < suc c → ¬ (d ∣ n))
step-candidate n zero          _   _    =
  inj₂ (λ d 2≤d d<1 → ⊥-elim (2≤→¬<2 d 2≤d (<-suc-r d<1)))
step-candidate n (suc zero)    _   _    =
  inj₂ (λ d 2≤d d<2 → ⊥-elim (2≤→¬<2 d 2≤d d<2))
step-candidate n (suc (suc c')) c<n none with (suc c') ∣suc? n
... | yes c∣n  = inj₁ (suc (suc c') , s≤s (s≤s z≤n) , c<n , c∣n)
... | no ¬c∣n  = inj₂ ext
  where
    ext : (d : ℕ) → 2 ≤ d → d < suc (suc (suc c')) → ¬ (d ∣ n)
    ext d 2≤d (s≤s d≤ssc') d∣n with ≤→<⊎≡ d (suc (suc c')) d≤ssc'
    ... | inj₁ d<ssc' = none d 2≤d d<ssc' d∣n
    ... | inj₂ d≡ssc' = ¬c∣n (subst (λ x → x ∣ n) d≡ssc' d∣n)
