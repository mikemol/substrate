------------------------------------------------------------------------
-- Substrate.Lifecycle.Instance
--
-- Defines: ingest, project, resolve, reclaim-path, ingest-orientation,
--          project-orientation, reclaim-orientation, reclaim-decomposes
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Instance where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Path
open import Substrate.Lifecycle.Graded
open import Substrate.Lifecycle.Adjunction


------------------------------------------------------------------------
-- THE CONCRETE LIFECYCLE — the store's actual pipeline, as a path.
--
-- ⚑ THIS IS THE EXTRUDABLE INSTANCE. `lifecycle-graded` is GENERIC (an
-- algebra over any grade); the extruder needs a CONCRETE inhabitant so the
-- emitted `.agdai` carries real structure to decode. Everything above this
-- file is the algebra; this file is the datum.
--
-- Four boundaries, matching `lifecycle.py --boundaries` exactly:
--
--   0  ε        → sourced     the ingest draws from the filesystem
--   1  sourced  → observed    a position is assigned in the log
--   2  observed → settled     the inserting transaction commits
--   3  settled  → consumed    a cursor consumer advances past it
--
-- ⚑ THE DIGIT AT EACH STEP IS THE ORIENTATION — which actor released at that
-- boundary, out of the `suc k` positions available at grade k. The digits
-- below are the store's MEASURED configuration: at boundary 3 the projection
-- is caught up (`sppf:projection` at 505,776) while `scope_fix:resolver` is
-- terminal and pins the floor at 0, so the orientation there is the LAST
-- slot — the maximal residue, everything still held.
------------------------------------------------------------------------

-- grade 1: the ingest step. One slot at grade 0, so the digit is forced.
ingest : LifecyclePath 1
ingest = origin ◂ fzero

-- grade 2: the log-position step. Two slots; the observation lands at the
-- first, because a position is assigned before it can settle.
project : LifecyclePath 2
project = ingest ◂ fzero

-- grade 3: the commit step.
resolve : LifecyclePath 3
resolve = project ◂ (fsuc fzero)

-- grade 4: the consumption step — the terminal actor pins here, so the
-- residue is the LAST slot (nothing below has been released).
reclaim-path : LifecyclePath 4
reclaim-path = resolve ◂ (fsuc (fsuc (fsuc fzero)))

------------------------------------------------------------------------
-- THE ORIENTATIONS, READ BACK. Each is the counit-defect at its boundary —
-- the datum the forgetful side drops and the wedge hands back. That these
-- hold by `refl` is the point: the orientation is RECORDED, not recomputed.
------------------------------------------------------------------------

-- ⚑ THE IMPLICITS MUST BE SUPPLIED. `term n a b = Σ (R n) (λ r → a ≡ recon n b r)`,
-- so a bare `(r , refl)` leaves `a` and `b` UNDETERMINED — `[UnsolvedMetaVariables]`,
-- not a type error, which is the failure mode that looks like the term is fine.
-- Naming the endpoints is what makes each orientation a closed term the extractor
-- can decode.
ingest-orientation : orientation-of 0 {ingest} {origin} (fzero , refl) ≡ fzero
ingest-orientation = refl

project-orientation : orientation-of 1 {project} {ingest} (fzero , refl) ≡ fzero
project-orientation = refl

reclaim-orientation :
  orientation-of 3 {reclaim-path} {resolve} (fsuc (fsuc (fsuc fzero)) , refl)
  ≡ fsuc (fsuc (fsuc fzero))
reclaim-orientation = refl

------------------------------------------------------------------------
-- THE WEDGE AT THE TOP GRADE: the whole path decomposes against its base
-- with the consumption orientation as residue — by `refl`, so the extractor
-- sees a closed term rather than a proof obligation.
------------------------------------------------------------------------

reclaim-decomposes : forget-eval 3 resolve (fsuc (fsuc (fsuc fzero))) ≡ reclaim-path
reclaim-decomposes = refl
