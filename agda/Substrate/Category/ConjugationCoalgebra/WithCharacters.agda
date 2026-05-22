------------------------------------------------------------------------
-- Substrate.Category.ConjugationCoalgebra.WithCharacters
--
-- Extension of T3 ConjugationCoalgebra adding character-table data:
-- a function Class × Class → V where V is the user-chosen value type
-- (typically ℤ or ℚ). The character table is the cohomological
-- diffraction content — characters are the "Fourier coefficients" of
-- the conjugation coalgebra's action on irreducible representations.
--
-- U1 of the WithCharacters / Happy-Family extension arc per
-- [[prime-factored-gauge-arc]] follow-on.
--
-- Per [[continuous-via-discrete-inference-rules]]: the character
-- table is FINITE discrete data (Class × Class entries; finite group
-- ⇒ finite Class index). No continuous content; substrate-safe.
--
-- Per [[categorical-name-first]]: "character table" / "character of a
-- representation" is standard categorical naming from finite group
-- theory; the universal property is "irreducible-class-function
-- decomposition" (= row orthogonality + column orthogonality).
-- Orthogonality axioms are deferred to U2; this slice just adds the
-- table data field.
--
-- Per [[expose-generator-not-orbit]]: with characters added, the
-- Monster's 194 × 194 = 37636 character values + 194 class
-- representatives + 194 in-class predicates fully describe the
-- group's structural content — vastly more efficient than enumerating
-- 10^53 elements.
--
-- Value type V parametric: instances pick their own (ℤ for most
-- ordinary characters; ℚ if rational characters appear; ℤ[ζ] for
-- groups with non-rational character values).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConjugationCoalgebra.WithCharacters where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.ConjugationCoalgebra
  using (ConjugationCoalgebra)

private
  variable
    ℓ ℓV : Level

------------------------------------------------------------------------
-- The WithCharacters extension record.
--
-- Bundles a base ConjugationCoalgebra with character-table data over
-- a user-chosen value type V. The Char function takes two classes
-- (irrep index, class index) and returns the corresponding character
-- value.
--
-- Convention: Char i c = the i-th irreducible character evaluated at
-- the class-c representative. For finite groups, the number of
-- irreducible characters equals the number of conjugacy classes
-- (= the cardinality of Class). So Char : Class × Class → V is the
-- complete character table.
--
-- Orthogonality axioms (U2 follow-on) are NOT in this record — the
-- minimal extension adds just the table data; downstream consumers
-- can layer orthogonality as a separate WithOrthogonality wrapper.
------------------------------------------------------------------------

record WithCharacters
  (base : ConjugationCoalgebra {ℓ})
  (V : Set ℓV) : Set (ℓ ⊔ ℓV) where
  constructor mkWithCharacters
  open ConjugationCoalgebra base using (Class)
  field
    Char : Class → Class → V

open WithCharacters public

------------------------------------------------------------------------
-- Capstone — character extension primitive in place.
--
-- U1 of the WithCharacters / Happy-Family arc. With U1 landed:
--   * U2 will add character orthogonality axioms (row/column)
--   * U3 will populate GL(3, F₂) ≅ PSL(2,7)'s 6 × 6 character table
--     as a concrete WithCharacters instance (V = ℤ)
--   * U4 will instantiate Monster.WithCharacters with parametric
--     194 × 194 character data (V = ℤ or ℚ)
--
-- Per [[expose-generator-not-orbit]]: the character table IS the
-- cohomological description of the group's representation theory
-- — far more compact than element enumeration even for the Monster.
--
-- Per [[homology-cohomology-recursion]]: the conjugation coalgebra
-- (T3) is the HOMOLOGY side (observed structure); the character
-- table (this extension) is the COHOMOLOGY side (cataloged
-- structure). Together they instantiate the substrate's
-- observed↔cataloged duality at the group-theoretic level.
------------------------------------------------------------------------
