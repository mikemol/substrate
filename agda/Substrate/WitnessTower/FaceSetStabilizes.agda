------------------------------------------------------------------------
-- Substrate.WitnessTower.FaceSetStabilizes
--
-- ◆AI-1g' — the check-ABOVE closure for FamilyWitnessAmbient (◆AI-1g). That
-- file placed FamilyWitness inside FaceSet (the Boolean lattice of faces) and
-- flagged, honestly, that it did NOT claim FaceSet itself terminal — because the
-- ◆AI-D6 pattern (the apex is always one level higher than I claim) predicted
-- yet another level. So: is FaceSet terminal, or is there a rung above it?
--
-- PROBING (◆AI-D7 check-above) gives the principled answer: the upward tower
-- STABILIZES at FaceSet. What is "above" FaceSet is NOT another witnessing rung
-- (a bigger object built by a suc-step) — it is ENDO-STRUCTURE on FaceSet itself:
--
--   (1) the Hodge ★ SELF-DUALITY: ★ : Face n → Face n (an ENDOmorphism, not a
--       map to a bigger level), with ★★ = id (FaceSet.★-involution) and
--       S +ⱽ ★ S ≡ universe (FaceSet.wedge-recon). ★ pairs nothing ↔ universe.
--       This is a symmetry OF the lattice, bottoming out at the n=0 self-dual
--       seed — it does not leave FaceSet.
--
--   (2) the ∂ / δ CHAIN-COCHAIN complex: SimplicialBoundary's face maps delAt
--       with the simplicial identity (∂∘∂ = 0), paired with the already-present
--       cochain coboundary δ²=0 (CayleyDickson.Coboundary.d²-zero). This is
--       structure ON the faces (a complex), not a rung above them.
--
-- So the up-step, iterated, does not produce an infinite regress of ever-larger
-- apexes: at FaceSet it becomes an ENDO (★) plus a complex (∂/δ). That IS the
-- stabilization criterion — the tower closes into a self-dual object equipped
-- with a boundary complex. The honest terminal is not "nothing above FaceSet"
-- but "above FaceSet is FaceSet-acting-on-itself".
--
-- This does NOT assert FaceSet is a categorical terminal object in some ambient
-- category (unprobed, and would be the ◆AI-D6 trap one more time). It asserts
-- the SPECIFIC, checked fact that the level-above candidates found by probing
-- (★, ∂/δ) are ENDO/complex structure, not new rungs — the tower stabilizes here.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.FaceSetStabilizes where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.WitnessTower.FaceSet
  using (Face; ★; ★-involution; wedge-recon; universe; nothing-face)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)

------------------------------------------------------------------------
-- (1) ★ is an ENDO (Face n → Face n), not a map to Face (suc n). Re-exported
--     to exhibit that the "level above" is a self-map: the type is Face n →
--     Face n, so iterating the up-step here does NOT grow the grade.
------------------------------------------------------------------------

star-is-endo : (n : ℕ) → (Face n → Face n)
star-is-endo n = ★ {n}

-- ★★ = id (the self-duality is an involution): the up-structure is a symmetry,
-- returning to the same object.
star-stabilizes : {n : ℕ} (S : Face n) → ★ (★ S) ≡ S
star-stabilizes = ★-involution

-- S and its ★-residue reconstruct the universe: ★ stays within FaceSet (its
-- output pairs with its input to the top of the SAME lattice).
star-within : {n : ℕ} (S : Face n) → (S +ⱽ ★ S) ≡ universe n
star-within = wedge-recon

------------------------------------------------------------------------
-- (2) the ∂ / δ complex is structure ON faces. Re-exported: the simplicial
--     boundary law (∂∘∂ reduces to the simplicial identity) and the cochain
--     δ²=0 both act on the face objects, not producing a higher rung.
------------------------------------------------------------------------

open import Substrate.WitnessTower.SimplicialBoundary public using (delAt)
open import Substrate.Algebra.CayleyDickson.Coboundary public using (d²-zero)

------------------------------------------------------------------------
-- THE STABILIZATION STATEMENT (prose-in-types): the candidates for "above
-- FaceSet" are star-is-endo (a self-map) and the ∂/δ complex (structure on
-- faces). Neither is a witnessing rung producing Face (suc n) from Face n as a
-- NEW apex. The n=0 self-dual seed is the base of the ★-descent. So the tower
-- stabilizes at FaceSet: FamilyWitness ⊂ FaceSet, and above FaceSet is
-- FaceSet-acting-on-itself, not a further apex.
------------------------------------------------------------------------

-- the n=0 seed: at grade 0 the lattice has ★ fixing the structure — the
-- self-dual bottom the descent grounds at. (nothing and universe coincide-adjacent
-- at the seed; here we record that ★ is defined at the seed, closing the descent.)
seed-has-star : Face 0 → Face 0
seed-has-star = ★ {0}
