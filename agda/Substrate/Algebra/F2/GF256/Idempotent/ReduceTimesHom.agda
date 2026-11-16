------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent.ReduceTimesHom
--
-- Defines: reduce-*-hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.GF256.Idempotent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent.ReduceTimesHom where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.GF256.Reduce
open import Substrate.Algebra.F2.GF256.Expand
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.GF256.Idempotent.ReduceIdempotent



-- A9: reduce is a ring hom in the multiplicative slot — reducing a factor first
-- doesn't change the reduced product. Falls straight out of A4 + A6 (no keystone).
reduce-*-hom : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
             → reduce-mod-m (p *P q) ≡ reduce-mod-m (p *P reduce-mod-m q)
reduce-*-hom p q =
  trans (reduce-*P-expand p q)
        (sym (trans (reduce-*P-expand p (reduce-mod-m q))
                    (cong (hsum p) (reduce-idempotent (reduce-mod-m q)))))
