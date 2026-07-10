------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Transport
--
-- BRIDGES MAP SHAPE NATURALLY — the one fact the symmetric double category
-- rests on. A bridge transports a trace (transport-trace), and `shape` reads off
-- the quotient sequence (now `List (C D)`, the quotients being carrier
-- representatives); this proves the two commute up to the bridge's translation:
--     shape (transport-trace br t) ≡ map (translate br) (shape t).
-- `transport-wedge` translates every `quot` by the bridge, so the shape is
-- carried POINTWISE through `translate` — `shape` is a natural transformation,
-- not a strict invariant (it was invariant only when the quotient was a
-- carrier-free ℕ count). The spine length is preserved exactly.
--
-- WHY IT MATTERS: it makes BOTH kinds of wedge-morphism shape-preserving —
-- bridges (this lemma) and correspondences (`Corresponds` IS shape-equality,
-- Shape.agda). So bridges and correspondences are two species of arrow over
-- ONE base (the shape), and the structure fibers over the shape in BOTH
-- directions — the symmetric double category. The Möbius/transpose (swap
-- bridge ↔ correspondence) fixes the shape; the within-carrier wedge is the
-- diagonal slice (A = A, identity bridge), the seam.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Transport where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; cong; subst)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Wedge using (DivStr; Trace; done; more; quot)

-- list map (Foundation.List is minimal — no map); used to carry the quotient
-- sequence pointwise through a bridge's `translate`.
mapL : {A B : Set} → (A → B) → List A → List B
mapL f []       = []
mapL f (x ∷ xs) = f x ∷ mapL f xs
open import Substrate.Algebra.Wedge.Shape using (WedgeShape; shape)
open import Substrate.Algebra.Wedge.Bridge
  using (Bridge; translate; z-pres; transport-trace)

-- `shape` is invariant under subst on the divisor (b) index: the spine does
-- not depend on the middle index, so re-indexing it changes nothing.
shape-subst : {C : Set} {D : DivStr C} {a g x y : C} (eq : x ≡ y) (tr : Trace D a x g) →
              shape (subst (λ d → Trace D a d g) eq tr) ≡ shape tr
shape-subst refl tr = refl

-- bridges preserve shape: transport keeps every quotient, so the spine is
-- carried unchanged.
shape-transport : {C₁ C₂ : Set} {D₁ : DivStr C₁} {D₂ : DivStr C₂} (br : Bridge D₁ D₂) {a b g : C₁}
                  (t : Trace D₁ a b g) →
                  shape (transport-trace br t) ≡ mapL (translate br) (shape t)
shape-transport br (done a)       = shape-subst (sym (z-pres br)) (done (translate br a))
shape-transport br (more b w rec) = cong (translate br (quot w) ∷_) (shape-transport br rec)
