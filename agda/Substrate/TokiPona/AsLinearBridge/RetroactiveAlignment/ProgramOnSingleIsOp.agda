------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.ProgramOnSingleIsOp
--
-- Defines: program-on-single-is-op
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge.RetroactiveAlignment.ProgramOnSingleIsOp where

open import Substrate.Groups.Coxeter.Word
open import Substrate.TokiPona.Nimi
open import Substrate.TokiPona.AsLinearBridge
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Z.JacobianNegSemiring
open import Substrate.TokiPona.LinearAlgebra



------------------------------------------------------------------------
-- 2. The AsLinearBridge's `program` agrees with the basis-action
-- on single-nimi words.
--
-- For any V + per-nimi operation, the Bridge program applied to a
-- single-nimi word IS the basis operation. The FreeOverBasis
-- η-coherence at the program layer (Toki Pona side).
------------------------------------------------------------------------

program-on-single-is-op :
  (V : Set) (_⊞_ : V → V → V) (e : V) (nimi-image : Nimi → V) →
  (n : Nimi) (s : V) →
  Bridge.program V _⊞_ e nimi-image (n ∷ []) s ≡ (s ⊞ nimi-image n)
program-on-single-is-op V _⊞_ e nimi-image n s = refl
