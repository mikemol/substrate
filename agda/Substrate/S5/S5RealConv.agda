{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- S5RealConv — ⟡N1b-Real-conv. The generator→CF-digit map + convergents.
-- Closes ADD 46's remaining representation item: a combinator regress
-- (a CoTrace over the generator carrier) becomes a ℕ continued fraction via
-- a digit map, and its convergents pₖ/qₖ are computed by the CF recurrence —
-- which IS the DivStr recon fold (⟡H0: conv-go's update (head r * p₁) + p₀ is
-- literally recon (head r) p₁ p₀ under ℕ-div.recon q b r = q*b+r, verified in
-- Wedge.agda:154 and R/Trace.agda:71). Reproduces the substrate's convergent
-- (seeds (1,0,0,1)); the √2 ground truth 17/12 checks by refl.
------------------------------------------------------------------------

module Substrate.S5.S5RealConv where

open import Substrate.S5.S5Verdict using (_≡_; refl; ℕ; zero; suc)
open import Substrate.S5.S5Real using (CoTrace; head; tail; take; cycle; List; []; _∷_)
import Substrate.S5.S5Real as S5R   -- for the ⟡def-eq constant witnesses below
open import Substrate.Foundation.Nat     using (_+_; _*_)
open import Substrate.Foundation.Product using (_×_; _,_) renaming (proj₁ to fst; proj₂ to snd)

------------------------------------------------------------------------
-- generator → CF digit. The combinator generator carrier A is abstract here;
-- `digit : A → ℕ` assigns each generator its CF digit (its size/rank/interned
-- fingerprint on the Python side). comap pushes it along the productive trace.
------------------------------------------------------------------------
comap : {A : Set} → (A → ℕ) → CoTrace A → CoTrace ℕ
head (comap f r) = f (head r)
tail (comap f r) = comap f (tail r)

------------------------------------------------------------------------
-- recon (ℕ-div): recon q b r = q·b + r. The convergent step IS this.
------------------------------------------------------------------------
recon : ℕ → ℕ → ℕ → ℕ
recon q b r = (q * b) + r

------------------------------------------------------------------------
-- convergents, reproducing the substrate's conv-go (seeds (1,0,0,1)). The
-- numerator update p₁' = recon (head r) p₁ p₀ and denominator q₁' = recon
-- (head r) q₁ q₀ — the CF recurrence AS recon folding.
------------------------------------------------------------------------
conv-go : ℕ → ℕ → ℕ → ℕ → ℕ → CoTrace ℕ → (ℕ × ℕ)
conv-go zero    p₁ q₁ _  _  _ = (p₁ , q₁)
conv-go (suc n) p₁ q₁ p₀ q₀ r =
  conv-go n (recon (head r) p₁ p₀) (recon (head r) q₁ q₀) p₁ q₁ (tail r)

convergent : ℕ → CoTrace ℕ → (ℕ × ℕ)
convergent n r = conv-go n (suc zero) zero zero (suc zero) r

-- the convergent step IS recon (the DivStr fold) — by definition, refl.
recon-is-conv-step : (a p₁ p₀ : ℕ) → recon a p₁ p₀ ≡ (a * p₁) + p₀
recon-is-conv-step a p₁ p₀ = refl

------------------------------------------------------------------------
-- GROUND TRUTH: √2 = [1; 2̄]. Its 4th convergent is 17/12 (the substrate's own
-- test, R/Trace.agda:107). Built here from cycle over ℕ digits.
------------------------------------------------------------------------
two : ℕ
two = suc (suc zero)

twos : CoTrace ℕ
twos = cycle two []

sqrt2 : CoTrace ℕ
head sqrt2 = suc zero
tail sqrt2 = twos

-- 17 and 12 as ℕ (generated, no hand-miscount)
n17 : ℕ
n17 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (zero)))))))))))))))))
n12 : ℕ
n12 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (zero))))))))))))

four : ℕ
four = suc (suc (suc (suc zero)))

-- ⟡def-eq: S5RealConv's ground-truth constants ARE S5Real's — the two modules
-- name the SAME √2 digits, witnessed (not merely re-typed by coincidence).
two≡  : two  ≡ S5R.two
two≡  = refl
four≡ : four ≡ S5R.four
four≡ = refl

-- the 4th convergent of √2 computes to 17/12 — BY REFL. The regress value's
-- convergents CONVERGE (a real), the reframe (ADD 45) realized numerically.
sqrt2-convergent-4 : convergent four sqrt2 ≡ (n17 , n12)
sqrt2-convergent-4 = refl
