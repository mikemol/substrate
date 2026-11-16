------------------------------------------------------------------------
-- Substrate.Category.PolyLens.Eval (T11)
-- PolyLensTerm → semantic polymorphism via Poly.Eval.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PolyLens.Eval where

open import Substrate.Category.PolyLens.Term
-- ⚑ `public` RETIRED (Ⓑ2c).  Zero external importers — this module forwarded
-- `eval` to nobody.  ⚑ AND THAT LEAVES THE FILE A PURE CONDUIT: it defines
-- nothing, so with the forward gone its two imports are its whole body.  A
-- retire candidate (ⓉBARREL-REST), not a repair — recorded, not acted on here.
open import Substrate.Category.Poly.Eval using (eval)
