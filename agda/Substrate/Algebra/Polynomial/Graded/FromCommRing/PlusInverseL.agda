------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseL
--
-- Defines: +-inverseˡ
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Algebra.Polynomial.Graded.FromCommRing; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Algebra.AbelianGroup
open import Substrate.Algebra.CommutativeRing.Record
open import Substrate.Algebra.Group
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Ring
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Trans

module Substrate.Algebra.Polynomial.Graded.FromCommRing.PlusInverseL {A : Set} (CR : CommutativeRing A) where

open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Group
open import Substrate.Algebra.AbelianGroup
open import Substrate.Algebra.Ring
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Trans

open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Neg CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.OpOf
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Plus CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.R CR
open import Substrate.Algebra.Polynomial.Graded.FromCommRing.Zero CR
+-inverseˡ : (a : A) → neg a + a ≡ 𝟘
+-inverseˡ = subst (λ M → (a : A) → opOf M (neg a) a ≡ ε M)
                   (+-coherent R) (inv-left (group (+-abelian R)))
