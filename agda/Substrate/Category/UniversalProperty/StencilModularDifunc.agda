{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilModularDifunc — ⟡stencil-modular-difunc:
-- the stencil's cross-relation `agree` is DIFUNCTIONAL (agree ⨾ agree† ⨾ agree ≈ agree).
--
-- HONEST FINDING (the audit, continuing 195's correction pattern — the FOURTH time): for
-- the stencil's agree, difunctionality does NOT genuinely USE the modular law. agree is an
-- EQUIVALENCE (refl/sym/trans/idempotent, 192-195), and difunctionality follows DIRECTLY
-- from its structure:
--   • agree ⊆ agree ⨾ agree† ⨾ agree  (⊇)  is ALWAYS true (diagonal witnesses) — GENERIC.
--   • agree ⨾ agree† ⨾ agree ⊆ agree  (⊆)  from SYMMETRY (agree† ⊆ agree, 193) + IDEMPOTENCE
--     (agree ⨾ agree ⊆ agree, 195, applied twice) — NOT the modular law.
-- THE INVARIANT this settles: agree is an equivalence, so ALL its relational properties
-- (idempotence 195, difunctionality here) come from refl/sym/trans — the modular law (194)
-- is the ambient allegory COHERENCE, genuinely USED only on NON-equivalence relations (maps
-- — the cross ⊗ as a map, abstract setting), NOT on the equivalence agree. The recursion
-- "what does the modular law give the stencil?" BOTTOMS OUT here: nothing new for agree
-- (it's already an equivalence); the modular law is the coherence agree lives in.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilModularDifunc where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.Allegory using (Rel; _⨾_; _†; _≈_; _⊆_)

module _ {F : Set}
         (agree : Rel F F)
         (agree-refl : (p : F) → agree p p)
         (agree-sym  : {p q : F} → agree p q → agree q p)
         (agree-trans : {p q r : F} → agree p q → agree q r → agree p r)
  where

  -- symmetry as self-converse (193): agree† ⊆ agree.
  agree†⊆agree : (agree †) ⊆ agree
  agree†⊆agree p q h = agree-sym h

  ------------------------------------------------------------------------
  -- ① THE ⊇ DIRECTION, GENERIC (always true, diagonal witnesses): agree ⊆ agree ⨾ agree†
  -- ⨾ agree. Any related (p, s) factors through q = p, r = p: (agree p p, agree† p p,
  -- agree p s) — using reflexivity for the diagonal. Holds for ANY reflexive relation.
  ------------------------------------------------------------------------
  agree⊆difunc : agree ⊆ (agree ⨾ ((agree †) ⨾ agree))
  agree⊆difunc p s h = p , (agree-refl p , (p , (agree-refl p , h)))
  --                    q=p: agree p p ; then r=p: agree† p p (= agree p p) , agree p s.

  ------------------------------------------------------------------------
  -- ② THE ⊆ DIRECTION, from SYMMETRY + TRANSITIVITY (NOT modular): agree ⨾ agree† ⨾ agree
  -- ⊆ agree. Unfold: (q, agree p q, (r, agree† q r, agree r s)) → agree p s. agree† q r =
  -- agree r q; sym → agree q r; trans (p q) (q r) → agree p r; trans (p r) (r s) → agree p s.
  ------------------------------------------------------------------------
  difunc⊆agree : (agree ⨾ ((agree †) ⨾ agree)) ⊆ agree
  difunc⊆agree p s (q , (pq , (r , (rq , rs)))) =
    agree-trans (agree-trans pq (agree-sym rq)) rs
    -- pq : agree p q ; rq : agree† q r = agree r q ; agree-sym rq : agree q r ;
    -- agree-trans pq (sym rq) : agree p r ; agree-trans _ rs : agree p s.

  ------------------------------------------------------------------------
  -- ③ DIFUNCTIONALITY: agree ⨾ agree† ⨾ agree ≈ agree (⊆ from sym+trans, ⊇ generic).
  ------------------------------------------------------------------------
  agree-difunctional : (agree ⨾ ((agree †) ⨾ agree)) ≈ agree
  agree-difunctional = difunc⊆agree , agree⊆difunc

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — agree's properties ALL come from refl/sym/trans; the
-- modular law is the backdrop, genuinely used only on non-equivalence maps): the stencil's
-- cross-relation agree is DIFUNCTIONAL (agree-difunctional) — and, continuing 195's honest
-- correction (the FOURTH), this does NOT use the modular law: the ⊇ is generic (diagonal,
-- reflexivity), the ⊆ is symmetry (193) + transitivity (the hinge) via the equivalence
-- structure. So BOTH idempotence (195) and difunctionality (here) of agree follow from its
-- being an EQUIVALENCE (refl/sym/trans) — NOT from the modular law. The recursion "what
-- fresh property does the modular law give the stencil's agree?" BOTTOMS OUT: nothing —
-- agree is already the strongest relational structure (an equivalence), self-sufficient
-- from refl/sym/trans; the modular law (194) is the ambient allegory COHERENCE agree lives
-- IN, genuinely USED only on NON-equivalence relations (maps — the cross ⊗ as a function
-- in the abstract allegory, ⟡stencil-modular-map). The either/or "difunctionality via
-- modular vs via equivalence" dissolves: for an equivalence it is via the equivalence
-- structure; the modular law is where that structure COHERES, not a source of new
-- properties. agree is a difunctional idempotent symmetric reflexive transitive relation:
-- a full allegory equivalence, and every consequence flows from that — the settling point.
------------------------------------------------------------------------
