------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Base.Gen
--
-- Defines: Gen
-- ⚑cap-128-forcing: one lemma, one elaboration unit (split horizontally
--   out of Substrate.Groups.Coxeter.Cyclic.Base; telescope carried by split_telescoped).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ these imports precede the module header BECAUSE THE TELESCOPE USES
--   them: a parameter list is scope-checked before anything in `where`.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong

module Substrate.Groups.Coxeter.Cyclic.Base.Gen where


------------------------------------------------------------------------
-- 1. Gen: single generator.
------------------------------------------------------------------------

data Gen : Set where      -- ⟦shape:d42c6364 a⟧
  a : Gen
