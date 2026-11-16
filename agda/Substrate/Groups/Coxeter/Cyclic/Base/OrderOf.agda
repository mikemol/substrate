------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.OrderOf
--
-- Defines: σ-OrderOf
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec

module Substrate.Groups.Coxeter.Cyclic.Base.OrderOf (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n

-- ⟡cap-384: the ABSTRACT-σ seal (n is a module param → cyclic-suc {n} abstract →
-- cheap, no iterate normalization). Rides the `public` re-export chain to every
-- Zn-Coxeter-Fin; the capability field consumes THIS (a non-reducing token) so a
-- concrete cap-Zₙ record never re-normalizes `iterate n (cyclic-suc)`.
σ-OrderOf : OrderOf σ (suc n)
σ-OrderOf = seal-order σ-HasOrderPerm
