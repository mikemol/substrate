------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarGraded  (Ξ★.g)
--
-- GRADED center-is-★: the residual CenterIsStar (Ξ★.3) flagged. There the
-- cross-carrier tie was a CrossMix at the CLEAN extreme (square-zero R, cross
-- term → z everywhere = the bridge-null / orthogonal correspondence). Ξ★.g is
-- the GRADED case CrossMul defers: a richer common carrier (the N-complex
-- three-mul, degree-3 nilpotent) in which the SAME CrossMix cospan has cross
-- terms of VARYING nilpotency degree — the degree IS the cost of the
-- obstruction (the off-balance Wheatstone coupling), not a binary wall.
--
--   * η ⊗ η  ↦  η·η = sq : a NONZERO nilpotent of degree 2 — a graded
--     OBSTRUCTION (the strands interfere; the coupling carries current; cost = 2).
--   * η ⊗ sq ↦  η·sq = 𝟘 = z : a CLEAN pair (degree 0) — back to the bridge-null
--     / orthogonal correspondence of Ξ★.3 (the witness/centre, coupling null).
--
-- Same cospan, two grades: that IS graded coherence. The bridge-null (Ξ★.3) is
-- the degree-0 extreme of this same picture; here the obstruction is measured,
-- not absent.
--
-- Still residual (honest): a NUMERAL carrier (ℤ/p^k via Quotient.CRT, the CRT
-- instance) where the degree varies with actual conductance imbalance, and the
-- projective ℙ¹ center↔periphery exchange. This abstract N-complex gives the
-- graded STRUCTURE (degree-as-cost) without numerals, matching two-mul's style.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarGraded where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge.NComplex using (Three; 𝟘; η; sq; three-div; three-mul)
open import Substrate.Algebra.Wedge.Bridge using (id-bridge)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)

------------------------------------------------------------------------
-- The graded cospan: both strands embed (identically) into the N-complex.
------------------------------------------------------------------------

graded-mix : CrossMix three-div three-div three-mul
graded-mix = record { embA = id-bridge three-div ; embB = id-bridge three-div }

------------------------------------------------------------------------
-- The cross terms, and their grades.
------------------------------------------------------------------------

-- η ⊗ η = sq : nonzero, degree-2 nilpotent — the GRADED obstruction (cost 2).
obstruction-cross : cross graded-mix η η ≡ sq
obstruction-cross = refl

graded-obstruction : Coherent graded-mix η η     -- sq² = 𝟘 : nilpotent of degree 2
graded-obstruction = 1 , refl

-- η ⊗ sq = 𝟘 : the CLEAN pair (degree 0) — the bridge-null / centre of Ξ★.3.
clean-cross : cross graded-mix η sq ≡ 𝟘
clean-cross = refl

clean-pair : Coherent graded-mix η sq            -- already z : degree 0
clean-pair = 0 , refl
