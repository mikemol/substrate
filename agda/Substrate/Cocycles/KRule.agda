------------------------------------------------------------------------
-- Substrate.Cocycles.KRule
--
-- The CY-2 K-rule variable cocycle (catalog M17) as a
-- `WeakCocycleStructure` instance.
--
-- Layer        : K-rule variable assignments (2-variable K-rules)
-- Base         : V × V where V = Fin n
-- Gauge group  : S_n acting on V by variable renaming
-- Classes      : two orbits — diagonal {(v, v)} and off-diagonal
--                {(v, w) : v ≠ w}
-- Invariant    : distinctness pattern on the two slots
--
-- Validation purpose: this is the second cocycle instantiated in
-- Agda. It tests the abstraction's generality across catalogues. The
-- design choice IS the finding:
--
--   * CY-5 uses `IsomorphicCocycleStructure` because its fibers (the
--     4 V_4-translates per orbit) are V_4-torsors — free transitive
--     action, no canonical baseline.
--   * CY-2 uses `WeakCocycleStructure` because the S_n action on each
--     orbit is NOT free: the diagonal orbit has stabilizer S_{n-1} on
--     each (v, v); the off-diagonal orbit has stabilizer S_{n-2}. So
--     the orbits are coset spaces (S_n / S_{n-1}, S_n / S_{n-2}), not
--     S_n-torsors.
--
-- This split between strong/weak abstraction tracks the catalogue's
-- split between cocycles where isomorphic-storage applies (CY-5) and
-- those where it doesn't (CY-2). The abstraction layer correctly
-- refuses to admit CY-2 as `IsomorphicCocycleStructure` — the
-- `fiber-torsor` field cannot be filled without changing the gauge.
--
-- See: catalog/cocycles.md § CY-2 — K-rule variable cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.KRule where

open import Level using (0ℓ)
open import Data.Empty using (⊥; ⊥-elim)
open import Data.Nat using (ℕ)
open import Data.Fin using (Fin; _≟_)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Relation.Nullary using (Dec; yes; no)

open import Substrate.Groups.SFin as SFin
  using (Permutation; _·_; ε; _⁻¹; _≈_; S-Group; σ-injective)
  renaming (apply to applyₛ)
open import Substrate.Cocycle
  using (WeakCocycleStructure; Action)

------------------------------------------------------------------------
-- The cocycle is parametric in n (the size of the variable space).
------------------------------------------------------------------------

module _ (n : ℕ) where

  ----------------------------------------------------------------------
  -- The variable space V = Fin n.
  ----------------------------------------------------------------------

  V : Set
  V = Fin n

  ----------------------------------------------------------------------
  -- Base: 2-variable K-rule assignments.
  ----------------------------------------------------------------------

  Assignment : Set
  Assignment = V × V

  ----------------------------------------------------------------------
  -- The invariant: distinctness pattern on the two slots.
  --
  -- Equivalent to: the partition refinement of {1, 2} into either
  -- {1, 2} (slots agree) or {1}{2} (slots distinct).
  ----------------------------------------------------------------------

  data DistPattern : Set where
    diagonal     : DistPattern
    off-diagonal : DistPattern

  ----------------------------------------------------------------------
  -- Projection: classify an assignment by distinctness.
  ----------------------------------------------------------------------

  dist : Assignment → DistPattern
  dist (v , w) with v ≟ w
  ... | yes _ = diagonal
  ... | no  _ = off-diagonal

  ----------------------------------------------------------------------
  -- Action: S_n acts on Assignment componentwise (diagonal action).
  --
  --   σ · (v, w) = (σ v, σ w)
  ----------------------------------------------------------------------

  sn-act : Permutation n → Assignment → Assignment
  sn-act σ (v , w) = applyₛ σ v , applyₛ σ w

  sn-act-id : (a : Assignment) → sn-act ε a ≡ a
  sn-act-id (v , w) = refl

  sn-act-∙ : (σ τ : Permutation n) (a : Assignment) →
             sn-act (σ · τ) a ≡ sn-act σ (sn-act τ a)
  sn-act-∙ σ τ (v , w) = refl

  action : Action S-Group Assignment
  action = record
    { act    = sn-act
    ; act-id = sn-act-id
    ; act-∙  = sn-act-∙
    }

  ----------------------------------------------------------------------
  -- Gauge invariance of dist.
  --
  -- The case analysis on `v ≟ w` and `applyₛ σ v ≟ applyₛ σ w`:
  --
  --   yes | yes  ⇒  both diagonal              ⇒  refl
  --   yes | no   ⇒  contradiction:                   the σ-image of a
  --                  diagonal pair is diagonal       (cong applyₛ σ)
  --   no  | yes  ⇒  contradiction:                   σ is injective,
  --                  so σ(v) = σ(w) ⇒ v = w          (σ-injective)
  --   no  | no   ⇒  both off-diagonal          ⇒  refl
  ----------------------------------------------------------------------

  dist-gauge-inv :
    (σ : Permutation n) (a : Assignment) →
    dist (sn-act σ a) ≡ dist a
  dist-gauge-inv σ (v , w) with v ≟ w | applyₛ σ v ≟ applyₛ σ w
  ... | yes _    | yes _      = refl
  ... | yes v≡w  | no  σv≢σw  = ⊥-elim (σv≢σw (cong (applyₛ σ) v≡w))
  ... | no  v≢w  | yes σv≡σw  = ⊥-elim (v≢w (σ-injective σ v w σv≡σw))
  ... | no  _    | no  _      = refl

  ----------------------------------------------------------------------
  -- WeakCocycleStructure packaging.
  ----------------------------------------------------------------------

  KRule-Cocycle : WeakCocycleStructure 0ℓ 0ℓ 0ℓ
  KRule-Cocycle = record
    { Base                    = Assignment
    ; Gauge                   = S-Group
    ; action                  = action
    ; Invariant               = DistPattern
    ; project                 = dist
    ; project-gauge-invariant = dist-gauge-inv
    }

------------------------------------------------------------------------
-- Notes
--
-- 1. Two orbits, not "infinitely many" — the cocycle classes are
--    determined purely by the distinctness pattern, independent of n
--    (for n ≥ 2; the off-diagonal orbit is empty when n ≤ 1). The
--    WeakCocycleStructure abstraction does not require enumerating
--    orbits or proving the orbit count; that's catalogue-level
--    detail, not abstraction-level.
--
-- 2. Why not IsomorphicCocycleStructure: filling `fiber-torsor`
--    requires the S_n action on each orbit to be free transitive.
--    For CY-2 it is transitive but not free — the diagonal orbit has
--    stabilizer S_{n-1} at each point, the off-diagonal S_{n-2}. The
--    abstraction layer's refusal to admit this as isomorphic-storage
--    is a feature: it surfaces the structural difference between
--    cocycles where the gauge acts freely (CY-5: V_4 on its torsors)
--    and those where it doesn't (CY-2: S_n on coset spaces).
--
-- 3. Connection to the catalogue's metacircularity claim: CY-2 is
--    described as "shown" with no Type-D drift recorded. The catalogue
--    does not claim CY-2 satisfies the strong (isomorphic) discipline;
--    the WeakCocycleStructure shape is the catalogue-faithful reading.
--
-- 4. Possible follow-ons (deferred):
--    - Prove the two orbits exist: ∃ representatives of `diagonal`
--      and `off-diagonal` for n ≥ 2.
--    - Prove orbit completeness: every Assignment is in exactly one
--      of the two orbits (a partition theorem).
--    - Decidability of orbit membership (trivial: lift `_≟_`).
------------------------------------------------------------------------
