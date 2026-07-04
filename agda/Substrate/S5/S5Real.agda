{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- S5Real — ⟡N1b-Real. The regress verdict is NOT a non-termination proof
-- (correction #17, ADD 45): it is a PRODUCTIVE CF trace whose PERIOD is its
-- finite description — a real (a quadratic irrational), exactly as the
-- substrate's Algebra.R.Trace builds √2 = [1; 2̄] as a coinductive value
-- ("finite ⇒ ℚ, productive ⇒ ℝ").
--
-- ⟡H0: RealTrace is a coinductive record (head : ℕ, tail : RealTrace), ℕ-
-- specific. Here we generalize the SAME structure over the generator carrier
-- A (the combinator quotient); the substrate's RealTrace is the A = ℕ
-- instance (twos = cycle 2 [], sqrt2 = 1 ∷∞ twos). The regress verdict = the
-- periodic trace built from the detected period; value = the finite Trace
-- (S5EEA.done). BOTH are values — the finite-CF and periodic-CF SECTIONS of
-- the one coinductive carrier. No non-termination anywhere.
------------------------------------------------------------------------

module Substrate.S5.S5Real where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong; ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_) public

-- the coinductive productive CF trace over a carrier A (RealTrace generalized).
record CoTrace (A : Set) : Set where
  coinductive
  field
    head : A
    tail : CoTrace A
open CoTrace public

-- take: the first n digits — finite observation, recursion on fuel (the
-- productive stream is never forced past n). Mirrors RealTrace.take.
take : {A : Set} → ℕ → CoTrace A → List A
take zero    _ = []
take (suc n) r = head r ∷ take n (tail r)

------------------------------------------------------------------------
-- cycle: build the PERIODIC trace from a finite non-empty period (x₀ ∷ xs).
-- The tail eventually returns to the period start — the CF is periodic, the
-- period is its FINITE description. This IS the regress verdict.
------------------------------------------------------------------------
cycle-go : {A : Set} → A → List A → List A → CoTrace A
head (cycle-go x₀ xs [])       = x₀
tail (cycle-go x₀ xs [])       = cycle-go x₀ xs xs
head (cycle-go x₀ xs (y ∷ ys)) = y
tail (cycle-go x₀ xs (y ∷ ys)) = cycle-go x₀ xs ys

cycle : {A : Set} → A → List A → CoTrace A
cycle x₀ xs = cycle-go x₀ xs (x₀ ∷ xs)

------------------------------------------------------------------------
-- OBSERVABLE: the period reproduces. Taking (1 + length xs) digits of the
-- cycled trace gives back exactly the period — the finite description IS the
-- value's representation. (Stated for a concrete small period; the general
-- length lemma is take-cycle below.)
------------------------------------------------------------------------
open import Substrate.Foundation.List.Length using (length)   -- ⟡dedup: was a local re-derivation

-- taking the period-length prefix of the cycled remainder reproduces that
-- remainder, then loops — the key productivity/faithfulness observation.
take-cycle-go : {A : Set} (x₀ : A) (xs ys : List A)
              → take (length ys) (cycle-go x₀ xs ys) ≡ ys
take-cycle-go x₀ xs []       = refl
take-cycle-go x₀ xs (y ∷ ys) = cong (y ∷_) (take-cycle-go x₀ xs ys)

-- therefore the full period is reproduced by the cycle:
take-period : {A : Set} (x₀ : A) (xs : List A)
            → take (length (x₀ ∷ xs)) (cycle x₀ xs) ≡ x₀ ∷ xs
take-period x₀ xs = take-cycle-go x₀ xs (x₀ ∷ xs)

------------------------------------------------------------------------
-- The ℕ instance IS the substrate's RealTrace. twos = cycle 2 []; the CF of
-- √2's tail. (Convergents — 1/1,3/2,7/5,17/12 → √2 — are Algebra.R.Trace's
-- `convergent`, cited, not re-derived; the value is the periodic trace.)
------------------------------------------------------------------------
two : ℕ
two = suc (suc zero)

four : ℕ
four = suc (suc (suc (suc zero)))

twos : CoTrace ℕ
twos = cycle two []

_ : take four twos ≡ (two ∷ two ∷ two ∷ two ∷ [])
_ = refl

-- √2 = [1; 2̄] : a genuine irrational, finitely described — a VALUE, not a
-- failure to terminate. (regress = exactly this shape over the combinator
-- generator carrier: a finite period, cycled.) sqrt2's tail IS twos.
sqrt2 : CoTrace ℕ
head sqrt2 = suc zero
tail sqrt2 = twos

_ : take four sqrt2 ≡ (suc zero ∷ two ∷ two ∷ two ∷ [])
_ = refl
