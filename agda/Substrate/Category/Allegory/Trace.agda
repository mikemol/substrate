------------------------------------------------------------------------
-- Substrate.Category.Allegory.Trace  (ALG-CF)
--
-- The continued-fraction / Euclidean-trace tie-in: the allegory IS the
-- foundation under the CF approach to B-EEA (the GF(2⁸) inverse).  This
-- module lands the CF↔allegory connection and pins the two fixed-point
-- endpoints to their existing repo proofs.
--
-- PROVEN HERE:
--   * `cf-of a b` — the CF/EEA expansion (quotient-digit sequence) of a/b,
--     = `digits-of-EEA ∘ compute-trace` (reused).
--   * `cf-map` — THE TIE-IN: the CF expansion is an allegory MAP (ALG-5
--     `isMap` via `graph-map`).  CF-uniqueness IS the singleton-fiber / map
--     property.  The Bézout/inverse readout (B-EEA-INV) is the convergent of
--     this map; B-EEA-FOLD-bez is the residual-fold (ALG-6) over the trace.
--
-- THE TWO FIXED-POINT ENDPOINTS (identified, with existing proofs — the
-- inductive/coinductive halves of the one operator Φ):
--   * μΦ = the inductive `Trace` (`Algebra/Wedge.agda`, ctors done/more) — the
--     INITIAL ALGEBRA of the wedge-step by construction; `eea-fold`
--     (`Nat/GCD/Fold.agda`) is its eliminator.  The finite (rational/poly) CF.
--     My `PolyEEATrace` + `eea-fold-poly` are the F₂[x] instance = B-EEA's trace.
--   * νΦ = the coinductive `RealTrace` (`Algebra/R/Trace.agda`) — proven to be
--     the TERMINAL COALGEBRA of S(X)=ℕ×X in `Algebra/R/Trace/Final.agda`
--     (`out` Lambek-iso, `ana`, `ana-unique`).  The infinite (irrational) CF.
--
-- REMAINING ALG-CF CLOSURE (honest deferral): the polynomial degree-descent
-- `lp-bound` (B-DIVc) as a well-founded measure = a concrete wedge-step
-- `Refinement` whose `chain` descends — i.e. `PolyEEATrace` termination AS the
-- Φ-chain.  Needs a poly `DivStr`/`CertifiedWedge` bridge (PolyEEATrace is a
-- parallel construction); cheap once that bridge exists, but not yet wired.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.Allegory.Trace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Product using (Σ; proj₂)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.R.Trace using (digits-of-EEA)
open import Substrate.Category.Allegory.Maps using (isMap; graph; graph-map)

-- the continued-fraction / EEA expansion of a/b: the quotient (digit) sequence.
cf-of : ℕ → ℕ → List ℕ
cf-of a b = digits-of-EEA (proj₂ (compute-trace a b))

-- THE TIE-IN: the CF expansion is an allegory MAP (deterministic + entire) —
-- CF-uniqueness IS the singleton-fiber/map property (ALG-5), for each divisor b.
cf-map : (b : ℕ) → isMap (graph (λ a → cf-of a b))
cf-map b = graph-map (λ a → cf-of a b)
