------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegBothInvol
--
-- Defines: negBoth-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegBothInvol where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



negBoth-invol : (x : Evidence) → negBoth (negBoth x) ≡ x
negBoth-invol ⟨ true  , true  ⟩ = refl
negBoth-invol ⟨ true  , false ⟩ = refl
negBoth-invol ⟨ false , true  ⟩ = refl
negBoth-invol ⟨ false , false ⟩ = refl
