------------------------------------------------------------------------
-- Substrate.Solresol.Fragment
--
-- C4 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Solresol as the **Free cyclic group** witness in the lattice.
-- Solresol is a musical-syllable conlang designed by François Sudre
-- in 1827 using the seven solfège notes (do, re, mi, fa, sol, la, si)
-- as syllables; words are formed by ordered note sequences. The
-- CYCLIC STRUCTURE on the basis (notes form Z/7, with transposition
-- giving cyclic-shift symmetry) is the distinguishing categorical
-- feature.
--
-- This slice formalises:
--   1. The 7 Solresol notes as a finite basis with Z/7 structure
--      (via the existing Substrate.Groups infrastructure).
--   2. The free monoid over the notes (using Substrate.Groups.Coxeter.Word).
--   3. Transposition as cyclic-shift action on the basis.
--   4. The FreeOverBasis instance + LanguageWitness packaging.
--
-- Per [[feedback-prefer-coxeter-backed]]: notes are atoms; Solresol
-- words live in Coxeter Word. Transposition is the Z/7-action on
-- the basis lifted (per FreeLinearization-style universal property)
-- to an action on words.
--
-- Per [[feedback-comments-dont-overclaim]]: real Solresol has tonal
-- semantics + repetition-as-stress + word-length-as-grammar; the
-- fragment captures only the cyclic-basis + free-monoid layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Solresol.Fragment where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-cyclic;
         WitnessName; Solresol)

------------------------------------------------------------------------
-- 1. The 7 Solresol notes.
--
-- The Western diatonic scale. Note index in Z/7 captures the
-- cyclic structure: transposition by k semitones shifts the index
-- by k mod 7.
------------------------------------------------------------------------

data Note : Set where
  do₁ : Note   -- C
  re₁ : Note   -- D
  mi₁ : Note   -- E
  fa₁ : Note   -- F
  sol : Note   -- G
  la₁ : Note   -- A
  si₁ : Note   -- B

------------------------------------------------------------------------
-- 2. Note → Fin 7 index (the Z/7 embedding).
------------------------------------------------------------------------

note-count : ℕ
note-count = 7

note-index : Note → Fin note-count
note-index do₁ = zero
note-index re₁ = suc zero
note-index mi₁ = suc (suc zero)
note-index fa₁ = suc (suc (suc zero))
note-index sol = suc (suc (suc (suc zero)))
note-index la₁ = suc (suc (suc (suc (suc zero))))
note-index si₁ = suc (suc (suc (suc (suc (suc zero)))))

------------------------------------------------------------------------
-- 3. Solresol words: free monoid over Note via Coxeter Word.
------------------------------------------------------------------------

SolresolWord : Set
SolresolWord = Word Note

ε : SolresolWord
ε = []

single : Note → SolresolWord
single n = n ∷ []

------------------------------------------------------------------------
-- 4. Worked example words.
--
-- Real Solresol vocabulary uses multi-note words; the fragment
-- demonstrates a few. Names are illustrative.
------------------------------------------------------------------------

-- "doredo" — pronoun "I" in Solresol
word-doredo : SolresolWord
word-doredo = do₁ ∷ re₁ ∷ do₁ ∷ []

-- "domi" — affirmation
word-domi : SolresolWord
word-domi = do₁ ∷ mi₁ ∷ []

-- "soldorela" — illustrative 4-note word
word-soldorela : SolresolWord
word-soldorela = sol ∷ do₁ ∷ re₁ ∷ la₁ ∷ []

------------------------------------------------------------------------
-- 5. Cyclic transposition on Notes (the Z/7 action on the basis).
--
-- transpose-1 shifts each note up by one semitone (do → re, re → mi,
-- ..., si → do). This is the Z/7 cyclic-shift action that
-- distinguishes Solresol's basis from a generic free-monoid basis.
------------------------------------------------------------------------

transpose-1 : Note → Note
transpose-1 do₁ = re₁
transpose-1 re₁ = mi₁
transpose-1 mi₁ = fa₁
transpose-1 fa₁ = sol
transpose-1 sol = la₁
transpose-1 la₁ = si₁
transpose-1 si₁ = do₁

-- After 7 applications, transpose returns to identity (Z/7 cyclic order).
transpose-7 : Note → Note
transpose-7 n =
  transpose-1 (transpose-1 (transpose-1 (transpose-1
    (transpose-1 (transpose-1 (transpose-1 n))))))

transpose-7-id : (n : Note) → transpose-7 n ≡ n
transpose-7-id do₁ = refl
transpose-7-id re₁ = refl
transpose-7-id mi₁ = refl
transpose-7-id fa₁ = refl
transpose-7-id sol = refl
transpose-7-id la₁ = refl
transpose-7-id si₁ = refl

------------------------------------------------------------------------
-- 6. Transposition lifted to SolresolWord (pointwise).
--
-- Lifting the Z/7-action on the basis to an action on the free
-- monoid is the FreeLinearization-style universal property at the
-- free-cyclic site: the basis-action extends uniquely to a
-- word-action.
------------------------------------------------------------------------

transpose-word : SolresolWord → SolresolWord
transpose-word []      = []
transpose-word (n ∷ w) = transpose-1 n ∷ transpose-word w

------------------------------------------------------------------------
-- 7. The FreeOverBasis instance.
------------------------------------------------------------------------

solresol-free-structure : FreeOverBasis Note SolresolWord
solresol-free-structure = mkFreeOverBasis single

solresol-witness : LanguageWitness
solresol-witness = mkWitness
  Solresol
  Note
  SolresolWord
  solresol-free-structure
  Free-cyclic
