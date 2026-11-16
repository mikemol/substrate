------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.HsumOneId
--
-- Defines: hsum-𝟙₈-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.HsumOneId where

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
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Xtime
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.GF256.Idempotent.One
open import Substrate.Algebra.F2.GF256.Idempotent.SumCong
open import Substrate.Algebra.F2.GF256.Idempotent.HsumIsSum
open import Substrate.Algebra.F2.GF256.Idempotent.HsumOneBasis



hsum-𝟙₈-id : (p : Vector 8) → hsum p one₈ ≡ p
hsum-𝟙₈-id p =
  trans (hsum-is-sum p one₈)
  (trans (sum-cong (λ i → cong (lookup p i *ₛ_) (hsum-one-basis i)))
         (sym (basis-decomp p)))
