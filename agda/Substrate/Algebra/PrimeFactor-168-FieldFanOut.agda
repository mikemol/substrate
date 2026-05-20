------------------------------------------------------------------------
-- Substrate.Algebra.PrimeFactor-168-FieldFanOut
--
-- |PSL(2, 7)| = 168 = 2³ · 3 · 7 as a FieldFanOut 3 sketch.
--
-- Per [[project-reserved-selfdual-bijection-gauge]]: the 168-gauge
-- family for the substrate's Reserved↔SelfDual bijection has 168
-- F₂-linear choices. 168 is NOT a prime power, so the structural
-- decomposition is into THREE host fields (F₂³ = Z/8, F₃, F₇)
-- connected via three bonds from Z/168 — a FieldFanOut 3.
--
-- For this slice: the FanOut SHAPE is realized; concrete bond
-- functions (mod 8, mod 3, mod 7) are PLACEHOLDERS (constant zero).
-- Real mod functions over Fin 168 would require 168 cases each;
-- deferred until a use site demands concrete computation.
--
-- The structural value: the substrate's 168-gauge IS a 3-field
-- fan-out decomposition; this slice surfaces the categorical
-- representation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PrimeFactor-168-FieldFanOut where

open import Data.Fin using (Fin; zero; suc)
open import Substrate.Category.FieldFanOut

------------------------------------------------------------------------
-- N-1: Targets of the FanOut — F₂³ (= Z/8 as additive), F₃, F₇.
------------------------------------------------------------------------

PSL27-Target : Fin 3 → Set
PSL27-Target zero                = Fin 8   -- F₂³ component (size 2³)
PSL27-Target (suc zero)          = Fin 3   -- F₃ component
PSL27-Target (suc (suc zero))    = Fin 7   -- F₇ component

------------------------------------------------------------------------
-- N-2: Bond functions — PLACEHOLDER (return zero) for each target.
--
-- Real bonds: n ↦ n mod 8, n ↦ n mod 3, n ↦ n mod 7. Each requires
-- 168 cases. Deferred.
------------------------------------------------------------------------

PSL27-Bond : (i : Fin 3) → Fin 168 → PSL27-Target i
PSL27-Bond zero             _ = zero
PSL27-Bond (suc zero)       _ = zero
PSL27-Bond (suc (suc zero)) _ = zero

------------------------------------------------------------------------
-- N-3: The FieldFanOut 3 instance for 168.
------------------------------------------------------------------------

PSL27-FieldFanOut : FieldFanOut 3
PSL27-FieldFanOut = record
  { Source = Fin 168
  ; Target = PSL27-Target
  ; Bond   = PSL27-Bond
  }

------------------------------------------------------------------------
-- N-4: Capstone.
--
-- After this slice: 168 = |PSL(2,7)| is represented as a FieldFanOut
-- 3 sketch. The fan-out shape captures the three-prime decomposition
-- 168 = 2³ · 3 · 7; the actual bond functions are placeholders
-- pending a substantive computation use site.
--
-- Per [[project-tree-shaped-field-bonds]]: this is the first FanOut
-- instance at a non-trivial composite count. The Z6 fan-out (Z/6 →
-- (Z/2, Z/3)) would be a FieldFanOut 2 sibling.
--
-- Per [[project-reserved-selfdual-bijection-gauge]]: the 168-gauge
-- IS this fan-out structure. The substrate's sacrifice ladder
-- selects which "chain" (FieldTower) flattens the fan-out for a
-- specific computational use.
------------------------------------------------------------------------
