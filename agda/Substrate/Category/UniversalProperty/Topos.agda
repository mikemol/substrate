------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Topos
--
-- UP31 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The Grothendieck-topos record specialised to the UP-site:
-- a category of sheaves on UPCategory equipped with the
-- topos-canonical structure (cartesian-closure, subobject
-- classifier Ω, internal logic).
--
-- Substrate-honest scope: signature-bearing — each field names an
-- obligation; concrete construction proceeds at UP32-UP38.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Topos where

open import Substrate.Category.UniversalProperty.Sheaf using (UPSheaf)

------------------------------------------------------------------------
-- 1. The UP-Topos record (signature).
------------------------------------------------------------------------

record UPTopos : Set₃ where
  field
    Sh-Obj  : Set₂           -- UPSheaf is in Set₂
    -- Cartesian-closed structure on Sh-Obj:
    has-product-stated     : Set
    has-exponential-stated : Set
    -- Finite limits:
    finite-limits-stated   : Set
    -- Subobject classifier Ω as a designated UPSheaf:
    Ω-sheaf-stated         : Set
    -- Internal logic surface:
    internal-logic-stated  : Set

open UPTopos public

------------------------------------------------------------------------
-- 2. Capstone for UP31.
--
-- UPTopos record lands. UP32 supplies Ω explicitly; UP33 truth
-- values for UP-membership; UP34 internal logic surface;
-- UP38 the canonical UPTopos = Topos(UPSite).
------------------------------------------------------------------------
