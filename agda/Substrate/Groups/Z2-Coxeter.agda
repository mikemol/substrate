------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter
--
-- ℤ/2ℤ as Coxeter ⟨a | a² = ε⟩. Thin instance of Coxeter.Cyclic 1.
-- Useful theorem: `self-inverse` (every element is its own inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic 1 public
  hiding (Canonical; insert-canonical; inv-canonical; c-ε; canonical-cover)
  renaming (Canonical-ex to Canonical; insert-canonical-ex to insert-canonical;
            inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin;
            inv-left-canonical-ex to inv-left-canonical;
            inv-right-canonical-ex to inv-right-canonical;
            inv-inv-canonical-ex to inv-inv-canonical)

pattern c-ε = zero     , c-here zero
pattern c-a = suc zero , c-here (suc zero)

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _) c-ε = p
canonical-cover _ (_ , p) c-a = p

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/2-specific theorem: self-inverse. Specialization of the generic
-- nth-power-identity from Coxeter.Cyclic at n = 1
-- (apply-power-suc w 1 = w · w by definition).
------------------------------------------------------------------------

self-inverse : (w : Word Gen) → (w · w) ≈ []
self-inverse = nth-power-identity
