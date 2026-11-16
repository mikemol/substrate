------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Reduce.NatXmul
--
-- Defines: nat-xmul
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Reduce; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Reduce.NatXmul where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong



-- The shared ℕ cross-mult identity, with the cofactor witnesses substituted:
--   n · (den/g) ≡ (n/g) · den.
nat-xmul : (n qn g qd′ d : ℕ) →
           n ≡ qn * g → suc d ≡ suc qd′ * g → n * suc qd′ ≡ qn * suc d
nat-xmul n qn g qd′ d eqn eqd =
  trans (cong (_* suc qd′) eqn)
  (trans (*-assoc qn g (suc qd′))
  (trans (cong (qn *_) (*-comm g (suc qd′)))
         (cong (qn *_) (sym eqd))))
