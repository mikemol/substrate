------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegNegInvol
--
-- Defines: negNeg-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegNegInvol where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



negNeg-invol : (x : Evidence) → negNeg (negNeg x) ≡ x
negNeg-invol ⟨ p , true  ⟩ = refl
negNeg-invol ⟨ p , false ⟩ = refl
