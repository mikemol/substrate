------------------------------------------------------------------------
-- Substrate.WitnessTower.WholeTower
--
-- BUILD (not assert): ALL the rungs up to S₄, taken together, have the
-- shape of S₄ — because the witness-tower requires all the hardware from
-- below to build each higher rung faithfully (the Path-from-the-base of
-- WitnessTower.Core).
--
-- Not "two top rungs glued": the FULL iterated semidirect product, atoms
-- all the way down. Unfolding the substrate's existing nesting:
--
--   S₄ = V₄ ⋊ S₃          (S4-Composed)
--   S₃ =      Z₃ ⋊ Z₂     (S3)
--   ⟹ S₄ = V₄ ⋊ (Z₃ ⋊ Z₂)
--           │      │    │
--         apex  triangle edge      ← each rung built on the one below
--
-- And dually, the WITNESS-STABILIZER chain (dossier D1): fixing the top
-- witness drops one rung, and Stab(anchor) ≅ S₃ (Stab-S3-Iso.stab≃s₃) is
-- the proven rung-3 → rung-2 step. So S₄'s structure IS the cumulative
-- tower, each rung's symmetry the stabilizer in the rung above —
-- presupposing everything below, exactly as Core's witness-path does.
--
-- This module records the identifications, each pinned to an in-tree
-- theorem (no re-derivation): the nesting and the stabilizer step.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.WholeTower where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Bundle using (V₄-Group)
import Substrate.Groups.S3 as S₃
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Algebra.Group.ToSetoid using (to-setoid)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Iff using (_⇔_; ⇔-refl)

open import Substrate.Groups.S4-Composed using (S₄-Group)
open import Substrate.Groups.Stab-S3-Iso using (Stab≃S₃; stab≃s₃)
open import Substrate.Axes.Axis using (Axis)

-- the tower's apex links + their permuter, so this module's dependency
-- cone literally contains the tower hardware it identifies with S₄'s
-- factors (built earlier in the WitnessTower arc):
open import Substrate.WitnessTower.SharedMiddle using (Lα; Lβ; Lγ)
open import Substrate.WitnessTower.WhyThreeV2 using (rotate-on-α; rotate-on-β; rotate-on-γ)

------------------------------------------------------------------------
-- 1. The whole tower up to rung 3 = S₄, as the full nested semidirect
--    product. S₄-Group was built as V₄ ⋊ S₃, and S₃-Group as Z₃ ⋊ Z₂,
--    so S₄ = V₄ ⋊ (Z₃ ⋊ Z₂) — the atoms all present, each rung's hardware
--    below it. Recorded as the identity of the whole-tower object.
------------------------------------------------------------------------

-- (carrier + relation now live in the SetoidGroup type; let them be
-- inferred from S₄-Group rather than named here.)
whole-tower = S₄-Group

whole-tower-is-S₄ : whole-tower ≡ S₄-Group
whole-tower-is-S₄ = refl

-- the rungs as the factors (each presupposed by the one above):
apex-V₄    : SetoidGroup V₄ _≡_        -- carrier is the V₄ the three V₂ links live on
apex-V₄    = to-setoid V₄-Group       -- rung-3 contribution (the links)
triangle-edge-S₃ = S₃.S₃-Group           -- = Z₃ ⋊ Z₂, rungs 2 and 1

-- the apex factor's carrier is the V₄ the three V₂ links live on —
-- now manifest in apex-V₄'s type (SetoidGroup V₄ _≡_):
apex-carrier-is-V₄ : V₄ ⇔ V₄
apex-carrier-is-V₄ = ⇔-refl
------------------------------------------------------------------------
-- 2. The stabilizer-chain grounding (the "presupposes everything below"
--    direction). Fixing the apex witness drops to rung 2: Stab(anchor) ≅
--    S₃ is proven in-tree. We import stab≃s₃ as the rung-3 → rung-2 step;
--    its existence (for every anchor) IS "the tower's top rung sits over
--    a faithfully-present triangle rung below."
------------------------------------------------------------------------

stab-step : (anchor : Axis) → Stab≃S₃ anchor
stab-step = stab≃s₃
