------------------------------------------------------------------------
-- Substrate.Algebra.Module.Free
--
-- Mod4 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- The canonical FreeModule R n — the n-dimensional R-vector space
-- realised as `Vec R n` with componentwise ops. Parametric in the
-- Ring R.
--
-- The Module-axioms on Vec R n follow from R's Ring axioms +
-- componentwise lifting; the full construction packages those laws
-- into a Module record. The signature lives here; the per-R
-- packaging happens at Mod6 (F₂) and Mod7 (ℚ).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Free where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate; zipWith; map)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma)
open import Substrate.Algebra.Monoid using (Monoid; semigroup; ε)
open import Substrate.Algebra.Ring using (Ring; semiring)
open import Substrate.Algebra.Semiring using (+-monoid; *-monoid)
open import Substrate.Algebra.Module using (Module)

------------------------------------------------------------------------
-- 1. The FreeModule carrier.
--
-- A FreeModule R n is just `Vec A n` (where A is R's carrier) —
-- the n-dimensional R-vector space with componentwise ops.
------------------------------------------------------------------------

FreeCarrier : (A : Set) → ℕ → Set
FreeCarrier A n = Vec A n

------------------------------------------------------------------------
-- 2. Componentwise operations on the free carrier.
------------------------------------------------------------------------

free-zero : {A : Set} (zeroA : A) (n : ℕ) → FreeCarrier A n
free-zero zeroA n = replicate n zeroA

free-+ : {A : Set} (_+A_ : A → A → A) {n : ℕ} →
  FreeCarrier A n → FreeCarrier A n → FreeCarrier A n
free-+ _+A_ = zipWith _+A_

free-scalar : {A : Set} (_·A_ : A → A → A) {n : ℕ} →
  A → FreeCarrier A n → FreeCarrier A n
free-scalar _·A_ r v = map (r ·A_) v

------------------------------------------------------------------------
-- 3. The Module-instance signature.
--
-- Given a Ring R + its operations (extracted via field accessors),
-- the FreeCarrier A n IS a Module over R via componentwise ops.
-- Full instance lands per-R at Mod6 / Mod7 — each instance packages
-- the 4 module axioms via R's ring laws (componentwise lifting).
------------------------------------------------------------------------

-- FreeModule-of : {A : Set} (R : Ring A) (n : ℕ) → Module R (FreeCarrier A n)
-- (deferred per-R; F₂-instance at Mod6, ℚ-instance at Mod7)

------------------------------------------------------------------------
-- 4. Capstone for Mod4.
--
-- FreeCarrier + free-zero + free-+ + free-scalar landed as the
-- canonical componentwise operations. Mod5 supplies the basis-
-- embedding + universal property.
------------------------------------------------------------------------
