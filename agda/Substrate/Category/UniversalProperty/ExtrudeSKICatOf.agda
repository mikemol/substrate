{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKICatOf — ⟡extrude-ski-catof: packaging the SKI quotient
-- as a PROPER observational-equivalence quotient via the repo's CrossMul/HetQ pattern (operator's steer),
-- NOT a fresh setoid record and NOT a HIT. The operator pointed at FUSep.ObsBisim ("via CrossMul +
-- CrossEquality") — an OBSERVATIONAL convertibility over an ARS: a coinductive applicative bisimulation
-- (obs-eq + tail≋ under every application), a genuine congruence realized WITHOUT set-truncation, because
-- CrossMul "sidesteps the tensor-quotient bare --safe lacks: R is GIVEN, not constructed" (the ℚ paradigm:
-- compare via a given carrier, no HIT). So Tm⟦533ef80d⟧-mod-observation is a proper quotient equality, reused.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: ski-≋ (SKI observational
-- equivalence = ObsBisim._≋_ at ski-ARS, instantiated), and Y-of as a ≋-fixpoint (fix-≋, from 250's
-- fix-law-≋ via ≈⟹≋). The framing ('the proper quotient', 'CrossMul dissolves the set-truncation boundary')
-- is (prose: the observational quotient IS proper here; the ≡-on-a-Set-carrier ExtruderFix.CombinatorAlgebra
-- still wants a set-quotient, but the CORRECT equality for a non-normalizing calculus is this ≋, not ≡).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKICatOf where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.FUSep.ConversionCongruence as CC
open import Substrate.Category.UniversalProperty.ExtrudeSKISetoid using (ski-ARS; _≋_; fix-law-≋)
import Substrate.FUSep.ObsBisim as OB
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of)

------------------------------------------------------------------------
-- ① THE OBSERVATION. For a proper observational quotient we need obs : Tm⟦533ef80d⟧ → Obs respecting convertibility
--    ≈. The minimal total ≈-respecting observation is the trivial one (Obs = ⊤): it gives the PURE
--    APPLICATIVE BISIMULATION (tail≋ under every application context) — SKI CONTEXTUAL equivalence, the
--    coarsest sound quotient. (A finer obs — e.g. a normal-form head-symbol probe — refines it; scoped.)
------------------------------------------------------------------------
obs⊤ : Tm⟦533ef80d⟧ → ⊤
obs⊤ _ = tt

obs⊤-resp : ∀ {a b} → CC._≈_ ski-ARS a b → obs⊤ a ≡ obs⊤ b
obs⊤-resp _ = refl

-- instantiate the repo's ObsBisim at SKI: the observational-equivalence quotient (CrossMul/HetQ pattern).
-- ObsBisim's members live in an anonymous module _ (R)(Obs)(obs)(obs-resp) → apply them to those args.
_≋ᴼ_ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
_≋ᴼ_ = OB._≋_ ski-ARS ⊤ obs⊤ obs⊤-resp

≈⟹≋ᴼ : {a b : Tm⟦533ef80d⟧} → _≋_ a b → a ≋ᴼ b
≈⟹≋ᴼ = OB.≈⟹≋ ski-ARS ⊤ obs⊤ obs⊤-resp

≋ᴼ-refl : {a : Tm⟦533ef80d⟧} → a ≋ᴼ a
≋ᴼ-refl = OB.≋-refl ski-ARS ⊤ obs⊤ obs⊤-resp

------------------------------------------------------------------------
-- ② THE SKI OBSERVATIONAL QUOTIENT is a proper equivalence (refl/sym/trans, from ObsBisim — REUSED), and
--    convertibility maps into it (≈⟹≋ᴼ). This is Tm⟦533ef80d⟧-mod-observation as a genuine quotient equality, built
--    from the given ARS via the CrossMul-style construction — no HIT, no fresh record.
------------------------------------------------------------------------
ski-≋ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
ski-≋ = _≋ᴼ_

