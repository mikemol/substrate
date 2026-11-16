------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegBothCentralSwapE
--
-- Defines: negBoth-central-swapE
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegBothCentralSwapE where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg



------------------------------------------------------------------------
-- The kernel ℤ₂ = {id, −id} is CENTRAL: −id commutes with both generators
-- of the extension (this is what makes 1 → ℤ₂ → D₄ → V₄ → 1 *central*).
------------------------------------------------------------------------

negBoth-central-swapE : (x : Evidence) → negBoth (swapE x) ≡ swapE (negBoth x)
negBoth-central-swapE ⟨ p , n ⟩ = refl
