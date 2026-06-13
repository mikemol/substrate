------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.TraceWord
--
-- REFLECTING the R-arc machinery over the term-algebra-bridges pivot (user,
-- 2026-06-13: "TermAlgebraBridges… that's a pivot point we need to reflect our
-- machinery over"). `Category.TermAlgebraBridges` is the category-of-term-algebras:
-- every morphism category gets a `.Term` presentation and the bridges are functors
-- between them, inhabiting UPCategory. Our division/EEA machinery ALREADY has its
-- free term — `Algebra.Wedge.Trace` (keep every wedge step, recurse on the
-- remainder). This is its first bridge into that diagram.
--
-- THE BRIDGE (forgetful functor, T28-parallel — there `CharTerm` IS a Coxeter
-- word): the free wedge term collapses to its CONTINUED-FRACTION DIGIT WORD — the
-- list of quotients, a free-monoid element on ℕ. So `Wedge.Trace` (the free term)
-- maps to `List ℕ` (the free monoid), exactly as `digits-of-EEA` does for the ℕ
-- instance, but uniform over every `DivStr`. `done` ↦ [] (gcd reached, no more
-- digits); `more b w rest` ↦ quot w ∷ (rest's word).
--
-- This sits beside `Wedge.collapse` (→ g, the gcd index): both are forgetful reads
-- of the same free term, the gcd-read and the word-read. The FREE read is the
-- Trace itself, kept ([[feedback_never_discard_residue]]); these are two
-- projections of it. RealTrace is the coinductive dual of this free term; the
-- windowed-CF view (`Algebra.R.Trace.Windowed`) is `trace-word` of the value's
-- trace — the R-arc and the wedge term meeting at the digit word.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.TraceWord where

open import Substrate.Foundation.Nat  using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Wedge   using (DivStr; C; Trace; done; more; quot)

------------------------------------------------------------------------
-- The forgetful functor: free wedge term ↦ its continued-fraction digit word.
------------------------------------------------------------------------

trace-word : {D : DivStr} {a b g : C D} → Trace D a b g → List ℕ
trace-word (done _)        = []
trace-word (more _ w rest) = quot w ∷ trace-word rest
