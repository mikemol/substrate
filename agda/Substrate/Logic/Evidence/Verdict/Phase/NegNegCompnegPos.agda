------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegNegCompnegPos
--
-- Defines: negNeg∘negPos
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegNegCompnegPos where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



negNeg∘negPos : (x : Evidence) → negNeg (negPos x) ≡ negBoth x
negNeg∘negPos ⟨ p , n ⟩ = refl
