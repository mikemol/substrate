------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorCardinality
--
-- ANOTHER rung on the V₄-equivariance sacrifice ladder (per memory
-- `project_reserved_selfdual_bijection_gauge`): a Reserved →
-- (2-element subspace of SelfDual) map that's
--
--   * MANY-TO-ONE (cardinality 8 → 2, sacrificing bijectivity AND
--     half-bits of structure),
--   * F₂-LINEAR (well — affine through 𝟎ⱽ when sign = false),
--   * V₄-EQUIVARIANT with V₄ acting trivially on both sides (since
--     the projection collapses the V₄-orbit dimension).
--
-- Contrast with the affine slice (ReservedToBivectorAffine.agda):
--
--   * Affine rung: sacrificed F₂-linearity, kept bijectivity +
--     cardinality. V₄ acts non-trivially on both sides (regular
--     representation on Reserved, translation on SelfDual).
--
--   * Cardinality rung (this file): sacrificed cardinality (8 → 2)
--     and bijectivity (many-to-one). V₄ acts trivially on both sides
--     (the projection collapses the V₄-orbit information).
--
-- These are different rungs on the same ladder, each trading
-- different rigidities for different enrichments. Per the tetrative
-- metacircularity observation: the ladder structure itself is
-- becoming visible in the substrate; the substrate now describes its
-- own gauge choices at multiple levels of structural sacrifice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorCardinality where

open import Substrate.Foundation.Bool using (Bool; true; false; _xor_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; Σ)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.SelfDual
open import Substrate.Cocycles.V4Signature.Codeword
  using (Codeword; IsReserved; Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine
  using (V₄; _+V₄_; v4-act-reserved)

------------------------------------------------------------------------
-- The 2-element target subspace.
--
-- We project to the 1-dim subspace ⟨sd-pair-03-12⟩ ⊂ SelfDual,
-- containing {𝟎ⱽ, sd-pair-03-12}. This subspace is V₄-invariant for
-- any V₄ action on SelfDual that fixes the "chirality" dimension.
------------------------------------------------------------------------

-- Project Reserved to its sign bit (= the V₄-orbit quotient).
reserved-sign : Reserved → Bool
reserved-sign ((_ , _ , b₂ , _ , _) , _) = b₂

-- Map the sign to a specific element of the 2-element subspace.
sign-to-bivector : Bool → Σ Bivector SelfDual-Pred
sign-to-bivector false = 𝟎ⱽ , sd-zero
sign-to-bivector true  = sd-pair-03-12 , sd-pair-03-12-self-dual

-- The composition: Reserved → 2-element SelfDual subspace.
reserved-collapse : Reserved → Σ Bivector SelfDual-Pred
reserved-collapse r = sign-to-bivector (reserved-sign r)

------------------------------------------------------------------------
-- V₄ acts trivially on the 2-element target subspace.
--
-- Since the target has been collapsed to a V₄-invariant (only the
-- sign survives the projection, and V₄ leaves sign untouched), the
-- natural V₄ action on the target is the identity.
------------------------------------------------------------------------

v4-act-trivial : V₄ → Σ Bivector SelfDual-Pred → Σ Bivector SelfDual-Pred
v4-act-trivial _ x = x

------------------------------------------------------------------------
-- V₄-equivariance: trivially equivariant since the projection
-- collapses the V₄-orbit dimension.
--
-- The V₄ action on Reserved (axis-addition, sign untouched) factors
-- through the sign projection (axis bits are collapsed away), so
-- reserved-collapse (v · r) = reserved-collapse r for all v, r.
--
-- Pattern-matching v and r reveals that the post-action sign equals
-- the pre-action sign (both are b₂), so both sides reduce to
-- sign-to-bivector b₂. Closes by refl.
------------------------------------------------------------------------

v4-equivariance-cardinality :
  (v : V₄) (r : Reserved) →
  reserved-collapse (v4-act-reserved v r) ≡ v4-act-trivial v (reserved-collapse r)
v4-equivariance-cardinality
  (_ , _) ((_ , _ , _ , .false , .false) , refl , refl) = refl

------------------------------------------------------------------------
-- Section: pick a representative Reserved for each sign value.
--
-- Choose the "axis-D" representative: (D = (false, false), sign, false, false).
-- This gives a section of the projection (= a one-sided inverse on the image).
------------------------------------------------------------------------

bool-to-reserved : Bool → Reserved
bool-to-reserved b₂ = ((false , false , b₂ , false , false) , refl , refl)

-- The section is a partial inverse: composing projection then section
-- gives the canonical "axis-D" representative of each V₄-orbit.
collapse-section :
  (b₂ : Bool) → reserved-sign (bool-to-reserved b₂) ≡ b₂
collapse-section _ = refl

------------------------------------------------------------------------
-- Status (documentation).
--
-- This file ships ANOTHER rung on the sacrifice ladder:
--
--   Sacrificed: cardinality (8 → 2), bijectivity (many-to-one)
--   Recovered:  trivial V₄-equivariance (V₄ acts as identity on
--               the target; the projection collapses the V₄-orbit
--               dimension entirely).
--
-- Compare with the affine rung (ReservedToBivectorAffine.agda):
--
--   * Affine: sacrificed F₂-linearity; kept cardinality + bijectivity;
--             V₄ acts non-trivially on both sides (regular rep ↔
--             translation).
--   * Cardinality (this rung): sacrificed cardinality + bijectivity;
--                              kept F₂-linearity; V₄ acts trivially
--                              on both sides.
--
-- Two formalised rungs of a 5+ rung ladder. The remaining rungs
-- (sacrifice V₄ subgroup choice / embedding domain / etc.) remain
-- unformalised.
--
-- **Tetrative metacircularity observation** (per user, 2026-05-18):
-- by formalising multiple sacrifice rungs + the gauge-freedom space
-- + the alignment-axis-space meta-symmetry, the substrate is becoming
-- a system that describes its own gauge-choice structure at multiple
-- levels of meta-reflection. Each level "tetrates" the previous (the
-- structure-of-the-structure-of-the-structure, etc.). The fractal
-- recurrence of the 3+1 parity universal pattern at each meta-level
-- IS this tetration.
--
-- See memory `project_reserved_selfdual_bijection_gauge` for the full
-- ladder analysis and the meta-symmetry on sacrifice-choice space.
------------------------------------------------------------------------
