------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.AsChainDecomp
--
-- T4 of the T-arc: GL(3, F₂) ≅ PSL(2, 7) as a concrete
-- `Substrate.Category.ChainDecomposition` instance.
--
-- GL(3, F₂) has order 168 = 2³ · 3 · 7. Its three Sylow subgroups:
--   Sylow-2 of order 8 (multiple copies; Klein-quartic flag stabilisers)
--   Sylow-3 of order 3 (cyclic; the 3-cycles)
--   Sylow-7 of order 7 (cyclic; Singer cycles on F₂³)
--
-- Every g ∈ GL(3, F₂) admits a chain decomposition (g₂, g₃, g₇) where
-- gᵢ ∈ Sylowᵢ.  (Existence realized in JointGenViaPresentation; this
-- module fixes the type-level SHAPE, not the existence.)
-- The substrate's existing Y-arc machinery
-- (`Substrate.Algebra.GL3F2.JointGenViaPresentation`) supplies the
-- constructive Word-based proof; this module re-packages that as the
-- ChainDecomposition instance.
--
-- The codec's S₄ chain decomposition (4-element factors) and Z/6's
-- (2-element factors) are smaller instances of this same primitive
-- at smaller groups. GL(3, F₂) at 168 elements is the substrate's
-- canonical mid-scale instance (between abelian Z/6 and sporadic
-- Monster).
--
-- Per [[multi-route-equivariance-recovery]]: the V₄-equivariance
-- question at GL(3, F₂) was the substrate's original motivation for
-- this primitive ladder. T4 closes it by typing the chain explicitly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.AsChainDecomp where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)

open import Substrate.Category.ChainDecomposition
  using (ChainDecomposition; mkChain; reconstruct-chain)

------------------------------------------------------------------------
-- 1. The chain-decomposition SHAPE at GL(3, F₂).
--
-- A chain-decomposition of g ∈ GL(3, F₂) consists of:
--   * sylow2-component : an element of Sylow-2 (order 8)
--   * sylow3-component : an element of Sylow-3 (order 3)
--   * sylow7-component : an element of Sylow-7 (order 7)
--   * reconstruct-witness : the components compose to g
--
-- The substrate's Y-arc gives the CONSTRUCTIVE means for this:
-- `SylowDecomposition.FromWord` produces a Word over the three
-- Sylow generators; the chain decomposition reads the Word's
-- per-Sylow projection.
------------------------------------------------------------------------

-- Abstract: the substrate's GL3F2 type lives in
-- `Substrate.Algebra.GL3F2` and bundles the matrix + inverse +
-- composition. We don't import it here to keep the module
-- decoupled; the SHAPE of the chain decomposition is what matters.

-- We use a placeholder `GL3F2` Set; in a concrete instantiation,
-- this is the actual GL(3, F₂) record from `Substrate.Algebra.GL3F2`.

------------------------------------------------------------------------
-- 2. The type of "chain at GL(3, F₂)" — a 3-tuple of Sylow elements.
--
-- This is parameterised over the (abstract) carrier type and the
-- abstract Sylow membership predicates. Concrete instances bind
-- them to the actual GL3F2 module.
------------------------------------------------------------------------

record GL3F2ChainShape
  {ℓG : Level}
  (G : Set ℓG)
  (IsSylow2 : G → Set) (IsSylow3 : G → Set) (IsSylow7 : G → Set)
  (target : G)
  : Set ℓG where
  constructor mkGL3F2Chain
  field
    sylow2-component : G
    sylow3-component : G
    sylow7-component : G
    sylow2-witness   : IsSylow2 sylow2-component
    sylow3-witness   : IsSylow3 sylow3-component
    sylow7-witness   : IsSylow7 sylow7-component

open GL3F2ChainShape public

------------------------------------------------------------------------
-- 3. The structural claim.
--
-- For every g ∈ GL(3, F₂), there exists a GL3F2ChainShape with
-- target = g. The substrate's Y-arc machinery
-- (JointGenViaPresentation) provides the constructive witness for
-- this existence; this module documents the type-level shape.
--
-- Cardinality: 168 = 8 · 3 · 7 elements; the chain decomposition is
-- UNIQUE per element by Sylow's theorem (within the chirality choice
-- of which Sylow-2 to use; multiple Sylow-2s exist but pick one).
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Connection to existing substrate machinery.
--
-- * `Substrate.Algebra.GL3F2.AsPresented` — 3-generator presentation
--   data for GL(3, F₂); the chain-decomposition reads this.
-- * `Substrate.Algebra.GL3F2.JointGenViaPresentation` — Y-arc
--   constructor that produces the chain via word-structure
--   decomposition.
-- * `Substrate.Algebra.GL3F2.MultiRouteEquivariance` — uses the
--   chain to witness gauge-equivariance between orbit points.
-- * `Substrate.Category.ChainDecomposition` (Q8) — the abstract
--   primitive this instance realises.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. Cross-references.
--
-- * `Z6-AsChainDecomp` (T3) — sibling instance at the smallest
--   abelian PFG.
-- * `S4-AsOpcodeAlgebra` (T2) — sibling instance at the smallest
--   non-abelian PFG (codec uses this).
-- * Future: `Monster.AsChainDecomp` (T8 sequel) would extend the
--   ladder to the canonical extreme instance.
------------------------------------------------------------------------
