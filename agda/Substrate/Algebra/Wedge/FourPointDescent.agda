------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.FourPointDescent
--
-- THE REVERSE DESCENT: wordAct factors through BV₄ — making wordAct ⟷ BV₄ an iff.
--
-- FourPointGroupoid.act-via-word gave the forward seam: each of BV₄'s four
-- morphisms acts as the reflection representation of its normal-form word
-- (act = wordAct ∘ to-c). This file gives the reverse: EVERY word — not just a
-- canonical one — acts via its V₄ class (wordAct w = act (from-c w)). So the free
-- Coxeter reflection representation and the delooped-groupoid action are the same
-- map, in both directions.
--
-- It rests on normalize-invariance of wordAct, which rests on wordAct respecting
-- `insert` — and each of the eight insert cases is discharged by exactly the
-- FourPointV4 relation it encodes (A² ↦ rowSwap-inv, B² ↦ colSwap-inv, the mixed
-- cases ↦ row-col-commute). That IS the Coxeter descent: the free monoid on the
-- generators quotiented by the reflection relations.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.FourPointDescent where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.V4-Coxeter
  using (Gen; A; B; c-ε; c-A; c-B; c-AB; insert; normalize; normalize-canonical)
  renaming (Canonical to Canonical⟦ab211b40⟧)   -- shape-specialize the ambiguous name
open import Substrate.Groups.V4.Bijection using (from-c; to-from-canonical)
open import Substrate.Algebra.Wedge.FourPointV4
  using (Square; rowSwap; colSwap; rowSwap-inv; colSwap-inv; row-col-commute)
open import Substrate.Algebra.Wedge.FourPointReflection using (genAct; wordAct)
open import Substrate.Algebra.Wedge.FourPointGroupoid using (act; act-via-word)

module _ {C : Set} where

  ------------------------------------------------------------------------
  -- 1. wordAct respects `insert`: inserting a generator into a CANONICAL word
  --    acts as pre-composing that generator's reflection. Each case is exactly
  --    the Coxeter relation it triggers.
  ------------------------------------------------------------------------

  wordAct-insert : (g : Gen) {w : Word Gen} (c : Canonical⟦ab211b40⟧ w) (s : Square {C}) →
                   wordAct (insert g w) s ≡ genAct g (wordAct w s)
  wordAct-insert A c-ε  s = refl                                    -- insert A [] = A∷[]
  wordAct-insert A c-A  s = sym (rowSwap-inv s)                     -- A² = ε
  wordAct-insert A c-B  s = refl                                    -- insert A (B∷[]) = A∷B∷[]
  wordAct-insert A c-AB s = sym (rowSwap-inv (colSwap s))           -- A·(A∷B) = B : A²=ε
  wordAct-insert B c-ε  s = refl                                    -- insert B [] = B∷[]
  wordAct-insert B c-A  s = sym (row-col-commute s)                 -- B·A = A∷B : AB=BA
  wordAct-insert B c-B  s = sym (colSwap-inv s)                     -- B² = ε
  wordAct-insert B c-AB s =                                         -- B·(A∷B) = A : AB=BA, B²=ε
    sym (trans (row-col-commute (colSwap s)) (cong rowSwap (colSwap-inv s)))

  ------------------------------------------------------------------------
  -- 2. wordAct is invariant under normalization (normalize = insert-fold).
  ------------------------------------------------------------------------

  wordAct-normalize : (w : Word Gen) (s : Square {C}) →
                      wordAct (normalize w) s ≡ wordAct w s
  wordAct-normalize []      s = refl
  wordAct-normalize (g ∷ w) s =
    trans (wordAct-insert g (normalize-canonical w) s)
          (cong (genAct g) (wordAct-normalize w s))

  ------------------------------------------------------------------------
  -- 3. THE REVERSE DESCENT: every word acts via its V₄ class. With the forward
  --    seam (act-via-word), wordAct ⟷ BV₄ is an iff — the free reflection
  --    representation IS the delooped groupoid's action, and conversely.
  ------------------------------------------------------------------------

  wordAct-descends : (w : Word Gen) (s : Square {C}) →
                     wordAct w s ≡ act (from-c w) s
  wordAct-descends w s =
    sym (trans (act-via-word (from-c w) s)
               (trans (cong (λ v → wordAct v s) (to-from-canonical (normalize-canonical w)))
                      (wordAct-normalize w s)))
