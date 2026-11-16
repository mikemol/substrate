------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.EqFromLookupA
--
-- Defines: ≡-from-lookup-A
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.EqFromLookupA where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
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
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- Generic ≡-from-lookup for Vec of any element type.
--
-- The substrate's existing `≡-from-lookup` is specialised to
-- `Vector n = Vec F₂ n`. The proof body is structural and works for
-- any element type. Local helper here to avoid a stdlib dependency
-- on Data.Vec.Properties.
------------------------------------------------------------------------

≡-from-lookup-A :
  ∀ {ℓ} {A : Set ℓ} {n} (u v : Vec A n) →
  ((i : Fin n) → lookup u i ≡ lookup v i) →
  u ≡ v
≡-from-lookup-A []      []      _  = refl
≡-from-lookup-A (x ∷ u) (y ∷ v) eq =
  cong₂ _∷_ (eq zero) (≡-from-lookup-A u v (λ i → eq (suc i)))
