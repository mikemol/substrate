{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.V4Grounding — ⟡v4-from-the-build: the canonical Klein four-group V₄ (Groups.V4)
-- grounded IN the tower's build, NOT compared against it. The tower's growth process inductively
-- constructs the chain of symmetric groups Sₙ (Enumerate.perms, up the rungs); V₄ is the Klein-four
-- subgroup that build PRODUCES at rung 4 (KleinCensus: it debuts there — klein-pairs 4 = 24 → 4 subgroups;
-- rung 3 has zero). So V₄'s elements ARE permutations of the build (⟦_⟧ into Perm 4 — the normal V₄,
-- {id + the 3 double-transpositions}) and its operation IS the build's composition: Groups.V4's `_·_` is
-- BISIMILAR-WITH-THE-BUILD's `compose` (·-is-compose, all 16 cases refl — ⟦_⟧ is a group homomorphism onto
-- the double-transposition subgroup). This is the ExtrudeSKIKFaces method (a face's dimension IS its
-- build-trace, read off FaceSet's cone) applied to V₄: V₄ IS its build-trace — the permutation it is at
-- rung 4 — so its op need never be recomputed, it is read off `compose`. The 3 non-identity elements are
-- the double-transpositions (is-involution, refl), FirstAppearance's rung-4 debut. Hence the abstract V₄
-- carrier is regrounded on the tower's construction, and its TopologicalGroup site is a Group taken FROM
-- the tower (V₄-Group), witnessed here.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED (machine-checked) = the embedding ⟦_⟧ into the build; the
-- bisimilarity-with-build law ·-is-compose (Groups.V4's op IS the tower's compose under ⟦_⟧, 16× refl);
-- the involution/double-transposition placement (α/β/γ-involution); and the tower-grounded TopologicalGroup
-- inhabitant. SCOPED (reused-in-spirit): the FULL Sₙ-tower growth as a coalgebra (Enumerate's per-rung
-- insertion is the grounded finite shadow — the unbounded rung process is not re-run here); the KleinCensus
-- COUNT (klein-pairs 4 = 24 → 4 subgroups) is cited, not re-proven; the discrete topology is the trivial
-- marker (TopologicalGroup's only field is the group).
------------------------------------------------------------------------

module Substrate.WitnessTower.V4Grounding where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Bool using (Bool; true)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose; is-involution)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Bundle using (V₄-Group)
open import Substrate.Algebra.TopologicalGroup using (TopologicalGroup)

------------------------------------------------------------------------
-- ① V₄ EMBEDDED IN THE BUILD. Each element IS a permutation the tower's `perms 4` enumeration produces:
--    the identity and the 3 double-transpositions — the normal Klein-four V₄ ⊆ S₄.
------------------------------------------------------------------------
⟦_⟧ : V₄ → Perm 4
⟦ e ⟧ = zero ∷ suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ []       -- id
⟦ α ⟧ = suc zero ∷ zero ∷ suc (suc (suc zero)) ∷ suc (suc zero) ∷ []       -- (1 2)(3 4)
⟦ β ⟧ = suc (suc zero) ∷ suc (suc (suc zero)) ∷ zero ∷ suc zero ∷ []       -- (1 3)(2 4)
⟦ γ ⟧ = suc (suc (suc zero)) ∷ suc (suc zero) ∷ suc zero ∷ zero ∷ []       -- (1 4)(2 3)

------------------------------------------------------------------------
-- ② THE BISIMILARITY-WITH-BUILD LAW. Groups.V4's operation IS the tower's composition under ⟦_⟧ — the
--    element-shadow of the build. All 16 cases refl: ⟦_⟧ is a group homomorphism, so the abstract V₄ op is
--    never recomputed — it is READ OFF `compose`.
------------------------------------------------------------------------
·-is-compose : (x y : V₄) → ⟦ x · y ⟧ ≡ compose ⟦ x ⟧ ⟦ y ⟧
·-is-compose e e = refl
·-is-compose e α = refl
·-is-compose e β = refl
·-is-compose e γ = refl
·-is-compose α e = refl
·-is-compose α α = refl
·-is-compose α β = refl
·-is-compose α γ = refl
·-is-compose β e = refl
·-is-compose β α = refl
·-is-compose β β = refl
·-is-compose β γ = refl
·-is-compose γ e = refl
·-is-compose γ α = refl
·-is-compose γ β = refl
·-is-compose γ γ = refl

------------------------------------------------------------------------
-- ③ THE PLACEMENT. The 3 non-identity elements are the double-transpositions — involutions — that debut at
--    rung 4 (FirstAppearance's double-transposition seam; KleinCensus's Klein-four debut).
------------------------------------------------------------------------
α-involution : is-involution ⟦ α ⟧ ≡ true
α-involution = refl
β-involution : is-involution ⟦ β ⟧ ≡ true
β-involution = refl
γ-involution : is-involution ⟦ γ ⟧ ≡ true
γ-involution = refl

------------------------------------------------------------------------
-- THE SITE, GROUNDED. V₄ as a topological group: its Group is taken FROM the tower (V₄-Group, whose carrier
-- is now grounded in the build above), with the trivial discrete topology (the record's only field).
------------------------------------------------------------------------
V4-TopologicalGroup : TopologicalGroup V₄
V4-TopologicalGroup = record { group = V₄-Group }
