{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderNfGradedRealigned — ⟡nf-graded: the
-- GRADED-OBSTRUCTION normal form (the non-clean case ExtruderNfCrossRealigned
-- scoped out). A normal form WITH residual interference: the two strands
-- (reduction, peel) leave a cross term that is nilpotent of degree n > 1 — a
-- genuine graded obstruction (dⁿ = 0, but d ≠ 0), its degree the COST of
-- resolving the residual redex.
--
-- The substrate ALREADY NAMES this center: Wedge.CrossMulGraded (⊙.c5b) embeds
-- Two → M₂ so cross(ε,ε) = e₁₁·e₁₂ = e₁₂, a NONZERO degree-2 nilpotent, while
-- other pairs stay clean (degree 0). So ⟡nf-graded is an INSTANCE, not a build:
-- the clean Nf (ExtruderNfCrossRealigned) is coherent-everywhere over two-mul;
-- the graded Nf is coherent-graded over M₂ — SAME Coherent, VARYING degree.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderNfGradedRealigned where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.Wedge.Mul using (Two; ε; two-div) renaming (𝟘 to t0)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)
open import Substrate.Algebra.Wedge.Wedderburn using (M2; M2-mul-str; e₁₂; 𝟎)
open import Substrate.Algebra.Wedge.CrossMulGraded
  using (mix-M2; coherent-graded; cross-εε; cross-εε-not-clean)

------------------------------------------------------------------------
-- THE GRADED-OBSTRUCTION Nf cospan = mix-M2 (Two → M₂, the Wedderburn corner).
-- FUSepQNf's redW/peelW strands embed into M₂ instead of the square-zero carrier;
-- the cross term of a live reduction-residue (ε) and a live peel-residue (ε) is
-- now the NONZERO corner e₁₂ — the residual redex that peeling+reducing left.
------------------------------------------------------------------------
nf-graded-cospan : CrossMix two-div two-div M2-mul-str
nf-graded-cospan = mix-M2

nf-graded-cross : Two → Two → M2
nf-graded-cross = cross nf-graded-cospan

------------------------------------------------------------------------
-- STILL COHERENT (the normal form EXISTS — the residual is nilpotent, it resolves
-- in finitely many steps), but the degree VARIES: clean pairs are degree 0, the
-- (ε,ε) live-live pair is degree 2. The degree IS the cost of the residual redex.
------------------------------------------------------------------------
nf-graded-coherent : (a b : Two) → Coherent nf-graded-cospan a b
nf-graded-coherent = coherent-graded

-- the interference is REAL: the (ε,ε) cross is the named obstruction e₁₂ ...
nf-obstruction : cross nf-graded-cospan ε ε ≡ e₁₂
nf-obstruction = cross-εε

-- ... and it is NOT clean (degree 0) — unlike the ExtruderNfCrossRealigned case,
-- this normal form genuinely carried a residual redex. The either/or "clean vs
-- obstructed Nf" is not a choice: it is the DEGREE of the coherent cross term,
-- 0 (clean, ExtruderNfCrossRealigned) or n>1 (graded, here) — one invariant.
nf-genuinely-graded : cross nf-graded-cospan ε ε ≡ 𝟎 → ⊥
nf-genuinely-graded = cross-εε-not-clean

------------------------------------------------------------------------
-- THE INVARIANT (dissolving clean-vs-graded): a normal form's well-definedness is
-- the COHERENCE of the reduction×peel cross term (it is nilpotent — resolves in
-- finite steps); its CLEANNESS is the DEGREE of that nilpotency. Degree 0 = clean
-- (ExtruderNfCrossRealigned, two-mul); degree n>1 = graded obstruction (here, M₂).
-- Not two kinds of Nf — one coherent cross, graded by residual cost. The two
-- Nf modules are the degree-0 and degree-2 poles of ONE CrossMul invariant.
------------------------------------------------------------------------
