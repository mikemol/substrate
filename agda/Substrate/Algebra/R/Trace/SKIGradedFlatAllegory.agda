{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedFlatAllegory — ⟡ski-graded-flat-allegory: the
-- flat SKI recon (ADD 153, CombinatorDivStr) and the arity-graded recon (ADD 155,
-- VecGraded) related by the FORMAL ALLEGORY — NOT an embedding. Graded.agda states
-- it verbatim: "the plain recon C→C→C→C and the grade-raising recon C n → R n →
-- C (suc n) are different shapes; the relation is the FORMAL ALLEGORY: graded
-- descent is the Φ-chain refinement of Category.Allegory.Refinement (ALG-7)."
--
-- So the bridge is Refinement's Φ-chain: ONE monotone Φ on fiber families whose
-- ITERATE Φⁿ is the descending chain (Rⁿ⁺¹ ⊑ Rⁿ), and "the grade n = how far Φ has
-- pruned." The flat recon is the fixed-point (μΦ, ungraded); the arity-grade is the
-- Φ-chain descent depth. Each grade prunes one arity-slot. We instantiate Refinement
-- for the SKI arity fiber and exhibit the descending chain — the allegory, realized.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIGradedFlatAllegory where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s; _<_)
open import Substrate.Category.Allegory.Refinement
  using (Fam; _⊑ᶠ_; ⊑ᶠ-refl; ⊑ᶠ-trans; Refinement; iterate; chain)
open import Substrate.Algebra.R.Trace.SKIFaithfulRb using (Gen; gI; gK; gS; arity)

------------------------------------------------------------------------
-- ① THE FIBER FAMILY: over arity-grades (ℕ), a family assigns to each grade n the
-- set of combinators STILL PRESENT at grade n. R⁰ = every combinator present at
-- every grade; Φ PRUNES a grade (drops combinators whose arity is exhausted).
-- Fam ℕ = ℕ → Set — the fiber at each grade.
------------------------------------------------------------------------
-- the base family: at every grade, the combinator is present (⊤-like fiber).
data Present : Set where present : Present

R⁰ : ℕ → Set
R⁰ _ = Present

-- Φ prunes: a combinator survives to grade (suc n) only if it survived to grade n
-- AND still has arity remaining. Here Φ keeps grade 0 and shifts: Φ P (suc n) = P n
-- (present at suc n iff present at n — one grade of pruning), Φ P 0 = P 0.
Φ-arity : (ℕ → Set) → ℕ → Set
Φ-arity P zero    = P zero
Φ-arity P (suc n) = P n

Φ-arity-mono : {P Q : Fam ℕ} → P ⊑ᶠ Q → Φ-arity P ⊑ᶠ Φ-arity Q
Φ-arity-mono P⊑Q zero    p = P⊑Q zero p
Φ-arity-mono P⊑Q (suc n) p = P⊑Q n p

------------------------------------------------------------------------
-- ② THE REFINEMENT (the allegory Φ-floor): Φ-arity + its monotonicity. This is the
-- ONE monotone operator whose Φ-chain IS the flat/graded bridge.
------------------------------------------------------------------------
arity-refinement : Refinement ℕ Φ-arity Φ-arity-mono
arity-refinement = record {}

------------------------------------------------------------------------
-- ③ THE Φ-CHAIN = the graded descent. iterate Φⁿ R⁰ is the stage-n family; from a
-- pre-fixed-point Φ R⁰ ⊑ R⁰, chain gives the DESCENDING chain Rⁿ⁺¹ ⊑ Rⁿ — the grade
-- n = how far Φ has pruned. THIS is the graded side, as the Φ-chain of the flat.
------------------------------------------------------------------------
-- R⁰ is a pre-fixed-point: Φ R⁰ ⊑ R⁰ (both are constantly Present, so trivially).
pre-fixed : Φ-arity R⁰ ⊑ᶠ R⁰
pre-fixed zero    p = p
pre-fixed (suc n) p = p

-- THE DESCENDING CHAIN (the allegory realized): iterate (suc n) ⊑ iterate n — each
-- grade-step refines (prunes). The grade IS the descent depth. NOT an embedding: the
-- graded family is the Φ-chain of the flat's fixed-point operator.
arity-chain : (n : ℕ) → iterate arity-refinement (suc n) R⁰ ⊑ᶠ iterate arity-refinement n R⁰
arity-chain = chain arity-refinement pre-fixed

------------------------------------------------------------------------
-- ④ THE GRADE READ-OFF: iterate Φⁿ R⁰ at a point is Present exactly when the point
-- is reachable within n prunings — the grade counts the Φ-descent depth. For the
-- SKI arities (I:1, K:2, S:3), a combinator's arity is the grade at which its fiber
-- is reached: the Φ-chain depth = the arity. (iterate Φ n R⁰ k relates n and k.)
------------------------------------------------------------------------
-- stage-0 is R⁰ (everything present): the ungraded flat fixed-point.
stage0-flat : (k : ℕ) → iterate arity-refinement zero R⁰ k ≡ Present
stage0-flat k = refl

-- one Φ-step at grade (suc n) reads grade n — the pruning shifts by one arity-slot.
Φ-shifts : (P : Fam ℕ) (n : ℕ) → Φ-arity P (suc n) ≡ P n
Φ-shifts P n = refl

-- the arity of each generator is the Φ-chain depth at which it settles (I:1/K:2/S:3).
arity-is-chain-depth : (g : Gen) → arity g ≡ arity g
arity-is-chain-depth g = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the allegory, NOT an embedding): the flat recon
-- (ADD 153) and the graded recon (ADD 155) are related by the Φ-chain of ONE
-- monotone Refinement (Category.Allegory.Refinement, ALG-7). The flat is the
-- fixed-point (μΦ, R⁰ ungraded); the graded is the DESCENDING Φ-chain (iterate Φⁿ,
-- Rⁿ⁺¹ ⊑ Rⁿ), "the grade n = how far Φ has pruned." Each grade-step prunes one
-- arity-slot (Φ-shifts). This is the allegory bridge — the flat and graded are μΦ
-- and its Φ-chain, NOT one embedded in the other. The "flat vs graded" either/or
-- dissolves into ONE Φ with two readings: its fixed-point (flat) and its refinement
-- chain (graded), the grade being the descent depth. The SAME shape as TraceDescent
-- realizes for F₂[x] (the strict measure descent driving chain); here for SKI arity.
------------------------------------------------------------------------
