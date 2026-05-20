------------------------------------------------------------------------
-- Substrate.Category.RuleAction
--
-- U-arc: the codec's RuleAction abstraction lifted to a substrate
-- categorical primitive. Recognises that each emission of a rule
-- reference carries an algebraic action `a ∈ A` applied to the
-- rule's expansion before contribution to the chain.
--
-- A is a product monoid:
--
--   A = V₄ × AffineProjection × F₂Patch × SpanCoupling
--
-- where:
--   V₄              = Coxeter group of order 4 (existing residue).
--   AffineProjection = (start_phase, length_mask) — subsumes LZ77.
--   F₂Patch          = sparse F₂ correction vector — subsumes fuzzy
--                       match via Hodge-bivector flip pattern.
--   SpanCoupling     = (rule_right, overlap_mask) — subsumes B-frame
--                       bidirectional reference.
--
-- The first three factors are commutative; SpanCoupling is NOT — it
-- carries H-rung non-commutativity (which rule is "left" vs "right"
-- matters). The product is therefore a semi-direct product, not a
-- direct product, when the span factor is engaged.
--
-- Per [[categorical-name-first]]: this structure is a monoid acting
-- on the type `Rules` — equivalently, A is a monoid object internal
-- to (Rules → Rules). The categorical name is "monoid action on a
-- set"; the substrate-internal name `RuleAction` is the carrier.
--
-- Per [[grothendieck-coherence-rule]]: the action must satisfy
--   * identity:    apply 1_A r ≡ r
--   * compose:     apply (a₁ ∘ a₂) r ≡ apply a₁ (apply a₂ r)
-- Proof obligations stated below; not yet discharged (the proofs
-- are mechanical record-update lemmas under positive sparsity, and
-- require additional V₄-action infrastructure for the residue factor).
--
-- Per [[expose-generator-not-orbit]]: the four factors of A are the
-- generators of the action algebra. Each opcode in the runtime codec
-- is an orbit-element under a specific generator combination.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction where

open import Data.Nat using (ℕ; zero; suc; _+_)
open import Data.Bool using (Bool; true; false)
open import Data.List using (List; []; _∷_)
open import Data.Maybe using (Maybe; just; nothing)
open import Data.Product using (_×_; _,_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- V₄ residue: Coxeter framework requires a presentation; we mirror
-- the codec's runtime by indexing residues as Fin 4 (the four V₄
-- elements). Composition is XOR on the two underlying Z/2 indices.

data V₄ : Set where
  e α β γ : V₄

-- Composition table (mirrors eliza/rule_action.py:_V4_COMPOSE).
_∘V_ : V₄ → V₄ → V₄
e ∘V x = x
α ∘V e = α
α ∘V α = e
α ∘V β = γ
α ∘V γ = β
β ∘V e = β
β ∘V α = γ
β ∘V β = e
β ∘V γ = α
γ ∘V e = γ
γ ∘V α = β
γ ∘V β = α
γ ∘V γ = e

------------------------------------------------------------------------
-- A factor: affine projection on a rule's body.

record AffineProjection : Set where
  field
    start-phase : ℕ
    length-mask : Maybe ℕ    -- nothing = "use full suffix"

open AffineProjection

identity-affine : AffineProjection
identity-affine = record { start-phase = 0 ; length-mask = nothing }

------------------------------------------------------------------------
-- A factor: F₂-patch as a list of (index, replacement) substitutions.
-- Sparsity = list length; identity patch = empty list.
-- The values are chain-symbol indices (Fin 24 in the codec runtime;
-- here ℕ for generic substrate use).

F₂Patch : Set
F₂Patch = List (ℕ × ℕ)

identity-patch : F₂Patch
identity-patch = []

------------------------------------------------------------------------
-- A factor: SpanCoupling — bifilar reference. A right-rule identifier
-- + an overlap mask describing which positions come from the right
-- rule's expansion vs the left.

