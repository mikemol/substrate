{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.NuWholeBisim — ⟡nu-whole-bisim: the WHOLE-ν
-- (the coinductive shape-stream of the ν coalgebra) is UNIQUE UP TO BISIMULATION (~),
-- via ana-unique — the THIRD uniqueness layer, coinductive, distinct from the two ≡
-- layers (μ ≡-unconditional, 185; ν step ≡-bounded, 186).
--
-- GROUNDED (surfacing, per the audited scope-claim — which held this time): NuShapeIso
-- (161) already has shape-is-canonical co = ana-unique (quotient-coalg co) : ANY h
-- agreeing with the ν coalgebra's head/tail is ~ to the shape-stream. Instantiating it
-- at the CONCRETE ℕ-coalg (184, the registered ν's coalgebra) gives the whole-ν bisim
-- uniqueness for the REGISTERED ν. The whole-ν is a DIFFERENT object from nu-backed (the
-- step solver, 186): the step is one wedge (≡-bounded); the whole is the coinductive CF
-- stream (~-unique). So μ ⊣ ν uniqueness is: μ ≡-unconditional (fold) ⊣ ν-step ≡-bounded
-- (wedge) ⊣ ν-whole ~-bisim (stream) — three layers, two frames (≡ and ~).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.NuWholeBisim where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; proj₁; proj₂)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana)
open import Substrate.Algebra.R.Trace.Bisim using (_~_)
open import Substrate.Algebra.Wedge.NuShapeIso using (QState; quotient-coalg; shape-stream; shape-is-canonical)
open import Substrate.Category.UniversalProperty.NuRegistryEntry using (ℕ-coalg)

------------------------------------------------------------------------
-- ① THE WHOLE-ν STREAM of the registered ℕ-coalg: the shape-stream (CF digit stream) =
-- the ana of the ℕ-div quotient-coalgebra. This is the ν coalgebra's WHOLE unfold.
------------------------------------------------------------------------
ν-whole : QState → RealTrace
ν-whole = shape-stream ℕ-coalg

------------------------------------------------------------------------
-- ② THE WHOLE-ν IS UNIQUE UP TO BISIM (~): any h agreeing with the ℕ-coalg quotient-
-- coalgebra's head (the CF digit = quot) and tail (the residual's stream) is ~ to ν-whole.
-- This is shape-is-canonical (= ana-unique) at the CONCRETE registered ℕ-coalg — the
-- terminal-coalgebra universal property, the ~-frame uniqueness of the whole unfold.
------------------------------------------------------------------------
ν-whole-unique :
  (h : QState → RealTrace)
  → (∀ s → head (h s) ≡ proj₁ (quotient-coalg ℕ-coalg s))
  → (∀ s → tail (h s) ≡ h (proj₂ (quotient-coalg ℕ-coalg s)))
  → ∀ s → h s ~ ν-whole s
ν-whole-unique = shape-is-canonical ℕ-coalg

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the μ⊣ν uniqueness picture COMPLETE, three layers, two
-- frames): the whole-ν (the coinductive shape-stream of the registered ℕ-coalg) is UNIQUE
-- UP TO BISIMULATION (~) — ν-whole-unique = shape-is-canonical ℕ-coalg = ana-unique at the
-- concrete coalgebra. This is the terminal-coalgebra universal property (~-frame), the
-- coinductive DUAL of the initial-algebra fold uniqueness (μ, ≡-frame). So the full μ ⊣ ν
-- uniqueness picture is now THREE layers:
--   μ  (fold, initial algebra)     : ≡-uniqueness, UNCONDITIONAL (Adm = ⊤)   — 185
--   ν-step (wedge, one unfold)     : ≡-uniqueness, BOUNDED (Adm = r < b)     — 186
--   ν-whole (stream, coinductive)  : ~-uniqueness (bisim), via ana-unique    — 187 (here)
-- The either/or "≡-uniqueness vs bisim-uniqueness" dissolves into the LEVEL: the finite/
-- halting reading (μ fold, ν step) is ≡ (inductive), the unbounded/non-halting reading
-- (ν whole stream) is ~ (coinductive) — ONE universal property (Lawvere's fixed-point) read
-- at two levels, as Final.agda's own comment says ("bounded/halting: ≡; unbounded/non-
-- halting: ana-unique"). The whole-ν bisim was NOT nu-backed's step uniqueness (186's
-- correction) — it is THIS, a different object, and it IS in the substrate (NuShapeIso),
-- surfaced here at the registered ℕ-coalg. The μ⊣ν uniqueness picture is COMPLETE.
------------------------------------------------------------------------
