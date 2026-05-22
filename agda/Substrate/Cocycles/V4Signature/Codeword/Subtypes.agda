------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.Subtypes
--
-- Reserved (8) and Live (24) as Σ-type wrappers around Codeword.
-- Per multi-reading-ambient discipline, no constructor-based
-- enumeration; the ambient + predicate is the structural commitment.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.Subtypes where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Cocycles.V4Signature.Codeword.Type using (Codeword)
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved using (IsReserved)

Reserved : Set
Reserved = Σ Codeword IsReserved

Live : Set
Live = Σ Codeword (λ cw → ¬ IsReserved cw)
