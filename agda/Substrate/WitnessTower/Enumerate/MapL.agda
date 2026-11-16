------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.MapL
--
-- Defines: mapL
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.MapL where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List



------------------------------------------------------------------------
-- 0. List helpers (map / concatMap not in Foundation.List; local).
------------------------------------------------------------------------

mapL : ∀ {a b} {A : Set a} {B : Set b} → (A → B) → List A → List B
mapL f []       = []
mapL f (x ∷ xs) = f x ∷ mapL f xs
