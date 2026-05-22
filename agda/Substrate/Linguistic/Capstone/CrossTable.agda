------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone.CrossTable
--
-- The full pairwise cross-table — all 6 × 6 = 36 RosettaEntry pairs.
-- Substrate-internal data; downstream tools (markdown-export, future
-- pedagogical interface) can iterate over it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone.CrossTable where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)
open import Substrate.Linguistic.RosettaTable using (RosettaEntry; pair-entry)

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
