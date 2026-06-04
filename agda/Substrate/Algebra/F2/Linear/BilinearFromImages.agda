------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.BilinearFromImages
--
-- FreeLinearization at ARITY 2 = the bilinear SPPF as its universal
-- property. Sibling of Substrate.Algebra.F2.Linear.FromImages (the
-- arity-1 free-linearization combinator); this module both constructs
-- and proves, mirroring FromImages (NOT a *.Properties split).
--
-- Given a k×l table of basis-pair images
--     f : Fin k → Fin l → Vector n
-- the construction produces the unique bilinear map sending the basis
-- PAIR (eᵢ, eⱼ) to f i j. The construction is a nested application of
-- the arity-1 combinator:
--
--     apply₂ f u v
--       = apply (linear-from-images (λ i → apply (linear-from-images (f i)) v)) u
--
-- THE UNIVERSAL PROPERTY (witness-once table lookup): applying the
-- arity-1 basis lemma TWICE collapses apply₂ f (basis i) (basis j) to
-- the stored table entry f i j. The k×l basis-pair table is the
-- shared-packed witness (witness-once); bilinearity is the no-recompute
-- extension; bilinear-from-images-basis is the table lookup = the UP.
--
-- The categorical name is Day convolution over the (ℕ, ×) grading: the
-- arity-2 free linear map is the Day-convolution tensor of two arity-1
-- free linear maps. Construction = name (the free-construction
-- principle): naming the table-with-bilinear-extension IS the
-- construction.
--
-- (Framing above is prose. What the Agda BELOW establishes is exactly
-- the four bilinearity laws + the basis collapse, no more.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.BilinearFromImages where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin)
  renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂; cong-trans; sym-trans; trans-sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using ( linear-from-images
        ; apply-linear-from-images-lookup
        ; apply-linear-from-images-basis )

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
    -- (w + x) + (y + z) ≡ (w + y) + (x + z), via F₂ assoc/comm.
    swap-+ : (w x y z : F₂) → ((w + x) + (y + z)) ≡ ((w + y) + (x + z))
    swap-+ w x y z =
      trans (+-assoc w x (y + z))
      (cong-trans (w +_) (sym (+-assoc x y z))
      (cong-trans (λ t → w + (t + z)) (+-comm x y)
      (cong-trans (w +_) (+-assoc y x z)
      (sym (+-assoc w y (x + z))))))

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

------------------------------------------------------------------------
-- The arity-2 construction.
------------------------------------------------------------------------

apply₂ : ∀ {k l n} → (Fin k → Fin l → Vector n) → Vector k → Vector l → Vector n
apply₂ f u v =
  apply (linear-from-images (λ i → apply (linear-from-images (f i)) v)) u

------------------------------------------------------------------------
-- THE UNIVERSAL PROPERTY: apply₂ f (basis i) (basis j) ≡ f i j.
--
-- The table lookup, obtained by applying the arity-1 basis lemma twice.
------------------------------------------------------------------------

bilinear-from-images-basis :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (i : Fin k) (j : Fin l) →
  apply₂ f (basis i) (basis j) ≡ f i j
bilinear-from-images-basis f i j =
  trans (apply-linear-from-images-basis
           (λ i' → apply (linear-from-images (f i')) (basis j)) i)
        (apply-linear-from-images-basis (f i) j)

------------------------------------------------------------------------
-- Bilinearity — all four laws, both chirality legs.
--
-- LEFT (free, inherited directly from the outer arity-1 Linear).
------------------------------------------------------------------------

bilinear-+ₗ :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (u u' : Vector k) (v : Vector l) →
  apply₂ f (u +ⱽ u') v ≡ (apply₂ f u v +ⱽ apply₂ f u' v)
bilinear-+ₗ f u u' v =
  preserves-+ (linear-from-images (λ i → apply (linear-from-images (f i)) v)) u u'

bilinear-*ₛₗ :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (c : F₂) (u : Vector k) (v : Vector l) →
  apply₂ f (c *ₛ u) v ≡ (c *ₛ apply₂ f u v)
bilinear-*ₛₗ f c u v =
  preserves-*ₛ (linear-from-images (λ i → apply (linear-from-images (f i)) v)) c u

------------------------------------------------------------------------
-- RIGHT (needs images-add / images-scale to push the inner-Linear
-- combination through the outer layer).
--
-- The inner images depend on the right argument; each inner
-- `linear-from-images (f i)` is itself linear, so it splits the right
-- argument. images-cong rewrites the outer images family pointwise; then
-- images-add / images-scale push the combination out through the outer
-- arity-1 map.
------------------------------------------------------------------------

bilinear-+ᵣ :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (u : Vector k) (v v' : Vector l) →
  apply₂ f u (v +ⱽ v') ≡ (apply₂ f u v +ⱽ apply₂ f u v')
bilinear-+ᵣ f u v v' =
  trans (images-cong
           (λ i → preserves-+ (linear-from-images (f i)) v v') u)
        (images-add (λ i → apply (linear-from-images (f i)) v)
                    (λ i → apply (linear-from-images (f i)) v') u)

bilinear-*ₛᵣ :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (c : F₂) (u : Vector k) (v : Vector l) →
  apply₂ f u (c *ₛ v) ≡ (c *ₛ apply₂ f u v)
bilinear-*ₛᵣ f c u v =
  trans (images-cong
           (λ i → preserves-*ₛ (linear-from-images (f i)) c v) u)
        (images-scale c (λ i → apply (linear-from-images (f i)) v) u)

------------------------------------------------------------------------
-- Package: a record mirroring Linear, carrying apply₂ + the four
-- bilinearity laws.
------------------------------------------------------------------------

record Bilinear (k l n : ℕ) : Set where
  field
    apply₂′       : Vector k → Vector l → Vector n
    preserves-+ₗ  : (u u' : Vector k) (v : Vector l) →
                    apply₂′ (u +ⱽ u') v ≡ (apply₂′ u v +ⱽ apply₂′ u' v)
    preserves-*ₛₗ : (c : F₂) (u : Vector k) (v : Vector l) →
                    apply₂′ (c *ₛ u) v ≡ (c *ₛ apply₂′ u v)
    preserves-+ᵣ  : (u : Vector k) (v v' : Vector l) →
                    apply₂′ u (v +ⱽ v') ≡ (apply₂′ u v +ⱽ apply₂′ u v')
    preserves-*ₛᵣ : (c : F₂) (u : Vector k) (v : Vector l) →
                    apply₂′ u (c *ₛ v) ≡ (c *ₛ apply₂′ u v)

open Bilinear public

bilinear-from-images : ∀ {k l n} → (Fin k → Fin l → Vector n) → Bilinear k l n
bilinear-from-images f = record
  { apply₂′       = apply₂ f
  ; preserves-+ₗ  = bilinear-+ₗ f
  ; preserves-*ₛₗ = bilinear-*ₛₗ f
  ; preserves-+ᵣ  = bilinear-+ᵣ f
  ; preserves-*ₛᵣ = bilinear-*ₛᵣ f
  }
