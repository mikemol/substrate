------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatSym.Comp
--
-- Defines: _∘ˢ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatSym; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatSym.Comp where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Vec.Properties.LookupComptabulate
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Surjective
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
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Iso
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsoToIsPerm
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsPermToIso
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IspermSubst
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Hom

infixr 9 _∘ˢ_

_∘ˢ_ : {i j k : ℕ} → Homˢ j k → Homˢ i j → Homˢ i k
g ∘ˢ f = h , IsPerm→Iso (proj₂ h) (compose-is-perm σg τf pg pf)
  where
    h  = proj₁ g ∘ᵣ proj₁ f
    σg = proj₂ (proj₁ g)
    τf = subst Perm (proj₁ (proj₁ g)) (proj₂ (proj₁ f))
    pg = Iso→IsPerm σg (proj₂ g)
    pf = isperm-subst (proj₁ (proj₁ g)) (proj₂ (proj₁ f))
                      (Iso→IsPerm (proj₂ (proj₁ f)) (proj₂ f))
