------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.PrimeDivisors
--
-- The three orders cover all prime divisors of |GL(3, F₂)| = 168:
--   168 = 2³ · 3 · 7
--   swap01-GL has order 2 (prime divisor of 2³)
--   cycle3-GL has order 3 (the prime divisor 3)
--   singer-GL has order 7 (the prime divisor 7)
--
-- This is the constructive HYPOTHESIS of the multi-route theorem:
-- three generators with orders covering all prime divisors of |G|.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.PrimeDivisors where

open import Substrate.Algebra.GL3F2 using (HasOrder-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL          using (swap01-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSwap01GL  using (HasOrder-GL-swap01)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL          using (cycle3-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderCycle3GL  using (HasOrder-GL-cycle3)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL          using (singer-GL)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSingerGL  using (HasOrder-GL-singer)

prime-divisor-2 : HasOrder-GL swap01-GL 2
prime-divisor-2 = HasOrder-GL-swap01

prime-divisor-3 : HasOrder-GL cycle3-GL 3
prime-divisor-3 = HasOrder-GL-cycle3

prime-divisor-7 : HasOrder-GL singer-GL 7
prime-divisor-7 = HasOrder-GL-singer
