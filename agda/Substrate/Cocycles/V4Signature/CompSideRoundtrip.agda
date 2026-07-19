------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.CompSideRoundtrip
--
-- ⟡comp-side-roundtrip — the OTHER half of the ⟡full-s4-route bijection:
-- `perm-to-compositional (compositional-to-perm c) S4C.≈ c`, which upgrades
-- FullS4Route's left-inverse-only injection to a full two-sided bijection
-- TotalSpace ≃ tower-rung-3.
--
-- HONEST STATUS — CONDITIONAL, not unconditional. After reading the maps:
--   compositional-to-perm (v , s) = embed v · embed-S₃ s
--   perm-to-compositional σ       = (v-for σ , extract-s (s-for σ))
-- the roundtrip needs recovery of BOTH components:
--   * V₄ component: v-for (embed v · embed-S₃ s) ≡ v — closeable from the
--     in-tree factorisation-unique-V₄ / v-for-anchor-sends + embed-S₃-D
--     (embed-S₃ fixes D), which this session did NOT fully assemble.
--   * S₃ component: extract-s (s-for (embed v · embed-S₃ s)) S₃.≈ s —
--     needs `embed-S₃` FAITHFUL (embed-S₃ s ≈ embed-S₃ t → S₃.≈ s t). The
--     tree has embed-S₃-cong (the EASY direction, S₃.≈ → ≈) but NOT its
--     converse. That converse is the ONE genuinely-missing lemma.
--
-- So this module states the roundtrip CONDITIONAL on the two recovery facts
-- as PARAMETERS, discharging the composition. It is a rigorous reduction:
-- "given (v-recovers) and (s-recovers), the composed-side roundtrip holds",
-- isolating EXACTLY what remains to prove (chiefly S₃-embedding faithfulness).
-- No postulate, no hole — the gaps are honest hypotheses, --safe.
--
-- ⟡set1-paydown: carriers (V₄, S₃.Carrier, S4C.Carrier) all come from their
-- home modules as Sets; this module adds only functions/proofs over them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.CompSideRoundtrip where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂; _×_)

import Substrate.Groups.S4          as S4
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.S3          as S₃
open import Substrate.Groups.V4 using (V₄)
open S4 using (Permutation; _≈_)

open import Substrate.Groups.S4-Iso.Extract   using (perm-to-compositional)
open import Substrate.Groups.S4-Iso.Embedding using (compositional-to-perm)

------------------------------------------------------------------------
-- The two component-recovery facts, as hypotheses. Each is a real, in-tree-
-- reachable statement (V₄ side from factorisation-unique-V₄; S₃ side from the
-- missing embed-S₃-faithful). Named here so consumers see EXACTLY the debt.
------------------------------------------------------------------------

-- S4C.≈ is pointwise: (v₁,s₁) ≈ (v₂,s₂) ⇔ v₁ ≡ v₂ (V₄ is discrete) ∧ s₁ S₃.≈ s₂.
-- We take the two projections of `perm-to-compositional ∘ compositional-to-perm`
-- back to identity as the hypotheses.

module _
  (v-recovers :
     (v : V₄) (s : S₃.Carrier) →
     proj₁ (perm-to-compositional (compositional-to-perm (v , s))) ≡ v)
  (s-recovers :
     (v : V₄) (s : S₃.Carrier) →
     proj₂ (perm-to-compositional (compositional-to-perm (v , s))) S₃.≈ s)
  where

  -- The pointwise S4C.≈ on the recovered pair, assembled from the two
  -- component recoveries. (V₄ side is ≡, promoted to S4C's V₄-relation;
  -- S₃ side is S₃.≈.)
  comp-side-roundtrip :
    (c : S4C.Carrier) →
    (proj₁ (perm-to-compositional (compositional-to-perm c)) ≡ proj₁ c)
    × (proj₂ (perm-to-compositional (compositional-to-perm c)) S₃.≈ proj₂ c)
  comp-side-roundtrip (v , s) = v-recovers v s , s-recovers v s

------------------------------------------------------------------------
-- ⟡residue-home — INTERLINK to the ORIENTED-RESIDUE apparatus.
--
-- The `s-recovers` hypothesis (embed-S₃ faithfulness: the S₃-word recovered
-- through the round trip is ≈ the original) is a RESIDUE statement in the
-- sense of Substrate.Category.ResidueCompensation: two representations of the
-- same group element differ by a compensating residue, and faithfulness is
-- "the residue is trivial ⇒ the representations are ≈". ResidueCompensation
-- packages exactly this (residue : V₄ / S₄, the group element compensating a
-- representational difference). So the missing ⟡embed-s3-faithful lemma has a
-- natural home there: instantiate the residue apparatus to the S₃-embedding
-- setting and show the compensating residue is trivial. The import is the
-- durable pointer to that reframing (NOT a discharge — it names the tool).
------------------------------------------------------------------------

open import Substrate.Category.ResidueCompensation using (ResidueCompensation; FullResidueCompensation)
