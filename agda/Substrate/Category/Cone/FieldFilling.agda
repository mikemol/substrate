------------------------------------------------------------------------
-- Substrate.Category.Cone.FieldFilling
--
-- The field-filling constraint on a Cone: |apex| + |base| = q^k for
-- some prime power q^k.
--
-- Per [[project-3plus1-is-cone-instance]]: the M:N cone STRUCTURALLY
-- FILLS a finite field of size M+N. The apex isn't a free choice; it's
-- whatever completes the base to a prime-power total.
--
-- This module provides a lightweight record packaging:
--   * A Cone (apex + base + legs).
--   * The prime p and power k such that M+N = p^k.
--   * The cardinality witness (= proof apex-size + n ≡ p^k).
--
-- Primality of p is NOT enforced at the type level (would require
-- importing/building IsPrime infrastructure). The "prime power"
-- nature is a SEMANTIC commitment by the caller, documented but
-- not type-checked.
--
-- Substrate examples:
--   * 3+1 cone in V₄ ≅ F₂²: q=2, k=2, q^k = 4 = 3+1.
--   * 24+8 cone in F₂⁵: q=2, k=5, q^k = 32 = 24+8.
--   * 7+1 cone in F₂³ (Hamming): q=2, k=3, q^k = 8 = 7+1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.FieldFilling where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; _+_; _^_)
open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.Cone

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- N-1: FieldFilling record.
--
-- For a Cone with n base objects and apex of size apex-size, the
-- field-filling constraint asserts apex-size + n = p^k.
--
-- p and k are PARAMETERS — the caller chooses them, asserting that p
-- IS prime (semantic commitment, not type-checked here).
------------------------------------------------------------------------

record FieldFilling
  (n apex-size p k : ℕ)
  {Base : Fin n → Set ℓ}
  {Apex : Set ℓ}
  (cone : Cone n Base Apex)
  : Set where
  field
    fills : apex-size + n ≡ p ^ k

------------------------------------------------------------------------
-- N-2: Capstone.
--
-- After this slice: a Cone + field-filling witness packages the
-- substrate's structural claim that M:N cones live in finite fields
-- of size M+N.
--
-- The semantic constraint (p prime) isn't type-checked; relying on
-- the caller's commitment. A future arc could add an IsPrime
-- predicate and require it, but the substrate's existing prime-
-- power use sites (Z₂, Z₃, Z₅; F₂; V₄ = F₂²; etc.) have known
-- primes that the caller asserts naturally.
--
-- Substrate-wide implication: this record + the Cone primitive
-- formalize the M:N cone universal at the type level. Each
-- structurally-observed M:N split in the substrate (3+1, 7+1, 24+8,
-- 15+1, etc.) becomes a FieldFilling instance.
--
-- Per [[project-3plus1-is-cone-instance]]: this is the type-level
-- realization of the cardinality constraint that distinguishes the
-- cone primitive from a generic categorical product.
--
-- Deferred follow-ons:
--
--   * **IsPrime predicate + enforced primality**: add a substrate-
--     native IsPrime that's required by FieldFilling. Avoids
--     unsafe caller assertions.
--
--   * **Cardinality computation**: derive |apex| from the type
--     itself (needs Fin-iso witness on Apex), making the witness
--     mechanical rather than asserted.
--
--   * **Multi-field bonds when M+N is NOT a prime power**: per
--     [[project-3plus1-is-cone-instance]] bond extension, when
--     M+N can't fit a single field, the substrate has a bond
--     into another field. The FieldBond primitive (slice 8 of
--     this arc) handles this.
------------------------------------------------------------------------
