{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeMinimalRun — ⟡extrude-minimal-run: the CONCRETE μ run — a
-- deterministic one-step reducer step : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧, iterated (275b's Function.Iterate), giving the wedge-run's
-- halt at the term level. 275b grounded μ = iteration abstractly (over any f); this instantiates f = step
-- (leftmost-outermost β-reduction on Tm⟦533ef80d⟧), so the reduction stream IS iterate step, and a NORMAL FORM is a
-- fixed point of step (iterating stays — the HALT, via 275b's fixed-preserved).
--
--   step   : one β-reduction at the head/left-spine (or the term itself if no redex there = normal-ish)
--   step-sound : t ⇒* step t          — step is a VALID reduction (the β-rules + cong-l lifted to ⇒*)
--   run-sound  : t ⇒* iterate k step t — iterating step is a valid multi-step reduction (the μ stream)
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: step (the deterministic
-- head/left reducer), cong-l* (cong-l lifted to ⇒*), step-sound (t ⇒* step t), and run-sound (t ⇒* iterate
-- k step t). The framing ('the μ run is iterate step; halt = normal-form fixed point') is (prose: 264/265/275b;
-- the full SPPF shared-forest cycle-closing with DecEq — the `loop`/`stop` outcomes — stays scoped, Tm⟦533ef80d⟧ has
-- no DecEq).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeMinimalRun where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Function.Iterate using (iterate)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-I; β-K; β-S; cong-l)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; _++*_)

------------------------------------------------------------------------
-- ① cong-l lifted to ⇒* : a reduction on the left spine lifts to the application (reused pattern — map
--    cong-l over the ◅-chain). The left-descent congruence the step needs.
------------------------------------------------------------------------
cong-l* : {f f' : Tm⟦533ef80d⟧} (g : Tm⟦533ef80d⟧) → f ⇒* f' → (f ∙ g) ⇒* (f' ∙ g)
cong-l* g done        = done
cong-l* g (s ◅ rest) = cong-l g s ◅ cong-l* g rest

------------------------------------------------------------------------
-- ② THE STEP EMITS ITS WITNESS (the operator's reframe): step′ returns the reduct TOGETHER with a proof it
--    is a reduct — soundness BY CONSTRUCTION, per clause. Clause overlap between the redex cases and the
--    general application case is Agda's clause-ordering (the SPPF's sharing/overlap bookkeeping); all we owe
--    is that each emitted (reduct, witness) is COHERENT. One general app clause — never stuck.
------------------------------------------------------------------------
step′ : (t : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ t' → t ⇒* t')
step′ (I ∙ x)             = x                     , (β-I x ◅ done)
step′ ((K ∙ x) ∙ y)       = x                     , (β-K x y ◅ done)
step′ (((S ∙ x) ∙ y) ∙ z) = ((x ∙ z) ∙ (y ∙ z))  , (β-S x y z ◅ done)
step′ (f ∙ x)             = (proj₁ r ∙ x)         , cong-l* x (proj₂ r)  where r = step′ f
step′ S                   = S                     , done
step′ K                   = K                     , done
step′ I                   = I                     , done

-- the reducer and its soundness are just the two projections — no clause-mirroring, no coverage gymnastics:
step : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
step t = proj₁ (step′ t)

step-sound : (t : Tm⟦533ef80d⟧) → t ⇒* step t
step-sound t = proj₂ (step′ t)

------------------------------------------------------------------------
-- ④ THE RUN IS A VALID MULTI-STEP REDUCTION: iterating step k times is reachable by ⇒* — the μ reduction
--    stream. (Halt: at a normal form, step fixes it, so iterate stays — 275b's fixed-preserved.)
------------------------------------------------------------------------
run-sound : (k : ℕ) (t : Tm⟦533ef80d⟧) → t ⇒* iterate k step t
run-sound zero    t = done
run-sound (suc k) t = run-sound k t ++* step-sound (iterate k step t)
-- iterate (suc k) step t = step (iterate k step t); but iterate applies OUTSIDE-IN: iterate (suc k) f t =
-- f (iterate k f t). So t ⇒* iterate k step t (IH) then one more step... we thread via step-sound at t first:
-- t ⇒* step t ⇒* iterate k step (step t) = iterate (suc k) step t. Aligns by iterate's definition.

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the μ run is CONCRETE: iterate step, a valid reduction stream, halting at a
-- normal-form fixed point): 275b grounded μ = iteration abstractly; this instantiates the step to a real Tm⟦533ef80d⟧
-- reducer. step (②) fires the leftmost redex (β-I/β-K/β-S) or descends the left spine, total; step-sound (③)
-- proves step t is a genuine ⇒* reduct (the β-rules + cong-l* lifting cong-l to ⇒*); run-sound (④) proves
-- iterate k step t is a valid multi-step reduction — the μ stream. A normal form is a fixed point of step, so
-- (275b's fixed-preserved) the run HALTS there — the wedge-run's `halt` at the term level. So the extruder's
-- μ is a concrete, sound, iterated reduction whose fixed point is the normal form (the minimal extruded
-- object). Positive — it EXISTS, reachable by reduction. No spook. Chain: 264 (run) → 265 (μ) → 275b
-- (μ=iterate) → 276a (iterate step, concrete + sound).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = step (deterministic reducer), cong-l* (⇒* left-congruence),
-- step-sound (t ⇒* step t), run-sound (t ⇒* iterate k step t). SCOPED (reused-in-spirit): the full SPPF
-- shared-forest run with the `loop`/`stop` outcomes (Wedge.Coalgebra.run needs Tm⟦533ef80d⟧ DecEq for the cycle-test —
-- Tm⟦533ef80d⟧ has none, ⟡ski-tm-deceq); step's COMPLETENESS (that a fixed point of step IS a normal form, not just
-- fixed — needs the no-redex characterization, ⟡extrude-step-complete). What's grounded: the μ run is a
-- concrete sound iterated reduction (iterate step), halting at a fixed point — the wedge-run `halt` on Tm⟦533ef80d⟧.
------------------------------------------------------------------------
