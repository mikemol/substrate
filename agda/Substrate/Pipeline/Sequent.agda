------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent
--
-- The structural rules of sequent calculus, lifted to the brick layer.
-- Every wire between two bricks IS a Sequent brick — a structural
-- derivation that the upstream's D-out is acceptable as the downstream's
-- D-in. File-per-lemma decomposition:
--
--   Sequent.SequentRule              — 6 structural-rule tags
--   Sequent.SequentType              — signature (A → B) + brick lifter
--   Sequent.Type                     — Sequent record
--   Sequent.AsBrick                  — lift to the Brick framework
--
-- The standard structural rules as concrete Sequents:
--   Sequent.IdentitySequent          — A ⊢ A
--   Sequent.WeakeningSequent         — A ⊢ A × B
--   Sequent.ContractionSequent       — A × A ⊢ A
--   Sequent.ExchangeSequent          — A × B ⊢ B × A
--   Sequent.CoerceSequent            — A ⊢ B via named iso
--   Sequent.CutSequent               — composition
--   Sequent.ComposeViaSequent        — bridge two Bricks via Sequent
--
-- Fixed-point Sequents (the substrate's coalgebraic-stability pattern):
--   Sequent.CanonicalSpec            — canonical-form predicate
--   Sequent.SequentFixed             — endofunction + spec + obligation
--   Sequent.IterateToCanonical       — terminating iteration
--   Sequent.FixedPointSequentToBrick — lift fixed-point sequent to Brick
--
-- A general Sequent has shape A → A (endofunction); the derivation
-- iterates until a canonical predicate holds. Structural-rule
-- Sequents are the degenerate case (canonical = ⊤, zero iterations).
-- Normalising Sequents (e.g., Coxeter `normalize`) have non-trivial
-- canonical predicates.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent where

open import Substrate.Pipeline.Sequent.SequentRule                 public
open import Substrate.Pipeline.Sequent.SequentType                 public
open import Substrate.Pipeline.Sequent.Type                        public
open import Substrate.Pipeline.Sequent.AsBrick                     public
open import Substrate.Pipeline.Sequent.IdentitySequent             public
open import Substrate.Pipeline.Sequent.WeakeningSequent            public
open import Substrate.Pipeline.Sequent.ContractionSequent          public
open import Substrate.Pipeline.Sequent.ExchangeSequent             public
open import Substrate.Pipeline.Sequent.CoerceSequent               public
open import Substrate.Pipeline.Sequent.CutSequent                  public
open import Substrate.Pipeline.Sequent.ComposeViaSequent           public
open import Substrate.Pipeline.Sequent.CanonicalSpec               public
open import Substrate.Pipeline.Sequent.SequentFixed                public
open import Substrate.Pipeline.Sequent.IterateToCanonical          public
open import Substrate.Pipeline.Sequent.FixedPointSequentToBrick    public
