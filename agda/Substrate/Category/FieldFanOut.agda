------------------------------------------------------------------------
-- Substrate.Category.FieldFanOut
--
-- Fan-out bond structure: one source carrier with target fields
-- indexed by a Base (typically a position in a 1D corpus) whose
-- arity may VARY per Base point.
--
-- ★ Generalized 2026-05-21 (in-place per user direction) ★
--
-- Old shape (preserved as `FixedFanOut`):
--   FieldFanOut (n : ℕ) — fixed n targets, one Source, one Bond per target
--
-- New shape:
--   FieldFanOut (Base : Set) (arity-fn : Base → ℕ) — for each Base point b,
--     arity-fn b targets and arity-fn b bonds
--
-- The old shape is recovered as `FixedFanOut n = FieldFanOut ⊤ (const n)`.
--
-- Substrate use-cases:
--   * Z/30 = Z/2 × Z/3 × Z/5 (CRT, stationary): FixedFanOut 3.
--   * |GL(3, F₂)| = 168 = 2³·3·7 (stationary): FixedFanOut 3.
--   * Multi-Sylow PLL bank where the active prime-set varies over
--     corpus position: FieldFanOut Position (active-primes-count-at).
--   * Stratified bundles per [[multi-route-equivariance-recovery]]:
--     fiber arity varies per stratum.
--
-- Per [[multi-field-tower-architecture]]: variable-arity FanOut is the
-- natural lift to handle compositional/heterogeneous corpora where
-- the prime-factor structure is itself a function of position.
--
-- Per the DBE constructive-completeness criterion (user 2026-05-21):
-- this record is constructively complete — given the (Base, arity-fn,
-- Source, Target, Bond) tuple, the caller can apply Bond at any (b, i)
-- to map a Source element through to its corresponding Target b i.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FieldFanOut where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The generalized FieldFanOut record.
--
-- Parameterized by a Base type (typically a 1D corpus position) and
-- an arity function specifying how many targets exist at each Base
-- point. Source is uniform across Base; Target and Bond vary per
-- Base point.
------------------------------------------------------------------------

record FieldFanOut (Base : Set) (arity-fn : Base → ℕ) : Set (lsuc ℓ) where
  field
    Source  : Set ℓ
    Target  : (b : Base) → Fin (arity-fn b) → Set ℓ
    Bond    : (b : Base) → (i : Fin (arity-fn b)) → Source → Target b i

------------------------------------------------------------------------
-- Backward-compatible FIXED-arity case.
--
-- FixedFanOut n = FieldFanOut ⊤ (const n).
-- This is the original (pre-generalization) signature, recoverable
-- as a one-Base-point specialization.
------------------------------------------------------------------------

FixedFanOut : ℕ → Set (lsuc ℓ)
FixedFanOut {ℓ} n = FieldFanOut {ℓ} ⊤ (λ _ → n)

------------------------------------------------------------------------
-- Constructor for the fixed-arity case.
--
-- Lifts the old (Source, Target, Bond) triple into the generalized
-- shape with Base = ⊤ and arity-fn = const n.
------------------------------------------------------------------------

make-fixed : {ℓ : Level} (n : ℕ)
             (S : Set ℓ)
             (T : Fin n → Set ℓ)
             (B : (i : Fin n) → S → T i) →
             FixedFanOut {ℓ} n
make-fixed n S T B = record
  { Source = S
  ; Target = λ _ → T
  ; Bond   = λ _ → B
  }

------------------------------------------------------------------------
-- Capstone (updated 2026-05-21).
--
-- FieldFanOut now captures the variable-arity tree-shaped bond
-- structure. The fixed-arity case (FixedFanOut) recovers the
-- original signature for stationary CRT decompositions.
--
-- Substrate use:
--   * Stationary CRT (Z/30, 168-gauge, etc.): use FixedFanOut.
--   * Compositional / heterogeneous corpora: use FieldFanOut with
--     a non-trivial Base type.
--
-- Per [[multi-route-equivariance-recovery]]: the variable-arity
-- generalization is what makes atlas-of-charts work over
-- compositional corpora where the chart family itself varies.
--
-- Per [[3plus1-parity-universal]]: at every Base point, the
-- (arity-fn b)-target structure carries a (n-axis + 1-chirality)
-- structure when arity-fn b = n+1.
------------------------------------------------------------------------
