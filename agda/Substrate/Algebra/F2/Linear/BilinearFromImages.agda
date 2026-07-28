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
open import Substrate.Foundation.Fin.Fin
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
-- Ⓑ′: the image-family properties now live at their base (ImagesProps), and
-- this special (n=2) module imports the GENERIC (MultilinearFromImages) —
-- special = instance of generic, the right direction (the inversion is gone).
open import Substrate.Algebra.F2.Linear.ImagesProps
  using (images-cong; images-add; images-scale)
open import Substrate.Algebra.F2.Linear.MultilinearFromImages
  using (apply-n)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Unit using (tt)

-- sum-F₂-+-distrib / sum-F₂-·-distrib and images-cong / images-add /
-- images-scale moved to Substrate.Algebra.F2.Linear.ImagesProps (their base
-- layer; imported above). The four bilinearity laws below use them from there.

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

------------------------------------------------------------------------
-- Ⓑ: apply₂ IS the n=2 instance of the generic apply-n. The bilinear
-- existence map reduces, DEFINITIONALLY (function-η on the inner table), to
-- apply-n at arity (k ∷ l ∷ []) on the uncurried basis-pair table — so the
-- existence side is ONE INSTANCE of the generic, the mirror of the uniqueness
-- side (BilinearUniversal: bilinear-extensionality = multilinear-extensionality
-- at n=2). The either/or "apply₂ vs apply-n" dissolves: apply₂ is apply-n at n=2.
------------------------------------------------------------------------

apply₂-is-apply-n :
  ∀ {k l n} (f : Fin k → Fin l → Vector n) (u : Vector k) (v : Vector l) →
  apply₂ f u v
    ≡ apply-n {ks = k ∷ l ∷ []} (λ idx → f (proj₁ idx) (proj₁ (proj₂ idx))) (u , v , tt)
apply₂-is-apply-n f u v = refl