record SpanCoupling : Set where
  field
    rule-right   : Maybe ℕ      -- nothing = no span engaged
    overlap-mask : List Bool    -- F₂ vector

open SpanCoupling

identity-span : SpanCoupling
identity-span = record { rule-right = nothing ; overlap-mask = [] }

------------------------------------------------------------------------
-- The full action algebra A.

record RuleAction : Set where
  field
    residue       : V₄
    affine        : AffineProjection
    f2-patch      : F₂Patch
    span-coupling : SpanCoupling

open RuleAction public

identity : RuleAction
identity = record
  { residue       = e
  ; affine        = identity-affine
  ; f2-patch      = identity-patch
  ; span-coupling = identity-span
  }

------------------------------------------------------------------------
-- Composition. The first three factors compose componentwise; the
-- span factor is non-commutative — its composition picks the first
-- non-trivial coupling.

compose-affine : AffineProjection → AffineProjection → AffineProjection
compose-affine a₁ a₂ = record
  { start-phase = start-phase a₁ + start-phase a₂
  ; length-mask = pick-length (length-mask a₁) (length-mask a₂)
  }
  where
    pick-length : Maybe ℕ → Maybe ℕ → Maybe ℕ
    pick-length (just l) _ = just l
    pick-length nothing  m = m

-- Patch composition is XOR-style: union of indices, with later
-- substitutions overwriting earlier ones at the same index. For
-- simplicity (and to match Python's tuple-of-pairs semantics) we
-- concatenate and let the runtime resolve duplicates.
compose-patch : F₂Patch → F₂Patch → F₂Patch
compose-patch []      ys = ys
compose-patch (x ∷ xs) ys = x ∷ compose-patch xs ys

-- Span composition: non-commutative; the FIRST non-trivial coupling
-- wins (matches Python's `a.span_coupling or b.span_coupling`).
compose-span : SpanCoupling → SpanCoupling → SpanCoupling
compose-span s₁ s₂ with rule-right s₁
... | just _  = s₁
... | nothing = s₂

compose : RuleAction → RuleAction → RuleAction
compose a b = record
  { residue       = residue a ∘V residue b
  ; affine        = compose-affine (affine a) (affine b)
  ; f2-patch      = compose-patch (f2-patch a) (f2-patch b)
  ; span-coupling = compose-span (span-coupling a) (span-coupling b)
  }

------------------------------------------------------------------------
-- Action laws (proof obligations).
--
-- The categorical-name "monoid action" requires:
--   (L1)  compose identity a ≡ a
--   (L2)  compose a identity ≡ a
--   (L3)  compose a (compose b c) ≡ compose (compose a b) c
--
-- Under --safe these are not postulates; they would be mechanical
-- record-decomposition proofs. The first two follow from the
-- identity properties of `_∘V_`, `compose-affine`, `compose-patch`,
-- `compose-span`. The third (associativity) is non-trivial because
-- `compose-span` is non-commutative — the "first non-trivial coupling
-- wins" rule must be associative under repeated composition. Proof
-- sketch: case analysis on whether each input's `rule-right` is
-- `nothing` or `just _`; in each case both sides reduce to the same
-- `SpanCoupling` record.
--
-- The proofs are deferred to a follow-up slice. For the U-arc
-- capstone they are stated as types but not inhabited:

LeftIdentity  : Set
LeftIdentity  = ∀ (a : RuleAction) → compose identity a ≡ a

RightIdentity : Set
RightIdentity = ∀ (a : RuleAction) → compose a identity ≡ a

Associativity : Set
Associativity = ∀ (a b c : RuleAction) →
                  compose a (compose b c) ≡ compose (compose a b) c

-- The action `apply : RuleAction → Body → Body` (where Body is a
-- chain-symbol list) is defined at the runtime layer (eliza/
-- rule_action.py); its categorical name is "left action of the
-- monoid (RuleAction, compose, identity) on the type `List ℕ`."
------------------------------------------------------------------------
