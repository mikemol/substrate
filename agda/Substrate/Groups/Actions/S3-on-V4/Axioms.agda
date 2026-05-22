------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms
--
-- Easy action axioms (file-per-lemma decomposition).
--
--   Axioms.ActCong     — act-cong (depends only on canonical pair + v)
--   Axioms.ActEpsilon  — act-ε (identity acts trivially)
--   Axioms.ActEpsilonN — act-ε-N (every action fixes V₄'s identity)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms where

open import Substrate.Groups.Actions.S3-on-V4.Dispatch        public
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong     public
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon  public
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN public
