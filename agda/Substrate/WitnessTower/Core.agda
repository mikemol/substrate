------------------------------------------------------------------------
-- Substrate.WitnessTower.Core
--
-- The witnessed-simplex primitive, BUILT exactly as narrated. One object,
-- one move — no derived arithmetic (factorial, symmetry orders) here;
-- this file is only the base concept, so experiments run on something
-- faithful to the narration.
--
-- The narration:
--   * A node witnesses the universe (nothing else to witness)  → rung 0.
--   * A second node witnesses the first; together they form the first
--     edge                                                     → rung 1.
--   * A third node witnesses the edge just formed              → rung 2.
--   * ... each additional node witnesses the simplex below.
--
-- Each additional node constructs a PATH OF WITNESSES from the base of
-- the tower to the active rung. The k-rung is a simplex of k+1 nodes, one
-- node witnessing a (k−1)-simplex. The path is a first-class recorded
-- object here (`Path`), because the narration's content is the chain of
-- witnessings itself, not any numeric summary of it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Core where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

------------------------------------------------------------------------
-- 1. The simplex rungs and the one move.
--
-- WSimplex k is the rung-k object. `base` is the node witnessing the
-- universe; `witnessing s` is a new node witnessing the simplex s below,
-- which forms the next rung.
------------------------------------------------------------------------

data WSimplex : ℕ → Set where
  base       : WSimplex zero
  witnessing : ∀ {k} → WSimplex k → WSimplex (suc k)

------------------------------------------------------------------------
-- 2. The path of witnesses.
--
-- A Path k records the chain of witnessing steps from the base of the
-- tower up to rung k: `start` at the base, and `_witnesses_` extends the
-- path by one node witnessing the current top rung. So a Path k literally
-- IS the sequence of designations the narration describes, and its
-- top-rung simplex is recovered by `top`.
------------------------------------------------------------------------

data Path : ℕ → Set where
  start       : Path zero
  _witnesses_ : ∀ {k} → Path k → WSimplex k → Path (suc k)

infixl 5 _witnesses_

-- The simplex at the top of a path (the active rung).
top : ∀ {k} → Path k → WSimplex k
top start             = base
top (_witnesses_ {k} p s) = witnessing s

-- The canonical path: at each rung, the new node witnesses the simplex
-- the path has so far reached. This is "walk the tower from the base".
walk : (k : ℕ) → Path k
walk zero    = start
walk (suc k) = walk k witnesses top (walk k)

------------------------------------------------------------------------
-- 3. Length of the path = number of witnessing steps = the rung index.
--    (The one numeric fact that is purely the narration: a path to rung
--    k took exactly k witnessing steps.)
------------------------------------------------------------------------

steps : ∀ {k} → Path k → ℕ
steps start         = zero
steps (p witnesses _) = suc (steps p)

steps-walk : (k : ℕ) → steps (walk k) ≡ k
steps-walk zero    = refl
steps-walk (suc k) = cong suc (steps-walk k)
