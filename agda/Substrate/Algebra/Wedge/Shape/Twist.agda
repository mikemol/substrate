------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Twist
--
-- TWISTING THE DOUBLE CATEGORY — equipping each bridge with a COMPANION
-- (forward) and a CONJOINT (backward), as correspondences. This is what makes
-- the shape-indexed double category (Shape.Double) into a twisted/equipment
-- structure: the conjoint is the twist.
--
-- A bridge preserves shape (`shape-transport`), so it induces a correspondence
-- between a trace and its image — read two ways:
--   * companion br t : Corr t (br·t)        — FORWARD, the TRACE direction
--                                             (quotient / quantify);
--   * conjoint  br t : Corr (br·t) t        — BACKWARD, the BÉZOUT direction
--                                             (coefficients / exchange).
-- They are the two readings of one fact, swapped by the vertical groupoid's
-- inversion: `corr-sym (companion br t) ≡ conjoint br t` (the TWIST). `corr-sym`
-- is involutive, so companion and conjoint are a genuine sym-pair — and on the
-- iso/identity seam (where the bridge is invertible and the correspondence is
-- `refl`) the two coincide: the Möbius closes.
--
-- So Bézout is not merely analogous to the twist; in this equipment it IS the
-- conjoint, and the trace IS the companion — the same bridge, read with the
-- variance flipped.
--
-- SCOPE: the twist DATA (companion / conjoint / their involution). The full
-- equipment axioms (companion ⊣ conjoint triangle identities) are the next
-- coherence layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Twist where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)
open import Substrate.Algebra.Wedge.Shape.Transport using (shape-transport)
open import Substrate.Algebra.Wedge.Shape.Double using (Corr; corr-sym)

-- companion: the bridge read FORWARD (the trace direction).
companion : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
            (t : Trace D₁ a b g) → Corr t (transport-trace br t)
companion br t = sym (shape-transport br t)

-- conjoint: the bridge read BACKWARD (the twist; the Bézout direction).
conjoint : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
           (t : Trace D₁ a b g) → Corr (transport-trace br t) t
conjoint br t = shape-transport br t

-- `sym` is involutive (local; absent from Foundation.Eq).
sym-sym : {A : Set} {x y : A} (p : x ≡ y) → sym (sym p) ≡ p
sym-sym refl = refl

-- THE TWIST: conjoint = the vertical inversion of companion. One bridge, two
-- readings, swapped by `corr-sym` — companion (trace) ⟷ conjoint (Bézout).
twist : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁}
        (t : Trace D₁ a b g) → corr-sym (companion br t) ≡ conjoint br t
twist br t = sym-sym (shape-transport br t)
