------------------------------------------------------------------------
-- Substrate.Foundation.Bool.Properties.OrXorAnd
--
-- Defines: or-xor-and
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.Properties.OrXorAnd where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Eq
-- identity, read by CayleyDickson/Grade (∨-anf) and Algebra.F2.FromBool (∨-as-xor-recon derives from it).
or-xor-and : (a b : Bool) → (a ∨ b) ≡ (a xor b) xor (a ∧ b)
or-xor-and true  true  = refl
or-xor-and true  false = refl
or-xor-and false true  = refl
or-xor-and false false = refl
