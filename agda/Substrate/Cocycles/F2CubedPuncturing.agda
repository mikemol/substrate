------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing
--
-- The CY-4 F_2³ puncturing gauge cocycle (catalog M22-bis) as an
-- `IsomorphicCocycleStructure` instance.
--
-- Layer        : the 8 puncturings of RM(1, 3)
-- Base         : 8 coordinate puncturings as an F_2³ torsor
-- Gauge group  : F_2³ — translation (3-bit XOR on puncture index)
-- Classes      : a single orbit — the WHT core shared by all 8
--                puncturings (trivial cohomology)
-- Invariant    : the WHT core (a singleton type, since one orbit)
--
-- Second strong-discipline instance after CY-5. The key contrast:
--
--   * CY-5: V_4 acts on its 6 V_4-torsor fibers; non-trivial cohomology.
--   * CY-4: F_2³ acts on a SINGLE F_2³-torsor fiber; trivial cohomology.
--
-- Both fit IsomorphicCocycleStructure because the gauge acts freely
-- transitively on each fiber. CY-4 is the simplest case: the gauge
-- acts on itself by translation (regular representation), so the
-- torsor structure is the group's own. This is the cleanest test
-- that the abstraction handles trivial-cohomology (single orbit)
-- cases without degeneration.
--
-- See: catalog/cocycles.md § CY-4 — F_2³ puncturing gauge cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing where

open import Substrate.Foundation.Product using (_,_; ∃; -,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong-trans; sym-trans)

open import Substrate.Groups.F2Cubed
  using (F₂³; _+_; -_; ε; F₂³-Group;
         +-assoc; +-identityˡ; +-identityʳ; +-self)
open import Substrate.Cocycle
  using (IsomorphicCocycleStructure; Action; IsTorsor)
open import Substrate.Algebra.Group.ToSetoid using (to-setoid)

F₂³-Group-Setoid = to-setoid F₂³-Group

------------------------------------------------------------------------
-- The invariant: the WHT core, the architecturally-meaningful
-- structure shared by all 8 puncturings.
--
-- Singleton type — one inhabitant — since CY-4 has a single orbit.
-- Naming it `WHTCore` rather than ⊤ keeps the catalog's semantic
-- vocabulary visible at the type level.
------------------------------------------------------------------------

data WHTCore : Set where
  wht-core : WHTCore

------------------------------------------------------------------------
-- Puncturing index space: the 8 coordinate puncturings of RM(1, 3).
--
-- Identified with F_2³ via the bit-pattern of the punctured coordinate.
-- This is a type-level distinction from F_2³-as-group: F_2³ here is
-- the underlying SET (the 8 puncturings); the F_2³ in F₂³-Group is the
-- gauge GROUP. They share carriers because the gauge acts on itself
-- by translation (regular representation).
------------------------------------------------------------------------

PunctureIndex : Set
PunctureIndex = F₂³

------------------------------------------------------------------------
-- The fiber over the unique invariant.
--
-- For CY-4 the orbit-decomposition is trivial (1 orbit), so the fiber
-- over `wht-core` is the entire PunctureIndex space.
------------------------------------------------------------------------

Fiber : WHTCore → Set
Fiber wht-core = PunctureIndex

------------------------------------------------------------------------
-- The action: F_2³ acts on PunctureIndex by translation (XOR).
------------------------------------------------------------------------

puncturing-act : F₂³ → PunctureIndex → PunctureIndex
puncturing-act g p = g + p

puncturing-act-id : (p : PunctureIndex) → puncturing-act ε p ≡ p
puncturing-act-id = +-identityˡ

puncturing-act-∙ :
  (g h : F₂³) (p : PunctureIndex) →
  puncturing-act (g + h) p ≡ puncturing-act g (puncturing-act h p)
puncturing-act-∙ = +-assoc

puncturing-action : Action F₂³ _≡_ F₂³-Group-Setoid PunctureIndex
puncturing-action = record
  { act    = puncturing-act
  ; act-id = puncturing-act-id
  ; act-∙  = puncturing-act-∙
  }

------------------------------------------------------------------------
-- Torsor structure: F_2³ acts freely transitively on PunctureIndex.
--
-- Free: g + t ≡ t  ⇒  g ≡ ε.
--   Argument: from g + t ≡ t, add t to the right.
--   (g + t) + t ≡ t + t
--   g + (t + t) ≡ t + t       (assoc)
--   g + ε ≡ ε                  (+-self on each side)
--   g ≡ ε                      (right identity)
--
-- Transitive: for any t₁, t₂, witness g = t₂ + t₁.
--   (t₂ + t₁) + t₁ ≡ t₂ + (t₁ + t₁) ≡ t₂ + ε ≡ t₂.
------------------------------------------------------------------------

puncturing-free :
  (g : F₂³) (t : PunctureIndex) → g + t ≡ t → g ≡ ε
puncturing-free g t eq =
  sym-trans (+-identityʳ g)
   (cong-trans (g +_) (sym (+-self t))
    (sym-trans (+-assoc g t t)
     (cong-trans (_+ t) eq (+-self t))))

puncturing-transitive :
  (t₁ t₂ : PunctureIndex) → ∃ λ g → puncturing-act g t₁ ≡ t₂
puncturing-transitive t₁ t₂ = (t₂ + t₁) , proof
  where
    proof : (t₂ + t₁) + t₁ ≡ t₂
    proof = trans (+-assoc t₂ t₁ t₁)
            (cong-trans (t₂ +_) (+-self t₁)
                   (+-identityʳ t₂))

fiber-is-torsor : (i : WHTCore) → IsTorsor F₂³ _≡_ F₂³-Group-Setoid (Fiber i)
fiber-is-torsor wht-core = record
  { action     = puncturing-action
  ; free       = puncturing-free
  ; transitive = puncturing-transitive
  }

------------------------------------------------------------------------
-- IsomorphicCocycleStructure packaging.
------------------------------------------------------------------------

F2³-Puncturing-Cocycle : IsomorphicCocycleStructure
F2³-Puncturing-Cocycle = record
  { Invariant    = WHTCore
  ; GaugeCarrier = F₂³
  ; GaugeRel     = _≡_
  ; Gauge        = F₂³-Group-Setoid
  ; Fiber        = Fiber
  ; fiber-torsor = fiber-is-torsor
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
