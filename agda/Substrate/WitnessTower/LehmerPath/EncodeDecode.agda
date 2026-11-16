------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.EncodeDecode
--
-- Defines: encode-decode′
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.EncodeDecode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Decompose
open import Substrate.WitnessTower.DuplicateFree
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.Encode
open import Substrate.WitnessTower.LehmerPath.DecompHeadInsert
open import Substrate.WitnessTower.LehmerPath.DecompTailInsert
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Sym
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ProofEq



------------------------------------------------------------------------
-- 6. (Ⓣ₁b) encode ∘ decode ≡ id — every factoradic path is its own
--    re-encoding. Generalised over the IsPerm proof (so the recursion can
--    feed whatever proof `decomp-tail-perm` yields), then specialised.
------------------------------------------------------------------------

encode-decode′ : ∀ {n} (l : LehmerPath n) (pf : IsPerm (decode l)) →
                 encode (decode l) pf ≡ l
encode-decode′ start    pf = refl
encode-decode′ (l ◂ p)  pf =
  cong₂ _◂_ tail-eq (decomp-head-insert p (decode l))
  where
    eq : decomp-tail (insert-at p (decode l)) pf ≡ decode l
    eq = decomp-tail-insert p (decode l) pf
    tail-eq : encode (decomp-tail (insert-at p (decode l)) pf)
                     (decomp-tail-perm (insert-at p (decode l)) pf) ≡ l
    tail-eq = subst (λ Z → (pZ : IsPerm Z) → encode Z pZ ≡ l) (sym eq)
                    (encode-decode′ l)
                    (decomp-tail-perm (insert-at p (decode l)) pf)
