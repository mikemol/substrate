------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.Refinement
--
-- Defines: Refinement, mkRefinement
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.Refinement where

open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.SqsubF



-- ⟡set1-rp-refinement: Φ AND mono are PARAMETERS now — the VESTIGIAL-record pattern (UPArrowP/
-- mkUP precedent). Φ is Set-valued (set1-carrier-always-parameterize) and mono's type ∀-quantifies
-- over families ({P Q : A → Set} → … is Set₁-sorted), so as a FIELD it pins the record at Set₁;
-- as PARAMS neither raises the record's sort — the record drops Set₁→Set with an empty body.
record Refinement (A : Set) (Φ : (A → Set) → A → Set)
                  (mono : {P Q : A → Set} → P ⊑ᶠ Q → Φ P ⊑ᶠ Φ Q) : Set where
  constructor mkRefinement
