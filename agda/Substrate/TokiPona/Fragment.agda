------------------------------------------------------------------------
-- Substrate.TokiPona.Fragment
--
-- Worked examples grounding the Toki Pona arc (T1-T8) against the
-- substrate's modifier-bilinear semantic space + particle-marker
-- algebra.
--
-- File-per-lemma decomposition per [[s3-on-v4-file-per-lemma]]:
--
--   Example1Intransitive      — soweli li suli
--   Example2Transitive        — mi moku e kili
--   Example3ModifierChain     — jan pona li toki e ijo
--   Example4PiRegrouping      — tomo lili pi soweli wawa
--   Example5ParticleStacking  — la + e particle stacking coherence
--   Example6Linearity         — TokiLinearity record witness (T7)
--   Example7Free              — NimiFreeLinearization witness (T8)
--
-- The substrate-vocabulary re-exports from the T1-T8 arc stay here so
-- downstream consumers (e.g. Substrate.Linguistic.ClosureCapstone)
-- continue to see the whole T-arc surface through one import.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Fragment where

-- Re-export T1-T8 publicly so consumers get the whole arc.
open import Substrate.TokiPona.SemanticSpace
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.NimiSpace
  using (nimi-as-vector; nimi-from-index; from-index∘index)
open import Substrate.TokiPona.ModifierBilinear
  using (modify; modifier-chain;
         modify-identityˡ; modify-identityʳ;
         modify-comm; modify-assoc; modify-self-inverse)
open import Substrate.TokiPona.TokiSentence
open import Substrate.TokiPona.Particles
open import Substrate.TokiPona.Linearity
open import Substrate.TokiPona.LinearAlgebra
-- Worked examples (file-per-lemma decomposition).
open import Substrate.TokiPona.Fragment.Example1Intransitive
open import Substrate.TokiPona.Fragment.Example2Transitive
open import Substrate.TokiPona.Fragment.Example3ModifierChain
open import Substrate.TokiPona.Fragment.Example4PiRegrouping
open import Substrate.TokiPona.Fragment.Example5ParticleStacking
open import Substrate.TokiPona.Fragment.Example6Linearity
open import Substrate.TokiPona.Fragment.Example7Free