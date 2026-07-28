------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.EEAReduce
--
-- CONNECTION LEAF (1 <-> 8): the EEA fold-table HUB meets the ℚ-setoid /
-- reduce node. One half is `WitnessTower.EEAFoldTable` read through
-- `Nat.GCD.Fold` — ONE EEA trace, `gcd-trace a b : EEATrace a b (gcd-ℕ a b)`,
-- whose FORGETFUL fold `gcd-fold` collapses to the terminal residue g
-- (`gcd-fold-correct : gcd-fold t ≡ g`). The other half is `Algebra.Q.Reduce`
-- / `Algebra.Q.Reduction`, where `reduce q` divides num and den by
-- `gcd-of-ℚ q = gcd-ℕ (abs-ℤ (num q)) (denominator q)` using the cofactors
-- KEPT by `gcd-divides-left` / `gcd-divides-right`.
--
-- CLAIM: the EEA fold-table's gcd (and the Bézout cofactors it carries) are the
-- PRECISE tools that reduce a rational to lowest terms with NO new division.
-- The number `reduce` divides by is exactly the trace's forgetful fold
-- (`reduce-divisor-is-gcd-fold` below: gcd-of-ℚ q ≡ gcd-fold (gcd-trace …)),
-- and the cofactors num/g, den/g are the divisibility witnesses the SAME trace
-- already projects (`gcd-divides-left/right`, "we never discard residue").
-- Uniqueness of the reduced form has a SECOND route beyond Bézout: when the gcd
-- index is pinned to 1 (coprime), `cf-injective` makes the continued-fraction
-- shape injective — two coprime ratios with the same CF shape are equal. Both
-- routes read the same `EEATrace`.
--
-- Zero postulates, --safe --without-K. Re-export + refl + ONE small bridge lemma.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.EEAReduce where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)

open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; denominator)

open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace; coprime-trace)
open import Substrate.Algebra.Nat.GCD.Fold using (gcd-fold; gcd-fold-correct)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)
open import Substrate.Algebra.Nat.GCD.CFInjective using (cf-injective)

open import Substrate.Algebra.Q.Reduction using (abs-ℤ; gcd-of-ℚ; is-reduced)
open import Substrate.Algebra.Q.Reduce using (reduce)

------------------------------------------------------------------------
-- 1. THE BRIDGE LEMMA. The number `reduce` divides by — `gcd-of-ℚ q` — is the
--    EEA fold-table's FORGETFUL fold of the gcd-trace. `gcd-of-ℚ q` is, by
--    definition, `gcd-ℕ (abs-ℤ (num q)) (denominator q)`; `gcd-fold-correct`
--    says the forgetful fold of ANY EEATrace returns its terminal index g, and
--    `gcd-trace a b : EEATrace a b (gcd-ℕ a b)` pins that index to `gcd-ℕ a b`.
--    So the divisor `reduce` uses IS the trace residue — no separate gcd, no
--    new division.
------------------------------------------------------------------------

reduce-divisor-is-gcd-fold :
  (q : ℚ) →
  gcd-of-ℚ q ≡ gcd-fold (gcd-trace (abs-ℤ (num q)) (denominator q))
reduce-divisor-is-gcd-fold q =
  sym (gcd-fold-correct (gcd-trace (abs-ℤ (num q)) (denominator q)))

------------------------------------------------------------------------
-- 2. THE COFACTORS ARE THE KEPT RESIDUES. `reduce` consumes precisely the two
--    divisibility witnesses `gcd-divides-left/right` give (num = qn·g,
--    den = qd·g); the quotients qn, qd ARE the reduced numerator/denominator
--    magnitudes. We name them here to make the "no new division" claim a term:
--    these are projections of the SAME trace the gcd-fold collapses, not a
--    fresh computation.
------------------------------------------------------------------------

cofactor-num : (q : ℚ) → gcd-of-ℚ q ∣ abs-ℤ (num q)
cofactor-num q = gcd-divides-left (abs-ℤ (num q)) (denominator q)

cofactor-den : (q : ℚ) → gcd-of-ℚ q ∣ denominator q
cofactor-den q = gcd-divides-right (abs-ℤ (num q)) (denominator q)

------------------------------------------------------------------------
-- 3. WORKED CASE — mirrors the EEAFoldTable trace of (3, 2). q = 3/2.
--    abs-ℤ (num q) = 3, denominator q = 2, gcd-ℕ 3 2 = 1 (already reduced).
--    The divisor `reduce` would divide by is the trace residue, 1.
------------------------------------------------------------------------

3/2 : ℚ
3/2 = mkℚ (+ 3) 1                              -- num +3, den-1 = 1, so denominator = 2

example-divisor : gcd-of-ℚ 3/2 ≡ 1
example-divisor = refl                          -- gcd-ℕ 3 2 = 1 (the trace's terminal residue)

example-reduced : is-reduced 3/2
example-reduced = refl                          -- 3/2 is already in lowest terms

------------------------------------------------------------------------
-- 4. SECOND UNIQUENESS ROUTE (the CF-shape route, complementing Bézout). When
--    the gcd index is pinned to 1, `cf-injective` makes the continued-fraction
--    shape of the EEA trace injective: two coprime fractions with the SAME CF
--    shape have equal numerator AND denominator. This is the shape-route ground
--    for canonical-form uniqueness (the Bézout route lives in
--    Q.Properties.CanonicalBezout); both read one EEATrace. Re-exported as the
--    edge's witness that reduce's output is canonical from EITHER direction.
------------------------------------------------------------------------

cf-shape-injective = cf-injective

-- The coprime certificate the shape route consumes is the SAME EEA engine: a
-- trace whose terminal residue is 1.
coprime-certificate : (a b : ℕ) → gcd-ℕ a b ≡ 1 → EEATrace a b 1
coprime-certificate = coprime-trace
