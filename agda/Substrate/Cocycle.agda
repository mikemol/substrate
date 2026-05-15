------------------------------------------------------------------------
-- Substrate.Cocycle
--
-- The primary abstraction is `IsomorphicCocycleStructure` — the
-- type-level realisation of the catalog's strong discipline (rule 11
-- strong, isomorphic storage). The "base" type is DERIVED, not
-- primitive: it is a Σ-type whose first projection IS the invariant,
-- and each fiber over an invariant is a torsor for the gauge group
-- (free transitive action, no canonical origin).
--
-- This means:
--   * There is no separate `Base` field — only `Invariant` and `Fiber`.
--     The total space is `Σ Invariant Fiber`.
--   * There is no `project` function. The projection is the first
--     component of the Σ-type, definitionally.
--   * There is no canonical-relative coordinate in storage. The fiber
--     is a torsor; "canonical" is not part of the type structure.
--
-- The catalog's weak discipline (orbit-collapse with virtual recovery,
-- rule 11 weak) is expressed here as `WeakCocycleStructure` — a
-- separate compatibility shape. Any `IsomorphicCocycleStructure` can
-- be downcast to a `WeakCocycleStructure`; the converse requires
-- additional structure (a chosen canonical) and is what the rewrite
-- ELIMINATES rather than refines.
--
-- See:
--   * catalog/cocycles.md § Isomorphic storage — the deeper discipline
--   * catalog/cocycles.md § Orbit collapse with virtual recovery
--   * catalog/clarified_foundation.md rule 11 (strong vs weak)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycle where

open import Level using (Level; _⊔_; suc)
open import Algebra.Bundles using (Group)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)
open import Data.Product using (Σ; Σ-syntax; _×_; _,_; proj₁; proj₂; ∃)

------------------------------------------------------------------------
-- Group action on a type.
--
-- A left action of a group G on a set B. Used both for the fiber-
-- action in IsomorphicCocycleStructure (where B is each fiber) and
-- for total-space actions in the derived weak shape.
------------------------------------------------------------------------

record Action {ℓ ℓg : Level} (G : Group ℓg ℓg) (B : Set ℓ) : Set (ℓ ⊔ ℓg) where
  open Group G using () renaming (Carrier to ∣G∣; _∙_ to _·G_; ε to εG)
  field
    act     : ∣G∣ → B → B
    act-id  : (b : B) → act εG b ≡ b
    act-∙   : (g h : ∣G∣) (b : B) → act (g ·G h) b ≡ act g (act h b)

------------------------------------------------------------------------
-- Torsor: a set with a free, transitive group action.
--
-- A G-torsor is "G without a chosen identity" — a set on which G acts
-- by translation in a way that distinguishes any two points by a
-- unique group element, but where no specific point is privileged as
-- the "origin."
--
-- This is exactly what isomorphic storage requires of each orbit's
-- fiber: the 4 V_4-translates within an orbit form a V_4-torsor, with
-- no canonical baseline among them.
------------------------------------------------------------------------

record IsTorsor {ℓ ℓg : Level} (G : Group ℓg ℓg) (T : Set ℓ) : Set (ℓ ⊔ ℓg) where
  open Group G using () renaming (Carrier to ∣G∣; ε to εG)
  field
    action : Action G T
    -- Free: only the identity fixes any point.
    free : (g : ∣G∣) (t : T) → Action.act action g t ≡ t → g ≡ εG
    -- Transitive: any two points are connected by some group element.
    transitive : (t₁ t₂ : T) → ∃ λ g → Action.act action g t₁ ≡ t₂

------------------------------------------------------------------------
-- IsomorphicCocycleStructure — the PRIMARY abstraction.
--
-- A cocycle expressed under isomorphic-storage discipline:
--   * `Invariant` is the type of orbits (cohomology classes).
--   * For each invariant `i`, the fiber `Fiber i` is a G-torsor.
--   * The "operational" objects are pairs (i, t : Fiber i) — but
--     there is no canonical t per orbit.
--
-- Storage payload topology ≡ invariant space: every operationally
-- distinct value is (orbit-class, position-in-torsor). The orbit-
-- class IS the invariant; the position is gauge-equivalent across
-- the torsor, with no canonical choice.
------------------------------------------------------------------------

record IsomorphicCocycleStructure (ℓi ℓg : Level) : Set (suc (ℓi ⊔ ℓg)) where
  field
    Invariant : Set ℓi
    Gauge     : Group ℓg ℓg
    -- Fiber over each invariant — the elements of each orbit.
    Fiber     : Invariant → Set ℓi
    -- Each fiber is a G-torsor.
    fiber-torsor : (i : Invariant) → IsTorsor Gauge (Fiber i)

  -- The "total space" of operational values, derived as a Σ-type.
  -- Note: this is a definition, not a field — the total space is
  -- NOT primitive. There is no separate `Base` declaration.
  TotalSpace : Set ℓi
  TotalSpace = Σ Invariant Fiber

  -- The projection to the invariant is the first component of the
  -- Σ-type, definitionally. There is no `project` function as a
  -- separate field — the projection IS the type structure.
  project : TotalSpace → Invariant
  project = proj₁

