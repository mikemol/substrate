------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.InternalHom
--
-- UP28 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The internal hom [P, Q] in PSh(UPCategory): a presheaf whose
-- sections at U are natural transformations Yoneda(U) × P → Q.
--
-- PSh(C) is cartesian closed for any small C; the signature of the
-- internal hom lands here. Concrete construction (using the
-- naturality square) is canonical category-theoretic content.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.InternalHom where


------------------------------------------------------------------------
-- 1. Internal-hom signature.
------------------------------------------------------------------------

-- ⟡rc-deletes (⟡rerank2-floor-dissolve): the `InternalHomType` signature-stub
-- (an uninhabited, unconsumed Set₁ obligation surface — "concrete bridge
-- deferred") is DELETED. It was never a fiber-family HOLDER, just dead
-- scaffolding; when the internal-hom presheaf is actually built it will be a
-- real def (a UPPresheaf-valued construction), not a Set₁ type-alias.

-- Standard construction: [P, Q](U) = naturality-respecting maps
-- (V → U) × P(V) → Q(V) parametric in V. The Yoneda lemma gives
-- this Set explicitly. Concrete bridge deferred.

------------------------------------------------------------------------
-- 2. Capstone for UP28.
--
-- Internal-hom signature lands. UP29 supplies substrate examples.
------------------------------------------------------------------------
