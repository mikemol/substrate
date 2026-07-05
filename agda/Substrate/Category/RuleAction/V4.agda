------------------------------------------------------------------------
-- Substrate.Category.RuleAction.V4
--
-- The V₄ residue factor (Klein four group) — Coxeter group of order 4.
--
-- Ⓒ.v4 (2026-07-05): this WAS a local `data V₄ = e|α|β|γ` reinvention of the
-- Klein four-group carrier. It now RE-EXPORTS the substrate's canonical V₄
-- (Groups.V4) — so RuleAction's residues are the SAME group elements as
-- everywhere else (they no longer fail to interoperate across subsystems), and
-- V4Compose's composition is the canonical Groups.V4 operation (not a
-- hand-written table). Dependents (Record, V4Compose) open it unchanged
-- (constructor names e α β γ preserved).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.V4 where

open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ) public
