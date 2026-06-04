------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.EEATrace.Keystone
--
-- EEATrace IS KEYSTONE #1, ITERATED — and (find the common structure,
-- recursively) it is now the ℕ INSTANCE of the carrier-generic residue-shedding
-- on the wedge Trace (Algebra.Wedge.Trace.Residues), reached via
-- Algebra.Wedge.fromEEATrace. The Euclidean trace is the wedge applied
-- recursively, shedding a residue each step until it vanishes (the gcd); each
-- `step` carries a CERTIFIED wedge (Algebra.Nat.GCD.Wedge, with r < b).
--
--   eea-residues  = trace-residues ∘ fromEEATrace   — the shed residues.
--   eea-classify  = trace-classify ℕ-torsor ℕ-zero? ∘ fromEEATrace — each shed
--                   residue tagged by prove-or-correct (0 = stop/gcd, ≠0 =
--                   fixed-point-free correction & recurse).
--
-- The ONE part that does NOT lift to the generic Trace is the certified
-- smallness r < b: fromEEATrace forgets it (the generic Trace uses the loose
-- wedge), so eea-head-small-< stays the ℕ-GCD specialization's extra — the
-- well-founded measure that makes the recursion terminate.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.EEATrace.Keystone where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Sum using (_⊎_)
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Algebra.Nat.GCD.Wedge using (remainder; r<b)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; step)
open import Substrate.Algebra.Wedge using (fromEEATrace)
open import Substrate.Algebra.Wedge.Trace.Residues using (trace-residues; trace-classify)
open import Substrate.Algebra.Wedge.ResidueAtom using (ℕ-torsor; ℕ-zero?)
open import Substrate.Category.Lawvere using (FixedPointFree)

------------------------------------------------------------------------
-- 1. The shed residues + their prove-or-correct tags = the carrier-generic
--    Trace operations specialised to ℕ via fromEEATrace.
------------------------------------------------------------------------

eea-residues : {a b g : ℕ} → EEATrace a b g → List ℕ
eea-residues t = trace-residues (fromEEATrace t)

eea-classify : {a b g : ℕ} → EEATrace a b g →
               List (Σ ℕ (λ r → (r ≡ zero) ⊎ FixedPointFree ℕ))
eea-classify t = trace-classify ℕ-torsor ℕ-zero? (fromEEATrace t)

------------------------------------------------------------------------
-- 2. The certified smallness — the part fromEEATrace forgets, so it stays
--    here: each shed residue is < the divisor (the well-founded measure ⟹
--    termination). This is the certified r<b live at every EEA step.
------------------------------------------------------------------------

eea-head-small : {a g : ℕ} (b′ : ℕ) (t : EEATrace a (suc b′) g) → ℕ
eea-head-small b′ (step _ w _) = remainder w

eea-head-small-< : {a g : ℕ} (b′ : ℕ) (t : EEATrace a (suc b′) g) →
                   eea-head-small b′ t < suc b′
eea-head-small-< b′ (step _ w _) = r<b w
