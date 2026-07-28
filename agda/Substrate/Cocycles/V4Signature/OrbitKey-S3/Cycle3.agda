------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3
--
-- cycle3 (a b c : Fin 3) : SFinP.Permutation 3.
-- Parametric 3-cycle a → b → c → a (fixes the remaining index).
-- Expressed as composition of two transpositions: (a b) ∘ (b c).
-- Symmetric in (a, b, c); no chirality choice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.Cycle3 where

open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.Symmetric.Permutation.SFinCompose as SFinC
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
  using (transposition)

cycle3 : (a b c : Fin 3) → SFinP.Permutation 3
cycle3 a b c = transposition a b SFinC.· transposition b c
