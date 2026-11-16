------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.QLtqTimesp
--
-- Defines: q<q*p
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.QLtqTimesp where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 4. The factorisation EXISTENCE theorem: the div-mod wedge iterated by the
--    least prime divisor, well-founded on the strictly-decreasing quotient.
------------------------------------------------------------------------

-- a positive quotient against a factor ≥ 2 strictly decreases: q < q·p.
q<q*p : (q' p : ℕ) → 2 ≤ p → suc q' < suc q' * p
q<q*p q' p 2≤p = ≤-trans sucq≤q*2 q*2≤q*p
  where
    q*2≡q+q : suc q' * 2 ≡ suc q' ℕ+ suc q'
    q*2≡q+q = trans (*-suc (suc q') (suc zero)) (cong (suc q' ℕ+_) (*-identityʳ (suc q')))
    sucq≤q+q : suc (suc q') ≤ suc q' ℕ+ suc q'
    sucq≤q+q = s≤s (n≤m+n q' (suc q'))
    sucq≤q*2 : suc (suc q') ≤ suc q' * 2
    sucq≤q*2 = subst (λ x → suc (suc q') ≤ x) (sym q*2≡q+q) sucq≤q+q
    q*2≤q*p : suc q' * 2 ≤ suc q' * p
    q*2≤q*p = *-monoʳ-≤ (suc q') 2≤p
