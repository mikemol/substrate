------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.Morphism
--
-- The MISSING morphism layer of the graded wedge: a map between two
-- `GradedDivStr` that commutes with `recon` — the graded analogue of
-- `Algebra.Wedge.Bridge` (DivStr morphisms) and `Algebra.Wedge.Product.Hom`
-- (`GradedHom`, GradedProduct morphisms). With it the three carrier layers
-- (DivStr / GradedDivStr / GradedProduct) and their morphism layers connect:
--
--   GradedHom P Q  ── graded-of-product ──▶  GradedDivStrMorphism (gop P) (gop Q)
--   GradedHom P Q  ──────── flatten ───────▶  Bridge (flatten P) (flatten Q)
--
-- so the graded product (the richest, with ∧) projects to BOTH the +1-step
-- graded carrier and the flattened plain carrier — the fragmented graded layer,
-- connected.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.Morphism where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr; C; R; recon)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; graded-of-product; flatten; flatten-recon; gpower)
  renaming (C to Cᵖ; u to uᵖ; _∧_ to _∧ᵖ_)
open import Substrate.Algebra.Wedge.Product.Hom
  using (GradedHom; map₀; map-u; map-∧; flatten-map)

------------------------------------------------------------------------
-- 1. The graded-divstr morphism (parallel to Bridge / GradedHom).
------------------------------------------------------------------------

record GradedDivStrMorphism (G₁ G₂ : GradedDivStr) : Set where
  field
    map-C : {n : ℕ} → C G₁ n → C G₂ n
    map-R : {n : ℕ} → R G₁ n → R G₂ n
    respects-recon : (n : ℕ) (b : C G₁ n) (r : R G₁ n) →
                     map-C (recon G₁ n b r) ≡ recon G₂ n (map-C b) (map-R r)

open GradedDivStrMorphism public

------------------------------------------------------------------------
-- 2. Category structure: identity and composition.
------------------------------------------------------------------------

id-gdsm : (G : GradedDivStr) → GradedDivStrMorphism G G
id-gdsm G = record
  { map-C = λ x → x ; map-R = λ x → x ; respects-recon = λ n b r → refl }

comp-gdsm : {G₁ G₂ G₃ : GradedDivStr} →
            GradedDivStrMorphism G₂ G₃ → GradedDivStrMorphism G₁ G₂ →
            GradedDivStrMorphism G₁ G₃
comp-gdsm g f = record
  { map-C = λ x → map-C g (map-C f x)
  ; map-R = λ x → map-R g (map-R f x)
  ; respects-recon = λ n b r →
      trans (cong (map-C g) (respects-recon f n b r))
            (respects-recon g n (map-C f b) (map-R f r))
  }

------------------------------------------------------------------------
-- 3. Connector A: a GradedHom lifts to a GradedDivStrMorphism on the
--    +1-step slices (graded-of-product). recon = ∧ with the digit on the left.
------------------------------------------------------------------------

gradedHom→gdsMorphism : {P Q : GradedProduct} → GradedHom P Q →
  GradedDivStrMorphism (graded-of-product P) (graded-of-product Q)
gradedHom→gdsMorphism h = record
  { map-C = map₀ h
  ; map-R = map₀ h
  ; respects-recon = λ n b r → map-∧ h r b
  }

------------------------------------------------------------------------
-- 4. Connector B: a GradedHom lifts to a Bridge on the flattened carriers.
--    Needs that the hom respects the q-fold ∧ (gpower).
------------------------------------------------------------------------

map-gpower : {P Q : GradedProduct} (h : GradedHom P Q) {i : ℕ}
             (b : Cᵖ P i) (q : ℕ) →
             map₀ h (gpower P b q) ≡ gpower Q (map₀ h b) q
map-gpower h b zero    = map-u h
map-gpower {P} {Q} h b (suc q) =
  trans (map-∧ h b (gpower P b q))
        (cong (_∧ᵖ_ Q (map₀ h b)) (map-gpower h b q))

gradedHom→bridge : {P Q : GradedProduct} (h : GradedHom P Q) →
  Bridge (flatten P) (flatten Q)
gradedHom→bridge {P} {Q} h = record
  { translate = flatten-map h
  ; respects  = λ where
      q (i , bb) (j , rr) →
        cong ((q * i) + j ,_)
          (trans (map-∧ h (gpower P bb q) rr)
                 (cong (λ z → _∧ᵖ_ Q z (map₀ h rr)) (map-gpower h bb q)))
  ; z-pres    = cong (0 ,_) (map-u h)
  }
