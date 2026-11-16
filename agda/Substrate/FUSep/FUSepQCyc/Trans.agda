------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Trans
--
-- Defines: ~-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Trans where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.Op
open import Substrate.FUSep.FUSepQCyc.TrEq



~-trans : {A : Set} {s t u : Stream A} → s ~ₛ t → t ~ₛ u → s ~ₛ u
hd~ (~-trans p q) = trEq (hd~ p) (hd~ q)
tl~ (~-trans p q) = ~-trans (tl~ p) (tl~ q)
