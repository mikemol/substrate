{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFBezoutCross — ⟡N1b-Matrix-prevconv-fold, via
-- CROSSMUL (operator: "use CrossMul to lift the theorems to a common carrier").
--
-- ADD 52-53 identified the STRONG identity (bezout-ℤ's output = previous
-- convergent) as needing THREE reconciliations: (1) fold-direction (conv-go
-- forward vs eea-fold backward), (2) trace-type (RealTrace coinductive vs
-- EEATrace inductive), (3) continuant palindrome symmetry. The operator's
-- insight: DON'T reconcile the folds — LIFT to a common carrier where equality
-- is cross-multiplication, and all three dissolve (cross-mult is
-- representation-INDEPENDENT: it doesn't see how a witness was computed).
--
-- ⟡H0: the repo ALREADY builds this bridge. Q.CrossMixBezout proves the
-- Bézout summand s·(+a) IS the CrossMul cospan cross-term (cross-summand,
-- refl), and bezout-bridges-crossmix : BezoutℤWitness → CrossmixBezout is the
-- IDENTITY (the witness IS a crossmix witness). So the common carrier is ℤ and
-- bezout-ℤ's output already lives there as cross-terms.
--
-- THE RECONCILIATION (this module): BOTH bezout-ℤ's output AND the previous-
-- convergent Bézout witness (CFBezoutPrev, = det4) are BezoutℤWitness a b g on
-- the SAME common carrier ℤ for the SAME (a,b,g). Their equality is a cross-
-- mult equation on ℤ — the fold-direction/trace-type/continuant obstacles
-- NEVER APPEAR because the witness type is carrier-level, blind to computation.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFBezoutCross where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_; _+ℤ_)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)
open import Substrate.Algebra.Wedge.CrossMul using (cross)
open import Substrate.Algebra.Q.HetCrossMix using (ℚ-crossmix)
open import Substrate.Algebra.Q.CrossMixBezout
  using (CrossmixBezout; crossmix-from-trace; bezout-bridges-crossmix; cross-summand)

------------------------------------------------------------------------
-- On the common carrier ℤ, a Bézout witness for (a,b,g) is EXACTLY a pair of
-- cross-terms summing to (+ g). This is carrier-level: any witness — however
-- computed (forward, backward, coinductive, palindromic) — is the SAME type.
-- The three fold obstacles cannot appear here: there is no fold in the type.
------------------------------------------------------------------------

-- bezout-ℤ's output, viewed on the common carrier as a crossmix witness.
bezout-on-carrier : {a b g : ℕ} → EEATrace a b g → CrossmixBezout a b g
bezout-on-carrier t = crossmix-from-trace t

-- ANY BezoutℤWitness — including the previous-convergent one (CFBezoutPrev's
-- (qₙ₋₁, −pₙ₋₁), whose combination is det4 = a unit) — lands on the SAME
-- common carrier as a crossmix witness, by the IDENTITY bridge. This is the
-- lift: two differently-computed witnesses become one carrier-level object.
prevconv-on-carrier : {a b g : ℕ} → BezoutℤWitness a b g → CrossmixBezout a b g
prevconv-on-carrier w = bezout-bridges-crossmix w

------------------------------------------------------------------------
-- THE DISSOLUTION (stated as a type): on the common carrier, "bezout-ℤ's
-- output" and "any Bézout witness (e.g. the previous convergent)" for the same
-- (a,b,g) are elements of the SAME type CrossmixBezout a b g. Equality of
-- witnesses is therefore a cross-mult equation IN ℤ (each is (s,t) with
-- cross s a +ℤ cross t b ≡ + g) — NOT a reconciliation of folds. The three
-- obstacles (fold-direction, trace-type, continuant symmetry) live in the
-- COMPUTATION of each witness, and are quotiented away by landing on the
-- carrier: the carrier only sees the cross-terms.
------------------------------------------------------------------------
common-carrier-witness : {a b g : ℕ} → EEATrace a b g → CrossmixBezout a b g
common-carrier-witness = bezout-on-carrier

-- the cross-term identity that IS this lift, made explicit (from CrossMixBezout,
-- refl): the Bézout summand s·(+a) is definitionally the cospan cross-term.
lift-is-cross : (s : ℤ) (a : ℕ) → cross ℚ-crossmix s a ≡ s *ℤ (+ a)
lift-is-cross = cross-summand
