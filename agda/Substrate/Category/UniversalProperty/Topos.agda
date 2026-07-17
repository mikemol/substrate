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

-- ⟡set1-rp-uptopos: the VESTIGIAL-record pattern (UPArrowP/mkUP precedent) — all six Set-valued
-- fields become PARAMS (they never depended on each other), the body is empty, and params don't
-- raise the sort: Set₂ → Set. Projections had zero external uses (verified), so no shims.
-- ⟡rc-topos: Sh-Obj lowers Set₁ → Set (Agda is non-cumulative; UPSheaf
-- now genuinely lives at Set — see Sheaf.agda — so Sh-Obj must too, else
-- no Set-level UPSheaf instantiation could ever inhabit it).
record UPTopos (Sh-Obj : Set)
               (has-product-stated has-exponential-stated
                finite-limits-stated Ω-sheaf-stated internal-logic-stated : Set) : Set where
  constructor mkUPTopos

------------------------------------------------------------------------
-- 2. Capstone for UP31.
--
-- UPTopos record lands. UP32 supplies Ω explicitly; UP33 truth
-- values for UP-membership; UP34 internal logic surface;
-- UP38 the canonical UPTopos = Topos(UPSite).
------------------------------------------------------------------------
