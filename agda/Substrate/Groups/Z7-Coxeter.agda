------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter
--
-- ℤ/7ℤ as Coxeter ⟨a | a⁷ = ε⟩. Thin instance of Coxeter.Cyclic 6.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic 6 public
  hiding (Canonical; insert-canonical; inv-canonical; c-ε; canonical-cover)
  renaming (Canonical-ex to Canonical; insert-canonical-ex to insert-canonical;
            inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin)

pattern c-ε      = zero                                              , c-here zero
pattern c-a      = suc zero                                          , c-here (suc zero)
pattern c-aa     = suc (suc zero)                                    , c-here (suc (suc zero))
pattern c-aaa    = suc (suc (suc zero))                              , c-here (suc (suc (suc zero)))
pattern c-aaaa   = suc (suc (suc (suc zero)))                        , c-here (suc (suc (suc (suc zero))))
pattern c-aaaaa  = suc (suc (suc (suc (suc zero))))                  , c-here (suc (suc (suc (suc (suc zero)))))
pattern c-aaaaaa = suc (suc (suc (suc (suc (suc zero)))))            , c-here (suc (suc (suc (suc (suc (suc zero))))))

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa × P c-aaaa × P c-aaaaa × P c-aaaaaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _ , _ , _ , _ , _) c-ε      = p
canonical-cover _ (_ , p , _ , _ , _ , _ , _) c-a      = p
canonical-cover _ (_ , _ , p , _ , _ , _ , _) c-aa     = p
canonical-cover _ (_ , _ , _ , p , _ , _ , _) c-aaa    = p
canonical-cover _ (_ , _ , _ , _ , p , _ , _) c-aaaa   = p
canonical-cover _ (_ , _ , _ , _ , _ , p , _) c-aaaaa  = p
canonical-cover _ (_ , _ , _ , _ , _ , _ , p) c-aaaaaa = p

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

inv-left-canonical : {w : Word Gen} → Canonical w → normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w → normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl , refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- Z/7-specific theorem: every element to the seventh equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 6 (apply-power-suc w 6 = ((((((w·w)·w)·w)·w)·w)·w) by definition).
------------------------------------------------------------------------

seventh-power-identity : (w : Word Gen) → ((((((w · w) · w) · w) · w) · w) · w) ≈ ε
seventh-power-identity = nth-power-identity
