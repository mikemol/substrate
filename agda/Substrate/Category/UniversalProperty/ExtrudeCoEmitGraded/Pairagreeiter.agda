------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairagreeiter
--
-- Defines: pair-agree→iter
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pairagreeiter where

open import Substrate.Foundation.Unit
open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Iterate
  renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.Refinement
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lh
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Lt
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrefinementpair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Ppair
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

------------------------------------------------------------------------
-- pair-gfp-formal: the ⋂ₙ of coemit-refinement-pair as a FORMAL gfp — and THE BRIDGE (318 deferred): the
-- grading-Φ (Φ-pair) and the carrier-Φ (Φ_T, whose νΦ is bisimilarity) are DISTINCT, but their FIXED POINTS
-- COINCIDE AT THE LIMIT. νΦ-pair (r,t) = (∀ n, Riterate n P⁰-pair (r,t)) [the intersection of the descending
-- chain] ↔ t ~ r [the carrier's coinductive bisimilarity]. So the graded descent's LIMIT = the carrier's νΦ.
------------------------------------------------------------------------
-- reverse of pair-iter→agree: agree-upto n r t → the n-fold refinement fiber (by induction, cong lh/lt).
pair-agree→iter : (n : ℕ) (r t : RealTrace) → agree-upto n r t → Riterate coemit-refinement-pair n P⁰-pair (r , t)
pair-agree→iter zero    r t _  = tt
pair-agree→iter (suc n) r t eq = cong (lh (RealTrace.head t)) eq , pair-agree→iter n (RealTrace.tail r) (RealTrace.tail t) (cong lt eq)
