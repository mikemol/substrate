------------------------------------------------------------------------
-- Substrate.Category.PrimeSampledChain
--
-- HH-arc: three-crumb prime-sampled chain context for substrate
-- chain-walk prediction. Per the user 2026-05-21: 'connect the
-- three axes to three crumb samples spaced apart ... tested at
-- different prime intervals ... richer chain physics'.
--
-- Each chain position k draws three 2-bit crumbs from PAST chain
-- symbols at distances (1, p, q) where p, q are small primes. The
-- crumbs are V₄-coset positions extracted from each past chain
-- symbol's S₄ chamber index. The 4³ = 64 context values feed a
-- 64-bucket adaptive predictor.
--
-- Per [[3plus1-parity-universal]]: three crumbs (1 + p + q
-- positions) realise the universal 3-axis pattern over distinct
-- prime gauges.
--
-- Per [[chain-walk-blocks-rotation-factor]]: past chain symbols
-- carry the cumulative chain state; sampling at prime offsets
-- exposes long-range chain-walk correlations the single-step
-- transition cannot factor.
--
-- Per [[expose-generator-not-orbit]]: the (p, q) prime pair is the
-- gauge generator; the past-chain-context stream is one orbit point.
--
-- Empirical (HH4 revised, past-chain-v4): best (p, q) = (2, 3)
-- across all tested corpora; mutual information / chain entropy
-- ratio:
--   substrate_agda:    13.6%
--   substrate_memory:  13.5%
--   substrate_opcodes: 70.5%
--   t1t2_handcrafted:  82.2%
--
-- Empirical (HH7 simulated per-emission cost vs unigram):
--   substrate_agda:    -1.7%
--   substrate_memory:  -1.6%
--   substrate_opcodes: -60.4%
--   t1t2_handcrafted:  -66.3%
--
-- Per [[negative-findings-corpus-bound]]: results bounded to tested
-- corpora and tested prime sets {2, 3, 5, 7, 11, 13}; the simulated
-- gain compares against UNIGRAM, not against the codec's actual
-- best predictor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PrimeSampledChain where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- A prime pair gauge: (p, q) ∈ ℕ × ℕ with p < q small primes.
-- Per HH4: best (p, q) = (2, 3) across tested corpora.

record PrimePair : Set where
  field
    p : ℕ
    q : ℕ

open PrimePair public

------------------------------------------------------------------------
-- A crumb is a 2-bit value ∈ {0, 1, 2, 3}.

record Crumb : Set where
  field
    value : ℕ        -- value < 4 enforced by use

open Crumb public

------------------------------------------------------------------------
-- A three-crumb context is the triple sampled at offsets
-- (1, p, q) from the current chain position.

record ThreeCrumbContext : Set where
  field
    c-prev : Crumb     -- from chain symbol at position k - 1
    c-p    : Crumb     -- from chain symbol at position k - p
    c-q    : Crumb     -- from chain symbol at position k - q

open ThreeCrumbContext public

------------------------------------------------------------------------
-- V₄ part of a chain symbol.
--
-- Each chain symbol c ∈ [0, 24) (= S₄) lies in exactly one of the
-- 6 left cosets of V₄. Within each coset there are 4 elements;
-- the within-coset position (0..3) is the V₄ part.
--
-- The V₄ part is a Crumb-valued projection π : S₄ → V₄ (modulo
-- the coset's structural V₄ action).

record V4PartExtraction : Set₁ where
  field
    Chamber  : Set
    v4-part  : Chamber → Crumb

open V4PartExtraction public

------------------------------------------------------------------------
-- Predictor context family indexed by PrimePair.

record PrimeContextPredictor : Set₂ where
  field
    extract     : V4PartExtraction
    pair        : PrimePair
    -- The 64 (= 4³) count tables, one per context value.
    Distribution : Set
    table-at    : ThreeCrumbContext → Distribution

open PrimeContextPredictor public

------------------------------------------------------------------------
-- Symmetric encoder/decoder property.
--
-- Both encoder and decoder maintain the chain_terminals history
-- before emission/decoding at position k. The context derives only
-- from past chain symbols (positions k-1, k-p, k-q), so both sides
-- compute the same context value:
--   encoder.context(k) ≡ decoder.context(k)
-- This is the lossless symmetry property.

record SymmetricContextProperty : Set₂ where
  field
    predictor : PrimeContextPredictor

open SymmetricContextProperty public

------------------------------------------------------------------------
-- Hamming(7, 4) recovery layer.
--
-- When the prime-context predictor's top guess differs from the
-- actual emission AND probability mass on actual emission < 1/3,
-- check whether the actual emission is within Hamming-distance 1
-- of the top guess (under 5-bit chamber-index → 7-bit Hamming
-- embedding). If so, single-bit-syndrome lookup recovers the
-- correct emission.
--
-- Empirical (HH8) recovery rates on mispredicts:
--   substrate_agda:    19.5%
--   substrate_memory:  21.2%
--   substrate_opcodes:  6.7%
--   t1t2_handcrafted:  18.2%

record HammingMispredictRecovery : Set₂ where
  field
    predictor      : PrimeContextPredictor
    -- Distance threshold for "recoverable" mispredict.
    distance-threshold : ℕ

open HammingMispredictRecovery public

------------------------------------------------------------------------
-- Categorical reading.
--
-- The prime-sampled context is a FUNCTOR from the category of
-- chain-symbol histories to the category of 64-bucketed predictor
-- count tables. The functor's "p, q" parameters select among the
-- families of prime-spaced sampling patterns.
--
-- Per [[homology-cohomology-recursion]]: the past-chain-symbol
-- history is the homology cycle; the V₄-part projection IS the
-- cohomology contraction; the prime-context predictor closes one
-- layer of the recursion at the predictor-ring level.
--
-- Per [[3plus1-parity-universal]]: the (3-crumb × 1-chirality)
-- structure recurs — 3 crumbs at offsets (1, p, q) give 3 axes;
-- the "chirality" is the order of those offsets (1, p, q) vs
-- (1, q, p), an F₂ choice that distinguishes ordered vs unordered
-- contexts.
------------------------------------------------------------------------
