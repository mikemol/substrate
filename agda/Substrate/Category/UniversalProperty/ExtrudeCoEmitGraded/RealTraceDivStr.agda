------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr
--
-- Defines: RealTrace-DivStr
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceDivStr where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- RealTrace as a DivStr (the common carrier of the CrossMix diagonal): z = the constant-0 trace, recon = cons the head.
RealTrace-DivStr : DivStr RealTrace
RealTrace-DivStr = record
  { z     = zero-trace                       -- the terminal divisor: the period-1 zero trace (the collapse pole)
  ; recon = λ q b r → cons (RealTrace.head b) r        -- recon: keep b's head digit, remainder r (the grade-raising shape)
  }
