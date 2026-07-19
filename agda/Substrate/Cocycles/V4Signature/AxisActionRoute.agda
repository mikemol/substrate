------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.AxisActionRoute
--
-- ⟡axis-action-route — routes the CY-5 signature arc's V₄/pairing
-- structure through the WITNESS TOWER'S S₃-action, completing P2 at the
-- ACTION level (⟡apex-pin did the gauge-carrier level).
--
-- TWO ACTIONS, DIFFERENT CARRIERS ⇒ this is a naturality BRIDGE, not refl:
--   * TOWER: `rotate : V₄ → V₄` (S3-on-V4.Generators), the order-3 α→β→γ
--     Aut(V₄) generator = the S₃ of the tower's middle rung (WhyThreeV2).
--   * CY-5: `Pairing` = {α-pair,β-pair,γ-pair} = V₄'s three involutions as
--     axis-pairings, with the projection α↦α-pair, β↦β-pair, γ↦γ-pair.
--
-- ROUTE: `Pairing` is the shared carrier. The NATURALITY SQUARE below shows
-- projecting-then-rotateP = rotate-then-projecting on each involution — so
-- the tower's `rotate` DESCENDS along the projection to `rotateP`. The S₃
-- permuting the tower's middle rung IS the S₃ permuting CY-5's pairings
-- (Q-10 / OrbitKey-S3). Tower-manifest at the action level.
--
-- Zero postulates, --safe --without-K. Verified (agda 2.6.3).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.AxisActionRoute where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Cocycles.V4Signature.Pairing.Type using (Pairing; α-pair; β-pair; γ-pair)
open import Substrate.Cocycles.V4Signature.V4ToPairing using (V₄→Pairing; _≢_)  -- the REAL CY-5 projection + its ≢

------------------------------------------------------------------------
-- 1. The pairing rotate — the CY-5-side image of the tower's `rotate`.
--    Total (Pairing has no e), the same α→β→γ→α cycle.
------------------------------------------------------------------------

rotateP : Pairing → Pairing
rotateP α-pair = β-pair
rotateP β-pair = γ-pair
rotateP γ-pair = α-pair

------------------------------------------------------------------------
-- 2. Non-identity witnesses for the three involutions (V₄ is `data`, so
--    distinct constructors are absurd to equate — `λ ()`).
------------------------------------------------------------------------

α≢e : α ≢ e
α≢e ()
β≢e : β ≢ e
β≢e ()
γ≢e : γ ≢ e
γ≢e ()

------------------------------------------------------------------------
-- 3. THE NATURALITY SQUARE against the REAL CY-5 projection V₄→Pairing:
--       V₄→Pairing (rotate v) _  ≡  rotateP (V₄→Pairing v _)
--    for v ∈ {α,β,γ}. rotate maps involutions to involutions, so the
--    rotated input also has a ≢e witness. Both sides compute; refl.
--    This binds the descent to the ACTUAL cocycle projection, not a copy.
------------------------------------------------------------------------

square-α : V₄→Pairing (rotate α) β≢e ≡ rotateP (V₄→Pairing α α≢e)
square-α = refl   -- V₄→Pairing β = β-pair ; rotateP α-pair = β-pair

square-β : V₄→Pairing (rotate β) γ≢e ≡ rotateP (V₄→Pairing β β≢e)
square-β = refl   -- V₄→Pairing γ = γ-pair ; rotateP β-pair = γ-pair

square-γ : V₄→Pairing (rotate γ) α≢e ≡ rotateP (V₄→Pairing γ γ≢e)
square-γ = refl   -- V₄→Pairing α = α-pair ; rotateP γ-pair = α-pair

------------------------------------------------------------------------
-- 4. rotateP is order 3 (the descended action is genuinely the Z₃ = A₄/V₄
--    the cocycle's OrbitKey-S3 names — same cycle, now proven on Pairing).
------------------------------------------------------------------------

rotateP³ : (p : Pairing) → rotateP (rotateP (rotateP p)) ≡ p
rotateP³ α-pair = refl
rotateP³ β-pair = refl
rotateP³ γ-pair = refl
