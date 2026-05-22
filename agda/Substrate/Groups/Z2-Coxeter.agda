------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter
--
-- ℤ/2ℤ as a Coxeter-style presentation: ⟨a | a² = ε⟩.
--
-- Phase 4 migration of Path 2: thin instance of
-- Substrate.Groups.Coxeter.Cyclic 1 (group order 2). Z₂'s involution
-- semantics (a² = ε, inv = identity) drop out of the cyclic structure
-- at n=1.
--
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
import Substrate.Groups.Coxeter.Cyclic 1 as Cyc

open Cyc public using (Gen; a; power)

------------------------------------------------------------------------
-- Canonical = existential view + 2 pattern synonyms.
------------------------------------------------------------------------

Canonical : Word Gen → Set
Canonical w = Σ (Fin 2) (Cyc.Canonical w)

pattern c-ε = zero     , Cyc.c-here zero
pattern c-a = suc zero , Cyc.c-here (suc zero)

insert : Gen → Word Gen → Word Gen
insert = Cyc.insert

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical g (k , c) = Cyc.σ k , Cyc.insert-canonical g c

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _) c-ε = p
canonical-cover _ (_ , p) c-a = p

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover (λ {w} _ → normalize w ≡ w) (refl , refl)

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
                  insert g (insert g w) ≡ w
insert-cycle-id a = canonical-cover
  (λ {w} _ → insert a (insert a w) ≡ w)
  (refl , refl)

insert-append-lemma :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a {[]}     w₂ c-ε = refl
insert-append-lemma a {a ∷ []} w₂ c-a =
  sym (insert-cycle-id a (normalize-canonical w₂))

open WithLemmas canonical-is-fixed insert-append-lemma public

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Inversion via Cyclic's generic inv-pos + Word-level inv.
-- (Z/2 elements are self-inverse; Cyc.inv at n=1 implements this.)
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv = Cyc.inv

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical (k , c) = Cyc.inv-pos k , Cyc.inv-canonical c

inv-left-canonical : {w : Word Gen} → Canonical w → normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w → normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl)

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl)

------------------------------------------------------------------------
-- Z/2-specific theorem: self-inverse at the Core level.
------------------------------------------------------------------------

private
  flatten-self-product :
    (w : Word Gen) → normalize (w · w) ≡ normalize (normalize w ++ normalize w)
  flatten-self-product w =
    trans (normalize-idem (w ++ w))
          (normalize-distrib w w)

  self-inverse-canonical :
    {w : Word Gen} → Canonical w → normalize (w ++ w) ≡ []
  self-inverse-canonical = canonical-cover
    (λ {w} _ → normalize (w ++ w) ≡ [])
    (refl , refl)

self-inverse : (w : Word Gen) → (w · w) ≈ []
self-inverse w =
  trans (flatten-self-product w)
        (self-inverse-canonical (normalize-canonical w))
