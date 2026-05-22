------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter
--
-- ℤ/3ℤ as a Coxeter-style presentation: ⟨a | a³ = ε⟩.
--
-- Smallest cyclic group of odd order; first Coxeter instance whose
-- generator is NOT an involution (cf. Z2-Coxeter / V4-Coxeter). Validates
-- that Substrate.Groups.Coxeter.Core handles non-involutive cyclic
-- relations via `insert-cube` (the a³ = ε analog of Z/2's
-- insert-involution).
--
-- Useful theorem: `cube-identity` — every element cubes to ε
-- (the Z/3 parallel of Z/2's `self-inverse`).
--
-- Used by: future Substrate.Groups.S3 = Z/3 ⋊ Z/2 via the planned
-- SemidirectProduct combinator (S₄ = V₄ ⋊ S₃, see CY-5).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; _≢_)

------------------------------------------------------------------------
-- 1. Z/3-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

data Canonical : Word Gen → Set where
  c-ε  : Canonical []
  c-a  : Canonical (a ∷ [])
  c-aa : Canonical (a ∷ a ∷ [])

------------------------------------------------------------------------
-- 2. The insert step: encodes a³ = ε as a 3-cyclic wrap on canonical
-- forms — [] → [a] → [a,a] → [].
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert a []           = a ∷ []
insert a (a ∷ [])     = a ∷ a ∷ []
insert a (a ∷ a ∷ []) = []
insert g w            = g ∷ w  -- fallback (unreachable for Canonical inputs)

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical a c-ε  = c-a
insert-canonical a c-a  = c-aa
insert-canonical a c-aa = c-ε

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/3's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
--
-- canonical-is-fixed: trivial 3-refl enumeration.
--
-- insert-cube: the a³ = ε relation lifted to the insert level —
-- inserting `a` three times restores the input. Used by case [a,a] of
-- insert-append-lemma.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed c-ε  = refl
canonical-is-fixed c-a  = refl
canonical-is-fixed c-aa = refl

insert-cube : (g : Gen) {w : Word Gen} → Canonical w →
              insert g (insert g (insert g w)) ≡ w
insert-cube a c-ε  = refl
insert-cube a c-a  = refl
insert-cube a c-aa = refl

insert-append-lemma-Z3 :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-Z3 a {[]}         w₂ c-ε  = refl
insert-append-lemma-Z3 a {a ∷ []}     w₂ c-a  = refl
insert-append-lemma-Z3 a {a ∷ a ∷ []} w₂ c-aa =
  sym (insert-cube a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma-Z3 public

------------------------------------------------------------------------
-- 6. Decidable equality on Canonical forms.
------------------------------------------------------------------------

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ a a = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)
open import Substrate.Foundation.Product using (_×_; _,_)

------------------------------------------------------------------------
-- Canonical-cover for Z₃: dispatches a 3-tuple of per-position
-- proofs onto any `Canonical w`. Each refl literal infers its own
-- implicit {x} so heterogeneous-output Cayley tables work too.
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _) c-ε  = p
canonical-cover _ (_ , p , _) c-a  = p
canonical-cover _ (_ , _ , p) c-aa = p

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- 7. Inversion on canonical forms — Z/3 elements are NOT self-inverse:
--   inv []     = []
--   inv [a]    = [a,a]
--   inv [a,a]  = [a]
--
-- Exposed as a per-instance operation; the eventual Z3.agda adapter
-- will use this when constructing the Group bundle. The Core's
-- _·_/_≈_/ε layer remains inverse-free.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv []           = []
inv (a ∷ [])     = a ∷ a ∷ []
inv (a ∷ a ∷ []) = a ∷ []
inv w            = w  -- fallback (unreachable for Canonical inputs)

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c-ε  = c-ε
inv-canonical c-a  = c-aa
inv-canonical c-aa = c-a

------------------------------------------------------------------------
-- 8. Z/3-specific theorem: every element cubes to ε.
--
-- Parallel of Z2-Coxeter's `self-inverse`. Composes a flatten-step
-- (bridge `(w · w) · w` to a flat 3-arg form) with a 3-refl
-- enumeration on Canonical w.
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
  cube-canonical c-ε  = refl
  cube-canonical c-a  = refl
  cube-canonical c-aa = refl

cube-identity : (w : Word Gen) → ((w · w) · w) ≈ ε
cube-identity w =
  trans (flatten-triple-self-product w)
        (cube-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 9. Inverse-composition theorems on canonical forms.
--
-- inv-left-canonical / inv-right-canonical: on Canonical w, the
-- composition `inv w · w` and `w · inv w` both yield ε. 3 refl cases
-- each. Used by the eventual Z3.agda adapter to build the Group bundle.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical c-ε  = refl
inv-left-canonical c-a  = refl
inv-left-canonical c-aa = refl

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical c-ε  = refl
inv-right-canonical c-a  = refl
inv-right-canonical c-aa = refl

------------------------------------------------------------------------
-- 10. inv is involutive on canonical forms: inv (inv w) ≡ w.
------------------------------------------------------------------------

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical c-ε  = refl
inv-inv-canonical c-a  = refl
inv-inv-canonical c-aa = refl

------------------------------------------------------------------------
-- 11. Z/3 is abelian, so inv distributes (not anti-distributes) over
-- the product. 9 refl cases on canonical inputs.
--
-- Stated in the "after-normalize" form needed by the Z/2 → Aut(Z/3)
-- action: normalize (inv (normalize (w₁ ++ w₂))) ≡ normalize (inv w₁ ++ inv w₂).
------------------------------------------------------------------------

inv-distrib-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ →
                        normalize (inv (normalize (w₁ ++ w₂))) ≡
                        normalize (inv w₁ ++ inv w₂)
inv-distrib-canonical c-ε  c-ε  = refl
inv-distrib-canonical c-ε  c-a  = refl
inv-distrib-canonical c-ε  c-aa = refl
inv-distrib-canonical c-a  c-ε  = refl
inv-distrib-canonical c-a  c-a  = refl
inv-distrib-canonical c-a  c-aa = refl
inv-distrib-canonical c-aa c-ε  = refl
inv-distrib-canonical c-aa c-a  = refl
inv-distrib-canonical c-aa c-aa = refl
