------------------------------------------------------------------------
-- Substrate.WitnessTower.ResidueBridge
--
-- CO-APEX bridge: the substrate's residue-compensation and the tower's
-- orientation residue are the SAME structure — both instances of the
-- generic Algebra.Wedge (DivStr / Wedge: "a = recon q b r", recover the
-- quotient-representative q and remainder r that reconcile a against b).
-- The orientation-residue machinery IS the connective means (its purpose):
-- Category.ResidueCompensation ("residue = the group element compensating a
-- representational difference") and WitnessTower.Wedge.OrientationRigResidue
-- (divᴸ, the counit-defect over LehmerPath) both live under Algebra.Wedge.
--
-- This file exhibits the V₄ residue as a genuine DivStr V₄ (recon = the V₄
-- group multiplication; z = e, the no-residue identity), giving the REAL
-- reconciliation law `a ≡ residue · b · rem` as a Wedge — upgrading
-- ResidueCompensation's currently-trivial CompensationSoundness stub
-- (v4-act σ b ≡ v4-act σ b, refl) to the actual wedge equation. Then both
-- this and OrientationRigResidue.divᴸ are visibly DivStr instances: the
-- co-apex is the shared Algebra.Wedge apex, in the import graph.
--
-- Search "residue" / "compensat" / "wedge" / "DivStr" / "recover the
-- reconciling element" and land here.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.ResidueBridge where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Groups.V4 using (V₄; e)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Axioms using (·-assoc; ε-left; ε-right)

open import Substrate.Algebra.Wedge using (DivStr; Wedge)

------------------------------------------------------------------------
-- (V₄ leg) The V₄ residue as a DivStr: recon q b r = q · b · r, z = e.
-- This is the "residue = compensating group element" of
-- Category.ResidueCompensation, packaged as the generic wedge shape.
------------------------------------------------------------------------

v4-div : DivStr V₄
v4-div = record
  { z     = e
  ; recon = λ q b r → (q · b) · r
  }

------------------------------------------------------------------------
-- The REAL reconciliation law as a Wedge (not the trivial soundness stub):
-- given a residue σ with a ≡ σ · b (match reconstructed from growth by the
-- compensating σ), that IS a Wedge v4-div a b with quot = σ, rem = e.
------------------------------------------------------------------------

residue-wedge :
  (a b σ : V₄) → a ≡ (σ · b) → Wedge v4-div a b
residue-wedge a b σ eq = record
  { quot     = σ
  ; rem      = e
  ; wedge-eq = trans eq (sym (ε-right (σ · b)))
  }

-- The converse read-off: a Wedge over v4-div with rem = e recovers the
-- compensating residue as its quotient. (recover-the-reconciling-element,
-- the same shape as S4-Iso.extract-s and OrientationRigResidue.)
wedge-residue :
  (a b : V₄) (w : Wedge v4-div a b) → Wedge.rem w ≡ e →
  a ≡ (Wedge.quot w · b)
wedge-residue a b w rem-e =
  trans (Wedge.wedge-eq w)
        (trans (cong (λ r → (Wedge.quot w · b) · r) rem-e)
               (ε-right (Wedge.quot w · b)))

------------------------------------------------------------------------
-- ⟡residue-graded-honest — the HONEST flat/graded relation, mirroring
-- OrientationFlatGradedBridge's discipline (no false `flatten` morphism).
--
-- The v4-div above is FLAT (DivStr V₄): V₄ is a FIXED finite group, NOT
-- ℕ-indexed, so v4-div is genuinely single-grade — it is NOT the flatten of
-- a graded V₄ structure (there is none to flatten). The graded residue lives
-- on the TOWER: `tower-graded : GradedDivStr Perm (λ n → Fin (suc n))`, where
-- the grade IS the rung and recon = insert-at raises it.
--
-- So the honest relation is NOT "v4-div is graded" and NOT "v4-div flattens
-- tower-graded" (different carriers: V₄ vs Perm). It is: v4-div is a
-- SINGLE-GRADE residue that embeds into the tower's rung-3 slice (S₄) via the
-- group inclusion V₄ ↪ S₄ (Groups.V4-Embedding.embed). Per
-- OrientationFlatGradedBridge, flat↔graded is a grade-collapse ι (a
-- section-with-forgotten-discipline), NOT a DivStr morphism — the principled
-- home is the Allegory.Refinement Φ-chain. We import tower-graded to make the
-- edge REAL in the graph, and STATE the relation without overclaiming a
-- morphism that the shapes forbid.
------------------------------------------------------------------------

open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)

-- The graded residue is the tower's (imported, edge now real). v4-div is the
-- FLAT V₄ slice; their relation is the ι grade-collapse discipline, not a
-- morphism. This binding records that tower-graded is THE graded home, so a
-- search from v4-div reaches it — the co-apex is "flat V₄ residue vs graded
-- tower residue", honestly non-morphic, cross-referenced not falsely fused.
graded-residue-home = tower-graded
