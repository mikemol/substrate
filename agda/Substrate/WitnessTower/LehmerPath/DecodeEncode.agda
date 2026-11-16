------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.DecodeEncode
--
-- Defines: decode-encode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.DecodeEncode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Decompose
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.Encode
-- ⚑ Vec's constructors must be DIRECTLY in scope, or the `[]` in the {zero}
-- clause below is parsed as a fresh pattern VARIABLE shadowing `Vec.[]` — so σ
-- is never definitionally `[]` and the `refl` fails with
-- `Vec.[] != [] of type Vec (Fin fzero) fzero`.  Agda reports this as the
-- PatternShadowsConstructor warning immediately above the error.
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



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
