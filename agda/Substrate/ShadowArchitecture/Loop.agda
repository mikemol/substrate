------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Loop
--
-- Slice 5 of the shadow-architecture arc (Shadow G). The five-step
-- architectural loop from Increment 5, with the six warning signs
-- W1..W6 attached to their characteristic steps and mapped to the
-- specific charter gate each warning's failure compromises (Increment
-- 8's diagnostic kit).
--
-- Steps:
--   A. Classify      ⚠ W1 (over-classification)
--   B. Externalise   ⚠ W2 (speculative registration)
--   C. Fire probes   (no characteristic warning)
--   D. Act on events ⚠ W3, W4, W5 by sub-case
--   E. Loop          (no step-specific warning; W6 is at the
--                     interface level above the loop)
--
-- Warning → gate-broken (from Increment 8):
--   W1 over-classification         → observability
--   W2 speculative registration    → observability
--   W3 forced snap                  → alignment-with-request (5th gate)
--   W4 guard omission               → coverability
--   W5 L₇ deletion-reconciliation  → constructibility-across-time
--   W6 mode-fission                 → reachability
--
-- The L₆-routing fact (Increment 4 trigger #3: an unmediated 001 is
-- redirected to 110 via L₆ specifically because the Steiner property
-- forces the line) is recorded as a structural lemma. The two
-- points 001 and 110 are co-incident on exactly one Fano line, and
-- that line is L₆; L₆'s normal is 110; hence the redirect target.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Loop where

open import Substrate.Foundation.List using (List; []; _∷_; foldl; foldr)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.Duality using (normal-vector)
open import Substrate.ShadowArchitecture.SelfReference
  using (_on_; L₆-normal-is-110)
open import Substrate.ShadowArchitecture.Mode
  using (001-on-L₆)

------------------------------------------------------------------------
-- 1. The five loop steps.
------------------------------------------------------------------------

data Step : Set where      -- ⟦shape:cd0b14ad Step-A,Step-B,Step-C⟧
  Step-A : Step  -- Classify
  Step-B : Step  -- Externalise
  Step-C : Step  -- Fire probes
  Step-D : Step  -- Act on events
  Step-E : Step  -- Loop

------------------------------------------------------------------------
-- 2. The six warning signs.
------------------------------------------------------------------------

data Warning : Set where
  W1 : Warning  -- over-classification
  W2 : Warning  -- speculative registration
  W3 : Warning  -- forced snap
  W4 : Warning  -- guard omission
  W5 : Warning  -- L₇ deletion-reconciliation
  W6 : Warning  -- mode-fission

------------------------------------------------------------------------
-- 3. The five charter gates (the four canonical + the alignment
-- meta-gate from Increment 8).
------------------------------------------------------------------------

data Gate : Set where
  G-constructible           : Gate
  G-reachable               : Gate
  G-observable              : Gate
  G-coverable               : Gate
  G-alignment-with-request  : Gate

------------------------------------------------------------------------
-- 4. Warning → gate-broken mapping (Increment 8's table).
--
-- W5 is "constructibility-across-time": we use G-constructible (the
-- temporal extension is in Slice 6, `Persistence`).
------------------------------------------------------------------------

warning-gate : Warning → Gate
warning-gate W1 = G-observable
warning-gate W2 = G-observable
warning-gate W3 = G-alignment-with-request
warning-gate W4 = G-coverable
warning-gate W5 = G-constructible
warning-gate W6 = G-reachable

------------------------------------------------------------------------
-- 5. Step → warnings mapping.
--
-- W6 (mode-fission) is at the INTERFACE level above the loop, not
-- attached to any step — re-instantiating the four modes as separate
-- skills breaks cross-mode entailments at L₄/L₅, which lives above
-- the single-loop structure.
------------------------------------------------------------------------

step-warnings : Step → List Warning
step-warnings Step-A = W1 ∷ []
step-warnings Step-B = W2 ∷ []
step-warnings Step-C = []
step-warnings Step-D = W3 ∷ W4 ∷ W5 ∷ []
step-warnings Step-E = []

interface-warnings : List Warning
interface-warnings = W6 ∷ []

------------------------------------------------------------------------
-- 6. L₆-routing fact (Increment 4, trigger #3).
--
-- The redirect target of an unmediated 001 is 110 specifically
-- because: (a) both 001 and 110 lie on L₆; (b) L₆'s normal IS 110
-- (the ★ self-reference); (c) the Steiner property guarantees a
-- unique line through any two distinct points. Together: there is
-- exactly one Fano line through both 001 and 110, that line is L₆,
-- and L₆'s normal-vector is 110.
--
-- These three facts each close mechanically.
------------------------------------------------------------------------

-- 001 ∈ L₆ comes from `Substrate.ShadowArchitecture.Mode` (re-exported
-- here as the Loop-level fact). The companion fact 110 ∈ L₆ is recorded
-- locally; the third (L₆'s normal IS 110) is `L₆-normal-is-110` from
-- `Substrate.ShadowArchitecture.SelfReference`.

110-on-L₆ : p₁₁₀ on L₆
110-on-L₆ = inj₂ (inj₁ refl)

L₆-normal-is-target : normal-vector L₆ ≡ p₁₁₀
L₆-normal-is-target = L₆-normal-is-110

-- Re-export 001-on-L₆ at the Loop level for callers who reach for
-- the L₆-routing fact via the Loop module.
loop-001-on-L₆ : p₀₀₁ on L₆
loop-001-on-L₆ = 001-on-L₆
