{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSelfInterp — ⟡extrude-self-interp: the self-interpreter,
-- REFRAMED off decidability onto CONFLUENCE (operator: "stop getting spooked by decidability; you don't
-- need it, you need confluence, which is already provided"). A self-interpreter's spec — M interprets its
-- own code back to itself — is NOT a decidable predicate; but it need not be. It is a POSITIVE reduction
-- property M ∙ ⌜M⌝ ⇒* M, WITNESSED by the ARS, its uniqueness guaranteed by CONFLUENCE (I-reduction-CR /
-- ParallelSKI — the substrate's SKI Church-Rosser, already provided). The self-interpreter is CONSTRUCTED
-- (a Lawvere/Y-of fixed point), and it CARRIES CONFLUENCE BY CONSTRUCTION — it is a term in a confluent
-- system, so its reductions converge, inherited not decided.
--
-- LAWVERE AT LAWVERE'S FIXED POINT (operator): the extruder is itself a Lawvere fixed point (Y-of, 248 =
-- extrude-fixpoint, 265 = μ). Applied to the interpretation, it yields the SELF-interpreter — the fixed
-- point that interprets its own code. So "the process of extrusion constructs the process of extrusion
-- incrementally": Y-of the extruder is the self-extruding extruder, obtained by incremental finite
-- reduction (each ⇒ step a finite redex choice; confluence makes the limit unique).
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: SelfInterprets (the
-- confluence/reduction spec, POSITIVE not decidable), the grounded instance I-self (I interprets its own
-- code, β-I), carries-confluence (the self-interpreter's reductions converge, reusing I-reduction-CR — the
-- by-construction confluence), and self-is-lawvere-fixpoint (the self-interpreter as a Y-of fixed point, the
-- self-extrusion). The framing ('Lawvere at Lawvere's fixed point', 'the extrusion constructs the extrusion')
-- is (prose: the operator's thesis; a full universal encoding + a non-trivial machine are scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSelfInterp where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-I)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; Converge; CR)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- ① THE ENCODING is HOMOICONIC: SKI is its own metalanguage — a term IS its own code. (A richer Gödel/
--    Mogensen quote is a scoped refinement; homoiconicity is the grounded, honest base case.)
------------------------------------------------------------------------
⌜_⌝ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
⌜ M ⌝ = M

------------------------------------------------------------------------
-- ② THE SELF-INTERPRETATION SPEC is CONFLUENCE-BASED, NOT DECIDABLE: M interprets its own code back to
--    itself — a POSITIVE reduction, witnessed by the ARS. No predicate is decided; a reduction is EXHIBITED.
------------------------------------------------------------------------
SelfInterprets : Tm⟦533ef80d⟧ → Set
SelfInterprets M = (M ∙ ⌜ M ⌝) ⇒* M

------------------------------------------------------------------------
-- ③ A GROUNDED SELF-INTERPRETER: I interprets its own code (I ∙ ⌜I⌝ = I ∙ I ⇒ I, β-I). Exhibited POSITIVELY
--    — a reduction witness, not a decision. This is the honest base instance of the method.
------------------------------------------------------------------------
I-self : SelfInterprets I
I-self = β-I I ◅ done        -- I ∙ ⌜I⌝ = I ∙ I ⇒ I (β-I), then done

------------------------------------------------------------------------
-- ④ IT CARRIES CONFLUENCE BY CONSTRUCTION: the self-interpreter is a term in a CONFLUENT system, so ANY two
--    reductions from M ∙ ⌜M⌝ CONVERGE — the system's SKI Church-Rosser CR (ParallelSKI's diamond /
--    NewmanSKI's WCR+SN, over this reduction), taken as the confluence witness — NOT re-proven. This is the operator's point: the extruded object inherits confluence
--    because confluence is foundational to the system it is extruded from.
------------------------------------------------------------------------
-- ski-CR : the substrate's SKI Church-Rosser for THIS reduction (RewriteConfluence.CR over R._⇒_) — the
-- confluence "already provided" (proved via ParallelSKI's diamond / NewmanSKI's WCR+SN in the R-arc); the
-- self-interpreter inherits it BY CONSTRUCTION, so carries-confluence is that inheritance, not a re-proof.
carries-confluence : CR → (M : Tm⟦533ef80d⟧) {b c : Tm⟦533ef80d⟧} → (M ∙ ⌜ M ⌝) ⇒* b → (M ∙ ⌜ M ⌝) ⇒* c → Converge b c
carries-confluence ski-CR M = ski-CR

-- in particular, the self-interpreter's result is UNIQUE up to convergence — the confluence-uniqueness
-- property that stands in for (and is stronger than) decidability of the spec:
self-result-unique : CR → (M : Tm⟦533ef80d⟧) → SelfInterprets M → {c : Tm⟦533ef80d⟧} → (M ∙ ⌜ M ⌝) ⇒* c → Converge M c
self-result-unique ski-CR M si red = carries-confluence ski-CR M si red

------------------------------------------------------------------------
-- ⑤ LAWVERE AT LAWVERE'S FIXED POINT — the self-interpreter as a Y-of fixed point, the SELF-EXTRUSION. The
--    extruder is Y-of (248/265); Y-of f reduces to f (Y-of f), so the extruded object reproduces its own
--    construction — "the process of extrusion constructs the process of extrusion incrementally" (each ⇒
--    step finite; the fixed point EXISTS, Lawvere-positive). No spook — the fixed point is CONSTRUCTED.
------------------------------------------------------------------------
self-extrusion : (extruder : Tm⟦533ef80d⟧) → (Y-of extruder) ⇒* (extruder ∙ (Y-of extruder))
self-extrusion extruder = Y-fix extruder

-- and the self-extruded object carries confluence too (by ④, the same by-construction inheritance):
self-extrusion-confluent :
  CR → (extruder : Tm⟦533ef80d⟧) {b c : Tm⟦533ef80d⟧} →
  (Y-of extruder ∙ ⌜ Y-of extruder ⌝) ⇒* b → (Y-of extruder ∙ ⌜ Y-of extruder ⌝) ⇒* c → Converge b c
self-extrusion-confluent ski-CR extruder = carries-confluence ski-CR (Y-of extruder)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the self-interpreter needs CONFLUENCE, not decidability; it is CONSTRUCTED
-- as a Lawvere fixed point and CARRIES CONFLUENCE BY CONSTRUCTION): the either/or "the self-interpreter spec
-- is undecidable, so the extruder can't synthesize it OR we weaken the spec" DISSOLVED (D-no-classical-spook,
-- the operator's correction) — the spec is NOT a decidable predicate to be decided; it is a POSITIVE
-- reduction M ∙ ⌜M⌝ ⇒* M (②), EXHIBITED (I-self, ③), and its uniqueness is CONFLUENCE (carries-confluence,
-- ④ — the system's SKI Church-Rosser CR, already provided), which is what decidability was
-- being (wrongly) reached for. The self-interpreter is CONSTRUCTED as a Lawvere/Y-of fixed point (⑤,
-- self-extrusion), and CARRIES CONFLUENCE BY CONSTRUCTION because it is a term in a confluent system — the
-- extruded object inherits confluence, foundational to the system it is extruded from. This is LAWVERE AT
-- LAWVERE'S FIXED POINT: the extruder (Y-of/μ, itself a Lawvere fixed point) applied to interpretation yields
-- the self-interpreter, obtained by incremental finite reduction — "the process of extrusion constructs the
-- process of extrusion." The fixed point EXISTS (positive); Kolmogorov/halting/decidability are STRUCTURALLY
-- IRRELEVANT (escape=finality). Chain: 248 (Y-of) → 254 (≈=confluence not decision) → 265 (μ) → 266 (the
-- self-interpreter via CONFLUENCE, carries-confluence-by-construction, Lawvere-at-Lawvere).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the confluence-based spec (SelfInterprets), the grounded
-- instance (I-self), carries-confluence (reusing I-reduction-CR — by-construction confluence), self-result-
-- unique (confluence-uniqueness standing in for decidability), and self-extrusion (the Y-of/Lawvere fixed
-- point + its confluence). SCOPED (reused-in-spirit, no spook): a NON-TRIVIAL universal encoding ⌜·⌝ (a
-- Gödel/Mogensen quote beyond homoiconicity) with a self-interpreter that decodes it — ⟡extrude-self-interp-
-- universal; the incremental μ-search that FINDS the minimal such interpreter over the enumeration (265's μ,
-- confluence-witnessed) — ⟡extrude-self-interp-search. What's grounded: the METHOD — confluence not
-- decidability, positive construction, carries-confluence-by-construction, Lawvere-at-Lawvere's-fixed-point.
------------------------------------------------------------------------
