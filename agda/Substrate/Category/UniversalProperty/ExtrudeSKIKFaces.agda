{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIKFaces — ⟡extrude-ski-kfaces: the higher FaceSet faces
-- beyond vertices (258), with the face DIMENSION defined AS BISIMILAR WITH THE TOWER'S BUILD (operator:
-- "isn't this just bisimilarity with the tower's build pattern? any attribute you derive from it can be
-- bisimilar with it") — NOT a fresh popcount. A face IS its build-trace: the sequence of with-apex/
-- without-apex cone choices up the rungs (FaceSet). weight recurses via the cone vocabulary (apex-bit +
-- base-face), so it CO-VARIES with the build; the cone-commutation laws (weight-with/without-apex) are the
-- ELEMENT-SHADOW of FaceCount's Pascal cone-step (faces (suc n)(suc k) ≡ faces n (suc k) + faces n k). So
-- weight is bisimilar with the tower's build, reused not reinvented.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: weight (via the cone),
-- the bisimilarity-with-build laws (weight-with-apex ≡ suc; weight-without-apex ≡ id), the k-face and vertex
-- (weight-1) characterizations, and vertex-is-eᵢ-weight (258's singleton has weight 1). The framing ('weight
-- is bisimilar with the build', 'the element-shadow of Pascal') is (prose: the operator's coalgebra point;
-- the full coinductive tower-growth bisimulation is reused-in-spirit, the finite per-rung fold grounded).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIKFaces where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.WitnessTower.FaceSet using (Face; with-apex; without-apex; apex-bit; base-face)
open import Substrate.Category.UniversalProperty.ExtrudeSKIFaceset using (eᵢ)

------------------------------------------------------------------------
-- ① THE DIMENSION, BISIMILAR WITH THE BUILD. weight recurses via the tower's cone: an apex-present move
--    (with-apex, bit 𝟙) contributes 1, an apex-absent move (without-apex, bit 𝟘) contributes 0, then the
--    base. So weight CO-RECURSES with the build coalgebra — it reads the build-trace (the cone choices).
------------------------------------------------------------------------
bit : F₂ → ℕ
bit 𝟘 = zero
bit 𝟙 = suc zero

weight : {n : ℕ} → Vec F₂ n → ℕ
weight []       = zero
weight (b ∷ f)  = bit b + weight f

------------------------------------------------------------------------
-- ② THE BISIMILARITY-WITH-BUILD LAWS (the cone-commutation): weight commutes with the tower's build moves.
--    These ARE the element-shadow of FaceCount's Pascal cone-step (adding an apex-vertex increments the
--    dimension iff the apex bit is set). So weight is bisimilar with the tower's build, by definition.
------------------------------------------------------------------------
weight-with-apex : {n : ℕ} (f : Face n) → weight (with-apex f) ≡ suc (weight f)
weight-with-apex f = refl        -- with-apex f = 𝟙 ∷ f ; weight = bit 𝟙 + weight f = suc (weight f)

weight-without-apex : {n : ℕ} (f : Face n) → weight (without-apex f) ≡ weight f
weight-without-apex f = refl     -- without-apex f = 𝟘 ∷ f ; weight = 0 + weight f = weight f

-- the cone-split reconstruction (FaceSet) means EVERY face's weight is its apex-bit contribution + its
-- base-face weight — weight is fully determined by the build history:
weight-cone : {n : ℕ} (f : Face (suc n)) → weight f ≡ bit (apex-bit f) + weight (base-face f)
weight-cone (b ∷ f) = refl

------------------------------------------------------------------------
-- ③ k-FACES AND VERTICES. A k-face is a face of dimension k = weight (suc k) (k+1 vertices). A VERTEX is a
--    0-face = weight 1 — and 258's singleton indicator eᵢ IS a weight-1 face (a vertex), confirming the
--    vertex layer (258) is the dimension-0 stratum of THIS face grading.
------------------------------------------------------------------------
is-kface : {m : ℕ} → ℕ → Vec F₂ m → Set
is-kface k f = weight f ≡ suc k        -- dimension k ⟺ k+1 selected vertices

is-vertex : {m : ℕ} → Vec F₂ m → Set
is-vertex = is-kface 0                  -- a vertex = a 0-face = weight 1

-- 258's singleton indicator eᵢ has weight 1 — it is a vertex (dimension-0 face), bisimilar-with-build:
𝟎-weight : {n : ℕ} → weight (𝟎ⱽ {n}) ≡ zero
𝟎-weight {zero}  = refl
𝟎-weight {suc n} = 𝟎-weight {n}       -- 𝟎ⱽ {suc n} = 𝟘 ∷ 𝟎ⱽ {n} ; weight = 0 + weight 𝟎ⱽ = weight 𝟎ⱽ

eᵢ-weight : {n : ℕ} (i : Fin n) → weight (eᵢ i) ≡ suc zero
eᵢ-weight {suc n} zero    = cong suc (𝟎-weight {n})  -- eᵢ zero = 𝟙 ∷ 𝟎ⱽ ; weight = suc (weight 𝟎ⱽ) = suc zero
eᵢ-weight (suc i) = eᵢ-weight i                      -- eᵢ (suc i) = 𝟘 ∷ eᵢ i ; weight (𝟘 ∷ eᵢ i) = weight (eᵢ i)

is-vertex-eᵢ : {n : ℕ} (i : Fin n) → is-vertex (eᵢ i)
is-vertex-eᵢ i = eᵢ-weight i

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the face DIMENSION is BISIMILAR WITH THE TOWER'S BUILD, not a fresh
-- popcount; and 258's vertices are the dimension-0 stratum): the either/or "compute a fresh weight/popcount
-- OR reuse the tower's counting" DISSOLVED via the operator's coalgebra point — a face IS its build-trace
-- (the cone-choice sequence, FaceSet), so its dimension is READ OFF the build: weight recurses through the
-- cone vocabulary (apex-bit/base-face, ①), co-varying with the build coalgebra, and the cone-commutation
-- laws (weight-with/without-apex, ②) ARE the element-shadow of FaceCount's Pascal cone-step. So weight is
-- bisimilar with the tower's build, reused not reinvented. The k-face grading (③) then places 258's vertices
-- as the dimension-0 stratum (eᵢ has weight 1, is-vertex-eᵢ) — the vertex machinery (255-260) is the bottom
-- of THIS face lattice, and the higher faces (edges weight-2, triangles weight-3, …) are the same build,
-- higher up. No spook — a positive, build-bisimilar grading.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = weight (via the cone), the bisimilarity-with-build laws
-- (weight-with/without-apex/weight-cone), the k-face/vertex grading, and eᵢ-weight (258's vertices are the
-- weight-1 stratum). SCOPED (reused-in-spirit): the FULL coinductive tower-GROWTH bisimulation (the
-- unbounded rung process as a coalgebra, with weight an anamorphism — Trace/Final/Bisim) — the finite
-- per-rung fold is the grounded shadow; the numeric agreement weight ≡ FaceCount.faces (that the concrete
-- dimension matches the abstract Pascal count) is ⟡extrude-ski-fvector; the SKI wiring of a k-face to its
-- selected NF-combinator set (via 260's label-at) is ⟡extrude-ski-kface-combinators. What's grounded: the
-- face dimension is bisimilar with the tower's build (not a fresh popcount), and 258's vertices are its
-- dimension-0 stratum.
------------------------------------------------------------------------
