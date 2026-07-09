{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeNerveIdentitiesHi — ⟡extrude-nerve-identities-hi: the SIXTH
-- and final simplicial identity, completing 272's five. The face-degeneracy family has THREE cases by the
-- relative position of the face i and the degeneracy j; 272 grounded i<j (face-degen) and i=j, i=j+1
-- (the two collapses). This grounds the last: a face STRICTLY ABOVE the degeneracy (i > j+1) commutes past
-- it with a shifted face index —
--
--   (ds-hi)  dᵢsⱼ = sⱼdᵢ₋₁  (i > j+1)    :  delAt (suc i) (dupAt j xs) ≡ dupAt j (delAt i xs)  (suc j ≤ i)
--
-- With this, (delAt, dupAt) satisfies ALL SIX standard simplicial identities — it is a FULL simplicial-
-- operator structure, so the reduction's face/degeneracy zigzag (269 I/K faces, 270/271 S degeneracy) is a
-- completely coherent path in a genuine simplicial object.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY face-degen-hi (the sixth
-- identity, i>j+1, by induction on suc j ≤ i and xs). The framing ('completes all six; (delAt,dupAt) is a
-- full simplicial-operator structure') is (prose: the standard simplicial identities + 272).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeNerveIdentitiesHi where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.WitnessTower.SimplicialBoundary using (delAt)
open import Substrate.Category.UniversalProperty.ExtrudeNerveDegeneracy using (dupAt)

private variable A : Set

------------------------------------------------------------------------
-- (ds-hi) FACE-DEGENERACY, i > j+1: a face strictly above the degeneracy's position commutes past it, with
--    the face index dropped by one (dᵢ₋₁). The hypothesis suc j ≤ i is exactly i > j+1 for delAt (suc i).
------------------------------------------------------------------------
face-degen-hi : (i j : ℕ) → suc j ≤ i → (xs : List A) →
                delAt (suc i) (dupAt j xs) ≡ dupAt j (delAt i xs)
face-degen-hi i       j       lt      []       = refl
face-degen-hi (suc i) zero    (s≤s _) (x ∷ xs) = refl
face-degen-hi (suc i) (suc j) (s≤s p) (x ∷ xs) = cong (x ∷_) (face-degen-hi i j p xs)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — ALL SIX simplicial identities hold; (delAt, dupAt) is a FULL simplicial-
-- operator structure): 272 grounded five families (dᵢdⱼ, dⱼsⱼ=id, dⱼ₊₁sⱼ=id, sᵢsⱼ, dᵢsⱼ i<j); this grounds
-- the sixth (dᵢsⱼ = sⱼdᵢ₋₁, i>j+1, face-degen-hi). So the face-degeneracy family is COMPLETE in all three
-- position cases (i<j commute, i=j / i=j+1 collapse, i>j+1 commute), and together with dᵢdⱼ (faces) and sᵢsⱼ
-- (degeneracies) the pair (delAt, dupAt) satisfies EVERY standard simplicial identity. The reduction's
-- face/degeneracy zigzag (I/K faces down, S degeneracy up) is therefore a fully coherent path in a genuine
-- simplicial object — the simplicial reading of the extruder is COMPLETE, COHERENT, and now with the full
-- identity set. No spook. Chain: 272 (five identities) → 275a (the sixth — all six).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = face-degen-hi (the sixth identity, i>j+1). With 272's five,
-- ALL SIX simplicial identity families are now machine-checked — nothing scoped in the identity set.
------------------------------------------------------------------------
