------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatSym.OrientationRigCatSym
--
-- Defines: orientationRigCatSym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatSym; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatSym.OrientationRigCatSym where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Product
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Assoc
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Comp
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom2
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Id
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LeftId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LookupSubst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Oplusobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.OrientationRigCatPerm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Otimesobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.RightId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstCompose
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFinUip
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstIdperm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstSymL
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.SubstConst
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Hom2
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.HomEq
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Id
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Comp
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.LeftId
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.RightId
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Assoc
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.BraidOplus
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.BraidOtimes
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Oplusobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Otimesobj



------------------------------------------------------------------------
-- S7 — THE INSTANCE. The genuine symmetric (Sₙ-morphism) rig category.
-- Green at `: GradedRigCat Objₚ Homˢᵒ`.
------------------------------------------------------------------------

orientationRigCatSym : GradedRigCat Objₚ Homˢᵒ
orientationRigCatSym = record
  { idHom        = λ {i} _ → idˢ i
  ; _∘_          = λ g f → g ∘ˢ f
  ; left-id      = λ f → left-idˢ f
  ; right-id     = λ f → right-idˢ f
  ; assoc        = λ f g h → assocˢ f g h
  ; ⊕obj         = ⊕objₛ
  ; ⊗obj         = ⊗objₛ
  ; braid⊕       = λ a b → braidˢ⊕ a b
  ; braid⊗       = λ a b → braidˢ⊗ a b
  ; braid⊕-invol = λ a b → homEqˢ (braid⊕-invol ob a b)
  ; braid⊗-invol = λ a b → homEqˢ (braid⊗-invol ob a b)
  }
