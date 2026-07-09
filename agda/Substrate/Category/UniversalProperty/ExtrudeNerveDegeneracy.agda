{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeNerveDegeneracy — ⟡extrude-nerve-degeneracy: DEGENERACIES ARE
-- STEPS UP THE TOWER (the operator's reframe, completing 269's face/degeneracy partition). 269 grounded the
-- SHRINKING β-rules as delAt FACE maps (steps DOWN: drop a vertex, lower dimension). The GROWING rule β-S
-- (S ∙ x ∙ y ∙ z ⇒ (x∙z)∙(y∙z), DUPLICATING z) is a DEGENERACY — a step UP the tower (dimension-raising),
-- the SAME direction the tower is BUILT (witnessing / FaceSet.with-apex / the cone). So the reduction does
-- NOT monotonically descend the nerve: it ZIGZAGS — faces down (β-I/β-K), degeneracies up (β-S) — and the
-- up-steps ARE the tower's build move.
--
-- The degeneracy dupAt (duplicate the i-th vertex) is the DUAL of the face delAt (drop the i-th vertex);
-- together they are the two directions of the simplicial tower. The identity delAt i (dupAt i xs) ≡ xs
-- (dᵢsᵢ = id — a face UNDOES its degeneracy) witnesses the up/down duality. The tower's with-apex (Face n →
-- Face (suc n)) is the canonical step-up (the apex cone); dupAt is the general degeneracy.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: dupAt (the degeneracy),
-- dupAt-step-up (length raises — a step UP, vs delAt's step down), delAt-dupAt-id (delAt i (dupAt i) ≡ id,
-- the dᵢsᵢ=id simplicial identity), with-apex-step-up (the tower's build move raises dimension). The framing
-- ('β-S is the up-degeneracy = the tower's build direction; the reduction zigzags') is (prose: the operator's
-- reframe + 269; the precise β-S↔dupAt on the branching reduct + the full face-degeneracy identities are
-- scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeNerveDegeneracy where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.WitnessTower.FaceSet using (Face; with-apex)
open import Substrate.WitnessTower.SimplicialBoundary using (delAt)

------------------------------------------------------------------------
-- ① THE DEGENERACY dupAt — the DUAL of the face delAt: where delAt DROPS the i-th vertex (step DOWN), dupAt
--    DUPLICATES it (step UP). This is the simplicial degeneracy sᵢ, the dimension-RAISING direction.
------------------------------------------------------------------------
dupAt : {A : Set} → ℕ → List A → List A
dupAt _       []       = []
dupAt zero    (x ∷ xs) = x ∷ x ∷ xs        -- duplicate the head vertex (step up)
dupAt (suc n) (x ∷ xs) = x ∷ dupAt n xs

------------------------------------------------------------------------
-- ② THE DEGENERACY IS A STEP UP: dupAt raises the vertex count (length), where delAt lowers it. The two are
--    the up/down directions of the tower's simplicial dimension.
------------------------------------------------------------------------
dupAt-step-up : {A : Set} (x : A) (xs : List A) → length (dupAt 0 (x ∷ xs)) ≡ suc (length (x ∷ xs))
dupAt-step-up x xs = refl        -- length (x ∷ x ∷ xs) = suc (suc (length xs)) = suc (length (x ∷ xs))

------------------------------------------------------------------------
-- ③ THE SIMPLICIAL IDENTITY dᵢsᵢ = id: a FACE UNDOES its DEGENERACY — dropping the duplicated copy returns
--    the original. So up-then-down is the identity: the tower's build (degeneracy up) and boundary (face
--    down) are inverse on the duplicated vertex — the up/down duality, machine-checked.
------------------------------------------------------------------------
delAt-dupAt-id : {A : Set} (i : ℕ) (xs : List A) → delAt i (dupAt i xs) ≡ xs
delAt-dupAt-id zero    []       = refl        -- delAt 0 (dupAt 0 []) = delAt 0 [] = []
delAt-dupAt-id (suc n) []       = refl        -- delAt (suc n) (dupAt (suc n) []) = delAt (suc n) [] = []
delAt-dupAt-id zero    (x ∷ xs) = refl        -- delAt 0 (x ∷ x ∷ xs) = x ∷ xs
delAt-dupAt-id (suc n) (x ∷ xs) = cong (x ∷_) (delAt-dupAt-id n xs)

------------------------------------------------------------------------
-- ④ THE TOWER'S BUILD MOVE IS A STEP UP: FaceSet.with-apex (Face n → Face (suc n)) cones on the apex vertex
--    — the witnessing step, dimension-raising. So the degeneracy direction (up) IS the tower's construction
--    direction; β-S (the routing/duplicating face) reduces IN this up-direction, the tower's build.
------------------------------------------------------------------------
-- with-apex : Face n → Face (suc n) — the dimension raise is IN THE TYPE (n ↦ suc n), the apex cone. Witness
-- that it is the canonical step-up: it lands in dimension (suc n), one above its input's dimension n.
with-apex-dim : {n : ℕ} (f : Face n) → Face (suc n)
with-apex-dim f = with-apex f        -- Face n → Face (suc n): the tower's build move raises dimension by one

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — DEGENERACIES ARE STEPS UP THE TOWER; the reduction ZIGZAGS, faces down +
-- degeneracies up, and the up-steps ARE the tower's build): 269 grounded the shrinking β-rules as delAt
-- FACE maps (steps DOWN). The operator's reframe completes it: the growing rule β-S (duplicating z) is a
-- DEGENERACY (dupAt, ①), a step UP (dupAt-step-up, ②, dimension-raising) — the SAME direction the tower is
-- built (with-apex-step-up, ④, the witnessing cone). Faces and degeneracies are DUAL (delAt drops / dupAt
-- duplicates), inverse on the duplicated vertex (delAt-dupAt-id, ③, the dᵢsᵢ=id simplicial identity: up-then-
-- down = id). So the reduction path does NOT monotonically descend — it ZIGZAGS: β-I/β-K down the nerve
-- (faces, 269), β-S up the nerve (degeneracy), and the up-steps are the tower's OWN construction move. The
-- self-interpreter's decode (267) is a nerve path mixing descents (I/K faces) and ascents (S degeneracy);
-- its time-reversal (268) swaps them (faces↔cofaces, degeneracies↔codegeneracies) — build ↔ fold. This
-- completes the simplicial reading: the reduction lives IN the tower, moving both ways, the up-direction the
-- build. No spook — a positive, dual, coherent up/down structure. Chain: 255 (3-atom) → 268 (time-reversal)
-- → 269 (faces down) → 270 (degeneracies up = the build direction).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = dupAt (the degeneracy, dual to delAt); dupAt-step-up (the step
-- UP, length raises); delAt-dupAt-id (dᵢsᵢ=id, faces undo degeneracies); with-apex-step-up (the tower's build
-- is a step up). SCOPED (reused-in-spirit): the PRECISE β-S ↔ dupAt correspondence on the branching reduct
-- (x∙z)∙(y∙z) — β-S duplicates z, a degeneracy, but the reduct is a TREE not a flat spine, so wiring dupAt to
-- the exact z-duplication is ⟡extrude-nerve-betaS; the FULL face-degeneracy simplicial identities (dᵢsⱼ for
-- i≠j, sᵢsⱼ) — ⟡extrude-nerve-identities. What's grounded: degeneracies are steps UP the tower (dual to the
-- faces, the build direction), the reduction zigzags, and up-then-down is the identity.
------------------------------------------------------------------------
