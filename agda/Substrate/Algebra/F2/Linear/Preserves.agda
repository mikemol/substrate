------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Preserves
--
-- Defines: preserves-𝟎
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Preserves where

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
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- Derived: every linear map sends 𝟎ⱽ to 𝟎ⱽ.
--
-- Proof: 𝟎ⱽ ≡ 𝟘 *ₛ 𝟎ⱽ by absorption; apply respects *ₛ; 𝟘 *ₛ x ≡ 𝟎ⱽ.
------------------------------------------------------------------------

preserves-𝟎 : ∀ {n m} (L : Linear n m) → apply L 𝟎ⱽ ≡ 𝟎ⱽ
preserves-𝟎 L =
  trans (cong (apply L) (sym (*ₛ-absorbˡ 𝟎ⱽ)))
        (trans (preserves-*ₛ L 𝟘 𝟎ⱽ)
               (*ₛ-absorbˡ (apply L 𝟎ⱽ)))
