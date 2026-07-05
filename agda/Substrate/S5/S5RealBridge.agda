{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.S5.S5RealBridge — ⟡bridge-real: the WITNESSED transport
-- S5Real / S5RealConv ≅ Algebra.R.Trace.
--
-- The S5 regress-verdict subsystem builds a PRODUCTIVE CF trace (S5Real.CoTrace,
-- generalized over a generator carrier A) and its convergents (S5RealConv.conv-go),
-- and the R.Trace subsystem builds exactly the coinductive reals (RealTrace, conv-go,
-- twos = 2̄, sqrt2 = [1;2̄]). jea_pysim flags them IDENTICAL. Collapsing one would
-- delete the bridge between "S5 fuel-evaluation" and "the substrate's continued-
-- fraction reals". Instead (the KleinV4≅V₄ / S5MatrixBridge pattern) we WITNESS it —
-- but this bridge is COINDUCTIVE, so the stream equality is Bisim's _~_ and the finite
-- observations (take, convergent) are _≡_:
--
--   1. the transport `to : CoTrace ℕ → RealTrace` (coinductive, identity-on-observations)
--      + its round-trip `to (from r) ~ r`;
--   2. OBSERVATION TRANSPORT — `to` preserves every finite observation: `take` (the CF
--      prefix) and `convergent` (the rational pₙ/qₙ). So S5RealConv's convergents ARE the
--      substrate's convergents (convergent-agree) — the ℚ side is one theorem;
--   3. the NAMED-VALUE bridge (the punchline): `to S5.twos ~ Trace.twos` and
--      `to S5.sqrt2 ~ Trace.sqrt2` — S5's √2 IS the substrate's √2, up to bisimilarity.
--      "productive ⇒ ℝ" realised across both subsystems as the SAME real.
------------------------------------------------------------------------

module Substrate.S5.S5RealBridge where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq      using (_≡_; refl; cong)
open import Substrate.Foundation.List     using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)

import Substrate.S5.S5Real      as S5R
import Substrate.S5.S5RealConv  as S5C
import Substrate.Algebra.R.Trace as T
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)

------------------------------------------------------------------------
-- 1. the transport (coinductive; identity on head/tail) + round-trip up to ~.
------------------------------------------------------------------------
to : S5R.CoTrace ℕ → T.RealTrace
T.head (to r) = S5R.head r
T.tail (to r) = to (S5R.tail r)

from : T.RealTrace → S5R.CoTrace ℕ
S5R.head (from r) = T.head r
S5R.tail (from r) = from (T.tail r)

-- coinductive types have no η, so the round-trip is a BISIMILARITY, not ≡.
to-from : (r : T.RealTrace) → to (from r) ~ r
head~ (to-from r) = refl
tail~ (to-from r) = to-from (T.tail r)

------------------------------------------------------------------------
-- 2. OBSERVATION TRANSPORT: `to` preserves take (the CF prefix) and convergent.
------------------------------------------------------------------------
to-take : (n : ℕ) (r : S5R.CoTrace ℕ) → T.take n (to r) ≡ S5R.take n r
to-take zero    r = refl
to-take (suc n) r = cong (S5R.head r ∷_) (to-take n (S5R.tail r))

-- the convergent recurrence agrees through `to` — S5RealConv.recon q b r = q·b+r
-- IS Trace.conv-go's (head·p + p) update, so the folds coincide at every fuel.
conv-go-agree : (n p₁ q₁ p₀ q₀ : ℕ) (r : S5R.CoTrace ℕ)
              → T.conv-go n p₁ q₁ p₀ q₀ (to r) ≡ S5C.conv-go n p₁ q₁ p₀ q₀ r
conv-go-agree zero    p₁ q₁ p₀ q₀ r = refl
conv-go-agree (suc n) p₁ q₁ p₀ q₀ r =
  conv-go-agree n ((S5R.head r * p₁) + p₀) ((S5R.head r * q₁) + q₀) p₁ q₁ (S5R.tail r)

-- THE ℚ-SIDE THEOREM: S5's convergents ARE the substrate's convergents.
convergent-agree : (n : ℕ) (r : S5R.CoTrace ℕ)
                 → T.convergent n (to r) ≡ S5C.convergent n r
convergent-agree n r = conv-go-agree n (suc zero) zero zero (suc zero) r

------------------------------------------------------------------------
-- 3. THE NAMED-VALUE BRIDGE: S5's twos / √2 ARE the substrate's, up to ~.
------------------------------------------------------------------------
-- S5.twos loops through cycle-go two [] []; its transport is bisimilar to Trace.twos.
to-cycle-loop : to (S5R.cycle-go S5R.two [] []) ~ T.twos
head~ to-cycle-loop = refl
tail~ to-cycle-loop = to-cycle-loop

to-twos : to S5R.twos ~ T.twos
head~ to-twos = refl
tail~ to-twos = to-cycle-loop

to-sqrt2 : to S5R.sqrt2 ~ T.sqrt2
head~ to-sqrt2 = refl
tail~ to-sqrt2 = to-twos
