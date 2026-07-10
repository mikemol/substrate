------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.CrossMul
--
-- THE GENUINE CROSS-CARRIER MIXING. Two carriers A, B embed (via Bridges)
-- into a common multiplicative carrier R, and the cross-multiplication of
-- a : A and b : B is their product IN R:  cross a b = (embA a) · (embB b).
-- This is bilinear — it mixes A-content and B-content — and it sidesteps the
-- tensor-quotient bare --safe lacks: R is GIVEN, not constructed. Structurally
-- it is the COSPAN  A → R ← B  with R multiplicative (the dual of the
-- synchronized product in Cross.agda, which was the span/lockstep).
--
-- COHERENCE IS THE CROSS-TERM'S NILPOTENCY DEGREE (per the thread — graded,
-- not binary; the obstruction is a residue, not a wall):
--   * cross term reduces to z (degree ≤ 1) — the two strands are orthogonal,
--     a CLEAN correspondence;
--   * cross term nilpotent of degree n > 1 — a graded OBSTRUCTION (dⁿ = 0,
--     the boundary-of-a-boundary that doesn't vanish), its degree the cost.
--
-- CRT is the worked instance: the idempotents e₁, e₂ embed ℤ/3, ℤ/5 into
-- ℤ/15 and are ORTHOGONAL (e₁·e₂ ≡ 0) — the cross terms vanish, the factors
-- don't interfere, the correspondence is coherent. Non-coprime moduli give a
-- nonzero nilpotent cross term: the obstruction, graded by degree.
--
-- WITNESS here is abstract (no numerals): embedding into the square-zero
-- carrier `two-mul`, every cross term vanishes — coherence everywhere. GRADED
-- coherence (degree genuinely varying across pairs) needs a richer common
-- carrier; CRT is that numeral example, deliberately deferred.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.CrossMul where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; id-bridge)
open import Substrate.Algebra.Wedge.Mul
  using (MulDivStr; base; mul; Nilpotent; pow; two-div; two-mul; Two)

------------------------------------------------------------------------
-- 1. The cospan: two carriers meeting in a common multiplicative carrier.
------------------------------------------------------------------------

record CrossMix {CA CB Cr : Set} (A : DivStr CA) (B : DivStr CB) (R : MulDivStr Cr) : Set where
  field
    embA : Bridge A (base R)
    embB : Bridge B (base R)

open CrossMix public

------------------------------------------------------------------------
-- 2. The cross term: a : A times b : B, mixed in R.
------------------------------------------------------------------------

cross : {CA CB Cr : Set} {A : DivStr CA} {B : DivStr CB} {R : MulDivStr Cr} →
        CrossMix A B R → CA → CB → Cr
cross {R = R} cm a b = mul R (translate (embA cm) a) (translate (embB cm) b)

------------------------------------------------------------------------
-- 3. Coherence at a pair = the cross term is a graded nilpotent residue.
--    (Degree ≤ 1: orthogonal/clean. Degree n > 1: graded obstruction, dⁿ=0.)
------------------------------------------------------------------------

Coherent : {CA CB Cr : Set} {A : DivStr CA} {B : DivStr CB} {R : MulDivStr Cr} →
           CrossMix A B R → CA → CB → Set
Coherent {R = R} cm a b = Nilpotent R (cross cm a b)

------------------------------------------------------------------------
-- 4. Abstract witness: into the square-zero carrier, every cross term
--    vanishes — coherence everywhere (the orthogonal, clean extreme).
------------------------------------------------------------------------

mix-witness : CrossMix two-div two-div two-mul
mix-witness = record { embA = id-bridge two-div ; embB = id-bridge two-div }

coherent-everywhere : (a b : Two) → Coherent mix-witness a b
coherent-everywhere a b = 0 , refl
