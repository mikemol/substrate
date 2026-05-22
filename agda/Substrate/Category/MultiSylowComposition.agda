------------------------------------------------------------------------
-- Substrate.Category.MultiSylowComposition
--
-- JJ-arc: composing multiple Sylow-prime probes into joint atlases.
-- Per the user 2026-05-21: 'how many different sylow primes can we
-- compose?'
--
-- Answer (empirical + structural):
--
--   Theoretically: bounded by GL(n, F₂)'s prime factorization.
--     GL(3, F₂) = 168 = 2³·3·7      → Sylow primes {2, 3, 7}
--     GL(4, F₂) = 20160 = 2⁶·3²·5·7 → adds Sylow-5
--     GL(5, F₂) introduces Sylow-31 (Mersenne)
--     Each GL(n, F₂) potentially adds new primes from 2^k − 1
--     factorization for k ≤ n.
--
--   Information-theoretically: joint MI ≤ H(chain symbol) ≈ 4.58 bits.
--     Beyond ~6 Sylow primes, joint MI approaches the chain entropy
--     ceiling (saturation).
--
--   Sample-size: joint context space ≤ ~N samples for reliable MI.
--     4ᵏ-context (k Sylow probes) ≤ chain_length / 4 → k ≤ log₄(N).
--     At 8KB chain (16K symbols), k ≤ ~7.
--
-- Empirical JJ saturation curve at 8KB:
--   substrate_agda (natural text):   |S|=1 → 0.08; |S|=6 → 2.72 bits
--                                     (1.7% → 59% of H)
--   substrate_memory:                |S|=1 → 0.04; |S|=6 → 2.51 bits
--                                     (saturates at |S|=4-5 due to
--                                     sample sparsity)
--   substrate_opcodes:               |S|=1 → 0.96; |S|=6 → 1.51 bits
--                                     (low H ceiling = 2.04)
--   t1t2_handcrafted:                |S|=1 → 0.77; |S|=6 → 3.13 bits
--                                     (98% of H = 3.19)
--
-- Per [[multi-route-equivariance-recovery]]: cross-Sylow composition
-- generates the full gauge group; this is why MI grows ROUGHLY
-- MULTIPLICATIVELY per Sylow added on natural text (each Sylow
-- contributes a distinct orbit-axis the others miss).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.MultiSylowComposition where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; z≤n; s≤s; _⊔_)
open import Data.List using (List; []; _∷_; length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- A SylowPrime is a prime number ∈ the substrate's gauge group
-- factorization. Sylow primes for the various GL(n, F₂):
--
--   GL(2, F₂):  {2, 3}        (order 6)
--   GL(3, F₂):  {2, 3, 7}     (order 168)
--   GL(4, F₂):  {2, 3, 5, 7}  (order 20160)

data SylowPrime : Set where
  s-2  : SylowPrime
  s-3  : SylowPrime
  s-5  : SylowPrime
  s-7  : SylowPrime
  s-11 : SylowPrime
  s-13 : SylowPrime
  -- Higher primes (17, 31, 73, 127, ...) representable analogously.

-- Numeric value of a SylowPrime.

sylow-value : SylowPrime → ℕ
sylow-value s-2  = 2
sylow-value s-3  = 3
sylow-value s-5  = 5
sylow-value s-7  = 7
sylow-value s-11 = 11
sylow-value s-13 = 13

------------------------------------------------------------------------
-- A SylowProbe is a single Sylow prime; it samples the V₄-coset
-- crumb of the chain symbol at offset = sylow-value back.

record SylowProbe : Set where
  field
    prime : SylowPrime

open SylowProbe public

------------------------------------------------------------------------
-- A MultiSylowAtlas is a list of distinct SylowProbes. The joint
-- context value at chain position k is the bit-packed concatenation
-- of each probe's crumb (4 values = 2 bits per probe).
--
-- Width = 2 * |probes|; joint context cardinality = 4^|probes|.

record MultiSylowAtlas : Set where
  field
    probes      : List SylowProbe
    -- Distinctness of primes is structural (caller's responsibility).

open MultiSylowAtlas public

------------------------------------------------------------------------
-- Composition cardinality bound.
--
-- For a k-probe atlas, joint context has 4ᵏ values.
-- Sample-size constraint: 4ᵏ ≤ chain_length, i.e., k ≤ log₄(N).
--
-- Stated as a structural property at the meta level; concrete
-- bounds at the runtime side (eliza/sylow_prime_probe.py).

------------------------------------------------------------------------
-- Saturation curve (empirical observation).
--
-- Per [[multi-route-equivariance-recovery]] and the JJ empirical
-- results: joint MI grows monotonically with |Sylow-subset| up to
-- the sample-size or H(chain) ceiling. The growth is roughly
-- MULTIPLICATIVE on natural-text corpora — each Sylow adds an
-- independent orbit-axis contribution.

record SaturationCurve : Set₁ where
  field
    -- For each subset size k, the best joint MI achievable.
    best-mi-at-size : ℕ → ℕ        -- in millibits, abstracted
    -- Monotonic non-decreasing.
    -- Stated abstractly; concrete instances enumerate.

open SaturationCurve public

------------------------------------------------------------------------
-- The three compositional bounds.

record CompositionalBounds : Set where
  field
    -- Theoretical: |Sylow-set| ≤ |primes dividing |GL(n, F₂)||
    max-by-group           : ℕ
    -- Information-theoretic: joint MI ≤ H(chain)
    max-by-entropy         : ℕ
    -- Sample-size: 4^|Sylow-set| ≤ N
    max-by-samples         : ℕ
    -- Effective composable count is the min of these.

open CompositionalBounds public

-- For 8KB substrate-atlas data with GL(4, F₂)-anchored Sylow
-- primes:
--   max-by-group  = 4 ({2, 3, 5, 7})
--   max-by-entropy ≈ 7 (need 4^7 = 16384 ≥ data size of 16K)
--   max-by-samples ≈ 7
-- Effective: 4 prime classes from primary; up to 6-7 with
-- extension to {11, 13} from GL(10, F₂) / GL(12, F₂).

substrate-bounds-8kb : CompositionalBounds
substrate-bounds-8kb = record
  { max-by-group   = 4
  ; max-by-entropy = 7
  ; max-by-samples = 7
  }

------------------------------------------------------------------------
-- Sylow theory link: same-Sylow probes have ZERO marginal
-- contribution to joint MI (Sylow-2-only joint MI = single
-- Sylow-2 MI). Cross-Sylow probes add multiplicatively.
--
-- This is the substrate-honest formalization of
-- [[multi-route-equivariance-recovery]]: equivariance is a JOINT
-- property of the atlas of charts (= union of Sylow probes); no
-- single Sylow chart carries it alone.
--
-- Per [[168-tower-as-fanout]]: |GL(3, F₂)| = 168 is simple; any
-- subset containing one element of each Sylow class (Sylow-2 +
-- Sylow-3 + Sylow-7) generates the full group.

------------------------------------------------------------------------
-- Categorical reading.
--
-- The multi-Sylow atlas is a CRT-style decomposition: the chain
-- walk's GL(n, F₂) gauge group factors via the Sylow primes; each
-- Sylow probe extracts the corresponding factor's contribution.
--
-- Per [[homology-cohomology-recursion]]: each Sylow prime is one
-- homology layer; the joint atlas closes the cohomology cycle by
-- composing all Sylow contributions.
--
-- Per [[multi-field-tower-architecture]]: the joint Sylow atlas
-- IS the FieldFanOut over the prime factorization of |GL(n, F₂)|.
------------------------------------------------------------------------
