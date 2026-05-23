------------------------------------------------------------------------
-- Substrate.Codes.ReedMuller.RM-1-3
--
-- M-6 of the Cocycles structural-migration plan. The Reed-Muller
-- code RM(1, 3): length 8, dimension 4, minimum distance 4,
-- self-dual under Hodge ★ in dimension 4 (also = extended Hamming
-- [8, 4, 4]).
--
-- This is the SPECIFIC instance the CY-5 migration needs: the 8
-- "reserved" codewords in the V₄-signature ambient (per catalog/
-- cocycles.md § CY-5: 24 + 8 = 32 = 2⁵; the 8 are RM(1,3) image,
-- corresponding to signed singletons / Hodge 1-forms).
--
-- General RM(r, m) is deferred — the structural framework is the
-- same; we can lift this instance to the parametric form when a
-- consumer needs it.
--
-- Convention (LSB-first bit-encoding of point indices):
--   point 0 = (0, 0, 0)    point 4 = (0, 0, 1)
--   point 1 = (1, 0, 0)    point 5 = (1, 0, 1)
--   point 2 = (0, 1, 0)    point 6 = (0, 1, 1)
--   point 3 = (1, 1, 0)    point 7 = (1, 1, 1)
--
-- The 4 generator basis-images are the evaluations of the 4
-- degree-≤-1 monomials {1, x₁, x₂, x₃} at these 8 points:
--   g₀ = 1   (constant)                = 1 1 1 1 1 1 1 1
--   g₁ = x₁ (projection on first bit)  = 0 1 0 1 0 1 0 1
--   g₂ = x₂ (projection on second bit) = 0 0 1 1 0 0 1 1
--   g₃ = x₃ (projection on third bit)  = 0 0 0 0 1 1 1 1
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Codes.ReedMuller.RM-1-3 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃; ₄)
open import Substrate.Foundation.Vec using ([]; _∷_)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Code

------------------------------------------------------------------------
-- The 4 generator basis-images.
------------------------------------------------------------------------

g₀ : Vector 8
g₀ = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

g₁ : Vector 8
g₁ = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []

g₂ : Vector 8
g₂ = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []

g₃ : Vector 8
g₃ = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- The basis-image dispatcher.
------------------------------------------------------------------------

generators : Fin 4 → Vector 8
generators zero                = g₀
generators (suc zero)          = g₁
generators ₂    = g₂
generators (suc (suc (suc _))) = g₃

------------------------------------------------------------------------
-- The RM(1, 3) code.
------------------------------------------------------------------------

RM-1-3 : ImageCode 4 8
RM-1-3 = record { generator = linear-from-images generators }

------------------------------------------------------------------------
-- Convenience: the 4-tuple of basis-images as a Vec (useful for
-- iterating in proofs / downstream consumers).
------------------------------------------------------------------------

basis-images : Fin 4 → Vector 8
basis-images = generators
