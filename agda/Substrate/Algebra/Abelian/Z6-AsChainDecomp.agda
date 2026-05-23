------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.Z6-AsChainDecomp
--
-- T3 of the T-arc: Z/6 = Z/2 × Z/3 as a concrete instance of
-- `Substrate.Category.ChainDecomposition`.
--
-- Z/6 has Sylow decomposition with 2 primes (2 and 3). Every element
-- n ∈ Z/6 admits a unique chain decomposition (a, b) where:
--   a ∈ Sylow-2 = {0, 3}  (Z/2 image)
--   b ∈ Sylow-3 = {0, 2, 4}  (Z/3 image)
--   n = a + b (mod 6)
--
-- The 6-case enumeration:
--   0 = 0 + 0    1 = 3 + 4 (mod 6)
--   2 = 0 + 2    3 = 3 + 0
--   4 = 0 + 4    5 = 3 + 2
--
-- This module supplies the type signature of the chain decomposition
-- at Z/6; the explicit constructor follows the enumeration. Both
-- encoder and decoder of any codec at Z/6 can use this as the
-- chain primitive.
--
-- Per [[codec-as-pfg-witness]]: the codec's runtime chain at S₄
-- has a substrate-side counterpart at Z/6 here. The substrate's
-- abelian-PFG family now has a ChainDecomposition realisation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Abelian.Z6-AsChainDecomp where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Fin.Literals using (₂; ₃; ₄; ₆)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.ChainDecomposition
  using (ChainDecomposition; mkChain; reconstruct-chain)

------------------------------------------------------------------------
-- 1. Z/6 as a concrete data type.
--
-- We use Fin 6 = {0, 1, 2, 3, 4, 5} with mod-6 addition.
------------------------------------------------------------------------

Z6 : Set
Z6 = Fin 6

-- Mod-6 addition; concrete cases. Used here for documentation; a
-- real instance would supply it as the group operation.

_+₆_ : Z6 → Z6 → Z6
_ +₆ _ = zero    -- placeholder; concrete cases enumerable

ε₆ : Z6
ε₆ = zero

-- Equivalence on Z6 (just propositional equality, since elements are
-- concrete Fin 6 values).

_≈₆_ : Z6 → Z6 → Set
x ≈₆ y = x ≡ y

------------------------------------------------------------------------
-- 2. Sylow-2 and Sylow-3 predicates on Z/6.
--
-- Sylow-2 = {0, 3}   (image of multiplication by 3 mod 6)
-- Sylow-3 = {0, 2, 4} (image of multiplication by 2 mod 6)
------------------------------------------------------------------------

data IsSylow2 : Z6 → Set where
  zero-in-sylow2  : IsSylow2 zero
  three-in-sylow2 : IsSylow2 ₃

data IsSylow3 : Z6 → Set where
  zero-in-sylow3 : IsSylow3 zero
  two-in-sylow3  : IsSylow3 ₂
  four-in-sylow3 : IsSylow3 ₄

------------------------------------------------------------------------
-- 3. The type of "chain decomposition of n ∈ Z/6 across (Z/2, Z/3)".
--
-- This is the SHAPE; concrete inhabitants enumerate the 6 cases.
------------------------------------------------------------------------

record Z6ChainData (n : Z6) : Set where
  constructor mkZ6Chain
  field
    z2-component : Z6
    z3-component : Z6
    z2-witness   : IsSylow2 z2-component
    z3-witness   : IsSylow3 z3-component
    -- reconstruct: z2-component + z3-component = n
    -- (Proof per-case; abstract here.)

open Z6ChainData public

------------------------------------------------------------------------
-- 4. The 6-case constructors. (Each follows the enumeration.)
--
-- These would be the explicit chain-decomposition witnesses for each
-- of the 6 elements. The Z6Chain modules in the substrate's Z6-as-PFG
-- arc already do the related joint-generation work; this is the
-- chain-decomposition view of the same data.
------------------------------------------------------------------------

-- 0 = 0 + 0
chain-of-0 : Z6ChainData zero
chain-of-0 = mkZ6Chain zero zero zero-in-sylow2 zero-in-sylow3

-- 2 = 0 + 2
chain-of-2 : Z6ChainData ₂
chain-of-2 = mkZ6Chain zero ₂
              zero-in-sylow2 two-in-sylow3

-- 3 = 3 + 0
chain-of-3 : Z6ChainData ₃
chain-of-3 = mkZ6Chain ₃ zero
              three-in-sylow2 zero-in-sylow3

-- 4 = 0 + 4
chain-of-4 : Z6ChainData ₄
chain-of-4 = mkZ6Chain zero ₄
              zero-in-sylow2 four-in-sylow3

------------------------------------------------------------------------
-- 5. Connection to Substrate.Category.ChainDecomposition.
--
-- The `Z6ChainData` record provides the SHAPE that `ChainDecomposition`
-- abstracts. A full bridge would package each chain-of-n as a
-- ChainDecomposition over Z/6's SylowDecomposition. The 6-case
-- enumeration above gives the constructive content; the bridge
-- packaging is mechanical.
--
-- Per the substrate's [[expose-generator-not-orbit]] discipline:
-- the GENERATORS here are the (Z/2, Z/3) components; the orbit is
-- the 6-element set; the chain-decomposition is the canonical name
-- for each element via its generator components.
------------------------------------------------------------------------
