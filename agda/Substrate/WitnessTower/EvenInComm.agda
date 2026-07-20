------------------------------------------------------------------------
-- Substrate.WitnessTower.EvenInComm
--
-- ◆ip-cap-reverse — the two internal datatypes used by the proof of
-- Aₙ ⊆ [Sₙ,Sₙ]:
--
--   Tri i j    — the trichotomy of a pair of gen-indices (equal /
--                adjacent-either-order / separated-either-order).
--   AllInj1 w  — a word all of whose letters are `inj1 j` (never the top
--                element), the well-formedness a flattened Coxeter
--                derivation enjoys.
--
-- The proofs (even→InComm, conj-gtransp, classify, foldInComm, …) live in
-- EvenInComm.Properties (a proof module) — this definition module keeps a
-- proof-free import closure (def/proof separation policy).
--
-- --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.EvenInComm where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin) renaming (suc to fsuc)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral using (inj1)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid using (Sep)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

-- the trichotomy of a pair of adjacent-transposition gen-indices.
data Tri : {m : ℕ} (i j : Fin m) → Set where
  tri-eq   : {m : ℕ} {i j : Fin m} → i ≡ j → Tri i j
  tri-adj  : {n : ℕ} (k : Fin n) → Tri (inj1 k) (fsuc k)
  tri-adj' : {n : ℕ} (k : Fin n) → Tri (fsuc k) (inj1 k)
  tri-sep  : {m : ℕ} {i j : Fin m} → Sep i j → Tri i j
  tri-sep' : {m : ℕ} {i j : Fin m} → Sep j i → Tri i j

-- a word all of whose letters are `inj1 j` (never the top element).
data AllInj1 : {n : ℕ} → Word (Fin n) → Set where
  ai-nil  : {n : ℕ} → AllInj1 {n} []
  ai-cons : {m : ℕ} (j : Fin m) {w : Word (Fin (ℕ.suc m))} →
            AllInj1 w → AllInj1 (inj1 j ∷ w)
