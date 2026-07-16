{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalYClosed — ⟡diagonal-Y-closed:
-- the CLOSED fixed-point combinator on the SKI carrier — a single term
-- Θ : Tm⟦533ef80d⟧ with (Θ ∙ f) ⇒* (f ∙ (Θ ∙ f)) for every f. This packages
-- DiagonalYCombinator's fixed-point OPERATOR (Y-of : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧, a
-- meta-function) as an internal TERM, closing the standing ⟡diagonal-Y-closed residue.
--
-- WHY Θ (Turing) NOT Y (Curry): the substrate's fixed-point equality is the
-- one-directional reduction `⇒*` (the Lambek/reduction equality), NOT `=β`
-- convertibility. Curry's Y gives Y f =β f (Y f) (both reduce to a common term)
-- but NOT Y f ⇒* f (Y f). Turing's Θ = A ∙ A with A ∙ x ∙ y ⇒* y ∙ (x ∙ x ∙ y)
-- gives the ONE-directional (Θ ∙ f) ⇒* (f ∙ (Θ ∙ f)) — forced by the ⇒*-law.
--
-- CONSTRUCTION: A is the bracket-abstraction of λx.λf. f (ω x f), reusing the
-- committed ω = S I I (DiagonalLawvereSKI.ω-term, ω ∙ x ⇒* x ∙ x) so the inner
-- self-application x ∙ x is discharged by the existing 3-step ω reduction rather
-- than re-derived. Every reduction step is an explicit ◅-chain over the repo's
-- β-rules (β-I/β-K/β-S/cong-l/cong-r) + RewriteConfluence's _⇒*_/_++*_.
--
-- HONEST BOUNDARY (kept, do NOT force): this does NOT unlock the full Reflexive
-- Tm⟦533ef80d⟧ — total point-surjection onto ALL Tm⟦533ef80d⟧→Tm⟦533ef80d⟧ is
-- Cantor-FALSE, and the fixed point is up-to-⇒* not strict ≡. Θ is the internal-
-- term packaging + makes the Turing-vs-Curry (⇒*-vs-=β) distinction explicit; the
-- deeper boundary stays scoped, as DiagonalLawvereSKI/DiagonalYCombinator scope it.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalYClosed where

open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.R.Trace.SKIReductionToList using (β-I; β-K; β-S; cong-l; cong-r)
open import Substrate.Foundation.RewriteConfluence
  (Substrate.Algebra.R.Trace.SKIReductionToList._⇒_) using (_⇒*_; done; _◅_; _++*_)
open import Substrate.Category.UniversalProperty.DiagonalLawvereSKI
  using (ω-term; ω-step; ω-left; ω-right)

------------------------------------------------------------------------
-- ⓪ Congruence lifts of the multistep closure (the standard helpers): reduce a
--    subterm on the LEFT / RIGHT of an application by lifting each step.
------------------------------------------------------------------------
under-l : {a a' : Tm⟦533ef80d⟧} (g : Tm⟦533ef80d⟧) → (a ⇒* a') → ((a ∙ g) ⇒* (a' ∙ g))
under-l g done      = done
under-l g (r ◅ rs) = cong-l g r ◅ under-l g rs

under-r : (f : Tm⟦533ef80d⟧) {a a' : Tm⟦533ef80d⟧} → (a ⇒* a') → ((f ∙ a) ⇒* (f ∙ a'))
under-r f done      = done
under-r f (r ◅ rs) = cong-r f r ◅ under-r f rs

------------------------------------------------------------------------
-- ① THE PER-x/f RECURSOR A = bracket-abstraction of λx.λf. f (ω x f).
--    A = S (K (S I)) (S (S (K S) (S (K K) (S (K ω) I))) (K I)).
--    Its spec (proved below): A ∙ x ∙ f ⇒* f ∙ ((ω ∙ x) ∙ f), and ω ∙ x ⇒* x ∙ x,
--    so A ∙ x ∙ f ⇒* f ∙ (x ∙ x ∙ f) — the Turing recursor.
------------------------------------------------------------------------
A : Tm⟦533ef80d⟧
A = (S ∙ (K ∙ (S ∙ I)))
  ∙ ((S ∙ ((S ∙ (K ∙ S)) ∙ ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I)))) ∙ (K ∙ I))

-- the intermediate normal form of A ∙ x (before applying f):  λf. f (ω x f).
inner : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧
inner x = (S ∙ I) ∙ ((S ∙ (K ∙ (ω-term ∙ x))) ∙ I)

------------------------------------------------------------------------
-- ② A ∙ x ⇒* inner x — the 11-step outer bracket-abstraction unfold (all
--    reductions at the head of A ∙ x; each K/S contracts one constant).
------------------------------------------------------------------------
Ax-reduces : (x : Tm⟦533ef80d⟧) → (A ∙ x) ⇒* (inner x)
Ax-reduces x =
  -- A x = S P Q x ⇒ (P x)(Q x)
  β-S (K ∙ (S ∙ I))
      ((S ∙ ((S ∙ (K ∙ S)) ∙ ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I)))) ∙ (K ∙ I)) x
  -- P x = K (S I) x ⇒ S I
  ◅ cong-l (((S ∙ ((S ∙ (K ∙ S)) ∙ ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I)))) ∙ (K ∙ I)) ∙ x)
           (β-K (S ∙ I) x)
  -- Q x = S Q1 (K I) x ⇒ (Q1 x)((K I) x)
  ◅ cong-r (S ∙ I)
           (β-S ((S ∙ (K ∙ S)) ∙ ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I))) (K ∙ I) x)
  -- (K I) x ⇒ I
  ◅ cong-r (S ∙ I)
           (cong-r (((S ∙ (K ∙ S)) ∙ ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I))) ∙ x)
                   (β-K I x))
  -- Q1 x = S (K S) Q2 x ⇒ ((K S) x)(Q2 x)
  ◅ cong-r (S ∙ I)
           (cong-l I (β-S (K ∙ S) ((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I)) x))
  -- (K S) x ⇒ S
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-l (((S ∙ (K ∙ K)) ∙ ((S ∙ (K ∙ ω-term)) ∙ I)) ∙ x) (β-K S x)))
  -- Q2 x = S (K K) Q3 x ⇒ ((K K) x)(Q3 x)
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-r S (β-S (K ∙ K) ((S ∙ (K ∙ ω-term)) ∙ I) x)))
  -- (K K) x ⇒ K
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-r S (cong-l (((S ∙ (K ∙ ω-term)) ∙ I) ∙ x) (β-K K x))))
  -- Q3 x = S (K ω) I x ⇒ ((K ω) x)(I x)
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-r S (cong-r K (β-S (K ∙ ω-term) I x))))
  -- (K ω) x ⇒ ω
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-r S (cong-r K (cong-l (I ∙ x) (β-K ω-term x)))))
  -- I x ⇒ x
  ◅ cong-r (S ∙ I)
           (cong-l I (cong-r S (cong-r K (cong-r ω-term (β-I x)))))
  ◅ done

