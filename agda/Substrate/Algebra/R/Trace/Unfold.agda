------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Unfold
--
-- The composition operation of the substrate-ℝ arc: the ANAMORPHISM. A real is
-- built from a seed plus a STEP `S → ℕ × S` (emit one CF digit, advance the
-- state). Productivity is automatic — `head` is the step's output (a terminating
-- computation) and `tail` is guarded corecursion — so the ENTIRE burden of any
-- operation collapses to making its step TOTAL.
--
-- That reframes the "hard productivity wall" of Gosper CF arithmetic: an
-- operation whose natural step is an UNBOUNDED search ("ingest input until the
-- next output digit is determined") is not unprovable — it is unBOUNDED. Make
-- the step total by a CONSTRUCTED FINITE WINDOW (a fuel): finite ⟹ decidable, the
-- constructive resolution of the productivity-is-LEM problem
-- ([[feedback_finite_window_constructive_lem]]; UNIX 512B blocks; LZ77 windows;
-- Tarski — invert the tower, walk the finite descent down, turn it back up and
-- call the limit a fixed point). Then `unfold (windowed-step) seed` is a genuine
-- productive coinductive real. So +/× via Gosper ARE buildable (B3-next); the
-- step is a fuel-bounded walk-down, `unfold` assembles it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Unfold where

open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Unit    using (⊤; tt)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.R.Trace using (RealTrace; head; tail; take)

------------------------------------------------------------------------
-- The anamorphism. `head` terminates (it is `proj₁ (f s)`), so the whole
-- thing is productive; `tail` is the guarded corecursive call.
------------------------------------------------------------------------

unfold : {S : Set} → (S → ℕ × S) → S → RealTrace
head (unfold f s) = proj₁ (f s)
tail (unfold f s) = unfold f (proj₂ (f s))

------------------------------------------------------------------------
-- The simplest instances: a step with a total (here trivial) body. The all-k
-- real [k;k,k,…] is a one-state unfold — a worked check that the assembly is
-- productive. (Windowed-Gosper steps slot in here unchanged.)
------------------------------------------------------------------------

allK : ℕ → RealTrace
allK k = unfold (λ _ → (k , tt)) tt

_ : take 3 (allK 2) ≡ 2 ∷ 2 ∷ 2 ∷ []
_ = refl
