------------------------------------------------------------------------
-- Eliza.Engine
--
-- The n-ary composition of all layers. Per-char ingestion fires the
-- full pipeline:
--
--   Char ─Router→ Gen ─Manifold→ Chamber ─Orbit→ Orbit
--          │            │             │            │
--          ▼            ▼             ▼            ▼
--      Predictor    Grammar(Gen)  Grammar(Cham) Grammar(Orb)
--                                   │
--                                   ▼
--                              Holonomy + Period
--                                   │
--                                   ▼
--                                Recorder
--
-- All layers chain through the substrate's Word-based representation:
-- the spine is Word α for varying α. The Engine's state bundles one
-- instance of each layer's state.
--
-- The entailment claim: gauge-equivariance composes through the chain.
-- Stated formally as `engine-respects-gauge` below.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Engine where

open import Eliza.Prelude    using (_×_; _,_; _≡_)
open import Eliza.Alphabets  using (Char; Gen; Chamber; Orbit; e)
open import Eliza.Word       using (Word)
open import Eliza.Router     using (Router)
import Eliza.Router as R
open import Eliza.Manifold   using (apply)
open import Eliza.Trajectory using (endpoint; walk)
open import Eliza.Orbit      using (orbit-of; project-trajectory)
open import Eliza.Holonomy   using (BC-Cell; ℋ-closes; shadow; κ-band)
open import Eliza.Predictor  using (Predictor; update; surprise-bits)
open import Eliza.Sequitur   using (Grammar; observe)
open import Eliza.Recorder   using (Database; Turn; record-turn)

------------------------------------------------------------------------
-- 1. The Engine's state. One record bundling every layer.
------------------------------------------------------------------------

record EngineState : Set where
  field
    router      : Router
    chamber     : Chamber
    predictor   : Predictor
    grammar-Gen : Grammar Gen
    grammar-Cha : Grammar Chamber
    grammar-Orb : Grammar Orbit
    database    : Database

------------------------------------------------------------------------
-- 2. The per-char step. Composition of all layers. The fundamental
-- semantic content of "running" the eliza system.
--
-- Note the structural layering: each layer consumes its input and
-- produces both an output (passed to the next layer) and an update
-- to its own state component.
------------------------------------------------------------------------

postulate
  step : EngineState → Char → EngineState

------------------------------------------------------------------------
-- 3. The structural contracts the Engine commits to.
------------------------------------------------------------------------

-- (a) Manifold-walking: the chamber-component of step is exactly
-- apply g x where g is the routed generator. Established by direct
-- unfolding of `step`; postulated as the spec.

postulate
  step-chamber :
    (es : EngineState) (c : Char) →
    -- EngineState.chamber (step es c) ≡ apply (router c) (chamber es)
    -- (full statement requires named record-field access; sketched)
    Set

-- (b) Orbit-equivariance: any function of the post-step orbit is
-- invariant under V₄-action on the chamber state. The substrate's
-- Cocycle Rule 5 lifted to the Engine.

postulate
  engine-respects-gauge :
    (es : EngineState) (c : Char) →
    -- orbit-of (chamber (step es c)) is V₄-invariant —
    -- (full statement of "gauge-invariance of orbit projection
    -- through the Engine step")
    Set

-- (c) Compression-as-incremental: bits-per-symbol from the predictor
-- + grammar layers is monotonically non-increasing in observations.
-- The compression-engine reading the user proposed.

postulate
  compression-monotone :
    (es es' : EngineState) (c : Char) →
    -- step es c ≡ es' →
    -- bits-per-symbol es' ≤ bits-per-symbol es
    -- (where bits-per-symbol is a running average defined elsewhere)
    Set

------------------------------------------------------------------------
-- 4. Word-level lifting. `run` consumes a Word Char and threads it
-- through the Engine, producing a final state and the trajectory.
------------------------------------------------------------------------

postulate
  engine-run : EngineState → Word Char → EngineState × Word Chamber

------------------------------------------------------------------------
-- 5. The structural decomposition this skeleton commits to.
--
-- The Python implementation of the Engine MUST factor into the layers
-- named in this module. No layer may bypass another. Specifically:
--
--   * The Router is the only access point to the Char alphabet.
--   * The Manifold is the only access point to chamber-step semantics.
--   * The Orbit module is the only access point to the V₄ cocycle.
--   * The Holonomy module is the only access point to spectral
--     coordinates + their non-commutativity.
--   * The Predictor is the only access point to the trigram model.
--   * The Sequitur is the only access point to grammar induction.
--   * The Recorder is the only access point to persistent state.
--
-- This factoring is the deliverable of the skeleton; it tells the
-- Python decomposition exactly what module boundaries to enforce.
------------------------------------------------------------------------
