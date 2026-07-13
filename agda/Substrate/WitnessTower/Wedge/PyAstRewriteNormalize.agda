------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewriteNormalize
--
-- ⟡pyrig-rebuild-normalize — the CORRECTED normalize. (The old
-- PyAstRigNormalize built `normalize t = mapSPPF (rank (positions t)) t` — a
-- position-interning of an SPPF TERM, the WRONG carrier.) In the corrected rig a
-- rewrite IS a permutation, and its NORMAL FORM is the Lehmer factoradic — so
-- `normalize` is the tower's `encode`, REUSED, not rebuilt:
--
--   normalize = encode : (σ : Perm n) → IsPerm σ → PyRewrite n
--
-- The rewrite-level normal form is a BIJECTION (each permutation ↔ its UNIQUE
-- Lehmer word), and its two round-trips are the tower's OWN iso lemmas
-- (`encode-decode` / `decode-encode`) — the LehmerPath ≅ {permutations} iso. And it
-- is the two-sided inverse of the SnRig semantics `interp` (= decode-with-witness):
-- interpreting the normal word recovers the permutation (`interp-normalizeS`). So
-- normalize is the ORBIT-INTERNING KEY at the rewrite level — not new, the tower's
-- factoradic canonicalizer.
--
-- (Orbit COLLAPSE — many term-reorderings ↦ one key — is the OBJECT story, not the
-- rewrite one: rewrites are the group elements, each its own normal word.
-- ⟡pyrig-object-carrier.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewriteNormalize where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; trans)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath
  using (decode; encode; decode-is-perm; decode-encode; encode-decode)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym using (Iso→IsPerm)
open import Substrate.WitnessTower.Wedge.PyAstRewrite using (PyRewrite)
open import Substrate.WitnessTower.Wedge.PyAstRewriteSnRig using (Sₙ; interp; interp-is-decode; snEq)

-- THE NORMAL FORM: a permutation's canonical rewrite word. Reused verbatim — the tower's encode.
normalize : {n : ℕ} (σ : Perm n) → IsPerm σ → PyRewrite n
normalize = encode

-- 1. a rewrite WORD is already normal — normalizing its own permutation returns it (encode-decode).
normalize-decode : {n : ℕ} (l : PyRewrite n) → normalize (decode l) (decode-is-perm l) ≡ l
normalize-decode = encode-decode

-- 2. normalize is a SECTION — decoding the normal word recovers the permutation (decode-encode).
decode-normalize : {n : ℕ} (σ : Perm n) (perm : IsPerm σ) → decode (normalize σ perm) ≡ σ
decode-normalize = decode-encode

------------------------------------------------------------------------
-- 3. THE INVERSE OF THE SnRig SEMANTICS. interp (= foldR SnRig) is decode-with-witness;
--    normalize on an Sₙ element is its inverse: interpreting the normal word recovers it.
------------------------------------------------------------------------
normalizeS : {n : ℕ} → Sₙ n → PyRewrite n
normalizeS s = normalize (proj₁ s) (Iso→IsPerm (proj₁ s) (proj₂ s))

interp-normalizeS : {n : ℕ} (s : Sₙ n) → interp (normalizeS s) ≡ s
interp-normalizeS s =
  snEq (trans (interp-is-decode (normalizeS s))
              (decode-encode (proj₁ s) (Iso→IsPerm (proj₁ s) (proj₂ s))))
