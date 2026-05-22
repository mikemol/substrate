------------------------------------------------------------------------
-- Substrate.Category.RuleAction.V4
--
-- The V₄ residue factor (Klein four group) — Coxeter group of order 4.
-- Indexed as Fin 4; composition lives in V4Compose.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.V4 where

data V₄ : Set where
  e α β γ : V₄
