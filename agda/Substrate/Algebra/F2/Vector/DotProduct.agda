------------------------------------------------------------------------
-- Substrate.Algebra.F2.Vector.DotProduct
--
-- The F₂-valued inner product (dot product) on Vector n. Defined as
-- the sum-F₂ of componentwise F₂ products:
--
--   v ·F w = Σᵢ (lookup v i) · (lookup w i)
--
-- This is the standard bilinear form on F₂^n. Used by orthogonality
-- claims (e.g., V₄-plane ⊥ chirality-axis in F₂³, per M-11.dim3
-- Hodge-complement work).
--
-- Distinct from the existing `_·ⱽ_` (componentwise Hadamard product
-- in M-2), which returns a Vector. `_·F_` returns the F₂ sum.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Vector.DotProduct where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec using (lookup)

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
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂)

infixl 7 _·F_

_·F_ : ∀ {n} → Vector n → Vector n → F₂
_·F_ {n} v w = sum-F₂ {n} (λ i → (lookup v i) · (lookup w i))
