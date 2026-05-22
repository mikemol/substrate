------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter
--
-- ℤ/3ℤ as a Coxeter-style presentation: ⟨a | a³ = ε⟩.
--
-- Path 2 Phase 5: thin instance of Substrate.Groups.Coxeter.Cyclic 2.
-- Cyclic provides Gen / Canonical-ex / canonical-cover / σ / insert /
-- insert-canonical-ex / inv / inv-canonical-ex AND the ListPresentation
-- + WithLemmas surface (normalize / _·_ / _≈_ / ε / normalize-distrib /
-- etc.). This file just supplies:
--   * Named-constructor pattern synonyms (c-ε, c-a, c-aa)
--   * Named-version canonical-cover (uses the synonyms)
--   * gen-≟ + same-canonical (single-Gen decidability)
--   * cube-identity + inv-distrib-canonical (Z₃-specific theorems)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic 2 public
  hiding (Canonical; insert-canonical; inv-canonical; c-ε; canonical-cover)
  renaming (Canonical-ex to Canonical; insert-canonical-ex to insert-canonical;
            inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin)

------------------------------------------------------------------------
-- Named-constructor pattern synonyms.
------------------------------------------------------------------------

pattern c-ε  = zero               , c-here zero
pattern c-a  = suc zero           , c-here (suc zero)
pattern c-aa = suc (suc zero)     , c-here (suc (suc zero))

------------------------------------------------------------------------
-- Named-version canonical-cover (dispatches via the synonyms).
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _) c-ε  = p
canonical-cover _ (_ , p , _) c-a  = p
canonical-cover _ (_ , _ , p) c-aa = p

------------------------------------------------------------------------
-- Decidable equality.
------------------------------------------------------------------------

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Inverse-composition theorems (cover-applied with all-refls).
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl , refl)

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl , refl)

------------------------------------------------------------------------
-- Z/3-specific theorem: every element cubes to ε. Specialization of
-- the generic nth-power-identity from Coxeter.Cyclic at n = 2
-- (apply-power-suc w 2 = (w · w) · w by definition).
------------------------------------------------------------------------

cube-identity : (w : Word Gen) → ((w · w) · w) ≈ ε
cube-identity = nth-power-identity

------------------------------------------------------------------------
-- Z/3 is abelian: inv distributes over the product. 9 refls via
-- nested cover (3 outer × 3 inner) on canonical inputs.
------------------------------------------------------------------------

inv-distrib-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ →
                        normalize (inv (normalize (w₁ ++ w₂))) ≡
                        normalize (inv w₁ ++ inv w₂)
inv-distrib-canonical c₁ c₂ = canonical-cover
  (λ {w₁} _ → ∀ {w₂} (c₂' : Canonical w₂) →
              normalize (inv (normalize (w₁ ++ w₂))) ≡
              normalize (inv w₁ ++ inv w₂))
  ( canonical-cover
      (λ {w₂} _ → normalize (inv (normalize ([] ++ w₂))) ≡
                  normalize (inv [] ++ inv w₂))
      (refl , refl , refl)
  , canonical-cover
      (λ {w₂} _ → normalize (inv (normalize ((a ∷ []) ++ w₂))) ≡
                  normalize (inv (a ∷ []) ++ inv w₂))
      (refl , refl , refl)
  , canonical-cover
      (λ {w₂} _ → normalize (inv (normalize ((a ∷ a ∷ []) ++ w₂))) ≡
                  normalize (inv (a ∷ a ∷ []) ++ inv w₂))
      (refl , refl , refl)
  )
  c₁ c₂
