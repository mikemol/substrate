------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Refl
--
-- Defines: ~-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Refl where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Op



~-refl : {A : Set} (s : Stream A) → s ~ₛ s
hd~ (~-refl s) = refl
tl~ (~-refl s) = ~-refl (tl s)
