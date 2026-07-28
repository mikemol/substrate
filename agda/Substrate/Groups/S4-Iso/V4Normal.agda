------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.V4Normal
--
-- V₄-normal-compositional: V₄ ⊳ S₄ as iso-transport of the
-- compositional-side N-normal-in-SP.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.V4Normal where

import Substrate.Groups.V4.Operations as V4
open V4 using (V₄)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
open import Substrate.Groups.V4-Embedding using (embed; V₄-image)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.InverseCong Axis using (⁻¹-cong)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)

open import Substrate.Groups.S4-Iso.Embedding
  using (compositional-to-perm)
open import Substrate.Groups.S4-Iso.Extract
  using (perm-to-compositional)
open import Substrate.Groups.S4-Iso.ForwardHom using (forward-hom)
open import Substrate.Groups.S4-Iso.Roundtrip
  using (perm-roundtrip-≈; embed-as-N-injection)
open import Substrate.Groups.S4-Iso.IsoTransport
  using (forward-inv; compositional-to-perm-cong)
open import Substrate.Groups.V4.Bijection
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.EqSym Axis
open import Substrate.Groups.Symmetric.EqTrans Axis
open import Substrate.Groups.Symmetric.ComposeCong Axis
open import Substrate.Groups.Symmetric.EqRefl Axis

------------------------------------------------------------------------
-- V₄-normal-compositional.
------------------------------------------------------------------------

V₄-normal-compositional :
  (σ : Permutation) (v : V₄) → V₄-image ((σ · embed v) · (σ ⁻¹))
V₄-normal-compositional σ v =
  v' , conj-eq
  where
    σ̂ : S4C.Carrier
    σ̂ = perm-to-compositional σ

    v' : V₄
    v' = proj₁ (S4C.N-normal-in-SP σ̂ v)

    s4c-eq : (σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹)) S4C.≈ (v' , S₃.ε)
    s4c-eq = proj₂ (S4C.N-normal-in-SP σ̂ v)

    L  P-σ  P-v  P-σ⁻¹  P-σv  P-σvσ⁻¹  P-prod-inner  P-prod  P-result  R : Permutation
    L          = (σ · embed v) · (σ ⁻¹)
    P-σ        = compositional-to-perm σ̂
    P-v        = compositional-to-perm (v , S₃.ε)
    P-σ⁻¹      = compositional-to-perm (σ̂ S4C.⁻¹)
    P-σv       = P-σ · P-v
    P-σvσ⁻¹    = P-σv · P-σ⁻¹
    P-prod-inner = compositional-to-perm (σ̂ S4C.∙ (v , S₃.ε))
    P-prod       = compositional-to-perm (σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹))
    P-result     = compositional-to-perm (v' , S₃.ε)
    R            = embed v'

    σ≈P : σ ≈ P-σ
    σ≈P = ≈-sym {σ = P-σ} {τ = σ} (perm-roundtrip-≈ σ)

    v≈P : embed v ≈ P-v
    v≈P = embed-as-N-injection v

    σ⁻¹≈P : (σ ⁻¹) ≈ P-σ⁻¹
    σ⁻¹≈P = ≈-trans {σ = σ ⁻¹} {τ = (compositional-to-perm σ̂) ⁻¹} {ρ = P-σ⁻¹}
              (⁻¹-cong {σ = σ} {τ = compositional-to-perm σ̂} σ≈P)
              (≈-sym {σ = P-σ⁻¹} {τ = (compositional-to-perm σ̂) ⁻¹}
                      (forward-inv σ̂))

    eqE1 : L ≈ P-σvσ⁻¹
    eqE1 = ·-cong {σ₁ = σ · embed v} {σ₂ = P-σv}
                   {τ₁ = σ ⁻¹}        {τ₂ = P-σ⁻¹}
                   (·-cong {σ₁ = σ}       {σ₂ = P-σ}
                            {τ₁ = embed v} {τ₂ = P-v}
                            σ≈P v≈P)
                   σ⁻¹≈P

    eqE2-inner : P-σv ≈ P-prod-inner
    eqE2-inner = ≈-sym {σ = P-prod-inner} {τ = P-σv}
                        (forward-hom σ̂ (v , S₃.ε))

    eqE2 : P-σvσ⁻¹ ≈ P-prod
    eqE2 = ≈-trans {σ = P-σvσ⁻¹} {τ = P-prod-inner · P-σ⁻¹} {ρ = P-prod}
            (·-cong {σ₁ = P-σv} {σ₂ = P-prod-inner}
                     {τ₁ = P-σ⁻¹} {τ₂ = P-σ⁻¹}
                     eqE2-inner (≈-refl P-σ⁻¹))
            (≈-sym {σ = P-prod} {τ = P-prod-inner · P-σ⁻¹}
                    (forward-hom (σ̂ S4C.∙ (v , S₃.ε)) (σ̂ S4C.⁻¹)))

    eqE3 : P-prod ≈ P-result
    eqE3 = compositional-to-perm-cong
             {s₁ = σ̂ S4C.∙ (v , S₃.ε) S4C.∙ (σ̂ S4C.⁻¹)} {s₂ = v' , S₃.ε}
             s4c-eq

    eqE4 : P-result ≈ R
    eqE4 = ≈-sym {σ = R} {τ = P-result} (embed-as-N-injection v')

    conj-eq : L ≈ R
    conj-eq =
      ≈-trans {σ = L} {τ = P-σvσ⁻¹} {ρ = R} eqE1
        (≈-trans {σ = P-σvσ⁻¹} {τ = P-prod} {ρ = R} eqE2
          (≈-trans {σ = P-prod} {τ = P-result} {ρ = R} eqE3 eqE4))
