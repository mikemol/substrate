------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegPosNegNegComm
--
-- Defines: negPos-negNeg-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegPosNegNegComm where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg



-- the diagonal V₄ is abelian: negPos and negNeg commute.
negPos-negNeg-comm : (x : Evidence) → negPos (negNeg x) ≡ negNeg (negPos x)
negPos-negNeg-comm ⟨ p , n ⟩ = refl
