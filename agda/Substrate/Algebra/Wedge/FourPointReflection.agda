------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.FourPointReflection
--
-- THE REFLECTION REPRESENTATION OF THE FOUR-POINT V₄ — the Coxeter path.
--
-- V₄ = ⟨A, B | A² = B² = ε, AB = BA⟩ (Groups.V4-Coxeter). Its elements are
-- reduced WORDS in the two generators (Coxeter.Word = the free monoid on Gen),
-- and multiplication is word concatenation modulo the relations. So the action
-- on a wedge's four points is not cased over the four enumerated group elements
-- — it is defined on the GENERATORS (each a reflection: A ↦ rowSwap, B ↦
-- colSwap) and EXTENDED over words. Then:
--
--   * the action homomorphism act(w₁·w₂) = act w₁ ∘ act w₂ is FREE — a two-line
--     induction on the word (concatenation ↦ composition), no group table; and
--   * the Coxeter relations that cut the free monoid down to V₄ are discharged
--     by exactly the involution/commute facts FourPointV4 already proved
--     (A² = ε ↦ rowSwap-inv, B² = ε ↦ colSwap-inv, AB = BA ↦ row-col-commute).
--
-- This is what Coxeter is for: "combine/permute generators" IS the word algebra;
-- the reflection representation is the free-monoid map extending the generators.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.FourPointReflection where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Groups.V4-Coxeter using (Gen; A; B)
open import Substrate.Algebra.Wedge.FourPointV4
  using (Square; rowSwap; colSwap; rowSwap-inv; colSwap-inv; row-col-commute)

module _ {C : Set} where

  ------------------------------------------------------------------------
  -- 1. Each generator acts as its reflection (involution) on the four points.
  ------------------------------------------------------------------------

  genAct : Gen → Square {C} → Square {C}
  genAct A = rowSwap
  genAct B = colSwap

  ------------------------------------------------------------------------
  -- 2. Extend over words: a word acts as the composite of its letters'
  --    reflections. The empty word is the identity rewrite.
  ------------------------------------------------------------------------

  wordAct : Word Gen → Square {C} → Square {C}
  wordAct []      s = s
  wordAct (g ∷ w) s = genAct g (wordAct w s)

  ------------------------------------------------------------------------
  -- 3. THE HOMOMORPHISM IS FREE. Word concatenation ↦ function composition,
  --    by induction on the first word — no enumeration of V₄'s elements.
  ------------------------------------------------------------------------

  wordAct-hom : (w₁ w₂ : Word Gen) (s : Square {C}) →
                wordAct (w₁ ++ w₂) s ≡ wordAct w₁ (wordAct w₂ s)
  wordAct-hom []       w₂ s = refl
  wordAct-hom (g ∷ w₁) w₂ s = cong (genAct g) (wordAct-hom w₁ w₂ s)

  ------------------------------------------------------------------------
  -- 4. THE COXETER RELATIONS hold on the action, so it descends from the free
  --    monoid to V₄. Each relation is exactly a FourPointV4 lemma.
  ------------------------------------------------------------------------

  -- A² = ε : the row reflection is an involution.
  rel-A² : (s : Square {C}) → wordAct (A ∷ A ∷ []) s ≡ s
  rel-A² = rowSwap-inv

  -- B² = ε : the column reflection is an involution.
  rel-B² : (s : Square {C}) → wordAct (B ∷ B ∷ []) s ≡ s
  rel-B² = colSwap-inv

  -- AB = BA : the two reflections commute (the V₄-not-dihedral condition).
  rel-AB=BA : (s : Square {C}) → wordAct (A ∷ B ∷ []) s ≡ wordAct (B ∷ A ∷ []) s
  rel-AB=BA s = sym (row-col-commute s)
