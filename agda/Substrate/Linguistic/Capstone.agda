------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone
--
-- C10 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Capstone slice (file-per-lemma decomposition):
--
--   Capstone.CrossTable   — 6×6 = 36 pairwise RosettaEntry table
--   Capstone.SmokeTests   — 6 refl-cases verifying classification
--   Capstone.Worked       — 5 worked Rosetta entries
--
-- After C1-C10 the substrate has a substrate-native, mechanically-
-- generated classification of languages by free-construction.
-- Downstream consumers can iterate over `full-cross-table`, dispatch
-- on the 6-witness lattice, and extend with new cells.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone where

-- Re-export C1 (parent primitive) + the six witness modules + the
-- classification/Rosetta machinery so consumers see the whole arc.
open import Substrate.Category.FreeOverBasis public

open import Substrate.Lojban.AsFreeOverBasis public
  using (lojban-witness; lojban-free-structure)
open import Substrate.TokiPona.AsFreeOverBasis public
  using (tokipona-witness; tokipona-free-structure)
open import Substrate.Solresol.Fragment public
  using (solresol-witness; solresol-free-structure;
         Note; SolresolWord; transpose-1; transpose-7; transpose-7-id)
open import Substrate.Kelen.Fragment public
  using (kelen-witness; kelen-free-structure;
         Relational; KelenWord; arity)
open import Substrate.Lambda.Fragment public
  using (lambda-witness; lambda-free-structure;
         Combinator; SKIWord;
         S; K; I; B; C;
         expr-I; expr-SKK; expr-B-derived)
open import Substrate.Invented.LieFragment public
  using (lie-witness; lie-free-structure;
         LieGen; LieExpr; gen; bracket;
         expr-x; expr-xy; expr-jacobi-1; expr-jacobi-2)

open import Substrate.Linguistic.Classification public
  using (witness-count; all-witnesses;
         witness-by-name; witness-by-class;
         name∘witness-by-name; class∘witness-by-class;
         _⊎-OR_; here; there)
open import Substrate.Linguistic.RosettaTable public
  using (RosettaEntry; mkEntry; pair-entry; class-decide;
         rosetta-lojban-tokipona; rosetta-lojban-lambda;
         rosetta-tokipona-solresol; rosetta-kelen-lambda;
         rosetta-lojban-lojban; sample-entries)

-- File-per-lemma capstone submodules.
open import Substrate.Linguistic.Capstone.CrossTable public
open import Substrate.Linguistic.Capstone.SmokeTests public
open import Substrate.Linguistic.Capstone.Worked     public
