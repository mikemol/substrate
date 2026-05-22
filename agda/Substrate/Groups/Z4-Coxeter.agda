------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter
--
-- ℤ/4ℤ as a Coxeter-style presentation: ⟨a | a⁴ = ε⟩.
--
-- Phase 4 migration of Path 2: thin instance of
-- Substrate.Groups.Coxeter.Cyclic 3 (group order 4). Named-constructor
-- enumeration replaced by Cyclic's existential view + pattern synonyms.
-- Downstream pattern-matches continue to work transparently.
--
-- Useful theorem: `fourth-power-identity` — every element's fourth
-- power equals ε.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
import Substrate.Groups.Coxeter.Cyclic 3 as Cyc

------------------------------------------------------------------------
-- 1. Re-export the Z₄ generator from Cyclic 3.
------------------------------------------------------------------------

open Cyc public using (Gen; a; power)

------------------------------------------------------------------------
-- 2. Canonical = existential view + pattern synonyms.
------------------------------------------------------------------------

Canonical : Word Gen → Set
Canonical w = Σ (Fin 4) (Cyc.Canonical w)

pattern c-ε   = zero                       , Cyc.c-here zero
pattern c-a   = suc zero                   , Cyc.c-here (suc zero)
pattern c-aa  = suc (suc zero)             , Cyc.c-here (suc (suc zero))
pattern c-aaa = suc (suc (suc zero))       , Cyc.c-here (suc (suc (suc zero)))

------------------------------------------------------------------------
-- 3. insert + insert-canonical from Cyclic.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert = Cyc.insert

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical g (k , c) = Cyc.σ k , Cyc.insert-canonical g c

------------------------------------------------------------------------
-- 4. canonical-cover via named-constructor dispatch.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _ , _) c-ε   = p
canonical-cover _ (_ , p , _ , _) c-a   = p
canonical-cover _ (_ , _ , p , _) c-aa  = p
canonical-cover _ (_ , _ , _ , p) c-aaa = p

------------------------------------------------------------------------
-- 5. Open ListPresentation.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 6. Per-relation obligations.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover (λ {w} _ → normalize w ≡ w) (refl , refl , refl , refl)

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
                  insert g (insert g (insert g (insert g w))) ≡ w
insert-cycle-id a = canonical-cover
  (λ {w} _ → insert a (insert a (insert a (insert a w))) ≡ w)
  (refl , refl , refl , refl)

insert-append-lemma :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a {[]}             w₂ c-ε   = refl
insert-append-lemma a {a ∷ []}         w₂ c-a   = refl
insert-append-lemma a {a ∷ a ∷ []}     w₂ c-aa  = refl
insert-append-lemma a {a ∷ a ∷ a ∷ []} w₂ c-aaa =
  sym (insert-cycle-id a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 7. Open WithLemmas to inherit the Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma public

------------------------------------------------------------------------
-- 8. Decidable equality on Canonical forms.
------------------------------------------------------------------------

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- 9. Inversion on canonical forms — Z/4 table.
--   inv []        = []
--   inv [a]       = [a,a,a]      (a⁻¹ = a³)
--   inv [a,a]     = [a,a]        (a² self-inverse)
--   inv [a,a,a]   = [a]          ((a³)⁻¹ = a)
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv []               = []
inv (a ∷ [])         = a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ [])     = a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ []) = a ∷ []
inv w                = w  -- fallback

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c-ε   = c-ε
inv-canonical c-a   = c-aaa
inv-canonical c-aa  = c-aa
inv-canonical c-aaa = c-a

------------------------------------------------------------------------
-- 10. Z/4-specific theorem: every element to the fourth equals ε.
------------------------------------------------------------------------

private
  flatten-quad-self-product :
    (w : Word Gen) →
    normalize (((w · w) · w) · w) ≡
    normalize (normalize w ++ (normalize w ++ (normalize w ++ normalize w)))
  flatten-quad-self-product w =
    trans (normalize-idem ((normalize (normalize (w ++ w) ++ w)) ++ w))
    (trans (sym (normalize-append (normalize (w ++ w) ++ w) w))
    (trans (cong normalize (++-assoc (normalize (w ++ w)) w w))
    (trans (sym (normalize-append (w ++ w) (w ++ w)))
    (trans (cong normalize (++-assoc w w (w ++ w)))
           (normalize-quad w w w w)))))

  fourth-canonical : {w : Word Gen} → Canonical w →
                     normalize (w ++ (w ++ (w ++ w))) ≡ []
  fourth-canonical = canonical-cover
    (λ {w} _ → normalize (w ++ (w ++ (w ++ w))) ≡ [])
    (refl , refl , refl , refl)

fourth-power-identity : (w : Word Gen) → (((w · w) · w) · w) ≈ ε
fourth-power-identity w =
  trans (flatten-quad-self-product w)
        (fourth-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 11. Inverse-composition theorems on canonical forms.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl , refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl , refl , refl)

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl , refl , refl)
