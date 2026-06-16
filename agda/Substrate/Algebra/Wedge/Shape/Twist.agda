------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Twist
--
-- TWISTING THE DOUBLE CATEGORY — equipping each bridge with a COMPANION
-- (forward) and a CONJOINT (backward). This is what makes the shape-indexed
-- structure (Shape.Double) into a twisted/equipment structure: the conjoint is
-- the twist.
--
-- A bridge maps shape NATURALLY (`shape-transport`: shape (br·t) = map (translate
-- br) (shape t) — the quotients are relabelled by the bridge, the pivot from a
-- carrier-free ℕ shape), so it induces a bridge-mediated correspondence between
-- a trace's translated shape and its image's shape — read two ways:
--   * companion br t : map(translate br)(shape t) ≡ shape (br·t)   — FORWARD,
--                                             the TRACE direction (quantify);
--   * conjoint  br t : shape (br·t) ≡ map(translate br)(shape t)   — BACKWARD,
--                                             the BÉZOUT direction (exchange).
-- They are the two readings of one fact, swapped by `sym`: `sym (companion br t)
-- ≡ conjoint br t` (the TWIST). `sym` is involutive, so companion and conjoint
-- are a genuine sym-pair — and on the iso/identity seam the two coincide.
--
-- So Bézout is not merely analogous to the twist; in this equipment it IS the
-- conjoint, and the trace IS the companion — the same bridge, read with the
-- variance flipped. (Cross-carrier now, the comparison is bridge-MEDIATED — via
-- `map ∘ translate` — since the shape is carrier-bound, not carrier-free.)
--
-- SCOPE: the twist DATA (companion / conjoint / their involution). The full
-- equipment axioms (companion ⊣ conjoint triangle identities) are the next layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Twist where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; transport-trace)
open import Substrate.Algebra.Wedge.Shape using (shape)
open import Substrate.Algebra.Wedge.Shape.Transport using (shape-transport; mapL)

-- companion: the bridge read FORWARD (the trace direction). The image's shape
-- is the trace's shape relabelled through the bridge.
companion : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
            (t : Trace D₁ a b g) →
            mapL (translate br) (shape t) ≡ shape (transport-trace br t)
companion br t = sym (shape-transport br t)

-- conjoint: the bridge read BACKWARD (the twist; the Bézout direction).
conjoint : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
           (t : Trace D₁ a b g) →
           shape (transport-trace br t) ≡ mapL (translate br) (shape t)
conjoint br t = shape-transport br t

-- `sym` is involutive (local; absent from Foundation.Eq).
sym-sym : {A : Set} {x y : A} (p : x ≡ y) → sym (sym p) ≡ p
sym-sym refl = refl

-- THE TWIST: conjoint = the inversion of companion. One bridge, two readings,
-- swapped by `sym` — companion (trace) ⟷ conjoint (Bézout).
twist : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
        (t : Trace D₁ a b g) → sym (companion br t) ≡ conjoint br t
twist br t = sym-sym (shape-transport br t)
