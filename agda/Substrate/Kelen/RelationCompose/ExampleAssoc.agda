------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose.ExampleAssoc
--
-- Defines: example-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.RelationCompose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose.ExampleAssoc where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.Single
open import Substrate.Foundation.Eq
open import Substrate.Kelen.RelationCompose.Preamble
open import Substrate.Kelen.RelationCompose.Comp
open import Substrate.Kelen.RelationCompose.CompAssoc



-- Associativity check at concrete values.
example-assoc :
  ((single la ∘ᴿ single pa) ∘ᴿ single jana)
    ≡ (single la ∘ᴿ (single pa ∘ᴿ single jana))
example-assoc = ∘ᴿ-assoc (single la) (single pa) (single jana)
