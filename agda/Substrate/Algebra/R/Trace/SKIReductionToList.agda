{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIReductionToList — ⟡ski-reduction-to-list: derive
-- the List Tm shed-sequence (autochain's input, ADD 150) from an ACTUAL reduction,
-- so the cost-chain comes from a real _⇒_ reduction, not a hand-made list.
--
-- COUPLING NOTE (the ADD-150 lesson, applied): SKIShedDuality has Tm+cost;
-- NewmanKI has its OWN Tm+_⇒_. Deriving a List SKIShedDuality.Tm from a NewmanKI
-- reduction is the SAME two-Tm coupling wall. The grounded fix (shared base over
-- bridge): MIRROR the reduction onto SKIShedDuality.Tm — so cost AND reduction live
-- on ONE Tm. (CrossMul/Bridge could translate NewmanKI.Tm → this Tm — the two are
-- structurally identical — but the shared base is the elegant instance.) NewmanKI
-- stays residue: its Newman-confluence proof is intact; this consolidates the
-- reduction onto the cost-bearing Tm, and the SAME _⇒_ takes RewriteConfluence.newman.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIReductionToList where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)

-- REUSE the shared base (ADD 150): its Tm, cost, Chain, autochain, total-cost.
open import Substrate.Algebra.R.Trace.SKIShedDuality
  using (Tm; S; K; I; _∙_; cost; Chain; total-cost; autochain)

------------------------------------------------------------------------
-- ① The full SKI reduction, mirrored onto the SHARED Tm (β-I, β-K, β-S + congruence)
-- — so reduction and cost are on one carrier. Same shape as NewmanKI's, plus β-S.
------------------------------------------------------------------------
data _⇒_ : Tm → Tm → Set where      -- ⟦shape:66d2c034 β-I,β-K,β-S⟧
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  β-K    : (x y : Tm)          → ((K ∙ x) ∙ y) ⇒ x
  β-S    : (x y z : Tm)        → (((S ∙ x) ∙ y) ∙ z) ⇒ ((x ∙ z) ∙ (y ∙ z))
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')

-- reuse RewriteConfluence's reflexive-transitive closure at THIS _⇒_ (not re-rolled).
open import Substrate.Foundation.RewriteConfluence _⇒_ using (_⇒*_; done; _◅_)

------------------------------------------------------------------------
-- ② THE REDUCTION → LIST fold: walk the closure a ⇒* b, collecting the SOURCE term
-- at each step (the term at which a redex is contracted). done ↦ []; a step from a
-- collects a then recurses. This is the shed-sequence autochain consumes.
------------------------------------------------------------------------
reduction→list : {a b : Tm} → a ⇒* b → List Tm
reduction→list done          = []
reduction→list (_◅_ {a = a} _ rest) = a ∷ reduction→list rest

------------------------------------------------------------------------
-- ③ THE COST-CHAIN FROM A REAL REDUCTION: autochain the derived list — the cost
-- chain of an ACTUAL reduction, grade = Σ head-costs of the source terms.
------------------------------------------------------------------------
reduction-chain : {a b : Tm} (r : a ⇒* b) → Chain (total-cost (reduction→list r))
reduction-chain r = autochain (reduction→list r)

-- the total shed cost of a reduction = the grade of its chain (head-costs summed).
reduction-cost : {a b : Tm} → a ⇒* b → ℕ
reduction-cost r = total-cost (reduction→list r)

------------------------------------------------------------------------
-- ④ CONCRETE: a real head-reduction sequence and its derived list + cost. Each
-- HEAD step contracts a head redex (cost 1); the derived list's total-cost counts
-- them. (Deep cong-steps shed head-cost 0 — the head-cost model, SKIShedDuality's;
-- capturing the redex-position cost is ⟡ski-position-cost, scoped.)
------------------------------------------------------------------------
-- I ∙ (I ∙ K) ⇒ I ∙ K ⇒ K : two HEAD β-I steps, each cost 1.
red2 : (I ∙ (I ∙ K)) ⇒* K
red2 = β-I (I ∙ K) ◅ (β-I K ◅ done)

-- its shed-sequence is [I∙(I∙K), I∙K] and its total head-cost is 2 (both head redexes).
red2-list-cost : reduction-cost red2 ≡ 2
red2-list-cost = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): autochain's List Tm input is the FOLD of a real
-- reduction closure (reduction→list), so the cost-chain (ADD 150) is grounded in an
-- ACTUAL _⇒_ reduction — the shed-sequence is not hand-made. The coupling (cost on
-- SKIShedDuality.Tm, reduction on NewmanKI.Tm) dissolved by consolidating _⇒_ onto
-- the shared cost-bearing Tm (the ADD-150 shared-base move, one level up): ONE Tm
-- carries cost AND reduction AND (via RewriteConfluence.newman on this same _⇒_)
-- confluence. reduction→list is the trace-fold of the _⇒*_ closure into List Tm;
-- autochain is its cost read. The head-cost-vs-position-cost either/or is scoped
-- (head-cost is SKIShedDuality's model; per-position is ⟡ski-position-cost), not
-- collapsed — deep steps shed head-cost 0, honestly noted, not hidden.
------------------------------------------------------------------------
