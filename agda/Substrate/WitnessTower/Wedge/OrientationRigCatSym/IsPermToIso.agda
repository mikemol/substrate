------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsPermToIso
--
-- Defines: IsPerm→Iso
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatSym; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsPermToIso where

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
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Iso
open import Substrate.Linguistic.RosettaTable.RosettaEntry



-- IsPerm ⇒ Iso: the inverse is "where does σ send something to y"
-- (perm-surjective), exactly SymBridge.to-Sym at the vector level.
IsPerm→Iso : {n : ℕ} (σ : Perm n) → IsPerm σ → Iso σ
IsPerm→Iso σ pf = τ , right , left
  where
    τ : Perm _
    τ = tabulate (λ y → proj₁ (perm-surjective σ pf y))
    right : compose σ τ ≡ id-perm _
    right = apply-injective (λ y →
      trans (apply-compose σ τ y)
      (trans (cong (lookup σ) (lookup∘tabulate _ y))
      (trans (proj₂ (perm-surjective σ pf y))
             (sym (apply-id y)))))
    left : compose τ σ ≡ id-perm _
    left = apply-injective (λ x →
      trans (apply-compose τ σ x)
      (trans (lookup∘tabulate _ (lookup σ x))
      (trans (pf _ _ (proj₂ (perm-surjective σ pf (lookup σ x))))
             (sym (apply-id x)))))
