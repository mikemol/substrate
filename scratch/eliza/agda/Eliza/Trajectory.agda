------------------------------------------------------------------------
-- Eliza.Trajectory
--
-- The walk: `walk : Word Gen → Chamber → Word Chamber`. Folds the
-- Manifold's chamber-step over a word of generators starting from a
-- given chamber. The resulting Word Chamber is the trajectory.
--
-- Two readings:
--   * Constructive: the recursion on Word Gen.
--   * Categorical: the runStateful unfolding of the manifold step.
--
-- Both are equivalent (the constructive form below IS the unfolding);
-- the explicit recursion is given so downstream modules can pattern
-- match on the trajectory directly.
--
-- This module also names the period-detection contract from Inspiration
-- #3 of the agda/Substrate read: the smallest `k > 0` such that
-- `trajectory[t] ≡ trajectory[t-k]` is the local `HasOrder` witness.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Trajectory where

open import Eliza.Prelude   using (ℕ; zero; suc; Maybe; nothing; just; _≡_; refl)
open import Eliza.Word      using (Word; []; _∷_; length)
open import Eliza.Alphabets using (Gen; Chamber)
open import Eliza.Manifold  using (apply)

------------------------------------------------------------------------
-- 1. The walk. Starting from `x`, consume the Word Gen and emit each
-- visited chamber in order. The first emitted chamber is `apply g₀ x`,
-- not `x` itself (matching the Python convention where `trajectory`
-- contains the post-step chambers).
------------------------------------------------------------------------

walk : Word Gen → Chamber → Word Chamber
walk []       _ = []
walk (g ∷ gs) x = let y = apply g x in y ∷ walk gs y

------------------------------------------------------------------------
-- 2. The current chamber after walking a Word from `x`. Convenience.
------------------------------------------------------------------------

endpoint : Word Gen → Chamber → Chamber
endpoint []       x = x
endpoint (g ∷ gs) x = endpoint gs (apply g x)

------------------------------------------------------------------------
-- 3. Period detection. Given a trajectory and the "current" chamber
-- (always the last entry, by construction), return the smallest k ≥ 1
-- such that the chamber k steps back equals the current — `nothing` if
-- no such k exists within the window.
--
-- This is the local HasOrder γ k witness from Substrate.Category.
-- Coalgebra.FiniteOrder, specialised to the current trajectory window.
------------------------------------------------------------------------

postulate
  detect-period : Word Chamber → Maybe ℕ

------------------------------------------------------------------------
-- 4. Postulated correctness obligation for detect-period: if it
-- returns `just k`, then the k-th-from-last chamber equals the last.
-- Spelled out as a postulate; the concrete implementation in Python
-- discharges it by direct scan.
------------------------------------------------------------------------

postulate
  detect-period-witness :
    (t : Word Chamber) (k : ℕ) →
    detect-period t ≡ just k →
    -- There exist x and prefix p such that t = p ++ x ∷ (k chambers) ∷ x ∷ []
    -- (the precise statement, elided here for skeleton purposes)
    Chamber  -- placeholder for the existential witness
