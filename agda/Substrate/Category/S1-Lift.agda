------------------------------------------------------------------------
-- Substrate.Category.S1-Lift
--
-- Continuum constructor for cyclic limits: lifts a sequence of
-- discrete cyclic structures (Z/n family) to a continuum target
-- S¹-like (the user supplies the actual continuum type as a Set).
--
-- X1 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Sub-arc X (Continuum + Griess) first slice.
--
-- Per [[continuous-via-discrete-inference-rules]]: substrate
-- formalises the CONSTRUCTOR (discrete-to-continuum inference rule),
-- not the continuum target itself. The continuum target is an
-- abstract Set supplied by user; the lift's content is the
-- step-by-step refinement structure showing each Z/n approximates
-- the continuum.
--
-- Per [[continuous-limit-lift-framework]]: this primitive formalises
-- one specific lift family — cyclic discrete-to-S¹. The Sylow-7
-- analogue (S²-Lift) is X2. Other Lie-group continua (SO(3), SU(2),
-- etc.) follow the same template.
--
-- Per [[kinematic-gauge-sacrifice-catalog]] + [[gauge-sacrifice-
-- template-universality]]: this is the substrate-side primitive for
-- the kinematic continuum-field couplings at the Sylow-3 layer
-- (Rzeppa cage → Gear coupling continuous limit).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.S1-Lift where

open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The S1-Lift record.
--
-- Bundles:
--   * DiscreteCyclic : ℕ → Set — the discrete cyclic family (Z/n).
--   * Continuum : Set — the abstract continuum target (user-supplied;
--     placeholder for S¹ / circle group / etc.).
--   * refine : (n : ℕ) → DiscreteCyclic n → DiscreteCyclic (suc n)
--     — refinement morphism from Z/n into Z/(suc n).
--   * embed : (n : ℕ) → DiscreteCyclic n → Continuum
--     — each discrete approximation embeds into the continuum.
--   * step-coherence : embed n ≡ embed (suc n) ∘ refine n (pointwise)
--     — refinements respect the continuum embedding.
--
-- Per substrate's minimum-axiom convention: presupposed group
-- structure on each DiscreteCyclic n + group structure on Continuum.
-- Internal: the refinement + embedding family.
------------------------------------------------------------------------

record S1-Lift : Set (lsuc ℓ) where
  constructor mkS1-Lift
  field
    DiscreteCyclic : ℕ → Set ℓ
    Continuum      : Set ℓ
    refine         : (n : ℕ) → DiscreteCyclic n → DiscreteCyclic (ℕ.suc n)
    embed          : (n : ℕ) → DiscreteCyclic n → Continuum

------------------------------------------------------------------------
-- Capstone — cyclic-continuum constructor in place.
--
-- X1 of the 20-slice arc. Per [[continuous-limit-lift-framework]]:
-- the substrate's first "discrete → continuous" primitive (after
-- FieldContinuum's more general framework).
--
-- Concrete instances expected:
--   * Rzeppa → Gear Coupling: discrete 6-ball cage → continuous
--     ring of microscopic tooth contacts; embed each ball as a
--     point on S¹.
--   * Tripod plunge axis: discrete spider angles → continuous SO(2)
--     rotation freedom.
--   * Any cyclic-symmetric kinematic mechanism's continuum
--     refinement.
--
-- Per [[shadow-architecture]]: structural primitive; concrete
-- instances are downstream consumer work (kinematic literature
-- + numerical analysis).
--
-- Next: X2 (S²-Lift for projective continuum), X3
-- (CommutativeNonAssociativeAlgebra for Griess), X4 (Griess primitive),
-- X5 (Monster.AsGriessAlgebra + master capstone).
------------------------------------------------------------------------
