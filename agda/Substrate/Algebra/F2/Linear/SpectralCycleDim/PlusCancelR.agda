------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusCancelR
--
-- Defines: +-cancelʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusCancelR where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ



------------------------------------------------------------------------
-- conn4: orbit-hits-once — occ (suc n) k j ≡ 𝟙. Strategy: occ is INVARIANT
-- under k ↦ cyclic-suc k (the boundary term cancels via σ_p^p=id), so every k
-- reduces to k=0, where the orbit is the identity enumeration (Kronecker base).
------------------------------------------------------------------------

-- two F₂ helpers
+-cancelʳ : (a b c : F₂) → (a +F c) ≡ (b +F c) → a ≡ b
+-cancelʳ a b c eq =
  -- ⚑ THE SIGNATURE WAS REPAIRED TO `_+F_` AND THE BODY LEFT ON `_+_`.  At
  -- @771283c8~1 the parent read `(a + c) ≡ (b + c)` under a whole-module
  -- `open import Substrate.Algebra.F2`; the shard imports the decomposed leaves,
  -- where the operator is spelled `_+F_`.  Sections carry the spelling too.
  trans (sym (+-identityʳ a))
  (trans (cong (a +F_) (sym (+-self-inverse c)))
  (trans (sym (+-assoc a c c))
  (trans (cong (_+F c) eq)
  (trans (+-assoc b c c)
  (trans (cong (b +F_) (+-self-inverse c)) (+-identityʳ b))))))
