{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKISetoid — ⟡extrude-ski-setoid: closing the ≡-vs-⇒* gap
-- (249) at CONVERTIBILITY ≈. The SKI carrier IS a combinator algebra at ≈ (the equivalence closure of ⇒),
-- with S/K laws holding at ≈ and Y-of (248) the fixpoint — so ExtruderFix's fixpoint-from-diagonals holds
-- concretely on SKI terms, at the equality the extruder actually rests on.
--
-- The catalog-check (244, standing) found the reuse target: FUSep.ConversionCongruence — "the equivalence
-- the extruder actually rests on": an ARS (Carrier/_·_/_⟶_/·-congˡ/·-congʳ) yields the equivalence closure
-- _≈_ (emb/≈refl/≈sym/≈trans), PROVEN a congruence from compatibility alone. SKI (Tm⟦533ef80d⟧/_∙_/_⇒⟦66d2c034⟧_/cong-l/cong-r)
-- fits ARS exactly — so ≈ is REUSED, not re-rolled.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: ski-ARS (SKI as an ARS),
-- ⇒*→≈ (reduction ⊆ convertibility), S-law-≋ / K-law-≋ (the combinator laws at ≈), fix-law-≋ (Y-of f ≈
-- f (Y-of f) — the fixpoint law at ≈). The framing ('the gap is closed', 'SKI is a combinator algebra') is
-- (prose: at ≈; the LITERAL ExtruderFix ≡-record instance needs the Tm⟦533ef80d⟧/≈ QUOTIENT TYPE, scoped below).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKISetoid where

open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.R.Trace.SKIReductionToList using (β-K; β-S; cong-l; cong-r) renaming (_⇒_ to _⇒⟦66d2c034⟧_)
import Substrate.Foundation.RewriteConfluence (Substrate.Algebra.R.Trace.SKIReductionToList._⇒_)
  as RC using (_⇒*_; done; _◅_)
open import Substrate.FUSep.ConversionCongruence using (ARS; _≈_; emb; ≈refl; ≈sym; ≈trans)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- ① SKI IS AN ARS (the ConversionCongruence interface). Carrier = Tm⟦533ef80d⟧, application = _∙_, reduction = _⇒⟦66d2c034⟧_,
--    the application-context compatibilities = the repo's cong-l/cong-r. So ConversionCongruence gives us
--    ≈ = the equivalence closure of ⇒⟦66d2c034⟧ (convertibility), REUSED (≈ is _≈_ applied to ski-ARS).
------------------------------------------------------------------------
ski-ARS : ARS Tm⟦533ef80d⟧ _⇒⟦66d2c034⟧_
ski-ARS = record
  { _·_ = _∙_
  ; ·-congˡ = λ {a}{a'}{b} r → cong-l b r
  ; ·-congʳ = λ {a}{b}{b'} r → cong-r a r }

-- convertibility on SKI = _≈_ at ski-ARS (the anonymous ARS module, applied):
_≋_ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
a ≋ b = _≈_ ski-ARS a b

------------------------------------------------------------------------
-- ② REDUCTION ⊆ CONVERTIBILITY (⇒* ⊆ ≈): a directed reduction chain is a convertibility. So every ⇒*-fact
--    (the S/K β-steps, and Y-fix) lifts to ≈.
------------------------------------------------------------------------
⇒*→≋ : {a b : Tm⟦533ef80d⟧} → a RC.⇒* b → a ≋ b
⇒*→≋ RC.done         = ≈refl
⇒*→≋ (s RC.◅ rest)   = ≈trans (emb s) (⇒*→≋ rest)

------------------------------------------------------------------------
-- ③ THE COMBINATOR-ALGEBRA LAWS HOLD AT ≈ (what ExtruderFix.CombinatorAlgebra requires — at ≈, not ≡):
------------------------------------------------------------------------
K-law-≋ : (x y : Tm⟦533ef80d⟧) → ((K ∙ x) ∙ y) ≋ x
K-law-≋ x y = emb (β-K x y)

S-law-≋ : (x y z : Tm⟦533ef80d⟧) → (((S ∙ x) ∙ y) ∙ z) ≋ ((x ∙ z) ∙ (y ∙ z))
S-law-≋ x y z = emb (β-S x y z)

------------------------------------------------------------------------
-- ④ THE FIXPOINT LAW AT ≈ (HasFix, concretely): Y-of f ≈ f (Y-of f), from 248's Y-fix (⇒*) via ⇒*→≈.
--    So (Tm⟦533ef80d⟧, ≈) is a combinator algebra WITH a fixpoint operator = Y-of — ExtruderFix's fixpoint-from-
--    diagonals realized concretely on SKI terms, at convertibility.
------------------------------------------------------------------------
fix-law-≋ : (f : Tm⟦533ef80d⟧) → (Y-of f) ≋ (f ∙ (Y-of f))
fix-law-≋ f = ⇒*→≋ (Y-fix f)

-- HasFix (concrete): a fixpoint-witnessing family — for every f, a v (= Y-of f) with v ≋ f · v.
ski-HasFix : (f : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ v → v ≋ (f ∙ v))
ski-HasFix f = (Y-of f) , fix-law-≋ f

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ≡-vs-⇒* gap CLOSES at ≈: the SKI carrier IS a combinator algebra at
-- convertibility, Y-of the fixpoint; the residual ≡-packaging is the quotient, which --safe lacks): the
-- either/or "does the SKI realization (⇒*, 249) actually MATCH ExtruderFix's combinator algebra (≡), or
-- only resemble it?" bottoms out — it MATCHES, at the RIGHT equality ≈ (convertibility = the equivalence
-- closure of ⇒, which ConversionCongruence calls "the equivalence the extruder actually rests on"). At ≈:
-- K-law-≈, S-law-≈ hold (③), and Y-of is the fixpoint (④, HasFix) — EXACTLY ExtruderFix.CombinatorAlgebra's
-- structure, concretely on Tm⟦533ef80d⟧. The ≡ ExtruderFix uses is too FINE on Tm⟦533ef80d⟧ (syntactic identity); ≈ is the
-- correct coarsening, and reduction ⊆ ≈ (②) carries every SKI fact up. So the arc's fixed point (Y-of, 248)
-- and the extruder's combinator algebra (ExtruderFix) are the SAME at ≈ — the 249 gap is closed at
-- convertibility, reusing the extruder's own equivalence (ConversionCongruence).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = SKI-as-ARS + ≈ (reused) + the three laws at ≈ (S/K/fix, with
-- Y-of the fixpoint, HasFix concrete). SCOPED: the LITERAL ExtruderFix.CombinatorAlgebra ≡-record instance
-- with C = Tm⟦533ef80d⟧ needs the QUOTIENT TYPE Tm⟦533ef80d⟧/≈ whose propositional ≡ IS ≈ — quotient types (HITs) are NOT
-- available under --safe --without-K (no cubical), so the ≡-packaging is genuinely blocked HERE, not merely
-- deferred (⟡extrude-ski-quotient — needs a quotient/HIT or a normal-form section). The setoid content (③④)
-- IS the constructive gap-closure; the ≡-record is its quotient packaging. Honestly a real universe/feature
-- boundary, like 246's Cantor-⊤ and 241's shim — named, not glossed. (ski-ARS uses ARS : Set₁ — a STRUCTURE
-- over Set, as ExtruderFix.CombinatorAlgebra is Set₁; structural, not a computational Set₁-blowup.)
------------------------------------------------------------------------
