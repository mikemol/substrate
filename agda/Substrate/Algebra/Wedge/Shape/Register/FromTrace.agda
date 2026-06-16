------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Register.FromTrace
--
-- THE SUFFIX-SHARING DAG WAS THE EEA TRACE ALL ALONG. The "heavier build"
-- (a Fin-indexed flat-array DAG needing a well-founded `decode` measure to
-- rule out cycles) is unnecessary: the trace already IS the suffix DAG.
--   * `rec` (the sub-trace of `more b w rec`) IS the tail-pointer;
--   * `shape (more _ w rec) = quot w ∷ shape rec` is cons/cdr routing,
--     definitionally;
--   * `shape` is the decode — STRUCTURAL recursion, so terminating for free;
--   * `Trace` is INDUCTIVE, so acyclic for free — no well-founded measure.
-- A numeric index can point into a cycle; a structural `rec` cannot. The wall
-- was an artifact of the encoding, not the problem.
--
-- `intern-trace` interns every suffix of a trace's shape, BOTTOM-UP (tail
-- first), into the register — so shared suffixes collapse to one node. The
-- recursion is structural on the trace; no measure, no Fin, no flat array. The
-- trace supplies the suffix structure, the register the canonical addresses;
-- together they are the suffix-shared interned SPPF.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Register.FromTrace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (Trace; done; more; quot; ℕ-div)
open import Substrate.Algebra.Wedge.Shape using (shape)
open import Substrate.Algebra.Wedge.Shape.Register using (Register; _∈ᴿ_; intern)

-- Intern every suffix of a trace's shape, bottom-up. Structural recursion on
-- the inductive trace ⟹ terminating + acyclic for free (no well-founded
-- measure). Returns the register with the full shape interned + its address.
-- (At ℕ-div, where the Register lives — its shape elements are the ℕ quotients.)
intern-trace : {a b g : ℕ} (t : Trace ℕ-div a b g) (reg : Register) →
               Σ Register (λ reg′ → shape t ∈ᴿ reg′)
intern-trace (done a)       reg = intern [] reg
intern-trace (more b w rec) reg with intern-trace rec reg
... | (reg₁ , _) = intern (quot w ∷ shape rec) reg₁
