------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps
--
-- V₄-homomorphism witnesses for the three swap-type canonical S₃
-- elements: swap αβ, swap αγ, swap βγ. 16 refl cases each.
-- Plus the act-hom-on-canonical dispatch + act-hom (full action).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Axes using (v4×v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.HomRotations public

------------------------------------------------------------------------
-- ([], [a]) — swap αβ.
------------------------------------------------------------------------

hom-swap-αβ : ∀ v₁ v₂ →
  act-on-canonical [] (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical [] (Z₂.a ∷ []) v₁ V4.· act-on-canonical [] (Z₂.a ∷ []) v₂
hom-swap-αβ = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- ([a], [a]) — swap αγ.
------------------------------------------------------------------------

hom-swap-αγ : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) v₁ V4.· act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) v₂
hom-swap-αγ = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- ([a,a], [a]) — swap βγ.
------------------------------------------------------------------------

hom-swap-βγ : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₁ V4.· act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₂
hom-swap-βγ = v4×v4-cover _
  ( (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  , (refl , refl , refl , refl)
  )

------------------------------------------------------------------------
-- Dispatch act-hom-on-canonical + lift to full action.
------------------------------------------------------------------------

act-hom-on-canonical :
  ∀ {n h} (c-n : Z₃.Canonical n) (c-h : Z₂.Canonical h) →
  ∀ v₁ v₂ →
  act-on-canonical n h (v₁ V4.· v₂) ≡
  act-on-canonical n h v₁ V4.· act-on-canonical n h v₂
act-hom-on-canonical Z₃.c-ε  Z₂.c-ε = hom-id
act-hom-on-canonical Z₃.c-a  Z₂.c-ε = hom-rot
act-hom-on-canonical Z₃.c-aa Z₂.c-ε = hom-rot²
act-hom-on-canonical Z₃.c-ε  Z₂.c-a = hom-swap-αβ
act-hom-on-canonical Z₃.c-a  Z₂.c-a = hom-swap-αγ
act-hom-on-canonical Z₃.c-aa Z₂.c-a = hom-swap-βγ

act-hom : ∀ s v₁ v₂ → act s (v₁ V4.· v₂) ≡ act s v₁ V4.· act s v₂
act-hom (n , h) =
  act-hom-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)
