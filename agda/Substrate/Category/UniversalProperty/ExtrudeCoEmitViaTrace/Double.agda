------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Double
--
-- Defines: double
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.Double where

open import Substrate.Foundation.Nat.Nat



-- FAITHFUL ℕ-encoding of a CoEmit node: parity tags the constructor (even = ret value, odd = emit output),
-- so the head is injective on observations. ret a is terminal → it loops (tail = itself), giving the
-- constant stream 2a; emitᶜ o k advances to k with head 2o+1.
double : ℕ → ℕ
double zero    = zero
double (suc n) = suc (suc (double n))
