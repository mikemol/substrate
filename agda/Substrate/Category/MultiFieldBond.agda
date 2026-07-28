------------------------------------------------------------------------
-- Substrate.Category.MultiFieldBond
--
-- A tower of FieldBonds: a sequence of host fields connected by
-- oriented bonds. For a count c that factors into multiple prime
-- powers (c = p₁^k₁ · p₂^k₂ · ... · pₙ^kₙ), the substrate's
-- structural realization is a tower of n host fields connected by
-- n-1 bonds.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension: when a
-- structurally observed count is NOT a prime power, the structure
-- requires multiple host fields with bonds connecting them. This
-- module records the bond tower as data.
--
-- The simplest non-trivial tower: 2 fields + 1 bond = the plain
-- FieldBond primitive (slice 8 of the Cone+Bond arc). 3 fields + 2
-- bonds is the next level (e.g., Z/30 = F₂ × F₃ × F₅).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.MultiFieldBond where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- Cast Fin n → Fin (suc n) by reusing the same index.
------------------------------------------------------------------------

inj-suc : ∀ {k} → Fin k → Fin (suc k)
inj-suc zero    = zero
inj-suc (suc i) = suc (inj-suc i)

------------------------------------------------------------------------
-- FieldTower n: a sequence of n+1 carrier sets (indexed by Fin (suc n))
-- connected by n oriented bond morphisms.
--
-- Bond i : Field i → Field (suc i)  (= the bond going from the i-th
-- field to the (i+1)-th). Note the Fin n index for bonds is cast into
-- Fin (suc n) for indexing into Field.
------------------------------------------------------------------------

-- ⟡set1-rp: carrier→param — Field was a Set-valued FIELD (pinning the
-- record at Set (lsuc ℓ)); as a PARAMETER it never raises the sort.
record FieldTower (n : ℕ) (Field : Fin (suc n) → Set ℓ) : Set ℓ where
  field
    Bond    : (i : Fin n) → Field (inj-suc i) → Field (suc i)

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: a FieldTower n captures a chain of n+1 host
-- fields connected by n oriented bonds. Used for multi-prime-power
-- counts where a single FieldBond doesn't suffice.
--
-- Substrate examples (deferred to slice 5):
--   * Z/30 = Z/2 × Z/3 × Z/5: FieldTower 2 with bonds
--     Z/30 → Z/2, Z/30 → Z/3, Z/30 → Z/5 (= chain of CRT projections).
--   * 168 = 2³·3·7: FieldTower 2 with three host fields F₂³, F₃, F₇.
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- substrate's structural handle for composite-order Lagrange tower
-- decompositions.
------------------------------------------------------------------------
