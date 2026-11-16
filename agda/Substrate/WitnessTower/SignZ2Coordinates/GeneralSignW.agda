------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.GeneralSignW
--
-- Defines: general-signW
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.GeneralSignW where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.Xor
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- ◆ip-general-signW — proven, not pre-judged. For ANY perm σ, the Coxeter-length
-- parity signW of a completed derivation of insert-at p σ equals the sign fact
-- (= sym sign-wd ∘ signB-insert). Committed so the shape-DB can find a twin — if
-- one exists, that IS the "second construction" the filing worry denied.
------------------------------------------------------------------------

general-signW : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) (pf : IsPerm σ) →
  signW (coxeter-complete (insert-at p σ) (insert-at-preserves p σ pf))
    ≡ (oddB (toℕ p) xor sign σ)
general-signW p σ pf =
  trans (sym (sign-wd (coxeter-complete (insert-at p σ) (insert-at-preserves p σ pf))))
        (signB-insert p σ pf)
