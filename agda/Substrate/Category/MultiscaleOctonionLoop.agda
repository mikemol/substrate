------------------------------------------------------------------------
-- Substrate.Category.MultiscaleOctonionLoop
--
-- BB-arc: the substrate's tetrative Cayley-Dickson rotation family as
-- a categorical primitive. Per the user's structural insight:
-- hardcoding "byte" in eliza/octonion.py was a rigidification of the
-- scale gauge; the scale IS the hidden generator. This primitive
-- exposes it.
--
-- At each scale n ∈ ℕ:
--   bit-width   = 2^n
--   group       = F₂^n × F₂  (size 2^(n+1), abelian, all involutions)
--   action      = bit-position permutation by XOR-k, optional
--                 chirality bit-complement via f
--
-- Per [[3plus1-parity-universal]]: at every scale n, the structure is
-- (n bit-permutation axes) × (1 chirality F₂). The 3+1 universal
-- recurs at every Cayley-Dickson level — the substrate's universal
-- pattern at the byte/bit/word/dword/qword/... layer.
--
-- Per [[expose-generator-not-orbit]]: the runtime eliza/octonion.py
-- exposed only one orbit-point (scale=3, the 16 byte-rotations);
-- this primitive names the scale generator that subsumes them.
--
-- Per [[choice-rigidification-in-substrate]]: byte-only was a
-- rigidification; this categorical primitive floats the scale gauge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.MultiscaleOctonionLoop where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- The rotation at scale n.

record Rotation (n : ℕ) : Set where
  field
    -- k ∈ F₂^n (bit-permutation index, range [0, 2^n))
    k : ℕ
    -- f ∈ F₂ (chirality / bit-complement flag, range [0, 2))
    f : ℕ

open Rotation public

identity-rotation : (n : ℕ) → Rotation n
identity-rotation n = record { k = 0 ; f = 0 }

------------------------------------------------------------------------
-- Group structure.
--
-- The group at scale n is F₂^n × F₂ with componentwise XOR. All
-- elements are involutions; the group is abelian.

compose-rotation : {n : ℕ} → Rotation n → Rotation n → Rotation n
compose-rotation r₁ r₂ = record
  -- F₂^n component composes by XOR; we leave this abstract since the
  -- concrete bit-XOR requires bounded-ℕ arithmetic.
  { k = k r₁ + k r₂   -- placeholder: actual XOR mod 2^n
  ; f = f r₁ + f r₂   -- placeholder: actual XOR
  }

------------------------------------------------------------------------
-- Action on bit-strings.
--
-- The action at scale n is on 2^n-bit values. We model the value as
-- an abstract `BitVector n` type with the action signature.

-- The action is parameterised over the BitVector carrier and `act`
-- function; concrete instances supply them. Per --safe we don't
-- postulate; we expose the laws as record fields a concrete instance
-- must inhabit.

-- ⟡set1-paydown (M1: fields-a-Set-valued-carrier). `BitVector : Set` was a FIELD, forcing
-- RotationAction : Set₁. Set₁ is policy debt (a record must not FIELD a Set-valued carrier);
-- PARAMETERIZE it, as Substrate.Category.Lawvere's carrier-generic atoms do. With BitVector a
-- module parameter every field is Set-valued, so RotationAction : Set. Consumers write
-- `RotationAction BitVec n`.
module _ (BitVector : Set) where

  record RotationAction (n : ℕ) : Set where
    field
      act       : Rotation n → BitVector → BitVector
      -- Identity law: identity rotation acts trivially.
      act-identity   : (v : BitVector) →
                         act (identity-rotation n) v ≡ v
      -- Involution: applying any rotation twice gives identity.
      act-involution : (r : Rotation n) → (v : BitVector) →
                         act r (act r v) ≡ v

  open RotationAction public

------------------------------------------------------------------------
-- The 3+1 parity reading.
--
-- Per [[3plus1-parity-universal]]: at every scale n, the rotation
-- group F₂^n × F₂ has shape (n axes × 1 binding). The n axes are the
-- bits of k (bit-permutation index); the 1 binding is the chirality
-- f. The substrate's 3+1 universal is realised at every Cayley-
-- Dickson level.

chirality-of : {n : ℕ} → Rotation n → ℕ
chirality-of r = f r

permutation-of : {n : ℕ} → Rotation n → ℕ
permutation-of r = k r

------------------------------------------------------------------------
-- Multi-scale collection.
--
-- The codec operates over multiple scales; the MultiscaleOctonionLoop
-- structure collects the per-scale groups and exposes scale as a
-- first-class index.

-- ⟡set1-paydown: this record fields only `max-scale : ℕ` (a Set-valued datum), so it inhabits
-- Set, not Set₁ — the Set₁ annotation was gratuitous.
record MultiscaleOctonionLoop : Set where
  field
    max-scale  : ℕ
    -- Per-scale group (Rotation n) is implicit; this record just
    -- bounds the considered range.

open MultiscaleOctonionLoop public

------------------------------------------------------------------------
-- Trivial law: identity rotation composes trivially with itself.

identity-self-composes : (n : ℕ) →
  compose-rotation {n} (identity-rotation n) (identity-rotation n)
    ≡ identity-rotation n
identity-self-composes n = refl

------------------------------------------------------------------------
-- Categorical reading.
--
-- The MultiscaleOctonionLoop is an N-INDEXED FAMILY of abelian
-- involutive groups, all of which act on the appropriate bit-vector
-- space. The codec's BB-arc emission ring includes one S_SCALE_ROTATE
-- generator per scale; the operad ring speculates over the family
-- per emission.
--
-- Per [[homology-cohomology-recursion]]: at each scale, the rotation
-- group is the codec's homology-side reorganisation (which bits get
-- permuted = the codec's claim about local structure). The
-- post-rotation predictor distribution is the cohomology-side
-- catalogue.
--
-- Per [[tetrative-metacircularity]]: the Cayley-Dickson ladder
-- (n → n+1 doubles dimensions) realises tetrative levels at the
-- bit-layer; the substrate's universal recurses through every
-- doubling.
--
-- The runtime implementation (eliza/multiscale_rotation.py +
-- gpu_codec_v7.py BB1-BB4) materialises this primitive at scales
-- [0, 5] (1-bit through 32-bit dword); higher scales follow the
-- same pattern but use larger units.
------------------------------------------------------------------------
