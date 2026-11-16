------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.TwoNeq0
--
-- Defines: 2≢0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.SFinRoundTrip.TwoNeq0 where

open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Fin.Fin
import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


2≢0 : _≢_ {A = Fin 3} ₂ zero
2≢0 ()
