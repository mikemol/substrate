------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter-Strict2Monoid
--
-- V₄ packaged as a Strict2Monoid via the FromCoxeter constructor.
--
-- Demonstrates that the substrate's existing Coxeter instances
-- (V4-Coxeter in this case) lift directly to the categorical
-- Strict2Monoid primitive without any extra work — just open
-- FromCoxeter with the Core data.
--
-- This is a load-bearing demonstration: V₄ is the substrate's
-- canonical Klein four-group; surfacing it as a 1-object strict
-- 2-category names what was previously implicit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter-Strict2Monoid where
open import Substrate.Groups.Coxeter.Word using (++-assoc)

import Substrate.Groups.V4-Coxeter as V₄
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _++_; ++-identity-left; ++-identity-right)

------------------------------------------------------------------------
-- Instantiate FromCoxeter with V4-Coxeter's data.
------------------------------------------------------------------------

open import Substrate.Category.Strict2Monoid.FromCoxeter
  (Word V₄.Gen)
  _++_
  []
  (λ a b c → ++-assoc a b c)
  ++-identity-left
  ++-identity-right
  V₄.normalize
  V₄.normalize-distrib
  public

------------------------------------------------------------------------
-- After this module:
--
--   * V₄ is available as `Coxeter-Strict2Monoid : Strict2Monoid _ _`.
--   * Its 1-cells are Word V₄.Gen.
--   * Its strict composition is ++ on words.
--   * Its 2-cells are normalize-equality (≈).
--
-- The exact analog applies to Z₃-Coxeter, Z₄-Coxeter, Z₅-Coxeter,
-- FreeCyclic-Coxeter, V4-as-Z2xZ2 (DirectProduct flavor — though
-- that uses _++-prod_ privately so requires slight care). Each
-- instance lift is one open-import.
------------------------------------------------------------------------
