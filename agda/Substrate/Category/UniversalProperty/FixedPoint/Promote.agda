------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixedPoint.Promote
--
-- Defines: promote
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.FixedPoint; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FixedPoint.Promote where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Source
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Target
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2Morphism
-- ⚑ duplicate `variable` block deleted; `ArrowOfArrow.UPArrow2` (imported above)
-- owns these. Fifth and last module in this cluster carrying the copied preamble.
open import Substrate.Foundation.Product
open import Substrate.Category.UniversalProperty.Compose.ComposeUPMorphism
open import Substrate.Category.UniversalProperty.Compose.IdUPMorphism
open import Substrate.Category.UniversalProperty.FixedPoint.Op



------------------------------------------------------------------------
-- 2. The structural reading.
--
-- ι makes explicit: every UP-MORPHISM between two UPs is ITSELF a
-- UP. The substrate's category of universal properties is closed
-- under "promote a morphism to an object via composite-witness."
--
-- Formally, this is the FIXED-POINT property the user invoked:
--   the arrow category of UPCategory embeds canonically into
--   UPCategory itself. The embedding ι is the witness.
--
-- The iteration is self-similar:
--   ι : UPArrow²  → UPArrow
--   ι² : UPArrow⁴ → UPArrow²  (= UPArrow via the previous step)
--   ι³ : UPArrow⁸ → UPArrow⁴
--   ...
-- Every meta-level collapses down by one application of ι. The
-- substrate's [[tetrative-metacircularity]] is exactly the staging
-- of this collapse across structural depths.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 3. The reverse direction (not yet a left-inverse; signature).
--
-- A UPArrow at L0 is NOT automatically a UPArrow², because to
-- promote a single UP back up to an L2 meta-arrow we need to
-- choose two L0 UPs and a UPMorphism between them. The
-- self-promotion via the identity UPMorphism IS the canonical
-- lift; one direction of the fixed-point claim.
------------------------------------------------------------------------


promote : (U : UPArrowP S₁ T₁ W₁) → UPArrow² U U
promote U = record
  { L1-Witness = id-UPMorphism U
  }

------------------------------------------------------------------------
-- 4. Capstone for UP6.
--
-- The fixed-point pair (ι, promote) lands. The substrate's
-- UP-category is now exhibited as having the arrow-of-arrow
-- structure folded back via ι, and the L0 → L2 lift via promote.
-- Together they witness the metacircularity of UPCategory as an
-- arrow-of-arrow category.
--
-- UP7-UP10 close Phase 1: examples (UP7), Cat embedding (UP8),
-- terminal object (UP9), Phase-1 capstone (UP10).
------------------------------------------------------------------------
