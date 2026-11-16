------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Linear
--
-- Defines: Linear
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Linear where

open import Substrate.Foundation.Nat.Nat
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
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- F₂-linear map: record bundling apply + linearity proofs.
------------------------------------------------------------------------

record Linear (n m : ℕ) : Set where      -- ⟦shape:62b90d64 apply,preserves-+,preserves-*ₛ⟧
  field
    apply         : Vector n → Vector m
    preserves-+   : (u v : Vector n) → apply (u +ⱽ v) ≡ apply u +ⱽ apply v
    preserves-*ₛ  : (c : F₂) (v : Vector n) → apply (c *ₛ v) ≡ c *ₛ apply v

open Linear public
