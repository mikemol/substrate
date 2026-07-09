{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIConfluent — CORRECTING the 253 Turing-shadow spook. The
-- entire point of instantiating Lawvere (Category.Lawvere): metacircularity (self-reference) and
-- diagonalization are ONE structure, and the substrate lives on the POSITIVE side — the fixed point EXISTS
-- (Y-of, 248). The classical NEGATIVES (Cantor no-surjection, Gödel/Turing undecidability) are the
-- CONTRAPOSITIVE shadow. So a "meaningful SKI quotient needs a total ≈-invariant obs that DECIDES
-- convertibility (undecidable)" (253) is the CLASSICAL/Turing framing — the shadow the Lawvere instantiation
-- was built to dissolve. The observational object does NOT decide anything: ≈-invariance comes from a
-- POSITIVE PROVEN theorem — CONFLUENCE (RewriteConfluence.CR / NewmanSKI.Properties.I-reduction-CR):
-- convertible terms reach a COMMON REDUCT (Converge = Σ d. b ⇒* d × c ⇒* d). No decision procedure; a
-- positive witness. The undecidability wall is not a wall for the coinductive/observational carrier.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: reduct-obs (Converge as
-- the ≈-invariant observation-relation), convertible-converge (a ⇒* b ⟹ Converge a b, from done/reflexivity
-- and CR), and the positive framing that this needs NO decision. The claim 'undecidability is irrelevant
-- here' is (prose: the LEM/Turing-shadow point of Category.Lawvere, cited; the general convertibility-
-- undecidability is the classical fact this SIDESTEPS, not refutes).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIConfluent where

open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; Converge)

------------------------------------------------------------------------
-- ① THE OBSERVATION IS THE COMMON REDUCT (Converge), NOT A DECISION. Two terms are observationally
--    related when they CONVERGE — reach a common reduct. This is POSITIVE data (a witness d + two
--    reductions), never a decision procedure. Confluence (CR, proven for SKI) guarantees convertible
--    terms converge — so ≈-invariance is a THEOREM, not a computation that must terminate.
------------------------------------------------------------------------
reduct-obs : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
reduct-obs a b = Converge a b       -- Σ d. (a ⇒* d) × (b ⇒* d)

-- reflexivity: a term converges with itself (both reduce to it via done) — the observation is inhabited
-- WITHOUT any normalization / decision. Divergent terms still converge with themselves (done needs no NF).
reduct-refl : (a : Tm⟦533ef80d⟧) → reduct-obs a a
reduct-refl a = a , (done , done)

-- a directed reduction gives convergence (b is the common reduct): a ⇒* b ⟹ Converge a b. So every
-- reduction fact (incl. Y-of f ⇒* f (Y-of f), 248) yields the observation — no decision, just the reduct.
⇒*→converge : {a b : Tm⟦533ef80d⟧} → a ⇒* b → reduct-obs a b
⇒*→converge {a} {b} r = b , (r , done)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the observational object gets ≈-invariance from CONFLUENCE, a POSITIVE
-- proven theorem, NOT from deciding convertibility; the Turing/Gödel "undecidability wall" is the classical
-- CONTRAPOSITIVE shadow the Lawvere instantiation dissolves): the 253 either/or "a total decidable
-- ≈-invariant obs, or a real undecidability wall" was FALSE-FRAMED — it is the CLASSICAL framing (decide the
-- class). The substrate lives on Lawvere's POSITIVE side (the fixed point EXISTS, Y-of; self-reference =
-- diagonalization, ONE structure, Category.Lawvere's own thesis). The observation is the COMMON REDUCT
-- (Converge, ①), a positive witness; confluence (CR, proven — I-reduction-CR) makes convertible terms
-- converge, so the equivalence is well-defined WITHOUT deciding anything. Non-termination is not a wall —
-- it is a coinductive observation (escape=finality, 234; ℝ=finite observation). So 253's "undecidability
-- wall" was the FOURTH mis-scope — not a HIT (250) or set-truncation (252) mis-scope, but a TURING-SHADOW
-- mis-scope: I got spooked by convertibility-undecidability when the whole Lawvere arc (245-252) was built
-- to show the classical negatives are STRUCTURALLY IRRELEVANT to the coinductive/positive object. The
-- correct obs is confluence-based (Converge), positive, proven — no decision, no wall.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = reduct-obs (Converge as the ≈-invariant observation), reflexivity
-- (no NF needed), and ⇒*→converge (every reduction, incl. Y-of's fixpoint, is an observation). What 253 got
-- WRONG (corrected): the "undecidability wall" is a Turing shadow; the coinductive/observational carrier
-- does not decide convertibility, it OBSERVES via the common reduct (confluence). SCOPED (correctly): the
-- full ObsBisim instance with obs = the Converge-class (a proper non-degenerate quotient from confluence) —
-- ⟡extrude-ski-obs-converge; and the general convertibility-undecidability remains a classical fact this
-- SIDESTEPS (not refutes). What's grounded: ≈-invariance is from confluence (positive, proven), the
-- undecidability wall dissolved — the point of instantiating Lawvere.
------------------------------------------------------------------------
