------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.MulLaws.GmulAssoc
--
-- Defines: gmul-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.MulLaws; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.MulLaws.GmulAssoc where

open import Substrate.Algebra.F2.CommRing
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.MLo
open import Substrate.Algebra.F2.GF256.Mul.Gmul
open import Substrate.Algebra.F2.GF256.HornerSeam
import Substrate.Algebra.Polynomial.Graded.Quotient as Quot
open Quot.Over F₂-CommRing 7 m-lo using (_*Q_; *Q-identityˡ; *Q-identityʳ; *Q-zeroˡ; *Q-zeroʳ; *Q-assoc)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong



gmul-assoc : (a b c : Vector 8) → gmul (gmul a b) c ≡ gmul a (gmul b c)
gmul-assoc a b c =
  trans (cong (λ z → gmul z c) (sym (*Q-is-gmul a b)))
  (trans (sym (*Q-is-gmul (a *Q b) c))
  (trans (*Q-assoc a b c)
  (trans (*Q-is-gmul a (b *Q c))
         (cong (gmul a) (*Q-is-gmul b c)))))
