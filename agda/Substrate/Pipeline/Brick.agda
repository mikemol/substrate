------------------------------------------------------------------------
-- Substrate.Pipeline.Brick
--
-- The base brick: a typed 2-cell in the substrate's three-axis
-- triangular witnessing structure.
--
-- Three sorts:
--   * D — Data: values flowing through (bytes, crumbs, signatures, ...)
--   * S — State: carriers being read/written (counts, grammar, ...)
--   * C — Compute: the algorithm being applied
--
-- Six oriented morphisms among the sorts, each witnessed by the third:
--
--   D⇒S  (write)             witnessed by C
--   S⇒D  (read)              witnessed by C
--   D⇒C  (data selects)      witnessed by S
--   C⇒D  (compute yields)    witnessed by S
--   S⇒C  (state dispatches)  witnessed by D
--   C⇒S  (parameterised      witnessed by D
--         mutation)
--
-- A brick is a typed step (D-in × S-in) → (D-out × S-out) together
-- with a Witnessing tag declaring which of the six morphisms it
-- primarily instantiates. The C axis is implicit: each brick's step
-- IS its compute.
--
-- Per [[project_eliza_concept_orbit_catalog]] and the dataflow remodel
-- (scratch/eliza/DATAFLOW_REMODEL.md), this is the type-theoretic
-- skeleton of the codec architecture's brick layer. The Python
-- implementation in scratch/eliza/eliza/ is a runtime witness of
-- these types.
--
-- Composition: two bricks compose along D and S edges iff their
-- types align (see Substrate.Pipeline.Composition). The C axes are
-- internal; composition does NOT require C-types to match.
--
-- Homomorphism: a brick declares the algebraic structure its step
-- preserves (e.g., S₄ group action, V₄ XOR, prefix-tree refinement).
-- The declaration is a field; verification is a separate concern
-- (left to per-instance lemmas).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick where

open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Level using (Level; _⊔_; suc) renaming (zero to lzero)

------------------------------------------------------------------------
-- 1. The six witnessings.
------------------------------------------------------------------------

data Witnessing : Set where
  D⇒S : Witnessing  -- write
  S⇒D : Witnessing  -- read
  D⇒C : Witnessing  -- data selects compute
  C⇒D : Witnessing  -- compute produces data
  S⇒C : Witnessing  -- state dispatches compute
  C⇒S : Witnessing  -- compute mutates state

-- The third-axis label that witnesses each morphism.
data Axis : Set where
  𝔻 : Axis  -- Data witnesses
  𝕊 : Axis  -- State witnesses
  ℂ : Axis  -- Compute witnesses

witness-axis : Witnessing → Axis
witness-axis D⇒S = ℂ
witness-axis S⇒D = ℂ
witness-axis D⇒C = 𝕊
witness-axis C⇒D = 𝕊
witness-axis S⇒C = 𝔻
witness-axis C⇒S = 𝔻

------------------------------------------------------------------------
-- 2. The brick type signature: four typed edges.
------------------------------------------------------------------------

record BrickType : Set₁ where
  field
    D-in  : Set
    D-out : Set
    S-in  : Set
    S-out : Set

------------------------------------------------------------------------
-- 3. The unit type for trivial edges (pure transforms / read-only).
------------------------------------------------------------------------

record ⊤ : Set where
  constructor tt

------------------------------------------------------------------------
-- 4. A brick: step function + witnessing tag + homomorphism declaration.
--
-- The homomorphism field is informational: it names the algebraic
-- structure the step preserves. Per-instance lemmas (in
-- Substrate.Pipeline.Examples or instance-specific modules) provide
-- proofs.
------------------------------------------------------------------------

record Brick (T : BrickType) : Set₁ where
  open BrickType T public
  field
    witnesses : Witnessing
    step      : D-in × S-in → D-out × S-out
    -- Informational: a label naming the preserved algebraic structure.
    -- Proofs are external (per-instance lemmas). Lives in Set₁ since
    -- the tag is itself a Set.
    homomorphism-tag : Set

------------------------------------------------------------------------
-- 5. Specialised brick shapes.
--
-- Pure transforms: no state. Witnessing is always D⇒S or S⇒D in the
-- general schema; for pure, both states are ⊤ and the brick is
-- effectively a typed function D-in → D-out.
--
-- Read-only queries: state is unchanged (S-in = S-out, step's second
-- component is identity on s).
--
-- Write-only updates: data is unchanged or absent (D-out = ⊤).
------------------------------------------------------------------------

record PureBrick (A B : Set) : Set₁ where
  field
    f : A → B
    homomorphism-tag : Set

-- Lift a pure transform to a full Brick (with trivial S edges).
pure→Brick : ∀ {A B : Set} → PureBrick A B → BrickType
pure→Brick {A} {B} P = record
  { D-in  = A
  ; D-out = B
  ; S-in  = ⊤
  ; S-out = ⊤
  }

pure→Brick-step : ∀ {A B : Set} → (P : PureBrick A B)
                → (A × ⊤) → (B × ⊤)
pure→Brick-step P (a , _) = PureBrick.f P a , tt

-- A pure transform is a Brick witnessing D⇒S (or equivalently a
-- typed function): D-in → D-out, with state irrelevant.
pure-as-brick : ∀ {A B : Set} → (P : PureBrick A B)
              → Brick (pure→Brick P)
pure-as-brick P = record
  { witnesses        = D⇒S
  ; step             = λ x → PureBrick.f P (proj₁ x) , tt
  ; homomorphism-tag = PureBrick.homomorphism-tag P
  }

------------------------------------------------------------------------
-- 6. Edge accessors (handy for composition).
------------------------------------------------------------------------

D-in-of : ∀ {T : BrickType} → Brick T → Set
D-in-of {T} _ = BrickType.D-in T

D-out-of : ∀ {T : BrickType} → Brick T → Set
D-out-of {T} _ = BrickType.D-out T

S-in-of : ∀ {T : BrickType} → Brick T → Set
S-in-of {T} _ = BrickType.S-in T

S-out-of : ∀ {T : BrickType} → Brick T → Set
S-out-of {T} _ = BrickType.S-out T

------------------------------------------------------------------------
-- 7. The triangular witnessing as a per-brick lemma obligation.
--
-- For each brick, the SPECIFIC witnessing is what the step function
-- "is" — a write (D⇒S), a read (S⇒D), a selector (D⇒C), etc. The
-- third axis acts as the categorical witness in the sense that
-- without it the morphism would not be type-coherent:
--
--   * D⇒S, S⇒D: the step's specific computation IS the witness on C.
--     C is the brick itself.
--   * D⇒C, C⇒D: the brick's S-edge holds the choice / intermediate.
--     S is the witness.
--   * S⇒C, C⇒S: the data passing through (D-in, D-out) is the
--     trigger / parameter. D is the witness.
--
-- This is the brick-level analogue of the substrate's Beck-Chevalley
-- square (Substrate.Category.BeckChevalley): three paths through a
-- square (the three sorts) with one commutativity witness (the third
-- axis).
------------------------------------------------------------------------
