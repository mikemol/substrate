------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Sym
--
-- Defines: ~-sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Sym where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.SymEq



~-sym : {A : Set} {s t : Stream A} → s ~ₛ t → t ~ₛ s
hd~ (~-sym p) = symEq (hd~ p)
tl~ (~-sym p) = ~-sym (tl~ p)
