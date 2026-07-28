------------------------------------------------------------------------
-- Substrate.WitnessTower.FamilyWitnessAmbient
--
-- ◆AI-1g — the check-ABOVE closure for TowerFamilyApex (◆AI-1f). That file
-- named FamilyWitness (the DAG) as the apex over the tower family, with Core a
-- gauge choice. The ritual#4 G8 residue asked: is FamilyWitness itself the top,
-- or does it sit inside a level above? Probing (◆AI-D6/D7 check-above) ANSWERS:
-- FamilyWitness is NOT terminal. It sits inside the simplicial FACE structure:
--
--   FaceSet     : Face n = Vector (suc n) — the COMPLETE Boolean lattice of
--                 faces (every subset of the n+1 vertices is a face). The
--                 ambient in which a simplex lives.
--   FaceCount   : faces n k — the f-vector (k-face counts) by coning / Pascal.
--                 Crucially faces n 0 = n+1 — the SAME (n+1) that drives the
--                 permutation tower Ⓣ₁ (its rung census). FaceCount already
--                 documents this identity.
--   FamilyWitness.FSimplex : the simplex AS A DAG — cell : Vec (FSimplex k)
--                 (suc (suc k)) → FSimplex (suc k), a rung built from its k+2
--                 facets. This is ONE object living in the FaceSet lattice.
--
-- So the corrected FULL closure is FOUR levels, not three:
--   FaceSet (Boolean lattice of faces, the ambient)
--     ⊇ the simplex's faces (counted by FaceCount's f-vector)
--       ∋ FSimplex (the simplex-as-DAG, FamilyWitness)  ← ◆AI-1f called this the top
--         │ gauge choice (one vertex-ordering)
--         ▼
--       Core (linear witnessing spine)
--         ⊇ GradedDivStr-covered {Ⓣ₁,Ⓣ₂}   (◆AI-1e)
--
-- HONEST SCOPE (◆AI-D4): this file establishes FaceSet/FaceCount as the named
-- ambient ABOVE FamilyWitness by re-export + the faces-n-0 = n+1 tie back to the
-- census. It does NOT claim FaceSet is ITSELF terminal — that is the next
-- check-above (◆AI-1g' if pursued). It corrects the ◆AI-1f "FamilyWitness is the
-- apex" to "FamilyWitness is one object in the FaceSet lattice", one level up.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FamilyWitnessAmbient where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- the ambient Boolean lattice of faces (the level above the simplex-DAG).
open import Substrate.WitnessTower.FaceSet
  using (Face; nothing-face; universe)

-- the simplex-as-DAG (FamilyWitness) — one object in that lattice.
open import Substrate.WitnessTower.FamilyWitness
  using (FSimplex; vertex; cell; WSimplex-unique)

-- the f-vector census (k-face counts). Its 0-face count is n+1.
open import Substrate.WitnessTower.FaceCount public using (faces)

------------------------------------------------------------------------
-- THE TIE that makes the ambient non-trivial: FaceCount's 0-faces = n+1, the
-- SAME (n+1) driving the permutation tower Ⓣ₁'s rung census. So the FaceSet
-- ambient's vertex-count IS the census count that FamilyWitness showed is the
-- gauge group. The level-above (FaceSet) and the gauge group (Ⓣ₁ = Sₙ) meet at
-- the vertex level.
------------------------------------------------------------------------

vertices-are-n+1 : (n : ℕ) → faces n 0 ≡ suc n
vertices-are-n+1 n = refl
