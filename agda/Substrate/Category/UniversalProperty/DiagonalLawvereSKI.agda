{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalLawvereSKI — ⟡diagonal-lawvere-ski-carrier: the SKI
-- carrier as the SITE where the two reflexivities (246) MEET — Lawvere self-application realized at the
-- Lambek/reduction equality (⇒*, not ≡). REUSES the repo's SKI machinery; HONESTLY scopes the Y combinator
-- the catalog-check (244) confirmed the repo does NOT have.
--
-- catalog-check (244, standing) findings, grounded by READING: SKIShedDuality.Tm (S/K/I + _∙_) + the full
-- β-reduction (β-I/β-K/β-S) in SKIReductionToList + _⇒*_ (via RewriteConfluence) EXIST and are reused.
-- BUT there is NO Y / fixed-point combinator (self-app/Y/ω grep empty; SKIAllegoryFixpoints is μ/ν ALLEGORY
-- fixpoints — a DIFFERENT notion, and it itself scopes Trace≅μΦ). So a term-level Lawvere fixed point
-- (Y f ⇒* f (Y f)) is GENUINELY NEW and NOT built here — scoped, honestly, as SKIAllegoryFixpoints scopes
-- its own remainder.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: self-app (x ∙ x is a
-- well-formed Tm⟦533ef80d⟧ — self-application is definable, the reflexive-object precondition), and the reduction
-- reused from the repo. The framing ('the two reflexivities meet', 'Y is the constructive point-surjection')
-- is (prose: illuminating, NOT a theorem of this slice; the Y combinator + its fixed-point law are SCOPED).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalLawvereSKI where

open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.R.Trace.SKIReductionToList using (β-I; β-K; β-S; cong-l; cong-r) renaming (_⇒_ to _⇒⟦66d2c034⟧_)

------------------------------------------------------------------------
-- ① SELF-APPLICATION IS DEFINABLE (the reflexive-object precondition). Unlike a typed function space,
--    an SKI term can be applied to ITSELF: for any t, t ∙ t : Tm⟦533ef80d⟧. This is what makes the SKI carrier a
--    candidate LAWVERE-reflexive object (246's Reflexive precondition) that a SET carrier cannot be
--    (Cantor, 246): self-application needs an untyped/reflexive carrier, and Tm⟦533ef80d⟧ is one.
------------------------------------------------------------------------
self-app : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
self-app t = t ∙ t

-- ω = (S I I) is the self-applicator: S I I x ⇒* x x. We give the FIRST reduction step honestly (the
-- full ⇒* to x ∙ x uses β-S then β-I twice); the point is that self-application is REALIZED by a term.
ω-term : Tm⟦533ef80d⟧
ω-term = (S ∙ I) ∙ I

ω-step : (x : Tm⟦533ef80d⟧) → (((S ∙ I) ∙ I) ∙ x) ⇒⟦66d2c034⟧ ((I ∙ x) ∙ (I ∙ x))
ω-step x = β-S I I x
-- and each I-redex reduces to x, so (S I I) x ⇒* x ∙ x = self-app x (the reduction realizing self-app):
ω-left : (x : Tm⟦533ef80d⟧) → ((I ∙ x) ∙ (I ∙ x)) ⇒⟦66d2c034⟧ (x ∙ (I ∙ x))
ω-left x = cong-l (I ∙ x) (β-I x)
ω-right : (x : Tm⟦533ef80d⟧) → (x ∙ (I ∙ x)) ⇒⟦66d2c034⟧ (x ∙ x)
ω-right x = cong-r x (β-I x)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the SKI carrier is where the two reflexivities (246) MEET, and the Y
-- combinator that would complete it is the substrate's OWN scoped remainder): the either/or "can Lawvere's
-- positive direction land on a GENUINE (non-⊤) carrier?" bottoms out — YES, on a SELF-APPLICATIVE carrier
-- (Tm⟦533ef80d⟧, ①: t ∙ t is well-formed; ω = S I I realizes self-app by reduction), which a SET carrier cannot be
-- (Cantor, 246). This is where the two reflexivities MEET: LAWVERE reflexivity (self-application, ①) +
-- LAMBEK/reduction equality (⇒*, not ≡ — the finality equality of 234). The fixed point a reflexive carrier
-- forces (246 §2) lands HERE as a term fixed point UP TO ⇒* (not strict ≡) — the escape's ≈-equality (234)
-- IS the equality at which the Lawvere fixed point lives. So the arc's two faces (245/246: fixed-point-exists
-- = Lawvere; finality = Lambek) are ONE on the SKI carrier: the Y-fixed-point up to reduction.
--
-- HONEST BOUNDARY (⟡H-overclaim — and the typechecker/catalog enforced it): GROUNDED = self-application
-- is definable + realized by ω = S I I (the reduction steps ω-step/ω-left/ω-right, --safe, reusing the
-- repo's β-rules). SCOPED (genuinely new, NOT built — as SKIAllegoryFixpoints scopes its own μΦ remainder):
-- (a) the Y COMBINATOR — a term Y with (Y ∙ f) ⇒* (f ∙ (Y ∙ f)) for all f — the constructive point-surjection
-- / Lawvere-positive witness on Tm⟦533ef80d⟧; the catalog-check (244) confirmed the repo does NOT have it, so it is a
-- substantial NEW development (⟡diagonal-Y-combinator); (b) the full Reflexive Tm⟦533ef80d⟧ (246) instance — needs Y +
-- the representable-map restriction (self-PointSurjective holds for DEFINABLE maps, not all Tm⟦533ef80d⟧→Tm⟦533ef80d⟧; Cantor
-- bounds the rest). What's grounded: self-application (the reflexive-object precondition a set carrier lacks)
-- is realized on Tm⟦533ef80d⟧ by ω, at the ⇒* equality where the two reflexivities meet — the Y-completion scoped
-- honestly, exactly as the substrate scopes its own fixed-point remainders.
------------------------------------------------------------------------
