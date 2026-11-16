------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.SelbriPostcompose
--
-- Defines: selbri-postcompose
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.SelbriPostcompose where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lojban.PlaceStructure.Private
open import Substrate.Lojban.PlaceStructure.Selbri
open import Substrate.Lojban.Fragment.Carriers
open import Substrate.Lojban.Bridi



------------------------------------------------------------------------
-- 2. Post-composition: functorial in the codomain.
--
-- If S : Selbri n Sumti Sem and h : Sem → Sem', composing the meaning
-- function yields a new selbri at the new codomain. This is the
-- functoriality handle that L7 lifts.
------------------------------------------------------------------------

selbri-postcompose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} →
  (Sem → Sem') → Selbri n Sumti Sem → Selbri n Sumti Sem'
selbri-postcompose h S = mkSelbri (λ args → h (apply S args))
