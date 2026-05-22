------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Sites.F2n
--
-- Concrete site: the Walsh-Hadamard transform as the DFT of F₂ⁿ.
--
-- F₂ⁿ is self-dual (per Substrate.Algebra.PontryaginDual.PD6); its
-- characters are χ_v(u) = (-1)^⟨u, v⟩ where ⟨·,·⟩ is the standard
-- bilinear form on F₂ⁿ.
--
-- This site connects:
--   * Substrate.Category.DiscreteFourierTransform (the abstract DFT
--     primitive)
--   * The GG-arc's empirical Walsh-Hadamard work
--     (eliza/walsh_hadamard.py)
--
-- Per [[ee-arc-reed-muller-hierarchy]]: F₂ⁿ DFT IS the Hamming-code
-- / RM hierarchy's algebraic dual reading.
-- Per [[gg-arc-multiprime-spectral]]: GG-arc empirical WHT IS this
-- site's runtime instantiation.
-- Per [[expose-generator-not-orbit]]: WHT is the GENERATOR of
-- F₂-spectral analysis; per-corpus spectra are orbits.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Sites.F2n where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.PontryaginDual using (F2nSelfDual)
open import Substrate.Category.DiscreteFourierTransform

------------------------------------------------------------------------
-- The F₂ⁿ self-dual iso witness.
--
-- F₂ⁿ is self-dual: characters χ_v(u) = (-1)^⟨u, v⟩ index by
-- F₂-vectors. The substrate-pragmatic realisation uses
-- Substrate.Algebra.F2.Vector.Vector n as both the vector carrier
-- and the character carrier; the iso is the identity bijection at
-- this granularity (the bilinear-form pairing is the consumer's
-- responsibility downstream).
------------------------------------------------------------------------

F2n-self-dual : (n : ℕ) → F2nSelfDual n
F2n-self-dual n = record
  { F2nVec   = Vector n
  ; F2nChars = Vector n
  ; to       = λ v → v
  ; from     = λ c → c
  ; to-from  = λ _ → refl
  ; from-to  = λ _ → refl
  }

------------------------------------------------------------------------
-- The F₂ⁿ Walsh-Hadamard DFT site.
--
-- The WHT is a length-2ⁿ × 2ⁿ matrix of signs ({+1, -1}). At the
-- substrate level we package the WalshHadamardDFT obligation around
-- the self-dual witness.
------------------------------------------------------------------------

ℤ-signs : Set
ℤ-signs = ℕ  -- placeholder for {+1, -1}; concrete instances use ℤ

ℤ-WHT-Site : (n : ℕ) → WalshHadamardDFT n
ℤ-WHT-Site n = record
  { self-dual-witness = F2n-self-dual n
  }
