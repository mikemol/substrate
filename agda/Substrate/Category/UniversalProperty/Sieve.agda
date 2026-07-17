------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sieve
--
-- UP13 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A SIEVE on an object U is a downward-closed family of UPTerm morphisms into
-- U: a predicate `member` on terms into U, closed under precomposition.
--
-- ⟡ta-upterm + ⟡ta-upterm-L5-reflow: objects are the Set₀ alphabet O; homs are
-- UPTerm O Hom. The `member` codomain lowers Set₁ → Set (the Set₁ was only to
-- quantify over the old carrier Sets), so Sieve lowers Set₂ → Set₁; the bespoke
-- `⊤₁ : Set₁` is replaced by the Set₀ `⊤`. (O, Hom) via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sieve where

open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; _++ᵤ_)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- The Sieve record: a term-predicate closed under precomposition.
  ------------------------------------------------------------------------

  -- ⟡rc-topos (⟡set1-rerank2): `member` is a PARAMETER now (a Set-valued field
  -- pinned the record at Set₁; params never raise the sort) — a sieve's predicate
  -- is visible in its TYPE, and only the closure proof is data.
  record Sieve (U : O) (member : {V : O} → UPTerm O Hom V U → Set) : Set where
    field
      closure : {V W : O} (t : UPTerm O Hom V U) (u : UPTerm O Hom W V) →
                member t → member (u ++ᵤ t)

  open Sieve public

  ------------------------------------------------------------------------
  -- The maximal sieve (always-true predicate).
  ------------------------------------------------------------------------

  max-Sieve : (U : O) → Sieve U (λ _ → ⊤)
  max-Sieve U = record { closure = λ _ _ _ → tt }
