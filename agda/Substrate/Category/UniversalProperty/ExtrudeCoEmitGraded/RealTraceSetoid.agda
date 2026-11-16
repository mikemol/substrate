------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceSetoid
--
-- Defines: RealTrace-Setoid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RealTraceSetoid where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Bisim.Sym
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.R.Trace.Bisim.Sym

open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-stardivstr-setoid: the ~-SETOID on RealTrace (refining Substrate.Algebra.Setoid), on which the
--     conjugation IS involutive and recon-compatible. This is StarDivStr's data with ≈ := ~ — the honest home
--     (352: the record's intensional ≡ is a CARRIER requirement; the setoid supplies the totality as ≈).
------------------------------------------------------------------------
RealTrace-Setoid : Setoid RealTrace _~_
RealTrace-Setoid = record { ≈-refl = ~-refl ; ≈-sym = ~-sym ; ≈-trans = ~-trans }
