{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIFaceset — ⟡extrude-ski-faceset: wire the vertex-index
-- through the tower's ACTUAL face geometry. WitnessTower.FaceSet says a face of Δⁿ is an F₂-indicator over
-- its n+1 vertices (Face n = Vector (suc n)); a VERTEX is the SINGLETON indicator eᵢ (1 at position i, 0
-- elsewhere). 256/257 indexed vertices by Fin (suc n); this exhibits the Fin-index AS the FaceSet singleton
-- basis — vertex i = eᵢ : Face n — and shows the embedding is injective (distinct positions ⟹ distinct
-- indicators), so the Fin-index and the geometric face-index agree.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: eᵢ (the singleton
-- indicator, a vertex-as-face) and eᵢ-inj (distinct positions ⟹ distinct singleton faces). The framing
-- ('the Fin-index IS the FaceSet vertex basis') is (prose: the geometric identification; the full
-- Boolean-lattice face structure of FaceSet is reused-in-spirit, the singleton/vertex layer grounded here).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIFaceset where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; 𝟘≢𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)

------------------------------------------------------------------------
-- ① THE VERTEX AS A SINGLETON F₂-INDICATOR (the FaceSet vertex = a weight-1 face). eᵢ i has 𝟙 at position
--    i and 𝟘 elsewhere — the standard basis vector, the tower's rung-n vertex as an actual face.
------------------------------------------------------------------------
eᵢ : {n : ℕ} → Fin n → Vector n
eᵢ zero    = 𝟙 ∷ 𝟎ⱽ
eᵢ (suc i) = 𝟘 ∷ eᵢ i

------------------------------------------------------------------------
-- ② THE EMBEDDING IS INJECTIVE (distinct vertices ⟹ distinct singleton faces) — so the Fin-index (256/257)
--    and the FaceSet geometric face-index AGREE. By exhaustion on the position.
------------------------------------------------------------------------
vtail : {n : ℕ} → Vector (suc n) → Vector n
vtail (_ ∷ v) = v

∷-injʳ : {n : ℕ} {x : F₂} {u v : Vector n} → (x ∷ u) ≡ (x ∷ v) → u ≡ v
∷-injʳ eq = cong vtail eq

eᵢ-inj : {n : ℕ} {i j : Fin n} → eᵢ i ≡ eᵢ j → i ≡ j
eᵢ-inj {suc n} {zero}  {zero}  _  = refl
eᵢ-inj {suc n} {suc i} {suc j} eq = cong suc (eᵢ-inj (∷-injʳ eq))
eᵢ-inj {suc n} {zero}  {suc j} ()   -- (𝟙 ∷ _) ≡ (𝟘 ∷ _) forces 𝟙 ≡ 𝟘, absurd
eᵢ-inj {suc n} {suc i} {zero}  ()   -- (𝟘 ∷ _) ≡ (𝟙 ∷ _) forces 𝟘 ≡ 𝟙, absurd

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the Fin vertex-index (256/257) IS the tower's FaceSet vertex geometry: a
-- vertex is the singleton F₂-indicator eᵢ, and the embedding Fin (suc n) ↪ Face n is injective): the
-- either/or "abstract Fin-index OR the tower's actual FaceSet faces?" dissolves — they AGREE. eᵢ (①) realizes
-- each Fin-position as the singleton indicator (the weight-1 face = a vertex), and eᵢ-inj (②) shows distinct
-- positions give distinct faces, so the vertex-family (256) / the fibration fibre (257) is LITERALLY the
-- tower's rung-n vertex set as faces. The SKI non-degeneracy (distinct vertices don't converge) is thus
-- carried on the tower's own face geometry, not a stand-in Fin. No spook — a positive geometric identification.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = eᵢ (vertex-as-singleton-face) + eᵢ-inj (injective embedding).
-- SCOPED: the FULL Boolean-lattice face structure of FaceSet (all subsets, with-apex/without-apex cone, the
-- Hodge ★) beyond the singleton/vertex layer — reused-in-spirit; wiring the k-faces (edges, triangles) to
-- SKI sub-configurations is ⟡extrude-ski-kfaces. What's grounded: the vertex-index IS the FaceSet singleton
-- basis, injectively — the machinery's vertex layer is now the tower's actual geometry.
------------------------------------------------------------------------
