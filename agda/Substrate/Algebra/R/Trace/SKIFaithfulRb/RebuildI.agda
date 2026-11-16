------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIFaithfulRb.RebuildI
--
-- Defines: rebuild-I
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIFaithfulRb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIFaithfulRb.RebuildI where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Gen
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arity
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.GenTotm
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyMany
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.FaithfulRb
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.ApplyHom
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.CF
open import Substrate.Algebra.R.Trace.SKIFaithfulRb.Arities
-- ⚑ Ⓒ9: the CONSTRUCTORS `S`/`I` come from `Tm` itself, not through any sibling.
-- The split's import seed carries what a leaf's DEPENDENCIES mention, not what
-- the LEAF mentions — and since Ⓡ1 made emitted imports bare/non-public, a
-- constructor one hop away is out of scope. Second instance this turn
-- (cf. `SKIGradedTraceChain/SkiProduct.agda`).
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm


rebuild-I : faithful-rb gI (S ∷ []) ≡ (I ∙ S)
rebuild-I = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the arity either/or dissolved): "different
-- arities need different fixed rb" is FALSE. Arity is a GRADE; the reconstruction
-- is the ANTILOG (pow/apply-many) of the arity — ONE application step, iterated
-- arity-many times. faithful-rb g = apply-many (gen→tm g), and its behaviour varies
-- with the arity of the arg-list BECAUSE it iterates (the pow structure), witnessed
-- by apply-hom (apply xs then ys = apply xs++ys — arities ADD, exactly gpowg-hom's
-- additive→multiplicative shape). The CF then carries the REAL generators (the
-- contracted combinators), each with its arity as its grade — the two-strand SPPF
-- (reduce generator + peel structure), the varying degree of CrossMulGraded (I:1,
-- K:2, S:3). ONE rb, the antilog; the arity is its exponent, not a fixed slot.
------------------------------------------------------------------------
