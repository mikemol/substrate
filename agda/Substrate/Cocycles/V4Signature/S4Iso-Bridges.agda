------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso-Bridges
--
-- Slice 18 (β refactor, Phase 1): bridges making the 2-path
-- commutativity between the cocycle's 6 hand-coded Stab(D)
-- representatives and the parametric `extend D` form EXPLICIT.
--
-- Background. Slice 4's V_4 ⋊ Stab(D) ≅ S_4 picture uses 6 named
-- canonical representatives (stab-id, stab-sw, stab-cs, stab-cw,
-- stab-csw, stab-cws) hand-coded as S_4 Permutation records.
-- Slice 14 (Stab-S3-*) made `Stab anchor` and the `extend anchor s`
-- construction fully parametric in anchor. Slice 17 (OrbitKey-S3)
-- added the OrbitKey ↔ S_3 chirality labeling.
--
-- The hidden 2-path (per [[feedback-two-path-commutativity]]):
--
--     stab-X  (D-specific, 6 named records)
--        ║  this file (bridges, refl-only)
--     extend D s3-X  (instance of parametric form)
--        │   ← anchor=D collapses the bottom row
--        ↓
--     extend anchor s3-X  (parametric, exists)
--
-- The 6 bridges below prove the top edge of the square pointwise.
-- The square commutes by `refl` at each Axis input because every
-- intermediate normalisation step is definitional.
--
-- WHAT THIS FILE DOES NOT DO. It does not delete the hand-coded
-- stab-X records, and it does not rewrite slice 4's `stab-round-
-- trip` to use the parametric machinery directly. A full collapse
-- ("Phase 2") would route `orbit-key-to-stab-d ok` through
-- `extend D (orbit-key-to-s3 ok)` and replace the 6 case-α/β/γ
-- lemmas with a parametric proof via `extend-restrict D`. That
-- refactor hits Agda's `with`-abstraction limit on the
-- non-anchor-to-fin3 proof-irrelevance arguments — `refl` no
-- longer closes the per-axis equalities because applyₛ σ C inside
-- the unfolded `restrict-apply` doesn't substitute eagerly enough.
-- The fix is explicit `non-anchor-to-fin3-cong` chains (slice 14b),
-- which expand line count to roughly parity with the original
-- case lemmas. Phase 2 is left as a future slice if downstream
-- theorems need the parametric form.
--
-- See: [[feedback-two-path-commutativity]] — the structural
-- principle; [[feedback-expose-generator-not-orbit]] — the 1D
-- precursor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso-Bridges where

open import Substrate.Foundation.Product using (_,_; proj₁)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 as S4 using (Permutation)
  renaming (apply to applyₛ)
open import Substrate.Groups.Stab-S3-Extend using (extend)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey)
open import Substrate.Cocycles.V4Signature.OrbitKey-S3
  using (s3-id; s3-sw; s3-cs; s3-cw; s3-csw; s3-cws;
         orbit-key-to-s3)
open import Substrate.Cocycles.V4Signature.S4Iso
  using (stab-id; stab-sw; stab-cs; stab-cw; stab-csw; stab-cws;
         orbit-key-to-stab-d)

------------------------------------------------------------------------
-- The bridge: for each OrbitKey, the named stab record agrees with
-- `extend D` applied to the corresponding S_3 element s3-X, pointwise
-- on Axis. All 24 cases close by `refl` because both sides reduce to
-- the same Axis constant at every input.
--
-- Annealing patch (2026-05-16): originally six separate stab-X-≈-extend
-- definitions (one per X), surfaced by `scratch/findings.py` as a
-- 6-element shape-quotient orbit. Replaced by this inlined dispatch.
-- See [[project-annealing-methodology]] — orbit detected, orbit
-- patched, run the detector again for the next finding.
------------------------------------------------------------------------

orbit-key-to-stab-d-≈-extend :
  (ok : OrbitKey) (x : Axis) →
  applyₛ (orbit-key-to-stab-d ok) x ≡ applyₛ (proj₁ (extend D (orbit-key-to-s3 ok))) x
orbit-key-to-stab-d-≈-extend (α-pair , even) D = refl
orbit-key-to-stab-d-≈-extend (α-pair , even) C = refl
orbit-key-to-stab-d-≈-extend (α-pair , even) S = refl
orbit-key-to-stab-d-≈-extend (α-pair , even) W = refl
orbit-key-to-stab-d-≈-extend (α-pair , odd)  D = refl
orbit-key-to-stab-d-≈-extend (α-pair , odd)  C = refl
orbit-key-to-stab-d-≈-extend (α-pair , odd)  S = refl
orbit-key-to-stab-d-≈-extend (α-pair , odd)  W = refl
orbit-key-to-stab-d-≈-extend (β-pair , even) D = refl
orbit-key-to-stab-d-≈-extend (β-pair , even) C = refl
orbit-key-to-stab-d-≈-extend (β-pair , even) S = refl
orbit-key-to-stab-d-≈-extend (β-pair , even) W = refl
orbit-key-to-stab-d-≈-extend (β-pair , odd)  D = refl
orbit-key-to-stab-d-≈-extend (β-pair , odd)  C = refl
orbit-key-to-stab-d-≈-extend (β-pair , odd)  S = refl
orbit-key-to-stab-d-≈-extend (β-pair , odd)  W = refl
orbit-key-to-stab-d-≈-extend (γ-pair , even) D = refl
orbit-key-to-stab-d-≈-extend (γ-pair , even) C = refl
orbit-key-to-stab-d-≈-extend (γ-pair , even) S = refl
orbit-key-to-stab-d-≈-extend (γ-pair , even) W = refl
orbit-key-to-stab-d-≈-extend (γ-pair , odd)  D = refl
orbit-key-to-stab-d-≈-extend (γ-pair , odd)  C = refl
orbit-key-to-stab-d-≈-extend (γ-pair , odd)  S = refl
orbit-key-to-stab-d-≈-extend (γ-pair , odd)  W = refl
