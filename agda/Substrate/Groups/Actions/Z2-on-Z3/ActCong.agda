------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActCong
--
-- act respects both groups' equalities. One definition; relational, so
-- it names both group instances — the folder says which two.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActCong where

-- ⚑ `normalize` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹³) — applied at
-- the Z₃ index with that index's five arguments.
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
cap-Z₂ = CoxeterGroupW.cap 1

import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ as Z₂G
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-cong : ∀ {h₁ h₂ n₁ n₂} → h₁ Z₂G.≈ h₂ → n₁ Z₃G.≈ n₂ →
           act h₁ n₁ Z₃G.≈ act h₂ n₂
act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq =
  cong Z₃LP.normalize (cong₂ act-letter h-eq n-eq)
