------------------------------------------------------------------------
-- Substrate.Foundation.Bool.IfThenElse
--
-- Defines: if_then_else_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.IfThenElse where

open import Substrate.Foundation.Bool.Bool



if_then_else_ : {A : Set} → Bool → A → A → A
if true  then x else _ = x
if false then _ else y = y
