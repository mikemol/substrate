------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter
--
-- ℤ/4ℤ as a Coxeter-style presentation: ⟨a | a⁴ = ε⟩.
--
-- First cyclic-of-composite-order Coxeter instance (order 4 = 2²).
-- Mirror of Substrate.Groups.Z3-Coxeter at n=4: explicit Canonical
-- constructors c-ε / c-a / c-aa / c-aaa, insert wraps at length 4
-- (c-aaa + a → c-ε), and `fourth-power-identity` plays the role of
-- Z3's `cube-identity`.
--
-- Useful theorem: `fourth-power-identity` — every element to the
-- fourth equals ε. The composite-order analog: a² is itself an order-2
-- element (a² · a² = a⁴ = ε), so Z/4 contains a non-trivial Z/2
-- subgroup.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this is the
-- substrate-native alternative to Data.Fin.Permutation / Data.Nat.DivMod
-- for representing cyclic structure at n=4. The word algebra's
-- normalize gives mod-4 reduction structurally.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Data.Empty using (⊥; ⊥-elim)
open import Relation.Nullary using (Dec; yes; no)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong; _≢_)

------------------------------------------------------------------------
-- 1. Z/4-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

data Canonical : Word Gen → Set where
  c-ε   : Canonical []
  c-a   : Canonical (a ∷ [])
  c-aa  : Canonical (a ∷ a ∷ [])
  c-aaa : Canonical (a ∷ a ∷ a ∷ [])

------------------------------------------------------------------------
-- 2. The insert step: encodes a⁴ = ε as a 4-cyclic wrap on canonical
-- forms — [] → [a] → [a,a] → [a,a,a] → [].
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert a []               = a ∷ []
insert a (a ∷ [])         = a ∷ a ∷ []
insert a (a ∷ a ∷ [])     = a ∷ a ∷ a ∷ []
insert a (a ∷ a ∷ a ∷ []) = []
insert g w                = g ∷ w  -- fallback (unreachable for Canonical inputs)

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical a c-ε   = c-a
insert-canonical a c-a   = c-aa
insert-canonical a c-aa  = c-aaa
insert-canonical a c-aaa = c-ε

------------------------------------------------------------------------
-- 3. Open ListPresentation with Z/4's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
--
-- canonical-is-fixed: trivial 4-refl enumeration.
--
-- insert-fourth-power: the a⁴ = ε relation lifted to insert level —
-- inserting `a` four times restores the input. Used by case [a,a,a]
-- of insert-append-lemma.
------------------------------------------------------------------------

canonical-is-fixed-Z4 : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed-Z4 c-ε   = refl
canonical-is-fixed-Z4 c-a   = refl
canonical-is-fixed-Z4 c-aa  = refl
canonical-is-fixed-Z4 c-aaa = refl

insert-fourth-power : (g : Gen) {w : Word Gen} → Canonical w →
                      insert g (insert g (insert g (insert g w))) ≡ w
insert-fourth-power a c-ε   = refl
insert-fourth-power a c-a   = refl
insert-fourth-power a c-aa  = refl
insert-fourth-power a c-aaa = refl

insert-append-lemma-Z4 :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-Z4 a {[]}             w₂ c-ε   = refl
insert-append-lemma-Z4 a {a ∷ []}         w₂ c-a   = refl
insert-append-lemma-Z4 a {a ∷ a ∷ []}     w₂ c-aa  = refl
insert-append-lemma-Z4 a {a ∷ a ∷ a ∷ []} w₂ c-aaa =
  sym (insert-fourth-power a (normalize-canonical w₂))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed-Z4 insert-append-lemma-Z4 public

------------------------------------------------------------------------
-- 6. Decidable equality on Canonical forms.
------------------------------------------------------------------------

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical c-ε   c-ε   = yes refl
same-canonical c-a   c-a   = yes refl
same-canonical c-aa  c-aa  = yes refl
same-canonical c-aaa c-aaa = yes refl
same-canonical c-ε   c-a   = no (λ ())
same-canonical c-ε   c-aa  = no (λ ())
same-canonical c-ε   c-aaa = no (λ ())
same-canonical c-a   c-ε   = no (λ ())
same-canonical c-a   c-aa  = no (λ ())
same-canonical c-a   c-aaa = no (λ ())
same-canonical c-aa  c-ε   = no (λ ())
same-canonical c-aa  c-a   = no (λ ())
same-canonical c-aa  c-aaa = no (λ ())
same-canonical c-aaa c-ε   = no (λ ())
same-canonical c-aaa c-a   = no (λ ())
same-canonical c-aaa c-aa  = no (λ ())

------------------------------------------------------------------------
-- 7. Inversion on canonical forms — Z/4 inversion table:
--   inv []        = []
--   inv [a]       = [a,a,a]      (a⁻¹ = a³)
--   inv [a,a]     = [a,a]        (a² is its own inverse)
--   inv [a,a,a]   = [a]          ((a³)⁻¹ = a)
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv []               = []
inv (a ∷ [])         = a ∷ a ∷ a ∷ []
inv (a ∷ a ∷ [])     = a ∷ a ∷ []
inv (a ∷ a ∷ a ∷ []) = a ∷ []
inv w                = w  -- fallback (unreachable for Canonical inputs)

inv-canonical : {w : Word Gen} → Canonical w → Canonical (inv w)
inv-canonical c-ε   = c-ε
inv-canonical c-a   = c-aaa
inv-canonical c-aa  = c-aa
inv-canonical c-aaa = c-a

------------------------------------------------------------------------
-- 8. Z/4-specific theorem: every element to the fourth equals ε.
--
-- Parallel of Z2-Coxeter's `self-inverse` and Z3-Coxeter's `cube-
-- identity`. Composes a flatten-step (bridge `((w · w) · w) · w` to
-- a flat 4-arg right-associated form) with a 4-refl enumeration on
-- Canonical w.
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
  fourth-canonical c-ε   = refl
  fourth-canonical c-a   = refl
  fourth-canonical c-aa  = refl
  fourth-canonical c-aaa = refl

fourth-power-identity : (w : Word Gen) → (((w · w) · w) · w) ≈ ε
fourth-power-identity w =
  trans (flatten-quad-self-product w)
        (fourth-canonical (normalize-canonical w))

------------------------------------------------------------------------
-- 9. Inverse-composition theorems on canonical forms.
------------------------------------------------------------------------

inv-left-canonical : {w : Word Gen} → Canonical w →
                     normalize (inv w ++ w) ≡ []
inv-left-canonical c-ε   = refl
inv-left-canonical c-a   = refl
inv-left-canonical c-aa  = refl
inv-left-canonical c-aaa = refl

inv-right-canonical : {w : Word Gen} → Canonical w →
                      normalize (w ++ inv w) ≡ []
inv-right-canonical c-ε   = refl
inv-right-canonical c-a   = refl
inv-right-canonical c-aa  = refl
inv-right-canonical c-aaa = refl

------------------------------------------------------------------------
-- 10. inv is involutive on canonical forms: inv (inv w) ≡ w.
------------------------------------------------------------------------

inv-inv-canonical : {w : Word Gen} → Canonical w → inv (inv w) ≡ w
inv-inv-canonical c-ε   = refl
inv-inv-canonical c-a   = refl
inv-inv-canonical c-aa  = refl
inv-inv-canonical c-aaa = refl
