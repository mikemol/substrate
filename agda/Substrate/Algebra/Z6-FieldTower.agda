------------------------------------------------------------------------
-- Substrate.Algebra.Z6-FieldTower
--
-- Z/6 as a FieldTower 2 instance: chain Z/6 → Z/3 → Z/1.
--
-- Demonstrates the multi-field bond tower at small n. Z/6 = 2·3
-- factors into Z/3 (after extracting the Z/2 component, since
-- gcd(2, 3) = 1 the quotient by ⟨3⟩ gives Z/2, but the cleaner
-- chain is mod-3: Z/6 → Z/3 sends n ↦ n mod 3).
--
-- The 3-element chain (Z/6, Z/3, Z/1) with two bonds (mod 3, mod 1)
-- realizes a FieldTower 2 — i.e., 3 host fields with 2 oriented
-- bonds.
--
-- Note: a tower with 3 PRIME factors (Z/30 = 2·3·5) would more
-- naturally fit FieldTower 2 with primes as host fields, but the
-- per-case mod-30 has 30 inhabitants. The Z/6 → Z/3 → Z/1 chain is
-- smaller and demonstrates the tower shape with manageable case
-- enumeration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z6-FieldTower where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅)
open import Substrate.Category.MultiFieldBond

------------------------------------------------------------------------
-- N-1: Bond Z/6 → Z/3 (mod 3, by case enumeration).
------------------------------------------------------------------------

mod3-of-6 : Fin 6 → Fin 3
mod3-of-6 zero                                                = zero
mod3-of-6 ₁                                          = suc zero
mod3-of-6 ₂                                    = suc ₁
mod3-of-6 ₃                              = zero
mod3-of-6 ₄                        = suc zero
mod3-of-6 ₅                  = suc ₁

------------------------------------------------------------------------
-- N-2: Bond Z/3 → Z/1 (always zero, since Z/1 has one inhabitant).
------------------------------------------------------------------------

to-trivial : Fin 3 → Fin 1
to-trivial _ = zero

------------------------------------------------------------------------
-- N-3: The FieldTower 2 instance.
------------------------------------------------------------------------

Z6-FieldTower : FieldTower 2
Z6-FieldTower = record
  { Field = λ where
      zero             → Fin 6
      ₁       → Fin 3
      ₂ → Fin 1
  ; Bond = λ where
      zero       → mod3-of-6
      ₁ → to-trivial
  }

------------------------------------------------------------------------
-- N-4: Capstone.
--
-- After this slice: Z/6 → Z/3 → Z/1 instantiates FieldTower 2 (=
-- 3 host fields, 2 oriented bonds). Substrate's first multi-field
-- tower instance.
--
-- Scaling: Z/30 → Z/6 → Z/2 (or any 3-prime chain) follows the
-- same shape but needs 30-case per-mod enumeration; deferred until
-- a use site demands.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension: realizes
-- the multi-host-field reading at 3 fields. The Z6-FieldBond
-- (slice 9 of the Cone+Bond arc) was the 2-field case (FieldTower 1);
-- this is the 3-field case (FieldTower 2).
------------------------------------------------------------------------
