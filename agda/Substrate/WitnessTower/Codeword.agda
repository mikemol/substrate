------------------------------------------------------------------------
-- Substrate.WitnessTower.Codeword
--
-- BUILD (not assert) the dossier §4 codeword layer: the incident vector
-- is an RM(1,4) codeword. RM(1,4) is the direct m=4 analogue of the
-- existing Substrate.Codes.ReedMuller.RM-1-3 (which is m=3): the
-- evaluations of the degree-≤1 monomials {1, x₁, x₂, x₃, x₄} at the 16
-- points of GF(2)⁴, as a generator-matrix (ImageCode) code.
--
-- Parameters (the dossier's §4 numbers, here as the actual build):
--   length 16   (Vector 16 — the 16 evaluation points / incident bits)
--   dimension 5 (5 generators: the constant + 4 coordinate projections)
--   ⟹ 2⁵ = 32 codewords ("32" is the COUNT, not a bit-length — the
--      dossier's explicit warning against re-reading it as RM(1,5)).
--
-- Message split (dossier §4): the 5 message bits = (2-bit V₄) ⊕ (3-bit
-- S₃ frame). The V₄ factor is a true GF(2)² SUBSPACE (XOR-closed); the
-- S₃ factor is 3 bits, 6 of 8 valid; 4 × 6 = 24 = |S₄| valid actions,
-- 8-codeword complement. What this file BUILDS is the code itself + the
-- generator structure; the count/length are definitional in the types.
-- (Distance-8 over all 32×32 pairs is a larger computation; not done
-- here — see the status note at the end.)
--
-- Convention (LSB-first point indexing, extending RM-1-3): point p in
-- 0..15 has bits (x₁ x₂ x₃ x₄) = (p&1, p&2, p&4, p&8).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Codeword where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Code

------------------------------------------------------------------------
-- 1. The 5 generators: evaluations of {1, x₁, x₂, x₃, x₄} at the 16
--    points of GF(2)⁴ (LSB-first). Each is a Vector 16.
------------------------------------------------------------------------

-- g₀ = 1 : the constant function (all 16 points evaluate to 𝟙).
g₀ : Vector 16
g₀ = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙
   ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

-- g₁ = x₁ : bit 0 of the point index (period 2).
g₁ : Vector 16
g₁ = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙
   ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []

-- g₂ = x₂ : bit 1 (period 4).
g₂ : Vector 16
g₂ = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙
   ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []

-- g₃ = x₃ : bit 2 (period 8).
g₃ : Vector 16
g₃ = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙
   ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

-- g₄ = x₄ : bit 3 (period 16 — first half 𝟘, second half 𝟙).
g₄ : Vector 16
g₄ = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘
   ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- 2. The generator dispatcher: Fin 5 → Vector 16. dimension = 5.
------------------------------------------------------------------------

generators : Fin 5 → Vector 16
generators zero                      = g₀
generators (suc zero)                = g₁
generators (suc (suc zero))          = g₂
generators (suc (suc (suc zero)))    = g₃
generators (suc (suc (suc (suc _)))) = g₄

------------------------------------------------------------------------
-- 3. RM(1,4) as a generator-matrix code: ImageCode 5 16.
--    k = 5 (message bits / dimension), n = 16 (length). 2⁵ = 32 codewords.
------------------------------------------------------------------------

RM-1-4 : ImageCode 5 16
RM-1-4 = record { generator = linear-from-images generators }

------------------------------------------------------------------------
-- 4. The message-bit split (dossier §4): the 5 generators partition as
--    (V₄ axis: g₀,g₁ — wait, the split is 2-bit V₄ ⊕ 3-bit S₃). We name
--    the two generator-blocks so the V₄/S₃ factoring is explicit at the
--    code level. (Which 2 vs which 3 is a basis choice; the dossier's
--    claim is that SOME 2+3 split makes the V₄ block a true subspace —
--    here recorded as the named partition, the subspace-closure proof
--    deferred to a computation over the 4 V₄ codewords.)
------------------------------------------------------------------------

-- V₄ block: 2 of the 5 message coordinates (a GF(2)² subspace of messages).
V₄-gens : Fin 2 → Vector 16
V₄-gens zero       = g₁
V₄-gens (suc _)    = g₂

-- S₃ block: 3 of the 5 (the frame; 6 of its 8 patterns valid).
S₃-gens : Fin 3 → Vector 16
S₃-gens zero             = g₀
S₃-gens (suc zero)       = g₃
S₃-gens (suc (suc _))    = g₄

------------------------------------------------------------------------
-- STATUS (honest): BUILT here — the RM(1,4) generator code (length 16,
-- dimension 5, hence 32 codewords), as the m=4 analogue of RM-1-3, and
-- the named V₄/S₃ generator partition. NOT built here: the distance-8
-- spectrum (all 32×32 pairwise weights), the V₄-block XOR-closure proof,
-- and the 24-valid / 8-complement count — these are computations over the
-- enumerated codeword set (a follow-on). The dossier's §4 "VERIFIED"
-- referred to a separate session's external build; in THIS tree, length
-- and dimension are definitional (the types), the rest is POSITED pending
-- the codeword-enumeration computation.
------------------------------------------------------------------------
