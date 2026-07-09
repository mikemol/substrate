{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimDetect — ⟡extrude-bisim-detect: the per-step bisimilar
-- cycle-DETECTION, the last place "detect the loop" could smuggle in TOTAL decidability (the 6th-spook, 277).
-- It does NOT. Detection is a per-step SEARCH: at each step decide the CHEAP head observation (head-eq on
-- HeadShape, 277) and BLEED THE RESIDUE (compare the tails via more), bounded by fuel. The full bisimilarity
-- ≈ (278) is the fuel→∞ COINDUCTIVE LIMIT — NOT decidable; bisim-upto is the decidable BOUNDED piece:
--
--   bisim-upto n s t   = the traces agree on the first n observations (decide head, bleed residue) — DECIDABLE
--   ≈→upto             = full ≈ ⟹ bounded agreement to ANY depth (the observation is SOUND; ≈ the limit)
--   lasso→upto         = 279's k-cycle lasso is confirmed OBSERVATIONALLY to any bounded depth
--   detect-period      = the bounded per-step search for period k (bisim-upto against the k-shift)
--
-- So the loop is DETECTED by a bounded observation (bisim-upto), CONFIRMED by the coinductive bisimulation
-- (≈, bled), never by a total decision. The search IS the reduction strategy.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: head-eq (+ head-eq-refl/
-- -sound), bisim-upto (the bounded bisimilarity), ≈→upto (soundness), lasso→upto (the lasso observed), and
-- detect-period (the bounded search). The framing ('detection is a per-step search + residue-bleed, not a
-- total decision; ≈ is the coinductive limit') is (prose: 277/278/279 + Bisim; the full fuel+k-threaded
-- driver producing a BisimOutcome stays scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimDetect where

open import Substrate.Foundation.Eq using (_≡_; refl; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape; isS; isK; isI; isApp)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun
  using (RedTrace; run-trace; obs; more; _≈_; obs≈; more≈)
open import Substrate.Category.UniversalProperty.ExtrudeBisimLassoK using (more^; lasso-k)

open import Substrate.Foundation.Function.Iterate using (iterate)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)

------------------------------------------------------------------------
-- ① THE CHEAP PER-STEP OBSERVATION-EQUALITY: head-eq on HeadShape (a finite 4-tag) — the cheapest bijective
--    decidable piece (Bool-valued), with head-eq a a ≡ true and equality-soundness.
------------------------------------------------------------------------
head-eq : HeadShape → HeadShape → Bool
head-eq isS   isS   = true
head-eq isK   isK   = true
head-eq isI   isI   = true
head-eq isApp isApp = true
head-eq _     _     = false

head-eq-refl : (a : HeadShape) → head-eq a a ≡ true
head-eq-refl isS   = refl
head-eq-refl isK   = refl
head-eq-refl isI   = refl
head-eq-refl isApp = refl

head-eq-sound : {a b : HeadShape} → a ≡ b → head-eq a b ≡ true
head-eq-sound {a} p = subst (λ x → head-eq a x ≡ true) p (head-eq-refl a)

------------------------------------------------------------------------
-- ② BOUNDED BISIMILARITY: agree on the first n observations — decide the head (head-eq), bleed the residue
--    (more), up to depth n. DECIDABLE (Bool). The full ≈ is the n→∞ limit; this is the cheap bounded piece.
------------------------------------------------------------------------
bisim-upto : ℕ → RedTrace → RedTrace → Bool
bisim-upto zero    s t = true
bisim-upto (suc n) s t = head-eq (obs s) (obs t) ∧ bisim-upto n (more s) (more t)

------------------------------------------------------------------------
-- ③ SOUNDNESS: full bisimilarity ⟹ bounded agreement to ANY depth. The observation (bisim-upto) is sound
--    against ≈; ≈ carries the residue (the deeper agreement), bisim-upto reads a bounded prefix of it.
------------------------------------------------------------------------
≈→upto : (n : ℕ) (s t : RedTrace) → s ≈ t → bisim-upto n s t ≡ true
≈→upto zero    s t p = refl
≈→upto (suc n) s t p rewrite head-eq-sound (obs≈ p) = ≈→upto n (more s) (more t) (more≈ p)

------------------------------------------------------------------------
-- ④ THE LASSO IS OBSERVED: 279's k-cycle lasso (run-trace t ≈ more^ k (run-trace t)) is confirmed by the
--    bounded observation to any depth — the loop is DETECTABLE observationally (a bounded witness), its truth
--    the coinductive bisimulation (bled).
------------------------------------------------------------------------
lasso→upto : (t : Tm⟦533ef80d⟧) (k : ℕ) → iterate k step t ≡ t →
             (n : ℕ) → bisim-upto n (run-trace t) (more^ k (run-trace t)) ≡ true
lasso→upto t k cyc n = ≈→upto n (run-trace t) (more^ k (run-trace t)) (lasso-k t k cyc)

------------------------------------------------------------------------
-- ⑤ THE BOUNDED PER-STEP SEARCH for a period-k loop: does the trace agree with its k-shift up to fuel? A
--    DECIDABLE bounded observation (the per-step search); the real cycle is confirmed by the lasso (④, bled).
------------------------------------------------------------------------
detect-period : (fuel k : ℕ) (t : Tm⟦533ef80d⟧) → Bool
detect-period fuel k t = bisim-upto fuel (run-trace t) (more^ k (run-trace t))

-- a genuine k-cycle IS detected to any fuel (the search never gives a false negative on a real cycle):
detect-sound : (fuel k : ℕ) (t : Tm⟦533ef80d⟧) → iterate k step t ≡ t → detect-period fuel k t ≡ true
detect-sound fuel k t cyc = lasso→upto t k cyc fuel

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — cycle DETECTION is a per-step bounded SEARCH (decide the cheap head, bleed
-- the residue), NOT a total decision; ≈ is the coinductive limit, bisim-upto its bounded observation): 277
-- said the cycle-test is bisimilarity (per-step obs + residue), not total DecEq; 278/279 built the run + the
-- lasso; 280 tagged the outcomes. 281 grounds DETECTION without total decidability: bisim-upto (②) is the
-- BOUNDED bisimilarity — decide the head (head-eq, ①, the cheapest bijective piece) and bleed the residue
-- (more), up to fuel — DECIDABLE; ≈→upto (③) proves it SOUND against the full ≈ (which carries the residue,
-- the coinductive limit); lasso→upto (④) confirms 279's k-cycle observationally to any depth; detect-period
-- (⑤) is the bounded per-step SEARCH, with detect-sound proving a real cycle is never missed. At no point is
-- total Tm⟦533ef80d⟧-DecEq used — the head is decided cheaply, the residue bled, the full bisimulation deferred as the
-- coinductive limit. The search IS the reduction strategy: observe the cheap piece, bleed the rest. Positive,
-- coinductive, no Turing spook (the 6th dissolved, now even the detection is a bounded search). Chain: 277
-- (bisimilarity) → 278/279 (run + lasso) → 280 (Unfold tags) → 281 (bounded detection, not total).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = head-eq (+refl/+sound), bisim-upto (bounded bisimilarity),
-- ≈→upto (soundness against ≈), lasso→upto (the lasso observed), detect-period + detect-sound (the bounded
-- search, sound on real cycles). SCOPED (reused-in-spirit, coinductive — NOT a total decision): the full
-- fuel+k-threaded DRIVER that searches over periods k and produces a BisimOutcome (280) — bounded, reporting
-- `stopped` if no period found within fuel (⟡extrude-bisim-driver); the COMPLETENESS direction (bisim-upto n
-- ≡ true for ALL n ⟹ ≈) is the coinductive limit, NOT decidable (that IS the point — ⟡extrude-upto-limit,
-- coinductive). What's grounded: detection is a per-step bounded search (decide cheap head + bleed residue),
-- sound on real cycles, with ≈ the coinductive limit — no total DecEq, the 6th spook fully dissolved.
------------------------------------------------------------------------
