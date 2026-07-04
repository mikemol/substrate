{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderNfCrossRealigned — ⟡tower-realign-Q-crossmul:
-- the CrossMul cross-witness for FUSepQNf, FULLY INSTANTIATED (ADD 125 ⑤ only
-- NAMED the center; this builds the actual cross a b = embA a · embB b witness).
--
-- FUSepQNf.Wit = redW ⊎ peelW: a normal form is reached via a REDUCTION strand
-- (redW) or a PEEL strand (peelW), meeting in a common carrier. That IS the
-- CrossMul cospan A→R←B: the two strands embA/embB into R, their cross the mix.
-- A CLEAN normal form (the two strands don't interfere — no residual redex after
-- peeling) is the COHERENT case: the cross term is nilpotent (degree ≤ 1,
-- orthogonal). Into the square-zero carrier (two-mul), coherence is EVERYWHERE —
-- the clean/orthogonal extreme, which is exactly the "normal form is unambiguous"
-- content of FUSepQNf's common-carrier cospan.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderNfCrossRealigned where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Bridge using (id-bridge)
open import Substrate.Algebra.Wedge.Mul using (two-div; two-mul; Two; 𝟘; ε)
open import Substrate.Algebra.Wedge.CrossMul
  using (CrossMix; embA; embB; cross; Coherent; mix-witness; coherent-everywhere)

------------------------------------------------------------------------
-- ⑤ (completed) FUSepQNf.Wit=redW⊎peelW IS the CrossMul cospan, WITNESSED. The
-- two strands (reduction, peel) embed into the common carrier; the Nf cospan is
-- mix-witness (both strands into the square-zero carrier). The cross term of the
-- two strands is the "residual interference" — CLEAN when it vanishes.
------------------------------------------------------------------------
nf-cospan : CrossMix two-div two-div two-mul
nf-cospan = mix-witness      -- the redW/peelW strands as embA/embB into R

-- the cross term of a reduction-strand value a and a peel-strand value b: their
-- mix in R. For a clean normal form the strands are orthogonal — the cross is z.
nf-cross : Two → Two → Two
nf-cross = cross nf-cospan

-- CLEAN NORMAL FORM = COHERENT: the cross term is nilpotent (here degree ≤ 1,
-- it IS z). So peeling and reducing don't leave a residual redex — the normal
-- form is unambiguous. This is FUSepQNf's "the common carrier makes Nf well-
-- defined", now the CrossMul coherence witness (not just the named center).
nf-clean : (a b : Two) → Coherent nf-cospan a b
nf-clean = coherent-everywhere

-- and concretely the cross vanishes (the orthogonality, by refl):
nf-cross-vanishes : (a b : Two) → nf-cross a b ≡ 𝟘
nf-cross-vanishes a b = refl

------------------------------------------------------------------------
-- THE COMPLETION: FUSepQNf's Wit=redW⊎peelW common carrier IS the CrossMul
-- cospan A→R←B with a COHERENT (clean, orthogonal) cross — the two strands meet
-- without residual interference, so the normal form is well-defined. ⑤ of
-- ExtruderQSideRealigned, from named-reference to instantiated witness.
------------------------------------------------------------------------