------------------------------------------------------------------------
-- ③ inner x ∙ f ⇒* f ∙ ((ω x) f) — the 5-step inner unfold.
------------------------------------------------------------------------
inner-applies : (x f : Tm⟦533ef80d⟧) → ((inner x) ∙ f) ⇒* (f ∙ ((ω-term ∙ x) ∙ f))
inner-applies x f =
  -- (S I M) f ⇒ (I f)(M f)
  β-S I ((S ∙ (K ∙ (ω-term ∙ x))) ∙ I) f
  -- I f ⇒ f
  ◅ cong-l (((S ∙ (K ∙ (ω-term ∙ x))) ∙ I) ∙ f) (β-I f)
  -- M f = S (K (ω x)) I f ⇒ ((K (ω x)) f)(I f)
  ◅ cong-r f (β-S (K ∙ (ω-term ∙ x)) I f)
  -- (K (ω x)) f ⇒ ω x
  ◅ cong-r f (cong-l (I ∙ f) (β-K (ω-term ∙ x) f))
  -- I f ⇒ f
  ◅ cong-r f (cong-r (ω-term ∙ x) (β-I f))
  ◅ done

------------------------------------------------------------------------
-- ④ THE RECURSOR SPEC: A ∙ x ∙ f ⇒* f ∙ ((ω ∙ x) ∙ f).
------------------------------------------------------------------------
A-spec : (x f : Tm⟦533ef80d⟧) → ((A ∙ x) ∙ f) ⇒* (f ∙ ((ω-term ∙ x) ∙ f))
A-spec x f = under-l f (Ax-reduces x) ++* inner-applies x f

------------------------------------------------------------------------
-- ⑤ THE CLOSED COMBINATOR Θ = A ∙ A, and its fixed-point law.
------------------------------------------------------------------------
Θ : Tm⟦533ef80d⟧
Θ = A ∙ A

-- ω ∙ A ⇒* A ∙ A = Θ, via the 3 reused ω-steps at x = A.
ω-A : (ω-term ∙ A) ⇒* (A ∙ A)
ω-A = ω-step A ◅ ω-left A ◅ ω-right A ◅ done

-- THE FIXED-POINT THEOREM: Θ ∙ f ⇒* f ∙ (Θ ∙ f), for every f, one-directional.
--   Θ ∙ f = A ∙ A ∙ f ⇒* f ∙ ((ω ∙ A) ∙ f)     [A-spec A f]
--                    ⇒* f ∙ ((A ∙ A) ∙ f) = f ∙ (Θ ∙ f)  [ω-A, lifted]
Θ-fix : (f : Tm⟦533ef80d⟧) → (Θ ∙ f) ⇒* (f ∙ (Θ ∙ f))
Θ-fix f = A-spec A f ++* under-r f (under-l f ω-A)

------------------------------------------------------------------------
-- ⑥ Smoke: the fixed-point law at f = K (a closed instance that computes).
------------------------------------------------------------------------
Θ-fix-K : (Θ ∙ K) ⇒* (K ∙ (Θ ∙ K))
Θ-fix-K = Θ-fix K

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the fixed-point OPERATOR (Y-of, a meta-function
-- Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧) is now packaged as a CLOSED TERM Θ : Tm⟦533ef80d⟧
-- with the internal fixed-point law (Θ ∙ f) ⇒* (f ∙ (Θ ∙ f)). The Turing-vs-Curry
-- fork bottoms out at the reduction equality: the ONE-directional ⇒*-law forces
-- Turing's Θ (Curry's Y gives only =β). The self-application at the core is the
-- SAME ω = S I I the carrier already realizes — Θ is A ∙ A where A wraps ω, so the
-- whole diagonal arc's positive face is one closed term with an explicit proof.
------------------------------------------------------------------------
