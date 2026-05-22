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

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Operations public
  using (v4-cover; v4×v4-cover; v4×v4×v4-cover)

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

------------------------------------------------------------------------
-- Constructor-cover combinator for Axis. Mirror of fin-cover for the
-- 4-element Axis enumeration. Heterogeneous payload via 4 separate
-- refls (each refl infers its own implicit {x}).
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (_×_; _,_)

axis-cover :
  ∀ {ℓ} (P : Axis → Set ℓ) →
  P D × P C × P S × P W →
  ∀ a → P a
axis-cover _ (p , _ , _ , _) D = p
axis-cover _ (_ , p , _ , _) C = p
axis-cover _ (_ , _ , p , _) S = p
axis-cover _ (_ , _ , _ , p) W = p

------------------------------------------------------------------------
-- v4-cover / v4×v4-cover / v4×v4×v4-cover are sourced from
-- Substrate.Groups.V4.Operations and re-exported above. The
-- axis-side product cover is the analogous composition for Axis.
------------------------------------------------------------------------

axis×axis-cover :
  ∀ {ℓ} (P : Axis → Axis → Set ℓ) →
  (P D D × P D C × P D S × P D W) ×
  (P C D × P C C × P C S × P C W) ×
  (P S D × P S C × P S S × P S W) ×
  (P W D × P W C × P W S × P W W) →
  ∀ a x → P a x
axis×axis-cover P rows a x =
  axis-cover (P a)
    (axis-cover (λ a' → P a' D × P a' C × P a' S × P a' W) rows a)
    x

axis-of-v-v-of-axis : (a : Axis) → axis-of-v (v-of-axis a) ≡ a
axis-of-v-v-of-axis = axis-cover _ (refl , refl , refl , refl)

v-of-axis-axis-of-v : (v : V₄) → v-of-axis (axis-of-v v) ≡ v
v-of-axis-axis-of-v = v4-cover _ (refl , refl , refl , refl)

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
