------------------------------------------------------------------------
-- Substrate.Pipeline.Composition
--
-- Composing bricks into pipelines. Two bricks compose along D and S
-- edges iff their types align; the C axes are internal. A pipeline
-- is a sequence (or DAG) of bricks whose edge-types align pairwise.
--
-- The composition is type-coherent: we use propositional equality on
-- Set to require alignment, which forces well-typed pipelines at
-- construction time.
--
-- For a more flexible DAG (multiple parallel branches), see the
-- combinators below: Tee, Tap, Product. Each is a brick-of-bricks
-- with explicit splitting/merging semantics.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Composition where

open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; cong; sym)
open import Substrate.Pipeline.Brick

------------------------------------------------------------------------
-- 1. Sequential composition.
--
-- b₁ : Brick T₁ and b₂ : Brick T₂ compose into Brick (compose T₁ T₂)
-- iff D-out T₁ ≡ D-in T₂ and S-out T₁ ≡ S-in T₂.
------------------------------------------------------------------------

-- The composite brick's type.
compose-type : (T₁ T₂ : BrickType)
             → BrickType.D-out T₁ ≡ BrickType.D-in T₂
             → BrickType.S-out T₁ ≡ BrickType.S-in T₂
             → BrickType
compose-type T₁ T₂ _ _ = record
  { D-in  = BrickType.D-in  T₁
  ; D-out = BrickType.D-out T₂
  ; S-in  = BrickType.S-in  T₁
  ; S-out = BrickType.S-out T₂
  }

-- Sequential composition of two bricks.
--
-- The composite step is: apply b₁ to (d, s); rewrite via the edge
-- equalities; apply b₂.
compose : ∀ {T₁ T₂}
        → (b₁ : Brick T₁)
        → (b₂ : Brick T₂)
        → (d-eq : BrickType.D-out T₁ ≡ BrickType.D-in T₂)
        → (s-eq : BrickType.S-out T₁ ≡ BrickType.S-in T₂)
        → Brick (compose-type T₁ T₂ d-eq s-eq)
compose {T₁} {T₂} b₁ b₂ refl refl = record
  { witnesses = Brick.witnesses b₁  -- the composite's witnessing is
                                     -- the leftmost (entry) brick's
                                     -- — refined further per-composite
                                     -- in higher modules
  ; step      = λ (d , s) →
                  let mid = Brick.step b₁ (d , s)
                  in Brick.step b₂ mid
  ; homomorphism-tag = ⊤  -- composite preserves what BOTH preserve;
                          -- specific tags belong to per-instance lemmas
  }

------------------------------------------------------------------------
-- 2. Tee: pass-through with side-channel observation.
--
-- Given a brick b and an observer obs (a read-only function on b's
-- output edges), produce a brick that runs b normally AND emits the
-- observed value as a side-channel. The side channel is part of S-out
-- (the observer's effect lands in state).
--
-- This is the "Tap"/"Tee" combinator from the catalog: it implements
-- the Read role.
------------------------------------------------------------------------

record Observer (T : BrickType) (O : Set) : Set where
  open BrickType T
  field
    observe : D-out × S-out → O

-- Tee adds an observer's output to the state (S-out becomes S-out × O).
tee-type : (T : BrickType) → (O : Set) → BrickType
tee-type T O = record
  { D-in  = BrickType.D-in T
  ; D-out = BrickType.D-out T
  ; S-in  = BrickType.S-in T
  ; S-out = BrickType.S-out T × O
  }

tee : ∀ {T O} → (b : Brick T) → (obs : Observer T O)
    → Brick (tee-type T O)
tee b obs = record
  { witnesses = Brick.witnesses b
  ; step      = λ (d , s) →
                  let (d' , s') = Brick.step b (d , s)
                      o         = Observer.observe obs (d' , s')
                  in d' , (s' , o)
  ; homomorphism-tag = Brick.homomorphism-tag b
  }

------------------------------------------------------------------------
-- 3. Product: the DirectProduct 2-cell.
--
-- Given two bricks operating on the same data axis with different
-- state axes, plus a chooser that selects between their outputs,
-- produce a composite brick whose state holds both. The chooser IS
-- the 2-cell witnessing coherence between the two layers.
--
-- This is the substrate's DirectProduct (Substrate.Groups.Coxeter.
-- DirectProduct) at the brick layer.
------------------------------------------------------------------------

record Chooser (T₁ T₂ : BrickType) : Set where
  open BrickType T₁ renaming (D-out to D-out₁; S-out to S-out₁)
  open BrickType T₂ renaming (D-out to D-out₂; S-out to S-out₂)
  field
    select : D-out₁ × D-out₂ × S-out₁ × S-out₂ → D-out₁
    -- The chooser picks one of the two output streams. (For more
    -- complex selections, generalise this signature; see
    -- DATAFLOW_REMODEL.md's Chooser decomposition into
    -- score / selection / coupling.)

-- The product brick requires shared D-in but allows independent S.
product-type : (T₁ T₂ : BrickType)
             → BrickType.D-in T₁ ≡ BrickType.D-in T₂
             → BrickType.D-out T₁ ≡ BrickType.D-out T₂
             → BrickType
product-type T₁ T₂ _ _ = record
  { D-in  = BrickType.D-in T₁
  ; D-out = BrickType.D-out T₁
  ; S-in  = BrickType.S-in T₁ × BrickType.S-in T₂
  ; S-out = BrickType.S-out T₁ × BrickType.S-out T₂
  }

product : ∀ {T₁ T₂}
        → (b₁ : Brick T₁)
        → (b₂ : Brick T₂)
        → (din-eq : BrickType.D-in T₁ ≡ BrickType.D-in T₂)
        → (dout-eq : BrickType.D-out T₁ ≡ BrickType.D-out T₂)
        → (c : Chooser T₁ T₂)
        → Brick (product-type T₁ T₂ din-eq dout-eq)
product {T₁} {T₂} b₁ b₂ refl refl c = record
  { witnesses = D⇒C   -- The product is fundamentally a D⇒C
                       -- (data selects between two computes)
                       -- witnessed by S (each layer's state)
  ; step      = λ (d , (s₁ , s₂)) →
                  let (d₁ , s₁') = Brick.step b₁ (d , s₁)
                      (d₂ , s₂') = Brick.step b₂ (d , s₂)
                      chosen = Chooser.select c (d₁ , d₂ , s₁' , s₂')
                  in chosen , (s₁' , s₂')
  ; homomorphism-tag = ⊤
  }

------------------------------------------------------------------------
-- 4. Type-level edge alignment is a constructive proof obligation.
--
-- A pipeline (n-brick chain) is constructed by repeated `compose`,
-- each step requiring two `refl`-style proofs of D and S alignment.
-- This forces every pipeline to be type-coherent BY CONSTRUCTION;
-- there is no way to build an ill-typed pipeline.
--
-- Per substrate convention: this is the brick-layer analogue of the
-- Beck-Chevalley square commuting condition. The square's two paths
-- (the two compositions: b₁ ∘ id vs id ∘ b₂) commute trivially when
-- the edge equalities are refl.
------------------------------------------------------------------------
