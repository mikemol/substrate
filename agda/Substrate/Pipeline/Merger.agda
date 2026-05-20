------------------------------------------------------------------------
-- Substrate.Pipeline.Merger
--
-- The multi-input merger brick: takes a tuple of D-in streams and
-- selects one to admit on its D-out, per some strategy.
--
-- Dual to Chooser (in Brick.agda's Examples):
--
--   * Chooser:   one D-in → many candidate computes → one D-out.
--                Data selects compute (D⇒C witnessing).
--   * Merger:    many D-ins → one strategy → one D-out.
--                Compute (the strategy) selects data (C⇒D witnessing).
--
-- In sequent-calculus terms, Merger is the case-elimination rule:
--
--   Γ ⊢ A    Γ ⊢ B    Γ ⊢ C    ...
--   ─────────────────────────────── (case-elim by strategy σ)
--             Γ ⊢ X
--
-- where X is one of {A, B, C, ...} chosen by σ.
--
-- Strategies range over: round-robin, priority, predicate-based,
-- race-based, etc. The strategy is the C axis; the inputs are the
-- multi-D axis; the chosen output is witnessed by some State (the
-- strategy's memory: counter for round-robin, queue for priority,
-- etc.).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Merger where

open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Data.Nat using (ℕ; zero; suc; _+_; _%_)
open import Data.List using (List; []; _∷_; length)
open import Data.Fin using (Fin; zero; suc) renaming (fromℕ to Fin-fromℕ)
open import Substrate.Pipeline.Brick

------------------------------------------------------------------------
-- 1. Merger strategies as data.
------------------------------------------------------------------------

data MergeStrategy : Set where
  round-robin : MergeStrategy   -- cycle through inputs
  priority    : MergeStrategy   -- earliest input wins
  predicate   : MergeStrategy   -- predicate over input content
  race        : MergeStrategy   -- first to arrive wins (input order)

------------------------------------------------------------------------
-- 2. A homogeneous Merger: all D-ins share the same type A.
--
-- This is the simplest case. The Merger has D-in = List A (the
-- bundle of available inputs) and D-out = A (the chosen one).
-- State carries the strategy-specific memory.
------------------------------------------------------------------------

record HomogeneousMergerType (A : Set) : Set₁ where
  field
    n-inputs       : ℕ           -- number of input streams
    strategy-state : Set         -- e.g., ℕ for round-robin counter

homogeneous-merger-type : ∀ {A} → HomogeneousMergerType A → BrickType
homogeneous-merger-type {A} M = record
  { D-in  = List A
  ; D-out = A
  ; S-in  = HomogeneousMergerType.strategy-state M
  ; S-out = HomogeneousMergerType.strategy-state M
  }

------------------------------------------------------------------------
-- 3. Concrete merger: round-robin.
--
-- State = ℕ (the next-index counter, modulo n-inputs).
-- Strategy: at step k, pick input k mod n.
------------------------------------------------------------------------

-- List-indexing (with a default for out-of-bounds, since List doesn't
-- have a total indexing operation built in).
nth : ∀ {A : Set} → A → List A → ℕ → A
nth def [] _ = def
nth def (x ∷ _)  zero    = x
nth def (_ ∷ xs) (suc n) = nth def xs n

round-robin-merger
  : ∀ {A : Set}
  → A                  -- default value (for empty input)
  → ℕ                  -- n-inputs (a runtime parameter)
  → Brick (record
      { D-in  = List A
      ; D-out = A
      ; S-in  = ℕ
      ; S-out = ℕ
      })
round-robin-merger {A} def n = record
  { witnesses = C⇒D  -- the compute (strategy) selects which data wins
  ; step      = λ (inputs , counter) →
                  nth def inputs counter , (suc counter)
                  -- (no modulo here for simplicity; real impl wraps)
  ; homomorphism-tag = MergeStrategy
  }

------------------------------------------------------------------------
-- 4. Heterogeneous Merger: inputs have different types.
--
-- A more general merger takes a tuple of distinct-typed inputs and
-- picks one. The output type is a sum (disjoint union) of the inputs.
-- Strategy selects which sum variant to admit.
--
-- For the codec, this is e.g., I/P/Patch/B frames: each has its own
-- input type; the chooser picks one frame type per window.
--
-- Modeled here as a binary Merger (2 inputs) for clarity. The general
-- N-ary case generalises by induction on N.
------------------------------------------------------------------------

data Either (A B : Set) : Set where
  inj-left  : A → Either A B
  inj-right : B → Either A B

record BinaryMerger (A B : Set) : Set where
  field
    strategy   : MergeStrategy
    -- Selector decides which input to admit, based on both inputs +
    -- the strategy's state. We model state-less selection for the
    -- minimal case; stateful variants extend this with S-in/S-out.
    select     : A × B → Either A B

binary-merger-type : (A B : Set) → BrickType
binary-merger-type A B = record
  { D-in  = A × B
  ; D-out = Either A B
  ; S-in  = ⊤
  ; S-out = ⊤
  }

binary-merger : ∀ {A B} → BinaryMerger A B → Brick (binary-merger-type A B)
binary-merger {A} {B} m = record
  { witnesses = C⇒D  -- strategy (C) selects which D admits
  ; step      = λ ((a , b) , _) → BinaryMerger.select m (a , b) , tt
  ; homomorphism-tag = MergeStrategy
  }

------------------------------------------------------------------------
-- 5. Merger as the C⇒D witnessing.
--
-- The Merger fills the remaining witnessing-tag we hadn't shown a
-- concrete example for: C⇒D, "compute produces data witnessed by
-- state."
--
-- The compute here is the strategy. The state is the strategy's
-- memory (counter, queue, ...). The data being produced is the
-- chosen input. Without the state, the strategy would have nothing
-- to remember between selections; without the compute (strategy),
-- the data couldn't be ordered/disambiguated; without the data
-- (multiple inputs), there'd be nothing to merge.
--
-- This completes the six-axis catalog of witnessings:
--
--   D⇒S  (write):    predictor_update                  [Examples.agda]
--   S⇒D  (read):     predictor_surprise                [Examples.agda]
--   D⇒C  (chooser):  choose_rotation                   [Examples.agda]
--   C⇒D  (merger):   round-robin-merger                [this module]
--   S⇒C  (dispatch): range_encode_renorm sketch        [Examples.agda]
--   C⇒S  (param mu): arithmetic-coder bit-write sketch [Examples.agda]
------------------------------------------------------------------------
