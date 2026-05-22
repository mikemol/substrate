------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition
--
-- D5 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Promotes Solresol's `transpose-word` (the pointwise-recursive
-- transposition on words, from C4) to a FREE-MONOID universal-
-- property realisation. The basis-action `transpose-1 : Note → Note`
-- (cyclic shift by one semitone) extends uniquely to a word-
-- transformer `SolresolWord → SolresolWord` via the free-monoid
-- universal property — since `Word Note` is the free monoid over
-- the Note basis.
--
-- Per [[project-freelinearization-names-linear-from-images]] (at
-- the free-monoid analog): the existing `transpose-word` from C4
-- IS the unique monoid homomorphism extending the basis-action;
-- this slice surfaces the universal property explicitly.
--
-- Per [[feedback-categorical-name-first]]: this is the free-monoid
-- universal property at the Note basis. Sister to Lojban L8
-- WordAlgebra applied to a different basis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition where

open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; trans; sym)

open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_)
open import Substrate.Solresol.Fragment
  using (Note; SolresolWord; ε; single;
         transpose-1; transpose-word)

------------------------------------------------------------------------
-- 1. The basis-map.
--
-- Each Note transposes by one semitone, lifted to a single-symbol
-- SolresolWord. This is the basis-image for the free-monoid
-- extension.
------------------------------------------------------------------------

note-shift-basis : Note → SolresolWord
note-shift-basis n = single (transpose-1 n)

------------------------------------------------------------------------
-- 2. transpose-word agrees with the basis-map on basis vectors.
--
-- The free-extension property's "extension on basis" half:
-- transpose-word applied to a single-Note word IS the basis-map.
------------------------------------------------------------------------

transpose-word-on-basis :
  (n : Note) → transpose-word (single n) ≡ note-shift-basis n
transpose-word-on-basis _ = refl

------------------------------------------------------------------------
-- 3. transpose-word is a monoid homomorphism.
--
-- The free-extension property's "preserves composition" half:
-- transpose-word respects word concatenation.
------------------------------------------------------------------------

transpose-word-++ :
  (w₁ w₂ : SolresolWord) →
  transpose-word (w₁ ++ w₂) ≡ transpose-word w₁ ++ transpose-word w₂
transpose-word-++ []      w₂ = refl
transpose-word-++ (n ∷ w₁) w₂ =
  cong (transpose-1 n ∷_) (transpose-word-++ w₁ w₂)

------------------------------------------------------------------------
-- 4. transpose-word respects ε.
------------------------------------------------------------------------

transpose-word-ε : transpose-word ε ≡ ε
transpose-word-ε = refl

------------------------------------------------------------------------
-- 5. Uniqueness of the free extension.
--
-- Given any candidate `f : SolresolWord → SolresolWord` that:
--   * preserves ε,
--   * respects word concatenation (is a monoid homomorphism),
--   * agrees with `note-shift-basis` on single-Note words,
-- then f IS transpose-word (pointwise).
--
-- The full free-monoid universal property; the homomorphism that
-- extends the basis-map is UNIQUE.
------------------------------------------------------------------------

transpose-word-unique :
  (f : SolresolWord → SolresolWord) →
  (f-ε : f ε ≡ ε) →
  (f-++ : (w₁ w₂ : SolresolWord) → f (w₁ ++ w₂) ≡ f w₁ ++ f w₂) →
  (f-basis : (n : Note) → f (single n) ≡ note-shift-basis n) →
  (w : SolresolWord) → f w ≡ transpose-word w
transpose-word-unique f f-ε f-++ f-basis [] = f-ε
transpose-word-unique f f-ε f-++ f-basis (n ∷ w) =
  -- f (n ∷ w) = f (single n ++ w)
  --          = f (single n) ++ f w        [by f-++]
  --          = note-shift-basis n ++ f w  [by f-basis]
  --          = (transpose-1 n ∷ []) ++ f w
  --          = transpose-1 n ∷ f w
  -- And by IH: f w ≡ transpose-word w
  -- So:   f (n ∷ w) ≡ transpose-1 n ∷ transpose-word w ≡ transpose-word (n ∷ w)
  let step1 : f (n ∷ w) ≡ f (single n ++ w)
      step1 = refl
      step2 : f (single n ++ w) ≡ f (single n) ++ f w
      step2 = f-++ (single n) w
      step3 : f (single n) ++ f w ≡ note-shift-basis n ++ f w
      step3 = cong (_++ f w) (f-basis n)
      step4 : note-shift-basis n ++ f w ≡ transpose-1 n ∷ f w
      step4 = refl
      step5 : transpose-1 n ∷ f w ≡ transpose-1 n ∷ transpose-word w
      step5 = cong (transpose-1 n ∷_) (transpose-word-unique f f-ε f-++ f-basis w)
  in trans step1 (trans step2 (trans step3 (trans step4 step5)))

------------------------------------------------------------------------
-- 6. Capstone.
--
-- transpose-word is the UNIQUE monoid homomorphism SolresolWord →
-- SolresolWord extending the basis-action transpose-1 : Note →
-- Note. This is the free-monoid universal property applied at the
-- Note basis — the Solresol-side analog of Lojban L8 WordAlgebra
-- and Toki Pona T8 LinearAlgebra. All three witnesses now have
-- the universal property surfaced.
--
-- Closes the implicit deferral at C4's transpose-word: the
-- "transposition as universal lift" is no longer just a stated
-- claim but a proven uniqueness lemma.
------------------------------------------------------------------------
