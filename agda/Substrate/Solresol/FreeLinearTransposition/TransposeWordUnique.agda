------------------------------------------------------------------------
-- Substrate.Solresol.FreeLinearTransposition.TransposeWordUnique
--
-- Defines: transpose-word-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Solresol.FreeLinearTransposition; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.FreeLinearTransposition.TransposeWordUnique where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Solresol.Fragment.Note
open import Substrate.Solresol.Fragment.Transpose
open import Substrate.Solresol.Fragment.TransposeWord
open import Substrate.Solresol.Fragment.Word
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.Solresol.FreeLinearTransposition.NoteShiftBasis
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2



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
