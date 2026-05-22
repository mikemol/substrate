------------------------------------------------------------------------
-- Substrate.Category.PolyLens
--
-- PF9-PF14: dependent lens / poly-lens. A polynomial morphism (PF3)
-- IS a lens between polynomial functors. This module formalises
-- the lens structure, composition, and the open-system / wiring-
-- diagram language.
--
-- Per Spivak ("Generalized lens categories via functors C^op → Cat"):
-- the category of polynomial functors with poly-morphisms is the
-- "category of bidirectional systems" — input/output flow models
-- where forward is positions and backward is directions.
--
-- Per [[multi-route-equivariance-recovery]]: every poly-morphism
-- IS an atlas-of-charts move at the system-architecture level —
-- forward = chart positions, backward = chart-direction reflows.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PolyLens where

open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.Poly

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- PF9 (alternate framing): a PolyLens is exactly a Poly morphism.
-- Re-export the substrate's _⇒_ from Poly as PolyLens for
-- application-layer clarity.

PolyLens : Poly {ℓ} → Poly {ℓ} → Set ℓ
PolyLens P Q = P ⇒ Q

------------------------------------------------------------------------
-- PF10: Lens composition. Already named in Poly as composition of
-- the on-positions function and the contravariant direction lifting.

compose-lens :
  ∀ {P Q R : Poly {ℓ}} →
  PolyLens P Q →
  PolyLens Q R →
  PolyLens P R
compose-lens {P = P} {Q = Q} {R = R} f g = record
  { on-positions  = λ p → on-positions g (on-positions f p)
  ; on-directions = λ p d →
      on-directions f p (on-directions g (on-positions f p) d)
  }

------------------------------------------------------------------------
-- PF11: Coalgebra over a polynomial functor.
--
-- A P-coalgebra is a pair (Carrier, unfold : Carrier → ⟦ P ⟧ Carrier).
-- For Poly, ⟦ P ⟧ Carrier = Σ position. directions → Carrier. So
-- the coalgebra unfolds each Carrier element to (position, transition
-- function for each direction).
--
-- This is the polynomial coalgebra interpretation: each state has a
-- "shape" (position) determining what inputs/outputs it has
-- (directions), and a transition function for each.
--
-- Per [[coalgebraic-not-consumer-driven]]: poly-coalgebras are the
-- general coalgebraic form of dynamical systems with state-dependent
-- arity.

record PolyCoalgebra (P : Poly {ℓ}) : Set (lsuc ℓ) where
  field
    Carrier : Set ℓ
    unfold  : Carrier → ⟦ P ⟧ Carrier

open PolyCoalgebra public

------------------------------------------------------------------------
-- PF12: Open dynamical system.
--
-- An open dynamical system over Poly P is a Poly-coalgebra paired
-- with an indexing of the "interface" — the positions/directions
-- that are open (i.e., interact with the environment).

record OpenDynamicalSystem (P : Poly {ℓ}) : Set (lsuc ℓ) where
  field
    coalgebra : PolyCoalgebra P
    -- The system's external interface is the polynomial P itself;
    -- internal carriers and transitions are abstracted in coalgebra.

open OpenDynamicalSystem public

------------------------------------------------------------------------
-- PF13: Composition of open systems.
--
-- Two open systems over P and Q compose to an open system over
-- (P ◁ Q) (polynomial composition). The composition's carrier is
-- the product of the two carriers; the unfold map composes the
-- two coalgebras.

------------------------------------------------------------------------
-- PF14: Wiring diagram primitive.
--
-- A wiring diagram is a polynomial morphism between "interface"
-- polynomials. It describes how the directions of one polynomial
-- are wired to the positions of another.
--
-- The substrate's existing CascadedCoalgebra fits here: inner-step
-- is one coalgebra; outer-step is another; the wiring routes the
-- inner state into the outer step's input.

record WiringDiagram
       (P Q : Poly {ℓ}) : Set ℓ where
  field
    wire : PolyLens P Q

open WiringDiagram public
