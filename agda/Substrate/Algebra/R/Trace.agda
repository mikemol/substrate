------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace
--
-- ℝ in the substrate's existing terms: a real is a PROCESS that Wedges. A
-- computer never holds a real — it reasons about one. `RealTrace` is the
-- reasoning: a coinductive continued-fraction / Euclidean-Gauss stream, the
-- NON-TERMINATING dual of the inductive `Algebra.Nat.GCD.EEATrace`.
--
-- The Euclidean algorithm on integers TERMINATES (`EEATrace` reaches `base` at
-- the gcd) — a finite continued fraction, i.e. a RATIONAL. On a real it never
-- terminates: the same Wedge step (digit = quotient, residual = the Gauss-map
-- image) repeated forever. So ℚ-Canonical's CF shape ([[project_sppf_eea_unification]])
-- and this share one machinery; finite ⇒ ℚ, productive ⇒ ℝ.
--
-- "Reasoning about ℝ" is finite observation: `take` (the CF-digit prefix = the
-- provenance) and `convergent` (the rational pₙ/qₙ that approximates it). We
-- exhibit √2 = [1;2,2,2,…] — a genuine irrational with a finite description —
-- and reason about it without ever holding it. (B1 of the substrate-ℝ arc; B2+
-- add the Cauchy modulus, field ops, and analytic exp/log — see
-- [[project_substrate_real_arc]].)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_; _*_; _≤_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Nat.GCD.Wedge    using (Wedge; quotient)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)

------------------------------------------------------------------------
-- The carrier: the coinductive Euclidean trace. One node = one Wedge step's
-- quotient (a CF digit); `tail` is the residual process (never reaches base).
------------------------------------------------------------------------

record RealTrace : Set where
  coinductive
  field
    head : ℕ           -- the CF digit aᵢ = the Euclidean quotient at this step
    tail : RealTrace   -- the residual real (the Gauss-map image)
open RealTrace public

-- Regularity: every CF digit ≥ 1 — the coinductive predicate dual to the
-- carrier, under which the convergent denominators grow (proved in .Properties).
record AllPos (r : RealTrace) : Set where
  coinductive
  field hd : 1 ≤ head r
        tl : AllPos (tail r)
open AllPos public

------------------------------------------------------------------------
-- Finite observation 1 — the first n CF digits (the provenance prefix).
-- Recursion is on the fuel `n` (terminating), not on the coinductive stream.
------------------------------------------------------------------------

take : ℕ → RealTrace → List ℕ
take zero    _ = []
take (suc n) r = head r ∷ take n (tail r)

------------------------------------------------------------------------
-- Finite observation 2 — the n-th convergent pₙ/qₙ ∈ ℚ, by the CF recurrence
-- pₖ = aₖ·pₖ₋₁ + pₖ₋₂, qₖ = aₖ·qₖ₋₁ + qₖ₋₂. State = the last two (p,q) columns.
------------------------------------------------------------------------

conv-go : ℕ → ℕ → ℕ → ℕ → ℕ → RealTrace → ℕ × ℕ
conv-go zero    p₁ q₁ _  _  _ = (p₁ , q₁)
conv-go (suc n) p₁ q₁ p₀ q₀ r =
  conv-go n ((head r * p₁) + p₀) ((head r * q₁) + q₀) p₁ q₁ (tail r)

convergent : ℕ → RealTrace → ℕ × ℕ
convergent n r = conv-go n 1 0 0 1 r   -- seed (p₋₁,q₋₁,p₋₂,q₋₂) = (1,0,0,1)

------------------------------------------------------------------------
-- A genuine IRRATIONAL with a finite description: √2 = [1; 2,2,2,…].
------------------------------------------------------------------------

twos : RealTrace
head twos = 2
tail twos = twos

sqrt2 : RealTrace
head sqrt2 = 1
tail sqrt2 = twos

------------------------------------------------------------------------
-- The bridge to the existing machinery: the quotients ALONG an EEATrace are a
-- FINITE continued fraction — the CF of a rational. `RealTrace` is exactly this
-- reading, never reaching `base`. One Wedge step; finite ⇒ ℚ, infinite ⇒ ℝ.
------------------------------------------------------------------------

digits-of-EEA : {a b g : ℕ} → EEATrace a b g → List ℕ
digits-of-EEA (base _)     = []
digits-of-EEA (step _ w t) = quotient w ∷ digits-of-EEA t

------------------------------------------------------------------------
-- Worked: we never hold √2, but we reason about it — its CF prefix and its
-- convergents 1/1, 3/2, 7/5, 17/12 → √2 (17/12 = 1.41666…; √2 = 1.41421…).
------------------------------------------------------------------------

_ : take 4 sqrt2 ≡ (1 ∷ 2 ∷ 2 ∷ 2 ∷ [])
_ = refl

_ : convergent 4 sqrt2 ≡ (17 , 12)
_ = refl
