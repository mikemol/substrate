------------------------------------------------------------------------
-- Substrate.Category.Allegory.Division.Slash
--
-- Defines: _／_
-- The RIGHT RESIDUAL of composition: (S ／ T) is the greatest R with
-- R⨾S ⊆ T.  A universally-quantified fiber, so Set₀ under --without-K.
--
-- ⟡alg6-restore: recovered from efe21483^ (ALG-6).  One lemma, one
-- elaboration unit; no barrel re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Division.Slash where


infixr 5 _／_
_／_ : {A B C : Set} → (B → C → Set) → (A → C → Set) → A → B → Set
_／_ {A} {B} {C} S T a b = (c : C) → S b c → T a c
