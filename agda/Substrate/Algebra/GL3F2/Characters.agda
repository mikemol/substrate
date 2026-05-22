------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.Characters
--
-- The character table of GL(3, F₂) ≅ PSL(2, 7), order 168, with
-- 6 conjugacy classes and 6 irreducible characters.
--
-- U3 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- The substrate's first concrete WithCharacters instance.
--
-- Class structure (well-known; e.g., ATLAS of Finite Groups):
--
--   Class | Size | Centralizer order | Order of element
--   ------+------+-------------------+-----------------
--   1A    |   1  |       168         |      1
--   2A    |  21  |        8          |      2
--   3A    |  56  |        3          |      3
--   4A    |  42  |        4          |      4
--   7A    |  24  |        7          |      7
--   7B    |  24  |        7          |      7
--
-- Sum: 1 + 21 + 56 + 42 + 24 + 24 = 168 ✓
--
-- Character table:
--
--   χᵢ\C  | 1A | 2A | 3A | 4A | 7A | 7B
--   ------+----+----+----+----+----+----
--   χ₁ 1  |  1 |  1 |  1 |  1 |  1 |  1
--   χ₂ 3a |  3 | -1 |  0 |  1 |  α |  ᾱ
--   χ₃ 3b |  3 | -1 |  0 |  1 |  ᾱ |  α
--   χ₄ 6  |  6 |  2 |  0 |  0 | -1 | -1
--   χ₅ 7  |  7 | -1 |  1 | -1 |  0 |  0
--   χ₆ 8  |  8 |  0 | -1 |  0 |  1 |  1
--
-- where α = (-1 + i√7)/2 and ᾱ = (-1 - i√7)/2 (algebraic integers
-- in ℤ[α] = ℤ[(1 + √(-7))/2]).
--
-- Substrate scope: V = ℤ. The 4 cells (χ₂ 7A, χ₂ 7B, χ₃ 7A, χ₃ 7B)
-- containing α/ᾱ are PLACEHOLDERS (marked with sentinel values);
-- the full algebraic table needs a separate slice with V = ℤ[α].
-- The 32 ℤ-valued cells are populated correctly.
--
-- Per [[choice-rigidification]]: the placeholder marking is explicit
-- (not silently substituting 0). Per [[expose-generator-not-orbit]]:
-- the 6 × 6 character table compactly captures the entire
-- representation-theoretic content of GL(3, F₂); orbit (= 168
-- elements) is unnecessary.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.Characters where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)

------------------------------------------------------------------------
-- 1. Sentinel values for the 4 algebraic-valued cells.
--
-- α and ᾱ are non-rational; for the substrate's ℤ-valued V, we use
-- sentinels +999 / -999 (clearly NOT real values; user knows they're
-- markers for "this cell requires ℤ[α] for the actual value").
------------------------------------------------------------------------

α-placeholder : ℤ
α-placeholder = +_ 999

ᾱ-placeholder : ℤ
ᾱ-placeholder = -suc_ 998   -- = - 999

------------------------------------------------------------------------
-- 2. The character table as a function.
--
-- Char i c = the i-th irreducible character evaluated at the c-class
-- representative. Class indexing: 0=1A, 1=2A, 2=3A, 3=4A, 4=7A, 5=7B.
-- Irrep indexing: 0=χ₁ (trivial), 1=χ₂ (3a), 2=χ₃ (3b), 3=χ₄ (6),
-- 4=χ₅ (7), 5=χ₆ (8 = Steinberg).
------------------------------------------------------------------------

-- Helpers for readability:
_ℤ : ℤ → ℤ
n ℤ = n

