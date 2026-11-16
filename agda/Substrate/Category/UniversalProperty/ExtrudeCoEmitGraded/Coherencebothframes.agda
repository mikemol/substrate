------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coherencebothframes
--
-- Defines: coherence-both-frames
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coherencebothframes where

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


-- coherence-everywhere (both frames agree: cross nilpotent at every grade = no obstruction degree = bisimilar).
coherence-both-frames : (r t : RealTrace) → t ~ r → ((n : ℕ) → ObstructionDegree r t n → Bot)
coherence-both-frames r t p n deg = degree⇒not-bisim r t n deg p
