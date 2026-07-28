------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.FourPointGroupoid
--
-- THE ONE-OBJECT GROUPOID OF WEDGE REWRITES — deloop the four-point V₄.
--
-- Wedge.FourPointV4 gives the four points of a wedge a V₄ (two commuting ℤ/2's,
-- rowSwap/colSwap, closed to Klein four by CommutingInvolutions). A group is a
-- one-object groupoid: DELOOP it (Category.DeloopingGroup) and you get BV₄ — a
-- single object (a generic wedge) with exactly FOUR morphisms, each invertible,
-- and those four morphisms ARE the four rewrite actions on the wedge's points.
--
-- The deloop reuses the canonical V₄ group (Groups.V4.V₄-Group) — the four
-- elements {e, α, β, γ}. `act` realizes each as a concrete rewrite of the four
-- points (e ↦ id, α ↦ rowSwap, β ↦ colSwap, γ ↦ the Klein rotation).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.FourPointGroupoid where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Group using (Group; monoid)
open import Substrate.Category.Delooping using (deloop)
open import Substrate.Category.DeloopingGroup using (deloop-group-isGroupoid)
open import Substrate.Category.Iso using (IsGroupoid)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Bundle using (V₄-Group)
open import Substrate.Groups.V4.Operations using () renaming (inv to v4-inv)
open import Substrate.Groups.V4.Bijection using (to-c)
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (trans; cong; sym)
open import Substrate.Algebra.Wedge.FourPointV4 using (Square; rowSwap; colSwap; klein-rot)
open import Substrate.Algebra.Wedge.FourPointReflection using (wordAct; wordAct-hom)

------------------------------------------------------------------------
-- 1. THE DELOOP: BV₄ = deloop (monoid V₄-Group), the one-object groupoid. Its
--    hom-set is V₄ (four morphisms); composition is the group product; every
--    morphism is invertible. This is "the groupoid inhabited by the four points"
--    — the four points are its four morphisms.
--
--    The category `deloop (monoid V₄-Group) : CategoryOf` is left INLINE (not a
--    named def): CategoryOf is Set₁ (it fields Obj/Mor : Set), and naming it
--    would inhabit Set₁ for nothing — the DeloopingGroup house pattern states the
--    groupoid property over the inline deloop, keeping this at Set₀.
------------------------------------------------------------------------

open import Substrate.Algebra.Wedge.FourPointV4
  using (rowSwap-inv; colSwap-inv; klein-rot-inv)
BV₄-isGroupoid : IsGroupoid (deloop (monoid V₄-Group))
BV₄-isGroupoid = deloop-group-isGroupoid V₄-Group

------------------------------------------------------------------------
-- 2. THE ACTION: each of the four morphisms realized as a rewrite of a wedge's
--    four points. e is the identity rewrite; α/β are the two ℤ/2 axis-swaps;
--    γ (= α·β) is the Klein rotation (the composite / 180° turn).
------------------------------------------------------------------------

act : {C : Set} → V₄ → Square {C} → Square {C}
act e s = s
act α s = rowSwap s
act β s = colSwap s
act γ s = klein-rot s

-- the identity morphism acts trivially (the empty rewrite).
act-e : {C : Set} (s : Square {C}) → act e s ≡ s
act-e s = refl

-- every wedge rewrite is its own inverse — matching V₄'s `inv x = x` (exponent 2):
-- applying any of the four rewrites twice returns the wedge unchanged.

act-selfinv : {C : Set} (x : V₄) (s : Square {C}) → act x (act x s) ≡ s
act-selfinv e s = refl
act-selfinv α s = rowSwap-inv s
act-selfinv β s = colSwap-inv s
act-selfinv γ s = klein-rot-inv s

------------------------------------------------------------------------
-- 3. THE SEAM: the enumerated BV₄ action IS the free Coxeter word action,
--    routed through the normal form. Each morphism x of BV₄ acts on the four
--    points exactly as the reflection representation of its canonical word
--    (to-c x) — so `act = wordAct ∘ to-c`. (All refl: to-c γ = A ∷ B ∷ [], and
--    klein-rot reduces to rowSwap ∘ colSwap = wordAct (A ∷ B ∷ []).)
------------------------------------------------------------------------

act-via-word : {C : Set} (x : V₄) (s : Square {C}) → act x s ≡ wordAct (to-c x) s
act-via-word e s = refl
act-via-word α s = refl
act-via-word β s = refl
act-via-word γ s = refl

------------------------------------------------------------------------
-- 4. THE PAYOFF: composition of BV₄ morphisms ↦ CONCATENATION of their
--    normal-form words. Transported from the FREE word homomorphism
--    (wordAct-hom) through the seam — no group table, no normalize-invariance.
--    This is the homomorphism content the enumerated `act` could not reach
--    directly: composing two rewrites is the word-action of the concatenated
--    canonical words (which normalizes to the product's normal form).
------------------------------------------------------------------------

act-compose : {C : Set} (x y : V₄) (s : Square {C}) →
              act x (act y s) ≡ wordAct (to-c x ++ to-c y) s
act-compose x y s =
  trans (act-via-word x (act y s))
        (trans (cong (wordAct (to-c x)) (act-via-word y s))
               (sym (wordAct-hom (to-c x) (to-c y) s)))
