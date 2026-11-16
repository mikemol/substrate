------------------------------------------------------------------------
-- Substrate.Lambda.Fragment.Combinator
--
-- Defines: B, C, Combinator, I, K, S
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lambda.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment.Combinator where




------------------------------------------------------------------------
-- 1. The SKI combinator basis.
--
-- Three primitive combinators generating the entire untyped lambda
-- calculus:
--   S = λ x y z. (x z)(y z)   — substitution
--   K = λ x y. x              — constant
--   I = λ x. x                — identity
--
-- (B, C are derivable but included as named combinators for
-- ergonomic worked examples.)
------------------------------------------------------------------------

data Combinator : Set where
  S : Combinator   -- S x y z = (x z)(y z)
  K : Combinator   -- K x y = x
  I : Combinator   -- I x = x
  B : Combinator   -- B = S(KS)K     — composition
  C : Combinator   -- C = S(BBS)(KK) — swap
