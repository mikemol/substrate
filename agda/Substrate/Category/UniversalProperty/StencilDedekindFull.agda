{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilDedekindFull — ⟡dedekind-full-pointfree: the
-- COMPLETE point-free ≈ of maps-preserve-meets, BOTH directions via allegory operations, no
-- witness-casing. Pairs the point-free ⊇ (199, Dedekind + determinism collapse) with a
-- point-free ⊆ (monotonicity via ⨾-mono-r + the meet GLB), completing the abstract assembly.
--
-- The ⊆ direction is now ALSO point-free: f⨾(S∧T) ⊆ f⨾S and ⊆ f⨾T (⨾-mono-r on the meet
-- projections), so ⊆ (f⨾S)∧(f⨾T) by ∧-greatest — the GLB universal property, no split.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilDedekindFull where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.Allegory
  using (_⨾_; _∧_; _⊆_; _≈_; ∧-⊆ˡ; ∧-⊆ʳ; ∧-greatest)
open import Substrate.Category.Allegory.Maps using (deterministic)
open import Substrate.Category.UniversalProperty.StencilDedekindCollapse
  using (map-meet-⊇-pointfree)
open import Substrate.Category.Allegory.Mono using (⨾-mono-r)

module _ {A B C : Set} (f : A → B → Set) (det : deterministic f) where

  -- ① THE ⊆ DIRECTION, POINT-FREE (monotonicity via the GLB, no witness-split): f⨾(S∧T)
  -- lands below each of f⨾S, f⨾T (⨾-mono-r on the projections), so below their meet.
  map-meet-⊆-pointfree : (S T : B → C → Set) → (f ⨾ (S ∧ T)) ⊆ ((f ⨾ S) ∧ (f ⨾ T))
  map-meet-⊆-pointfree S T =
    ∧-greatest (⨾-mono-r f (∧-⊆ˡ S T)) (⨾-mono-r f (∧-⊆ʳ S T))

  -- ② THE FULL POINT-FREE ≈: maps preserve meets, BOTH directions via allegory ops.
  map-preserves-meet-pointfree : (S T : B → C → Set) → (f ⨾ (S ∧ T)) ≈ ((f ⨾ S) ∧ (f ⨾ T))
  map-preserves-meet-pointfree S T =
    map-meet-⊆-pointfree S T , map-meet-⊇-pointfree f det S T

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — maps preserve meets, fully point-free, both hands): the ≈
-- of maps-preserve-meets is now assembled ENTIRELY abstractly (map-preserves-meet-pointfree)
-- — the ⊆ hand via the meet GLB (∧-greatest of the two ⨾-mono-r projections), the ⊇ hand via
-- the Dedekind form + determinism collapse (199). NO witness-casing on either side. This
-- completes the chirality picture at the proof level (198/199): the two directions are the
-- two chiral hands, both now proven point-free through the allegory's own operations —
-- monotonicity the free hand (GLB), Dedekind the structured hand (modular + the map). The
-- concrete version (197) and this point-free version prove the SAME ≈; the either/or
-- "concrete vs point-free" dissolves into the two proofs of one fact, both machine-checked.
-- The modular-law picture of the stencil is COMPLETE and FULLY assembled: agree the
-- equivalence (192-196), ⊗ the map (197 concrete, 198 chiral, 199 ⊇-pointfree, here ≈-pointfree).
------------------------------------------------------------------------
