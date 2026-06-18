------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath  (Ⓣ₁ — Sₙ is BUILT OF the witnessing step)
--
-- The constructive reduction "the symmetric group is the witness tower",
-- as a theorem rather than a narration. `WitnessTower.Core` gives the bare
-- spine — `Path` (`start`, `_witnesses_`), each rung witnessing the one
-- below. A PERMUTATION is that same path with a CHOICE attached at each
-- step: where the new top element inserts. That decorated path is the
-- factoradic / Lehmer code, and decoding it IS the witnessing walk.
--
--   Core.witnessing : WSimplex k → WSimplex (suc k)      -- the bare step
--   _◂_             : LehmerPath k → Fin (suc k) → …      -- step + its choice
--   decode (l ◂ p)  = insert-at p (decode l)              -- = the walk
--
-- So `insert-at` (Enumerate) is the witnessing step decorated by its
-- insertion position, `decompose` (Decompose) is the inverse (un-witness),
-- and the headline `decode-encode` says: EVERY permutation equals the result
-- of decoding its own factoradic path — i.e. is built of exactly n
-- witnessing steps. This is the STRUCTURE-level companion of
-- `WitnessTower.Wedge.Factoradic` (which does it at the COUNT level: the
-- choice-alphabet sizes Fin (suc k) are that module's radices `suc k`).
--
-- SCOPE (not overclaimed): `decode-encode` (decode ∘ encode ≡ id — every
-- permutation is its path) is proved here. The dual `encode ∘ decode ≡ id`
-- (the path is unique = decode injective) is deferred (Ⓣ₁b): it needs
-- decompose ∘ insert-at = id, which threads the IsPerm proof through punchOut
-- and wants punchOut∘punchIn = id — a separate brick.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; [])
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; IsPerm-[]; insert-at-preserves)
open import Substrate.WitnessTower.Decompose
  using (decomp-head; decomp-tail; decomp-tail-perm; decomp-correct)

------------------------------------------------------------------------
-- 1. The decorated witness path: Core.Path with an insertion-CHOICE at each
--    step. At rung k the new top witnesses the rung below by choosing one of
--    the (suc k) positions — exactly the factoradic digit Fin (suc k).
------------------------------------------------------------------------

data LehmerPath : ℕ → Set where
  start : LehmerPath zero
  _◂_   : ∀ {k} → LehmerPath k → Fin (suc k) → LehmerPath (suc k)

infixl 5 _◂_

------------------------------------------------------------------------
-- 2. decode = the witnessing WALK: replay the choices, each `_◂_` an
--    `insert-at`. Every decoded path is a genuine permutation (the walk
--    never leaves Sₙ — insert-at-preserves at each rung).
------------------------------------------------------------------------

decode : ∀ {n} → LehmerPath n → Perm n
decode start    = []
decode (l ◂ p)  = insert-at p (decode l)

decode-is-perm : ∀ {n} (l : LehmerPath n) → IsPerm (decode l)
decode-is-perm start   = IsPerm-[]
decode-is-perm (l ◂ p) = insert-at-preserves p (decode l) (decode-is-perm l)

------------------------------------------------------------------------
-- 3. encode = the inverse walk: peel the top element off with `decompose`
--    (its position is the rung's choice), recurse on the smaller permutation.
------------------------------------------------------------------------

encode : ∀ {n} (σ : Perm n) → IsPerm σ → LehmerPath n
encode {zero}  σ perm = start
encode {suc n} σ perm =
  encode (decomp-tail σ perm) (decomp-tail-perm σ perm) ◂ decomp-head σ

------------------------------------------------------------------------
-- 4. THE REDUCTION: every permutation IS its decoded factoradic path — it is
--    built of exactly n witnessing steps. (decode ∘ encode ≡ id, by
--    induction: the top step is recovered by decomp-correct, the rest by IH.)
------------------------------------------------------------------------

decode-encode : ∀ {n} (σ : Perm n) (perm : IsPerm σ) → decode (encode σ perm) ≡ σ
decode-encode {zero}  []  perm = refl
decode-encode {suc n} σ   perm =
  trans (cong (insert-at (decomp-head σ))
              (decode-encode (decomp-tail σ perm) (decomp-tail-perm σ perm)))
        (sym (decomp-correct σ perm))
