------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Foundation
--
-- Foundation lemmas for forward-hom + V₄-normal transport:
--   embed-S₃-ε    — embed-S₃ ε_S₃ ≈ ε_perm.
--   embed-S₃-hom  — embed-S₃ (s₁ ∙ s₂) ≈ embed-S₃ s₁ · embed-S₃ s₂.
--   swap-relation — embed-S₃ s · embed v ≈ embed (φ.act s v) · embed-S₃ s.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Foundation where

open import Substrate.Axes
  using (Axis; v-of-axis; axis-of-v; v-of-axis-axis-of-v; axis-of-v-v-of-axis)
import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.S4
  using (Permutation; _·_)
open Permutation
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)

open import Substrate.Groups.S4-Iso.Embedding public

------------------------------------------------------------------------
-- embed-S₃ of S₃'s identity is the identity permutation (pointwise).
------------------------------------------------------------------------

embed-S₃-ε : (x : Axis) → apply (embed-S₃ S₃.ε) x ≡ x
embed-S₃-ε x =
  trans (cong axis-of-v (φ.act-ε (v-of-axis x)))
        (axis-of-v-v-of-axis x)

------------------------------------------------------------------------
-- embed-S₃ is a Group homomorphism (pointwise).
------------------------------------------------------------------------

embed-S₃-hom : (s₁ s₂ : S₃.Carrier) →
               (x : Axis) →
               apply (embed-S₃ (s₁ S₃.∙ s₂)) x ≡
               apply (embed-S₃ s₁ · embed-S₃ s₂) x
embed-S₃-hom s₁ s₂ x =
  trans (cong axis-of-v (φ.act-∙ s₁ s₂ (v-of-axis x)))
        (cong (λ y → axis-of-v (φ.act s₁ y))
              (sym (v-of-axis-axis-of-v (φ.act s₂ (v-of-axis x)))))

------------------------------------------------------------------------
-- The defining "S₃ conjugates V₄" relation at the Permutation level.
------------------------------------------------------------------------

swap-relation : (s : S₃.Carrier) (v : V₄) →
                (x : Axis) →
                apply (embed-S₃ s · embed v) x ≡
                apply (embed (φ.act s v) · embed-S₃ s) x
swap-relation s v x = trans LHS-to-canonical (sym RHS-to-canonical)
  where
    open import Substrate.Groups.V4-Embedding using (act-axis-as-V₄-mult)
    LHS-to-canonical :
      apply (embed-S₃ s · embed v) x ≡
      axis-of-v (φ.act s v V4.· φ.act s (v-of-axis x))
    LHS-to-canonical =
      trans (cong (λ y → axis-of-v (φ.act s (v-of-axis y)))
                  (act-axis-as-V₄-mult v x))
      (trans (cong (λ y → axis-of-v (φ.act s y))
                   (v-of-axis-axis-of-v (v V4.· v-of-axis x)))
             (cong axis-of-v (φ.act-hom s v (v-of-axis x))))
    RHS-to-canonical :
      apply (embed (φ.act s v) · embed-S₃ s) x ≡
      axis-of-v (φ.act s v V4.· φ.act s (v-of-axis x))
    RHS-to-canonical =
      trans (act-axis-as-V₄-mult (φ.act s v)
                                  (axis-of-v (φ.act s (v-of-axis x))))
            (cong (λ y → axis-of-v (φ.act s v V4.· y))
                  (v-of-axis-axis-of-v (φ.act s (v-of-axis x))))
