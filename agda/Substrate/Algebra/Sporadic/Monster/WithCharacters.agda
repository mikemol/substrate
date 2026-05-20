------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.Monster.WithCharacters
--
-- Character-data module for the Monster. Provides a parametric
-- placeholder for the 194 × 194 = 37,636 character-table values
-- (ATLAS-cited externally).
--
-- U4 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Sibling to T8 (Monster.AsCoalgebra); together they give the
-- complete substrate-side representation of the Monster as a
-- ConjugationCoalgebra with character table.
--
-- Per [[continuous-via-discrete-inference-rules]]: 37,636 ℤ values
-- (finite, discrete) is well within substrate scope as long as the
-- data is supplied as input rather than enumerated internally.
--
-- Per [[expose-generator-not-orbit]] at extreme scale: 37,636
-- character values + 194 class representatives + 194 in-class
-- predicates fully describe the Monster's representation theory.
-- Compare with 10^53 element enumeration: ~16 orders of magnitude
-- compression.
--
-- This module's role is to NAME the Monster's character-data target.
-- Concrete consumer modules supply (V + Char) and wire to the
-- T8 ConjugationCoalgebra to produce a full WithCharacters instance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)
open import Data.Fin using (Fin)

module Substrate.Algebra.Sporadic.Monster.WithCharacters
  -- The value type for character values.
  -- For ordinary characters of the Monster, V = ℤ suffices for most
  -- entries (the Monster has many integer-valued characters); some
  -- entries require algebraic extensions ℤ[α] / ℤ[ζ_n] for various n.
  {ℓV : Level}
  (V : Set ℓV)
  -- The 194 × 194 character table.
  (Monster-Char : Fin 194 → Fin 194 → V)
  where

------------------------------------------------------------------------
-- 1. Re-export the character function with a documented name.
------------------------------------------------------------------------

Monster-character-table : Fin 194 → Fin 194 → V
Monster-character-table = Monster-Char

------------------------------------------------------------------------
-- 2. Capstone — Monster character data placeholder in place.
--
-- U4 of the 20-slice arc. The 194 × 194 table is supplied as a
-- module parameter. Concrete consumer modules combining this with
-- T8's Monster-ConjugationCoalgebra produce a full WithCharacters
-- instance — the substrate's most complete representation of the
-- Monster.
--
-- Outstanding concrete content: actual ATLAS values. The 194 × 194
-- table is well-documented in the ATLAS of Finite Groups and in
-- Conway-Norton 1979 ("Monstrous Moonshine"); populating substrate-
-- side data is a mechanical follow-on (~37,636 entries; can be
-- transcribed in batches per-row).
--
-- Per [[shadow-architecture]]: this is a thin DBE-naming slice;
-- structural content + scope-discipline established, actual data
-- entry is downstream.
--
-- Next: U5 (WithCharacters capstone refresh).
------------------------------------------------------------------------
