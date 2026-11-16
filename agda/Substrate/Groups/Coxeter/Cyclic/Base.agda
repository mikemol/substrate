------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base
--
-- Foundation layer: Gen, power, Canonical-at (Fin-indexed), canonical-cover,
-- bijection to/from Fin, σ permutation, σ-HasOrderPerm, Word-level insert.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Foundation.Fin.Iterate
  using (HasOrderPerm; OrderOf; seal-order)
open import Substrate.Algebra.Nat.CyclicSuc
  using (cyclic-suc; cyclic-suc-HasOrderPerm)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Base.LengthPower
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt n
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalCover n
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalToFin n
open import Substrate.Groups.Coxeter.Cyclic.Base.FinToCanonical n
open import Substrate.Groups.Coxeter.Cyclic.Base.FinRoundtrip n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
open import Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm n
open import Substrate.Groups.Coxeter.Cyclic.Base.OrderOf n
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
