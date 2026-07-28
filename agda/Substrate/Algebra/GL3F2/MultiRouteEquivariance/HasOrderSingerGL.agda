------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSingerGL
--
-- singer-GL has order 7 in GL(3, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSingerGL where

open import Substrate.Algebra.GL3F2 using (HasOrder-GL)
open import Substrate.Algebra.GL3F2.SingerOrder.HasOrder using (HasOrder-singer)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerGL using (singer-GL)

HasOrder-GL-singer : HasOrder-GL singer-GL 7
HasOrder-GL-singer = HasOrder-singer
