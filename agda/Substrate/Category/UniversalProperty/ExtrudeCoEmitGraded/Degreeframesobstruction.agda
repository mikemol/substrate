------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Degreeframesobstruction
--
-- Defines: degree-frames-obstruction
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Degreeframesobstruction where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Empty.Bot
  renaming (⊥ to Bot)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ObstructionDegree
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Degreenotbisim
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- and the ~/ν frame: t ~ r ⟺ no obstruction degree (the degree is where the ν-frame agreement first fails).
-- degree-is-nilpotency: an obstruction degree n (ν frame) is exactly a witnessed failure of coherence-everywhere.
degree-frames-obstruction : (r t : RealTrace) (n : ℕ) → ObstructionDegree r t n → (t ~ r → Bot)
degree-frames-obstruction = degree⇒not-bisim
