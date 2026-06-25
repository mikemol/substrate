------------------------------------------------------------------------
-- Substrate.Algebra.Q.CrossMixBezout
--
-- A connection leaf coupling node 5 (HetQ / CrossMix — the ℚ
-- cross-multiplication cospan `ℚ-crossmix : CrossMix ℤ-div ℕ-div ℤ-mul`,
-- whose `cross` is the bilinear `s *ℤ (+ a)` product into ℤ) to node 2
-- (the Bézout / EEA spine — `bezout-ℤ : EEATrace a b g → BezoutℤWitness a b g`,
-- the oriented identity `s *ℤ (+ a) +ℤ t *ℤ (+ b) ≡ + g`).
--
-- CLAIM: the ℚ CrossMix cospan (ℤ-div by the identity bridge, ℕ-div by the
-- inclusion ℕ ↪ ℤ) is MEDIATED by the Bézout coefficients — cross-multiplication
-- IS the Bézout identity. Each Bézout summand `s *ℤ (+ a)` is, definitionally,
-- the cospan's own cross-term `cross ℚ-crossmix s a` (the A-element being the
-- Bézout coefficient, the B-element the carrier). Hence the Bézout fold's output
-- equation reads, with no rewriting, as a SUM OF TWO CROSS-TERMS equal to `+ g`;
-- for a coprime trace (g ≡ 1) it equals `+ 1` — the cross-multiplication of the
-- Bézout coefficients against (a , b) reconstructs the unit. The EEA/Bézout
-- spine is exactly the mediator the CrossMix cospan factors through.
--
-- All claims are refl / re-export plus the single transport of the existing
-- `bezout-ℤ` witness through the (definitional) `cross = s *ℤ (+ ·)` identity.
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.CrossMixBezout where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_; _+ℤ_)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (coprime-trace)
open import Substrate.Algebra.Wedge.CrossMul using (cross)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)

-- The two halves, brought in unrestricted (re-exported for downstream wiring).
open import Substrate.Algebra.Q.HetCrossMix using (ℤ-mul; ℚ-crossmix)

------------------------------------------------------------------------
-- 1. The cross-term of the ℚ cospan IS a Bézout summand (definitional).
--    `cross ℚ-crossmix s a` = (translate id-bridge s) *ℤ (translate ℕ↪ℤ a)
--                            = s *ℤ (+ a).
--    So with the A-element being a Bézout COEFFICIENT and the B-element the
--    carrier, the cospan's bilinear cross-term is exactly the Bézout summand.
------------------------------------------------------------------------

cross-summand : (s : ℤ) (a : ℕ) → cross ℚ-crossmix s a ≡ s *ℤ (+ a)
cross-summand s a = refl

------------------------------------------------------------------------
-- 2. The Bézout identity, read through `cross`. The fold's stored equation
--    `s *ℤ (+ a) +ℤ t *ℤ (+ b) ≡ + g` is DEFINITIONALLY the sum of the two
--    cospan cross-terms `cross ℚ-crossmix s a +ℤ cross ℚ-crossmix t b ≡ + g`.
--    This is the mediation: the cross-multiplication of the Bézout
--    coefficients against (a , b) reconstructs `+ g`.
------------------------------------------------------------------------

CrossmixBezout : ℕ → ℕ → ℕ → Set
CrossmixBezout a b g =
  Σ ℤ (λ s → Σ ℤ (λ t →
    (cross ℚ-crossmix s a +ℤ cross ℚ-crossmix t b) ≡ (+ g)))

-- Re-typing of the existing witness through the (refl) cross identity: the
-- Bézout fold's output IS a CrossMix mediation. No new proof — the two
-- predicates are definitionally equal, so the witness transports by id.
crossmix-from-trace : {a b g : ℕ} → EEATrace a b g → CrossmixBezout a b g
crossmix-from-trace t = bezout-ℤ t

-- The orientation made explicit: the same s, t, and equation, now NAMED as
-- a coefficient pair whose two cross-products sum to + g.
bezout-bridges-crossmix : {a b g : ℕ} → BezoutℤWitness a b g → CrossmixBezout a b g
bezout-bridges-crossmix w = w

------------------------------------------------------------------------
-- 3. The coprime case: the cross-multiplication of the Bézout coefficients
--    against a coprime pair reconstructs the UNIT (+ 1 = 1ℤ). The EEA trace
--    bottoming at 1 is the certificate; its Bézout coefficients are the two
--    A-elements whose cospan cross-terms sum to + 1.
------------------------------------------------------------------------

coprime-crossmix-unit : (a b : ℕ) → gcd-ℕ a b ≡ 1 → CrossmixBezout a b 1
coprime-crossmix-unit a b eq = crossmix-from-trace (coprime-trace a b eq)

-- Worked instance: a = 2, b = 3 are coprime, so there exist Bézout
-- coefficients s, t with cross ℚ-crossmix s 2 +ℤ cross ℚ-crossmix t 3 ≡ + 1.
crossmix-unit-2-3 : CrossmixBezout 2 3 1
crossmix-unit-2-3 = coprime-crossmix-unit 2 3 refl
