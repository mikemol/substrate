{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.StreamMap — the two head-function endomorphisms of
-- RealTrace, LIFTED (⟡dedup.tree). jea_pysim flagged Cancel.bump / Cancel.unbump /
-- Ops.addℕ as "one parametric concept" (STRONG orbit, 88%, one hole @ the tail):
-- each has the SHARED head clause `head (F f x) = f (head x)` and differs only in
-- the TAIL — recurse (map every digit) or stop (touch the head only). That hole is
-- NOT a clean function parameter: Agda's guardedness REJECTS corecursion-through-a-
-- function, so the recurse-vs-stop choice is a genuine (not cosmetic) distinction
-- between two guarded copattern generics. Both share the head-function `f`:
--
--   mapT f   — apply f to EVERY digit  (a map; the guarded corecursion)
--   onHead f — apply f to the HEAD only (modify-head; tail untouched)
--
-- Instances (were three separate copattern defs; now lifted): Cancel.bump = mapT (k +_),
-- Cancel.unbump = mapT (_∸ k), Ops.addℕ = onHead (k +_). The generic stream map was
-- genuinely absent from the repo (reuse-search) — the three ops were each reinventing it.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.StreamMap where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)

-- map a per-digit function over the WHOLE trace (guarded corecursion).
mapT : (ℕ → ℕ) → RealTrace → RealTrace
head (mapT f x) = f (head x)
tail (mapT f x) = mapT f (tail x)

-- apply f to the HEAD digit only; the tail passes through unchanged.
onHead : (ℕ → ℕ) → RealTrace → RealTrace
head (onHead f x) = f (head x)
tail (onHead f x) = tail x
