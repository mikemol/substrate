------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.ListPresentation
--
-- Bridge from Word-based Coxeter presentations to the abstract
-- Substrate.Groups.Coxeter.Core.
--
-- Uses the self-contained Substrate.Groups.Coxeter.Word type
-- (NOT stdlib Data.List) to avoid clashing-definition friction when
-- Core re-exports the operations alongside instance-local imports.
--
-- Structure: outer module takes the per-generator atoms (Gen,
-- Canonical, canonical-ε, insert, insert-canonical), provides the
-- carrier (= Word Gen) + normalize + normalize-canonical. Inner
-- sub-module `WithLemmas` takes the per-relation proof obligations
-- (canonical-is-fixed, insert-append-lemma), derives normalize-distrib
-- by Word induction, and instantiates the abstract Core (re-exported
-- via `public`).
--
-- USERS: Substrate.Groups.Z2-Coxeter, Substrate.Groups.V4-Coxeter
-- (any Coxeter group whose presentation is naturally a Word Gen).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Groups.Coxeter.Word
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong)

module Substrate.Groups.Coxeter.ListPresentation
  (Gen : Set)
  (Canonical : Word Gen → Set)
  (canonical-ε : Canonical [])
  (insert : Gen → Word Gen → Word Gen)
  (insert-canonical :
    (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w))
  where

------------------------------------------------------------------------
-- 1. The Word-induced normalize and its canonicality.
------------------------------------------------------------------------

normalize : Word Gen → Word Gen
normalize []       = []
normalize (x ∷ xs) = insert x (normalize xs)

normalize-canonical : (w : Word Gen) → Canonical (normalize w)
normalize-canonical []       = canonical-ε
normalize-canonical (x ∷ xs) = insert-canonical x (normalize-canonical xs)

------------------------------------------------------------------------
-- 2. WithLemmas: takes the per-relation obligations + derives the
-- bridge lemmas + instantiates abstract Core.
------------------------------------------------------------------------

module WithLemmas
  (canonical-is-fixed :
    {w : Word Gen} → Canonical w → normalize w ≡ w)
  (insert-append-lemma :
    (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
    normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂)))
  where

  ----------------------------------------------------------------------
  -- 2a. Inductively-derive normalize-distrib (Core's input
  -- obligation). The intermediate lemmas are private so they don't
  -- clash with Core's own derived versions when we re-export below.
  ----------------------------------------------------------------------

  private
    normalize-idem-list :
      (w : Word Gen) → normalize (normalize w) ≡ normalize w
    normalize-idem-list w = canonical-is-fixed (normalize-canonical w)

    normalize-append-list :
      (a b : Word Gen) → normalize (a ++ b) ≡ normalize (normalize a ++ b)
    normalize-append-list [] b = refl
    normalize-append-list (x ∷ a) b =
      trans (cong (insert x) (normalize-append-list a b))
            (sym (insert-append-lemma x b (normalize-canonical a)))

    normalize-append-right-list :
      (a b : Word Gen) → normalize (a ++ b) ≡ normalize (a ++ normalize b)
    normalize-append-right-list [] b = sym (normalize-idem-list b)
    normalize-append-right-list (x ∷ a) b =
      cong (insert x) (normalize-append-right-list a b)

  normalize-distrib :
    (a b : Word Gen) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b)
  normalize-distrib a b =
    trans (normalize-append-list a b)
          (normalize-append-right-list (normalize a) b)

  ----------------------------------------------------------------------
  -- 2b. Instantiate the abstract Core.
  ----------------------------------------------------------------------

  open import Substrate.Groups.Coxeter.Core
    (Word Gen)
    _++_
    []
    ++-assoc
    Canonical
    normalize
    normalize-canonical
    canonical-is-fixed
    normalize-distrib
    public
