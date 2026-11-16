------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SemidirectProductGroup.Private
--
-- Defines: H, N
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.SemidirectProductGroup; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑⚑ THE SIX-PARAMETER TELESCOPE WAS DROPPED BY THE SPLIT (Ⓐ¹⁴).  This file
-- referenced `G-N`/`G-H` — parameters of the pre-split parent — with nothing
-- binding them, so it named two free variables.  Recovered verbatim from
-- `--at 771283c8^`; the parent declared:
--
--   module …SemidirectProductGroup
--     (N-Carrier : Set) (_≈N_ : N-Carrier → N-Carrier → Set)
--     (G-N : SetoidGroup N-Carrier _≈N_)
--     (H-Carrier : Set) (_≈H_ : H-Carrier → H-Carrier → Set)
--     (G-H : SetoidGroup H-Carrier _≈H_)
--
-- ⚑ AND THE `private` KEYWORD IS GONE.  The parent wrote `private module N = …`;
-- under file-per-lemma that block is this whole file, and its sibling
-- `WithAction` needs `N.`/`H.` — a `private` here would hide from the one
-- consumer that exists.  `private` is banned for exactly this reason: it narrows
-- a surface that decomposition has already narrowed.
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Algebra.Q.HetBasis

module Substrate.Groups.Coxeter.SemidirectProductGroup.Private
  (N-Carrier : Set) (_≈N_ : N-Carrier → N-Carrier → Set)
  (G-N : SetoidGroup N-Carrier _≈N_)
  (H-Carrier : Set) (_≈H_ : H-Carrier → H-Carrier → Set)
  (G-H : SetoidGroup H-Carrier _≈H_)
  where

module N = SetoidGroup G-N
module H = SetoidGroup G-H
