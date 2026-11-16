------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Tm
--
-- Defines: Tm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Tm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- ① THE SHARED BASE (defined ONCE — the coupling fix). One SKI term, one cost.
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm
