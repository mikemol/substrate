------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.F23PuncturingCocycle
--
-- Defines: F2³-Puncturing-Cocycle
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.F23PuncturingCocycle where

open import Substrate.Groups.F2Cubed
open import Substrate.Cocycle
open import Substrate.Algebra.Group.ToSetoid
open import Substrate.Foundation.Eq
open import Substrate.Cocycles.F2CubedPuncturing.F23GroupSetoid
open import Substrate.Cocycles.F2CubedPuncturing.WHTCore
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex
open import Substrate.Cocycles.F2CubedPuncturing.Fiber
open import Substrate.Cocycles.F2CubedPuncturing.FiberIsTorsor



------------------------------------------------------------------------
-- IsomorphicCocycleStructure packaging.
------------------------------------------------------------------------

-- ⟡set1-paydown: ICS carrier/family fields are now module params — moved into the type annotation.
F2³-Puncturing-Cocycle : IsomorphicCocycleStructure WHTCore F₂³ _≡_ F₂³-Group-Setoid Fiber
F2³-Puncturing-Cocycle = record
  { fiber-torsor = fiber-is-torsor
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. Total space: Σ WHTCore Fiber. Since WHTCore has a unique
--    inhabitant `wht-core`, the total space is isomorphic to the
--    fiber: PunctureIndex = F_2³. The "8 puncturings" enumeration is
--    therefore the 8 elements of F_2³.
--
-- 2. Trivial cohomology: with a single orbit, the cocycle's
--    cohomology classes form a one-element set. CY-4 thus serves as
--    the degenerate-but-non-trivial validation of the abstraction:
--    the type structure does NOT special-case single-orbit cocycles;
--    they instantiate the same ICS record as multi-orbit ones.
--
-- 3. Connection to RM(1, 3): the 8 puncturings of the [8, 4, 4]
--    Reed-Muller code RM(1, 3) form an F_2³-affine space. The WHT
--    core (the shared invariant) is the architectural symmetry
--    "S as gauge-invariant pivot" reading of catalog M23-bis. We
--    don't formalise RM(1, 3) itself here — the cocycle structure
--    captures the gauge-action portion of the catalog claim, which
--    is the structural commitment that survives extraction.
--
-- 4. Strong/weak split confirmed at three data points:
--    - CY-5 (V_4 signature): strong (ICS), 6 non-trivial orbits.
--    - CY-4 (F_2³ puncturing): strong (ICS), 1 trivial orbit.
--    - CY-2 (K-rule variable): weak (WCS), 2 orbits, non-free action.
--    The split tracks whether the gauge acts FREELY on each orbit,
--    not whether the cocycle has multiple orbits. CY-4 confirms
--    that strong discipline applies to trivial-cohomology cocycles
--    too — the criterion is the freeness of the action, not the
--    orbit count.
------------------------------------------------------------------------
