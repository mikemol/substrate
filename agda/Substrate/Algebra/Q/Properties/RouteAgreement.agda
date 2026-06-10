------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.RouteAgreement
--
-- The exp-chart certificate (and an honest accounting of what it is worth).
--
-- ℚ has decidable equality (`_≟ℚ_`), so by Hedberg its identity paths are
-- contractible: `reduce a ≡ reduce b` is a PROPOSITION. Hence the two route
-- proofs agree:
--
--   routes-agree : canonical-respects-≈ hab ≡ canonical-respects-≈-bezout hab
--
-- READ THIS AS A CHART, NOT A VERDICT. The agreement is VACUOUS as
-- "convergence": any two proofs of `reduce a ≡ reduce b` are equal — a third,
-- deliberately silly one would be too. It certifies the CODOMAIN is a prop, not
-- that the shape route and the Bézout route share content. The real convergence
-- is structural: the shared assembly (Q.Properties.Uniqueness) and the decision
-- that computes the same verdict (Q.Properties.Decidable).
--
-- The PHASE-WITNESS triangle below shows the contractible-paths chart is a
-- CHOICE, not the territory: raw 2/4 and 1/2 are ≈ℚ-equal AND same-reduced AND
-- propositionally DISTINCT. The reduced/quotient chart collapses them; the raw-ℚ
-- chart keeps them apart. All three hold at once only because each is read in
-- its own chart — `--without-K` is the phase index that keeps this from
-- exploding (drop the index and you have "equal and not equal"). Hedberg proves
-- one chart of the atlas has contractible paths; it forbids no other.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.RouteAgreement where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Reduce using (reduce)
open import Substrate.Algebra.Q.DecidableEq using (_≟ℚ_)
open import Substrate.Algebra.Q.Properties.Canonical using (canonical-respects-≈)
open import Substrate.Algebra.Q.Properties.CanonicalBezout using (canonical-respects-≈-bezout)

------------------------------------------------------------------------
-- 1. The chart certificate: ℚ is a set (Hedberg on _≟ℚ_).
------------------------------------------------------------------------

ℚ-isSet : {p q : ℚ} (r s : p ≡ q) → r ≡ s
ℚ-isSet = Decidable⇒UIP _≟ℚ_

-- The two routes' proofs are equal — because the codomain is a prop.
routes-agree : {a b : ℚ} (hab : a ≈ℚ b) →
               canonical-respects-≈ {a} {b} hab ≡ canonical-respects-≈-bezout {a} {b} hab
routes-agree {a} {b} hab =
  ℚ-isSet (canonical-respects-≈ {a} {b} hab) (canonical-respects-≈-bezout {a} {b} hab)

------------------------------------------------------------------------
-- 2. The phase-witness triangle: the OTHER chart does not collapse.
--    2/4 and 1/2 — ≈ℚ-equal, same reduced form, yet distinct raw points.
------------------------------------------------------------------------

equiv : mkℚ (+ 2) 3 ≈ℚ mkℚ (+ 1) 1            -- related by ≈ℚ
equiv = refl

same-reduced : reduce (mkℚ (+ 2) 3) ≡ reduce (mkℚ (+ 1) 1)   -- one canonical point
same-reduced = refl

raw-distinct : ¬ (mkℚ (+ 2) 3 ≡ mkℚ (+ 1) 1)  -- two distinct RAW points
raw-distinct eq = +2≢+1 (cong num eq)
  where
    +2≢+1 : ¬ ((+ 2) ≡ (+ 1))
    +2≢+1 ()
