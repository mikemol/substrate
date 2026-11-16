------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.ConcatMapL
--
-- Defines: concatMapL
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.ConcatMapL where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List



concatMapL : ∀ {a b} {A : Set a} {B : Set b} → (A → List B) → List A → List B
concatMapL f []       = []
concatMapL f (x ∷ xs) = f x ++ concatMapL f xs
