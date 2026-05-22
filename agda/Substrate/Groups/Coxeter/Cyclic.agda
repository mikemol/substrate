------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic
--
-- The cyclic Coxeter framework as a single parametric module, indexed
-- by the order n+1 of the group. The per-Zₙ named-constructor
-- enumeration (c-ε / c-a / c-aa / …) collapses into one structural
-- constructor `c-here k` for k : Fin (suc n).
--
-- Thin re-export shim — implementation lives in the per-concern
-- submodules (Base / Bridge / Inverse / Existential / Core),
-- each small enough to one-pass rewrite per the substrate's
-- file-size-one-pass-rewrite discipline.
--
-- Submodule layering:
--   Base        — Gen, power, Canonical (indexed), canonical-cover,
--                 bijection to Fin, σ + σ-HasOrderPerm, insert (Word).
--   Bridge      — insert-power-eq, insert-canonical (indexed),
--                 per-case insert helpers.
--   Inverse     — inv-pos, inv (Word), inv-canonical (indexed).
--   Existential — Canonical-ex view + ex-versions + ListPresentation
--                 outer module (normalize + normalize-canonical).
--   Core        — power-canonical-bounded, canonical-is-fixed,
--                 iter / iter-insert-pos / insert-cycle-id-word,
--                 normalize-power-prepend, insert-append-lemma,
--                 opens WithLemmas (the Coxeter Core surface).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)

module Substrate.Groups.Coxeter.Cyclic (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Core n public
