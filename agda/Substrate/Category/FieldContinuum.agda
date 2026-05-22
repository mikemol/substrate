------------------------------------------------------------------------
-- Substrate.Category.FieldContinuum
--
-- The 5th gauge class primitive — Continuum Field Couplings. Joins
-- FieldBond, FieldTower, FieldFanOut in the substrate's categorical
-- primitive ladder for multi-field gauge architecture.
--
-- Per [[gauge-sacrifice-template-universality]] +
-- [[continuous-limit-lift-framework]]: the catalog of mechanical
-- gauge mechanisms ([[kinematic-gauge-sacrifice-catalog]]) has four
-- rigid-body classes (Sylow-2, Sylow-3, Sylow-7, Null) at the
-- discrete level, plus a 5th class (Continuum Field Couplings:
-- Fluidic, Magnetic, Photonic) where the rigid-body assumption is
-- abandoned and the discrete Sylow framework dissolves into a smooth
-- Lie-group continuum.
--
-- This module names that 5th class structurally.
--
-- Per [[continuous-via-discrete-inference-rules]]: the substrate
-- does NOT formalize continuous content (SO(3) Lie group, smooth
-- principal bundles, Maxwell's stress tensor) as Agda objects. What
-- it formalizes is the CONSTRUCTOR: a record packaging a discrete
-- predecessor (a FieldFanOut at finite N) + a continuum-target type
-- (treated abstractly as a Set) + a continuum-bond morphism from
-- the discrete source to the continuum target.
--
-- The continuum target's specific structure (whether it's SO(3),
-- S¹, S², electromagnetic field, etc.) is the USER's domain choice;
-- this record provides only the categorical name and the discrete-
-- predecessor connection.
--
-- Per [[categorical-name-first]]: "Continuum field coupling" / "field
-- continuum" is the standard categorical naming for the 5th class.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FieldContinuum where

open import Substrate.Foundation.Level using (Level) renaming (suc to lsuc)

open import Substrate.Category.FieldFanOut using (FieldFanOut; FixedFanOut)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- 1. The FieldContinuum record.
--
-- Bundles:
--   * discrete-predecessor : a FieldFanOut at finite N (the discrete
--     skeletal approximation).
--   * Continuum : the continuum target type (no continuous content
--     formalized — the user supplies the type as an abstract Set;
--     might be SO(3), S¹, S², ℂP^n, an electromagnetic field, etc.).
--   * continuum-bond : a morphism from the discrete source to the
--     continuum target (the discrete-to-continuous "limit" inference).
--
-- The discrete predecessor's role is documentary: it identifies WHICH
-- discrete Sylow-classification layer the continuum extends from.
-- The continuum-bond is the per-instance constructor; concrete
-- continuum instances (Fluidic / Magnetic / Photonic) supply it.
------------------------------------------------------------------------

-- Per FieldFanOut generalization 2026-05-21: the discrete-predecessor
-- is a stationary (= constant-arity) FanOut, modelled here as
-- FixedFanOut. The continuum-limit lift takes a FixedFanOut to its
-- continuum target.

record FieldContinuum {n : _} (𝒹 : FixedFanOut {ℓ} n) : Set (lsuc ℓ) where
  open FieldFanOut 𝒹
  field
    Continuum      : Set ℓ
    continuum-bond : Source → Continuum

------------------------------------------------------------------------
-- 2. Capstone.
--
-- The 5th gauge class primitive in place. Examples of expected
-- downstream instances (per [[kinematic-gauge-sacrifice-catalog]]):
--
--   * Fluidic CV: discrete predecessor = a FieldFanOut at large N
--     over Z/n approximating an S¹ (= the velocity-field circle in
--     a Navier-Stokes torus); Continuum = an abstract S¹-like
--     placeholder; continuum-bond = N→∞ limit.
--
--   * Coaxial Magnetic: discrete predecessor = FieldFanOut over
--     N pole-pairs; Continuum = an SO(3)-like placeholder
--     (electromagnetic-field configuration space);
--     continuum-bond = the field-theoretic limit.
--
--   * Photonic / Optical: discrete predecessor = FieldFanOut over
--     N GRIN-lens stages; Continuum = a placeholder for the
--     refractive-index manifold; continuum-bond = optical-limit.
--
-- These specific instances are out of scope as substrate-side Agda
-- content (per [[continuous-via-discrete-inference-rules]]); they
-- live in domain-specific consumer modules.
--
-- Combined with FieldBond / FieldTower / FieldFanOut, the substrate
-- now exposes the FULL 4-tier multi-field architecture:
--
--   FieldBond     — single bond between two fields
--   FieldTower    — chain of fields connected in sequence
--   FieldFanOut   — one source projecting to multiple targets
--   FieldContinuum — discrete-to-continuum extension (THIS slice)
--
-- Per the 4+1 meta-pattern in [[gauge-sacrifice-template-
-- universality]]: FieldBond / Tower / FanOut are the 3 discrete
-- topologies; FieldContinuum is the +1 continuum class. The
-- 3+1 universal recurs at the categorical-primitive design level.
------------------------------------------------------------------------
