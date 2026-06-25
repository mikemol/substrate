------------------------------------------------------------------------
-- Substrate.WitnessTower.EEAFoldTable
--
-- Ⓢ.eea-fold-table — the recursion's fixed point, machine-checked. ONE EEA
-- trace, read through its folds. The EEA trace is the UNIVERSAL GENERATOR under
-- the bridges and towers: bridges, residues, CF convergents, and CRT splits are
-- all FOLDS of one trace over different targets — `eea-fold` (Nat.GCD.Fold) is
-- the catamorphism, and the fold TARGET picks the structure. (Z.Bezout's header:
-- "recognition returns the bridge… changing the type EEA operates on.")
--
-- Closes the G8 blind spot: this unification was narrated from headers; here it
-- is a term. For one t : EEATrace 3 2 (gcd-ℕ 3 2):
--   • gcd / RESIDUE     — the trace's TARGET INDEX g is the gcd.
--   • Bézout / BRIDGE   — `bezout-ℤ` = eea-fold {BezoutℤWitness}: s·a + t·b = g.
--   • digits / CF TOWER — `digits-of-EEA` = eea-fold {List ℕ}: the convergent
--                         quotients (`digits-is-catamorphism` proves it IS the fold).
--   • tower AGREEMENT   — those digits are the convergents the coinductive CF
--                         emits (`digit-agreement`).
--   • CRT / SPLIT       — g ≡ 1 ⟹ coprime: the same data certifies the clean split.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.EEAFoldTable where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.Wedge using () renaming (quotient to quotient⟦b7e6a995⟧)
open import Substrate.Algebra.Nat.GCD.Fold using (eea-fold)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace; coprime-trace)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)
open import Substrate.Algebra.R.Trace using (digits-of-EEA; take)
open import Substrate.Algebra.R.Trace.RationalAdjunction using (qToRℚ)
open import Substrate.WitnessTower.EEATower using (cf-length; digit-agreement)

------------------------------------------------------------------------
-- ONE trace: the EEA of (3, 2). Its target index IS the gcd.
------------------------------------------------------------------------

t : EEATrace 3 2 (gcd-ℕ 3 2)
t = gcd-trace 3 2

------------------------------------------------------------------------
-- FOLD 0 — gcd / RESIDUE: the trace's target index is the gcd.
------------------------------------------------------------------------

fold-gcd : gcd-ℕ 3 2 ≡ 1
fold-gcd = refl

------------------------------------------------------------------------
-- FOLD 1 — Bézout / BRIDGE: bezout-ℤ = eea-fold {BezoutℤWitness}; s·a + t·b = g.
------------------------------------------------------------------------

fold-bezout : BezoutℤWitness 3 2 (gcd-ℕ 3 2)
fold-bezout = bezout-ℤ t

------------------------------------------------------------------------
-- FOLD 2 — digits / CF TOWER: digits-of-EEA IS eea-fold at (List ℕ), and the
-- digits are the continued-fraction quotients of 3/2 = [1, 2].
------------------------------------------------------------------------

digits-as-fold : ∀ {a b g} → EEATrace a b g → List ℕ
digits-as-fold = eea-fold {T = λ _ _ _ → List ℕ} (λ _ → []) (λ _ w rest → quotient⟦b7e6a995⟧ w ∷ rest)

digits-is-catamorphism : digits-of-EEA t ≡ digits-as-fold t
digits-is-catamorphism = refl

fold-digits : digits-of-EEA t ≡ 1 ∷ 2 ∷ []
fold-digits = refl

------------------------------------------------------------------------
-- FOLD 3 — tower AGREEMENT: the same digits are the first cf-length convergents
-- the coinductive CF (qToRℚ = ana qStep) emits.
------------------------------------------------------------------------

fold-tower : digits-of-EEA t ≡ take (cf-length t) (qToRℚ (3 , 2))
fold-tower = digit-agreement t

------------------------------------------------------------------------
-- CRT / SPLIT — g ≡ 1 ⟹ coprime: the same data certifies the clean split.
------------------------------------------------------------------------

fold-crt : EEATrace 3 2 1
fold-crt = coprime-trace 3 2 refl
