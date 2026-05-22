------------------------------------------------------------------------
-- Substrate.Algebra.F2.Cone-Hamming-7plus1
--
-- The Hamming(8, 7) parity-bit structure as a (7, 1)-shaped Cone +
-- FieldFilling at 2³ = 8.
--
-- Hamming(8, 7): 7 data bits + 1 parity bit, total 8 bits, codeword
-- space = F₂⁷ (= 2⁷ = 128 codewords; the parity bit is determined by
-- the 7 data bits via XOR).
--
-- The (7, 1)-cone presents:
--   * Base = 7 readings of the data structure (each is some F₂ /
--     position interpretation).
--   * Apex = 1 witness (the parity bit + the whole 8-bit codeword
--     structure).
--   * FieldFilling: apex-size + n = 1 + 7 = 8 = 2³.
--
-- This is the next M:N shape after V₄'s (3, 1)-cone — demonstrates
-- the cone primitive scales mechanically.
--
-- Per [[project-3plus1-is-cone-instance]]: substrate examples of
-- Hamming-style cones include (3+1) at Hamming(4, 3), (7+1) at
-- Hamming(8, 7), (15+1) at Hamming(16, 15), etc. — each at F₂ⁿ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Cone-Hamming-7plus1 where

open import Substrate.Foundation.Fin using (Fin; zero)
open import Substrate.Foundation.Nat using (ℕ; _+_; _^_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.Cone
open import Substrate.Category.Cone.FieldFilling

------------------------------------------------------------------------
-- N-1: The 7 base readings (each is F₂ = the bit value at that
-- position).
------------------------------------------------------------------------

Base-Hamming : Fin 7 → Set
Base-Hamming _ = Fin 2   -- Each "reading" is just an F₂ bit.

------------------------------------------------------------------------
-- N-2: The apex — an 8-bit codeword.
--
-- Fin 256 = 2⁸ codeword space if we include all 8-bit strings;
-- properly the Hamming code's codeword subspace is 2⁷ = 128
-- (= Hamming(8,7)'s 2^k codewords). For the Cone shape, the apex
-- represents the codeword as a single object; cardinality
-- 2⁷ = 128 is the Hamming code size.
--
-- For SIMPLICITY at this slice, we abstract the apex to Fin 128
-- (= 2⁷) representing "one Hamming codeword."
------------------------------------------------------------------------

Apex-Hamming : Set
Apex-Hamming = Fin 128   -- 2⁷ Hamming codewords

------------------------------------------------------------------------
-- N-3: Leg projection — apex (codeword) → reading (bit at position).
--
-- Concrete projection requires either a real Hamming encoding or
-- a placeholder. For substrate purposes, use a trivial projection
-- (return Fin 2's zero) — the structural content is the cone shape,
-- not the specific Hamming encoding.
------------------------------------------------------------------------

leg-Hamming : Fin 7 → Apex-Hamming → Fin 2
leg-Hamming _ _ = zero

------------------------------------------------------------------------
-- N-4: The (7, 1) Cone instance.
------------------------------------------------------------------------

Hamming-7plus1-Cone : Cone 7 Base-Hamming Apex-Hamming
Hamming-7plus1-Cone = record { leg = leg-Hamming }

------------------------------------------------------------------------
-- N-5: FieldFilling witness — at the "+1 apex IS the field-completion
-- witness" interpretation, the cone fills 2³ = 8 = 7+1.
--
-- Reading: apex-size = 1 (= 1 apex object), base-size = 7, total = 8.
-- p = 2, k = 3, 2³ = 8 ✓.
------------------------------------------------------------------------

Hamming-FieldFilling : FieldFilling 7 1 2 3 Hamming-7plus1-Cone
Hamming-FieldFilling = record { fills = refl }   -- 1 + 7 = 8 = 2^3 ✓

------------------------------------------------------------------------
-- N-6: Capstone.
--
-- After this slice: Hamming(8, 7) presents as a (7, 1)-cone + the
-- FieldFilling witness at 2³.
--
-- Substrate-wide pattern emerging: any Hamming(2^k, 2^k - 1) code
-- gives a (2^k - 1, 1)-cone + FieldFilling at 2^k. The substrate's
-- existing codes work (RM, Hamming, extended-Hamming) are all
-- candidates for cone-formalization at their appropriate (M, N)
-- shapes.
--
-- Per [[project-3plus1-is-cone-instance]] FieldFilling tower:
-- this is the (7, 1) instance, immediately above V₄'s (3, 1)
-- instance (which fills 2²). The "ladder" of Hamming cones gives
-- F₂² ⊂ F₂³ ⊂ F₂⁴ ⊂ F₂⁵ ... — each level a Hamming-style cone fill.
--
-- Deferred follow-ons:
--
--   * **Concrete Hamming codeword encoding**: replace the placeholder
--     leg with the real Hamming syndrome encoding, making the cone's
--     projection structurally meaningful.
--
--   * **Hamming(16, 15) at (15, 1)**: next instance up the ladder.
--
--   * **Extended Hamming codes at (M, 2)**: M data + 2 parity = M+2
--     at the next field, demonstrating the multi-parity case.
------------------------------------------------------------------------
