{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeStepDecidable — ⟡extrude-step-decidable (REGROUNDING the
-- mis-scoped ⟡ski-tm-deceq): the extruder's cycle-test does NOT need TOTAL Tm⟦533ef80d⟧ decidable equality — that is
-- the TURING/TOTAL-space spook (the 6th D-no-classical-spook). We operate coinductively/bisimilarly: WITHIN
-- a step we take the CHEAPEST bijective DECIDABLE piece (an observation), and BLEED THE RESIDUE to the next
-- step. The search pattern IS the reduction strategy.
--
-- The substrate already NAMES this: Bisim._~_ is the coinductive equality —
--   head~ : head x ≡ head y     — the WITHIN-STEP decidable observation (one ℕ equality, cheap, bijective)
--   tail~ : tail x ~ tail y     — the RESIDUE, coinductively DEFERRED to the next step
-- So "equality" of the coinductive carrier is BISIMILARITY (observe the head, bleed the tail), never decided
-- in one total shot. Wedge.Coalgebra.eq? is `Dec (x ≡ y)` only in the LINEAR SPECIALIZATION (a within-step
-- residue check on the finite forest), not a global Tm⟦533ef80d⟧-DecEq; the run's `loop` is a bisimulation LASSO
-- (residues coincide up to ~), `stop` the residue still being bled (aperiodic so far). No total decision.
--
-- THIS MODULE grounds the reground: step-obs (the within-step decidable observation — a cheap head-shape
-- test on Tm⟦533ef80d⟧), and obs-bleeds-residue (the observation decides the head, the rest is the coinductive
-- residue for the next step) — the weaker-than-total form the extruder actually uses.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: HeadShape (the finite
-- within-step observation of a Tm⟦533ef80d⟧'s head), head-shape (the cheap decidable observation — total on the FINITE
-- head, the residue is the subterms), and head-shape-obs (the observation is a decidable ℕ/finite tag, the
-- bijective decidable piece per step). The framing ('bisimilarity not total DecEq; bleed residue; search =
-- reduction strategy') is (prose: Bisim._~_ + the 254/266 confluence regrounds; the full bisimilar SPPF run
-- stays coinductive, NOT a total decision).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeStepDecidable where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)

------------------------------------------------------------------------
-- ① THE WITHIN-STEP OBSERVATION: a Tm⟦533ef80d⟧'s head shape is a FINITE tag (S / K / I / app) — the cheapest
--    bijective decidable piece. The subterms are NOT inspected here; they are the RESIDUE for the next step.
------------------------------------------------------------------------
data HeadShape : Set where
  isS isK isI isApp : HeadShape

head-shape : Tm⟦533ef80d⟧ → HeadShape
head-shape S       = isS
head-shape K       = isK
head-shape I       = isI
head-shape (_ ∙ _) = isApp

------------------------------------------------------------------------
-- ② THE OBSERVATION IS DECIDABLE (within the step) — HeadShape has decidable equality (a finite tag), so the
--    per-step head-test is a genuine Dec; but it decides ONLY the head, bleeding the subterms as residue.
------------------------------------------------------------------------
_≟ₕ_ : (a b : HeadShape) → Dec (a ≡ b)
isS   ≟ₕ isS   = yes refl
isK   ≟ₕ isK   = yes refl
isI   ≟ₕ isI   = yes refl
isApp ≟ₕ isApp = yes refl
isS   ≟ₕ isK   = no λ ()
isS   ≟ₕ isI   = no λ ()
isS   ≟ₕ isApp = no λ ()
isK   ≟ₕ isS   = no λ ()
isK   ≟ₕ isI   = no λ ()
isK   ≟ₕ isApp = no λ ()
isI   ≟ₕ isS   = no λ ()
isI   ≟ₕ isK   = no λ ()
isI   ≟ₕ isApp = no λ ()
isApp ≟ₕ isS   = no λ ()
isApp ≟ₕ isK   = no λ ()
isApp ≟ₕ isI   = no λ ()

-- the within-step cycle-test observation: compare the head shapes (decidable) — the head is decided, the
-- subterms (for an app) are the RESIDUE bled to the next unfold step (never decided totally here):
step-obs : (a b : Tm⟦533ef80d⟧) → Dec (head-shape a ≡ head-shape b)
step-obs a b = head-shape a ≟ₕ head-shape b

------------------------------------------------------------------------
-- ③ THE RESIDUE IS BLED FORWARD: for two applications, the head observation (isApp ≡ isApp) is decided, and
--    the ARGUMENTS are the residue — the next step's observation. This is the search-as-reduction-strategy:
--    decide the cheap head, defer the subterms coinductively (à la Bisim.tail~).
------------------------------------------------------------------------
residue : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ × Tm⟦533ef80d⟧
residue (f ∙ x) = f , x
residue a       = a , a

-- head decided + residue deferred: an app's observation is isApp (decided), its residue the two subterms:
obs-bleeds-residue : (f x : Tm⟦533ef80d⟧) → (head-shape (f ∙ x) ≡ isApp) × (residue (f ∙ x) ≡ (f , x))
obs-bleeds-residue f x = refl , refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's cycle-test is BISIMILARITY (per-step decidable observation +
-- residue bled forward), NOT total Tm⟦533ef80d⟧ decidable equality; reaching for total DecEq is the Turing spook): the
-- either/or "the SPPF loop/stop needs total Tm⟦533ef80d⟧-DecEq (undecidable-ish, a wall) OR we can't do the run"
-- DISSOLVED (the 6th D-no-classical-spook) — the carrier is COINDUCTIVE, and its equality is BISIMILARITY
-- (Bisim._~_): head~ (a WITHIN-STEP decidable observation — head-shape, ①/②, the cheapest bijective decidable
-- piece) + tail~ (the RESIDUE, coinductively deferred — residue/obs-bleeds-residue, ③). So each step DECIDES
-- the cheap head (step-obs, a genuine Dec on the finite HeadShape) and BLEEDS the subterm residue to the next
-- step — the search pattern AS a reduction strategy. Wedge.Coalgebra.eq?'s Dec is the LINEAR-specialization
-- within-step check, not a global Tm⟦533ef80d⟧-DecEq; the run's `loop` is a bisimulation lasso (~), `stop` the residue
-- still bled. Every time "decidable" reaches for the TOTAL space it is the Turing shadow (250/252/253/254/266,
-- now 277 — the 6th); the weaker per-step/coinductive form is what the extruder uses, positive and confluent.
-- No spook. Chain: 254 (≈=confluence) → 264 (eq?=within-step) → 266 (spec=positive-reduction) → 277 (cycle-
-- test = per-step observation + residue, NOT total DecEq).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = HeadShape + head-shape (the within-step observation), _≟ₕ_ +
-- step-obs (the per-step DECIDABLE head-test — cheap, finite, bijective), residue + obs-bleeds-residue (the
-- subterms bled forward). SCOPED (reused-in-spirit, coinductive — NOT a total decision): the full bisimilar
-- SPPF run wiring the observation into Wedge.Coalgebra.run's loop/stop via Bisim._~_ (the residues coincide
-- up to ~ = loop; still bled = stop) — ⟡extrude-bisim-run; this REPLACES the mis-scoped ⟡ski-tm-deceq (total
-- DecEq is neither attainable nor wanted). What's grounded: the cycle-test is a per-step decidable observation
-- + residue bled forward (bisimilarity), the weaker-than-total form — the Turing spook dissolved a 6th time.
------------------------------------------------------------------------
