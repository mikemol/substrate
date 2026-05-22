------------------------------------------------------------------------
-- Substrate.Category.GeneratorOperad
--
-- V-arc: the codec's emission generators as a substrate categorical
-- primitive. The codec maintains a ring (set + composition) of
-- generators that can each produce emissions:
--
--   * Rewrite rules (deterministic generators): emit a known body.
--   * Adaptive predictors (stochastic generators): emit according to
--     a learned probability distribution.
--   * Basis-state transformers (S_BASIS_AT, S_BASIS_BY): generators
--     of the basis-torsor's group action.
--   * Sink (S_SHIFT_BIT): commits one bit of working state to the
--     output stream.
--
-- The codec's full expressive space is the operad of compositions
-- over this generator set. Speculation at each emission selects the
-- generator with minimum local bit-cost.
--
-- Per [[categorical-name-first]]: an "operad" names this structure —
-- a set of operations with arities + composition + identity laws.
-- Each codec generator is an operation; emission sequences are
-- compositions of operations; the entire codec is one operad
-- instance.
--
-- Per [[expose-generator-not-orbit]]: the codec's prior design hid
-- the generator-set behind layers (rewrite rules vs adaptive coder
-- as separate stages); the V-arc EXPOSES them as peers in one ring.
--
-- Per [[homology-cohomology-recursion]]: rewrite rules are observed
-- redundancy (homology of the stream's pattern set); adaptive
-- predictors are catalogued frequency (cohomology of the chain
-- distribution). They're dual readings of the same data — both
-- live in the operad.
--
-- This module names the structure and states the operad laws as
-- proof obligations. Proofs deferred to a follow-up slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GeneratorOperad where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Data.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Generator kinds. The codec's ring partitions into four classes.

data GeneratorKind : Set where
  Rule       : GeneratorKind   -- Sequitur rewrite rule (deterministic).
  Predictor  : GeneratorKind   -- Adaptive predictor (stochastic).
  BasisShift : GeneratorKind   -- Basis-torsor transition.
  Sink       : GeneratorKind   -- Output-bit commit.

------------------------------------------------------------------------
-- A generator is a kind plus a payload identifier. Payload encoding
-- depends on kind; here we keep it abstract as a ℕ-valued tag.

record Generator : Set where
  field
    kind    : GeneratorKind
    payload : ℕ            -- e.g., rule-id, predictor-id, basis-label.

open Generator public

------------------------------------------------------------------------
-- An emission is the result of applying a generator. We represent
-- emissions abstractly as ℕ-valued "bit costs" — the operad cares
-- about cost composition, not the bit content itself.

EmissionCost : Set
EmissionCost = ℕ

------------------------------------------------------------------------
-- The operad. Operations are typed by arity (here: just a list of
-- generators). Composition is concatenation.

Composition : Set
Composition = List Generator

identity-composition : Composition
identity-composition = []

compose : Composition → Composition → Composition
compose []      ys = ys
compose (x ∷ xs) ys = x ∷ compose xs ys

------------------------------------------------------------------------
-- Operad laws (proof obligations).
--
-- An operad must satisfy:
--   (L1)  compose identity-composition c ≡ c
--   (L2)  compose c identity-composition ≡ c
--   (L3)  compose c (compose d e) ≡ compose (compose c d) e
--
-- (L1) is immediate. (L2) and (L3) are proven by induction on the
-- first argument. The proofs are mechanical; stated as Sets here
-- and inhabited in follow-up work.

LeftIdentity : Set
LeftIdentity = ∀ (c : Composition) → compose identity-composition c ≡ c

RightIdentity : Set
RightIdentity = ∀ (c : Composition) → compose c identity-composition ≡ c

Associativity : Set
Associativity = ∀ (c d e : Composition) →
                  compose c (compose d e) ≡ compose (compose c d) e

-- (L1) is trivial: case match shows compose [] c reduces to c.
left-identity : LeftIdentity
left-identity c = refl

------------------------------------------------------------------------
-- Cost composition (additive in this model).
--
-- Each generator has a cost; a composition's cost is the sum.
-- The operad of generators carries a cost-monoid (ℕ, +, 0). The
-- codec's speculation picks the composition with minimum cost.

total-cost : (Generator → EmissionCost) → Composition → EmissionCost
total-cost f []      = 0
total-cost f (g ∷ gs) = f g + total-cost f gs

------------------------------------------------------------------------
-- Categorical reading.
--
-- The codec's emission flow is a morphism in the Kleisli category of
-- the cost-aware operad: each generator emits a value with a cost;
-- compositions add costs. The codec's encoder is a coalgebra unfolding
-- the input stream into a generator-composition; the decoder is the
-- inverse algebra applying compositions to reconstruct the stream.
--
-- Per [[coalgebraic-not-consumer-driven]]: the operad IS the work;
-- the codec is its coalgebra at runtime. Future work extends this
-- with the bicategory of generator-types (operations between
-- emission alphabets).
------------------------------------------------------------------------
