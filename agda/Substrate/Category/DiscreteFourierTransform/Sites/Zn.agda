------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Sites.Zn
--
-- Concrete site: the cyclic discrete Fourier transform for Z/n.
--
-- For Z/n with characters χ_k(j) = ζ^(jk) (ζ = primitive n-th root
-- of unity), the DFT is the classical
--   F(f)(k) = Σ_j f(j) · ζ^(-jk).
--
-- Per [[roll-our-own-via-word-algebra]]: the cyclic generator g
-- is the Coxeter generator; characters are g^k mod n.
-- Per [[jj-arc-multi-sylow-composition]]: multi-Sylow DFT
-- decomposes via CRT into cyclic-prime DFTs at each Sylow prime
-- of n; this site provides the cyclic atomic case.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Sites.Zn where

open import Substrate.Foundation.Nat using (ℕ)

open import Substrate.Category.DiscreteFourierTransform

------------------------------------------------------------------------
-- The Z/n CRT decomposition site.

ℤ/n-CRT-Site : (n : ℕ) → CRTDecomposition n
ℤ/n-CRT-Site n = record {}

------------------------------------------------------------------------
-- The Z/n multi-Sylow DFT decomposition site.

ℤ/n-MultiSylow-Site : (n : ℕ) → MultiSylowDFTDecomposition n
ℤ/n-MultiSylow-Site n = record {}

------------------------------------------------------------------------
-- Per [[multi-sylow-composition]]: the substrate's multi-Sylow
-- predictor IS this site at the substrate's primary group structure.
-- Per [[expose-generator-not-orbit]]: cyclic-prime DFT is the
-- generator; composite-Z/n DFT is the orbit reached via CRT.
