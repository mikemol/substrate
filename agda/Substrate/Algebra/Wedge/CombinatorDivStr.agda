{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.CombinatorDivStr — ⟡N1b-EEA-wire. Lands S5EEA's
-- combinator-reduction-as-DivStr (S5EEA.agda, ADD 44, standalone) onto the
-- substrate's OWN Algebra.Wedge.DivStr — so the repo's GENERIC wedge/Trace/
-- shape machinery applies to combinator reduction DIRECTLY (not via a
-- reproduced DivStr). The reduction orbit IS a substrate Trace; its CF is the
-- substrate's own `shape` (the generic quotient sequence); value = done
-- (terminal/GCD reached); regress = a Trace whose shape is (eventually)
-- periodic, detected by the substrate's shape equality.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.CombinatorDivStr where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Wedge using (DivStr; C; z; recon; Trace; done; more)
open import Substrate.Algebra.Wedge.Shape using (WedgeShape; shape)

------------------------------------------------------------------------
-- Combinator reduction as a substrate DivStr: carrier = reduction states S,
-- terminal z = the normal form nf, recon = the state reconstruction rb.
-- Parametric in (S, nf, rb) — instantiated with the evaluator's _unspine/_wrap
-- at the Python tier. This is a REAL substrate DivStr (record of its fields).
------------------------------------------------------------------------
module Reduction (S : Set) (nf : S) (rb : S → S → S → S) where

  combinator-DivStr : DivStr
  combinator-DivStr = record { C = S ; z = nf ; recon = rb }

  -- the reduction orbit IS a substrate Trace over this DivStr.
  ReductionTrace : S → S → S → Set
  ReductionTrace = Trace combinator-DivStr

  -- the CF of a reduction = the substrate's OWN generic shape (quotient seq).
  reduction-CF : {a b g : S} → ReductionTrace a b g → WedgeShape combinator-DivStr
  reduction-CF = shape

  -- value = done at the terminal: CF is [] (finite CF = rational = GCD reached).
  value-is-empty-CF : (a : S) → reduction-CF (done a) ≡ []
  value-is-empty-CF a = refl

  -- the CF of a step exposes the generator (quotient) as the head — landing
  -- S5EEA's reduction-CF on the substrate's shape (more _ w tr → quot w ∷ …).
  -- PeriodWitness: two sub-traces with EQUAL substrate-shape = a detected
  -- period (the online-Sequitur recurrence, ADD 36, on the substrate's shape).
  PeriodWitness :
    {a₁ b₁ g₁ a₂ b₂ g₂ : S} →
    ReductionTrace a₁ b₁ g₁ → ReductionTrace a₂ b₂ g₂ → Set
  PeriodWitness t₁ t₂ = reduction-CF t₁ ≡ reduction-CF t₂