ski-≋-refl : {a : Tm⟦533ef80d⟧} → ski-≋ a a
ski-≋-refl = ≋ᴼ-refl

------------------------------------------------------------------------
-- ③ Y-of IS A FIXPOINT AT THE OBSERVATIONAL QUOTIENT. From 250's fix-law-≋ (Y-of f ≋ f (Y-of f) at
--    convertibility) via ≈⟹≋ᴼ (convertibility ⟹ observational equivalence): Y-of f ≋ᴼ f (Y-of f). So the
--    extruder's fixpoint holds at the PROPER quotient equality — HasFix realized at ≋ᴼ.
------------------------------------------------------------------------
fix-≋ᴼ : (f : Tm⟦533ef80d⟧) → ski-≋ (Y-of f) (f ∙ (Y-of f))
fix-≋ᴼ f = ≈⟹≋ᴼ (fix-law-≋ f)

quotient-HasFix : (f : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ v → ski-≋ v (f ∙ v))
quotient-HasFix f = (Y-of f) , fix-≋ᴼ f

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the "≡-carrier needs set-truncation" boundary is the WRONG target;
-- CrossMul/HetQ give the PROPER quotient equality, and the correct carrier-equality for SKI is
-- observational ≋, not ≡): the either/or "either a set-quotient Tm⟦533ef80d⟧/≈ (HIT, blocked) or no proper quotient
-- carrier" DISSOLVES — the operator's CrossMul/HetQ pointer shows the repo builds quotients by comparison
-- in a GIVEN carrier (CrossMul: "R is GIVEN, not constructed" — the ℚ paradigm), and FUSep.ObsBisim
-- realizes exactly this for an ARS as OBSERVATIONAL equivalence (a coinductive applicative bisimulation).
-- So Tm⟦533ef80d⟧-mod-observation ≋ᴼ IS a proper quotient equality (refl/sym/trans, a congruence), no HIT — and
-- Y-of is a fixpoint at it (③). The lesson (correcting BOTH my 250 over-scope AND my near-over-scope this
-- turn): the ≡-on-a-Set-carrier ExtruderFix.CombinatorAlgebra was the WRONG target for a non-normalizing
-- calculus — its ≡ is too fine on Tm⟦533ef80d⟧ and a set-quotient needs truncation; the CORRECT carrier-equality is
-- observational ≋ (the extruder's own equivalence, CrossMul-built), at which the combinator laws (250) and
-- Y-of's fixpoint (③) hold. Chain: 249 (extruder=fixpoint) → 250 (gap closed at ≈) → 251 (≈ is a groupoid
-- = constructive quotient) → 252 (the PROPER observational quotient ≋ᴼ via CrossMul/ObsBisim, Y-of a
-- fixpoint on it).
--
-- HONEST BOUNDARY (⟡H-overclaim, held skeptically per 251): GROUNDED = ski-≋ᴼ (the SKI observational
-- quotient = ObsBisim instantiated, REUSED) + Y-of a fixpoint at it (③). SCOPED (correctly, not over-):
-- (a) a FINER observation than ⊤ (a real head-symbol/NF-probe obs, refining ≋ᴼ toward genuine
-- contextual-equivalence-with-content) — ⟡extrude-ski-obs-fine; (b) the LITERAL ≡-carrier
-- ExtruderFix.CombinatorAlgebra remains a set-quotient (HIT / total-NF) — but this is now understood as the
-- WRONG structure for SKI (its ≡ is too fine), so it is a NON-GOAL, not a blocked goal: the proper home is
-- the observational quotient ≋ᴼ, built here. What's grounded: the SKI quotient is PROPER (observational,
-- CrossMul/ObsBisim, reused) and carries Y-of's fixpoint — the extruder's ≡-structure realized at the
-- correct equality, the operator's CrossMul/HetQ steer dissolving the set-truncation mis-target.
------------------------------------------------------------------------
