------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.EEATrace.Keystone
--
-- EEATrace IS KEYSTONE #1, ITERATED. The Euclidean trace is the wedge applied
-- recursively, shedding a residue at every step until it vanishes (the gcd).
-- Each `step` carries a CERTIFIED wedge (Algebra.Nat.GCD.Wedge, with r < b —
-- the smallness the keystone's certified residue needs, already present for ℕ),
-- sheds `remainder w`, and recurses on (suc b, remainder w). The `base` case is
-- the residue reaching 0 — the clean reconstruction end (gcd(a,0) = a).
--
-- Read through prove-or-correct (Category.Lawvere / ResidueAtom.Properties):
-- every shed residue is EITHER 0 (stop — reconstruct cleanly) OR a fixed-point-
-- free correction (shed and recurse). EEA never dead-ends, and it TERMINATES
-- because r < b strictly decreases — the certified smallness is the well-founded
-- measure. So "EEA does the recursive factoring, shedding residues" is exactly
-- keystone #1's prove-or-correct engine run to the gcd fixpoint.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.EEATrace.Keystone where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Sum using (_⊎_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Nat.GCD.Wedge using (remainder; r<b)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Category.Lawvere using (FixedPointFree)
open import Substrate.Algebra.Wedge.ResidueAtom.Properties using (ℕ-prove-or-correct)

------------------------------------------------------------------------
-- 1. The residues EEA sheds, in order — the recursive factoring's leftovers.
------------------------------------------------------------------------

eea-residues : {a b g : ℕ} → EEATrace a b g → List ℕ
eea-residues (base _)       = []
eea-residues (step _ w rec) = remainder w ∷ eea-residues rec

------------------------------------------------------------------------
-- 2. The certified smallness at each step IS the well-founded measure: the
--    shed residue is strictly smaller than the divisor it was shed against.
--    (r < b, directly from the certified wedge — the keystone's r<b, live.)
------------------------------------------------------------------------

eea-head-small : {a g : ℕ} (b′ : ℕ) (t : EEATrace a (suc b′) g) → ℕ
eea-head-small b′ (step _ w _) = remainder w

eea-head-small-< : {a g : ℕ} (b′ : ℕ) (t : EEATrace a (suc b′) g) →
                   eea-head-small b′ t < suc b′
eea-head-small-< b′ (step _ w _) = r<b w

------------------------------------------------------------------------
-- 3. EEA classified by prove-or-correct: each shed residue is either 0 (stop,
--    the gcd is reached) or a fixed-point-free correction (shed and recurse).
--    Keystone #1's prove-or-correct, iterated to the gcd fixpoint.
------------------------------------------------------------------------

eea-classify : {a b g : ℕ} → EEATrace a b g →
               List (Σ ℕ (λ r → (r ≡ zero) ⊎ FixedPointFree ℕ))
eea-classify (base _)       = []
eea-classify (step _ w rec) =
  (remainder w , ℕ-prove-or-correct (remainder w)) ∷ eea-classify rec
