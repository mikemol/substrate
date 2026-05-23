------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3.V4Plane
--
-- N-1 of M-11.dim3. The V₄-plane in F₂³ as a structural F₂-linear
-- subspace: the kernel of the "project chirality bit" linear map.
--
-- Structural identification:
--   V₄-plane = ⟨e₁, e₂⟩ = {v ∈ F₂³ : lookup v 2 ≡ 𝟘}
--           = the 4-element 2-dim subspace {𝟎ⱽ, e₁, e₂, e₁+e₂}
--
-- Two views, with a bridge between them:
--   * KernelCode form: V₄-plane = ker (V4Plane-Selector : Linear 3 1)
--     where V4Plane-Selector projects to the chirality bit.
--   * Predicate form:  V₄-plane-Pred v = lookup v ₂ ≡ 𝟘
--     (direct bit constraint; easier for computational arguments).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3.V4Plane where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₄)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Code

------------------------------------------------------------------------
-- Basis-images of the "project chirality bit" linear map.
--
-- Maps F₂³'s 3 basis vectors to F₂¹:
--   e₀ ↦ 𝟎ⱽ        (V₄ bit 0 doesn't contribute to chirality)
--   e₁ ↦ 𝟎ⱽ        (V₄ bit 1 doesn't contribute)
--   e₂ ↦ 𝟙 ∷ []   (chirality bit is the output)
------------------------------------------------------------------------

chirality-bit-images : Fin 3 → Vector 1
chirality-bit-images zero          = 𝟎ⱽ
chirality-bit-images (suc zero)    = 𝟎ⱽ
chirality-bit-images (suc (suc _)) = 𝟙 ∷ []

------------------------------------------------------------------------
-- The F₂-linear projection itself.
------------------------------------------------------------------------

V4Plane-Selector : Linear 3 1
V4Plane-Selector = linear-from-images chirality-bit-images

------------------------------------------------------------------------
-- The V₄-plane as a KernelCode: membership = kernel of the selector.
------------------------------------------------------------------------

V4-Plane : KernelCode 3 1
V4-Plane = record { parity-check = V4Plane-Selector }

------------------------------------------------------------------------
-- Predicate form: direct bit-constraint.
--
-- A vector v ∈ V₄-plane iff its chirality bit (index 2) is 𝟘.
------------------------------------------------------------------------

V4-Plane-Pred : Vector 3 → Set
V4-Plane-Pred v = lookup v ₂ ≡ 𝟘

------------------------------------------------------------------------
-- Application of V4Plane-Selector reduces to the chirality bit.
--
-- The key computational fact: apply V4Plane-Selector v ≡ lookup v 2 ∷ [].
-- Proved by ≡-from-lookup + lookup-sum + componentwise reduction.
------------------------------------------------------------------------

apply-V4Plane-Selector-lookup :
  (v : Vector 3) →
  lookup (apply V4Plane-Selector v) zero ≡ lookup v ₂
apply-V4Plane-Selector-lookup (a ∷ b ∷ c ∷ []) =
  -- LHS unfolds to: a · 𝟘 + (b · 𝟘 + (c · 𝟙 + 𝟘))
  -- Chain: simplify each summand, then collapse identities to c.
  trans (cong (_+ (b · 𝟘 + (c · 𝟙 + 𝟘))) (·-absorbʳ a))
  (trans (+-identityˡ _)
  (trans (cong (_+ (c · 𝟙 + 𝟘)) (·-absorbʳ b))
  (trans (+-identityˡ _)
  (trans (cong (_+ 𝟘) (·-identityʳ c))
         (+-identityʳ c)))))

------------------------------------------------------------------------
-- Bridges between KernelCode membership and predicate form.
------------------------------------------------------------------------

pred→kernel : (v : Vector 3) → V4-Plane-Pred v → In-Kernel V4-Plane v
pred→kernel v pred = ≡-from-lookup _ _ goal
  where
    goal : (j : Fin 1) →
           lookup (apply V4Plane-Selector v) j ≡ lookup (𝟎ⱽ {1}) j
    goal zero = trans (apply-V4Plane-Selector-lookup v)
                      (trans pred (sym (lookup-𝟎 {1} zero)))

kernel→pred : (v : Vector 3) → In-Kernel V4-Plane v → V4-Plane-Pred v
kernel→pred v ker =
  trans (sym (apply-V4Plane-Selector-lookup v))
        (trans (cong (λ w → lookup w zero) ker) (lookup-𝟎 {1} zero))
