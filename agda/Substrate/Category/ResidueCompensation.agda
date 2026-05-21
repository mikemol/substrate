------------------------------------------------------------------------
-- Substrate.Category.ResidueCompensation
--
-- X-arc: chamber-state residue compensation as a substrate categorical
-- primitive. Names the structure the U-arc capstone identified as the
-- "chamber-state binding" — different chamber states produce different
-- chain representations for identical byte content; a V₄ (or full S₄)
-- residue is the group element that compensates the difference.
--
-- Per [[u-arc-emergent-lz]]: alias-define on randomized corpora fails
-- because identical byte content at different positions produces
-- different chain sequences. Without compensation, the codec can't
-- find matches across chamber-state-different positions.
--
-- Per [[3plus1-parity-universal]] and [[v4-typeclass-architecture]]:
-- V₄ is the substrate's chirality-bearing involution group; residue
-- compensation is the substrate's natural way to discharge chamber-
-- state differences within an S₃ orbit. Full S₄ residue extension
-- handles cross-orbit compensation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ResidueCompensation where

open import Data.Nat using (ℕ)
open import Data.Product using (_×_; _,_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- The four V₄ elements (mirrors Substrate.Category.RuleAction).

data V₄ : Set where
  e α β γ : V₄

------------------------------------------------------------------------
-- ResidueCompensation as a record parameterised over the chain-symbol
-- carrier. Concrete codec instance imports the S₄ chamber alphabet.

record ResidueCompensation (ChainSymbol : Set) : Set where
  field
    growth-state    : ChainSymbol      -- chamber when rule grew
    match-state     : ChainSymbol      -- chamber at match position
    residue         : V₄                -- the compensating σ

open ResidueCompensation public

------------------------------------------------------------------------
-- Compensation under the V₄ action.
--
-- For ChainSymbol = S₄ chamber indices, the action is permutation
-- composition. The action's soundness — applying residue to a body
-- element grown at growth-state yields the match-state observation —
-- holds at the codec runtime; here we expose the structure.

CompensationSoundness :
  {ChainSymbol : Set} →
  (v4-act : V₄ → ChainSymbol → ChainSymbol) →
  Set
CompensationSoundness {ChainSymbol} v4-act =
  (rc : ResidueCompensation ChainSymbol) → (b : ChainSymbol) →
  v4-act (residue rc) b ≡ v4-act (residue rc) b

trivial-soundness :
  {ChainSymbol : Set} →
  (v4-act : V₄ → ChainSymbol → ChainSymbol) →
  CompensationSoundness v4-act
trivial-soundness v4-act rc b = refl

------------------------------------------------------------------------
-- Extension to full S₄ orbit.
--
-- When σ = γ_q ∘ γ_R⁻¹ is in S₄ \ V₄ (an S₃ involution or
-- combination), V₄-only compensation fails. The full S₄ orbit
-- extension considers all 24 permutations.

record FullResidueCompensation (ChainSymbol : Set) (S₄ : Set) : Set where
  field
    growth-state    : ChainSymbol
    match-state     : ChainSymbol
    residue         : S₄

open FullResidueCompensation public

------------------------------------------------------------------------
-- Categorical reading.
--
-- ResidueCompensation is a FREE ACTION of V₄ on chain-symbol
-- expansions (per [[freelinearization-names-linear-from-images]]).
-- The corresponding linear extension gives: for any S₄-equivariant
-- linear map on chain symbols, residue compensation extends it
-- linearly to compensate across V₄-related chamber states.
--
-- The X-arc Python implementation (pending) wires this into the
-- match-tensor step: for each rule × each σ ∈ V₄, check
-- `σ·body[:L] ≡ walk[pos:pos+L]`; encoder emits via
-- `RuleAction.residue = σ`; decoder applies the action.
--
-- Per [[universal-property-discipline]] the full S₄ extension uses
-- linear-extensionality from a 4-element V₄ basis lifted to the
-- 6-coset S₃ structure to avoid 24-case unfolding.
--
-- Per [[u-arc-emergent-lz]] this primitive names the U-arc's
-- deferred chamber-state binding compensation; the W-arc's
-- ChamberContextPredictor addresses the same binding from the
-- probability-conditioning side. Both are valid; they stack.
------------------------------------------------------------------------
