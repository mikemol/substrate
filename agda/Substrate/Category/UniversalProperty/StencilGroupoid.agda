{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilGroupoid — ⟡stencil-groupoid: DOES the
-- uniqueness stencil (UNIQUENESS_STENCIL.md, 188) form a groupoid? The honest answer is
-- not yes/no but WHICH structure — dissolving the either/or:
--
--   • The TWO FRAMES are each a GROUPOID (a setoid-as-groupoid = an equivalence, where
--     every morphism/proof is invertible by sym):
--       - the ≡-frame: ≡ is refl/sym/trans (Foundation.Eq) — the equality groupoid.
--       - the ~-frame: ~ is refl/sym/trans (bisimulation) — the bisim groupoid. Bisim
--         (169) had only ~-refl; ~-sym/~-trans are supplied HERE (coinductively),
--         COMPLETING the ~-frame as a groupoid.
--   • The WEDGE-ISO layer is the substrate's EXPLICIT funext-free GROUPOID
--     (Wedge.IsoGroupoid: iso-sym + ≈ʷ-invˡ/invʳ, "EVERY morphism invertible").
--   • The stencil's UNIQUENESS is a CONTRACTIBILITY: "unique up to (unique) iso" = the
--     solution-groupoid of each fixed-point is contractible (connected, all iso).
--   • BUT the TRANSPORT-category of solvers (BackedCategory, 181) is NOT a groupoid:
--     count⇒eq (182, σ = count-solve) has no inverse — a genuine non-iso arrow. The
--     groupoid-DISTANCE (IsoGroupoid's own invariant) is exactly these non-iso arrows.
--
-- So: the stencil's FRAMES form groupoids (the uniqueness IS a contractibility in them);
-- the stencil's TRANSPORT-category does not. Neither "yes" nor "no" — the invariant is
-- the LEVEL at which the groupoid lives (the frame/equality, not the solver-transport).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilGroupoid where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)

------------------------------------------------------------------------
-- ① THE ~-FRAME IS A GROUPOID: ~ is an equivalence. ~-refl (169) + ~-sym + ~-trans
-- (here, coinductive) — every ~-proof invertible (~-sym), composable (~-trans). This
-- completes the bisim frame as a (proof-relevant) groupoid / setoid.
------------------------------------------------------------------------
~-sym : {x y : RealTrace} → x ~ y → y ~ x
head~ (~-sym p) = sym (head~ p)
tail~ (~-sym p) = ~-sym (tail~ p)

~-trans : {x y z : RealTrace} → x ~ y → y ~ z → x ~ z
head~ (~-trans p q) = trans (head~ p) (head~ q)
tail~ (~-trans p q) = ~-trans (tail~ p) (tail~ q)

------------------------------------------------------------------------
-- ② THE ≡-FRAME IS A GROUPOID: ≡ is refl/sym/trans (Foundation.Eq) — the trivial
-- equality groupoid. (Re-exported as the frame's witnesses for symmetry with ~.)
------------------------------------------------------------------------
≡-sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
≡-sym = sym

≡-trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
≡-trans = trans

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the groupoid lives at the FRAME level, and the
-- uniqueness is contractibility): DOES the stencil form a groupoid? The either/or
-- dissolves — the answer is WHICH structure:
--   YES at the frame level: each of the stencil's TWO FRAMES is a groupoid — the ≡-frame
--     (≡-sym/≡-trans, the equality groupoid) and the ~-frame (~-sym/~-trans HERE, the
--     bisim groupoid) — plus the wedge-iso layer is IsoGroupoid's explicit funext-free
--     groupoid. The stencil's UNIQUENESS (185/186/187) is then a CONTRACTIBILITY: each
--     fixed-point is unique UP TO (unique) ISO in its frame's groupoid — the μ-fold up to
--     ≡, the ν-step up to ≡-bounded, the ν-whole up to ~. "Unique up to unique iso" = the
--     solution-groupoid is contractible.
--   NO at the transport level: the category of registered solvers (BackedCategory, 181)
--     is NOT a groupoid — count⇒eq (182) has no inverse. The non-iso arrows ARE the
--     groupoid-distance (IsoGroupoid's own invariant): how far the solver-transport is
--     from the underlying iso-groupoid.
-- So the stencil's groupoid is the LAMBEK-hinged pair of frame-groupoids (≡ and ~), in
-- which each fixed-point's solution is a contractible object; the transport of solvers
-- across fixed-points is a category (with genuine non-iso arrows), not a groupoid. The
-- Lambek iso itself is the invertible hinge BETWEEN the frames (≡ one way, ~ the other) —
-- an iso in the combined groupoid, invertible up to the frames' own equalities, NOT strict
-- ≡ (the funext-free / bisim invertibility, IsoGroupoid's ≈ʷ pattern). This is the same
-- answer as the funext question (181): the substrate's invertibility lives up to the
-- pointwise/bisim equality, never strict ≡ on the underlying functions.
------------------------------------------------------------------------
