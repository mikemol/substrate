------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3.ChiralityAxis
--
-- N-2 of M-11.dim3. The chirality-axis in F₂³ as a structural
-- F₂-linear subspace: the kernel of the "project V₄-coords" linear
-- map.
--
-- Structural identification:
--   chirality-axis = ⟨e₃⟩ = {w ∈ F₂³ : lookup w 0 ≡ 𝟘 ∧ lookup w 1 ≡ 𝟘}
--                = the 2-element 1-dim subspace {𝟎ⱽ, e₃}
--
-- Two views, with bridges:
--   * KernelCode form: chirality-axis = ker (ChiralityAxis-Selector : Linear 3 2)
--     where ChiralityAxis-Selector projects the two V₄-coordinate bits.
--   * Predicate form:  ChiralityAxis-Pred w = (lookup w 0 ≡ 𝟘) × (lookup w 1 ≡ 𝟘)
--
-- This is the Hodge dual of V4-Plane (N-1) in F₂³: the codim-2
-- subspace IS the chirality F₂ (per memory
-- `project_3plus1_parity_universal`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3.ChiralityAxis where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₂)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong-trans; sym-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Linear.KernelPredBridge
  using (pred-at-i→kernel-at-i; kernel-at-i→pred-at-i)
open import Substrate.Algebra.F2.Code

------------------------------------------------------------------------
-- Basis-images of the "project V₄-coords" linear map.
--
-- Maps F₂³'s 3 basis vectors to F₂²:
--   e₀ ↦ 𝟙 ∷ 𝟘 ∷ []   (first V₄ coord)
--   e₁ ↦ 𝟘 ∷ 𝟙 ∷ []   (second V₄ coord)
--   e₂ ↦ 𝟎ⱽ           (chirality bit doesn't contribute to V₄ coords)
------------------------------------------------------------------------

v4-coords-images : Fin 3 → Vector 2
v4-coords-images zero          = 𝟙 ∷ 𝟘 ∷ []
v4-coords-images (suc zero)    = 𝟘 ∷ 𝟙 ∷ []
v4-coords-images ₂ = 𝟎ⱽ

------------------------------------------------------------------------
-- The F₂-linear projection itself.
------------------------------------------------------------------------

ChiralityAxis-Selector : Linear 3 2
ChiralityAxis-Selector = linear-from-images v4-coords-images

------------------------------------------------------------------------
-- The chirality-axis as a KernelCode.
------------------------------------------------------------------------

ChiralityAxis : KernelCode 3 2
ChiralityAxis = record { parity-check = ChiralityAxis-Selector }

------------------------------------------------------------------------
-- Predicate form: both V₄-coordinate bits (indices 0, 1) are 𝟘.
------------------------------------------------------------------------

ChiralityAxis-Pred : Vector 3 → Set
ChiralityAxis-Pred w = (lookup w zero ≡ 𝟘) × (lookup w (suc zero) ≡ 𝟘)

------------------------------------------------------------------------
-- Application of ChiralityAxis-Selector reduces componentwise to
-- the first two bits of the input.
------------------------------------------------------------------------

apply-ChirAxis-Selector-lookup-0 :
  (v : Vector 3) →
  lookup (apply ChiralityAxis-Selector v) zero ≡ lookup v zero
apply-ChirAxis-Selector-lookup-0 (a ∷ b ∷ c ∷ []) =
  -- opaque `linear-from-images` → reach the dense sum via its characterising
  -- lemma: a · 𝟙 + (b · 𝟘 + (c · 𝟘 + 𝟘)), which collapses to a.
  trans (apply-linear-from-images-lookup v4-coords-images (a ∷ b ∷ c ∷ []) zero)
  (cong-trans (_+ (b · 𝟘 + (c · 𝟘 + 𝟘))) (·-identityʳ a)
  (cong-trans (a +_) (cong (_+ (c · 𝟘 + 𝟘)) (·-absorbʳ b))
  (cong-trans (a +_) (+-identityˡ _)
  (cong-trans (a +_) (cong (_+ 𝟘) (·-absorbʳ c))
  (cong-trans (a +_) (+-identityˡ _)
         (+-identityʳ a))))))

apply-ChirAxis-Selector-lookup-1 :
  (v : Vector 3) →
  lookup (apply ChiralityAxis-Selector v) (suc zero) ≡ lookup v (suc zero)
apply-ChirAxis-Selector-lookup-1 (a ∷ b ∷ c ∷ []) =
  -- opaque `linear-from-images` → reach the dense sum via its characterising
  -- lemma: a · 𝟘 + (b · 𝟙 + (c · 𝟘 + 𝟘)), which collapses to b.
  trans (apply-linear-from-images-lookup v4-coords-images (a ∷ b ∷ c ∷ []) (suc zero))
  (cong-trans (_+ (b · 𝟙 + (c · 𝟘 + 𝟘))) (·-absorbʳ a)
  (trans (+-identityˡ _)
  (cong-trans (_+ (c · 𝟘 + 𝟘)) (·-identityʳ b)
  (cong-trans (b +_) (cong (_+ 𝟘) (·-absorbʳ c))
  (cong-trans (b +_) (+-identityˡ _)
         (+-identityʳ b))))))

------------------------------------------------------------------------
-- Bridges between KernelCode membership and predicate form.
------------------------------------------------------------------------

pred→kernel : (w : Vector 3) → ChiralityAxis-Pred w → In-Kernel ChiralityAxis w
pred→kernel w (p0 , p1) = ≡-from-lookup _ _ goal
  where
    S = ChiralityAxis-Selector
    goal : (j : Fin 2) →
           lookup (apply S w) j ≡ lookup (𝟎ⱽ {2}) j
    goal zero       = pred-at-i→kernel-at-i S w zero       (apply-ChirAxis-Selector-lookup-0 w) p0
    goal (suc zero) = pred-at-i→kernel-at-i S w (suc zero) (apply-ChirAxis-Selector-lookup-1 w) p1

kernel→pred : (w : Vector 3) → In-Kernel ChiralityAxis w → ChiralityAxis-Pred w
kernel→pred w ker =
  kernel-at-i→pred-at-i ChiralityAxis-Selector w zero       (apply-ChirAxis-Selector-lookup-0 w) ker ,
  kernel-at-i→pred-at-i ChiralityAxis-Selector w (suc zero) (apply-ChirAxis-Selector-lookup-1 w) ker
