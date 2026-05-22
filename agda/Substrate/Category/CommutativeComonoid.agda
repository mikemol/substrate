------------------------------------------------------------------------
-- Substrate.Category.CommutativeComonoid
--
-- MK2: a commutative comonoid additionally satisfies cocommutativity:
--   swap ∘ comult ≡ comult
-- where swap is the symmetry of the underlying SMC.
--
-- This is the structure each object in a Markov category carries.
-- Per [[categorical-name-first]]: commutative comonoid is standard.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CommutativeComonoid where

open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.Comonoid

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- A commutative comonoid extends Comonoid with cocommutativity.
-- The swap function is the symmetry of the underlying SMC; concrete
-- instances supply both the comonoid and the swap.

record CommutativeComonoid
       (Carrier : Set ℓ)
       (Tensor : Set ℓ → Set ℓ → Set ℓ)
       (Unit : Set ℓ) : Set ℓ where
  field
    comonoid : Comonoid Carrier Tensor Unit
    swap     : Tensor Carrier Carrier → Tensor Carrier Carrier
    -- Cocommutativity: swap (comult x) ≡ comult x.
    -- Stated as a field; concrete instances provide the proof.
    cocomm   : (x : Carrier) →
               swap (comult comonoid x) ≡ comult comonoid x

open CommutativeComonoid public

-- File-per-lemma child re-exported here so consumers see the
-- CommutativeComonoid surface through one import.
open import Substrate.Category.CommutativeComonoid.Term public
