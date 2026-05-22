------------------------------------------------------------------------
-- Substrate.Linguistic.RosettaTable
--
-- C9 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- The cross-language Rosetta-table generator: given two
-- LanguageWitness instances, produces an alignment record stating
-- their shared shape (both are FreeOverBasis) and their classifying
-- difference (which FreeConstructionClass cell each occupies).
--
-- This is the "morphisms" side of the category-of-languages
-- (Yoneda perspective from the peer review): C8 gives the objects;
-- C9 gives the alignment-morphisms between pairs of objects.
--
-- Per [[user-rosetta-code-contrastive-pedagogy]]: the
-- pedagogical-product surface. Each RosettaEntry is one row of the
-- contrastive table; the catalog of all pairs is the substrate-
-- native version of a Rosetta Code page.
--
-- Per [[feedback-categorical-name-first]]: the categorical name for
-- the alignment is "morphism in the category of free constructions"
-- — at the moment realised as a comparison record without enforced
-- coherence laws; a future arc can lift this to a proper
-- categorical morphism with composition and identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.RosettaTable where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness; WitnessName; FreeConstructionClass;
         name; class; Basis; FreeCarrier;
         Lojban; TokiPona; Solresol; Kelen; Lambda; LieFrag;
         Free-monoid; Free-F2-module; Free-cyclic;
         Free-relation; Free-CCC; Free-Lie; Free-other)
open import Substrate.Linguistic.Classification
  using (all-witnesses; witness-by-name; witness-by-class;
         _⊎-OR_; here; there)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)

------------------------------------------------------------------------
-- 1. RosettaEntry: a row of the cross-language alignment table.
--
-- Records the pair of names, classes, and the same-class? flag.
-- The substrate-native ⊎-OR carries the YES / NO flag without
-- needing Bool: `here` = same class; `there` = different class.
------------------------------------------------------------------------

record RosettaEntry : Set₁ where
  constructor mkEntry
  field
    left       : LanguageWitness
    right      : LanguageWitness
    same-class : (class left ≡ class right) ⊎-OR (class left ≡ class right → ⊥)

------------------------------------------------------------------------
-- 2. Decidable same-class? for pairs of witnesses.
--
-- The 6×6 = 36 pairs decompose: 6 reflexive same-class entries +
-- 30 different-class entries. Decided structurally on the class
-- enum.
------------------------------------------------------------------------

class-decide :
  (a b : FreeConstructionClass) →
  (a ≡ b) ⊎-OR (a ≡ b → ⊥)
-- Diagonal: same-class entries (7 cases)
class-decide Free-monoid    Free-monoid    = here refl
class-decide Free-F2-module Free-F2-module = here refl
class-decide Free-cyclic    Free-cyclic    = here refl
class-decide Free-relation  Free-relation  = here refl
class-decide Free-CCC       Free-CCC       = here refl
class-decide Free-Lie       Free-Lie       = here refl
class-decide Free-other     Free-other     = here refl
-- Off-diagonal: different-class entries (42 cases)
class-decide Free-monoid    Free-F2-module = there (λ ())
class-decide Free-monoid    Free-cyclic    = there (λ ())
class-decide Free-monoid    Free-relation  = there (λ ())
class-decide Free-monoid    Free-CCC       = there (λ ())
class-decide Free-monoid    Free-Lie       = there (λ ())
class-decide Free-monoid    Free-other     = there (λ ())
class-decide Free-F2-module Free-monoid    = there (λ ())
class-decide Free-F2-module Free-cyclic    = there (λ ())
class-decide Free-F2-module Free-relation  = there (λ ())
class-decide Free-F2-module Free-CCC       = there (λ ())
class-decide Free-F2-module Free-Lie       = there (λ ())
class-decide Free-F2-module Free-other     = there (λ ())
class-decide Free-cyclic    Free-monoid    = there (λ ())
class-decide Free-cyclic    Free-F2-module = there (λ ())
class-decide Free-cyclic    Free-relation  = there (λ ())
class-decide Free-cyclic    Free-CCC       = there (λ ())
class-decide Free-cyclic    Free-Lie       = there (λ ())
class-decide Free-cyclic    Free-other     = there (λ ())
class-decide Free-relation  Free-monoid    = there (λ ())
class-decide Free-relation  Free-F2-module = there (λ ())
class-decide Free-relation  Free-cyclic    = there (λ ())
class-decide Free-relation  Free-CCC       = there (λ ())
class-decide Free-relation  Free-Lie       = there (λ ())
class-decide Free-relation  Free-other     = there (λ ())
class-decide Free-CCC       Free-monoid    = there (λ ())
class-decide Free-CCC       Free-F2-module = there (λ ())
class-decide Free-CCC       Free-cyclic    = there (λ ())
class-decide Free-CCC       Free-relation  = there (λ ())
class-decide Free-CCC       Free-Lie       = there (λ ())
class-decide Free-CCC       Free-other     = there (λ ())
class-decide Free-Lie       Free-monoid    = there (λ ())
class-decide Free-Lie       Free-F2-module = there (λ ())
class-decide Free-Lie       Free-cyclic    = there (λ ())
class-decide Free-Lie       Free-relation  = there (λ ())
class-decide Free-Lie       Free-CCC       = there (λ ())
class-decide Free-Lie       Free-other     = there (λ ())
class-decide Free-other     Free-monoid    = there (λ ())
class-decide Free-other     Free-F2-module = there (λ ())
class-decide Free-other     Free-cyclic    = there (λ ())
class-decide Free-other     Free-relation  = there (λ ())
class-decide Free-other     Free-CCC       = there (λ ())
class-decide Free-other     Free-Lie       = there (λ ())

