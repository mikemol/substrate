------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg
--
-- Defines: --, negPos∘negNeg
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- The diagonal involutions form V₄: they compose as the Klein four-group
-- (negPos ∘ negNeg = negBoth) and commute. Realized on the substrate's V₄
-- via id↦e, negPos↦α, negNeg↦β, negBoth↦γ — the composition negPos∘negNeg
-- = negBoth mirrors α ·₄ β = γ.
------------------------------------------------------------------------

negPos∘negNeg : (x : Evidence) → negPos (negNeg x) ≡ negBoth x
negPos∘negNeg ⟨ p , n ⟩ = refl
