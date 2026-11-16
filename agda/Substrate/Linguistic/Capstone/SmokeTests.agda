------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone.SmokeTests
--
-- Each witness belongs to the cell its WitnessName / classification
-- field claims it does. Six refl-cases verify internal consistency.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone.SmokeTests where

open import Substrate.Category.FreeOverBasis
  using (class; Free-monoid; Free-F2-module; Free-cyclic;
         Free-relation; Free-CCC; Free-Lie)
open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.TokiPona.AsFreeOverBasis.TokiponaWitness
open import Substrate.Solresol.Fragment.Witness using (solresol-witness)
open import Substrate.Kelen.Fragment.KelenWitness
open import Substrate.Lambda.Fragment.LambdaWitness
open import Substrate.Invented.LieFragment using (lie-witness)
open import Substrate.Foundation.Eq

lojban-in-Free-monoid : class lojban-witness ≡ Free-monoid
lojban-in-Free-monoid = refl

tokipona-in-Free-F2-module : class tokipona-witness ≡ Free-F2-module
tokipona-in-Free-F2-module = refl

solresol-in-Free-cyclic : class solresol-witness ≡ Free-cyclic
solresol-in-Free-cyclic = refl

kelen-in-Free-relation : class kelen-witness ≡ Free-relation
kelen-in-Free-relation = refl

lambda-in-Free-CCC : class lambda-witness ≡ Free-CCC
lambda-in-Free-CCC = refl

lie-in-Free-Lie : class lie-witness ≡ Free-Lie
lie-in-Free-Lie = refl
