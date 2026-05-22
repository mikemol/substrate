------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter
--
-- ℤ/7ℤ as a Coxeter-style presentation: ⟨a | a⁷ = ε⟩.
--
-- Phase 4 migration of Path 2: thin instance of
-- Substrate.Groups.Coxeter.Cyclic 6 (group order 7).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
import Substrate.Groups.Coxeter.Cyclic 6 as Cyc

open Cyc public using (Gen; a; power)

------------------------------------------------------------------------
-- Canonical = existential view + 7 pattern synonyms.
------------------------------------------------------------------------

Canonical : Word Gen → Set
Canonical w = Σ (Fin 7) (Cyc.Canonical w)

pattern c-ε      = zero                                              , Cyc.c-here zero
pattern c-a      = suc zero                                          , Cyc.c-here (suc zero)
pattern c-aa     = suc (suc zero)                                    , Cyc.c-here (suc (suc zero))
pattern c-aaa    = suc (suc (suc zero))                              , Cyc.c-here (suc (suc (suc zero)))
pattern c-aaaa   = suc (suc (suc (suc zero)))                        , Cyc.c-here (suc (suc (suc (suc zero))))
pattern c-aaaaa  = suc (suc (suc (suc (suc zero))))                  , Cyc.c-here (suc (suc (suc (suc (suc zero)))))
pattern c-aaaaaa = suc (suc (suc (suc (suc (suc zero)))))            , Cyc.c-here (suc (suc (suc (suc (suc (suc zero))))))

insert : Gen → Word Gen → Word Gen
insert = Cyc.insert

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical g (k , c) = Cyc.σ k , Cyc.insert-canonical g c

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

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover (λ {w} _ → normalize w ≡ w)
    (refl , refl , refl , refl , refl , refl , refl)

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
                       insert g (insert g (insert g (insert g
                              (insert g (insert g (insert g w)))))) ≡ w
insert-cycle-id a = canonical-cover
  (λ {w} _ → insert a (insert a (insert a (insert a
              (insert a (insert a (insert a w)))))) ≡ w)
  (refl , refl , refl , refl , refl , refl , refl)

insert-append-lemma :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a {[]}                           w₂ c-ε      = refl
insert-append-lemma a {a ∷ []}                       w₂ c-a      = refl
insert-append-lemma a {a ∷ a ∷ []}                   w₂ c-aa     = refl
insert-append-lemma a {a ∷ a ∷ a ∷ []}               w₂ c-aaa    = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ []}           w₂ c-aaaa   = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ a ∷ []}       w₂ c-aaaaa  = refl
insert-append-lemma a {a ∷ a ∷ a ∷ a ∷ a ∷ a ∷ []}   w₂ c-aaaaaa =
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
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv = Cyc.inv

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical (k , c) = Cyc.inv-pos k , Cyc.inv-canonical c

------------------------------------------------------------------------
-- Z/7-specific theorem: every element to the seventh equals ε.
------------------------------------------------------------------------

private
  flatten-sept-self-product :
    (w : Word Gen) →
    normalize ((((((w · w) · w) · w) · w) · w) · w) ≡
    normalize (normalize w ++ (normalize w ++
               (normalize w ++ (normalize w ++
                (normalize w ++ (normalize w ++ normalize w))))))
  flatten-sept-self-product w =
    trans (normalize-idem ((normalize ((normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) ++ w)) ++ w))
    (trans (sym (normalize-append ((normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) ++ w) w))
    (trans (cong normalize (++-assoc (normalize ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w)) w w))
    (trans (sym (normalize-append (normalize ((normalize ((normalize (w ++ w) ++ w)) ++ w)) ++ w) (w ++ w)))
    (trans (cong normalize (++-assoc (normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) w (w ++ w)))
    (trans (sym (normalize-append ((normalize (normalize (w ++ w) ++ w)) ++ w) (w ++ (w ++ w))))
    (trans (cong normalize (++-assoc (normalize (normalize (w ++ w) ++ w)) w (w ++ (w ++ w))))
    (trans (sym (normalize-append (normalize (w ++ w) ++ w) (w ++ (w ++ (w ++ w)))))
    (trans (cong normalize (++-assoc (normalize (w ++ w)) w (w ++ (w ++ (w ++ w)))))
    (trans (sym (normalize-append (w ++ w) (w ++ (w ++ (w ++ (w ++ w))))))
    (trans (cong normalize (++-assoc w w (w ++ (w ++ (w ++ (w ++ w))))))
           (normalize-sept w w w w w w w)))))))))))

  seventh-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ (w ++ (w ++ (w ++ (w ++ (w ++ w)))))) ≡ []
  seventh-canonical = canonical-cover
    (λ {w} _ → normalize (w ++ (w ++ (w ++ (w ++ (w ++ (w ++ w)))))) ≡ [])
    (refl , refl , refl , refl , refl , refl , refl)

seventh-power-identity : (w : Word Gen) → ((((((w · w) · w) · w) · w) · w) · w) ≈ ε
seventh-power-identity w =
  trans (flatten-sept-self-product w)
        (seventh-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- Inverse-composition theorems.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical = canonical-cover
  (λ {w} _ → normalize (inv w ++ w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical = canonical-cover
  (λ {w} _ → normalize (w ++ inv w) ≡ [])
  (refl , refl , refl , refl , refl , refl , refl)

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical = canonical-cover
  (λ {w} _ → inv (inv w) ≡ w)
  (refl , refl , refl , refl , refl , refl , refl)
