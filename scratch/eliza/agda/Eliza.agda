------------------------------------------------------------------------
-- Eliza
--
-- Top-level imports for the eliza Agda skeleton. Re-exports every
-- layer module and states the n-ary entailment claim explicitly:
-- gauge-equivariance composes through the layered pipeline.
--
-- The skeleton's deliverable is the MODULE BOUNDARY, not the proof
-- content. Each module names a slice of the eliza Python script;
-- the Python decomposition must follow this factoring.
--
-- Module map (alphabet → role):
--
--   Eliza.Prelude       Self-contained type-theoretic basics (ℕ, ≡, ⊎, ×, Bool, Maybe).
--   Eliza.Word          Cons-list `Word α` — the universal spine at every layer.
--   Eliza.Transducer    Stateless + stateful per-symbol maps; composition.
--   Eliza.Alphabets     Char, Gen, Chamber, Orbit, V₄, Pairing, Chirality.
--   Eliza.Router        Char → Gen. The 1-cell selector layer.
--   Eliza.Manifold      Gen → Chamber → Chamber. Coxeter relations.
--   Eliza.Trajectory    Word Gen → Chamber → Word Chamber + period detection.
--   Eliza.Orbit         V₄-cocycle: orbit-of, fiber-of, decompose bijection.
--   Eliza.Holonomy      BC-cell, centroid, curvature, shadow chamber.
--   Eliza.Predictor     Trigram counter, surprise, project-text.
--   Eliza.Sequitur      Online grammar induction at any alphabet level.
--   Eliza.Synthesis     Unbiased / branched / grammar-projected continuations.
--   Eliza.Recorder      Database-backed counters + session lifecycle.
--   Eliza.Engine        n-ary composition + structural contracts.
--
-- The decomposition principle: every layer commits to a contract
-- (postulates + structural claims) that the Python implementation
-- must satisfy. No layer crosses another's boundary. The Engine is
-- the only assembly point.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza where

------------------------------------------------------------------------
-- Foundations.
------------------------------------------------------------------------

open import Eliza.Prelude    public
open import Eliza.Word       public
open import Eliza.Transducer public

------------------------------------------------------------------------
-- Alphabets + atomic actions.
------------------------------------------------------------------------

open import Eliza.Alphabets public
open import Eliza.Router    public
open import Eliza.Manifold  public

------------------------------------------------------------------------
-- Derived structures: trajectories, orbits, holonomy.
------------------------------------------------------------------------

open import Eliza.Trajectory public
open import Eliza.Orbit      public
open import Eliza.Holonomy   public

------------------------------------------------------------------------
-- Coalgebraic / grammatical layers.
------------------------------------------------------------------------

open import Eliza.Predictor public
open import Eliza.Sequitur  public
open import Eliza.Synthesis public

------------------------------------------------------------------------
-- Persistence + assembly.
------------------------------------------------------------------------

open import Eliza.Recorder public
open import Eliza.Engine   public
