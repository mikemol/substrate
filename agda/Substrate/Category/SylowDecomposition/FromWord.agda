------------------------------------------------------------------------
-- Substrate.Category.SylowDecomposition.FromWord
--
-- The foundational lemma: given a word over a generator alphabet
-- (where each generator is known to lie in some Sylow subgroup),
-- construct an InGenerated chain witnessing that the word's
-- evaluation lies in the joint-Sylow-generated subgroup.
--
-- Y1 of the 10-slice arc per [[prime-factored-gauge-arc]] follow-on
-- discussion (= "joint-gen via presentation, not enumeration").
--
-- KEY STRUCTURAL CONTENT:
--
--   The InGenerated chain IS THE WORD STRUCTURE. For empty word:
--   InGenerated.ident. For non-empty (g ∷ w'): InGenerated.product
--   applied to the generator's Sylow witness + recursive chain for w'.
--
--   This is the substrate's [[expose-generator-not-orbit]] discipline
--   at the joint-gen layer: no per-element enumeration; the chain
--   structure follows the word structure mechanically.
--
-- Per [[universal-property-discipline]]: this lemma bridges
-- PresentedGroup (T2) and SylowDecomposition (T0). Once applied at
-- specific groups (GL(3,F₂) Y4, Z/6 Y5, Monster Y8), it discharges
-- their joint-gen hypotheses without enumeration.
--
-- Per [[roll-our-own-via-word-algebra]]: the Word IS the word algebra;
-- this lemma is how the word algebra delivers joint-gen for free.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.SylowDecomposition.FromWord where

open import Level using (Level)
open import Data.Fin using (Fin)
open import Data.List using (List; []; _∷_)
open import Data.Nat using (ℕ)
open import Data.Product using (Σ; _,_)

open import Substrate.Category.SylowDecomposition
  using (InGenerated)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- 1. Word evaluation: fold a Word over the carrier's binary
-- operation, with each generator mapped to a carrier element.
------------------------------------------------------------------------

evaluate-word :
  {Gen : Set ℓ} {G : Set ℓ}
  (gen-to-elt : Gen → G)
  (_·G_ : G → G → G) (εG : G) →
  List Gen → G
evaluate-word ⌜_⌝ _·G_ εG []      = εG
evaluate-word ⌜_⌝ _·G_ εG (g ∷ w) =
  ⌜ g ⌝ ·G evaluate-word ⌜_⌝ _·G_ εG w

------------------------------------------------------------------------
-- 2. The foundational lemma: every word's evaluation is in the
-- joint-Sylow-generated subgroup, with the InGenerated chain
-- following the word structure.
--
-- Inputs:
--   * gen-to-elt : Gen → G (each generator's carrier element)
--   * n : ℕ (number of Sylow subgroups)
--   * Sylow : Fin n → (G → Set) (Sylow predicates)
--   * gen-to-sylow : (g : Gen) → Σ (Fin n) (λ i → Sylow i (gen-to-elt g))
--     (every generator lies in some Sylow)
--
-- Output: for every Word w, the evaluation evaluate-word ... w is
-- in the InGenerated joint-Sylow subgroup, with the chain structure
-- being induction on w.
------------------------------------------------------------------------

word-to-InGenerated :
  {Gen : Set ℓ} {G : Set ℓ}
  (gen-to-elt : Gen → G)
  (_·G_ : G → G → G) (εG : G)
  {n : ℕ}
  (Sylow : Fin n → (G → Set ℓ))
  (gen-to-sylow : (g : Gen) → Σ (Fin n) (λ i → Sylow i (gen-to-elt g))) →
  (w : List Gen) →
  InGenerated (λ z → Σ (Fin n) (λ i → Sylow i z))
              _·G_ εG
              (evaluate-word gen-to-elt _·G_ εG w)
word-to-InGenerated ⌜_⌝ _·G_ εG Sylow gen-to-sylow [] =
  InGenerated.ident
word-to-InGenerated ⌜_⌝ _·G_ εG Sylow gen-to-sylow (g ∷ w) =
  InGenerated.product ⌜ g ⌝ (evaluate-word ⌜_⌝ _·G_ εG w)
    (InGenerated.base ⌜ g ⌝ (gen-to-sylow g))
    (word-to-InGenerated ⌜_⌝ _·G_ εG Sylow gen-to-sylow w)

------------------------------------------------------------------------
-- 3. Capstone — generic word→chain bridge in place.
--
-- Y1 of the 10-slice arc. This is the LOAD-BEARING lemma for the
-- entire sub-arc: every subsequent slice (Y2-Y9) uses this lemma to
-- discharge joint-gen for specific groups via their presentations.
--
-- Per [[expose-generator-not-orbit]] at the discipline level: 168-,
-- 184-, 194- (and ultimately 10^53-) element enumerations are
-- AVOIDED universally. The word structure provides the InGenerated
-- chain mechanically.
--
-- Next: Y2 (PresentedGroup → joint-gen pipeline composing Y1 with
-- T1's PrimeFactoredGauge).
------------------------------------------------------------------------
