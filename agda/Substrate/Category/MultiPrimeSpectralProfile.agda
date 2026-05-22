------------------------------------------------------------------------
-- Substrate.Category.MultiPrimeSpectralProfile
--
-- GG-arc: multi-prime Walsh-Hadamard spectral atlas of an input
-- bit stream. Per [[168-tower-as-fanout]]: GL(3, F₂) Sylow primes
-- are 2, 3, 7; GL(4, F₂) adds 5. The substrate's gauge-aligned
-- analysis primes {2, 3, 5, 7} produce a four-dimensional spectral
-- atlas characterising the input's structure at each prime-width.
--
-- For each prime width p, the F₂-Fourier (Walsh-Hadamard Transform)
-- decomposes the sliding-window p-bit symbol distribution into
-- 2ᵖ characters of F₂ᵖ. Dominant coefficients identify the
-- prime-p-periodic structural patterns; sparse spectra indicate
-- highly structured inputs.
--
-- Per GG7 empirical: H_p7 ↔ codec bpb r = -0.958. The 7-prime
-- spectral entropy is a strong substrate-codec compressibility
-- predictor. Per GG8: 7-prime dominant WHT coefficients correlate
-- with Hamming(7, 4) codeword density — structured corpora's
-- spectrum peaks ON codewords, unstructured corpora's peaks AT
-- Hamming-distance-1 syndrome positions.
--
-- Per the user 2026-05-21: 'sniffing at prime numbers of bits...
-- producing a multidimensional profile of the input over a small
-- fourier series'.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.MultiPrimeSpectralProfile where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; z≤n; s≤s)
open import Data.List using (List; []; _∷_; length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- A bit-width parameter; the substrate's gauge-aligned primes are
-- {2, 3, 5, 7}, but the structure is generic in any small prime.

record BitWidth : Set where
  field
    p : ℕ                -- width in bits

open BitWidth public

------------------------------------------------------------------------
-- A p-bit symbol distribution over a bit stream.
--
-- Sliding window: at every bit position, read p bits as a symbol;
-- count occurrences across the full stream. Result is a vector
-- in ℕ^(2ᵖ).

record SymbolDistribution (w : BitWidth) : Set₁ where
  field
    Distribution : Set       -- typically a numeric vector
    -- Total occurrence count.
    total       : Distribution → ℕ
    -- Count at a specific symbol value v ∈ [0, 2ᵖ).
    count-at    : Distribution → ℕ → ℕ

open SymbolDistribution public

------------------------------------------------------------------------
-- The Walsh-Hadamard Transform: an F₂-Fourier on F₂ᵖ-indexed
-- distributions. Self-inverse up to scaling: WHT² = 2ᵖ · id.

record WalshHadamardTransform (w : BitWidth) : Set₁ where
  field
    symdist : SymbolDistribution w
    -- The transformed coefficients (same carrier).
    wht     : Distribution symdist → Distribution symdist
    -- WHT is self-inverse up to scaling factor 2ᵖ.
    -- Stated structurally; concrete instances enumerate.

open WalshHadamardTransform public

------------------------------------------------------------------------
-- A p-prime spectrum: the distribution at width p PLUS its WHT.
-- This is one "axis" of the multi-prime atlas.

record PrimeSpectrum (w : BitWidth) : Set₁ where
  field
    transform : WalshHadamardTransform w
    counts    : Distribution (symdist transform)
    coeffs    : Distribution (symdist transform)
    -- Coefficients are the WHT of counts.
    coeffs-from-counts :
      coeffs ≡ wht transform counts

open PrimeSpectrum public

------------------------------------------------------------------------
-- The multi-prime spectral atlas: a family of PrimeSpectrum
-- indexed by the substrate's gauge-aligned primes {2, 3, 5, 7}.
--
-- Per [[expose-generator-not-orbit]]: each prime is one gauge axis;
-- the atlas exposes all axes simultaneously rather than collapsing
-- to a single byte-aligned reading.

record MultiPrimeAtlas : Set₂ where
  field
    -- Spectra at p = 2, 3, 5, 7.
    spec2 : PrimeSpectrum (record { p = 2 })
    spec3 : PrimeSpectrum (record { p = 3 })
    spec5 : PrimeSpectrum (record { p = 5 })
    spec7 : PrimeSpectrum (record { p = 7 })

open MultiPrimeAtlas public

------------------------------------------------------------------------
-- Cross-prime correlation matrix.
--
-- M[i, j] = correlation between the normalised sparsity profiles
-- of the i-th and j-th primes. Symmetric; diagonal = 1.
-- 4 × 4 over the substrate's prime tuple (2, 3, 5, 7).
--
-- Per GG4 empirical: substrate_memory exhibits M[2, 7] ≈ 0.97 —
-- byte-level and septet-level linear-pattern alignment. Other
-- corpora show varied cross-prime structure characteristic of
-- their content.

record CrossPrimeCorrelation : Set where
  field
    M22 : ℕ            -- diagonal: always 1 (represented abstractly)
    M27 : ℕ            -- p2 vs p7 correlation entry
    M37 : ℕ            -- p3 vs p7 correlation entry
    M57 : ℕ            -- p5 vs p7 correlation entry

open CrossPrimeCorrelation public

------------------------------------------------------------------------
-- Hamming(7, 4) bridge — GG8 structural connection.
--
-- The 16 Hamming(7, 4) codewords sit at specific positions in the
-- 7-bit WHT spectrum. A corpus's dominant 7-bit WHT coefficients
-- can be classified as either {codeword, syndrome-k} for k ∈ [1, 7].
--
-- Substrate-aligned corpora (per GG8): substrate_opcodes' top WHT
-- coefficient lands exactly on Hamming codeword 0b1010101 (= 85),
-- the checkerboard codeword. Less-structured corpora's top
-- coefficients land at syndromes ∈ {3, 5, 7} (odd-syndrome
-- single-bit errors).

record HammingSpectrumBridge : Set₁ where
  field
    spectrum-7 : PrimeSpectrum (record { p = 7 })
    -- A coefficient index in [0, 128) classified as either:
    --   isCodeword(i) : i is a Hamming(7, 4) codeword (16 cases)
    --   syndrome(i)   : i's syndrome ∈ [1, 7]
    -- Abstracted; concrete classifier in eliza.hamming.

open HammingSpectrumBridge public

------------------------------------------------------------------------
-- GG7 empirical statement: H_p7 ↔ codec bpb correlation.
--
-- Stated as a record-level observation; not a theorem (no upstream
-- formal codec model to derive it from in Agda).
--
-- Per [[multi-reading-ambient-discipline]]: the atlas IS the
-- substrate-honest reading; per-corpus single-prime measurements
-- collapse the ambient.

record SpectralCompressibilityObservation : Set₂ where
  field
    atlas              : MultiPrimeAtlas
    -- The observed correlation: high H_p7 entropy → low codec bpb
    -- (byte-uniform but chain-structured inputs compress well).

open SpectralCompressibilityObservation public

------------------------------------------------------------------------
-- Categorical reading.
--
-- The multi-prime atlas is a FUNCTOR from the category of input
-- bit streams to the category of 4-tuples of WHT spectra. The
-- functor is faithful at the per-prime level (bit stream → counts)
-- and bijective for WHT (counts ↔ coeffs).
--
-- The composition with the codec's compression functor (bit stream
-- → encoded bytes) commutes up to the empirical correlation: high
-- atlas entropy at p=7 → low compression bpb (r = -0.958).
--
-- Per [[homology-cohomology-recursion]]: the WHT IS the
-- cohomology of the count vector under F₂ⁿ characters; the count
-- vector is the homology of the bit stream under the sliding
-- window functor. The atlas closes one layer of the recursion.
--
-- Per [[3plus1-parity-universal]]: at each prime p, the WHT
-- yields 2ᵖ characters = the dual group of F₂ᵖ. The pseudoscalar
-- (top-grade) character is the chirality F₂; the other 2ᵖ − 1
-- characters span the axes.
------------------------------------------------------------------------