------------------------------------------------------------------------
-- 3. Pairwise RosettaEntry constructor.
--
-- Build a Rosetta entry for any two witnesses. The same-class flag
-- is decided by class-decide.
------------------------------------------------------------------------

pair-entry : (left right : LanguageWitness) → RosettaEntry
pair-entry l r = mkEntry l r (class-decide (class l) (class r))

------------------------------------------------------------------------
-- 4. Worked cross-language pair entries.
--
-- A handful of demonstrated alignments — the substrate-internal
-- witnesses of the cross-classification work. C10 will display
-- the full pairwise catalog.
------------------------------------------------------------------------

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

-- Lojban × Toki Pona: different cells (discrete word-algebra vs.
-- F₂-module). The original linguistic Rosetta pair.
rosetta-lojban-tokipona : RosettaEntry
rosetta-lojban-tokipona = pair-entry lojban-witness tokipona-witness

-- Lojban × Lambda: both CCC-shaped, but Lambda is PURE FCC while
-- Lojban approximates with n-ary morphism. Different cells in the
-- arc's lattice (Free-monoid vs Free-CCC) but structurally adjacent.
rosetta-lojban-lambda : RosettaEntry
rosetta-lojban-lambda = pair-entry lojban-witness lambda-witness

-- Toki Pona × Solresol: both have "cyclic" flavour (F₂ self-inverse
-- vs. Z/7 cyclic basis) but different cells.
rosetta-tokipona-solresol : RosettaEntry
rosetta-tokipona-solresol = pair-entry tokipona-witness solresol-witness

-- Kelen × Lambda: relations vs. functions — the structural-
-- contrast pair (free-relation cell vs free-CCC cell).
rosetta-kelen-lambda : RosettaEntry
rosetta-kelen-lambda = pair-entry kelen-witness lambda-witness

-- Lojban × Lojban: trivial same-class diagonal entry.
rosetta-lojban-lojban : RosettaEntry
rosetta-lojban-lojban = pair-entry lojban-witness lojban-witness

------------------------------------------------------------------------
-- 5. Sample cross-table.
--
-- A short Vec of representative entries demonstrating that the
-- generator works across all combinations. C10 expands this.
------------------------------------------------------------------------

sample-entries : Vec RosettaEntry 5
sample-entries =
  rosetta-lojban-tokipona     ∷
  rosetta-lojban-lambda       ∷
  rosetta-tokipona-solresol   ∷
  rosetta-kelen-lambda        ∷
  rosetta-lojban-lojban       ∷
  []
