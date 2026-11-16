------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
--
-- Defines: zero-trace
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-as-crossmix (VERIFIED partial, D-verify-dont-assume-substance): RealTrace fits DivStr (C/z/recon) — the
-- COMMON CARRIER for a CrossMix DIAGONAL — but NOT MulDivStr (a coinductive stream has no natural mul; the full
-- CrossMix cross=mul R (transl a)(transl b) needs a multiplicative carrier RealTrace lacks). So the DivStr part
-- instantiates (below); the mul/Nilpotent cross-term is the CORRESPONDENCE (agree-upto = Coherent, ⟡obstruction-unify),
-- not a literal instance. HONEST: the diagonal common-carrier IS RealTrace-DivStr; the multiplicative face is documented.
------------------------------------------------------------------------

-- the constant-0 trace (the period-1 collapse pole = the terminal divisor z).
zero-trace : RealTrace
RealTrace.head zero-trace = 0
RealTrace.tail zero-trace = zero-trace
