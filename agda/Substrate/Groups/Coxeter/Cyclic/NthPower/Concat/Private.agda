------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.Private (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Base n
open import Substrate.Groups.Coxeter.Cyclic.Core n



-- insert a on power (k mod-suc n) advances by one in mod-suc n.