------------------------------------------------------------------------
-- WeakCocycleStructure — the compatibility shape.
--
-- The weak (rule-11-weak) discipline: a base type with an explicit
-- projection to the invariant, parametrised canonicalisation
-- function, and gauge action on the base. This is the shape the
-- CURRENT substrate satisfies (applied_grammar.py + s4_structure.py).
--
-- Any IsomorphicCocycleStructure induces a WeakCocycleStructure (by
-- letting Base = TotalSpace, action = total-space action, project =
-- Σ.fst). The converse requires CHOOSING a canonical per orbit and is
-- exactly the move the strong discipline eliminates.
------------------------------------------------------------------------

record WeakCocycleStructure (ℓb ℓi ℓg : Level) : Set (suc (ℓb ⊔ ℓi ⊔ ℓg)) where
  field
    Base      : Set ℓb
    Gauge     : Group ℓg ℓg
    action    : Action Gauge Base
    Invariant : Set ℓi
    project   : Base → Invariant
    project-gauge-invariant :
      (g : Group.Carrier Gauge) (b : Base) →
      project (Action.act action g b) ≡ project b

------------------------------------------------------------------------
-- Downcast: every IsomorphicCocycleStructure yields a
-- WeakCocycleStructure on the TotalSpace.
--
-- This makes the relationship between the two disciplines explicit:
-- strong implies weak. The reverse direction (weak → strong) requires
-- additional structure (a choice of canonical per orbit), which is
-- precisely the Type-D rigidification the strong discipline rejects.
------------------------------------------------------------------------

module Downcast {ℓi ℓg : Level} (𝒞 : IsomorphicCocycleStructure ℓi ℓg) where

  open IsomorphicCocycleStructure 𝒞
  open Group Gauge using () renaming (Carrier to ∣G∣; ε to εG)

  -- The total-space action: (i, t) ↦ (i, g · t) — acts only on the
  -- fiber, preserves the invariant.
  total-act : ∣G∣ → TotalSpace → TotalSpace
  total-act g (i , t) = i , Action.act (IsTorsor.action (fiber-torsor i)) g t

  total-act-id : (x : TotalSpace) → total-act εG x ≡ x
  total-act-id (i , t) =
    cong (i ,_) (Action.act-id (IsTorsor.action (fiber-torsor i)) t)

  total-act-∙ : (g h : ∣G∣) (x : TotalSpace) →
                total-act (Group._∙_ Gauge g h) x ≡ total-act g (total-act h x)
  total-act-∙ g h (i , t) =
    cong (i ,_)
      (Action.act-∙ (IsTorsor.action (fiber-torsor i)) g h t)

  total-action : Action Gauge TotalSpace
  total-action = record
    { act    = total-act
    ; act-id = total-act-id
    ; act-∙  = total-act-∙
    }

  -- Projection is the first component; gauge-invariance is then
  -- definitional (total-act preserves the first component by
  -- construction).
  proj-gauge-inv :
    (g : ∣G∣) (x : TotalSpace) →
    project (total-act g x) ≡ project x
  proj-gauge-inv g (i , t) = refl

  weak : WeakCocycleStructure ℓi ℓi ℓg
  weak = record
    { Base                    = TotalSpace
    ; Gauge                   = Gauge
    ; action                  = total-action
    ; Invariant               = Invariant
    ; project                 = project
    ; project-gauge-invariant = proj-gauge-inv
    }

------------------------------------------------------------------------
-- Notes
--
-- 1. The fact that `proj-gauge-inv` reduces to `refl` is the
--    type-level expression of "the storage's invariant cannot be
--    changed by a gauge action." Under the strong discipline this is
--    a definitional equality, not a theorem to prove — the type
--    structure forbids the alternative.
--
-- 2. To recover a "canonical-representative" function under the
--    strong discipline you would need to PICK one fiber element per
--    invariant. This is exactly the move that rule 11 (strong)
--    forbids. The type system does not provide a generic way to do
--    it; any instance choosing a canonical must construct it
--    manually, which advertises the choice.
--
-- 3. Cubical Agda would let us strengthen "Fiber i is a G-torsor" to
--    "Fiber i is propositionally equivalent to G as a G-set." Under
--    cubical the strong discipline would be exact equality rather
--    than a torsor structure. Deferred to S5.
------------------------------------------------------------------------
