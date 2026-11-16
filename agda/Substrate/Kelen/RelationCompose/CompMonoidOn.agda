------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.CompMonoidOn
--
-- Defines: ∘ᴿ-MonoidOn
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.CompMonoidOn where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Op
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
open import Substrate.Foundation.Eq
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp
open import Substrate.Kelen.RelationCompose.CompIdentityL
open import Substrate.Kelen.RelationCompose.CompIdentityR
open import Substrate.Kelen.RelationCompose.CompAssoc



------------------------------------------------------------------------
-- 6. Capstone.
--
-- The Kēlen word-level relation composition is the free monoid on
-- the four relationals. Per [[project-language-as-free-construction-classification]]
-- this puts Kēlen's free-relation cell on the same footing as
-- Lojban's free-monoid cell AT THE FREE LEVEL; the linguistic
-- distinction is in how the structure is INTERPRETED (relations vs.
-- functions), not in the free-construction shape.
--
-- Deferred for future arcs:
--   * Semantic relation composition (Rel-category morphisms)
--   * Dagger structure (relation reversal)
--   * Residuals / Galois connections
------------------------------------------------------------------------

------------------------------------------------------------------------
-- GROUNDED: (KelenWord, _∘ᴿ_, ε) IS a substrate-named `MonoidOn` — the free
-- relation monoid on the relationals, an instance of the word-algebra center's
-- free-monoid (Category.FreeUniversalProperty.FreeMonoid; cf. its `word-monoid`
-- for any `Word Gen`). The bare laws above witness the named primitive.
------------------------------------------------------------------------

∘ᴿ-MonoidOn : MonoidOn KelenWord
∘ᴿ-MonoidOn = record
  { ε       = ε
  ; _∙_     = _∘ᴿ_
  ; ∙-assoc = ∘ᴿ-assoc
  ; ε-left  = ∘ᴿ-identityˡ
  ; ε-right = ∘ᴿ-identityʳ
  }
