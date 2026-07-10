{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixpointStencil — ⟡fixpoint-stencil: THE THIRD
-- stencil instance, the one whose TWO FRAMINGS ARE the two existing instances.
--
-- THE QUESTION (operator): the stencil relates two framings; we have two instances of it
-- (trace/wedge, Kleene); what is the stencil instance where those two instances are
-- THEMSELVES the two framings?
--
-- THE ANSWER: the two existing instances are two CHARACTERIZATIONS of the SAME fixed-point.
--   • trace/wedge (185/186/187) = the ALGEBRAIC framing: Trace = INITIAL Φ-algebra,
--     RealTrace = TERMINAL coalgebra — the universal-property / map-out-map-in reading.
--   • Kleene (159/162, KleeneStencil 188) = the ITERATIVE framing: μΦ = ⋃ₙ Φⁿ⊥ (colimit,
--     ascending from ⊥), νΦ = ⋂ₙ Φⁿ⊤ (limit, descending from ⊤) — the chain/approximation
--     reading.
-- The THIRD instance is the fixed-point-CONSTRUCTION's own self-agreement: the object that
-- is the SAME fixed-point however you build it (algebraic = Kleene). Its two frames are the
-- two instances, RELATED LEVEL-WISE by the meta-Lambek hinge:
--   • ≡-frame (the μ level, EXACT): algebraic-μ ≅ Kleene-μ = Colim ≅ Trace (159, BOTH
--     directions proven) — the two framings' μ-halves are iso ON THE NOSE.
--   • ~-frame (the ν level, UP-TO): algebraic-ν ≟ Kleene-ν = RealTrace vs Limit — the
--     greatest-fixed-point UP (coalg-below-limit, 162) DELIVERED; the full RealTrace ≅ Limit
--     is SCOPED (162's honest remainder).
-- The one Lawvere fixed-point: the fixed-point-construction operator Fix, whose self-
-- application (Fix is characterization-INDEPENDENT — the fixed point is the fixed point
-- however built) is the diagonal. And it has the SAME ≡/~ asymmetry as the base stencil
-- (exact on μ/≡, partial/up-to on ν/~) — the stencil is a FIXED POINT of itself, self-similar.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FixpointStencil where

open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Category.Allegory.Refinement using (Fam; _⊑ᶠ_)
open import Substrate.Algebra.Wedge.TraceMuStep using (Idx; Φ-step; TraceF)
import Substrate.Algebra.Wedge.TraceKleeneColimit as Kμ
import Substrate.Algebra.Wedge.TraceNuColimit as Kν

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE ≡-FRAME HINGE (the μ level, EXACT): the ALGEBRAIC framing's μ (Trace = initial
  -- Φ-algebra) is ISO to the KLEENE framing's μ (Colim = ⋃ₙ Φⁿ⊥). BOTH directions — this
  -- is the two instances agreeing on the nose at the finite/halting level. Colim ≅ Trace.
  ------------------------------------------------------------------------
  algebraic-μ→kleene-μ : TraceF D ⊑ᶠ Kμ.Colim D          -- algebraic Trace ⊑ Kleene Colim
  algebraic-μ→kleene-μ = Kμ.trace→colim D

  kleene-μ→algebraic-μ : Kμ.Colim D ⊑ᶠ TraceF D          -- Kleene Colim ⊑ algebraic Trace
  kleene-μ→algebraic-μ = Kμ.colim→trace D
  -- together: Colim ≅ Trace — the ≡-frame of the third instance, the two framings' μ-halves
  -- iso EXACTLY (the meta-Lambek hinge on the halting side).

  ------------------------------------------------------------------------
  -- ② THE ~-FRAME HINGE (the ν level, UP-TO): the greatest-fixed-point universal property
  -- — every ν-coalgebra sits below the Kleene Limit (⋂ₙ Φⁿ⊤). This is the two framings
  -- agreeing at the non-halting level, DELIVERED as the UP (the full RealTrace ≅ Limit is
  -- scoped, 162 — the SAME ≡-exact / ~-partial asymmetry as the base stencil).
  ------------------------------------------------------------------------
  algebraic-ν-below-kleene-ν : {X : Fam (Idx D)} → (X ⊑ᶠ Φ-step D X) → X ⊑ᶠ Kν.Limit D
  algebraic-ν-below-kleene-ν = Kν.coalg-below-limit D

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the stencil is a FIXED POINT OF ITSELF): the THIRD stencil
-- instance is the fixed-point-CONSTRUCTION's characterization-independence. Its fixed-point
-- is THE fixed-point (Trace/RealTrace ≅ μΦ/νΦ); its TWO FRAMINGS are the two existing
-- instances — the ALGEBRAIC (trace/wedge, universal property) and the KLEENE (iterative,
-- chain) — related LEVEL-WISE by the meta-Lambek hinge:
--   ≡-frame (μ, EXACT):  algebraic Trace ≅ Kleene Colim  (Colim ≅ Trace, 159, BOTH dirs).
--   ~-frame (ν, UP-TO):  algebraic ν below Kleene Limit  (coalg-below-limit, 162; full ≅ scoped).
-- So "which stencil instance has the two instances as its framings?" = the instance whose
-- Lawvere fixed-point is Fix ITSELF (the construction is characterization-independent — the
-- fixed point is the fixed point however built), whose ≡-frame is the two instances' μ-halves
-- iso ON THE NOSE (Colim ≅ Trace) and whose ~-frame is their ν-halves related up-to (the
-- greatest-fixed-point UP). CRUCIALLY it has the SAME ≡/~ asymmetry as the base stencil
-- (exact μ, partial ν) — the stencil applied to its own instances REPRODUCES the stencil's
-- shape: the stencil is a FIXED POINT of itself, self-similar under "frame the two framings
-- as one framing". The either/or "is the third instance new, or just the same stencil?" 
-- dissolves: it is the SAME stencil (self-similar), which is exactly what makes it a genuine
-- Lawvere fixed-point (the diagonal = the construction naming itself). The two proven
-- instances ARE the two frames; the meta-instance's hinge is Colim ≅ Trace (159/162).
------------------------------------------------------------------------
