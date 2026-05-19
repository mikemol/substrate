------------------------------------------------------------------------
-- Substrate.Groups.FreeCyclic-Coxeter
--
-- The free monoid on one generator, presented as a Coxeter group with
-- NO relations. Plays the role of ℕ (count of generator applications)
-- in the substrate's Coxeter framework.
--
-- Structurally: ⟨a | (no relations)⟩. Every word in {a}* is in
-- canonical form; normalize is the identity. The element `a` has
-- INFINITE order (no aⁿ = ε relation).
--
-- Used by: the cyclic-cover construction (this module's primary
-- purpose). For a cyclic group Z/n, the universal cover is the
-- "FreeCyclic + Z/n" 2-D structure via DirectProduct — phase from
-- Z/n, cycle counter from FreeCyclic.
--
-- Per the 2-D word algebra arc: this is the "cycle counter" axis.
-- The phase axis is one of the existing Zₙ-Coxeter instances; the
-- cycle counter has no wraparound (counts how many full cycles deep).
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: substrate-native
-- representation of ℕ within the Coxeter framework. Avoids needing
-- to bridge ℕ as a separate algebraic structure.
--
-- Per [[feedback-categorical-name-first]]: this IS the free monoid on
-- one generator. Coxeter framing surfaces the "no-relation" case as
-- a valid Coxeter instance, completing the Coxeter family (Z/2 with
-- a² = ε, Z/3 with a³ = ε, ..., Z/∞ = FreeCyclic with NO relation).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.FreeCyclic-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong; trans; sym)

------------------------------------------------------------------------
-- 1. FreeCyclic-specific data.
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

-- Every word is canonical (no relations to satisfy).
data Canonical : Word Gen → Set where
  c-any : (w : Word Gen) → Canonical w

------------------------------------------------------------------------
-- 2. The insert step: cons (no wraparound, since no relation).
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert g w = g ∷ w

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical g (c-any w) = c-any (g ∷ w)

------------------------------------------------------------------------
-- 3. Open ListPresentation with FreeCyclic's atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical (c-any []) insert insert-canonical public

------------------------------------------------------------------------
-- 4. Per-relation obligations.
--
-- canonical-is-fixed: normalize is identity by induction on the word.
-- insert-append-lemma: refl (insert just conses).
------------------------------------------------------------------------

canonical-is-fixed-Free : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed-Free {w = []}     (c-any _) = refl
canonical-is-fixed-Free {w = x ∷ xs} (c-any _) =
  cong (x ∷_) (canonical-is-fixed-Free {w = xs} (c-any xs))

insert-append-lemma-Free :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-Free g w₂ _ = refl

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed-Free insert-append-lemma-Free public

------------------------------------------------------------------------
-- 6. The "infinite-order" non-theorem: there is NO k > 0 with aᵏ = ε.
--
-- The FreeCyclic group's defining feature: a's order is infinite.
-- We document this as a contrast to Zₙ-Coxeter's nth-power-identity.
-- No proof needed (the absence of the relation IS the content).
--
-- For substrate purposes, FreeCyclic's element `a ∷ []` has no
-- finite order. Iterating insert a gives ever-longer words, none
-- reducing to []. This is the "cycle counter never wraps" property
-- of the 2-D word algebra's cycle axis.
------------------------------------------------------------------------
