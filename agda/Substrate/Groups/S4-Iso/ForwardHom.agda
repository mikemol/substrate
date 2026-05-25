------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.ForwardHom
--
-- compositional-to-perm is a Group homomorphism (forward-hom).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.ForwardHom where

open import Substrate.Axes
  using (Axis; act-axis; v-of-axis; axis-of-v; v-of-axis-axis-of-v)
import Substrate.Groups.V4 as V4
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Groups.V4-Embedding using (embed; act-axis-as-V₄-mult)
open import Substrate.Groups.S4 using (_·_; _≈_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong; trans-sym)

open import Substrate.Groups.S4-Iso.Foundation public

------------------------------------------------------------------------
-- forward-hom: pointwise homomorphism property.
------------------------------------------------------------------------

forward-hom : (s₁ s₂ : S4C.Carrier) →
              compositional-to-perm (s₁ S4C.∙ s₂) ≈
              (compositional-to-perm s₁ · compositional-to-perm s₂)
forward-hom (v₁ , sa) (v₂ , sb) x = trans-sym LHS-form RHS-form
  where
    open import Substrate.Groups.S4 using (Permutation)
    open Permutation

    Canon : Axis
    Canon = axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· φ.act (sa S₃.∙ sb) (v-of-axis x))

    LHS-form :
      apply (compositional-to-perm ((v₁ , sa) S4C.∙ (v₂ , sb))) x ≡ Canon
    LHS-form =
      trans (act-axis-as-V₄-mult (v₁ V4.· φ.act sa v₂)
                                  (axis-of-v (φ.act (sa S₃.∙ sb) (v-of-axis x))))
            (cong (λ y → axis-of-v ((v₁ V4.· φ.act sa v₂) V4.· y))
                  (v-of-axis-axis-of-v (φ.act (sa S₃.∙ sb) (v-of-axis x))))

    RHS-form :
      apply (compositional-to-perm (v₁ , sa) · compositional-to-perm (v₂ , sb)) x ≡ Canon
    RHS-form = begin
      act-axis v₁ (apply (embed-S₃ sa) (act-axis v₂ (apply (embed-S₃ sb) x)))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) y))
                 (act-axis-as-V₄-mult v₂ (apply (embed-S₃ sb) x)) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· v-of-axis (apply (embed-S₃ sb) x))))
        ≡⟨ cong (λ y → act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· y))))
                 (v-of-axis-axis-of-v (φ.act sb (v-of-axis x))) ⟩
      act-axis v₁ (apply (embed-S₃ sa) (axis-of-v (v₂ V4.· φ.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → act-axis v₁ (axis-of-v (φ.act sa y)))
                 (v-of-axis-axis-of-v (v₂ V4.· φ.act sb (v-of-axis x))) ⟩
      act-axis v₁ (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x))))
        ≡⟨ act-axis-as-V₄-mult v₁
             (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· v-of-axis (axis-of-v (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (v-of-axis-axis-of-v
                   (φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))) ⟩
      axis-of-v (v₁ V4.· φ.act sa (v₂ V4.· φ.act sb (v-of-axis x)))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· y))
                 (φ.act-hom sa v₂ (φ.act sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· φ.act sa (φ.act sb (v-of-axis x))))
        ≡⟨ cong (λ y → axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· y)))
                 (sym (φ.act-∙ sa sb (v-of-axis x))) ⟩
      axis-of-v (v₁ V4.· (φ.act sa v₂ V4.· φ.act (sa S₃.∙ sb) (v-of-axis x)))
        ≡⟨ cong axis-of-v
                 (sym (V4.·-assoc v₁ (φ.act sa v₂)
                                    (φ.act (sa S₃.∙ sb) (v-of-axis x)))) ⟩
      Canon
        ∎
      where
        open import Substrate.Foundation.Eq using (module ≡-Reasoning)
        open ≡-Reasoning
