------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitnuisbisimfwd
--
-- Defines: coemit-nu-is-bisim-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitnuisbisimfwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bisimprefix
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesalways
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- coemit-agrees-is-bisim (GENUINE, via the ν frame) + coemit-v4-simplicial-literal (the SHARED square-zero law,
-- NOT a literal ≡ — trace-mul is on RealTrace, SimplicialBoundary's ∂ is on ordered face-lists, DIFFERENT
-- carriers; the honest link is the shared d²=0/∂²=0 shape). + coemit-s3-on-v4 (documented: the ⋊ gluing).
------------------------------------------------------------------------
-- (3) the GENUINE agrees-is-bisim: the ν-frame content — bisimilarity ⟺ agreement at every grade (NOT the
-- ∂²=0-trivialized swap [coemit-agrees-always], but the real ν coherence). Both directions (agree-limit + bisim→prefix).
coemit-nu-is-bisim-fwd : (a b : RealTrace) → b ~ a → ((n : ℕ) → agree-upto n a b)
coemit-nu-is-bisim-fwd a b p n = bisim→prefix n a b p
