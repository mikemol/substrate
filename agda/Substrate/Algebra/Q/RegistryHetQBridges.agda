------------------------------------------------------------------------
-- Substrate.Algebra.Q.RegistryHetQBridges
--
-- Ⓡ⇄Ⓗ.registry-hetq-bridges — the connection leaf wiring the Wedge
-- REGISTRY (the foundational quotient-algebra anchor: objects / morphisms /
-- bridges, Algebra.Wedge.Registry) to the HetQ COSPAN (the heterogeneous-ℚ
-- cross-multiply, Algebra.Q.HetCrossMix). The two halves:
--
--   * Registry side — `objects` carry ℤ-div and ℕ-div as wedge-founded roots,
--     and `bridges` lists `include-ℕℤ` (ℕ ↪ ℤ) as a living cross-root edge
--     (a genuine `Bridge`, non-invertible, hence a BridgeEntry not a Morphism).
--   * HetQ side — `ℚ-crossmix : CrossMix ℤ-div ℕ-div ℤ-mul` is the cospan
--     ℤ-div →(id) ℤ ←(ℕ↪ℤ) ℕ-div whose two codec legs `embA`, `embB` ARE
--     Bridges and whose `cross` IS ℚ's cross-multiplication.
--
-- CLAIM: the HetQ codec bridges are NOT new machinery — they are EXACTLY the
-- foundational Registry bridges. `embA ℚ-crossmix` is the identity bridge on
-- ℤ-div (the numerator is already in ℤ); `embB ℚ-crossmix` is `include-ℕℤ`,
-- the very inclusion bridge the Registry registers. Both equalities hold by
-- refl (the bridges ARE the same objects), and the cospan's denominator leg,
-- packaged as a `BridgeEntry`, is structurally identical to the Registry's
-- ℕ↪ℤ entry. So the HetQ cospan structure IS a Registry BridgeEntry.
--
-- Connection leaf: re-export + refl, one structural identity. Zero postulates,
-- --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.RegistryHetQBridges where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; id-bridge)
open import Substrate.Algebra.Wedge.InclusionBridge using (include-ℕℤ)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; embA; embB)
open import Substrate.Algebra.Wedge.Registry using (BridgeEntry; bridges; ObjCode; ℕ'; ℤ')
open import Substrate.Algebra.Q.HetCrossMix using (ℚ-crossmix; ℤ-mul)

------------------------------------------------------------------------
-- 1. The two codec legs of the HetQ cospan are the foundational bridges.
--    Both by refl — `ℚ-crossmix` was BUILT from exactly these bridges, so
--    the projections recover them definitionally. The point is not that the
--    proof is hard; it is that nothing NEW was constructed for HetQ — the
--    cross-multiply rides on the Registry's pre-existing edges.
------------------------------------------------------------------------

-- numerator leg: the identity bridge on ℤ-div (num is already an integer).
hetq-embA-is-id : embA ℚ-crossmix ≡ id-bridge ℤ-div
hetq-embA-is-id = refl

-- denominator leg: the Registry's ℕ↪ℤ inclusion bridge (the non-negative
-- coercion) — the very `include-ℕℤ` listed in `Registry.bridges`.
hetq-embB-is-include : embB ℚ-crossmix ≡ include-ℕℤ
hetq-embB-is-include = refl

-- the conjunction, as the sketch states it.
hetq-bridges-in-registry :
  (embA ℚ-crossmix ≡ id-bridge ℤ-div) × (embB ℚ-crossmix ≡ include-ℕℤ)
hetq-bridges-in-registry = hetq-embA-is-id , hetq-embB-is-include

------------------------------------------------------------------------
-- 2. The HetQ denominator leg, packaged as a Registry BridgeEntry, IS the
--    Registry's ℕ↪ℤ entry. A BridgeEntry is now Σ ObjCode (λ a → Σ ObjCode
--    (λ b → Bridge (objDivStr a) (objDivStr b))) — coded endpoints; the entry
--    built from the cospan's leg coincides (refl) with `Registry.bridges`'
--    inclusion entry `(ℕ' , ℤ' , include-ℕℤ)`. So the cospan's structure does
--    not extend the Registry — it instantiates one of its entries.
------------------------------------------------------------------------

-- the HetQ denominator leg as a standalone Registry BridgeEntry (coded endpoints).
hetq-denom-entry : BridgeEntry
hetq-denom-entry = ℕ' , ℤ' , embB ℚ-crossmix

-- the Registry's own ℕ↪ℤ entry (the inclusion bridge it registers).
registry-ℕℤ-entry : BridgeEntry
registry-ℕℤ-entry = ℕ' , ℤ' , include-ℕℤ

-- they are the SAME BridgeEntry — the cospan leg is a Registry entry, not new.
hetq-cospan-is-registry-entry : hetq-denom-entry ≡ registry-ℕℤ-entry
hetq-cospan-is-registry-entry = refl
