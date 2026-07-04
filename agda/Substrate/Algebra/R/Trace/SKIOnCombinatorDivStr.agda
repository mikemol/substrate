{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIOnCombinatorDivStr — ⟡ski-on-combinatordivstr: the
-- CORRECTED grounding of the whole SKI-shedding arc (ADD 143-151). Those five
-- modules hand-rolled `Tm`, `cost : Tm → ℕ`, and `_⇒_` — re-deriving what the
-- substrate ALREADY parameterizes as Wedge.CombinatorDivStr.Reduction (ADD 152).
--
-- Here: supply ONLY the carrier parameters (S = the term, nf = a normal form,
-- rb = reconstruction) and instantiate the center. EVERYTHING ELSE falls out —
-- the reduction is the ReductionTrace, the COST is Wedge.Shape.shape (the quotient
-- sequence, NOT a hand-rolled cost), SN is value-is-empty-CF (done ⟹ CF []), and
-- Diverges/regress is PeriodWitness (equal shapes = a detected period). No local
-- reduction, no hand-rolled cost, no coupling. The five modules stay residue.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIOnCombinatorDivStr where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Wedge using (DivStr; C; z; recon; Trace; done; more; quot)
open import Substrate.Algebra.Wedge.Shape using (WedgeShape; shape)
import Substrate.Algebra.Wedge.CombinatorDivStr as CDS

------------------------------------------------------------------------
-- ① THE CARRIER PARAMETER (the ONLY thing supplied — S, nf, rb). A minimal SKI
-- term as the reduction-state carrier. Note: this is the DivStr's C (a parameter),
-- NOT a re-derivation — the reduction/cost/SN/Diverges all come from the center.
------------------------------------------------------------------------
data Tm : Set where      -- ⟦shape:c800487a S K I,_∙_,nf⟧
  S K I : Tm
  _∙_   : Tm → Tm → Tm
  nf    : Tm                          -- the terminal/normal-form marker (the z)
infixl 7 _∙_

-- reconstruction rb q b r: rebuild a reduction state from generator q, base b,
-- residual r. For the combinator wedge, the generator applied to the residual —
-- the structure-rebuild (FUSepQSKI's rcn, the invertible peel), q kept as the head.
rb : Tm → Tm → Tm → Tm
rb q b r = (q ∙ b) ∙ r

------------------------------------------------------------------------
-- ② INSTANTIATE THE CENTER. This ONE line replaces the five hand-rolled modules'
-- reduction+cost+SN+Diverges machinery.
------------------------------------------------------------------------
open CDS.Reduction Tm nf rb
  using (combinator-DivStr; ReductionTrace; reduction-CF; value-is-empty-CF; PeriodWitness)

------------------------------------------------------------------------
-- ③ THE COST IS shape (NOT hand-rolled). reduction-CF = Wedge.Shape.shape = the
-- quotient sequence (the CF), quotients kept as carrier reps. A reduction's cost
-- IS its CF — the list of redex-contraction generators, from the center.
------------------------------------------------------------------------
ski-cost : {a b g : Tm} → ReductionTrace a b g → WedgeShape combinator-DivStr
ski-cost = reduction-CF                       -- = shape, the quotient sequence

------------------------------------------------------------------------
-- ④ SN = value-is-empty-CF: a term that IS a normal form has empty CF (done, no
-- steps shed). The least-fixed-point/terminal corner, from the center.
------------------------------------------------------------------------
ski-nf-empty : (a : Tm) → ski-cost (done a) ≡ []
ski-nf-empty = value-is-empty-CF

------------------------------------------------------------------------
-- ⑤ A CONCRETE REDUCTION as a ReductionTrace, its cost read as the shape. Two
-- steps shedding generators I then K: the CF is [I, K] — the real per-step cost,
-- carried by the quotients (NOT collapsed, NOT a hand-rolled ℕ). done at nf.
------------------------------------------------------------------------
-- more b w rec : Trace a b g. Build a 2-step trace ending in done. The wedge at
-- each step carries quot = the generator. We use the generic Wedge record.
open import Substrate.Algebra.Wedge using () renaming (Wedge to Wedge⟦478f66a6⟧)
step-wedge : (gen b r : Tm) → Wedge⟦478f66a6⟧ combinator-DivStr (rb gen b r) b
step-wedge gen b r = record { quot = gen ; rem = r ; wedge-eq = refl }

-- a 2-step reduction ending at nf. Build bottom-up so every wedge-eq is refl by
-- construction: the last step reduces (rb K nf nf) via generator K to nf; the first
-- reduces (rb I (rb K nf nf) nf) via generator I. Sources ARE the reconstructions.
inner : ReductionTrace (rb K nf nf) nf nf
inner = more nf (step-wedge K nf nf) (done nf)

red2 : ReductionTrace (rb I (rb K nf nf) nf) (rb K nf nf) nf
red2 = more (rb K nf nf) (step-wedge I (rb K nf nf) nf) inner

-- its cost IS the quotient sequence [I, K] — the real per-step generators, via shape.
red2-cost : ski-cost red2 ≡ (I ∷ K ∷ [])
red2-cost = refl

------------------------------------------------------------------------
-- ⑥ Diverges/regress = PeriodWitness: two sub-traces with EQUAL shape = a detected
-- period (the greatest-fixed-point/regress side, from the center — not a hand-rolled
-- coinductive stream). A trace corresponds to itself (trivial period witness).
------------------------------------------------------------------------
red2-self-period : PeriodWitness red2 red2
red2-self-period = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the correction realized): the SKI reduction, its
-- cost, its SN corner, and its regress/period ALL come from ONE instantiation of
-- Wedge.CombinatorDivStr.Reduction. The only thing supplied is the carrier (Tm, nf,
-- rb); reduction = ReductionTrace, cost = shape (the quotient sequence [I,K], not a
-- hand-rolled cost : Tm → ℕ), SN = value-is-empty-CF, period = PeriodWitness. The
-- five hand-rolled modules (ADD 143-151) are the residue this replaces: each
-- re-derived this parameterization; this instantiates it. The either/or "define the
-- SKI machinery vs reuse the center" dissolves — the machinery IS the center,
-- combinator-reduction-IS-a-DivStr, and the carrier is its sole parameter.
------------------------------------------------------------------------
