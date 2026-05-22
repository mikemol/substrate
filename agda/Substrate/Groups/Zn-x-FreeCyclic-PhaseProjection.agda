------------------------------------------------------------------------
-- Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
--
-- Parametric module for the phase projection from a 2-D word algebra
-- Zₙ × F (via Substrate.Groups.Coxeter.DirectProduct) back to Zₙ.
--
-- Consolidates the Z3-/Z4-/Z5-x-FreeCyclic-PhaseProjection per-n
-- boilerplate: `phase-project = proj₁` plus three pointwise refl
-- homomorphism lemmas. Each per-Zₙ instance becomes a one-line
-- application of this generic.
--
-- Models on Substrate.Groups.Coxeter-Fin-Generic / Zn-x-FreeCyclic's
-- parametric-over-Zₙ-data pattern.
--
-- Per [[expose-generator-not-orbit]]: the 4-line `phase-project +
-- 3-refl` chain repeated across Z₃/Z₄/Z₅ was an orbit; the generic
-- IS the chain, computed once from Zₙ + F carrier data.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

module Substrate.Groups.Zn-x-FreeCyclic-PhaseProjection
  -- The Zₙ carrier + raw ++ + normalize. The Coxeter Core's `_·_`
  -- is reconstructed below as `normalize ∘ ++`.
  (Zn-Word      : Set)
  (Zn-ε         : Zn-Word)
  (_Zn-++_      : Zn-Word → Zn-Word → Zn-Word)
  (Zn-normalize : Zn-Word → Zn-Word)
  -- The F (FreeCyclic, or any other Core-shaped) carrier.
  (F-Word       : Set)
  (F-ε          : F-Word)
  (_F-++_       : F-Word → F-Word → F-Word)
  (F-normalize  : F-Word → F-Word)
  where

------------------------------------------------------------------------
-- 1. The 2-D carrier + operations, matching what
-- Substrate.Groups.Coxeter.DirectProduct exposes via Core.
--
-- `_·_` = `normalize ∘ ++` per Core. `normalize` is pointwise per
-- DirectProduct. These definitions are definitionally equal to the
-- Z₃×F / Z₄×F / Z₅×F surfaces from Zn-x-FreeCyclic.
------------------------------------------------------------------------

Word : Set
Word = Zn-Word × F-Word

ε : Word
ε = (Zn-ε , F-ε)

_·_ : Word → Word → Word
(a₁ , a₂) · (b₁ , b₂) =
  ( Zn-normalize (a₁ Zn-++ b₁)
  , F-normalize  (a₂ F-++  b₂)
  )

normalize : Word → Word
normalize (w₁ , w₂) = (Zn-normalize w₁ , F-normalize w₂)

-- The Zₙ-side `_·_` matches Core: normalize ∘ ++.
_Zn-·_ : Zn-Word → Zn-Word → Zn-Word
a Zn-· b = Zn-normalize (a Zn-++ b)

------------------------------------------------------------------------
-- 2. The phase projection: `proj₁` on the underlying pair.
--
-- Per the 2-D word algebra arc: this is the operational realization
-- of "forget cycle, recover Zₙ." The kernel is the F component
-- (= the deck transformation group of the cover).
------------------------------------------------------------------------

phase-project : Word → Zn-Word
phase-project = proj₁

------------------------------------------------------------------------
-- 3. Coxeter Core homomorphism witnesses (all refl by pointwise
-- definition).
------------------------------------------------------------------------

phase-project-ε : phase-project ε ≡ Zn-ε
phase-project-ε = refl

phase-project-· :
  (a b : Word) →
  phase-project (a · b) ≡ phase-project a Zn-· phase-project b
phase-project-· (a₁ , a₂) (b₁ , b₂) = refl

phase-project-normalize :
  (w : Word) →
  phase-project (normalize w) ≡ Zn-normalize (phase-project w)
phase-project-normalize (w₁ , w₂) = refl

------------------------------------------------------------------------
-- Capstone — the phase projection is a Coxeter Core homomorphism
-- Zₙ-x-F → Zₙ. Used by per-Zₙ adapters as a one-line application.
------------------------------------------------------------------------
