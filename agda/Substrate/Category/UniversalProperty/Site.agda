------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Site
--
-- ⟡ta-upterm-site: the (O, Hom) scope-anchor for the UP-topos stack.
--
-- The UP topos ranges over a Set₀ object-alphabet O whose homs are the FREE
-- CATEGORY on the Hom generators — UPTerm O Hom (identity = [], composition
-- = ++ᵤ). This module fixes the telescope `module Site (O)(Hom)` and names the
-- site's hom-family + category (the reinstated UPCategory-canonical), re-exporting
-- the Set₀ term-forms so each downstream presheaf/sheaf/coverage module opens ONE
-- thing (`open Site O Hom`) instead of threading Term/Category imports separately.
--
-- This is the single anchor the O-parameterization inherits — the position the
-- flat UPArrowP object + the telescope UPTerm hom held. The ~15 topos modules
-- migrate onto it (⟡ta-upterm-L3…): objects UPArrowP S T W ↦ O, homs UPTerm ↦
-- site-hom. Additive re-export aggregator (the substrate's Phase-module pattern);
-- 0 importers today, so it cannot break the coexisting telescope stack.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Site where

open import Substrate.Category.UniversalProperty.Term
  using (UPGen; lift; UPTerm; []; _∷_; _++ᵤ_) public
open import Substrate.Category.UniversalProperty.Category
  using (UPCategory; UPCategory-canonical) public

------------------------------------------------------------------------
-- The site telescope: fix the object alphabet O and the Hom generators.
------------------------------------------------------------------------

module Site (O : Set) (Hom : O → O → Set) where

  -- The site's hom-family: the free category on the Hom generators. A downstream
  -- presheaf/cover writes its fields over `site-hom U V` (= UPTerm O Hom U V).
  site-hom : O → O → Set
  site-hom = UPTerm O Hom

  -- The site category: objects = O, homs = site-hom, id = [], ∘ = ++ᵤ — the
  -- reinstated canonical instance (UPCategory is level-polymorphic, so O : Set₀ fits).
  site-category : UPCategory O site-hom
  site-category = UPCategory-canonical O Hom
