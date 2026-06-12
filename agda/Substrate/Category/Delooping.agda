------------------------------------------------------------------------
-- Substrate.Category.Delooping
--
-- THE Algebra → Category bridge (the first real one). The substrate's
-- `Algebra.*` and `Category.*` are PARALLEL record hierarchies with no
-- connecting morphism ([[project-bridge-indexes-algebra-category]]):
-- Algebra imports zero Category, and a structure grounded in `Algebra.Monoid`
-- (e.g. `Cocycles/V4Signature/S4GroupIso`'s `TotalSpace-Monoid`) sits OFF the
-- categorical spine — a true positive the categorical-grounding advisory
-- flags but cannot fix per-module, because the gap is at the hierarchy level.
--
-- The classical fix is DELOOPING: every monoid M is the one-object category
-- BM (the "classifying" / one-object groupoid when M is a group) — one object
-- ⋆, hom(⋆,⋆) = M, identity = ε, composition = the monoid op. This module
-- builds that functor on objects:
--
--   deloop : Algebra.Monoid A → Category.CategoryOf
--
-- so any `Algebra.Monoid` is now provably a substrate-named `CategoryOf`,
-- putting the Algebra hierarchy ON the categorical spine. Composition is
-- taken as `compose g f = f · g` to match the substrate's existing CategoryOf
-- instances (Markov / Conjugate / Witness term categories), so the unit laws
-- pair as left-id = ε-right, right-id = ε-left and associativity transfers
-- directly (no `sym`).
--
-- A leaf module: nothing in Category.* imports it, so it introduces no
-- Category→Algebra dependency in the core — it is the bridge, used downstream.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Delooping where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)
open import Substrate.Algebra.Monoid    using (Monoid; ε; ε-left; ε-right; semigroup)
open import Substrate.Category.CategoryOf using (CategoryOf)

------------------------------------------------------------------------
-- deloop M = BM : the one-object category of a monoid.
--   Obj      = ⊤            (the single object ⋆)
--   Mor ⋆ ⋆  = A            (the carrier — every element is an endo of ⋆)
--   id       = ε
--   compose g f = f · g     (diagrammatic order, matching the term cats)
--   left-id  = ε-right      (compose (id ⋆) f = f · ε ≡ f)
--   right-id = ε-left       (compose f (id ⋆) = ε · f ≡ f)
--   assoc    = ·-assoc      ((f · g) · h ≡ f · (g · h))
------------------------------------------------------------------------

deloop : {A : Set} → Monoid A → CategoryOf
deloop {A} mon = record
  { Obj      = ⊤
  ; Mor      = λ _ _ → A
  ; id       = λ _ → ε mon
  ; compose  = λ g f → f ∙ g
  ; left-id  = ε-right mon
  ; right-id = ε-left mon
  ; assoc    = ·-assoc (semigroup mon)
  }
  where
    _∙_ : A → A → A
    _∙_ = Magma._·_ (magma (semigroup mon))
