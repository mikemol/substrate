------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Foundation
--
-- Foundation lemmas for forward-hom + V₄-normal transport:
--   embed-S₃-ε    — embed-S₃ ε_S₃ ≈ ε_perm.
--   embed-S₃-hom  — embed-S₃ (s₁ ∙ s₂) ≈ embed-S₃ s₁ · embed-S₃ s₂.
--   swap-relation — embed-S₃ s · embed v ≈ embed (φ-Act.act s v) · embed-S₃ s.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Foundation where

open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)
open import Substrate.Axes.AxisRoundtrip using (axis-of-v-v-of-axis)
open import Substrate.Axes.V4Roundtrip using (v-of-axis-axis-of-v)
import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act as φ-Act
import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot as φ-ActDot
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon as φ-ActEpsilon
import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom as φ-ActHom
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong; cong-trans)

open import Substrate.Groups.S4-Iso.Embedding

------------------------------------------------------------------------
-- embed-S₃ of S₃'s identity is the identity permutation (pointwise).
------------------------------------------------------------------------

embed-S₃-ε : (x : Axis) → apply (embed-S₃ S₃.ε) x ≡ x
embed-S₃-ε x =
  cong-trans axis-of-v (φ-ActEpsilon.act-ε (v-of-axis x))
             (axis-of-v-v-of-axis x)

------------------------------------------------------------------------
-- embed-S₃ is a Group homomorphism (pointwise).
------------------------------------------------------------------------

embed-S₃-hom : (s₁ s₂ : S₃.Carrier) →
               (x : Axis) →
               apply (embed-S₃ (s₁ S₃.∙ s₂)) x ≡
               apply (embed-S₃ s₁ · embed-S₃ s₂) x
embed-S₃-hom s₁ s₂ x =
  cong-trans axis-of-v (φ-ActDot.act-∙ s₁ s₂ (v-of-axis x))
             (cong (λ y → axis-of-v (φ-Act.act s₁ y))
                   (sym (v-of-axis-axis-of-v (φ-Act.act s₂ (v-of-axis x)))))

------------------------------------------------------------------------
-- The defining "S₃ conjugates V₄" relation at the Permutation level.
------------------------------------------------------------------------

swap-relation : (s : S₃.Carrier) (v : V₄) →
                (x : Axis) →
                apply (embed-S₃ s · embed v) x ≡
                apply (embed (φ-Act.act s v) · embed-S₃ s) x
swap-relation s v x = trans LHS-to-canonical (sym RHS-to-canonical)
  where
    open import Substrate.Groups.V4-Embedding using (act-axis-as-V₄-mult)
    LHS-to-canonical :
      apply (embed-S₃ s · embed v) x ≡
      axis-of-v (φ-Act.act s v V4.· φ-Act.act s (v-of-axis x))
    LHS-to-canonical =
      cong-trans (λ y → axis-of-v (φ-Act.act s (v-of-axis y)))
                 (act-axis-as-V₄-mult v x)
      (cong-trans (λ y → axis-of-v (φ-Act.act s y))
                  (v-of-axis-axis-of-v (v V4.· v-of-axis x))
                  (cong axis-of-v (φ-ActHom.act-hom s v (v-of-axis x))))
    RHS-to-canonical :
      apply (embed (φ-Act.act s v) · embed-S₃ s) x ≡
      axis-of-v (φ-Act.act s v V4.· φ-Act.act s (v-of-axis x))
    RHS-to-canonical =
      trans (act-axis-as-V₄-mult (φ-Act.act s v)
                                  (axis-of-v (φ-Act.act s (v-of-axis x))))
            (cong (λ y → axis-of-v (φ-Act.act s v V4.· y))
                  (v-of-axis-axis-of-v (φ-Act.act s (v-of-axis x))))
