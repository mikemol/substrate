------------------------------------------------------------------------
-- Substrate.Foundation.Eq.CongTrans
--
-- Defines: cong-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.CongTrans where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- Naturality-step combinator: `trans (cong f p) q` packaged as one
-- inference rule. Categorically a chain-cong / naturality-square step;
-- recognisable site-shape across the repo (338+ occurrences in 124
-- files at extraction time). Naming the step makes the rewrite-chain
-- structure visible to the similarity checker.
------------------------------------------------------------------------

cong-trans : {A : Set a} {B : Set b} (f : A → B) {x y : A} {z : B} →
             x ≡ y → f y ≡ z → f x ≡ z
cong-trans f p q = trans (cong f p) q
