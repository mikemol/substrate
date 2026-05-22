------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance
--
-- S5 of the multi-route equivariance arc
-- ([[multi-route-equivariance-recovery]] +
-- [[klein-quartic-kinematic-anatomy]]). File-per-lemma:
--
--   Swap01GL           — Sylow-2 generator as GL3F2
--   HasOrderSwap01GL   — order 2 witness
--   Cycle3Inv          — cycle3² inverse helper
--   Cycle3GL           — Sylow-3 generator as GL3F2
--   HasOrderCycle3GL   — order 3 witness
--   SingerInv          — singer⁶ inverse helper
--   SingerGL           — Sylow-7 generator as GL3F2
--   HasOrderSingerGL   — order 7 witness
--   PrimeDivisors      — orders cover prime divisors of 168
--
-- This module packages the three Sylow-canonical generators
-- (swap01-Linear, cycle3-Linear, singer-Linear) as full GL3F2 values
-- with verified inverse witnesses, then states the joint-generation
-- hypothesis: the three orders (2, 3, 7) cover all prime divisors of
-- |GL(3, F₂)| = |PSL(2, 7)| = 168.
--
-- Joint-generation theorem (META, justified by classical group theory):
--
--   ⟨swap01-GL, cycle3-GL, singer-GL⟩ = GL(3, F₂)
--
-- Justification chain: PSL(2, 7) is a simple group of order 2³·3·7;
-- the three generators witness elements of every prime order, and no
-- proper subgroup of PSL(2, 7) can contain all three (such a subgroup
-- would have order divisible by 42, giving index 4, but PSL(2, 7)'s
-- smallest non-trivial faithful permutation degree is 5).
--
-- Full constructive verification (enumeration of the 168-element
-- generated subgroup) is OUT of scope for this slice; queued as a
-- finite-check follow-on.
--
-- Per [[reserved-selfdual-bijection-gauge]]: the atlas of three
-- Sylow charts inherits GL(3, F₂)-equivariance JOINTLY via PSL(2, 7)'s
-- simplicity, even though no single chart carries it. The original
-- sacrifice ladder applies per chart; the atlas-of-charts is the
-- operational mechanism for the V₄-equivariance closure.
--
-- Per [[kinematic-gauge-sacrifice-catalog]]: the 12+ CV-joint family
-- members are 12+ kinematic embodiments of this atlas-of-charts
-- pattern — each joint is one chart within the full GL(3, F₂)-
-- equivariant atlas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance where

open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL          public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSwap01GL  public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3Inv         public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL          public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderCycle3GL  public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerInv         public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL          public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSingerGL  public
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.PrimeDivisors     public
