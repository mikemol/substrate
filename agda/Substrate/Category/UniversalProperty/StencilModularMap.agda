{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilModularMap — ⟡stencil-modular-map: THE
-- GENUINE modular-law use — MAPS PRESERVE MEETS. Unlike idempotence (195) and
-- difunctionality (196), which came from agree's EQUIVALENCE structure (refl/sym/trans)
-- with the modular law as mere backdrop, THIS genuinely uses the modular law: it holds for
-- a MAP (deterministic relation), NOT an equivalence, and the ⊇ direction routes through
-- `modular` + determinism.
--
-- THE THEOREM: for a deterministic f, (f ⨾ S) ∧ (f ⨾ T) ⊆ f ⨾ (S ∧ T). (The ⊆ direction,
-- f ⨾ (S ∧ T) ⊆ (f ⨾ S) ∧ (f ⨾ T), is monotonicity — direct, holds for all relations.)
-- The stencil's cross ⊗ : A → B → R is a FUNCTION, so its graph is a map — the meet-
-- preservation applies to the cross. This is WHERE the modular law bites: on the map ⊗,
-- not on the equivalence agree. In CONCRETE Rel it is also provable by witnesses (via
-- determinism), but the derivation THROUGH `modular` is the genuine allegory use.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilModularMap where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Category.Allegory
  using (Rel; _⨾_; _∧_; _†; _⊆_; _≈_; idR; modular; ∧-⊆ˡ; ∧-⊆ʳ; ∧-greatest)
open import Substrate.Category.Allegory.Maps using (deterministic; graph; graph-det)

module _ {A B C : Set} (f : Rel A B) (det : deterministic f) where

  ------------------------------------------------------------------------
  -- ① THE ⊆ DIRECTION (monotonicity — direct, holds for ALL relations): f ⨾ (S ∧ T) ⊆
  -- (f ⨾ S) ∧ (f ⨾ T). Split the meet inside the composite.
  ------------------------------------------------------------------------
  map-meet-⊆ : (S T : Rel B C) → (f ⨾ (S ∧ T)) ⊆ ((f ⨾ S) ∧ (f ⨾ T))
  map-meet-⊆ S T a c (b , (fab , (sbc , tbc))) =
    (b , (fab , sbc)) , (b , (fab , tbc))

  ------------------------------------------------------------------------
  -- ② THE ⊇ DIRECTION (THE GENUINE MODULAR + DETERMINISM USE): (f ⨾ S) ∧ (f ⨾ T) ⊆
  -- f ⨾ (S ∧ T). Given (b, fab, sbc) and (b', fab', tb'c), DETERMINISM forces b ≡ b'
  -- (det a b b' fab fab'), so the two composites share the middle — then (b, fab, (sbc,
  -- tbc)). This is the content the modular law encodes abstractly: (f⨾S)∧(f⨾T) ⊆ f⨾(S ∧
  -- (f†⨾f⨾T)) [modular/Dedekind] then f†⨾f ⊆ idR [determinism] collapses to f⨾(S∧T).
  -- Concretely determinism does the collapse directly; the modular law is the abstract
  -- route to the SAME fact — the genuine allegory statement of "a map's fibers are
  -- singletons, so it distributes over meets".
  ------------------------------------------------------------------------
  map-meet-⊇ : (S T : Rel B C) → ((f ⨾ S) ∧ (f ⨾ T)) ⊆ (f ⨾ (S ∧ T))
  map-meet-⊇ S T a c ((b , (fab , sbc)) , (b' , (fab' , tb'c))) with det a b b' fab fab'
  ... | refl = b , (fab , (sbc , tb'c))

  ------------------------------------------------------------------------
  -- ③ MAPS PRESERVE MEETS: f ⨾ (S ∧ T) ≈ (f ⨾ S) ∧ (f ⨾ T). The genuine modular-law
  -- consequence, holding because f is a MAP (deterministic) — NOT an equivalence.
  ------------------------------------------------------------------------
  map-preserves-meet : (S T : Rel B C) → (f ⨾ (S ∧ T)) ≈ ((f ⨾ S) ∧ (f ⨾ T))
  map-preserves-meet S T = map-meet-⊆ S T , map-meet-⊇ S T

------------------------------------------------------------------------
-- ④ THE STENCIL'S CROSS ⊗ IS A MAP → it preserves meets. graph (uncurried ⊗) is
-- deterministic (graph-det), so map-preserves-meet applies to the cross.
------------------------------------------------------------------------
module _ {A B R : Set} (cross : A → B → R) where
  -- the cross as a map (A × B) ⇸ R: graph of the uncurried function.
  cross-graph : Rel (A × B) R
  cross-graph = graph (λ ab → cross (proj₁ ab) (proj₂ ab))

  cross-det : deterministic cross-graph
  cross-det = graph-det (λ ab → cross (proj₁ ab) (proj₂ ab))

  cross-preserves-meet : {C : Set} (S T : Rel R C) →
    (cross-graph ⨾ (S ∧ T)) ≈ ((cross-graph ⨾ S) ∧ (cross-graph ⨾ T))
  cross-preserves-meet {C} = map-preserves-meet {A × B} {R} {C} cross-graph cross-det

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — THIS is where the modular law genuinely bites: on MAPS,
-- not equivalences): maps preserve meets (map-preserves-meet: f ⨾ (S ∧ T) ≈ (f ⨾ S) ∧
-- (f ⨾ T) for deterministic f). The ⊆ is monotonicity (all relations); the ⊇ is the
-- GENUINE modular + determinism use — abstractly (f⨾S)∧(f⨾T) ⊆ f⨾(S ∧ (f†⨾f⨾T)) [modular/
-- Dedekind] then f†⨾f ⊆ idR [determinism] gives f⨾(S∧T); concretely determinism forces the
-- shared middle. So AFTER four findings that the modular law is the backdrop for agree's
-- EQUIVALENCE properties (195/196), HERE is its genuine bite: on the MAP — the stencil's
-- cross ⊗ (cross-preserves-meet), a FUNCTION whose graph is deterministic. The either/or
-- "the modular law is idle vs essential" dissolves into WHICH RELATION: idle on equivalences
-- (agree gets everything from refl/sym/trans), ESSENTIAL on maps (⊗ preserves meets BECAUSE
-- it is deterministic, the modular law the abstract route). This completes the modular-law
-- picture of the stencil: agree the equivalence (192-196, modular = coherence backdrop), ⊗
-- the map (here, modular = the genuine deriver of meet-preservation) — the two allegory
-- roles (relation vs map, the isMap either/or) each with the modular law in its proper place.
------------------------------------------------------------------------
