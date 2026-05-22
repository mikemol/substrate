------------------------------------------------------------------------
-- Substrate.Pipeline.Examples
--
-- Concrete bricks from the eliza codec, modeled as instances of the
-- Brick framework. Each example shows the three-axis schema (D, S, C)
-- and the witnessing it instantiates.
--
-- These are minimal type-theoretic skeletons; the runtime
-- implementations live in scratch/eliza/eliza/.
------------------------------------------------------------------------

-- Postulates stand in for runtime types (Char, Counts, Window, ...).
-- These are concrete in the Python runtime; here we use postulates as
-- placeholders, so this module cannot be --safe.
{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Pipeline.Brick

------------------------------------------------------------------------
-- Example 1: A pure transform — V₄-rotation of a crumb.
--
-- D-in  = Crumb × V4Label
-- D-out = Crumb
-- S     = ⊤ (no state)
-- C     = XOR (lookup in the V₄ group action table)
-- Witnessing: D⇒S in the trivial sense (S = ⊤);
--             the brick is essentially a typed function.
-- Homomorphism: preserves V₄ group structure.
------------------------------------------------------------------------

-- Atomic types.
data Crumb : Set where
  c₀ c₁ c₂ c₃ : Crumb

data V4Label : Set where
  e α β γ : V4Label

-- The V₄ XOR action (Klein four group).
v4-xor : Crumb → V4Label → Crumb
v4-xor c₀ e = c₀ ; v4-xor c₁ e = c₁ ; v4-xor c₂ e = c₂ ; v4-xor c₃ e = c₃
v4-xor c₀ α = c₁ ; v4-xor c₁ α = c₀ ; v4-xor c₂ α = c₃ ; v4-xor c₃ α = c₂
v4-xor c₀ β = c₂ ; v4-xor c₁ β = c₃ ; v4-xor c₂ β = c₀ ; v4-xor c₃ β = c₁
v4-xor c₀ γ = c₃ ; v4-xor c₁ γ = c₂ ; v4-xor c₂ γ = c₁ ; v4-xor c₃ γ = c₀

-- The brick type.
RotateCrumb-Type : BrickType
RotateCrumb-Type = record
  { D-in  = Crumb × V4Label
  ; D-out = Crumb
  ; S-in  = ⊤
  ; S-out = ⊤
  }

-- A name for the homomorphism this preserves: the V₄ group structure.
record Preserves-V4 : Set where

-- The brick.
rotate-crumb : Brick RotateCrumb-Type
rotate-crumb = record
  { witnesses = D⇒S  -- trivial (S = ⊤); the brick is a pure transform
  ; step      = λ ((c , g) , _) → v4-xor c g , tt
  ; homomorphism-tag = Preserves-V4
  }

------------------------------------------------------------------------
-- Example 2: A state update — predictor.update (Trigram).
--
-- D-in  = Char (the symbol being observed)
-- D-out = ⊤ (write-only; no immediate output data)
-- S-in  = Counts (the predictor's count table)
-- S-out = Counts (updated)
-- C     = increment the bin for the current context
-- Witnessing: D⇒S — the char becomes part of the counts via update.
-- Homomorphism: counts form a free commutative monoid; update is
-- monoid concatenation by a singleton.
------------------------------------------------------------------------

postulate
  Char   : Set
  Counts : Set
  update-counts : Counts → Char → Counts

PredictorUpdate-Type : BrickType
PredictorUpdate-Type = record
  { D-in  = Char
  ; D-out = ⊤
  ; S-in  = Counts
  ; S-out = Counts
  }

record Preserves-CountMonoid : Set where

predictor-update : Brick PredictorUpdate-Type
predictor-update = record
  { witnesses = D⇒S
  ; step      = λ (ch , s) → tt , update-counts s ch
  ; homomorphism-tag = Preserves-CountMonoid
  }

------------------------------------------------------------------------
-- Example 3: A state query — predictor.surprise (read-only).
--
-- D-in  = Char (the symbol whose surprise we want)
-- D-out = ℕ (surprise in bits, simplified to ℕ here)
-- S-in  = Counts
-- S-out = Counts (unchanged; this is read-only)
-- C     = -log₂ P(ch | context) under Laplace smoothing
-- Witnessing: S⇒D — counts produce a surprise value.
-- Homomorphism: Shannon information is concave; preserves the
-- monoid structure modulo log.
------------------------------------------------------------------------

postulate
  surprise-bits : Counts → Char → ℕ

PredictorSurprise-Type : BrickType
PredictorSurprise-Type = record
  { D-in  = Char
  ; D-out = ℕ
  ; S-in  = Counts
  ; S-out = Counts
  }

record Preserves-Shannon : Set where

predictor-surprise : Brick PredictorSurprise-Type
predictor-surprise = record
  { witnesses = S⇒D
  ; step      = λ (ch , s) → surprise-bits s ch , s  -- s unchanged
  ; homomorphism-tag = Preserves-Shannon
  }

------------------------------------------------------------------------
-- Example 4: A chooser — selects which rotation to apply.
--
-- D-in  = Window (a chunk of input bytes)
-- D-out = RotIdx (the chosen rotation, ∈ [0,16))
-- S-in  = Predictor × Cache (the canonical predictor + memoisation)
-- S-out = Predictor × Cache' (cache may grow)
-- C     = score 16 rotations against predictor; argmin; cache
-- Witnessing: D⇒C — the window selects the compute (rotation),
--             witnessed by S (the cache records the choice).
-- Homomorphism: monotone in predictor confidence — better predictor
-- = sharper choice. (No simple algebraic structure; preserves
-- selection ranking under predictor evolution.)
------------------------------------------------------------------------

postulate
  Window    : Set
  RotIdx    : Set
  Predictor : Set
  Cache     : Set
  choose-rotation-impl
    : Window → Predictor × Cache → RotIdx × (Predictor × Cache)

Chooser-Type : BrickType
Chooser-Type = record
  { D-in  = Window
  ; D-out = RotIdx
  ; S-in  = Predictor × Cache
  ; S-out = Predictor × Cache
  }

record Preserves-Ranking : Set where

choose-rotation : Brick Chooser-Type
choose-rotation = record
  { witnesses = D⇒C  -- the data (window) selects the compute (rotation)
                     -- — witness is S (cache)
  ; step      = λ (w , s) → choose-rotation-impl w s
  ; homomorphism-tag = Preserves-Ranking
  }

------------------------------------------------------------------------
-- These four examples cover the four main witnessing types:
--   * D⇒S trivial (pure transform)        — rotate-crumb
--   * D⇒S non-trivial (state update)      — predictor-update
--   * S⇒D (state query)                   — predictor-surprise
--   * D⇒C (compute selection)             — choose-rotation
--
-- The remaining two witnessings (S⇒C, C⇒S, C⇒D) decompose similarly:
--   * S⇒C: range_encode_renorm dispatches based on RCState's window.
--   * C⇒S: arithmetic-coder step writes bits to state.
--   * C⇒D: sequitur.top_rule projects state to the current top rule.
--
-- The brick framework's correctness obligation is composition: see
-- Substrate.Pipeline.Composition. A pipeline of these bricks is
-- well-typed by construction; the substrate's Beck-Chevalley square
-- closes when adjacent bricks' (D, S) edges align via refl.
------------------------------------------------------------------------
