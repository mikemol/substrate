------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment.Example5ParticleStacking
--
-- Worked example: particle-stacking coherence.
--
-- Demonstrates T7's `mod-assoc` + the linearity coherence record's
-- `chain-++` law: combining particles via with-particle composes
-- their marker bits via merge-markers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment.Example5ParticleStacking where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.TokiPona.Particles
open import Substrate.TokiPona.Fragment.Example2Transitive
  using (example-mi-moku-e-kili)

-- A sentence with both `e` and `la` particles active:
example-5-stacked : MarkedSentence _
example-5-stacked =
  with-particle la (with-particle e (mark example-mi-moku-e-kili))

-- Compose markers directly:
example-5-direct-markers : MarkerSet
example-5-direct-markers =
  merge-markers (set-particle e) (set-particle la)

-- The composed marker matches the post-stacked one:
example-5-coherence :
  markers example-5-stacked ≡ example-5-direct-markers
example-5-coherence = refl
