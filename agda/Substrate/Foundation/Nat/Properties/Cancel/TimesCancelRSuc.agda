------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Cancel.TimesCancelRSuc
--
-- Defines: *-cancelʳ-suc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Cancel; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Cancel.TimesCancelRSuc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.SucInjective
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Cancel.PlusCancelL
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



-- cancel a positive right multiplier (suc d ≥ 1).
*-cancelʳ-suc : (m n d : ℕ) → (m * suc d) ≡ (n * suc d) → m ≡ n
*-cancelʳ-suc zero    zero    d eq = refl
*-cancelʳ-suc zero    (suc n) d ()
*-cancelʳ-suc (suc m) zero    d ()
*-cancelʳ-suc (suc m) (suc n) d eq =
  cong suc (*-cancelʳ-suc m n d (+-cancelˡ (suc d) eq))
