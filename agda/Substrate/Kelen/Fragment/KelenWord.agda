------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.KelenWord
--
-- Defines: KelenWord
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.KelenWord where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Kelen.Fragment.Relational



------------------------------------------------------------------------
-- 2. Sequences of relationals.
--
-- A KelenWord is a sequence of relationals; this is the free
-- carrier in the Free-relation cell. Composition of relationals
-- (relation composition in Rel) is the algebra acting on this
-- carrier; full relation composition is deferred per
-- [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

KelenWord : Set
KelenWord = Word Relational
