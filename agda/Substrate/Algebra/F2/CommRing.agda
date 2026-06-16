------------------------------------------------------------------------
-- Substrate.Algebra.F2.CommRing
--
-- F₂ as a CommutativeRing (F₂-Ring + multiplicative commutativity). The A=F₂
-- base of the AI-17 `R[y]` tower: instantiating `Polynomial.Graded.Over` here
-- reproduces F₂[x]'s graded ring laws as the generic functor's A=F₂ instance.
-- (Non-destructive: F₂'s hand-built `Polynomial.RingLaws` stays as the optimized
-- concrete copy GF256 consumes; this only witnesses they ARE the same construction.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.CommRing where

open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
open import Substrate.Algebra.F2 using (·-comm)
open import Substrate.Algebra.F2.AsField using (F₂-Ring)

F₂-CommRing : CommutativeRing _
F₂-CommRing = record { ring = F₂-Ring ; *-comm = ·-comm }
