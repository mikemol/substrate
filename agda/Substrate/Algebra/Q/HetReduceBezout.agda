------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetReduceBezout
--
-- CONNECTION LEAF (interconnect edge 5<->2): the HetQ / heterogeneous-basis
-- ℚ half (Algebra.Q.HetBasis — ℚ = HetQ ℤ ℕ, numerator in ℤ, denominator in ℕ)
-- meets the Bézout/gcd spine half (Algebra.Z.Bezout — the oriented EEA fold
-- s·a + t·b = g, via the coprime EEA trace Algebra.Nat.GCD.GcdTrace.coprime-trace).
--
-- Claim: a HetQ ℤ ℕ in REDUCED form (gcd(|hnum|, hden) = 1, i.e. Q.Reduction's
-- `is-reduced` on the corresponding ℚ) factors through Bézout's gcd — its
-- coprimality is CERTIFIED by a Bézout witness over ℤ. Concretely: from
-- `is-reduced q` we run `coprime-trace` to obtain the EEA trace bottoming at 1
-- and fold it (bezout-ℤ) into ∃ s t : ℤ. s·(+|num q|) + t·(+den q) = +1. This
-- wires reduce's coprimality predicate to the Bézout structure: "reduced HetQ
-- form is characterized by coprime Bézout witnesses." Reuse-only: every step is
-- an existing def (coprime-trace, bezout-ℤ, is-reduced, abs-ℤ, toHetQ) — no new
-- machinery, one composed lemma.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetReduceBezout where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Q using (ℚ; num; denominator)
open import Substrate.Algebra.Q.Reduction using (abs-ℤ; gcd-of-ℚ; is-reduced)
open import Substrate.Algebra.Q.HetBasis using (HetQ; _//_; hnum; hden; toHetQ)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (coprime-trace)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)

------------------------------------------------------------------------
-- 1. The two carriers of a HetQ ℤ ℕ, read off a ℚ via `toHetQ`. The numerator
--    magnitude |hnum| and the denominator hden are the gcd's two ℕ-arguments —
--    exactly the inputs `is-reduced`/`gcd-of-ℚ` already compute on.
------------------------------------------------------------------------

-- The numerator magnitude (ℕ) of the HetQ — the first gcd argument.
het-num-abs : ℚ → ℕ
het-num-abs q = abs-ℤ (hnum (toHetQ q))

-- The denominator (ℕ) of the HetQ — the second gcd argument. (toHetQ stores
-- den-1; the honest denominator used by gcd-of-ℚ / is-reduced is `denominator q`.)
het-den : ℚ → ℕ
het-den q = denominator q

-- `is-reduced q` is exactly gcd of these two carriers ≡ 1 (definitional):
-- gcd-of-ℚ q = gcd-ℕ (abs-ℤ (num q)) (denominator q), and hnum (toHetQ q) = num q.
reduced-is-coprime-carriers : (q : ℚ) →
  is-reduced q ≡ (gcd-of-ℚ q ≡ 1)
reduced-is-coprime-carriers q = refl

------------------------------------------------------------------------
-- 2. THE CONNECTION: a reduced HetQ ℤ ℕ has a Bézout witness over ℤ. From the
--    coprimality `gcd-ℕ |num| den ≡ 1` we get the EEA trace bottoming at 1
--    (coprime-trace — the EEA/Bézout certificate) and fold it (bezout-ℤ) into the
--    oriented bridge s·(+|num|) + t·(+den) = +1. This characterizes reduced form:
--    coprimality IS the existence of Bézout coefficients.
------------------------------------------------------------------------

reduce-hetq-coprime : (q : ℚ) → is-reduced q →
  BezoutℤWitness (het-num-abs q) (het-den q) 1
reduce-hetq-coprime q red =
  bezout-ℤ (coprime-trace (het-num-abs q) (het-den q) red)

------------------------------------------------------------------------
-- 3. Unfolded statement of the witness, to make the cross-vocabulary content
--    explicit: ∃ s t : ℤ. s ·ℤ (+|hnum|) + t ·ℤ (+hden) = +1. This is the same
--    Σ ℤ (λ s → Σ ℤ (λ t → ...)) `BezoutℤWitness` unfolds to (definitional refl) —
--    re-exported here as the leaf's headline type.
------------------------------------------------------------------------

bezout-statement : (q : ℚ) →
  BezoutℤWitness (het-num-abs q) (het-den q) 1
    ≡ (BezoutℤWitness (abs-ℤ (num q)) (denominator q) 1)
bezout-statement q = refl
