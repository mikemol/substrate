------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter
--
-- ℤ/3ℤ as a Coxeter-style presentation: ⟨a | a³ = ε⟩.
--
-- Thin instance of Substrate.Groups.Coxeter.Cyclic 2. Cyclic provides
-- Gen / Canonical-ex / canonical-cover-ex / σ / insert / insert-canonical-ex
-- / inv / inv-canonical-ex / the parametric c-pos pattern synonym AND
-- the ListPresentation + WithLemmas surface (normalize / _·_ / _≈_ / ε /
-- normalize-distrib / etc.). Consumers use `(Z₃.c-pos k)` for the
-- k-th canonical witness (k ∈ Fin 3); no per-arity pattern names are
-- needed. This file just supplies:
--   * canonical-cover (tuple-style dispatcher over (c-pos zero/₁/₂))
--   * same-canonical (single-Gen decidability)
--   * cube-identity + inv-distrib-canonical (Z₃-specific theorems)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter where
open import Substrate.Groups.Coxeter.Cyclic.Inverse 2 using (inv)
open import Substrate.Groups.Coxeter.Cyclic.NthPower 2 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 2 using (_·_; _≈_; ε)
open import Substrate.Groups.Coxeter.Cyclic.Base 2 using (Gen; gen-≟; a)

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 2 using (c-pos; normalize) renaming (Canonical-ex to Canonical-at; insert-canonical-ex to insert-canonical; inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv 2 using () renaming (inv-inv-canonical-ex to inv-inv-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left 2 using () renaming (inv-left-canonical-ex to inv-left-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right 2 using () renaming (inv-right-canonical-ex to inv-right-canonical)

------------------------------------------------------------------------
-- Tuple-style canonical-cover, built on the parametric c-pos pattern
-- synonym (no per-Zₙ legacy ladder needed).
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)
canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical-at w → Set ℓ) →
  P (c-pos zero) × P (c-pos ₁) × P (c-pos ₂) →
  ∀ {w} (c : Canonical-at w) → P c
canonical-cover _ (p , _ , _) (c-pos zero)             = p
canonical-cover _ (_ , p , _) (c-pos ₁)       = p
canonical-cover _ (_ , _ , p) (c-pos ₂) = p

------------------------------------------------------------------------
-- Decidable equality.
------------------------------------------------------------------------


same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

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

inv-distrib-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ →
                        normalize (inv (normalize (w₁ ++ w₂))) ≡
                        normalize (inv w₁ ++ inv w₂)
inv-distrib-canonical c₁ c₂ = canonical-cover
  (λ {w₁} _ → ∀ {w₂} (c₂' : Canonical-at w₂) →
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
