------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Coalg
--
-- Defines: ΩCoalg
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Coalg where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Product
open import Substrate.Foundation.Unit
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost



------------------------------------------------------------------------
-- ③ THE DIVERGES / GREATEST-FP SIDE: the coinductive cost stream (RealTrace via
-- ana/unfold), head = the shed cost at each step — ⟡ski-graded-diverges. A
-- reduction coalgebra S → ℕ × S emits (cost, next-state); ana assembles the
-- productive-forever stream. Its equality is Bisim._~_ (the terminal universal).
------------------------------------------------------------------------
-- a divergent reduction as a coalgebra: at each state, shed a cost and step on.
-- Ω = SII(SII) sheds cost 1 forever and returns to itself (one-state coalgebra).
ΩCoalg : ⊤ → ℕ × ⊤
ΩCoalg tt = 1 , tt
