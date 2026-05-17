------------------------------------------------------------------------
-- Substrate.Axes
--
-- The four CDSW axes — Compute, Data, State, Workspace. These are
-- substrate-architectural categories naming what every operation
-- engages with (per catalog/cocycles.md § CY-8). The choice of
-- specific letters and order is a labelling convention; downstream
-- code should treat AXES as parametric and not depend on the
-- specific encoding.
--
-- Architecture (per [[feedback-v4-typeclass-architecture]] +
-- [[feedback-composable-primitives-over-flat-enumeration]]):
-- Axis is a V₄-torsor anchored at D — the v-of-axis / axis-of-v
-- bijection IS the type-foundation, and act-axis is defined
-- structurally through V₄ multiplication rather than enumeratively.
-- Downstream code gets act-axis-as-V₄-mult as a DEFINITIONAL
-- equality (no bridging lemma needed). V₄'s algebra is now backed
-- by Substrate.Groups.V4-Coxeter (Coxeter presentation framework);
-- V4-Generic + V4-Index are retired.
--
-- This module exposes the type, the V₄ bijection (with round-trips),
-- and the V₄ axis-swap action, shared by Substrate.Cocycles.
-- V4Signature and Substrate.Groups.S4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes where

open import Relation.Binary.PropositionalEquality using (_≡_; refl)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)

------------------------------------------------------------------------
-- The four axes.
------------------------------------------------------------------------

data Axis : Set where
  D C S W : Axis

------------------------------------------------------------------------
-- Axis ↔ V₄ bijection. Axis is a V₄-torsor anchored at D:
--   D ↔ e (identity)
--   C ↔ α  (DC)(SW)
--   S ↔ β  (DS)(CW)
--   W ↔ γ  (DW)(CS)
------------------------------------------------------------------------

v-of-axis : Axis → V₄
v-of-axis D = e
v-of-axis C = α
v-of-axis S = β
v-of-axis W = γ

axis-of-v : V₄ → Axis
axis-of-v e = D
axis-of-v α = C
axis-of-v β = S
axis-of-v γ = W

axis-of-v-v-of-axis : (a : Axis) → axis-of-v (v-of-axis a) ≡ a
axis-of-v-v-of-axis D = refl
axis-of-v-v-of-axis C = refl
axis-of-v-v-of-axis S = refl
axis-of-v-v-of-axis W = refl

v-of-axis-axis-of-v : (v : V₄) → v-of-axis (axis-of-v v) ≡ v
v-of-axis-axis-of-v e = refl
v-of-axis-axis-of-v α = refl
v-of-axis-axis-of-v β = refl
v-of-axis-axis-of-v γ = refl

------------------------------------------------------------------------
-- V₄ action on Axis — defined STRUCTURALLY through V₄ multiplication.
--
--   act-axis v x = axis-of-v (v V4.· v-of-axis x)
--
-- Under this definition, act-axis-as-V₄-mult v x ≡ refl (the action
-- IS the V₄-torsor multiplication, by construction). Concrete-input
-- reductions chain through V₄'s 4-ctor Cayley table (now backed by
-- V4-Coxeter via the bijection in V4.agda), so `act-axis α D ≡ C`
-- etc. remain definitional. Variable-input reductions
-- (`act-axis e x ≡ x` etc.) compose V₄'s group axioms (ε-left,
-- ·-assoc, ...) — see act-axis-id in Substrate.Groups.V4-Embedding.
------------------------------------------------------------------------

act-axis : V₄ → Axis → Axis
act-axis v x = axis-of-v (v V4.· v-of-axis x)
