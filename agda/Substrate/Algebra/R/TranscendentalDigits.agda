------------------------------------------------------------------------
-- Substrate.Algebra.R.TranscendentalDigits
--
-- "On what computer could you prove exp-real x numerically equals eˣ? That's an
--  infinitely long number under any binary-mappable set of digits. So don't map
--  to binary digits. We've already defined π. We've already defined i. Those are
--  your digits." (user, 2026-06-12)
--
-- This dissolves the LAST hedge — my "genuinely-analytic value-correctness
-- residue". The question "does exp-real x equal eˣ to all binary digits?" is not
-- hard, it is INCOHERENT: eˣ is transcendental, hence infinite under ANY
-- positional digit basis, so the question is the binary-digit FORCING trap (the
-- LEM problem, [[feedback_finite_window_constructive_lem]]) reimported one level
-- up. You can never compute it; you must not try.
--
-- The escape is to change the BASIS. π, i, e are not numbers awaiting
-- approximation — they are the DIGITS of a transcendental presentation, in which:
--   • e is a suspended GENERATOR ([[feedback_suspended_generators_not_approximations]])
--     — here its regular continued fraction (Euler), an exact finite description
--     of an infinite object. Its "value" IS the generator; nothing to force.
--   • π and i are RATIONAL in the TURN basis: the angle π-radians is ½ turn and
--     π/2-radians (the argument of i) is ¼ turn. The irrationality was a
--     RADIAN/binary artifact ([[feedback_transcendental_phase_is_loop_fact]]).
--
-- And the transcendental IDENTITIES become FINITE relations among these digits:
-- i² = e^{iπ} is ¼ + ¼ = ½ (two quarter-turns = a half-turn), and e^{2iπ} = 1 is
-- ½ + ½ = 1 turn ≡ 0 on the loop ℝ/ℤ (Algebra.R.Circle). The half-turn is the
-- order-2 ANTIPODE = −1, whose F₂ shadow is `Verdict.Phase.negBoth-invol`
-- (referenced, not imported — Phase sits above Algebra.R). No limit, no forcing,
-- no analytic residue anywhere in the substrate-ℝ arc.
--
-- `e-real` IS e — the adopted Euler-CF generator-presentation. Per the digit
-- basis above, e is the generator; there is no privileged "true e" (a Taylor
-- generator, a digit string) that `e-real` must be PROVEN equal to. (An earlier
-- version of this header hedged exactly that — "agrees with the Taylor window but
-- isn't proven equal to it" — which was the forcing reflex once more: it presumes
-- a true-value to match. There is none to match; the generator is the number.)
-- The only generator-equality that IS a theorem is presentation-uniqueness within
-- a coalgebra — `Final.ana-unique`/`self-unfold` — and that is routine, not a
-- frontier. `π-turns`/`i-turns` are the ANGLES in turns — it is the angle in the
-- turn unit that is rational, not the bare number π.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.TranscendentalDigits where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Z       using (ℤ; +_)
open import Substrate.Algebra.Q       using (ℚ; mkℚ; 1ℚ)
open import Substrate.Algebra.Q.Add   using (_+ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

open import Substrate.Algebra.R.Trace        using (RealTrace; take)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Bisim  using (cons)

------------------------------------------------------------------------
-- e — the DIGIT, as a suspended generator. Euler's regular continued fraction
-- e = [2; 1,2,1, 1,4,1, 1,6,1, …]: a leading 2, then blocks (1, 2k, 1), k = 1,2,…
-- The state is (phase ∈ {0,1,2}, k); productivity is automatic (`unfold`).
------------------------------------------------------------------------

e-step : (ℕ × ℕ) → ℕ × (ℕ × ℕ)
e-step (zero        , k) = 1     , (suc zero       , k)
e-step (suc zero    , k) = k + k , (suc (suc zero) , k)       -- the 2k digit
e-step (suc (suc _) , k) = 1     , (zero           , suc k)

e-real : RealTrace
e-real = cons 2 (unfold e-step (zero , 1))

-- The generator emits Euler's CF, by construction — a sanity check that the
-- `unfold` produces the digits intended, NOT a verification of e against any
-- external "true" value (there is none to verify against):
e-real-window : take 6 e-real ≡ 2 ∷ 1 ∷ 2 ∷ 1 ∷ 1 ∷ 4 ∷ []
e-real-window = refl

------------------------------------------------------------------------
-- π and i — the DIGITS, rational in the turn basis.
------------------------------------------------------------------------

-- the angle π-radians, in turns = ½ (the half-period / the order-2 antipode).
π-turns : ℚ
π-turns = mkℚ (+ 1) 1

-- the angle of i (π/2-radians), in turns = ¼ (the quarter-turn; order 4).
i-turns : ℚ
i-turns = mkℚ (+ 1) 3

------------------------------------------------------------------------
-- The transcendental identities, as FINITE rational relations among the digits.
------------------------------------------------------------------------

-- i² = e^{iπ}:  two quarter-turns make a half-turn.  ¼ + ¼ = ½.
i²≡eⁱᵖ : (i-turns +ℚ i-turns) ≈ℚ π-turns
i²≡eⁱᵖ = refl

-- e^{2iπ} = 1:  the half-turn doubles to a full turn ≡ 0 on the loop ℝ/ℤ.  ½ + ½ = 1.
-- (The loop identification 1 ≡ 0 is `Circle.toS¹`; the antipode = −1 is the F₂
-- shadow `Verdict.Phase.negBoth-invol`.)
e²ⁱᵖ≡1 : (π-turns +ℚ π-turns) ≈ℚ 1ℚ
e²ⁱᵖ≡1 = refl
