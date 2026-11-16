------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsoBraidOtimes
--
-- Defines: iso-braid⊗
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatSym; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsoBraidOtimes where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Vec.Properties.LookupComptabulate
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Surjective
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
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Iso
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.LeftInvToisperm
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsPermToIso
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IspermSubstInv



iso-braid⊗ : {i j : ℕ} (a : Objₚ i) (b : Objₚ j) → Iso (proj₂ (braid⊗ ob a b))
iso-braid⊗ a b =
  IsPerm→Iso (proj₂ (braid⊗ ob a b))
    (isperm-subst-inv (proj₁ (braid⊗ ob b a)) (proj₂ (braid⊗ ob a b))
      (left-inv→isperm
        (proj₂ (braid⊗ ob b a))
        (subst Perm (proj₁ (braid⊗ ob b a)) (proj₂ (braid⊗ ob a b)))
        (cong proj₂ (braid⊗-invol ob a b))))
