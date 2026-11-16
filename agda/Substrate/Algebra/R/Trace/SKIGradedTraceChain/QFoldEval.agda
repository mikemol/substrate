------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIGradedTraceChain.QFoldEval
--
-- Defines: q-fold-eval
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIGradedTraceChain; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.R.Trace.SKIGradedTraceChain.QFoldEval where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.SkiProduct
open import Substrate.Algebra.R.Trace.SKIGradedTraceChain.QFoldChain



-- eval of a q-fold chain is the q-fold ∧ (the accumulated structure) — the reskin
-- of Product.gpower: the total cost q is carried, the structure rebuilt.
q-fold-eval : (b : Shed 1) (q : ℕ)
            → eval (q-fold-chain b q) ≡ gpower ski-product b q
q-fold-eval b q = eval-pow {P = ski-product} b q

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the accumulating-grade chain, reskinned): the
-- SKI cost-carrying reduction SEQUENCE is a WedgeTerm over a SKI GradedProduct.
-- The grade of the whole chain is the SUM of the leaf cost-grades — the total
-- redex-cost, KEPT by construction (WedgeTerm never discards a factor). This is
-- the chained form of ADD 147's single graded shed: one shed = one leaf (grade =
-- its cost); the chain = the ⊗ of leaves (grade = Σ costs). The flat Trace ℕ-shed
-- (ADD 146) was the grade-collapsed-to-a-point shadow — Product.agda's verbatim
-- "plain DivStr collapses all grades to a point"; the WedgeTerm is the faithful
-- form where the grade IS the accumulated cost. A reskin of the graded monoid,
-- the same shape as gpower / EEATrace's chained quotients. The either/or "chain
-- with accumulating cost vs the flat sequence" dissolves: the flat sequence is
-- the grade-collapsed projection; the WedgeTerm is the original that keeps it.
------------------------------------------------------------------------
