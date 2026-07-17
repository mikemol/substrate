{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilModularApp — ⟡stencil-modular-app: the
-- stencil's cross-relation `agree` is IDEMPOTENT (agree ⨾ agree ≈ agree) — the concrete
-- consequence of its allegory structure. HONEST SCOPE-CORRECTION of 194's residue phrasing
-- ("use the modular law to derive idempotence"): idempotence decomposes into two directions
-- with DISTINCT sources, and NEITHER is the modular law itself —
--   • agree ⊆ agree ⨾ agree  (⊇)  follows from REFLEXIVITY (agrees-refl, 192, GENERIC).
--   • agree ⨾ agree ⊆ agree  (⊆)  IS TRANSITIVITY (the per-instance hinge, 192).
-- The modular law (194) is the ambient allegory COHERENCE in which ⨾/∧/† cohere — it is
-- the backdrop, not the deriver. So idempotence = refl (⊇, generic) ⊕ trans (⊆, hinge);
-- the either/or "generic vs per-instance idempotence" dissolves into WHICH DIRECTION.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilModularApp where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.Allegory using (_⨾_; _≈_; _⊆_)

module _ {F : Set}
         (agree : F → F → Set)
         (agree-refl : (p : F) → agree p p)
         (agree-sym  : {p q : F} → agree p q → agree q p)
  where

  ------------------------------------------------------------------------
  -- ① THE ⊇ DIRECTION, GENERIC (from reflexivity): agree ⊆ agree ⨾ agree. Any related
  -- pair (p, r) factors through q = p — (agree p p, agree p r). NO hinge, NO modular law.
  ------------------------------------------------------------------------
  agree-below-square : agree ⊆ (agree ⨾ agree)
  agree-below-square p r h = p , (agree-refl p , h)

  ------------------------------------------------------------------------
  -- ② THE ⊆ DIRECTION, PER-INSTANCE (from transitivity — the hinge): agree ⨾ agree ⊆
  -- agree. This is exactly transitivity; supplied by the concrete stencil (the hinge, as
  -- HetBasis's trans is the cross-cancellation). Given it, idempotence follows.
  ------------------------------------------------------------------------
  module _ (agree-trans : {p q r : F} → agree p q → agree q r → agree p r) where

    square-below-agree : (agree ⨾ agree) ⊆ agree
    square-below-agree p r (q , (pq , qr)) = agree-trans pq qr

    -- IDEMPOTENCE: agree ⨾ agree ≈ agree (⊆ from trans, ⊇ from refl).
    agree-idempotent : (agree ⨾ agree) ≈ agree
    agree-idempotent = square-below-agree , agree-below-square

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — idempotence = refl ⊕ trans, in the modular allegory): the
-- stencil's cross-relation agree is IDEMPOTENT (agree ⨾ agree ≈ agree) — and the honest
-- decomposition is: the ⊇ direction (agree ⊆ agree ⨾ agree) is GENERIC from reflexivity
-- (agree-below-square, no hinge); the ⊆ direction (agree ⨾ agree ⊆ agree) IS transitivity,
-- the per-instance hinge (square-below-agree). So idempotence = refl (⊇) ⊕ trans (⊆). This
-- CORRECTS 194's residue phrasing "use the modular law to derive idempotence": the modular
-- law (194) is the ambient allegory COHERENCE (⨾/∧/† cohere), NOT the deriver — idempotence
-- follows from refl+trans specifically, and audit shows the modular law is the backdrop.
-- Combined with symmetry (agree-sym, 193) and reflexivity, an idempotent symmetric
-- reflexive relation IS an equivalence — the groupoid (189) at the relation level: agree is
-- a coreflexive-closed equivalence in the modular allegory (191/192/193/194). The either/or
-- "idempotence generic vs per-instance" dissolves into WHICH DIRECTION: ⊇ generic (refl),
-- ⊆ per-instance (trans) — the same refl/sym-generic, trans-per-instance split as HetBasis's
-- CrossEq (192). So the stencil's agree, across the arc, is: refl+sym generic (192), self-
-- converse commute (193), modular-coherent (194), idempotent = equivalence (here) — a full
-- allegory equivalence, the invariant the recursion settles on.
------------------------------------------------------------------------
