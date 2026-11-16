------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Assoc
--
-- Defines: assocᵣ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Assoc where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.CyclicGrounding
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstCompose
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Comp



assocᵣ : {i j k l : ℕ}
         (f : Homᵣ i j) (g : Homᵣ j k) (h : Homᵣ k l) →
         ((h ∘ᵣ g) ∘ᵣ f) ≡ (h ∘ᵣ (g ∘ᵣ f))
assocᵣ f g h =
  homEq (uipℕ _ _)
        (trans (compose-assoc σh (subst Perm ph σg) (subst Perm (trans pg ph) σf))
               (cong (compose σh) (sym eqInner)))
  where
    pf = proj₁ f ; σf = proj₂ f
    pg = proj₁ g ; σg = proj₂ g
    ph = proj₁ h ; σh = proj₂ h
    eqInner : subst Perm ph (compose σg (subst Perm pg σf))
              ≡ compose (subst Perm ph σg) (subst Perm (trans pg ph) σf)
    eqInner = trans (subst-compose ph σg (subst Perm pg σf))
                    (cong (compose (subst Perm ph σg)) (subst-fuse Perm pg ph σf))
