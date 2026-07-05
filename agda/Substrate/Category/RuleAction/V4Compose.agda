------------------------------------------------------------------------
-- Substrate.Category.RuleAction.V4Compose
--
-- _∘V_ : V₄ → V₄ → V₄, the V₄ residue composition.
--
-- Ⓒ.v4 (2026-07-05): this WAS a hand-written 16-entry Cayley table (mirroring
-- eliza/rule_action.py:_V4_COMPOSE, XOR on the two underlying Z/2 indices) — a
-- reinvention of the Klein four-group operation. Now that RuleAction.V4
-- re-exports the canonical Groups.V4 carrier, the composition IS deduped to
-- Groups.V4.Operations._·_ (same group, same values — it still computes to the
-- concrete result, so consumers reduce unchanged). Single source for the op.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.V4Compose where

-- A re-export barrel: `_∘V_` IS Groups.V4's canonical operation `_·_`, renamed to
-- RuleAction's compositional notation. Since the carrier is now the global V₄, a
-- fresh `_∘V_ : V₄ → V₄ → V₄` definition here would violate carrier-locality (a
-- V₄-operator outside Groups.V4's home); a renaming re-export is not a new operator.
open import Substrate.Groups.V4.Operations using () renaming (_·_ to _∘V_) public
