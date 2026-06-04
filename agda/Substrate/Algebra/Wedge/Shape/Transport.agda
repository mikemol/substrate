------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Transport
--
-- BRIDGES PRESERVE SHAPE — the one fact the symmetric double category rests
-- on. A bridge transports a trace (transport-trace), and `shape` reads off
-- the carrier-free quotient sequence; this proves the two commute:
--     shape (transport-trace br t) ≡ shape t.
-- Because `transport-wedge` copies every `quot` unchanged, transport only
-- relabels carrier content — the shape (the Peano spine) is invariant.
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
open import Substrate.Foundation.List using (_∷_)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace; done; more; quot)
open import Substrate.Algebra.Wedge.Shape using (WedgeShape; shape)
open import Substrate.Algebra.Wedge.Bridge
  using (Bridge; translate; z-pres; transport-trace)

-- `shape` is invariant under subst on the divisor (b) index: the spine does
-- not depend on the middle index, so re-indexing it changes nothing.
shape-subst : {D : DivStr} {a g x y : C D} (eq : x ≡ y) (tr : Trace D a x g) →
              shape (subst (λ d → Trace D a d g) eq tr) ≡ shape tr
shape-subst refl tr = refl

-- bridges preserve shape: transport keeps every quotient, so the spine is
-- carried unchanged.
shape-transport : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
                  (t : Trace D₁ a b g) →
                  shape (transport-trace br t) ≡ shape t
shape-transport br (done a)       = shape-subst (sym (z-pres br)) (done (translate br a))
shape-transport br (more b w rec) = cong (quot w ∷_) (shape-transport br rec)
