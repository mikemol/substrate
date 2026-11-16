------------------------------------------------------------------------
-- The graded wedge on `Bin`: the generic length-graded vector carrier at
-- Bool. Cited, not built — `recon` IS cons (VecGraded.recon-is-cons).
-- Context: Substrate/Algebra/Wedge/Bin/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bin.BinGraded where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.Algebra.Wedge.Bin.Carrier

bin-graded : GradedDivStr Bin (λ _ → Bool)
bin-graded = vec-graded Bool
