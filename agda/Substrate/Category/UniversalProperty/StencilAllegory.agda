{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilAllegory — ⟡stencil-allegory: the COMMUTE
-- of the stencil's cospan, in the ALLEGORY. The cospan A →(embA) R ←(embB) B (StencilAbstract,
-- 192) is itself an either/or — the two legs, the A-vs-B direction — and it COMMUTES: the
-- cross-relation `agrees` is a genuine allegory Rel, and its symmetry (agrees-sym, 192) IS
-- self-converse (R † ≈ R), the commute that dissolves the directional either/or.
--
-- THE ALLEGORY (grounded, Category.Allegory) is the category-theoretic name for the pattern:
-- Rel A B = A → B → Set (proof-relevant relations); converse _† ((R †) b a = R a b, the
-- fiber-flip, †-invol/†-comp); meet _∧_ (GLB); composition _⨾_; and graph f (FUNCTIONS ARE
-- MAPS — the map-vs-relation either/or, isMap = entire × deterministic, "Φ landing on a
-- singleton"). Every either/or the stencil touched lives here: relation-vs-function, the two
-- cospan legs (a relation and its converse), the refinement order ⊑ᶠ ⊆. The allegory is the
-- common structure — the commute is a RELATION being self-converse / composing with its
-- converse, machine-checked.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilAllegory where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.Allegory using (Rel; _†; _≈_; _⊆_; idR; _⨾_)

------------------------------------------------------------------------
-- ① THE STENCIL'S CROSS-RELATION AS AN ALLEGORY Rel. Given the cospan data (two framing-
-- carriers A, B crossing into R via ⊗, with frame-relation ≈R), the agreement is a
-- relation on the framed objects. We realize it directly as a Rel and show the COMMUTE.
------------------------------------------------------------------------
module _ {F : Set}                              -- the framed-object carrier (Framed, 192)
         (agree : Rel F F)                       -- the cross-equality `agrees` as a Rel
         (agree-sym : {p q : F} → agree p q → agree q p)   -- agrees-sym (192)
  where

  ------------------------------------------------------------------------
  -- THE COMMUTE (the either/or's dissolution): the cross-relation is SELF-CONVERSE —
  -- agree † ≈ agree. The A-vs-B / direction either/or commutes: reading the relation
  -- forward (p agrees q) or backward (its converse) gives the SAME relation. This is the
  -- allegory statement of "the cospan commutes" — its two legs' relation is symmetric,
  -- an involution-fixed point (R † = R = a coreflexive/symmetric allegory relation).
  ------------------------------------------------------------------------
  agree-self-converse : (agree †) ≈ agree
  agree-self-converse = (λ p q h → agree-sym h) , (λ p q h → agree-sym h)
  -- ⊆ both ways (≈): (agree †) p q = agree q p, and agree-sym flips it — so agree † ≈ agree.

------------------------------------------------------------------------
-- ② THE MAP-VS-RELATION either/or ALSO commutes (grounded, Maps): a FUNCTION becomes a
-- relation via graph (graph f a b = f a ≡ b), an allegory MAP (entire × deterministic).
-- So "function or relation?" dissolves — a function IS a relation (its graph), the
-- degenerate coreflexive case. The stencil's ⊗/cross (a function A → B → R) and its
-- agreement-relation are the SAME allegory object at different determinism-levels.
-- (Witnessed by the substrate's graph/isMap; re-exported conceptually here.)
------------------------------------------------------------------------

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ALLEGORY is the common structure; every either/or
-- commutes in it): the operator's point — the cospan (two framings, A vs B) is another
-- either/or, and it COMMUTES. In the allegory (Category.Allegory: Rel/†/∧/⨾/graph), the
-- commute is that the stencil's cross-relation `agrees` is SELF-CONVERSE (agree † ≈ agree,
-- agree-self-converse) — the A-vs-B direction dissolves into ONE symmetric relation read
-- both ways (the converse involution). And the map-vs-relation either/or dissolves too:
-- functions ARE maps (graph, isMap), the degenerate deterministic relations. So the ALLEGORY
-- is the category-theoretic name for the whole pattern — relations, functions, spans,
-- cospans, the refinement order ⊑ᶠ, the cross ⊗, the HetQ ≈H — all as allegory morphisms,
-- and every either/or among them (relation vs function, A vs B, forward vs converse) is a
-- COMMUTE in it, not a choice. This is WHY the repo is grounded in arrow categories +
-- allegory: heterogeneous objects related through a common frame, the either/ors dissolved
-- into commutes (converse, meet, the modular law), never forcibly identified. The stencil's
-- cross-relation is a symmetric allegory relation (a groupoid, 189, = self-converse here) —
-- the commute IS the invariant.
------------------------------------------------------------------------
