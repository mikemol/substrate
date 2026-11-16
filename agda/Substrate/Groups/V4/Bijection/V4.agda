------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.V4
--
-- Defines: V₄, e, α, β, γ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.V4 where

import Substrate.Groups.V4-Coxeter as C



------------------------------------------------------------------------
-- The carrier.
------------------------------------------------------------------------

data V₄ : Set where
  e α β γ : V₄
