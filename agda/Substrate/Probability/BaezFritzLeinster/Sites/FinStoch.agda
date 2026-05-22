------------------------------------------------------------------------
-- Substrate.Probability.BaezFritzLeinster.Sites.FinStoch
--
-- Concrete site: the BFL entropy functor on FinStoch.
--
-- Per BFL: Shannon entropy is the unique (up to scale) functor from
-- the category of finite probability spaces (with information-losing
-- maps) to (ℝ≥0, +) satisfying functoriality + convex-compatibility +
-- chain rule.
--
-- For the substrate's ℚ-valued realisation: the BFL functor sends
-- a finite-probability space to its ℚ-valued Shannon entropy.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.BaezFritzLeinster.Sites.FinStoch where

open import Substrate.Probability.BaezFritzLeinster
open import Substrate.Probability.Entropy.Sites.QFin using (ℚ-EntropyFunctor)

------------------------------------------------------------------------
-- The BFL entropy functor at ℚ-valued FinStoch entropy.

ℚ-FinStoch-BFL : BFLEntropyFunctor
ℚ-FinStoch-BFL = record
  { EF = ℚ-EntropyFunctor
  }

------------------------------------------------------------------------
-- Per [[expose-generator-not-orbit]]: BFL functoriality IS the
-- generator; per-distribution entropy values are orbits.
