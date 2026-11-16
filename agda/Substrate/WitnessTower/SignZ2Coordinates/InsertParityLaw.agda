------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.InsertParityLaw
--
-- Defines: insert-parity-law
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.InsertParityLaw where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool.Xor
open import Substrate.Algebra.F2.FromBool
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeIsPerm
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.TowerCocycleGraded
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsInvcount
open import Substrate.WitnessTower.SignZ2Coordinates.TowerSignIsLength



------------------------------------------------------------------------
-- ◆ip-chirality-apex — THE COVER = the two cross-linking TERMS above
-- (tower-sign-is-invcount ℕ+ tower-sign-is-length), which meet the flagship
-- terms sign-as-parity (Chirality) and sign-wd (the ℤ/2 well-defined). The
-- cover is PURE PROOF, NOT a record: a record fielding these proofs would drag
-- proof-module imports into a def-provider (def/proof-separation), and it would
-- add no content over the terms — exactly why Chirality itself "declares no
-- record". The graded sign coordinate agreeing with both static guises IS the
-- pair of terms; no bundling is needed or wanted.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- THE SINGLE-INSERTION SIGN LAW, as a TOTAL DICHOTOMY (not a ¬∀ quantification):
-- the circumstance where it HOLDS, the circumstance where it FAILS, and the two
-- combined are TOTAL — via decidability (Bool has decidable equality; Dec/Set₀,
-- our set₁-avoiding machinery). The bare carrier Perm n = Vec (Fin n) n includes
-- NON-permutations; the law is base-dependent there, base-independent (= the
-- digit parity) exactly on permutations.
------------------------------------------------------------------------

-- the law equation at (p, σ) — a Bool equality, so Set₀ (a …→Set family, uncounted).
insert-parity-law : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → Set
insert-parity-law p σ = sign (insert-at p σ) ≡ (oddB (toℕ p) xor sign σ)
