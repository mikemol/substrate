------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Embedding
--
-- embed-S₃ : S₃ acting on Axis via the Axis ↔ V₄ bijection.
-- compositional-to-perm : S4-Composed.Carrier → Permutation (forward).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Embedding where

open import Substrate.Axes using (Axis; D; C; S; W; act-axis;
                                   v-of-axis; axis-of-v;
                                   axis-of-v-v-of-axis; v-of-axis-axis-of-v)
import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_)
open Permutation
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; sym-trans; cong-trans)

------------------------------------------------------------------------
-- Internal apply / inv-apply combinators for embed-S₃.
------------------------------------------------------------------------

private
  s3-apply : S₃.Carrier → Axis → Axis
  s3-apply s x = axis-of-v (φ.act s (v-of-axis x))

  s3-inv-apply : S₃.Carrier → Axis → Axis
  s3-inv-apply s x = axis-of-v (φ.act (s S₃.⁻¹) (v-of-axis x))

  -- φ.act-cong specialised to v-eq = refl.
  φ-cong-v : (s₁ s₂ : S₃.Carrier) (v : V₄) → s₁ S₃.≈ s₂ →
             φ.act s₁ v ≡ φ.act s₂ v
  φ-cong-v s₁ s₂ v eq = φ.act-cong {s₁ = s₁} {s₂ = s₂} {v₁ = v} {v₂ = v} eq refl

  s3-apply-inv-r : (s : S₃.Carrier) (x : Axis) →
                   s3-apply s (s3-inv-apply s x) ≡ x
  s3-apply-inv-r s x =
    cong-trans (λ y → axis-of-v (φ.act s y))
               (v-of-axis-axis-of-v (φ.act (s S₃.⁻¹) (v-of-axis x)))
    (sym-trans (cong axis-of-v (φ.act-∙ s (s S₃.⁻¹) (v-of-axis x)))
    (cong-trans axis-of-v (φ-cong-v (s S₃.∙ s S₃.⁻¹) S₃.ε (v-of-axis x) (S₃.inv-right s))
    (cong-trans axis-of-v (φ.act-ε (v-of-axis x))
           (axis-of-v-v-of-axis x))))

  s3-inv-apply-l : (s : S₃.Carrier) (x : Axis) →
                   s3-inv-apply s (s3-apply s x) ≡ x
  s3-inv-apply-l s x =
    cong-trans (λ y → axis-of-v (φ.act (s S₃.⁻¹) y))
               (v-of-axis-axis-of-v (φ.act s (v-of-axis x)))
    (sym-trans (cong axis-of-v (φ.act-∙ (s S₃.⁻¹) s (v-of-axis x)))
    (cong-trans axis-of-v (φ-cong-v (s S₃.⁻¹ S₃.∙ s) S₃.ε (v-of-axis x) (S₃.inv-left s))
    (cong-trans axis-of-v (φ.act-ε (v-of-axis x))
           (axis-of-v-v-of-axis x))))

------------------------------------------------------------------------
-- embed-S₃: S₃ → Permutation Axis.
------------------------------------------------------------------------

embed-S₃ : S₃.Carrier → Permutation
embed-S₃ s = record
  { apply = s3-apply s
  ; invₐ  = s3-inv-apply s
  ; inv-l = s3-inv-apply-l s
  ; inv-r = s3-apply-inv-r s
  }

------------------------------------------------------------------------
-- compositional-to-perm: forward direction of the iso.
------------------------------------------------------------------------

compositional-to-perm : S4C.Carrier → Permutation
compositional-to-perm (v , s) = embed v · embed-S₃ s
