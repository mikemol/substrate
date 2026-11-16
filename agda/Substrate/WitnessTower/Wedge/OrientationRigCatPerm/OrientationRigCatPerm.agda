------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.OrientationRigCatPerm
--
-- Defines: orientationRigCatPerm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.OrientationRigCatPerm where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Vec.Properties.LookupComptabulate
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.CyclicGrounding
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationSumComm
open import Substrate.WitnessTower.Wedge.OrientationProductComm
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom2
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Id
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Comp
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LeftId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.RightId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Assoc
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Oplusobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Otimesobj



------------------------------------------------------------------------
-- S4 — THE INSTANCE. The genuine symmetric rig category with permutation
-- morphisms, assembled from S1–S3. Green at `: GradedRigCat Objₚ Homₚ`.
------------------------------------------------------------------------

orientationRigCatPerm : GradedRigCat Objₚ Homₚ
orientationRigCatPerm = record
  { idHom        = λ {i} _ → idᵣ i
  ; _∘_          = λ g f → g ∘ᵣ f
  ; left-id      = λ f → left-idᵣ f
  ; right-id     = λ f → right-idᵣ f
  ; assoc        = λ f g h → assocᵣ f g h
  ; ⊕obj         = ⊕objₚ
  ; ⊗obj         = ⊗objₚ
  ; braid⊕       = λ {i} {j} _ _ → +ℕ-comm i j , B⊕.swPerm i j
  ; braid⊗       = λ {i} {j} _ _ → *-comm i j , B⊗.swPerm i j
  ; braid⊕-invol = λ {i} {j} _ _ → homEq (uipℕ _ _) (B⊕.swPerm-invol i j)
  ; braid⊗-invol = λ {i} {j} _ _ → homEq (uipℕ _ _) (B⊗.swPerm-invol i j)
  }
