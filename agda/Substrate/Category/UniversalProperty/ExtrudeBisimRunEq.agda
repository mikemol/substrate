{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimRunEq — ⟡extrude-bisim-run-eq: the VERDICT is what happens
-- when you RUN OUT OF OUTPUT. The coinductive generator (run-trace, 278) runs forever; a fuel-bounded run
-- produces a finite OUTPUT (the observed prefix) and then, at truncation, emits the VERDICT. The verdict is
-- `stop` (you ran out of output) UNLESS a halt/loop was WITNESSED before truncation (280). This is exactly
-- Wedge.Coalgebra.run's shape: run _ 0 _ = ([] , stop) — at zero fuel you are immediately out of output, so
-- the verdict is stop; halt/loop arise only when a witness fires before the fuel runs out.
--
--   brun fuel t   = (the observed prefix, the truncation verdict `stop`)
--   brun-zero     = ([] , stop)   — EXACTLY Wedge.Coalgebra.run's base (out of output ⟹ stop)
--   len-obs       = the output has exactly `fuel` observations (what you produce before running out)
--   the halt/loop verdicts are WITNESSED upgrades (280), observed BEFORE truncation — NOT computed by the run
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: brun (the fuel-bounded run
-- = prefix + stop), brun-zero (the base = the wedge-run's base), len-obs (output length = fuel), verdict-is-
-- stop (the truncation verdict is stop), and upgrade (a witnessed BisimOutcome 280 gives the halt/loop tag).
-- The framing ('the verdict is the truncation; my run IS the wedge-run structurally') is (prose: 280 + the
-- operator's "verdict = run out of output"; the literal cross-carrier ≡ needs a WedgeCoalg-at-Tm⟦533ef80d⟧ eq? = the
-- spook, scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimRunEq where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₂)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.Wedge.Coalgebra using (Unfold; halt; loop; stop)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun using (RedTrace; run-trace; more; take-obs)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUnfold using (BisimOutcome; to-unfold)

-- a local length on the observation output (Foundation.List has no length):
len : List HeadShape → ℕ
len []       = zero
len (_ ∷ xs) = suc (len xs)

------------------------------------------------------------------------
-- ① THE FUEL-BOUNDED RUN: produce the observed prefix (take-obs, 278) and the truncation VERDICT `stop`. The
--    run itself never computes halt/loop — those are witnessed (②). This is the honest run: output + stop.
------------------------------------------------------------------------
brun : ℕ → Tm⟦533ef80d⟧ → List HeadShape × Unfold
brun fuel t = take-obs fuel (run-trace t) , stop

-- at zero fuel you are IMMEDIATELY out of output ⟹ the verdict is stop, output empty — EXACTLY the wedge-run:
--   (Wedge.Coalgebra.run co zero seen a b = [] , stop)
brun-zero : (t : Tm⟦533ef80d⟧) → brun 0 t ≡ ([] , stop)
brun-zero t = refl

-- the output has exactly `fuel` observations — what you produce before running out:
len-obs : (n : ℕ) (s : RedTrace) → len (take-obs n s) ≡ n
len-obs zero    s = refl
len-obs (suc n) s = cong suc (len-obs n (more s))

-- the run's output prefix has exactly `fuel` observations (the corollary at run-trace t):
len-run : (n : ℕ) (t : Tm⟦533ef80d⟧) → len (take-obs n (run-trace t)) ≡ n
len-run n t = len-obs n (run-trace t)

-- the truncation verdict IS stop (you ran out of output) — the honest default of the run:
verdict-is-stop : (fuel : ℕ) (t : Tm⟦533ef80d⟧) → proj₂ (brun fuel t) ≡ stop
verdict-is-stop fuel t = refl

------------------------------------------------------------------------
-- ② THE HALT/LOOP VERDICTS ARE WITNESSED UPGRADES (280): a BisimOutcome (a fixed point / a lasso / a prefix,
--    each POSITIVELY witnessed) gives the halt/loop/stop tag — observed BEFORE truncation, NOT computed by
--    the run. So the run's default verdict (stop, ①) upgrades to halt/loop ONLY on a witness.
------------------------------------------------------------------------
upgrade : {t : Tm⟦533ef80d⟧} → BisimOutcome t → Unfold
upgrade = to-unfold

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the VERDICT is what happens when you RUN OUT OF OUTPUT; the run produces a
-- prefix + `stop`, halt/loop are witnessed upgrades observed before truncation; my run IS the wedge-run
-- structurally): the coinductive generator (run-trace, 278) runs forever; a fuel-bounded run (brun, ①)
-- produces a finite output (take-obs prefix) and the truncation verdict `stop`. brun-zero shows the base
-- (zero fuel = immediately out of output = ([], stop)) is EXACTLY Wedge.Coalgebra.run's base; len-obs shows
-- the output is exactly `fuel` long (what you produce before running out); verdict-is-stop confirms the
-- truncation verdict is stop. The halt/loop verdicts (②, upgrade = to-unfold) are WITNESSED (280) — a fixed
-- point / a lasso, observed BEFORE the fuel runs out — NOT computed by the run itself (a run that computed
-- them would need total DecEq, the spook). So the verdict is the truncation artifact: stop by default (out of
-- output), halt/loop only by a witness. My run and the wedge-run coincide: same output-prefix + verdict
-- shape, my halt/loop the witnessed BisimOutcome (280), my stop the truncation. Positive, coinductive, no
-- Turing spook. Chain: 280 (Unfold tags) → 282 (frozen-generator driver) → 283b (verdict = truncation).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = brun (prefix + stop), brun-zero (= the wedge-run's base),
-- len-obs (output length = fuel), verdict-is-stop (truncation ⟹ stop), upgrade (witnessed halt/loop, 280).
-- SCOPED (the spook): the LITERAL cross-carrier ≡ to Wedge.Coalgebra.run's output needs a WedgeCoalg instance
-- at Tm⟦533ef80d⟧ with eq? = total Tm⟦533ef80d⟧ DecEq (the 6th spook — neither attainable nor wanted); the correspondence is
-- structural (same prefix+verdict shape; my witnessed outcomes 280 = the wedge's halt/loop; my stop = the
-- truncation) — ⟡extrude-bisim-run-eq-literal (scoped BECAUSE it needs the spook). What's grounded: the
-- verdict is the fuel-truncation (stop out of output, halt/loop witnessed), my run structurally the wedge-run.
------------------------------------------------------------------------
