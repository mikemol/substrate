------------------------------------------------------------------------
-- Substrate.Codes.Hamming.H-8-4-4
--
-- M-8 of the Cocycles structural-migration plan. The extended
-- Hamming code [8, 4, 4]: length 8, dimension 4, minimum distance 4.
-- Obtained from Hamming [7, 4, 3] (M-7) by adding an "overall parity
-- bit" that constrains the total weight of every codeword to be
-- even.
--
-- Structural construction (the 3+1 parity-lift reading): the
-- overall parity bit IS the F₂² parity relation lifted to length 8.
-- Per the universal 3+1 pattern (memory:
-- `project_3plus1_parity_universal`), the parity bit IS the
-- **chirality of the codeword** — ext-Hamming = "Hamming with
-- chirality balanced to zero." The 4th parity-check row IS the
-- chirality projection.
--
-- Construction:
--   * Take Hamming's parity-check `H : Vector 7 → Vector 3` (M-7's
--     H-cols).
--   * Augment to `H-ext : Vector 8 → Vector 4` by:
--       - Pad each of H's 3 rows with 𝟘 in the new 8th column
--         (the new bit position doesn't participate in the original
--         parity checks).
--       - Add a 4th row of all-𝟙 (the overall-parity / chirality
--         row).
--   * Equivalently, each column of H-ext is built as
--     "(H-cols column augmented with 𝟙) for positions 0..6, and
--     (𝟎ⱽ {3} augmented with 𝟙) for position 7."
--
-- Min distance 4 follows from Hamming [7,4,3]'s distance 3 plus
-- parity-bit chirality balancing (every nonzero codeword of odd
-- weight gets one more 𝟙 from the parity bit, bumping its weight
-- to at least 4). Distance proof deferred — not needed for the
-- structural construction itself.
--
-- The iso ExtHamming-8-4-4 ≅ RM(1, 3) (a well-known fact: both are
-- the unique self-dual [8, 4, 4] binary code) requires dual-code
-- machinery and is deferred to a separate slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Codes.Hamming.H-8-4-4 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅; ₆; ₇; ₈)
open import Substrate.Foundation.Vec using ([]; _∷_)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.Algebra.F2.Code
open import Substrate.Codes.Hamming.H-7-4-3
  using (col₁; col₂; col₃; col₄; col₅; col₆; col₇)

------------------------------------------------------------------------
-- Append-𝟙: the structural "parity-lift" operation.
--
-- Each Hamming column (length-3 F₂-vector) becomes the corresponding
-- ext-Hamming column by appending 𝟙 — the contribution of that bit
-- position to the overall parity / chirality.
------------------------------------------------------------------------

append-𝟙 : Vector 3 → Vector 4
append-𝟙 (a ∷ b ∷ c ∷ []) = a ∷ b ∷ c ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- The 8 columns of the extended parity-check matrix.
--
-- Columns 1..7: lifted Hamming columns (the original H-cols, each
-- with a 𝟙 appended for overall-parity contribution).
-- Column 8: the "pure parity" column 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ [] — the
-- new 8th bit position contributes ONLY to the overall parity row.
------------------------------------------------------------------------

ext-col₁ ext-col₂ ext-col₃ ext-col₄ ext-col₅ ext-col₆ ext-col₇ ext-col₈ : Vector 4
ext-col₁ = append-𝟙 col₁
ext-col₂ = append-𝟙 col₂
ext-col₃ = append-𝟙 col₃
ext-col₄ = append-𝟙 col₄
ext-col₅ = append-𝟙 col₅
ext-col₆ = append-𝟙 col₆
ext-col₇ = append-𝟙 col₇
ext-col₈ = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- The column dispatcher (0-indexed Fin 8 → 1-indexed column).
------------------------------------------------------------------------

H-ext-cols : Fin 8 → Vector 4
H-ext-cols zero                                                = ext-col₁
H-ext-cols (suc zero)                                          = ext-col₂
H-ext-cols ₂                                    = ext-col₃
H-ext-cols ₃                              = ext-col₄
H-ext-cols ₄                        = ext-col₅
H-ext-cols ₅                  = ext-col₆
H-ext-cols ₆            = ext-col₇
H-ext-cols ₇         = ext-col₈

------------------------------------------------------------------------
-- The extended Hamming [8, 4, 4] code as a KernelCode.
--
-- The augmented parity-check linear map H-ext : Vector 8 → Vector 4
-- is built via linear-from-images, so apply H-ext (basis i) =
-- H-ext-cols i = ext-col(i+1).
------------------------------------------------------------------------

ExtHamming-8-4-4 : KernelCode 8 4
ExtHamming-8-4-4 = record { parity-check = linear-from-images H-ext-cols }
