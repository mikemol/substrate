------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.ImagesProps  (Ⓑ′)
--
-- Base-level properties of `linear-from-images` in its IMAGE argument:
-- congruence, additivity, and scaling of `apply (linear-from-images g) u`
-- as g varies — plus the scalar sum-F₂ distributivity helpers they need.
--
-- These are NOT bilinear-specific; they are generic linear-from-images
-- facts. They were first needed (and lived) in BilinearFromImages, which
-- made the GENERIC MultilinearFromImages import the SPECIAL BilinearFromImages
-- (an inverted dependency). Factored here as their proper base layer so BOTH
-- the bilinear (n=2) and multilinear (generic) existence constructions build
-- on this base — and BilinearFromImages can then import the generic
-- MultilinearFromImages (special = instance of generic, the right direction).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.ImagesProps where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin)
  renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-lookup)
open import Substrate.Algebra.Medial using (medial)

------------------------------------------------------------------------
-- sum-F₂ additivity / scaling.
--
-- Neither already exists (Vector.Universal has only sum-F₂ + sum-F₂-cong
-- and the vector-valued sum-+ⱽ-distrib / *ₛ-sum-distrib). They are the
-- scalar analogues, proved here by induction on the index count.
------------------------------------------------------------------------

-- sum-F₂ (λ i → a i + b i) ≡ sum-F₂ a + sum-F₂ b.
sum-F₂-+-distrib :
  ∀ {n} (a b : Fin n → F₂) →
  sum-F₂ (λ i → a i + b i) ≡ (sum-F₂ a + sum-F₂ b)
sum-F₂-+-distrib {zero}  a b = refl
sum-F₂-+-distrib {suc _} a b =
  -- (a₀ + b₀) + Σ(aᵢ + bᵢ) ≡ (a₀ + Σaᵢ) + (b₀ + Σbᵢ)
  cong-trans ((a fz + b fz) +_) (sum-F₂-+-distrib (a ∘ fs) (b ∘ fs))
  (swap-+ (a fz) (b fz) (sum-F₂ (a ∘ fs)) (sum-F₂ (b ∘ fs)))
  where
    -- Ⓜ: the 4-term rearrange = the medial law (Algebra.Medial) at F₂'s `+`.
    swap-+ : (w x y z : F₂) → ((w + x) + (y + z)) ≡ ((w + y) + (x + z))
    swap-+ = medial _+_ +-assoc +-comm

-- sum-F₂ (λ i → c · a i) ≡ c · sum-F₂ a.
sum-F₂-·-distrib :
  ∀ {n} (c : F₂) (a : Fin n → F₂) →
  sum-F₂ (λ i → c · a i) ≡ (c · sum-F₂ a)
sum-F₂-·-distrib {zero}  c a = sym (·-absorbʳ c)
sum-F₂-·-distrib {suc _} c a =
  trans (cong (c · a fz +_) (sum-F₂-·-distrib c (a ∘ fs)))
        (sym (·-distribˡ-+ c (a fz) (sum-F₂ (a ∘ fs))))

------------------------------------------------------------------------
-- apply-congruence in the images family.
--
-- If two image families agree pointwise, the arity-1 maps they generate
-- agree on every input. Proved through the equational interface
-- (apply-linear-from-images-lookup + sum-F₂-cong), NOT by unfolding the
-- sealed `apply`.
------------------------------------------------------------------------

images-cong :
  ∀ {k n} {g h : Fin k → Vector n} → (∀ i → g i ≡ h i) →
  (u : Vector k) →
  apply (linear-from-images g) u ≡ apply (linear-from-images h) u
images-cong {g = g} {h = h} eq u = ≡-from-lookup _ _ (λ j →
  trans (apply-linear-from-images-lookup g u j)
  (trans (sum-F₂-cong (λ i → cong (λ w → lookup u i · lookup w j) (eq i)))
         (sym (apply-linear-from-images-lookup h u j))))

------------------------------------------------------------------------
-- images-additivity / images-scaling: the arity-1 map is additive /
-- scalar-homogeneous in its IMAGES argument (this is the "right" leg's
-- workhorse — the outer layer must push a combination of inner images
-- through).
------------------------------------------------------------------------

-- apply (lfi (λ i → g i +ⱽ h i)) u ≡ apply (lfi g) u +ⱽ apply (lfi h) u.
images-add :
  ∀ {k n} (g h : Fin k → Vector n) (u : Vector k) →
  apply (linear-from-images (λ i → g i +ⱽ h i)) u ≡
  (apply (linear-from-images g) u +ⱽ apply (linear-from-images h) u)
images-add g h u = ≡-from-lookup _ _ (λ j →
  trans (apply-linear-from-images-lookup (λ i → g i +ⱽ h i) u j)
  (trans (sum-F₂-cong (λ i →
            cong-trans (lookup u i ·_) (lookup-+ⱽ (g i) (h i) j)
                       (·-distribˡ-+ (lookup u i) (lookup (g i) j) (lookup (h i) j))))
  (trans (sum-F₂-+-distrib (λ i → lookup u i · lookup (g i) j)
                           (λ i → lookup u i · lookup (h i) j))
         (sym (trans (lookup-+ⱽ (apply (linear-from-images g) u)
                                (apply (linear-from-images h) u) j)
                     (cong₂ _+_ (apply-linear-from-images-lookup g u j)
                                (apply-linear-from-images-lookup h u j)))))))

-- apply (lfi (λ i → c *ₛ g i)) u ≡ c *ₛ apply (lfi g) u.
images-scale :
  ∀ {k n} (c : F₂) (g : Fin k → Vector n) (u : Vector k) →
  apply (linear-from-images (λ i → c *ₛ g i)) u ≡
  (c *ₛ apply (linear-from-images g) u)
images-scale c g u = ≡-from-lookup _ _ (λ j →
  trans (apply-linear-from-images-lookup (λ i → c *ₛ g i) u j)
  (trans (sum-F₂-cong (λ i →
            cong-trans (lookup u i ·_) (lookup-*ₛ c (g i) j)
            (trans (sym (·-assoc (lookup u i) c (lookup (g i) j)))
            (cong-trans (_· lookup (g i) j) (·-comm (lookup u i) c)
                        (·-assoc c (lookup u i) (lookup (g i) j))))))
  (trans (sum-F₂-·-distrib c (λ i → lookup u i · lookup (g i) j))
         (trans (cong (c ·_) (sym (apply-linear-from-images-lookup g u j)))
                (sym (lookup-*ₛ c (apply (linear-from-images g) u) j))))))
