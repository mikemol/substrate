------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter
--
-- ℤ/5ℤ as a Coxeter-style presentation: ⟨a | a⁵ = ε⟩.
--
-- First cyclic-of-prime-order Coxeter instance at prime > 3. Mirror
-- of Substrate.Groups.Z3-Coxeter and Substrate.Groups.Z4-Coxeter at
-- n=5: explicit Canonical constructors c-ε / c-a / c-aa / c-aaa /
-- c-aaaa, insert wraps at length 5, fifth-power-identity replaces
-- cube-identity / fourth-power-identity.
--
-- Demonstrates the substrate-native cyclic-Coxeter pattern scales
-- to arbitrary specific n with mechanical uniformity. Per
-- [[feedback-roll-our-own-via-word-algebra]]: third concrete instance
-- in the Zₙ family.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; _≢_)

------------------------------------------------------------------------
-- 1. Z/5-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

data Canonical : Word Gen → Set where
  c-ε    : Canonical []
  c-a    : Canonical (a ∷ [])
  c-aa   : Canonical (a ∷ a ∷ [])
  c-aaa  : Canonical (a ∷ a ∷ a ∷ [])
  c-aaaa : Canonical (a ∷ a ∷ a ∷ a ∷ [])

------------------------------------------------------------------------
-- 2. The insert step: encodes a⁵ = ε as a 5-cyclic wrap on canonical
-- forms — [] → [a] → [a,a] → [a,a,a] → [a,a,a,a] → [].
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert a []                   = a ∷ []
insert a (a ∷ [])             = a ∷ a ∷ []
insert a (a ∷ a ∷ [])         = a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ [])     = a ∷ a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ a ∷ []) = []
insert g w                    = g ∷ w  -- fallback (unreachable for Canonical inputs)

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical a c-ε    = c-a
insert-canonical a c-a    = c-aa
insert-canonical a c-aa   = c-aaa
insert-canonical a c-aaa  = c-aaaa
insert-canonical a c-aaaa = c-ε

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/5's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed c-ε    = refl
canonical-is-fixed c-a    = refl
canonical-is-fixed c-aa   = refl
canonical-is-fixed c-aaa  = refl
canonical-is-fixed c-aaaa = refl

insert-cycle-id : (g : Gen) {w : Word Gen} → Canonical w →
                     insert g (insert g (insert g (insert g (insert g w)))) ≡ w
insert-cycle-id a c-ε    = refl
insert-cycle-id a c-a    = refl
insert-cycle-id a c-aa   = refl
insert-cycle-id a c-aaa  = refl
insert-cycle-id a c-aaaa = refl

insert-append-lemma-Z5 :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-Z5 a {[]}                 w₂ c-ε    = refl
insert-append-lemma-Z5 a {a ∷ []}             w₂ c-a    = refl
insert-append-lemma-Z5 a {a ∷ a ∷ []}         w₂ c-aa   = refl
insert-append-lemma-Z5 a {a ∷ a ∷ a ∷ []}     w₂ c-aaa  = refl
insert-append-lemma-Z5 a {a ∷ a ∷ a ∷ a ∷ []} w₂ c-aaaa =
  sym (insert-cycle-id a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma-Z5 public

------------------------------------------------------------------------
-- 6. Inversion on canonical forms — Z/5 (prime-order cyclic):
--   inv []          = []
--   inv [a]         = [a,a,a,a]   (a⁻¹ = a⁴)
--   inv [a,a]       = [a,a,a]     ((a²)⁻¹ = a³)
--   inv [a,a,a]     = [a,a]       ((a³)⁻¹ = a²)
--   inv [a,a,a,a]   = [a]         ((a⁴)⁻¹ = a)
-- Z/5 has no non-trivial subgroups (prime order); every non-identity
-- element generates the full group.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv []                   = []
inv (a ∷ [])             = a ∷ a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ [])         = a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ [])     = a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ a ∷ []) = a ∷ []
inv w                    = w  -- fallback

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c-ε    = c-ε
inv-canonical c-a    = c-aaaa
inv-canonical c-aa   = c-aaa
inv-canonical c-aaa  = c-aa
inv-canonical c-aaaa = c-a

------------------------------------------------------------------------
-- 7. Z/5-specific theorem: every element to the fifth equals ε.
------------------------------------------------------------------------

private
  flatten-quint-self-product :
    (w : Word Gen) →
    normalize ((((w · w) · w) · w) · w) ≡
    normalize (normalize w ++ (normalize w ++
               (normalize w ++ (normalize w ++ normalize w))))
  flatten-quint-self-product w =
    trans (normalize-idem ((normalize ((normalize (normalize (w ++ w) ++ w)) ++ w)) ++ w))
    (trans (sym (normalize-append ((normalize (normalize (w ++ w) ++ w)) ++ w) w))
    (trans (cong normalize (++-assoc (normalize (normalize (w ++ w) ++ w)) w w))
    (trans (sym (normalize-append (normalize (w ++ w) ++ w) (w ++ w)))
    (trans (cong normalize (++-assoc (normalize (w ++ w)) w (w ++ w)))
    (trans (sym (normalize-append (w ++ w) (w ++ (w ++ w))))
    (trans (cong normalize (++-assoc w w (w ++ (w ++ w))))
           (normalize-quint w w w w w)))))))

  fifth-canonical : {w : Word Gen} → Canonical w →
                    normalize (w ++ (w ++ (w ++ (w ++ w)))) ≡ []
  fifth-canonical c-ε    = refl
  fifth-canonical c-a    = refl
  fifth-canonical c-aa   = refl
  fifth-canonical c-aaa  = refl
  fifth-canonical c-aaaa = refl

fifth-power-identity : (w : Word Gen) → ((((w · w) · w) · w) · w) ≈ ε
fifth-power-identity w =
  trans (flatten-quint-self-product w)
        (fifth-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 8. Inverse-composition theorems on canonical forms.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical c-ε    = refl
inv-left-canonical c-a    = refl
inv-left-canonical c-aa   = refl
inv-left-canonical c-aaa  = refl
inv-left-canonical c-aaaa = refl

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical c-ε    = refl
inv-right-canonical c-a    = refl
inv-right-canonical c-aa   = refl
inv-right-canonical c-aaa  = refl
inv-right-canonical c-aaaa = refl

------------------------------------------------------------------------
-- 9. inv is involutive on canonical forms.
------------------------------------------------------------------------

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical c-ε    = refl
inv-inv-canonical c-a    = refl
inv-inv-canonical c-aa   = refl
inv-inv-canonical c-aaa  = refl
inv-inv-canonical c-aaaa = refl
