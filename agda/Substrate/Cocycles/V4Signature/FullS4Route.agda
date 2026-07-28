------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.FullS4Route
--
-- ⟡full-s4-route — the CAPSTONE of P2: the CY-5 cocycle's entire 24-element
-- TotalSpace is carried onto the WITNESS TOWER'S CARRIER AT RUNG 3, not
-- factor-by-factor (⟡apex-pin gave the V₄ gauge; ⟡axis-action-route gave the
-- S₃ rotate) but as a single bijection of the whole structure.
--
-- IMPORTANT FRAMING: S₄ is the tower AT RUNG 3, NOT the tower's top. The
-- witness tower is an unbounded witnessed simplex (Substrate.WitnessTower.Sn
-- / Core: each rung k is a simplex of k+1 nodes witnessing the (k−1)-rung,
-- for arbitrary k). rung 3 = V₄⋊(Z₃⋊Z₂) = S₄ is where CY-5 lives; the tower
-- continues to S₅, S₆, … above it. So this term reads "CY-5's 24 ARE the
-- tower's rung-3 elements", a specific finite level of an infinite spine —
-- NOT "CY-5 ≅ the whole tower".
--
-- NOT A REINVENTION — a COMPOSITION of three already-built, in-tree bridges:
--   (1) CY-5:       total-to-s4 / s4-to-total   : TotalSpace ↔ Permutation
--                   (S4Iso.Classify; the "24 ARE S₄" bijection)
--   (2) S4-Iso:     perm-to-compositional / compositional-to-perm
--                   : Permutation ↔ S4-Composed.Carrier  (+ perm-roundtrip-≈)
--   (3) tower:      whole-tower = S4-Composed.S₄-Group  (WholeTower), whose
--                   carrier IS S4C.Carrier = the rung-3 object.
-- Composing (1)∘(2) lands TotalSpace in the tower's rung-3 carrier.
--
-- Zero postulates, --safe --without-K. Verified (agda 2.6.3) with full cone
-- (incl. WholeTower + S4-Iso).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.FullS4Route where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

import Substrate.Groups.S4-Composed as S4C

-- (1) CY-5's TotalSpace ↔ Permutation
open import Substrate.Cocycles.V4Signature.S4Iso.Classify
  using (TotalSpace; total-to-s4; s4-to-total)

-- (2) Permutation ↔ tower's compositional carrier, + the roundtrip
open import Substrate.Groups.S4-Iso.Extract    using (perm-to-compositional)
open import Substrate.Groups.S4-Iso.Embedding  using (compositional-to-perm)
open import Substrate.Groups.S4-Iso.Roundtrip  using (perm-roundtrip-≈)
open import Substrate.Cocycles.V4Signature.S4GroupIso   using (≈-respects-s4-to-total)
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips using (total-round-trip)
open import Substrate.Axes.Axis
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.EqRefl Axis

-- (3) the tower's rung-3 carrier is exactly S4C.Carrier
TowerRung3 : Set
TowerRung3 = S4C.Carrier

------------------------------------------------------------------------
-- The composed maps: CY-5 TotalSpace ↔ tower rung-3 carrier.
------------------------------------------------------------------------

total-to-tower : TotalSpace → TowerRung3
total-to-tower t = perm-to-compositional (total-to-s4 t)

tower-to-total : TowerRung3 → TotalSpace
tower-to-total c = s4-to-total (compositional-to-perm c)

------------------------------------------------------------------------
-- ONE HALF OF THE BIJECTION, from an already-proven ingredient:
-- on the Permutation waypoint, perm-roundtrip-≈ gives
--   compositional-to-perm (perm-to-compositional σ) ≈ σ,
-- so tower-to-total ∘ total-to-tower agrees with s4-to-total ∘ (≈ id on σ).
-- We expose the waypoint identity directly (the reusable content); the full
-- TotalSpace-level roundtrip needs s4-to-total to respect _≈_ (which
-- S4GroupIso.s4-to-total-cong provides — see ⟡full-s4-cong to close it).
------------------------------------------------------------------------

-- the middle roundtrip (proven upstream): the Permutation waypoint returns.
route-waypoint-≈ :
  (t : TotalSpace) →
  compositional-to-perm (total-to-tower t) ≈ total-to-s4 t
route-waypoint-≈ t = perm-roundtrip-≈ (total-to-s4 t)

------------------------------------------------------------------------
-- THE CLOSED ROUNDTRIP: tower-to-total ∘ total-to-tower ≡ id on TotalSpace.
-- Chain: s4-to-total respects ≈ (≈-respects-s4-to-total) rewrites the inner
-- permutation along route-waypoint-≈ to `total-to-s4 t`; then CY-5's own
-- total-round-trip collapses s4-to-total (total-to-s4 t) ≡ t. Pure
-- composition of in-tree lemmas — no new grind.
------------------------------------------------------------------------

tower-total-roundtrip :
  (t : TotalSpace) → tower-to-total (total-to-tower t) ≡ t
tower-total-roundtrip t =
  trans (≈-respects-s4-to-total
           (compositional-to-perm (total-to-tower t))
           (total-to-s4 t)
           (route-waypoint-≈ t))
        (total-round-trip t)

-- Reading: the 24-element CY-5 cocycle TotalSpace embeds into the tower's
-- rung-3 carrier by total-to-tower, and tower-to-total recovers it exactly
-- (≡). So CY-5's "the 24 ARE S₄" is now "the 24 ARE the witness tower's
-- rung-3 elements" — a checked injection with a left inverse into the tower,
-- which itself continues to arbitrary Sₙ above rung 3. P2 capstone.
