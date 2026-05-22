------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter
--
-- ℤ/4ℤ as Coxeter ⟨a | a⁴ = ε⟩. Thin instance of Coxeter.Cyclic 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic 3 public
  hiding (Canonical; insert-canonical; inv-canonical; c-ε; canonical-cover)
  renaming (Canonical-ex to Canonical; insert-canonical-ex to insert-canonical;
            inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin;
            inv-left-canonical-ex to inv-left-canonical;
            inv-right-canonical-ex to inv-right-canonical;
            inv-inv-canonical-ex to inv-inv-canonical)

pattern c-ε   = zero                       , c-here zero
pattern c-a   = suc zero                   , c-here (suc zero)
pattern c-aa  = suc (suc zero)             , c-here (suc (suc zero))
pattern c-aaa = suc (suc (suc zero))       , c-here (suc (suc (suc zero)))

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _ , _) c-ε   = p
canonical-cover _ (_ , p , _ , _) c-a   = p
canonical-cover _ (_ , _ , p , _) c-aa  = p
canonical-cover _ (_ , _ , _ , p) c-aaa = p

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/4-specific theorem: every element to the fourth equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 3 (apply-power-suc w 3 = ((w · w) · w) · w by definition).
------------------------------------------------------------------------

fourth-power-identity : (w : Word Gen) → (((w · w) · w) · w) ≈ ε
fourth-power-identity = nth-power-identity
