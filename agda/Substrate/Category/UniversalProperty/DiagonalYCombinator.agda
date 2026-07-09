{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalYCombinator — ⟡diagonal-Y-combinator: the fixed-point
-- OPERATOR on the SKI carrier, CONSTRUCTED — Y-of : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ with Y-of f ⇒* f (Y-of f) for every f. This
-- COMPLETES Lawvere's positive direction constructively on the genuine (non-⊤) carrier (246/247): every
-- term-endomap has a fixed point UP TO ⇒* (the Lambek/reduction equality where the two reflexivities meet).
-- Catalog-confirmed genuinely-new (247: no Y in the repo). REUSES 247's ω-steps + the repo's β-rules.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: W, Y-of, Y-fix
-- (Y-of f ⇒* f (Y-of f), the fixed-point property by an explicit 5-step reduction). The framing ('the
-- escape's positive face constructed', 'the two reflexivities meet') is (prose: illuminating, NOT a
-- theorem of this slice; the CLOSED combinator Y:Tm⟦533ef80d⟧ with Y∙f⇒*f(Y∙f) — Turing Θ — is scoped below).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalYCombinator where

open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.R.Trace.SKIReductionToList using (β-I; β-K; β-S; cong-l; cong-r) renaming (_⇒_ to _⇒⟦66d2c034⟧_)
open import Substrate.Foundation.RewriteConfluence
  (Substrate.Algebra.R.Trace.SKIReductionToList._⇒_) using (_⇒*_; done; _◅_)
open import Substrate.Category.UniversalProperty.DiagonalLawvereSKI
  using (ω-term; ω-step; ω-left; ω-right)

------------------------------------------------------------------------
-- ① THE PER-f RECURSOR W f = S (K f) ω. It satisfies W f ∙ x ⇒* f (x ∙ x): S (K f) ω x ⇒⟦66d2c034⟧ (K f x)(ω x)
--    ⇒ f (ω x) ⇒* f (x x). This is λx. f (x x) in SKI — the bracket-abstraction of self-application-under-f.
------------------------------------------------------------------------
W : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
W f = (S ∙ (K ∙ f)) ∙ ω-term

------------------------------------------------------------------------
-- ② THE FIXED-POINT OPERATOR Y-of f = W f ∙ W f. This is (λx. f (x x))(λx. f (x x)) — the fixed point.
------------------------------------------------------------------------
Y-of : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
Y-of f = (W f) ∙ (W f)

------------------------------------------------------------------------
-- ③ THE FIXED-POINT THEOREM: Y-of f ⇒* f (Y-of f), by an explicit reduction chain (Lawvere-positive,
--    CONSTRUCTED). The 5 steps: β-S unfolds the outer S; β-K selects f; the ω-steps (reused, 247) reduce
--    ω(W f) ⇒* (W f)(W f) = Y-of f, lifted under cong-r f. So every f has a fixed point up to ⇒*.
------------------------------------------------------------------------
Y-fix : (f : Tm⟦533ef80d⟧) → (Y-of f) ⇒* (f ∙ (Y-of f))
Y-fix f =
  -- Y-of f = ((S (K f)) ω) (W f) ⇒⟦66d2c034⟧ ((K f)(W f)) (ω (W f))
  β-S (K ∙ f) ω-term (W f)
  -- ⇒ f (ω (W f))
  ◅ cong-l (ω-term ∙ (W f)) (β-K f (W f))
  -- ⇒* f ((W f)(W f)) = f (Y-of f), via the reused ω reduction under cong-r f
  ◅ cong-r f (ω-step (W f))
  ◅ cong-r f (ω-left (W f))
  ◅ cong-r f (ω-right (W f))
  ◅ done

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — Lawvere's positive direction is now CONSTRUCTED on the genuine carrier:
-- every term-endomap HAS a fixed point, up to ⇒*, and the fixed point is EXHIBITED (Y-of f), not merely
-- forced): the either/or "does the escape's positive face (a fixed point exists, 246 §2) actually GET
-- CONSTRUCTED on a real carrier, or only forced abstractly?" bottoms out — CONSTRUCTED. 246 gave
-- reflexive ⟹ fixed point (generic, forced); 247 gave self-application realized (ω); 248 (here) EXHIBITS
-- the fixed point: Y-of f ⇒* f (Y-of f), explicitly. This is where the arc's two faces are ONE: the
-- Lawvere fixed point (self-application, Y-of f = W f ∙ W f) lives at the Lambek/reduction equality (⇒*,
-- not ≡ — the finality equality of 234). So "the escape is a Lawvere fixed point" and "the escape is
-- finality" are the SAME fact, now constructed: the Y-fixed-point up to reduction. The whole diagonal
-- arc's positive face is grounded in one explicit term-operator with a 5-step reduction proof.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = Y-of (the fixed-point OPERATOR, a meta-function Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧) +
-- Y-fix (Y-of f ⇒* f (Y-of f), explicit, --safe, reusing 247's ω + the repo's β-rules). SCOPED: (a) the
-- CLOSED combinator — a single term Y : Tm⟦533ef80d⟧ with (Y ∙ f) ⇒* (f ∙ (Y ∙ f)) for all f (Turing's Θ in SKI) —
-- packages the operator as a term; a further bracket-abstraction development (⟡diagonal-Y-closed); (b) the
-- full Reflexive Tm⟦533ef80d⟧ instance (246) — needs the representable-map restriction (Y-of witnesses fixed points
-- for the APPLICATION action; a full PointSurjective onto all definable maps is the wider claim, Cantor-
-- bounded). What's grounded: the escape's positive face is CONSTRUCTED — every f has an exhibited fixed
-- point up to ⇒* — completing the Lawvere-positive/coinductive-escape synthesis on the SKI carrier.
------------------------------------------------------------------------
