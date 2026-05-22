------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone
--
-- C10 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Capstone slice: top-level re-export of the arc + smoke tests +
-- a worked cross-arc Rosetta table generated mechanically from C9.
--
-- After this slice the substrate has:
--   * A categorical classification of languages by which free
--     construction they instantiate (parent primitive C1).
--   * Six language witnesses across the lattice (C2-C7).
--   * Classification record + lookup (C8).
--   * Rosetta-table generator + sample entries (C9).
--   * The full 6×6 = 36 cross-language alignment table (this slice).
--
-- Per [[user-rosetta-code-contrastive-pedagogy]]: the substrate
-- now produces the contrastive-pedagogy product the user has
-- wanted from the start — language-as-free-construction
-- classification with cross-table alignment as the pedagogical
-- output.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

-- Re-export C1 (parent primitive) publicly so consumers get the
-- whole arc at the capstone module.
open import Substrate.Category.FreeOverBasis public

-- Re-export the six witness modules.
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

-- Re-export the classification + Rosetta-table machinery.
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

------------------------------------------------------------------------
-- 1. The full pairwise cross-table.
--
-- All 6 × 6 = 36 pairs of LanguageWitness with their alignment
-- entries. The table is substrate-internal data; downstream tools
-- (a future markdown-export, a future pedagogical interface) can
-- iterate over it.
------------------------------------------------------------------------

private
  l : LanguageWitness
  l = lojban-witness
  t : LanguageWitness
  t = tokipona-witness
  s : LanguageWitness
  s = solresol-witness
  k : LanguageWitness
  k = kelen-witness
  λ-w : LanguageWitness
  λ-w = lambda-witness
  Λ : LanguageWitness
  Λ = lie-witness

full-cross-table : Vec RosettaEntry 36
full-cross-table =
  -- Row L: Lojban × {L, T, S, K, λ, Λ}
  pair-entry l l ∷ pair-entry l t ∷ pair-entry l s ∷
  pair-entry l k ∷ pair-entry l λ-w ∷ pair-entry l Λ ∷
  -- Row T: TokiPona × {L, T, S, K, λ, Λ}
  pair-entry t l ∷ pair-entry t t ∷ pair-entry t s ∷
  pair-entry t k ∷ pair-entry t λ-w ∷ pair-entry t Λ ∷
  -- Row S: Solresol × {L, T, S, K, λ, Λ}
  pair-entry s l ∷ pair-entry s t ∷ pair-entry s s ∷
  pair-entry s k ∷ pair-entry s λ-w ∷ pair-entry s Λ ∷
  -- Row K: Kelen × {L, T, S, K, λ, Λ}
  pair-entry k l ∷ pair-entry k t ∷ pair-entry k s ∷
  pair-entry k k ∷ pair-entry k λ-w ∷ pair-entry k Λ ∷
  -- Row λ: Lambda × {L, T, S, K, λ, Λ}
  pair-entry λ-w l ∷ pair-entry λ-w t ∷ pair-entry λ-w s ∷
  pair-entry λ-w k ∷ pair-entry λ-w λ-w ∷ pair-entry λ-w Λ ∷
  -- Row Λ: LieFrag × {L, T, S, K, λ, Λ}
  pair-entry Λ l ∷ pair-entry Λ t ∷ pair-entry Λ s ∷
  pair-entry Λ k ∷ pair-entry Λ λ-w ∷ pair-entry Λ Λ ∷
  []

------------------------------------------------------------------------
-- 2. Smoke tests: the classification is internally consistent.
--
-- Each witness belongs to the cell its WitnessName / classification
-- field claims it does. Six refl-cases verify.
------------------------------------------------------------------------

lojban-in-Free-monoid : class lojban-witness ≡ Free-monoid
lojban-in-Free-monoid = refl

tokipona-in-Free-F2-module : class tokipona-witness ≡ Free-F2-module
tokipona-in-Free-F2-module = refl

solresol-in-Free-cyclic : class solresol-witness ≡ Free-cyclic
solresol-in-Free-cyclic = refl

kelen-in-Free-relation : class kelen-witness ≡ Free-relation
kelen-in-Free-relation = refl

lambda-in-Free-CCC : class lambda-witness ≡ Free-CCC
lambda-in-Free-CCC = refl

lie-in-Free-Lie : class lie-witness ≡ Free-Lie
lie-in-Free-Lie = refl

------------------------------------------------------------------------
-- 3. Worked Rosetta entries — the contrastive-pedagogy payoff.
--
-- A handful of cross-language alignments demonstrating the
-- structural-contrast IS pedagogy claim.
------------------------------------------------------------------------

-- The original anchor pair (different cells: Free-monoid vs
-- Free-F2-module).
worked-lojban-tokipona : RosettaEntry
worked-lojban-tokipona = pair-entry lojban-witness tokipona-witness

-- The CCC-adjacent pair: Lojban (monoid, CCC-approximation) vs.
-- Lambda (pure CCC). Different cells; structurally adjacent.
worked-lojban-lambda : RosettaEntry
worked-lojban-lambda = pair-entry lojban-witness lambda-witness

-- The structural-contrast pair: Kelen (relations) vs. Lambda
-- (functions). Categorically distinct ways of composing meaning.
worked-kelen-lambda : RosettaEntry
worked-kelen-lambda = pair-entry kelen-witness lambda-witness

-- The cyclic-flavour pair: TokiPona (F₂ self-inverse) vs. Solresol
-- (Z/7 cyclic basis). Different cells but both have cyclic
-- structure.
worked-tokipona-solresol : RosettaEntry
worked-tokipona-solresol = pair-entry tokipona-witness solresol-witness

-- The fringe-cell pair: LieFrag (substrate-invented Lie cell) vs.
-- Lambda (CCC). Both algebraic; very different free constructions.
worked-lie-lambda : RosettaEntry
worked-lie-lambda = pair-entry lie-witness lambda-witness

------------------------------------------------------------------------
-- 4. Capstone statement.
--
-- After C1-C10 the substrate has a substrate-native, mechanically-
-- generated classification of languages by free-construction. The
-- classification is not aspirational prose — it's typed Agda data
-- that downstream consumers can iterate over, dispatch on, and
-- extend.
--
-- Future arcs:
--   * Add witnesses to the Free-other cell (Ithkuil, Aymara, ...)
--   * Add witness languages for FreeSMC and full FreeLie (invented)
--   * Bicategorify the parent primitive (BZ/2 discussion's payoff)
--   * Lift to a proper category-of-languages with composition
--     and identity morphisms (the Yoneda extension)
------------------------------------------------------------------------
