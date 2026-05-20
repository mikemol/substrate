------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor
--
-- The 168-bridge gauge family at HodgeDim4 packaged as a single
-- GL(3, F₂)-torsor — the substrate's first concrete GTorsor instance.
--
-- Per [[reserved-selfdual-bijection-gauge]]: there are 168 F₂-linear
-- bijections Reserved ↔ SelfDual (= GL(3, F₂)'s order). The original
-- gauge memory catalogued these as 168 alternatives floating without
-- structural unification; the multi-route equivariance arc gave
-- GL(3, F₂) the universal-property framework; THIS slice instantiates
-- the framework at the original problem site.
--
-- Framing. GL3F2 acts on itself by left-multiplication (the regular
-- representation). The function `bridge-of : GL3F2 → (Vector 3 →
-- Bivector)` parametrizes each GL3F2 element by its induced bridge
--
--   bridge-of g = vector3-to-selfdual ∘ applyG g
--
-- The canonical bridge is bridge-of id-GL = vector3-to-selfdual.
-- All 168 bridges are reached as bridge-of g for g ∈ GL3F2.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- the 168 bridges are NOT 168 separate definitions — they're the
-- orbit of one canonical bridge under a single torsor structure.
--
-- Per [[expose-generator-not-orbit]]: the torsor's action IS the
-- generator; the orbit (full 168) is automatically reachable.
--
-- Per [[choice-rigidification]]: no specific bridge is "the canonical"
-- — they're all torsor points, structurally equivalent up to the
-- chosen basepoint. The basepoint chosen here (id-GL ↦
-- vector3-to-selfdual) is a documented convention.
--
-- Equivalence handling. GL3F2 records contain functional content
-- (Linear maps' linearity proofs), so propositional equality requires
-- funext (forbidden per [[continuous-via-discrete-inference-rules]]).
-- We use pointwise equivalence on Vector 3 throughout — both for
-- _≈G_ (group equivalence) and as the carrier equivalence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor where

open import Data.Product using (Σ; _,_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge
  using (vector3-to-selfdual)
open import Substrate.Algebra.GL3F2
  using (GL3F2; mkGL3F2; id-GL; _·G_; _⁻¹G; applyG; L; L⁻¹;
         L-left; L-right)
open import Substrate.Category.GTorsor using (GTorsor; mkGTorsor)

------------------------------------------------------------------------
-- 1. Pointwise equivalence on GL3F2 (via apply on Vector 3).
------------------------------------------------------------------------

infix 4 _≈G_

_≈G_ : GL3F2 → GL3F2 → Set
g₁ ≈G g₂ = (v : Vector 3) → applyG g₁ v ≡ applyG g₂ v

------------------------------------------------------------------------
-- 2. The torsor action: GL3F2 acts on itself by left-multiplication.
--
-- act g x = g ·G x. Action axioms reduce definitionally: at the
-- pointwise level, both sides unfold to the same Linear-composition
-- evaluation.
------------------------------------------------------------------------

gauge-act : GL3F2 → GL3F2 → GL3F2
gauge-act g x = g ·G x

gauge-act-id : (x : GL3F2) → gauge-act id-GL x ≈G x
gauge-act-id x v = refl

gauge-act-·G :
  (g h x : GL3F2) →
  gauge-act (g ·G h) x ≈G gauge-act g (gauge-act h x)
gauge-act-·G g h x v = refl

------------------------------------------------------------------------
-- 3. Transitivity: any y is reachable from any x via g = y ·G x⁻¹G.
--
-- Pointwise:
--   applyG ((y ·G x⁻¹G) ·G x) v
--     = applyG y (applyG x⁻¹G (applyG x v))    [definitional]
--     = applyG y v                              [by L-left x]
------------------------------------------------------------------------

gauge-transitive :
  (x y : GL3F2) →
  Σ GL3F2 (λ g → gauge-act g x ≈G y)
gauge-transitive x y = (y ·G (x ⁻¹G)) , witness
  where
    witness : gauge-act (y ·G (x ⁻¹G)) x ≈G y
    witness v = cong (applyG y) (L-left x v)

------------------------------------------------------------------------
-- 4. Freeness: g₁ ·G x ≈G g₂ ·G x → g₁ ≈G g₂.
--
-- Pointwise. The hypothesis says ∀ v, applyG g₁ (applyG x v) ≡
-- applyG g₂ (applyG x v). To prove g₁ ≈G g₂ pointwise, given v', we
-- substitute v := applyG x⁻¹G v'; then applyG x v = applyG x
-- (applyG x⁻¹G v') = v' (by L-right x), so the hypothesis at v gives
-- the desired equality at v'.
------------------------------------------------------------------------

gauge-free :
  (x : GL3F2) (g₁ g₂ : GL3F2) →
  gauge-act g₁ x ≈G gauge-act g₂ x → g₁ ≈G g₂
gauge-free x g₁ g₂ hyp v' =
  trans (cong (applyG g₁) (sym (L-right x v')))
  (trans (hyp (applyG (x ⁻¹G) v'))
         (cong (applyG g₂) (L-right x v')))

------------------------------------------------------------------------
-- 5. THE GAUGE TORSOR — the universal-property packaging.
--
-- GL3F2 as a left-G-torsor over itself, with pointwise equivalence
-- on both group and carrier. This packages the four primitive
-- structural facts (act-id, act-·G, transitive, free) as a single
-- GTorsor instance, validating the "168 bridges = single torsor
-- universal-property object" claim.
------------------------------------------------------------------------

GaugeTorsor : GTorsor GL3F2 GL3F2 _·G_ id-GL _≈G_ _≈G_
GaugeTorsor = mkGTorsor
  gauge-act
  gauge-act-id
  gauge-act-·G
  gauge-transitive
  gauge-free

------------------------------------------------------------------------
-- 6. bridge-of — the parametrization of bridges by GL3F2 elements.
--
-- For each g ∈ GL3F2, the induced bridge is
--
--   bridge-of g : Vector 3 → Bivector
--   bridge-of g v = vector3-to-selfdual (applyG g v)
--
-- = vector3-to-selfdual ∘ applyG g (= canonical bridge precomposed
-- with the linear automorphism g).
--
-- The canonical bridge is bridge-of id-GL. All 168 bridges are
-- bridge-of g for g ∈ GL3F2.
------------------------------------------------------------------------

bridge-of : GL3F2 → Vector 3 → Bivector
bridge-of g v = vector3-to-selfdual (applyG g v)

bridge-of-id : (v : Vector 3) → bridge-of id-GL v ≡ vector3-to-selfdual v
bridge-of-id v = refl

------------------------------------------------------------------------
-- 7. Capstone — universal property in place.
--
-- The 168-bridge gauge family at HodgeDim4 IS this GaugeTorsor +
-- bridge-of parametrization. The atlas of bridges is the image of
-- bridge-of (which is the GL3F2-orbit of the canonical bridge).
--
-- Subsequent slices (S4, S5, S6, S8 in the universal-property
-- unification arc):
--
--   * S4 reformulates the existing ReservedBridgeAlternatives.Alt-A
--     and Alt-B as specific orbit points bridge-of α / bridge-of β
--     for specific α, β ∈ GL3F2 (no separate definitions needed).
--
--   * S5 builds cycle3-bridge / swap01-bridge / singer-bridge as
--     named orbit points bridge-of (cycle3-GL) etc., directly
--     applying the multi-route arc's Sylow generators.
--
--   * S6 identifies Hodge ★'s induced action on the gauge torsor as
--     a specific GL3F2 element.
--
--   * S8 builds the full 168-bridge atlas catalogue via bridge-of's
--     image; references S4/S5/S6's named witnesses as orbit points.
--
-- Per [[choice-rigidification]]: the choice of basepoint (id-GL ↦
-- vector3-to-selfdual) is a CONVENTION, not a privileged choice. Any
-- other GL3F2 element could equally serve as basepoint, yielding a
-- different specific "canonical" bridge but the same torsor structure.
------------------------------------------------------------------------
