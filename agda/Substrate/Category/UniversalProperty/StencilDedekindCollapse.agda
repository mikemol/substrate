{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilDedekindCollapse — ⟡dedekind-collapse: the
-- FULLY POINT-FREE meet-preservation ⊇, assembling the Dedekind landing (meet-dedekind,
-- 198) with the determinism collapse (f†⨾f ⊆ idR). This CLOSES THE SEAM between 197 (which
-- proved ⊇ CONCRETELY, determinism forcing the shared middle) and 198 (which exposed the
-- Dedekind LANDING f⨾(S ∧ (f†⨾f⨾T)) abstractly): here the landing is COLLAPSED to f⨾(S∧T)
-- point-free — the genuine irreducibly-abstract modular use, no witness-casing.
--
-- THE CHAIN (point-free): (f⨾S)∧(f⨾T)
--   ⊆ f⨾(S ∧ (f†⨾(f⨾T)))     [meet-dedekind, 198 — the Dedekind form]
--   ⊆ f⨾(S ∧ T)              [f†⨾(f⨾T) ⊆ T via ⨾-assoc, f†⨾f ⊆ idR (determinism), idR⨾T ≈ T]
-- The residual term f†⨾(f⨾T) collapses to T BECAUSE f is a map (f†⨾f ⊆ idR) — the modular
-- law (via the Dedekind form) + determinism, assembled abstractly.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilDedekindCollapse where

open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Category.Allegory
  using (_⨾_; _∧_; _†; _⊆_; _≈_; idR; ⊆-trans;
         ⨾-assoc; ⨾-identityˡ; ∧-⊆ˡ; ∧-⊆ʳ; ∧-greatest)
open import Substrate.Category.Allegory.Maps using (deterministic)
open import Substrate.Category.Allegory.Mono using (⨾-mono-l; ⨾-mono-r; ∧-mono-r; det→incl)
open import Substrate.Category.UniversalProperty.StencilDedekind using (meet-dedekind)

------------------------------------------------------------------------
-- ② THE COLLAPSE + THE POINT-FREE ⊇.
------------------------------------------------------------------------
module _ {A B C : Set} (f : A → B → Set) (det : deterministic f) where

  -- the residual term collapses: f† ⨾ (f ⨾ T) ⊆ T, via assoc → determinism → identity.
  residual-collapse : (T : B → C → Set) → ((f †) ⨾ (f ⨾ T)) ⊆ T
  residual-collapse T =
    ⊆-trans (proj₂ (⨾-assoc (f †) f T))                    -- f†⨾(f⨾T) ⊆ (f†⨾f)⨾T
      (⊆-trans (⨾-mono-l T (det→incl f det))               -- (f†⨾f)⨾T ⊆ idR⨾T
               (proj₁ (⨾-identityˡ T)))                     -- idR⨾T ⊆ T

  -- THE POINT-FREE ⊇: assemble meet-dedekind (198) + the collapse. No witness-casing.
  map-meet-⊇-pointfree : (S T : B → C → Set) → ((f ⨾ S) ∧ (f ⨾ T)) ⊆ (f ⨾ (S ∧ T))
  map-meet-⊇-pointfree S T =
    ⊆-trans (meet-dedekind f S T)                          -- ⊆ f⨾(S ∧ (f†⨾(f⨾T)))
            (⨾-mono-r f (∧-mono-r S (residual-collapse T)))  -- ⊆ f⨾(S ∧ T)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the seam CLOSED; the abstract modular use assembled): the
-- point-free ⊇ (map-meet-⊇-pointfree) assembles the Dedekind landing (meet-dedekind, 198,
-- the chiral twin of monotonicity) with the determinism collapse (residual-collapse: f†⨾f ⊆
-- idR forces f†⨾(f⨾T) ⊆ T). This CLOSES the seam between 197 (⊇ CONCRETELY via determinism
-- forcing the shared middle) and 198 (the Dedekind landing exposed abstractly): 197 and 199
-- prove the SAME ⊇, one by witness-casing, one point-free — they meet, and the point-free
-- one is the genuine irreducibly-abstract modular use (the modular law via Dedekind + the
-- map's determinism, no unfolding). The derived glue (⨾-mono-l/r, ∧-mono-r, det→incl) is the
-- monotonicity the substrate did not name — now assembled. So the modular-law picture is
-- complete AND its abstract assembly is machine-checked: agree the equivalence (192-196,
-- modular = backdrop), ⊗ the map (197 concrete, 198 chiral, 199 point-free abstract). The
-- either/or "concrete determinism vs abstract modular" dissolves: they are the two proofs of
-- ONE ⊇, meeting in the middle — the chirality (198) at the proof level, resolved.
------------------------------------------------------------------------
