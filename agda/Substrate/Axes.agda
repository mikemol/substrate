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
-- This module exposes the type and the V_4 axis-swap action, both
-- shared by Substrate.Cocycles.V4Signature and Substrate.Groups.S4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes where

open import Substrate.Groups.V4 using (V₄; e; α; β; γ)

------------------------------------------------------------------------
-- The four axes.
------------------------------------------------------------------------

data Axis : Set where
  D C S W : Axis

------------------------------------------------------------------------
-- V_4 action on a single axis.
--   e — identity
--   α — (DC)(SW) double-transposition
--   β — (DS)(CW) double-transposition
--   γ — (DW)(CS) double-transposition
--
-- Used by V4Signature (signature componentwise action) and by the
-- V_4 → S_4 embedding (each V_4 element becomes a permutation of
-- Axis).
------------------------------------------------------------------------

act-axis : V₄ → Axis → Axis
act-axis e x = x
act-axis α D = C
act-axis α C = D
act-axis α S = W
act-axis α W = S
act-axis β D = S
act-axis β C = W
act-axis β S = D
act-axis β W = C
act-axis γ D = W
act-axis γ C = S
act-axis γ S = C
act-axis γ W = D
