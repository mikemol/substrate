------------------------------------------------------------------------
-- Substrate.Category.StochasticLens.Sites.ChainWalk
--
-- Concrete site: the substrate's chain walk as a stochastic lens.
--
--   State S       = current chamber (Fin 24)
--   View A        = predicted next chain symbol (Fin 24)
--   Observation B = observed next chain symbol (Fin 24)
--
-- forward    : S → A    — predict via NIBBLE_TO_PERM[current_nibble]
-- backward   : S × B → S — update via inverse-chain-walk
--
-- The chain walk is DETERMINISTIC (per [[chain-walk-blocks-rotation-
-- factor]]), so the lens's "stochastic" character collapses to
-- pointwise certainty. This site demonstrates the lens primitive at
-- the substrate's load-bearing chain-walk carrier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens.Sites.ChainWalk where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

------------------------------------------------------------------------
-- The chain-walk lens at substrate-native chambers.
--
-- The 24 chambers of S₄ are represented as Fin 24.

Chamber : Set
Chamber = Fin 24

------------------------------------------------------------------------
-- ChainWalkLens record (specialised StochasticLens).
--
-- forward    : Chamber → Chamber predicts next chamber under
--              chain-walk dynamics.
-- backward   : Chamber × Chamber → Chamber updates state based on
--              actual observation.
--
-- Both are pure functions in this site (deterministic chain walk).
-- Concrete instances supply the specific NIBBLE_TO_PERM-based
-- prediction and inverse.

record ChainWalkLens : Set where
  field
    forward  : Chamber → Chamber
    backward : Chamber × Chamber → Chamber

open ChainWalkLens public

------------------------------------------------------------------------
-- Per [[expose-generator-not-orbit]]: the chain-walk's
-- deterministic dynamics IS the GENERATOR; per-corpus chain-symbol
-- streams are ORBITS. The lens makes the bidirectional structure
-- explicit at the categorical level.
--
-- Per [[chain-walk-blocks-rotation-factor]]: the chain walk's
-- statefulness means forward is NOT generally a bijection (multiple
-- prev states can lead to same next state). The backward map
-- corrects via observed-value consistency.