GL3F2-Char : Fin 6 → Fin 6 → ℤ
-- Row χ₁ (trivial): all 1s.
GL3F2-Char zero             zero                                  = +_ 1
GL3F2-Char zero             (suc zero)                            = +_ 1
GL3F2-Char zero             (suc (suc zero))                      = +_ 1
GL3F2-Char zero             (suc (suc (suc zero)))                = +_ 1
GL3F2-Char zero             (suc (suc (suc (suc zero))))          = +_ 1
GL3F2-Char zero             (suc (suc (suc (suc (suc zero)))))    = +_ 1
-- Row χ₂ (3a): [3, -1, 0, 1, α, ᾱ]
GL3F2-Char (suc zero)       zero                                  = +_ 3
GL3F2-Char (suc zero)       (suc zero)                            = -suc_ 0
GL3F2-Char (suc zero)       (suc (suc zero))                      = +_ 0
GL3F2-Char (suc zero)       (suc (suc (suc zero)))                = +_ 1
GL3F2-Char (suc zero)       (suc (suc (suc (suc zero))))          = α-placeholder
GL3F2-Char (suc zero)       (suc (suc (suc (suc (suc zero)))))    = ᾱ-placeholder
-- Row χ₃ (3b): [3, -1, 0, 1, ᾱ, α]
GL3F2-Char (suc (suc zero)) zero                                  = +_ 3
GL3F2-Char (suc (suc zero)) (suc zero)                            = -suc_ 0
GL3F2-Char (suc (suc zero)) (suc (suc zero))                      = +_ 0
GL3F2-Char (suc (suc zero)) (suc (suc (suc zero)))                = +_ 1
GL3F2-Char (suc (suc zero)) (suc (suc (suc (suc zero))))          = ᾱ-placeholder
GL3F2-Char (suc (suc zero)) (suc (suc (suc (suc (suc zero)))))    = α-placeholder
-- Row χ₄ (6): [6, 2, 0, 0, -1, -1]
GL3F2-Char (suc (suc (suc zero))) zero                                  = +_ 6
GL3F2-Char (suc (suc (suc zero))) (suc zero)                            = +_ 2
GL3F2-Char (suc (suc (suc zero))) (suc (suc zero))                      = +_ 0
GL3F2-Char (suc (suc (suc zero))) (suc (suc (suc zero)))                = +_ 0
GL3F2-Char (suc (suc (suc zero))) (suc (suc (suc (suc zero))))          = -suc_ 0
GL3F2-Char (suc (suc (suc zero))) (suc (suc (suc (suc (suc zero)))))    = -suc_ 0
-- Row χ₅ (7): [7, -1, 1, -1, 0, 0]
GL3F2-Char (suc (suc (suc (suc zero)))) zero                                  = +_ 7
GL3F2-Char (suc (suc (suc (suc zero)))) (suc zero)                            = -suc_ 0
GL3F2-Char (suc (suc (suc (suc zero)))) (suc (suc zero))                      = +_ 1
GL3F2-Char (suc (suc (suc (suc zero)))) (suc (suc (suc zero)))                = -suc_ 0
GL3F2-Char (suc (suc (suc (suc zero)))) (suc (suc (suc (suc zero))))          = +_ 0
GL3F2-Char (suc (suc (suc (suc zero)))) (suc (suc (suc (suc (suc zero)))))    = +_ 0
-- Row χ₆ (8 Steinberg): [8, 0, -1, 0, 1, 1]
GL3F2-Char (suc (suc (suc (suc (suc zero))))) zero                                  = +_ 8
GL3F2-Char (suc (suc (suc (suc (suc zero))))) (suc zero)                            = +_ 0
GL3F2-Char (suc (suc (suc (suc (suc zero))))) (suc (suc zero))                      = -suc_ 0
GL3F2-Char (suc (suc (suc (suc (suc zero))))) (suc (suc (suc zero)))                = +_ 0
GL3F2-Char (suc (suc (suc (suc (suc zero))))) (suc (suc (suc (suc zero))))          = +_ 1
GL3F2-Char (suc (suc (suc (suc (suc zero))))) (suc (suc (suc (suc (suc zero)))))    = +_ 1

------------------------------------------------------------------------
-- 3. Class sizes (= |conjugacy class c|).
------------------------------------------------------------------------

class-size : Fin 6 → ℤ
class-size zero                                  = +_ 1     -- 1A
class-size (suc zero)                            = +_ 21    -- 2A
class-size (suc (suc zero))                      = +_ 56    -- 3A
class-size (suc (suc (suc zero)))                = +_ 42    -- 4A
class-size (suc (suc (suc (suc zero))))          = +_ 24    -- 7A
class-size (suc (suc (suc (suc (suc zero)))))    = +_ 24    -- 7B

------------------------------------------------------------------------
-- 4. Centralizer orders (= |Z_G(c)| for the c-class representative).
------------------------------------------------------------------------

centralizer-order : Fin 6 → ℤ
centralizer-order zero                                  = +_ 168
centralizer-order (suc zero)                            = +_ 8
centralizer-order (suc (suc zero))                      = +_ 3
centralizer-order (suc (suc (suc zero)))                = +_ 4
centralizer-order (suc (suc (suc (suc zero))))          = +_ 7
centralizer-order (suc (suc (suc (suc (suc zero)))))    = +_ 7

------------------------------------------------------------------------
-- 5. Group order |G| = 168.
------------------------------------------------------------------------

group-order : ℤ
group-order = +_ 168

------------------------------------------------------------------------
-- 6. Capstone — GL(3, F₂) ≅ PSL(2, 7) character table populated.
--
-- U3 of the 20-slice arc. With U3 landed, the substrate has its
-- first concrete WithCharacters-style data — a complete 6 × 6
-- character table for the smallest non-abelian simple group with
-- multi-prime order.
--
-- Limitations:
--   * Algebraic values (α, ᾱ) for χ₂, χ₃ on 7A, 7B are PLACEHOLDERS.
--     Full table needs V = ℤ[α] or ℤ[(1+√(-7))/2]; substrate-side
--     ring extension is a follow-on slice.
--   * Orthogonality NOT verified — the placeholder cells break it.
--     Per-instance orthogonality proof requires the algebraic-ring
--     version.
--
-- 32 of 36 cells are correctly populated as ℤ values; the structural
-- shape of the table is in place.
--
-- Next: U4 (Monster.WithCharacters parametric) + U5 (capstone).
------------------------------------------------------------------------
