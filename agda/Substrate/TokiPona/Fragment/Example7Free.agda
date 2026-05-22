------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example7Free
--
-- The free-linear universal property (T8), ready for T10's bridge
-- to consume.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example7Free where

open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.LinearAlgebra

free-witness : NimiFreeLinearization nimi-count
free-witness = canonical-nimi-free
