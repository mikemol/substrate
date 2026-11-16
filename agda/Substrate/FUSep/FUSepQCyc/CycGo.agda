------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.CycGo
--
-- Defines: cyc-go
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.CycGo where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream



-- CycleWire's cycle: unfold a finite period into a PERIODIC stream (guarded
-- corecursion, the tail loops to the period start). THE greatest-fixed-point
-- object — the productive-periodic real.
cyc-go : {A : Set} → A → List A → List A → Stream A
hd (cyc-go x xs [])       = x
tl (cyc-go x xs [])       = cyc-go x xs xs
hd (cyc-go x xs (y ∷ ys)) = y
tl (cyc-go x xs (y ∷ ys)) = cyc-go x xs ys
