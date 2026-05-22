------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter
--
-- ℤ/3ℤ as a Coxeter-style presentation: ⟨a | a³ = ε⟩.
--
-- Phase 4 migration of Path 2: this file is a thin instance of
-- Substrate.Groups.Coxeter.Cyclic 2 (group order 3). The named-
-- constructor enumeration (data Canonical with c-ε / c-a / c-aa) is
-- replaced by Cyclic's existential view + pattern synonyms.
-- Downstream pattern-matches like `f Z₃.c-ε = …` continue to work
-- transparently.
--
-- Useful theorem: `cube-identity` — every element cubes to ε.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
import Substrate.Groups.Coxeter.Cyclic 2 as Cyc

------------------------------------------------------------------------
-- 1. Re-export the Z₃ generator + cyclic-suc machinery from Cyclic 2.
------------------------------------------------------------------------

open Cyc public using (Gen; a; power)

------------------------------------------------------------------------
-- 2. Canonical = the existential view + pattern synonyms.
--
-- The substrate's downstream pattern-matches on c-ε / c-a / c-aa
-- continue to work through the synonyms. Each synonym is BOTH a
-- pattern (for case-split) and an expression (for construction).
------------------------------------------------------------------------

Canonical : Word Gen → Set
Canonical w = Σ (Fin 3) (Cyc.Canonical w)

pattern c-ε  = zero               , Cyc.c-here zero
pattern c-a  = suc zero           , Cyc.c-here (suc zero)
pattern c-aa = suc (suc zero)     , Cyc.c-here (suc (suc zero))

------------------------------------------------------------------------
-- 3. insert + insert-canonical via Cyclic. The Word-level insert
-- comes from Cyclic; the existential-lift inserts at the Σ level.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert = Cyc.insert

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical g (k , c) = Cyc.σ k , Cyc.insert-canonical g c

------------------------------------------------------------------------
-- 4. canonical-cover — dispatch via the pattern synonyms.
--
-- The Fin-indexed dispatch lives in Cyc.canonical-cover; this is the
-- substrate's named-constructor form for downstream compat.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _) c-ε  = p
canonical-cover _ (_ , p , _) c-a  = p
canonical-cover _ (_ , _ , p) c-aa = p

------------------------------------------------------------------------
-- 5. Open ListPresentation with the existential Canonical.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 6. Per-relation obligations — same cover-dispatch as before.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover (λ {w} _ → normalize w ≡ w) (refl , refl , refl)

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
              insert g (insert g (insert g w)) ≡ w
insert-cycle-id a = canonical-cover
  (λ {w} _ → insert a (insert a (insert a w)) ≡ w)
  (refl , refl , refl)

insert-append-lemma :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a {[]}         w₂ c-ε  = refl
insert-append-lemma a {a ∷ []}     w₂ c-a  = refl
insert-append-lemma a {a ∷ a ∷ []} w₂ c-aa =
  sym (insert-cycle-id a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 7. Open WithLemmas to inherit the full abstract Core surface.
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
-- 9. Inversion via Cyclic's generic inv-pos + Word-level inv.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv = Cyc.inv

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical (k , c) = Cyc.inv-pos k , Cyc.inv-canonical c

------------------------------------------------------------------------
-- 10. Z/3-specific theorem: every element cubes to ε.
------------------------------------------------------------------------

private
  flatten-triple-self-product :
    (w : Word Gen) →
    normalize ((w · w) · w) ≡
    normalize (normalize w ++ (normalize w ++ normalize w))
  flatten-triple-self-product w =
    trans (normalize-idem (normalize (w ++ w) ++ w))
    (trans (sym (normalize-append (w ++ w) w))
    (trans (cong normalize (++-assoc w w w))
           (normalize-triple w w w)))

  cube-canonical : {w : Word Gen} → Canonical w →
                   normalize (w ++ (w ++ w)) ≡ []
  cube-canonical = canonical-cover
    (λ {w} _ → normalize (w ++ (w ++ w)) ≡ [])
    (refl , refl , refl)

cube-identity : (w : Word Gen) → ((w · w) · w) ≈ ε
cube-identity w =
  trans (flatten-triple-self-product w)
        (cube-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 11. Inverse-composition theorems on canonical forms.
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
-- 12. Z/3 is abelian: inv distributes over the product. 9 refls
-- via nested cover (3 outer × 3 inner) on canonical inputs.
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
