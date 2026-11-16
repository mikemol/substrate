------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.NSNoncommute
--
-- Defines: N₊-S-noncommute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.NSNoncommute where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.TNeqf



N₊-S-noncommute : ((x : Evidence) → negPos (swapE x) ≡ swapE (negPos x)) → ⊥
N₊-S-noncommute h = t≢f (cong pos (h eP))
