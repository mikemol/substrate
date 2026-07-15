------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Eval
--
-- T3: evaluation MarkovTerm → semantic target. The term IS the morphism; eval
-- is its denotation, threading each generator's kernel through the target's
-- composition.
--
-- With the payload dissolved to a kernel-generator word (Term LEG 1), the
-- kernel RELATION is recovered HERE — the valuation `lift-Hom : Word K → Hom X Y`
-- is the interpreter that turns a kernel-generator word into a concrete kernel
-- (a Markov matrix / the `X → Y → Set` relation the flat form stored inline).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Eval where

open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Probability.MarkovCategory.Term

-- Parameterised over the object alphabet O, the kernel-generator alphabet K,
-- and the SEMANTIC target — the abstract Hom, its composition, and the kernel
-- valuation `lift-Hom` (which recovers the relation from the generator word).
module _ (O : Set) (K : Set)
         {Hom : O → O → Set}
         (id-Hom : ∀ {X} → Hom X X)
         (comp-Hom : ∀ {X Y Z} → Hom Y Z → Hom X Y → Hom X Z)
         (lift-Hom : ∀ {X Y} → Word K → Hom X Y) where

  eval-gen : ∀ {X Y} → MarkovGen O K X Y → Hom X Y
  eval-gen (lift X Y w) = lift-Hom w

  eval : ∀ {X Y} → MarkovTerm O K X Y → Hom X Y
  eval []       = id-Hom
  eval (g ∷ ts) = comp-Hom (eval ts) (eval-gen g)
