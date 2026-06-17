------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.ComputeTrace  (B-COMPUTE, part 1)
--
-- The USE-CASE-SPECIFIC builder of a `PolyEEATrace` for the AES inverse
-- (user 06-16: the monic-divisor construction is inversion-specific, not a
-- generic substrate primitive — which is why the generic wedge deferred it).
-- Concrete to the job: modulus degree 8, dividend degree < 8, trace length ≤ 8
-- ⇒ FUEL (not Acc); the divisor is carried AS (d, f-lo) so `step` typechecks.
--
-- PART 1 (here): the MONIC PRESENTATION — a poly monic at full length
-- (`vlast v ≡ 𝟙`) with low part f-lo IS the divisor `b-poly` (no trim).  This
-- is the common case: each step's remainder, once at its exact degree, presents
-- as a `divisor-q` for the next step via `snoc-vinit-vlast` + char-2 `-P = id`.
--
-- REMAINING (the multi-piece grind):
--   * B-TRIM — present a remainder with TRAILING ZEROS (vlast = 𝟘, degree <
--     full length) as a SHORTER `divisor-q`: trim to exact degree (dependent
--     Vec length from `leading-position`; no generic `take`), with correctness
--     `v ≡ divisor-q d′ f-lo′` to `subst` into the trace.
--   * B-BUILD — the FUEL recursion (mirror `Nat/GCD/ComputeTrace.compute-trace`):
--     base (`zero-q` ⇒ g = a), step (`divmod` by the carried divisor + present
--     the remainder via monic-pres/B-TRIM + recurse + `step`-wrap with subst).
--   * B-INV-UNIT discharge — the concrete gcd's `nth g 0 ≡ 𝟙` / `nth g (suc k) ≡ 𝟘`.
-- Then `bezout-poly ∘ this` feeds `ModZero.inverse-from-bezout`; wrap = AI-8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.ComputeTrace where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as D

-- the monic presentation, relative to the candidate divisor's (d, f-lo).
module Pres (n : ℕ) (f-lo : Vec F₂ (suc n)) where
  open D.Over F₂-CommRing n f-lo

  -- char-2 negation is the identity.
  -P-id : {m : ℕ} (v : Poly m) → -P v ≡ v
  -P-id []      = refl
  -P-id (x ∷ v) = cong₂ _∷_ refl (-P-id v)

  -- a poly MONIC at full length, with low part f-lo, IS the divisor b-poly:
  -- the cheap monic presentation (no trim needed).
  monic-pres : (v : Poly (suc (suc n))) → vlast v ≡ 𝟙 → vinit v ≡ f-lo → v ≡ b-poly
  monic-pres v hv hf =
    trans (sym (snoc-vinit-vlast v))
    (trans (cong₂ snoc hf hv)
           (cong (λ z → snoc z 𝟙) (sym (-P-id f-lo))))
