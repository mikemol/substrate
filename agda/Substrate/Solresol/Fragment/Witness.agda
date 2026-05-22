------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.Witness
--
-- The FreeOverBasis instance + LanguageWitness packaging for the
-- linguistic Rosetta classification arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.Witness where

open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         Free-cyclic; Solresol)
open import Substrate.Solresol.Fragment.Note using (Note)
open import Substrate.Solresol.Fragment.Word using (SolresolWord; single)

solresol-free-structure : FreeOverBasis Note SolresolWord
solresol-free-structure = mkFreeOverBasis single

solresol-witness : LanguageWitness
solresol-witness = mkWitness
  Solresol
  Note
  SolresolWord
  solresol-free-structure
  Free-cyclic
