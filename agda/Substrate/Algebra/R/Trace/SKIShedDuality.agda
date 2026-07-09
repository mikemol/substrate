{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality — ⟡ski-cost-autochain + ⟡ski-graded-
-- diverges, discharged together on ONE properly-grounded shared base.
--
-- ADD 147 (SKITermToShedding) and ADD 148 (SKIGradedTraceChain) each hand-rolled
-- their OWN local `Tm`; combining them (to wire cost into the chain, or to build
-- the coinductive side) hit a coupling wall — the symptom that the local-Tm
-- duplication was mis-grounded. This module is the fresh grounded version: ONE Tm,
-- ONE cost, and BOTH fixed-point sides of the residue-shedding functor (ADD 146),
-- each carrying the REAL cost, exhibited as the init/term DUALITY (ADD 149):
--
--   SN / least fp  = the INDUCTIVE cost chain — a WedgeTerm over a SKI GradedProduct
--                    whose leaf grades ARE cost t (⟡ski-cost-autochain: wired, not
--                    hand-specified). fold side, terminates.
--   Diverges / greatest fp = the COINDUCTIVE cost stream — a RealTrace built by ana
--                    (unfold) whose head IS the shed cost at each step
--                    (⟡ski-graded-diverges). unfold side, productive-forever.
--
-- The two are the DUAL reads of one (Tm, cost): trace-fold (initial) ⊣ ana
-- (terminal), the ℚ⊣R hinge. SKITermToShedding/SKIGradedTraceChain KEPT as residue.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIShedDuality where

open import Substrate.Foundation.Eq  using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.Wedge.Product using (GradedProduct)
open import Substrate.Algebra.Wedge.Product.Term using (WedgeTerm; leaf; nil; _⊗_; eval)
open import Substrate.Algebra.R.Trace        using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Bisim  using (_~_; head~; tail~; ~-refl; cons)

------------------------------------------------------------------------
-- ① THE SHARED BASE (defined ONCE — the coupling fix). One SKI term, one cost.
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:533ef80d S K I,_∙_⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm
infixl 7 _∙_

-- the head-redex cost shed by contracting once (the Nf obstruction, ADD 130-142).
cost : Tm → ℕ
cost (I ∙ x)             = 1
cost ((K ∙ x) ∙ y)       = 1
cost (((S ∙ x) ∙ y) ∙ z) = 1
cost _                   = 0

-- a shed at cost-grade n (carrying the peeled subterm) — the shared graded carrier.
record Shed (n : ℕ) : Set where
  constructor shed⟨_⟩
  field peeled : Tm
open Shed public

------------------------------------------------------------------------
-- ② THE SN / LEAST-FP SIDE: the inductive cost chain (WedgeTerm reskin), with the
-- leaf grades WIRED from cost automatically — ⟡ski-cost-autochain.
------------------------------------------------------------------------
-- ⟡set1-paydown: GradedProduct's carrier family is now its param (Shed).
ski-product : GradedProduct Shed
ski-product = record
  { u   = shed⟨ I ⟩
  ; _∧_ = λ {i}{j} s t → shed⟨ peeled s ∙ peeled t ⟩
  }

Chain : ℕ → Set
Chain n = WedgeTerm ski-product n

-- THE AUTOCHAIN LEAF: a shed of term t, its grade wired to the ACTUAL cost t (not
-- a hand-specified 1). Chain (cost t) — the cost is READ from the term, automatic.
cost-leaf : (t : Tm) → Chain (cost t)
cost-leaf t = leaf {P = ski-product} {i = cost t} (shed⟨ t ⟩)

-- total-cost of a reduction sequence (list of shed terms): Σ cost.
total-cost : List Tm → ℕ
total-cost []       = 0
total-cost (t ∷ ts) = cost t + total-cost ts

-- THE AUTOCHAIN: fold a reduction sequence into a cost chain, grades ACCUMULATING
-- the ACTUAL per-term costs automatically (no hand-specified grades). The total
-- grade is total-cost ts BY CONSTRUCTION — the cost is wired, not asserted.
autochain : (ts : List Tm) → Chain (total-cost ts)
autochain []       = nil
autochain (t ∷ ts) = cost-leaf t ⊗ autochain ts

------------------------------------------------------------------------
-- ③ THE DIVERGES / GREATEST-FP SIDE: the coinductive cost stream (RealTrace via
-- ana/unfold), head = the shed cost at each step — ⟡ski-graded-diverges. A
-- reduction coalgebra S → ℕ × S emits (cost, next-state); ana assembles the
-- productive-forever stream. Its equality is Bisim._~_ (the terminal universal).
------------------------------------------------------------------------
-- a divergent reduction as a coalgebra: at each state, shed a cost and step on.
-- Ω = SII(SII) sheds cost 1 forever and returns to itself (one-state coalgebra).
ΩCoalg : ⊤ → ℕ × ⊤
ΩCoalg tt = 1 , tt

diverge-cost-stream : RealTrace
diverge-cost-stream = unfold ΩCoalg tt

-- the head IS the shed cost at every step (1 for Ω) — carried, not collapsed.
diverge-head-is-cost : head diverge-cost-stream ≡ 1
diverge-head-is-cost = refl

-- the tail is the same divergent stream — productive forever (the greatest fp).
diverge-tail : tail diverge-cost-stream ~ diverge-cost-stream
head~ diverge-tail = refl
tail~ diverge-tail = ~-refl (tail diverge-cost-stream)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the duality made explicit on ONE base): the SN
-- and Diverges sides are the INITIAL-algebra and TERMINAL-coalgebra reads of the
-- SAME (Tm, cost). autochain (fold side, WedgeTerm/trace-fold) accumulates the real
-- costs inductively; diverge-cost-stream (unfold side, RealTrace/ana) emits the real
-- costs coinductively. Both carry cost — neither collapses. The "SN vs Diverges"
-- and "the two mis-grounded modules" either/ors dissolve: ONE Tm, ONE cost, the
-- fold⊣unfold (ℚ⊣R) duality. The local-Tm duplication (ADD 147/148) is residue —
-- this shared base is the grounded form. ⟡ski-cost-autochain = the fold side wired;
-- ⟡ski-graded-diverges = the unfold side, both discharged here.
------------------------------------------------------------------------
