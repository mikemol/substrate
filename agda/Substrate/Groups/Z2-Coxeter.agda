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
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq
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
-- Canonical-cover for Z₂: 2-tuple of per-position proofs onto any
-- `Canonical w`. Heterogeneous-output via each refl's own implicit {x}.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (_×_; _,_)

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _) c-ε = p
canonical-cover _ (_ , p) c-a = p

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/2's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma public

------------------------------------------------------------------------
-- 6. Decidable equality on Canonical forms.
------------------------------------------------------------------------

-- Decidable Gen equality (Z₂'s Gen has a single constructor).
gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- 7. Inversion on canonical forms — Z/2 elements are self-inverse:
--   inv []    = []
--   inv [a]   = [a]
--
-- inv = identity on the canonical level (a is its own inverse).
-- The same-shape obligations for the GroupAdapter pipe come along
-- with it. Exposed at this level so Z2-Coxeter-Group stays a thin
-- adapter like its Z3/Z4/Z5/Z7 siblings.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv w = w

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c = c

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
-- 8. Z/2-specific theorem: self-inverse at the Core level.
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
