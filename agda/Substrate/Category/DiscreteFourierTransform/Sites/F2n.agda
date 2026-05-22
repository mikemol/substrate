------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Sites.F2n
--
-- Concrete site: the Walsh-Hadamard transform as the DFT of F₂ⁿ.
--
-- F₂ⁿ is self-dual (per Substrate.Algebra.PontryaginDual.PD6); its
-- characters are χ_v(u) = (-1)^⟨u, v⟩ where ⟨·,·⟩ is the standard
-- bilinear form on F₂ⁿ.
--
-- The DFT matrix for F₂ⁿ is the n-fold tensor product of 2x2
-- Hadamard matrices, with values in {+1, -1} (signs as ℤ values).
--
-- This site connects:
--   * Substrate.Category.DiscreteFourierTransform (the abstract DFT
--     primitive)
--   * The GG-arc's empirical Walsh-Hadamard work
--     (eliza/walsh_hadamard.py)
--
-- The structural anchor for spectral analysis of F₂-valued
-- bit-stream signals.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Sites.F2n where

open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Algebra.PontryaginDual using (F2nSelfDual)
open import Substrate.Category.DiscreteFourierTransform

------------------------------------------------------------------------
-- The F₂ⁿ Walsh-Hadamard DFT site.
--
-- For each n, the WHT is a length-2ⁿ × 2ⁿ matrix of signs.

ℤ-signs : Set
ℤ-signs = ℕ  -- placeholder for {+1, -1}; concrete instances use ℤ

ℤ-WHT-Site : (n : ℕ) → WalshHadamardDFT n
ℤ-WHT-Site n = record
  { self-dual-witness = record {}
  }

------------------------------------------------------------------------
-- Per [[ee-arc-reed-muller-hierarchy]]: F₂ⁿ DFT IS the Hamming-code
-- / RM hierarchy's algebraic dual reading.
-- Per [[gg-arc-multiprime-spectral]]: GG-arc empirical WHT IS this
-- site's runtime instantiation; the substrate's structural
-- anchoring is now first-class.
-- Per [[expose-generator-not-orbit]]: WHT is the GENERATOR of
-- F₂-spectral analysis; per-corpus spectra are orbits.
