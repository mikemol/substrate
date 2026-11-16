------------------------------------------------------------------------
-- Substrate.Algebra.F1.GL.GLF1
--
-- Defines: GL-F₁, backward, forward, inv-left, inv-right
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.GL; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.GL.GLF1 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.PointedSet.Map.Anon
open import Substrate.Foundation.Eq
open import Substrate.Algebra.F1.GL.F1N



------------------------------------------------------------------------
-- 2. GL(n, F₁) = basepoint-preserving bijections of F₁ⁿ.
--
-- A "linear automorphism" of F₁ⁿ is a PointedSetMap with a two-
-- sided inverse. The bundled record names the automorphism shape.
------------------------------------------------------------------------

record GL-F₁ (n : ℕ) : Set where
  field
    forward    : PointedSetMap (F₁ⁿ n) (F₁ⁿ n)
    backward   : PointedSetMap (F₁ⁿ n) (F₁ⁿ n)
    inv-left   : (x : Fin (suc n)) →
                 apply backward (apply forward x) ≡ x
    inv-right  : (x : Fin (suc n)) →
                 apply forward (apply backward x) ≡ x

open GL-F₁ public
