------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.IdL
--
-- Defines: id-L
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.IdL where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Function
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
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- Identity linear map.
------------------------------------------------------------------------

id-L : ∀ {n} → Linear n n
id-L = record
  { apply        = id
  ; preserves-+  = λ _ _ → refl
  ; preserves-*ₛ = λ _ _ → refl
  }

------------------------------------------------------------------------
-- Composition: linear-map composition.
--
-- (L ∘L M) sends v to L (M v); inherits linearity from both factors.
-- Convention: L ∘L M is "M then L" (matches function composition).
------------------------------------------------------------------------
