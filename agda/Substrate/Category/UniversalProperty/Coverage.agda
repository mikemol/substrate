------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Coverage
--
-- UP12 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Coverage on the UP-site: a family of UPTerm morphisms into an object U is a
-- COVER of U if the source objects collectively exhaust U.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; the source objects are ONE field
-- `src : Idx → O` (the ⟡ta-upterm-L3-coverage-src collapse of the old carrier-
-- families Sc/Tc/Wc + the source-UP shim — the source at i is just the object
-- src i). UPCover STAYS Set₁ (driver C: the `Idx : Set` field). (O, Hom) via the
-- enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Coverage where

open import Substrate.Category.UniversalProperty.Term
  using (UPTerm)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- UPCover: an indexed family of UPTerm morphisms into U.
  ------------------------------------------------------------------------

  record UPCover (U : O) : Set₁ where
    field
      Idx   : Set
      src   : Idx → O
      arrow : (i : Idx) → UPTerm O Hom (src i) U

  open UPCover public

  -- The source object at index i (was the UPArrowP `source-UP` shim; now just the
  -- object `src c i : O`). Kept as an alias so its importers need not rename.
  source-UP : {U : O} (c : UPCover U) (i : Idx c) → O
  source-UP c i = src c i

  ------------------------------------------------------------------------
  -- The covering condition (obligation placeholder; concrete covers discharge it).
  ------------------------------------------------------------------------

  Covering : {U : O} → UPCover U → Set₁
  Covering _ = Set
