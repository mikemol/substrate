{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostream — the UNBOUNDED emit: a coinductive costream of
-- outputs. The finite IO monad (285) emits a bounded computation; CoIO emits FOREVER (a costream). The
-- reduction run (277-283) gives a CoIO of head-shapes (emit an observation, step, repeat), and its finite
-- prefixes (take-coio) are exactly the bounded emit (take-obs, 278). Small — parameterized over the output O
-- (a concrete Set), NO levels/Set₁/funext/postulate.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: CoIO (the coinductive emit-
-- forever costream), run-coio (Tm⟦533ef80d⟧ → CoIO HeadShape via step), take-coio (finite prefix), and take-coio-run
-- (the prefix = take-obs, the bounded emit). The framing ('the unbounded emit; the run emits forever') is
-- (prose: 278/285).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeIOCostream where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape; head-shape)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun using (run-trace; take-obs)

private variable O : Set

------------------------------------------------------------------------
-- ① THE UNBOUNDED EMIT: a coinductive costream — emit one output, continue forever. The infinite analogue of
--    the finite IO (285): where IO ends with ret, CoIO never ends.
------------------------------------------------------------------------
record CoIO (O : Set) : Set where
  coinductive
  field
    emit-head : O
    emit-rest : CoIO O
open CoIO public

------------------------------------------------------------------------
-- ② THE RUN EMITS FOREVER: unfold a term into its unbounded observation costream (emit head-shape, step,
--    repeat) — guarded corecursion.
------------------------------------------------------------------------
run-coio : Tm⟦533ef80d⟧ → CoIO HeadShape
emit-head (run-coio t) = head-shape t
emit-rest (run-coio t) = run-coio (step t)

------------------------------------------------------------------------
-- ③ FINITE PREFIXES: take the first n emissions (a List) — the bounded emit. And these prefixes are EXACTLY
--    the run-side's bounded observation (take-obs, 278): the unbounded costream truncates to the finite emit.
------------------------------------------------------------------------
take-coio : ℕ → CoIO O → List O
take-coio zero    c = []
take-coio (suc n) c = emit-head c ∷ take-coio n (emit-rest c)

take-coio-run : (n : ℕ) (t : Tm⟦533ef80d⟧) → take-coio n (run-coio t) ≡ take-obs n (run-trace t)
take-coio-run zero    t = refl
take-coio-run (suc n) t = cong (head-shape t ∷_) (take-coio-run n (step t))

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the UNBOUNDED emit is a coinductive costream; the run emits forever, and its
-- finite prefixes ARE the bounded emit; small, no levels/funext): the finite IO (285) emits a bounded
-- computation (ending in ret). CoIO (①) emits FOREVER — the coinductive costream, the infinite analogue.
-- run-coio (②) unfolds a term into its unbounded observation costream (emit head-shape, step, repeat —
-- guarded corecursion, the run emitting forever). take-coio (③) truncates to a finite prefix, and
-- take-coio-run proves that prefix is EXACTLY the run-side's bounded observation (take-obs, 278) — so the
-- unbounded emit and the bounded emit (285/286) agree on every finite truncation. This is the emit-side's
-- coinductive completion: the run emits an infinite stream, observed/emitted a bounded prefix at a time
-- (D-verdict-is-truncation — the finite emit is the truncation of the infinite one). Small, parameterized
-- over O, no levels/Set₁/funext/postulate. Chain: 285/286 (finite emit) → 289c (the unbounded costream emit).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = CoIO (the coinductive emit-forever costream), run-coio (the run
-- emits forever), take-coio (finite prefix), take-coio-run (the prefix = the bounded emit take-obs). SCOPED:
-- bisimilarity on CoIO (a costream _≈_, mirroring RedTrace's — ⟡extrude-coio-bisim); the CoIO monad structure
-- (a coinductive emit-monad — ⟡extrude-coio-monad). What's grounded: the unbounded emit as a coinductive
-- costream whose finite prefixes are the bounded emit — the emit-side's coinductive completion, small.
------------------------------------------------------------------------
