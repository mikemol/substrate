------------------------------------------------------------------------
-- Substrate.Axes.PartnerIsEdgeV4
--
-- Defines: partner-is-edge-v₄
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.PartnerIsEdgeV4 where

open import Substrate.Foundation.Eq
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Axes.Opposite using (partner)
open import Substrate.Axes.EdgePairing using (edge-v₄)


------------------------------------------------------------------------
-- THE PARTNER IS THE EDGE'S OWN V₄ ELEMENT, ACTING.
--
-- `partner s t` was defined as `act-axis (v-of-axis s · v-of-axis t) s`, and
-- `edge-v₄ s t` is that same product. So this holds by `refl` — which is the
-- point, not a weakness: it records that the two readings are ONE definition
-- rather than two that happen to agree.
--
-- ⚑ WHY IT IS WORTH STATING AT ALL. The pairing has three descriptions in
-- this repo and nothing had connected them as terms:
--   * `Axes.Opposite.partner` — "who is s paired with", an axis
--   * `EdgePairing.edge-v₄`   — "which matching", a V₄ element
--   * `Cocycles.V4Signature.Pairing.Type` — the matching as a NAMED datum
--     (α-pair/β-pair/γ-pair), bijective to V₄∖{e} (`Pairing↔V4-Nonzero`)
-- This is the first link of that chain. It says the axis-level answer is the
-- group-level answer applied, so a consumer may use whichever the context
-- wants without a translation step.
--
-- ⚑ AND IT MAKES `w-opposite` COMPUTED RATHER THAN SUPPLIED. `Axes.Signature`
-- carries `¬ (witness ≡ partner source sink)` as a FIELD, so every
-- construction site must produce that proof. With the partner exhibited as a
-- group action, the witness's block is decidable from `edge-v₄` — the
-- constraint becomes an evaluation, not an obligation.
------------------------------------------------------------------------

partner-is-edge-v₄ : (s t : Axis) → partner s t ≡ act-axis (edge-v₄ s t) s
partner-is-edge-v₄ s t = refl
