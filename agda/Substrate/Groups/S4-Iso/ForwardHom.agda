------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.ForwardHom
--
-- compositional-to-perm is a Group homomorphism (forward-hom).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.ForwardHom where

open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)
open import Substrate.Axes.V4Roundtrip using (v-of-axis-axis-of-v)
open import Substrate.Axes.ActAxis using (act-axis)
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act as φ-Act
import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot as φ-ActDot
import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom as φ-ActHom
open import Substrate.Groups.V4-Embedding using (embed; act-axis-as-V₄-mult)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong; trans-sym)

open import Substrate.Groups.S4-Iso.Foundation
open import Substrate.Groups.S4-Iso.Embedding
------------------------------------------------------------------------
-- forward-hom: pointwise homomorphism property.
------------------------------------------------------------------------

forward-hom : (s₁ s₂ : S4C.Carrier) →
              compositional-to-perm (s₁ S4C.∙ s₂) ≈
              (compositional-to-perm s₁ · compositional-to-perm s₂)
forward-hom (v₁ , sa) (v₂ , sb) x = trans-sym LHS-form RHS-form
  where
    open import Substrate.Groups.S4 using (Permutation)

    Canon : Axis
    Canon = axis-of-v ((v₁ V4.· φ-Act.act sa v₂) V4.· φ-Act.act (sa S₃.∙ sb) (v-of-axis x))

    LHS-form :
      apply (compositional-to-perm ((v₁ , sa) S4C.∙ (v₂ , sb))) x ≡ Canon
    LHS-form =
      trans (act-axis-as-V₄-mult (v₁ V4.· φ-Act.act sa v₂)
                                  (axis-of-v (φ-Act.act (sa S₃.∙ sb) (v-of-axis x))))
            (cong (λ y → axis-of-v ((v₁ V4.· φ-Act.act sa v₂) V4.· y))
                  (v-of-axis-axis-of-v (φ-Act.act (sa S₃.∙ sb) (v-of-axis x))))

    RHS-form :
      apply (compositional-to-perm (v₁ , sa) · compositional-to-perm (v₂ , sb)) x ≡ Canon
    RHS-form = begin
      act-axis v₁ (apply (embed-S₃ sa) (act-axis v₂ (apply (embed-S₃ sb) x)))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) y))
                 (act-axis-as-V₄-mult v₂ (apply (embed-S₃ sb) x)) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· v-of-axis (apply (embed-S₃ sb) x))))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· y))))
                 (v-of-axis-axis-of-v (φ-Act.act sb (v-of-axis x))) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· φ-Act.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → act-axis v₁ (axis-of-v (φ-Act.act sa y)))
                 (v-of-axis-axis-of-v (v₂ V4.· φ-Act.act sb (v-of-axis x))) ⟩
      act-axis v₁ (axis-of-v (φ-Act.act sa (v₂ V4.· φ-Act.act sb (v-of-axis x))))
        ≡⟨ act-axis-as-V₄-mult v₁
             (axis-of-v (φ-Act.act sa (v₂ V4.· φ-Act.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· v-of-axis (axis-of-v (φ-Act.act sa (v₂ V4.· φ-Act.act sb (v-of-axis x)))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (v-of-axis-axis-of-v
                   (φ-Act.act sa (v₂ V4.· φ-Act.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· φ-Act.act sa (v₂ V4.· φ-Act.act sb (v-of-axis x)))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (φ-ActHom.act-hom sa v₂ (φ-Act.act sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ-Act.act sa v₂ V4.· φ-Act.act sa (φ-Act.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· (φ-Act.act sa v₂ V4.· y)))
                 (sym (φ-ActDot.act-∙ sa sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ-Act.act sa v₂ V4.· φ-Act.act (sa S₃.∙ sb) (v-of-axis x)))
        ≡⟨ cong axis-of-v
                 (sym (·-assoc v₁ (φ-Act.act sa v₂)
                                    (φ-Act.act (sa S₃.∙ sb) (v-of-axis x)))) ⟩
      Canon
        ∎
      where
        open import Substrate.Foundation.Eq using (module ≡-Reasoning)
        open ≡-Reasoning
