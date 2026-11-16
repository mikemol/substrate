------------------------------------------------------------------------
-- Substrate.Foundation.Eq.SymTrans
--
-- Defines: sym-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.SymTrans where

open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- Sym-composition pair. `sym-trans p q` rewrites the source of `q`
-- backwards along `p`; `trans-sym p q` rewrites the target of `p`
-- backwards along `q`. Together they package the two dual triangles
-- against a shared endpoint: `sym-trans` shares the source, `trans-sym`
-- shares the target. 72 + 81 occurrences across the repo at extraction.
------------------------------------------------------------------------

sym-trans : {A : Set a} {x y z : A} → x ≡ y → x ≡ z → y ≡ z
sym-trans p q = trans (sym p) q
