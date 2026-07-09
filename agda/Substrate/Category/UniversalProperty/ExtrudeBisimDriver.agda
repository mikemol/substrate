{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimDriver — ⟡extrude-bisim-driver: the run driver returns a
-- FROZEN GENERATOR, not a Bool/verdict (the operator's reframe, completing the coinductive frame). A driver
-- that returned true/false would be back in the TOTAL space (decide loop/no-loop — the 6th spook). Instead it
-- returns a FROZEN GENERATOR — the suspended, RESUMABLE run state (RedTrace, 278: obs = peek, more = resume) —
-- and the true/false is DERIVED, per step: "is THIS frozen generator the same as the LAST one, under a single
-- step of fuel?" (bisim-upto 1, 281). The driver is itself a COINDUCTIVE process, emitting {the frozen
-- generator, the per-step same?, the advance}, resumable indefinitely — it NEVER decides looping totally.
--
--   frozen  : the current FROZEN generator (resumable — a suspended process, not a forced value)
--   same?   : "same as the last generator, under a single step of fuel" (bisim-upto 1 — the cheap piece)
--   advance : resume — the current generator becomes the last, and we step on (coinductive)
--
-- So the driver bleeds the residue (the frozen generator carries the whole future run, unforced), and the
-- verdict is the CALLER's business (observe the same? stream), never the driver's. The search IS the run.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: freeze (Tm⟦533ef80d⟧ → the frozen
-- generator = run-trace), same-1 (the per-step generator-sameness = bisim-upto 1), the Driver record (frozen/
-- same?/advance), drive/drive-from (the coinductive driver), and same-at-fixed (at a fixed point the
-- generator IS the same as last, same? ≡ true). The framing ('return a frozen generator not a verdict; the
-- caller observes same?') is (prose: the operator's reframe + 278/281; verdict-extraction stays the caller's).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimDriver where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong)
open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Bool using (Bool; true)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (head-shape)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun using (RedTrace; run-trace; obs; more)
open import Substrate.Category.UniversalProperty.ExtrudeBisimDetect using (bisim-upto; head-eq-sound)

------------------------------------------------------------------------
-- ① THE FROZEN GENERATOR is the RedTrace (278): a suspended, resumable run — peek the observation (obs),
--    resume to the next frozen generator (more). freeze = run-trace: freeze a term into its frozen run.
------------------------------------------------------------------------
freeze : Tm⟦533ef80d⟧ → RedTrace
freeze = run-trace

------------------------------------------------------------------------
-- ② "SAME AS THE LAST, UNDER A SINGLE STEP OF FUEL" — bisim-upto 1 (281): compare two frozen generators by
--    ONE fuel step (their peeked observations agree). The Bool is THIS per-step comparison, not a verdict.
------------------------------------------------------------------------
same-1 : RedTrace → RedTrace → Bool
same-1 = bisim-upto 1

------------------------------------------------------------------------
-- ③ THE DRIVER: a COINDUCTIVE process emitting the frozen generator + the per-step same? + the advance. It
--    returns the FROZEN GENERATOR (resumable), never a total loop/no-loop decision.
------------------------------------------------------------------------
record Driver : Set where
  coinductive
  field
    frozen  : RedTrace       -- the current frozen generator (resumable — the bled residue, unforced)
    same?   : Bool           -- same as the last generator, under a single step of fuel
    advance : Driver         -- resume: the current generator becomes the last, step on
open Driver public

drive : (last cur : RedTrace) → Driver
frozen  (drive last cur) = cur
same?   (drive last cur) = same-1 last cur
advance (drive last cur) = drive cur (more cur)

-- freeze a term and drive its run (the first generator is its own `last`, so same? starts by self-comparison):
drive-from : Tm⟦533ef80d⟧ → Driver
drive-from t = drive (freeze t) (freeze t)

------------------------------------------------------------------------
-- ④ AT A FIXED POINT the generator IS the same as the last under one step (same? ≡ true) — the driver's
--    per-step observation flags the normal-form/lasso point WITHOUT any total decision.
------------------------------------------------------------------------
same-at-fixed : (t : Tm⟦533ef80d⟧) → step t ≡ t → same-1 (freeze t) (freeze (step t)) ≡ true
same-at-fixed t p rewrite head-eq-sound (sym (cong head-shape p)) = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the driver returns a FROZEN GENERATOR (resumable), NOT a verdict; the true/
-- false is the per-step "same as last under one fuel step", the caller's to observe): a driver returning a
-- Bool loop/no-loop verdict would be the TOTAL space again (decide looping — the 6th spook). The reframe: the
-- driver returns a FROZEN GENERATOR (①, the RedTrace — a suspended resumable run, the residue carried
-- unforced), and the true/false is DERIVED per-step — same-1 (②, bisim-upto 1) asks "is this generator the
-- same as the last, under a single step of fuel?". The Driver (③) is a coinductive process emitting {frozen,
-- same?, advance}, resumable indefinitely; drive advances by resuming (cur becomes last, more cur the next
-- frozen generator). At a fixed point same? ≡ true (④, same-at-fixed) — the per-step observation flags the
-- point, no total decision. The verdict (loop/halt/stop) is the CALLER's business — observe the same? stream,
-- bleed the residue — never the driver's. This completes the coinductive run-side: every layer (observation
-- 277, stream 278, lasso 279, Unfold 280, detection 281, driver 282) is per-step + residue-bled, and the
-- driver itself returns a resumable generator, not a verdict. Positive, coinductive, no Turing spook. Chain:
-- 277 (bisimilarity) → 278/279 (run/lasso) → 280 (Unfold) → 281 (bounded detection) → 282 (frozen-generator
-- driver, no verdict).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = freeze (the frozen generator), same-1 (the per-step generator-
-- sameness), the Driver record + drive/drive-from (the coinductive frozen-generator driver), same-at-fixed
-- (the fixed-point flag). SCOPED (reused-in-spirit, coinductive — deliberately NOT the driver's job): the
-- VERDICT-EXTRACTION (the caller observing the same? stream over a bounded run to emit a BisimOutcome, 280 —
-- ⟡extrude-driver-verdict); this is the caller's, because a driver that decided the verdict would be back in
-- the total space. What's grounded: the driver returns a frozen (resumable) generator + a per-step sameness
-- observation, never a total loop/no-loop decision — the coinductive frame fully realized.
------------------------------------------------------------------------
