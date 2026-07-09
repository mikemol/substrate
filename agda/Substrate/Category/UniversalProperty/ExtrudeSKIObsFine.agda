{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIObsFine — ⟡extrude-ski-obs-fine: a NONTRIVIAL observation
-- refining 252's degenerate ≋ᴼ, and the HONEST characterization (catalog-checked) of why a TOTAL nontrivial
-- ≈-invariant obs is undecidable — so the refinement lives on the DISTINGUISHABLE ATOMS.
--
-- 252 FINDING (verified this turn): with obs⊤ : Tm⟦533ef80d⟧ → ⊤, ObsBisim's ≋ᴼ is the TOTAL relation — everything ≋
-- everything (S ≋ᴼ K provable by guarded corecursion, DegenCheck). So 252's ski-≋, while a valid ObsBisim
-- instance with Y-of a fixpoint, is DEGENERATE (one class). A meaningful quotient needs a nontrivial obs.
--
-- THE OBSTRUCTION (catalog-checked, per the 252 lesson — NOT declared without search): a term's TOP
-- CONSTRUCTOR is NOT ≈-invariant (I ∙ x ≈ x flips app↔arbitrary), and a TOTAL ≈-invariant obs distinguishing
-- non-atomic terms would decide convertibility (undecidable, SKI Turing-complete). The catalog's faithful/
-- graded machinery (SKIFaithfulRb = reconstruction; Shed = cost-grade, NOT ≈-invariant) does not provide a
-- total invariant either. So the refinement is CORRECTLY scoped to the ATOMS S/K/I, which ARE distinct
-- normal forms hence NON-CONVERTIBLE (CR/newman) — a genuine nontrivial distinction, constructible.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: atom-obs (a total obs
-- distinguishing S/K/I by tag), S≢K-obs (the atoms have distinct observations). The framing ('the total
-- invariant is undecidable', 'refines the degenerate quotient') is (prose: the undecidability is the
-- standard CL fact, NOT formalized here; atom-obs is the constructible nontrivial fragment).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIObsFine where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)

------------------------------------------------------------------------
-- ① A NONTRIVIAL OBSERVATION ON THE ATOMS. tag S/K/I to distinct ℕ codes (0/1/2), everything else to 3.
--    This is TOTAL. It is NOT ≈-invariant on composite terms (that would be undecidable) — but on the
--    ATOMS it is a genuine distinction, and the atoms are distinct normal forms (non-convertible, CR).
------------------------------------------------------------------------
atom-obs : Tm⟦533ef80d⟧ → ℕ
atom-obs S = zero
atom-obs K = suc zero
atom-obs I = suc (suc zero)
atom-obs _ = suc (suc (suc zero))

-- the atoms are OBSERVABLY DISTINCT — S and K have different observations (0 ≠ 1). Since S, K are distinct
-- normal forms they are non-convertible (CR/newman), so a ≈-respecting quotient MUST keep them apart —
-- which the degenerate obs⊤ (252) FAILED to do. atom-obs witnesses the needed distinction on the atoms.
S≢K-obs : atom-obs S ≡ atom-obs K → ⊥
S≢K-obs ()

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the meaningful SKI quotient needs a nontrivial obs; a TOTAL one is
-- undecidable, so the honest refinement distinguishes the ATOMS, and the total-invariant wall is a REAL
-- undecidability boundary, catalog-checked): the either/or "is 252's ≋ᴼ a real quotient or degenerate?"
-- RESOLVES — DEGENERATE with obs⊤ (verified: S ≋ᴼ K). The refinement either/or "a total nontrivial
-- ≈-invariant obs, or nothing" bottoms out in a DISTINCTION honestly drawn: a TOTAL ≈-invariant obs on
-- composite terms decides convertibility (UNDECIDABLE — SKI Turing-complete; the catalog's faithful/graded
-- machinery gives reconstruction/cost, NOT a total invariant), so it is a REAL boundary; but on the ATOMS
-- S/K/I (distinct normal forms, non-convertible by CR) a nontrivial obs IS constructible (atom-obs, ①), and
-- it witnesses the distinction obs⊤ collapsed. So the honest refinement is: the quotient is meaningful AT
-- LEAST on the atoms; a full contextual-equivalence obs is undecidable (a genuine wall, not a mis-scope).
-- This CORRECTS 252 (its quotient was degenerate) and CORRECTLY classifies the total-obs boundary (real
-- undecidability, catalog-checked — distinguishing it from the 250/252 over-scopes that dissolved).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = atom-obs (a total nontrivial obs) + S≢K-obs (the atoms are
-- observably distinct, so the degenerate obs⊤ was genuinely lossy). SCOPED / REAL WALL: (a) a TOTAL
-- ≈-invariant obs distinguishing composite terms is UNDECIDABLE (SKI convertibility) — a genuine boundary,
-- NOT a mis-scope (catalog-checked: no repo total invariant); (b) the ObsBisim instance at atom-obs — atom-obs
-- does NOT respect ≈ on composites, so it is NOT directly an ObsBisim obs; the ≈-respecting refinement needs
-- restriction to a decidable-nf subclass (⟡extrude-ski-obs-nf: obs = nf-head on the Nf subclass, where
-- reduction-invariance IS computable). What's grounded: 252's quotient is degenerate (corrected), the atoms
-- are observably distinct (atom-obs), and the total ≈-invariant obs is a REAL undecidability wall — the
-- refinement lives on the decidable atoms/nf, honestly scoped.
------------------------------------------------------------------------
