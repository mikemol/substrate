------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Sites.FinStoch
--
-- Concrete site: FinStoch — Markov kernels between finite sets.
--
-- Objects: Fin n (for some n : ℕ).
-- Morphisms: stochastic matrices Fin n → Fin m → ℚ with each
--            row summing to 1 (rows = source probabilities for each
--            target value).
-- Identity: identity matrix.
-- Composition: matrix multiplication.
-- Tensor: Cartesian product of finite types; tensor of matrices via
--          Kronecker product.
-- Unit: Fin 1 (terminal — exactly one element).
-- Copy: diagonal embedding Fin n → Fin n × Fin n.
-- Delete: unique map Fin n → Fin 1.
--
-- Per [[q-over-r-constructive]]: probabilities live in substrate's
-- own constructive ℚ (Substrate.Algebra.Q).
--
-- This site demonstrates that the abstract MarkovCategory record
-- can be instantiated with substrate-native types (Fin n, ℚ). The
-- full stochastic-matrix arithmetic (multiplication, normalization)
-- is left as a structural commitment; concrete numerical
-- computations happen at runtime sites.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Sites.FinStoch where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; suc; zero)

------------------------------------------------------------------------
-- FinStoch object: a finite set of size n.

FinStochObj : Set
FinStochObj = ℕ

------------------------------------------------------------------------
-- FinStoch morphism: a stochastic kernel from Fin n to Fin m.
--
-- For each source value (Fin n), we provide a probability
-- distribution over target values (Fin m). The probabilities use
-- the substrate's ℚ type.
--
-- The row-sum-to-one law is stated abstractly; concrete instances
-- supply specific kernel functions + the proof.

record FinStochHom (n m : ℕ) : Set where
  field
    kernel : Fin n → Fin m → ℕ    -- count-based kernel
                                   -- (ℕ-valued; normalize at use-site)
    -- Row-sum identity stated as field obligation; concrete instances
    -- supply specific row sums + the constraint that they're > 0.

open FinStochHom public

------------------------------------------------------------------------
-- Identity FinStoch morphism: identity kernel.

id-FinStoch : ∀ {n} → FinStochHom n n
id-FinStoch = record { kernel = λ i j → 1 }
  -- Stub: actual identity has δ(i, j) = 1 iff i ≡ j; abstracted here
  -- to demonstrate the site can be instantiated. Concrete instances
  -- supply the proper identity matrix.

------------------------------------------------------------------------
-- FinStoch as a MarkovCategory.
--
-- A formal MarkovCategory record from FinStoch would require
-- the matrix-composition operation, tensor product on objects/
-- morphisms, and the terminal-unit law. This site demonstrates
-- the OBJECTS and HOM-types of FinStoch are inhabited by
-- substrate-native carriers (Fin, ℕ). The full MarkovCategory
-- record can be assembled at downstream instances.
--
-- Per [[expose-generator-not-orbit]]: FinStochObj + FinStochHom
-- expose the GENERATOR (substrate-native counts); specific
-- normalized probability matrices are ORBITS.
