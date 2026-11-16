------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.ToFin4
--
-- Defines: to-fin4
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.ToFin4 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Linear.Linear



------------------------------------------------------------------------
-- F₂² ↔ Fin 4 conversion. V₄ ≅ F₂² makes Fin 4 the binary fan-out
-- (i₁, i₂) ∈ Fin 2 × Fin 2 ↔ i ∈ Fin 4. Used to dispatch the 16-cell
-- 4×4 Cayley as a 2⁴ binary tree via `fin-cover-2⁴`.
------------------------------------------------------------------------

to-fin4 : Fin 2 → Fin 2 → Fin 4
to-fin4 zero       zero       = zero
to-fin4 zero       ₁ = suc zero
to-fin4 ₁ zero       = suc ₁
to-fin4 ₁ ₁ = suc ₂
