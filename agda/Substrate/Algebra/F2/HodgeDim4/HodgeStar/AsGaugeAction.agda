------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGaugeAction
--
-- Hodge ★'s action on the GaugeTorsor (= GL(3, F₂)-torsor of
-- Reserved↔SelfDual bridges, per
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor).
--
-- ★ acts on the bridge space by post-composition: a bridge
-- β : Vector 3 → Bivector maps to ★ ∘ β. The key structural fact:
-- every bridge in the GaugeTorsor lands in SelfDual (by construction,
-- bridge-of g = vector3-to-selfdual ∘ applyG g, and
-- vector3-to-selfdual-sd guarantees the codomain is SelfDual-fixed
-- under ★). Therefore:
--
--   ★ ∘ (bridge-of g) ≡ bridge-of g          (pointwise)
--
-- — i.e., Hodge ★ acts as the IDENTITY on the GaugeTorsor.
--
-- Categorically: the gauge torsor is ★-INVARIANT. Its action factors
-- through SelfDual, where ★ is identity by definition. The GL(3, F₂)-
-- gauge group is the symmetry group of SelfDual seen as a 3-dim
-- F₂-vector space — and ★'s involution structure on the ambient
-- Bivector space contributes nothing distinct to this gauge
-- symmetry (its only role is selecting SelfDual as the codomain
-- subspace).
--
-- Per [[reserved-selfdual-bijection-gauge]]: this is the formal
-- structural reason WHY the gauge group is GL(3, F₂) (= the
-- automorphisms of an abstract 3-dim F₂-vector space) rather than
-- something larger that "sees" ★. The ★-symmetry is FROZEN by the
-- choice of SelfDual codomain; the residual gauge freedom is purely
-- the linear-algebraic symmetry of the 3-dim subspace.
--
-- Per [[torsion-element-universal]]: ★ is an order-2 finite-order
-- automorphism; here it corresponds to the IDENTITY element of the
-- gauge group, which is the trivial torsion element. The 3+1 parity
-- universal at this gauge level is the ★-fixed / ★-anti-fixed split
-- of Bivector itself, NOT the GL(3, F₂)-action on the SelfDual half.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGaugeAction where

open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (SelfDual-Pred)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge
  using (vector3-to-selfdual; vector3-to-selfdual-sd)
open import Substrate.Algebra.GL3F2 using (GL3F2; id-GL; applyG)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
  using (bridge-of)

------------------------------------------------------------------------
-- 1. The action of Hodge ★ on a bridge.
--
-- For any bridge β : Vector 3 → Bivector, the ★-action is
-- post-composition: (★ ∘ β) v = apply hodge-star (β v).
------------------------------------------------------------------------

star-act : (Vector 3 → Bivector) → (Vector 3 → Bivector)
star-act β v = apply hodge-star (β v)

------------------------------------------------------------------------
-- 2. The structural fact: every bridge lands in SelfDual.
--
-- bridge-of g v = vector3-to-selfdual (applyG g v) — and
-- vector3-to-selfdual-sd guarantees vector3-to-selfdual lands in
-- SelfDual for any Vector 3 input.
------------------------------------------------------------------------

bridge-lands-in-SelfDual :
  (g : GL3F2) (v : Vector 3) →
  SelfDual-Pred (bridge-of g v)
bridge-lands-in-SelfDual g v = vector3-to-selfdual-sd (applyG g v)

------------------------------------------------------------------------
-- 3. The main theorem: Hodge ★ acts trivially on bridges.
--
-- ★ ∘ bridge-of g ≡ bridge-of g (pointwise).
--
-- Reason: SelfDual-Pred ω = apply hodge-star ω ≡ ω (by definition);
-- bridge-of g v ∈ SelfDual; so apply hodge-star (bridge-of g v) ≡
-- bridge-of g v.
------------------------------------------------------------------------

hodge-trivial-on-bridge :
  (g : GL3F2) (v : Vector 3) →
  star-act (bridge-of g) v ≡ bridge-of g v
hodge-trivial-on-bridge g v = bridge-lands-in-SelfDual g v

------------------------------------------------------------------------
-- 4. Equivalent statement: Hodge ★ corresponds to id-GL in the
-- GaugeTorsor.
--
-- Since star-act (bridge-of g) ≡ bridge-of g, the GL3F2 element that
-- "implements" ★ on the torsor is the identity. (Strictly: the
-- torsor's free + transitive structure assigns a unique GL3F2 element
-- to any pair of bridges; the pair (bridge-of g, star-act (bridge-of
-- g)) is the diagonal pair, witnessed by id-GL.)
------------------------------------------------------------------------

hodge-as-id-GL :
  (g : GL3F2) (v : Vector 3) →
  star-act (bridge-of g) v ≡ bridge-of (id-GL Substrate.Algebra.GL3F2.·G g) v
hodge-as-id-GL g v = bridge-lands-in-SelfDual g v

------------------------------------------------------------------------
-- 5. Capstone.
--
-- Hodge ★'s structural role at HodgeDim4 is to SELECT the SelfDual
-- subspace as the bridge codomain. Once selected, ★ becomes trivial
-- on the gauge torsor — the residual gauge freedom is purely
-- GL(3, F₂)-symmetry of SelfDual-as-3-dim-F₂-space.
--
-- This is the formal substrate-side statement of the "168 gauge
-- freedom = GL(3, F₂), not something larger" observation from
-- [[reserved-selfdual-bijection-gauge]]. The order-2 ★-involution is
-- FROZEN into the choice of codomain; the gauge group is the
-- automorphism group of what remains.
--
-- Per [[3plus1-parity-universal]]: the 3+1 split at this level is the
-- (SelfDual ⊕ AntiSelfDual) decomposition of Bivector, of which the
-- bridge codomain is the 3-dim SelfDual half. The "+1" chirality is
-- the ★-eigenvalue (+1 for SelfDual, -1 for AntiSelfDual; in
-- characteristic 2, these collapse to a single F₂ chirality bit).
------------------------------------------------------------------------
