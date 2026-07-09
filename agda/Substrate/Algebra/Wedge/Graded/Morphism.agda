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
-- ⟡set1-paydown: GradedDivStr's carrier/remainder families are now its params, so
-- the old projections `C G` / `R G` become the module params C… / R… threaded here.
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr; recon)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
-- ⟡set1-paydown: GradedProduct's carrier family is now its param (no `C` projection),
-- so the old `Cᵖ P` becomes the module params Cᴾ / Cᴽ threaded on the connectors.
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; graded-of-product; flatten; flatten-recon; gpower)
  renaming (u to uᵖ; _∧_ to _∧ᵖ_)
open import Substrate.Algebra.Wedge.Product.Hom
  using (GradedHom; map₀; map-u; map-∧; flatten-map)

------------------------------------------------------------------------
-- 1. The graded-divstr morphism (parallel to Bridge / GradedHom).
------------------------------------------------------------------------

module _ {C₁ R₁ C₂ R₂ : ℕ → Set} where
  record GradedDivStrMorphism (G₁ : GradedDivStr C₁ R₁)
                              (G₂ : GradedDivStr C₂ R₂) : Set where
    field
      map-C : {n : ℕ} → C₁ n → C₂ n
      map-R : {n : ℕ} → R₁ n → R₂ n
      respects-recon : (n : ℕ) (b : C₁ n) (r : R₁ n) →
                       map-C (recon G₁ n b r) ≡ recon G₂ n (map-C b) (map-R r)

  open GradedDivStrMorphism public

------------------------------------------------------------------------
-- 2. Category structure: identity and composition.
------------------------------------------------------------------------

id-gdsm : {C R : ℕ → Set} (G : GradedDivStr C R) → GradedDivStrMorphism G G
id-gdsm G = record
  { map-C = λ x → x ; map-R = λ x → x ; respects-recon = λ n b r → refl }

comp-gdsm : {C₁ R₁ C₂ R₂ C₃ R₃ : ℕ → Set}
            {G₁ : GradedDivStr C₁ R₁} {G₂ : GradedDivStr C₂ R₂}
            {G₃ : GradedDivStr C₃ R₃} →
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

gradedHom→gdsMorphism : {Cᴾ Cᴽ : ℕ → Set}
  {P : GradedProduct Cᴾ} {Q : GradedProduct Cᴽ} → GradedHom P Q →
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

map-gpower : {Cᴾ Cᴽ : ℕ → Set} {P : GradedProduct Cᴾ} {Q : GradedProduct Cᴽ}
             (h : GradedHom P Q) {i : ℕ}
             (b : Cᴾ i) (q : ℕ) →
             map₀ h (gpower P b q) ≡ gpower Q (map₀ h b) q
map-gpower h b zero    = map-u h
map-gpower {P = P} {Q = Q} h b (suc q) =
  trans (map-∧ h b (gpower P b q))
        (cong (_∧ᵖ_ Q (map₀ h b)) (map-gpower h b q))

gradedHom→bridge : {Cᴾ Cᴽ : ℕ → Set} {P : GradedProduct Cᴾ} {Q : GradedProduct Cᴽ}
  (h : GradedHom P Q) →
  Bridge (flatten P) (flatten Q)
gradedHom→bridge {P = P} {Q = Q} h = record
  { translate = flatten-map h
  ; respects  = λ where
      (qn , _) (i , bb) (j , rr) →
        cong ((qn * i) + j ,_)
          (trans (map-∧ h (gpower P bb qn) rr)
                 (cong (λ z → _∧ᵖ_ Q z (map₀ h rr)) (map-gpower h bb qn)))
  ; z-pres    = cong (0 ,_) (map-u h)
  }
