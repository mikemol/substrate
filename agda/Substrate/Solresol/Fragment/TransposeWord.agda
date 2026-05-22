------------------------------------------------------------------------
-- Substrate.Solresol.Fragment.TransposeWord
--
-- transpose-word : SolresolWord → SolresolWord. The Z/7-action on
-- the basis lifted pointwise to an action on words. Witnesses the
-- FreeLinearization-style universal property at the free-cyclic site.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment.TransposeWord where

open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Solresol.Fragment.Word using (SolresolWord)
open import Substrate.Solresol.Fragment.Transpose using (transpose-1)

transpose-word : SolresolWord → SolresolWord
transpose-word []      = []
transpose-word (n ∷ w) = transpose-1 n ∷ transpose-word w
