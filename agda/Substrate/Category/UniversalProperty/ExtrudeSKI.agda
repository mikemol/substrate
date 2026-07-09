{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKI — ⟡agda-extrude-ski: the SKI extruder's fixed-point core
-- as the ⇒*-CONCRETE realization of the repo's ExtruderFix, and the CONVERGENCE of the diagonal arc with
-- the extruder thread. The catalog-check (244, standing) found ExtruderFix ALREADY states the unification
-- the diagonal arc (245-248) reconstructed: "an extruder is minimisation = the μ-operator = a FIXED POINT
-- ... that fixpoint is Lawvere's (lawvere-fixed-point, POSITIVE) ... the ω = SII self-application". So the
-- arc and the extruder are ONE structure, already named.
--
-- ExtruderFix.CombinatorAlgebra.fixpoint-from-diagonals gives, ABSTRACTLY (at ≡): diagonals-for-all-f ⟹
-- fixed-points-for-all-f. My 248 Y-of/Y-fix is the CONCRETE SKI realization — but at ⇒* (reduction), NOT ≡,
-- because SKI reduction is not definitional equality on Tm⟦533ef80d⟧. So this is the ⇒*-ANALOG, honestly marked.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: ski-diagonal (the ω_f ω_f
-- self-application witness at ⇒*), extrude-fixpoint (the extruder's fixed-point synthesis = Y-of, ⇒*). The
-- framing ('the extruder IS the arc', 'minimisation = μ = fixpoint = Lawvere') is (prose: it is ExtruderFix's
-- OWN framing, reused; the ≡-level CombinatorAlgebra instantiation for Tm⟦533ef80d⟧ is scoped — Tm⟦533ef80d⟧'s laws are ⇒*, not ≡).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKI where

open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (_∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_)
open import Substrate.Category.UniversalProperty.DiagonalLawvereSKI using (self-app)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (W; Y-of; Y-fix)

------------------------------------------------------------------------
-- ① THE SKI DIAGONAL WITNESS (⇒*-concrete image of ExtruderFix's "Σ C (λ t → t · t ≡ f · (t · t))").
--    For each f, the term W f self-applies to a fixed point: (W f)(W f) ⇒* f ((W f)(W f)). This is
--    Lawvere's diagonal φ a a = ω_f ω_f, realized on Tm⟦533ef80d⟧ at the reduction equality.
------------------------------------------------------------------------
ski-diagonal : (f : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ t → (t ∙ t) ⇒* (f ∙ (t ∙ t)))
ski-diagonal f = (W f) , Y-fix f

------------------------------------------------------------------------
-- ② THE EXTRUDER'S FIXED-POINT SYNTHESIS = Y-of (the CONVERGENCE, ⇒*). ExtruderFix:
--    "an extruder is the minimal M satisfying control C = MINIMISATION = μ = a FIXED POINT". For the
--    fixed-point control (t ⇒* f t), the extruder does NOT search — Y-of CONSTRUCTS the witness directly.
--    So the SKI self-interpreter extruder's core (a fixed point of one-step-interpret) IS Y-of (248):
--    the μ-search collapses to the explicit self-applicative construction.
------------------------------------------------------------------------
extrude-fixpoint : (f : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ t → t ⇒* (f ∙ t))
extrude-fixpoint f = (Y-of f) , Y-fix f

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the diagonal arc and the extruder are ONE structure, ALREADY NAMED in
-- ExtruderFix; my 248 Y-of is its ⇒*-concrete SKI realization): the either/or "is the extruder's fixed-point
-- core a separate thing from the diagonal arc's Lawvere fixed point?" bottoms out — they are ONE, and the
-- repo already SAYS SO: ExtruderFix's header states "extruder = minimisation = μ = FIXED POINT = Lawvere's
-- (lawvere-fixed-point POSITIVE) = ω = SII self-application" — EXACTLY the arc's 244-catch → 248-construction.
-- The convergence is not a coincidence: an extruder is a self-referential synthesizer (search = recursion =
-- self-reference = fixed point), and self-reference IS self-application (ω/SII), whose fixed point is Lawvere-
-- positive. So the arc (escape = Lawvere fixed point, constructed at ⇒* in 248) and the extruder (minimal-M =
-- μ = fixed point) are the SAME fixed point, seen from two sides. My extrude-fixpoint = Y-of realizes
-- ExtruderFix.fixpoint-from-diagonals CONCRETELY on Tm⟦533ef80d⟧ at ⇒* — the extruder's essence, constructed.
--
-- HONEST BOUNDARY (⟡H-overclaim — the ≡ vs ⇒* gap, marked): GROUNDED = ski-diagonal + extrude-fixpoint
-- (the extruder's fixed-point synthesis = Y-of, at ⇒*, --safe). SCOPED: (a) a literal CombinatorAlgebra
-- (ExtruderFix, ≡-level) instance for Tm⟦533ef80d⟧ — BLOCKED at ≡ because SKI's S/K laws hold on Tm⟦533ef80d⟧ only up to ⇒*, not
-- definitional ≡ (β-S/β-K are reductions, not equalities); the honest bridge is the ⇒*-analog here, and a
-- setoid/quotient CombinatorAlgebra (C = Tm⟦533ef80d⟧/⇒*≈) is the route to the literal instance (⟡extrude-ski-setoid);
-- (b) the MINIMAL extruder (least-cost M via bounded enum + Dec) + its μ-uniqueness (trace-fold-unique,
-- Wedge) — the general search, of which extrude-fixpoint is the fixed-point case where search collapses to
-- construction. What's grounded: the extruder's fixed-point core is Y-of (248) — the arc and the extruder
-- are ONE fixed point (ExtruderFix's own thesis), realized concretely on Tm⟦533ef80d⟧ at ⇒*.
------------------------------------------------------------------------
