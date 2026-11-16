------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegPosInvol
--
-- Defines: negPos-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegPosInvol where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- The chart involutions are involutions (each squares to the identity).
------------------------------------------------------------------------

negPos-invol : (x : Evidence) → negPos (negPos x) ≡ x
negPos-invol ⟨ true  , n ⟩ = refl
negPos-invol ⟨ false , n ⟩ = refl
