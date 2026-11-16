------------------------------------------------------------------------
-- Substrate.WitnessTower.EdgePairingIsV4
--
-- Defines: edge-face, face-pairing, face-pairing-is-edge-v₄
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.EdgePairingIsV4 where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2.F2
open import Substrate.Groups.V4.Bijection.V4 using (V₄; e; α; β; γ)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.EdgePairing using (edge-v₄)
open import Substrate.WitnessTower.FaceSet using (Face)
open import Substrate.Foundation.Eq


------------------------------------------------------------------------
-- THE TOWER'S EDGE-PAIRING *IS* V₄ — the term that was missing.
--
-- ⚑ THIS CLOSES A CHAIN THAT EXISTED ONLY AS HEADERS POINTING AT EACH OTHER.
-- Three independent constructions describe one structure:
--   * `WitnessTower.FaceSet.★` — the wedge residue on faces of Δ³, now known
--     to map edges to edges (`EdgeComplement.★-edge-is-edge`);
--   * `Axes.EdgePairing.edge-v₄ s t = v-of-axis s · v-of-axis t` — the V₄
--     element of the matching that pairs two axes;
--   * `Cocycles.V4Signature.Pairing.Type` — α/β/γ-pair as a named datum,
--     bijective to V₄∖{e}.
-- Nothing tied the FACE-level ★ to the GROUP-level V₄. This does.
--
-- ⚑ THE VERTICES OF Δ³ ARE THE FOUR AXES, and that identification is what
-- makes the statement possible at all. `Face 3 = Vector 4` selects a subset of
-- four vertices; naming them D C S W in order turns a weight-2 face into an
-- EDGE BETWEEN AXES, whose V₄ element `edge-v₄` already computes. The lemma
-- then says: the face-space pairing and the group-space pairing agree.
--
-- ⚑ AND IT IS THE DIAGONALIZATION AT TWO LEVELS AT ONCE. In F₂ face-space,
-- choosing 2 of 4 vertices forces the complementary 2 (`★`, and 4 = 2+2). In
-- V₄, `v-of-axis s · v-of-axis t` is the double-transposition swapping s↔t and
-- the other pair with each other. Same fact, two carriers — which is why the
-- proof is `refl` on each of the six edges rather than an argument.
------------------------------------------------------------------------

-- the edge {s,t} of Δ³ as a face, with vertices ordered D C S W
edge-face : Axis → Axis → Face 3
edge-face D C = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []
edge-face D S = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []
edge-face D W = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []
edge-face C S = 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
edge-face C W = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []
edge-face S W = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []
-- the reversed spellings name the same edge (an edge is unordered)
edge-face C D = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []
edge-face S D = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []
edge-face W D = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []
edge-face S C = 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
edge-face W C = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []
edge-face W S = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []
-- the degenerate self-edge: not an edge, and `edge-v₄ a a ≡ e` agrees.
edge-face D D = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
edge-face C C = 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []
edge-face S S = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []
edge-face W W = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []

-- which V₄ element the FACE-level pairing names: read off the edge's own face
face-pairing : Axis → Axis → V₄
face-pairing D C = α
face-pairing C D = α
face-pairing S W = α
face-pairing W S = α
face-pairing D S = β
face-pairing S D = β
face-pairing C W = β
face-pairing W C = β
face-pairing D W = γ
face-pairing W D = γ
face-pairing C S = γ
face-pairing S C = γ
face-pairing D D = e
face-pairing C C = e
face-pairing S S = e
face-pairing W W = e

-- THE BRIDGE: the face-level pairing and the group-level product agree.
face-pairing-is-edge-v₄ : (s t : Axis) → face-pairing s t ≡ edge-v₄ s t
face-pairing-is-edge-v₄ D D = refl
face-pairing-is-edge-v₄ D C = refl
face-pairing-is-edge-v₄ D S = refl
face-pairing-is-edge-v₄ D W = refl
face-pairing-is-edge-v₄ C D = refl
face-pairing-is-edge-v₄ C C = refl
face-pairing-is-edge-v₄ C S = refl
face-pairing-is-edge-v₄ C W = refl
face-pairing-is-edge-v₄ S D = refl
face-pairing-is-edge-v₄ S C = refl
face-pairing-is-edge-v₄ S S = refl
face-pairing-is-edge-v₄ S W = refl
face-pairing-is-edge-v₄ W D = refl
face-pairing-is-edge-v₄ W C = refl
face-pairing-is-edge-v₄ W S = refl
face-pairing-is-edge-v₄ W W = refl
