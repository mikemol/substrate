------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.AxisDualLine
--
-- Slice 1.5 of the shadow-architecture arc. The axis-to-dual-line
-- map: each of the three coordinate axes e_i corresponds to the
-- Fano line consisting exactly of those points whose i-th coordinate
-- is 𝟘. From the document's Increment 1:
--
--   axis e₁ ↔ L₃ = {010, 001, 011}  — "signatures not on e₁"
--   axis e₂ ↔ L₂ = {100, 001, 101}  — "signatures not on e₂"
--   axis e₃ ↔ L₁ = {100, 010, 110}  — "signatures not on e₃"
--
-- Note the inversion: axis indexed 0 (= e₁) maps to L₃, not L₁. This
-- is the duality at the axis level — the line dual to an axis is the
-- hyperplane orthogonal to that axis, i.e., the line consisting of
-- signatures whose i-th coordinate vanishes.
--
-- Forward direction proved here (every point on the dual line has
-- the corresponding coordinate 𝟘). The reverse direction (every
-- point with coordinate 𝟘 is on the dual line) is also true and
-- holds by enumeration, but is deferred to a later slice if needed
-- — the forward direction is what the document's Increment 1 uses.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.AxisDualLine where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₂₃)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2 using (F₂; 𝟘)
open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.SelfReference using (_on_)

------------------------------------------------------------------------
-- 1. Axis-dual map.
--
-- The axis index 0 corresponds to e₁'s coordinate position (the
-- first F₂³ slot), and the dual line of e₁ is L₃ = {e₂, e₃, e₂₃} —
-- the three signatures with 𝟘 in the first slot.
------------------------------------------------------------------------

Axis : Set
Axis = Fin 3

pattern ax₁ = zero
pattern ax₂ = suc zero
pattern ax₃ = suc ₁

axis-dual : Axis → FanoLine
axis-dual ax₁ = L₃
axis-dual ax₂ = L₂
axis-dual ax₃ = L₁

------------------------------------------------------------------------
-- 2. Forward: every point on the dual line has the corresponding
-- coordinate 𝟘.
--
-- The three explicit facts below cover the three axes. Each closes
-- by case analysis on which of the three points on the dual line p
-- equals (a 3-way disjunction), then `refl` because lookup reduces
-- on concrete F₂³ vectors.
--
-- Notation: `coord i p` = the i-th component of point-to-vec p.
------------------------------------------------------------------------

coord : Axis → Point → F₂
coord i p = lookup (point-to-vec p) i

axis-1-dual-coord-zero :
  ∀ (p : Point) → p on axis-dual ax₁ → coord ax₁ p ≡ 𝟘
axis-1-dual-coord-zero p₀₁₀ (inj₁ refl)        = refl
axis-1-dual-coord-zero p₀₀₁ (inj₂ (inj₁ refl)) = refl
axis-1-dual-coord-zero p₀₁₁ (inj₂ (inj₂ refl)) = refl

axis-2-dual-coord-zero :
  ∀ (p : Point) → p on axis-dual ax₂ → coord ax₂ p ≡ 𝟘
axis-2-dual-coord-zero p₁₀₀ (inj₁ refl)        = refl
axis-2-dual-coord-zero p₀₀₁ (inj₂ (inj₁ refl)) = refl
axis-2-dual-coord-zero p₁₀₁ (inj₂ (inj₂ refl)) = refl

axis-3-dual-coord-zero :
  ∀ (p : Point) → p on axis-dual ax₃ → coord ax₃ p ≡ 𝟘
axis-3-dual-coord-zero p₁₀₀ (inj₁ refl)        = refl
axis-3-dual-coord-zero p₀₁₀ (inj₂ (inj₁ refl)) = refl
axis-3-dual-coord-zero p₁₁₀ (inj₂ (inj₂ refl)) = refl

------------------------------------------------------------------------
-- 3. The three axes form one S₃-orbit (Increment 1's structural
-- claim). Operationally: axis-dual is a bijection Axis ↔
-- {weight-1 lines = wt-1 orbit of FanoLine}. This is a recapitulation
-- of `Substrate.ShadowArchitecture.Weight`'s line-orbit-1 set
-- {L₁, L₂, L₃} as the image of axis-dual.
--
-- Stated as a section-of-the-Weight-orbit-image; the orbit-fact
-- itself lives in Weight.agda.
------------------------------------------------------------------------

open import Substrate.ShadowArchitecture.Weight
  using (line-orbit; wt-1)

axis-dual-lands-wt-1 : ∀ (i : Axis) → line-orbit (axis-dual i) ≡ wt-1
axis-dual-lands-wt-1 ax₁ = refl
axis-dual-lands-wt-1 ax₂ = refl
axis-dual-lands-wt-1 ax₃ = refl
