{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIORunEmit — ⟡extrude-io-run-emit: the coinductive run EMITS
-- its observations through the I/O monad, end to end. The run-side (277-283) OBSERVES (per-step head-shape +
-- residue); ExtrudeIO (285) EMITS (ret/emit). This composes them: run-emit fuel t = emit-list (take-obs fuel
-- (run-trace t)) — freeze a term, observe a bounded prefix, EMIT each observation as an IO program. collect
-- runs the emit program back to (outputs, value), and the ROUNDTRIP proves the emitted outputs ARE exactly
-- the run's observations. Pure — NO funext, NO Set₁, NO axiom.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: run-emit (the run→IO emit
-- program), collect (run an IO program to its outputs+value), collect-emit-list (collect ∘ emit-list = the
-- list), and run-emit-collect (the roundtrip: the emitted outputs = the run's observation prefix). The
-- framing ('the run emits its observations end to end') is (prose: 278/285).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeIORunEmit where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun using (run-trace; take-obs)

-- specialize the emit-monad at O = HeadShape (the caller supplies the concrete output type — parametrized):
open import Substrate.Category.UniversalProperty.ExtrudeIO HeadShape using (IO; ret; emit; emit-list)

------------------------------------------------------------------------
-- ① THE RUN EMITS: observe a bounded prefix of the reduction (take-obs, 278) and EMIT each head-shape.
------------------------------------------------------------------------
run-emit : ℕ → Tm⟦533ef80d⟧ → IO ⊤
run-emit fuel t = emit-list (take-obs fuel (run-trace t))

------------------------------------------------------------------------
-- ② COLLECT: run an IO program to its emitted outputs + final value (the interpreter for the emit effect).
------------------------------------------------------------------------
collect : {A : Set} → IO A → List HeadShape × A
collect (ret a)    = [] , a
collect (emit o k) = let r = collect k in (o ∷ proj₁ r) , proj₂ r
  where open import Substrate.Foundation.Product using (proj₁; proj₂)

------------------------------------------------------------------------
-- ③ THE ROUNDTRIP: collecting an emit-list gives back the list; collecting a run's emission gives back the
--    run's observation prefix. The emitted outputs ARE the observations — the run emits faithfully.
------------------------------------------------------------------------
collect-emit-list : (os : List HeadShape) → collect (emit-list os) ≡ (os , tt)
collect-emit-list []       = refl
collect-emit-list (o ∷ os) = cong (λ r → (o ∷ proj₁ r) , proj₂ r) (collect-emit-list os)
  where open import Substrate.Foundation.Product using (proj₁; proj₂)

run-emit-collect : (fuel : ℕ) (t : Tm⟦533ef80d⟧) →
                   collect (run-emit fuel t) ≡ (take-obs fuel (run-trace t) , tt)
run-emit-collect fuel t = collect-emit-list (take-obs fuel (run-trace t))

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the coinductive run EMITS its observations through the I/O monad, faithfully,
-- with no axiom): the run-side (277-283) observes (head-shape + residue); ExtrudeIO (285) emits. run-emit (①)
-- composes them — observe a bounded prefix, emit each head-shape as an IO program. collect (②) interprets the
-- emit effect back to (outputs, value), and the roundtrip (③: collect-emit-list + run-emit-collect) proves the
-- emitted outputs ARE exactly the run's observation prefix. So the observe-side and the emit-side are one
-- pipeline: freeze → run → observe → emit, and what comes out is what was observed. Pure structural equalities
-- on IO-values — NO funext, NO Set₁, NO axiom (D-parametrize-dont-assume / D-safe-no-postulate). The extruder's
-- reduction now EMITS its trace through the repo's category-theoretic emit-monad. Chain: 285 (the emit-monad)
-- → 286a (the run emits through it).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = run-emit (the run→IO emission), collect (the effect interpreter),
-- collect-emit-list + run-emit-collect (the faithful roundtrip). SCOPED: streaming the UNBOUNDED run (a
-- coinductive IO / an infinite emit) — here the emission is bounded by fuel (take-obs), the honest finite
-- prefix (the coinductive emit is ⟡extrude-io-costream). What's grounded: a bounded run emits its observations
-- faithfully through the monad — end-to-end emission, no axiom.
------------------------------------------------------------------------
