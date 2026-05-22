------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example6Linearity
--
-- The TokiLinearity record (T7) in scope, witnessing the coherence
-- laws for any consumer of this fragment.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example6Linearity where

open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.Linearity

linearity-witness : TokiLinearity nimi-count
linearity-witness = canonical-linearity
