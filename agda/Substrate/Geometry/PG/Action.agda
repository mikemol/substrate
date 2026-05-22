------------------------------------------------------------------------
-- Substrate.Geometry.PG.Action
--
-- The action of an F₂-linear map on PG. When the map preserves
-- nonzeroness, it lifts pointwise from F₂^(n+1) to PG n.
--
-- The action permutes points of PG when the map is invertible —
-- this is the GL(n+1, F₂) action on PG(n, F₂). Concretely
-- demonstrated at n=2 by Substrate.Geometry.HodgeDim3.Gl3's σ
-- and τ generators.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG.Action where

open import Substrate.Foundation.Nat using (suc)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Algebra.F2.Linear
open import Substrate.Geometry.PG.Type using (PG)
open import Substrate.Geometry.PG.Preserves using (Preserves-Nonzero)

PG-act :
  ∀ {n} (L : Linear (suc n) (suc n)) →
  Preserves-Nonzero L →
  PG n → PG n
PG-act L pres (v , v≢𝟎) = (apply L v , pres v v≢𝟎)
