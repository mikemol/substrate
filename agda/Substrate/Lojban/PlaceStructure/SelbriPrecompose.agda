------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.SelbriPrecompose
--
-- Defines: selbri-precompose
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.SelbriPrecompose where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lojban.PlaceStructure.Private
open import Substrate.Lojban.PlaceStructure.Selbri
open import Substrate.Lojban.Fragment.Carriers
open import Substrate.Lojban.Bridi



------------------------------------------------------------------------
-- 5. Sumti-substitution (pre-composition on the argument vector).
--
-- Pre-composing an n-ary substitution s : Vec Sumti' n → Vec Sumti n
-- on the argument side yields a new selbri at the new Sumti carrier.
-- Useful for L6 (cmavo wrappers that rearrange argument vectors)
-- and for the eventual Sumti-renaming arc.
------------------------------------------------------------------------

selbri-precompose :
  {Sumti Sumti' : Set ℓA} {Sem : Set ℓB} →
  (Vec Sumti' n → Vec Sumti n) →
  Selbri n Sumti Sem → Selbri n Sumti' Sem
selbri-precompose s S = mkSelbri (λ args → apply S (s args))
