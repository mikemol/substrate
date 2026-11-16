------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.ReduceIdempotent
--
-- Defines: reduce-idempotent
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.ReduceIdempotent where

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
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Xtime
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Idempotent.ReduceEqHsum
open import Substrate.Algebra.F2.GF256.Idempotent.HsumOneId



-- A6: reducing an already-reduced byte is the identity.
reduce-idempotent : (p : Vector 8) → reduce-mod-m p ≡ p
reduce-idempotent p = trans (reduce-eq-hsum p) (hsum-𝟙₈-id p)
