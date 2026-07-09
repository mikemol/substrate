------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Sites.Zn
--
-- Concrete site: the cyclic discrete Fourier transform for Z/n.
--
-- For Z/n with characters χ_k(j) = ζ^(jk) (ζ = primitive n-th root
-- of unity), the DFT is the classical F(f)(k) = Σ_j f(j) · ζ^(-jk).
--
-- Per [[roll-our-own-via-word-algebra]]: the cyclic generator g is
-- the Coxeter generator; characters are g^k mod n.
-- Per [[jj-arc-multi-sylow-composition]]: multi-Sylow DFT
-- decomposes via CRT into cyclic-prime DFTs at each Sylow prime of
-- n; this site provides the cyclic atomic case.
-- Per [[expose-generator-not-orbit]]: cyclic-prime DFT is the
-- generator; composite-Z/n DFT is the orbit reached via CRT.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Sites.Zn where

open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.DiscreteFourierTransform

------------------------------------------------------------------------
-- The Z/n CRT decomposition site.
--
-- Per CRTDecomposition's record obligation:
--   PrimeFactors    — placeholder list-of-primes (ℕ stand-in)
--   PerFactorDFT    — placeholder composite DFT bundle (ℕ → ℕ)
--   tensor-witness  — identity bundling (real implementation pending
--                     the substrate-native prime-factorisation arc)
------------------------------------------------------------------------

-- PrimeFactors / PerFactorDFT are now module parameters (⟡set1-paydown); supplied
-- positionally (ℕ stand-in for the prime list, ℕ → ℕ for the composite DFT bundle).
ℤ/n-CRT-Site : (n : ℕ) → CRTDecomposition ℕ (ℕ → ℕ) n
ℤ/n-CRT-Site n = record
  { tensor-witness = λ _ k → k
  }

------------------------------------------------------------------------
-- The Z/n multi-Sylow DFT decomposition site.
--
-- The Sylow primes of n determine the prime-power factor tensor
-- structure of the DFT for Z/n. Per
-- [[jj-arc-multi-sylow-composition]] this is the algebra side of
-- the JJ-arc empirical work.
------------------------------------------------------------------------

-- SylowPrimes / PerSylowDFT are now module parameters (⟡set1-paydown); supplied positionally.
ℤ/n-MultiSylow-Site : (n : ℕ) → MultiSylowDFTDecomposition ℕ (ℕ → ℕ) n
ℤ/n-MultiSylow-Site n = record
  { sylow-bundle = λ _ k → k
  }
