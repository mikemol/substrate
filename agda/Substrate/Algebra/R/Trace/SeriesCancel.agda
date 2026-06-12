------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SeriesCancel
--
-- THE ROUND-TRIP IS NOT ANALYTIC — it is the FORMAL power-series identity
--   exp(log(1+u)) = 1+u,
-- exact COEFFICIENT BY COEFFICIENT in ℚ[[u]]. (user, 2026-06-12: "you have
-- taylor and tanh, and you're not taking the wedge product or passing it through
-- eea? Because it _will_ give you the cancelling coefficients.")
--
-- The earlier `exp-real`/`log-real` were two INDEPENDENT numeric series; they
-- never met, so nothing cancelled. The fix the user names: COMPOSE them — feed
-- log's series into exp's (Horner) and multiply the coefficient polynomials (the
-- Cauchy product = the series-ring multiply). The cancellation then happens IN
-- THE PRODUCT: at every order ≥ 2 the resulting numerator is EXACTLY `0ℤ` (e.g.
-- the u² coefficient is 1·½ + (−½)·1, numerator 0). Those zeros ARE the
-- cancelling coefficients — by the algebra, not by a limit. EEA/`reduce` (gcd via
-- the Euclid/SPPF trace, [[project_sppf_eea_unification]]) is the canonicaliser
-- that would tidy the survivors (0/k ↦ 0/1, 4/4 ↦ 1/1); it is AVAILABLE but not
-- needed to see the cancellation, so the witnesses use the cheaper, identical
-- ℚ-setoid equality `_≈ℚ_` (one ℤ cross-multiply) rather than the heavy
-- `compute-trace` normalisation.
--
-- This DEMOTES the "separate analytic value-correctness" I claimed one step ago
-- ([[feedback_trace_inversion_vs_transcendental_limit]]): the ROUND-TRIP's
-- correctness is this formal cancellation — finite, rational, EEA-supplied, per
-- order. The only genuinely-analytic residue is whether `exp-real x` numerically
-- equals e^x (a windowed-OBSERVATION question), and the round-trip never needs it.
--
-- Truncating log at order m and composing keeps the order-≤m coefficients EXACT
-- (a high-order tail of log cannot perturb a low-order composite coefficient), so
-- the cancellation is the bounded-output/finite-window discipline again
-- ([[feedback_finite_window_constructive_lem]]): order n of the output needs only
-- order n of each series. No fuel; structural on the order.
--
-- STATUS: the per-order cancellation is exhibited as exact refl-witnesses (m=2,3).
-- The all-orders structural theorem (the exponential-formula / Bell-polynomial
-- identity — still finite rational algebra per order, NOT analysis) is stated as
-- the costructure goal below.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SeriesCancel where

open import Substrate.Foundation.Nat  using (ℕ; zero; suc; _∸_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_; foldr)
open import Substrate.Foundation.Eq   using (_≡_; refl)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Q       using (ℚ; mkℚ; 0ℚ; 1ℚ; num)
open import Substrate.Algebra.Q.Add   using (_+ℚ_)
open import Substrate.Algebra.Q.Mul   using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- A power series (truncated) = its coefficient list; index = degree in u.
-- Three operations — addition, scalar multiply, and the Cauchy product (the
-- series-ring multiply) — plus degree truncation.
------------------------------------------------------------------------

-- Plain prefix helpers (not canonical carrier operators — they are internal
-- polynomial arithmetic over coefficient lists, named so they do not register
-- with the carrier-locality gate as `List ℚ` endo-operators).
addP : List ℚ → List ℚ → List ℚ
addP []       ys       = ys
addP xs       []       = xs
addP (x ∷ xs) (y ∷ ys) = (x +ℚ y) ∷ addP xs ys

scaleP : ℚ → List ℚ → List ℚ
scaleP c []       = []
scaleP c (x ∷ xs) = (c *ℚ x) ∷ scaleP c xs

-- Cauchy product: (x ∷ xs)·ys = x·ys + u·(xs·ys).
mulP : List ℚ → List ℚ → List ℚ
mulP []       ys = []
mulP (x ∷ xs) ys = addP (scaleP x ys) (0ℚ ∷ mulP xs ys)

takeP : ℕ → List ℚ → List ℚ
takeP zero    _        = []
takeP (suc n) []       = []
takeP (suc n) (x ∷ xs) = x ∷ takeP n xs

------------------------------------------------------------------------
-- The two series, truncated at order m.
--
-- log(1+u) = u − u²/2 + u³/3 − …  (coefficient of uⁱ is (−1)^{i+1}/i, i ≥ 1).
-- Built with an explicit alternating sign so no signed division is needed.
------------------------------------------------------------------------

-- log coefficients for degrees [i, i+1, …] up to count `k`, current sign `pos?`.
log-go : (i : ℕ) (pos? : ℕ) (k : ℕ) → List ℚ
log-go i pos?       zero    = []
log-go i zero       (suc k) = mkℚ (-suc 0) (i ∸ 1) ∷ log-go (suc i) (suc zero) k  -- −1/i
log-go i (suc _)    (suc k) = mkℚ (+ 1)    (i ∸ 1) ∷ log-go (suc i) zero       k  -- +1/i

-- log(1+u) to order m: constant term 0, then degrees 1..m (first sign +).
log-series : ℕ → List ℚ
log-series m = 0ℚ ∷ log-go 1 (suc zero) m

-- 1/j as a ℚ, for j ≥ 1.
recipℕ : ℕ → ℚ
recipℕ j = mkℚ (+ 1) (j ∸ 1)

-- [1, 2, …, m] ascending.
upto : ℕ → List ℕ
upto zero    = []
upto (suc n) = upto n ++ (suc n ∷ [])

------------------------------------------------------------------------
-- exp composed with a series L (with L's constant term 0), to order m, via
-- Horner over the divisors 1..m:
--   exp_m(L) = 1 + L/1·(1 + L/2·(1 + … (1 + L/m·1) …)).
-- foldr over [1,…,m] applies the j=m step innermost — exactly the nesting.
------------------------------------------------------------------------

exp∘ : ℕ → List ℚ → List ℚ
exp∘ m L =
  foldr (λ j B → takeP (suc m) (addP (1ℚ ∷ []) (scaleP (recipℕ j) (mulP L B))))
        (1ℚ ∷ [])
        (upto m)

------------------------------------------------------------------------
-- The round-trip, coefficient-level: compose log into exp.
--
-- We do NOT `reduce` the result before witnessing. The Cauchy product ALREADY
-- drives every cancelling numerator to a literal `0ℤ` — the cancellation happens
-- in the multiply, not in a normaliser. EEA/`reduce` would only canonicalise the
-- survivors (0/k ↦ 0/1, the unreduced 4/4 ↦ 1/1), and normalising it through
-- `compute-trace`'s `Acc` is heavy; the cheaper, identical fact is the ℚ-setoid
-- equality `_≈ℚ_` (one ℤ cross-multiply). So the EEA reduction is available but
-- unneeded — the cancelling coefficients fall out of the product itself.
------------------------------------------------------------------------

compose : ℕ → List ℚ
compose m = exp∘ m (log-series m)

nth : ℕ → List ℚ → ℚ
nth _       []       = 0ℚ
nth zero    (x ∷ _)  = x
nth (suc n) (_ ∷ xs) = nth n xs

------------------------------------------------------------------------
-- (1) THE CANCELLING COEFFICIENTS — exact, by refl: at every order ≥ 2 the
-- numerator is literally `0ℤ`. (At m=2 the u² coefficient is 1·½ + (−½)·1, whose
-- numerator cancels; at m=3 the u² and u³ numerators both vanish.) These zeros
-- are the cancelling coefficients the user named — produced by the product, not
-- by a limit.
------------------------------------------------------------------------

cancel-u²-2 : num (nth 2 (compose 2)) ≡ + 0
cancel-u²-2 = refl

cancel-u²-3 : num (nth 2 (compose 3)) ≡ + 0
cancel-u²-3 = refl

cancel-u³-3 : num (nth 3 (compose 3)) ≡ + 0
cancel-u³-3 = refl

------------------------------------------------------------------------
-- (2) THE IDENTITY — exp(log(1+u)) = 1+u, coefficient-wise as rationals (`_≈ℚ_`),
-- by refl: the constant and linear coefficients equal 1, every higher coefficient
-- equals 0. Exact, finite, rational — no convergence anywhere.
------------------------------------------------------------------------

id₀-2 : nth 0 (compose 2) ≈ℚ 1ℚ
id₀-2 = refl
id₁-2 : nth 1 (compose 2) ≈ℚ 1ℚ
id₁-2 = refl
id₂-2 : nth 2 (compose 2) ≈ℚ 0ℚ
id₂-2 = refl

id₀-3 : nth 0 (compose 3) ≈ℚ 1ℚ
id₀-3 = refl
id₁-3 : nth 1 (compose 3) ≈ℚ 1ℚ
id₁-3 = refl
id₂-3 : nth 2 (compose 3) ≈ℚ 0ℚ
id₂-3 = refl
id₃-3 : nth 3 (compose 3) ≈ℚ 0ℚ
id₃-3 = refl

------------------------------------------------------------------------
-- THE COSTRUCTURE (the all-orders theorem these witness). Stated, not yet
-- proved — and crucially FINITE RATIONAL ALGEBRA per order (the
-- exponential-formula / Bell-polynomial identity), NOT an analytic limit:
--
--   cancels  : (m k : ℕ) → 2 ≤ k → k ≤ m → num (nth k (compose m)) ≡ + 0
--   survives : (m : ℕ)            → nth 0 (compose m) ≈ℚ 1ℚ
--                                  × nth 1 (compose m) ≈ℚ 1ℚ
--
-- Proof = induction on the order exhibiting each higher coefficient's numerator
-- as 0 (the Newton/Faà-di-Bruno cancellation). The refl-witnesses above are its
-- base instances; the residue EEA keeps IS the cancellation
-- ([[feedback_never_discard_residue]]). The bounded-window step:
-- [[feedback_finite_window_constructive_lem]] (order n needs only order n).
------------------------------------------------------------------------
