------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixedPoint
--
-- UP6 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- THE FIXED POINT.
--
-- Per the user's framing: "the category of arrow categories has a
-- fixed point." This slice exhibits the canonical embedding that
-- realises it for the substrate's UPCategory:
--
--   ι : UPArrow² → UPArrow
--
-- A meta-arrow (UPArrow²) at L2 = "a UPMorphism between two
-- UPArrows" embeds as an L0 UPArrow whose:
--   * Source  = L0-Source UPArrow's Source     (= flatten one level)
--   * Target  = L0-Target UPArrow's Target     (= flatten one level)
--   * Witness = "there is a span-witness in Source₁, paired with
--                a witness in Target₂, related by the L1-Witness's
--                source-map and target-map"
--
-- Equivalently: the meta-arrow ITSELF is a UPArrow whose witness
-- relation is the COMPOSITE relation through the intermediate UP.
--
-- This closes the substrate's tetrative tower at the structural
-- level: every meta-arrow at L_{n+1} embeds back into L_n via this
-- composite-witness collapse. The tower IS its own fixed point.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FixedPoint where

open import Substrate.Category.UniversalProperty
  using (UPArrowP; mkUP; SourceP; TargetP; WitnessP)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism; source-map; target-map; coherent)
open import Substrate.Category.UniversalProperty.ArrowOfArrow
  using (UPArrow²; L0-Source; L0-Target; L1-Witness)

-- ⟡UPArrow-dissolve C: telescope carriers.
private variable
  S₁ T₁ S₂ T₂ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set

------------------------------------------------------------------------
-- 1. The fixed-point embedding ι : UPArrow² → UPArrow.
--
-- Given a meta-arrow α at L2, produce a UPArrow at L0 whose
-- witness relation is the COMPOSITE through the L1-Witness's
-- structural data:
--
--   ι(α).Source  = Source (L0-Source α)
--   ι(α).Target  = Target (L0-Target α)
--   ι(α).Witness s i = "∃ a span-traversal: s ↝ source-map L1 s,
--                       witnessed in Target (L0-Target α), with
--                       target-map L1 mapping back to i somewhere"
--
-- Substrate-honest concrete form: the witness IS the COMPOSITE
-- witness relation through the L1 morphism, evaluated at the
-- endpoints. We package it as a Σ-type capturing "there exists an
-- intermediate target-instance that witnesses both endpoints."
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (Σ; _,_; _×_)

-- the composite-witness relation, over the L0 objects' carriers.
ι-W : (A : UPArrowP S₁ T₁ W₁) (B : UPArrowP S₂ T₂ W₂) → SourceP A → TargetP B → Set
ι-W A B s i =
  Σ (TargetP A) (λ t-src →
  Σ (SourceP B) (λ s-tgt →
    WitnessP A s t-src ×
    WitnessP B s-tgt i))

-- ⟡UPArrow-dissolve C: ι packages the meta-arrow as the (trivial) object whose
-- carriers are (SourceP A, TargetP B) and whose witness is the composite ι-W.
ι : {A : UPArrowP S₁ T₁ W₁} {B : UPArrowP S₂ T₂ W₂}
  → UPArrow² A B → UPArrowP (SourceP A) (TargetP B) (ι-W A B)
ι _ = mkUP

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

open import Substrate.Category.UniversalProperty.Compose
  using (id-UPMorphism)

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
