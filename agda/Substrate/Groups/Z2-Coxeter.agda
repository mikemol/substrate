------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter
--
-- ℤ/2ℤ as a Coxeter presentation: ⟨a | a² = ε⟩.
--
-- The SMALLEST non-trivial Coxeter instance. Uses the custom
-- Substrate.Groups.Coxeter.Word (NOT Data.List) — eliminates the
-- clashing-definition friction that arose when Core re-exports
-- alongside Data.List imports.
--
-- Useful theorem: `self-inverse` (every element is its own inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Data.Empty using (⊥; ⊥-elim)
open import Relation.Nullary using (Dec; yes; no)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong; _≢_)

------------------------------------------------------------------------
-- 1. Z/2-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

data Canonical : Word Gen → Set where
  c-ε : Canonical []
  c-a : Canonical (a ∷ [])

------------------------------------------------------------------------
-- 2. The insert step: encodes a² = ε via cancellation.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert a []       = a ∷ []
insert a (a ∷ []) = []
insert g w        = g ∷ w  -- fallback (unreachable for Canonical inputs)

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical a c-ε = c-a
insert-canonical a c-a = c-ε

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/2's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
------------------------------------------------------------------------

canonical-is-fixed-Z2 : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed-Z2 c-ε = refl
canonical-is-fixed-Z2 c-a = refl

insert-involution : (g : Gen) {w : Word Gen} → Canonical w →
                    insert g (insert g w) ≡ w
insert-involution a c-ε = refl
insert-involution a c-a = refl

insert-append-lemma-Z2 :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-Z2 a {[]}     w₂ c-ε = refl
insert-append-lemma-Z2 a {a ∷ []} w₂ c-a =
  sym (insert-involution a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed-Z2 insert-append-lemma-Z2 public

------------------------------------------------------------------------
-- 6. Decidable equality on Canonical forms.
------------------------------------------------------------------------

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical c-ε c-ε = yes refl
same-canonical c-a c-a = yes refl
same-canonical c-ε c-a = no (λ ())
same-canonical c-a c-ε = no (λ ())

------------------------------------------------------------------------
-- 7. Z/2-specific theorem: self-inverse.
------------------------------------------------------------------------

private
  flatten-self-product :
    (w : Word Gen) → normalize (w · w) ≡ normalize (normalize w ++ normalize w)
  flatten-self-product w =
    trans (normalize-idem (w ++ w))
          (normalize-distrib w w)

  self-inverse-canonical :
    {w : Word Gen} → Canonical w → normalize (w ++ w) ≡ []
  self-inverse-canonical c-ε = refl
  self-inverse-canonical c-a = refl

self-inverse : (w : Word Gen) → (w · w) ≈ []
self-inverse w =
  trans (flatten-self-product w)
        (self-inverse-canonical (normalize-canonical w))
