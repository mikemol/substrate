------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.Insert
--
-- Defines: insert
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Negation.Dec
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Word.Length

module Substrate.Groups.Coxeter.Cyclic.Base.Insert (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

------------------------------------------------------------------------
-- 7. insert — cyclic Word-level shift.
--
-- For length w < n: prepend `a`. For length ≥ n: wrap to ε.
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert g w with length w <? n
... | yes _ = g ∷ w
... | no  _ = []

