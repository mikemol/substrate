------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obstructionpersists
--
-- Defines: obstruction-persists
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obstructionpersists where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeshrink
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- obstruction-unify: the ONE graded obstruction across cover-the-cycle / CofreeDual / CrossMix. The obstruction
-- (disagreement between r,t) PERSISTS: ¬ agree-upto n ⇒ ¬ agree-upto (suc n) [contrapositive of agree-shrink] —
-- so a disagreement at grade n is a disagreement at ALL later grades (the graded obstruction, upward-closed by
-- degree, dⁿ=0 shape). And coherence ⟺ NO obstruction: t ~ r ⟺ (∀ n, agree-upto n r t). So the obstruction =
-- the failing grades (CrossMix's nilpotency degree = CofreeDual's ~-obstruction = the aperiodic pole — ONE thing).
------------------------------------------------------------------------

-- the obstruction PERSISTS (upward-closed in degree): disagreeing at grade n ⇒ disagreeing at (suc n).
obstruction-persists : (n : ℕ) (r t : RealTrace)
                     → (agree-upto n r t → ⊥) → (agree-upto (suc n) r t → ⊥)
obstruction-persists n r t ¬agree-n agree-sucn = ¬agree-n (agree-shrink n r t agree-sucn)
