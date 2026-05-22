------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Chirality.Type
--
-- Chirality: which coset of A₄ in S₄ — even = A₄, odd = S₄ \ A₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Chirality.Type where

data Chirality : Set where
  even odd : Chirality
