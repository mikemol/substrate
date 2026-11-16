------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.IsoDecodeLift
--
-- decode-DENSITY — the "prove on generators, then lift over the free UP" β-move,
-- as a reusable combinator. Every permutation IS `decode (encode σ)` (decode-encode),
-- so any property holding on ALL decode-images (all LehmerPath words) holds on any
-- `(σ, Iso σ)`. Proving on the tower's OWN generators (the Lehmer words) and lifting
-- is cheaper and avoids the dense form — exactly the free-extension β-interface.
--
-- (Extracted from PyAstRewriteSnRig, where the `rewrite sym (decode-encode …)`
-- skeleton was written TWICE — surfaced as the reuse interner's apex signal. The
-- carrier is the funext-free Sₙ witness `Iso` (OrientationRigCatSym).)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.IsoDecodeLift where

open import Substrate.Foundation.Nat.Nat
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath.Decode
open import Substrate.WitnessTower.LehmerPath.DecodeEncode
open import Substrate.WitnessTower.LehmerPath.Encode
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Iso
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.IsoToIsPerm
open import Substrate.Foundation.Eq.Sym

-- lift a property proven for every decode-image to any permutation-with-Iso.
on-iso : ∀ {n} {P : Perm n → Set} →
         ((l : LehmerPath n) → P (decode l)) → (σ : Perm n) → Iso σ → P σ
on-iso pf σ iσ rewrite sym (decode-encode σ (Iso→IsPerm σ iσ)) = pf (encode σ (Iso→IsPerm σ iσ))

-- binary variant (a property of two permutations).
on-iso₂ : ∀ {m n} {P : Perm m → Perm n → Set} →
          ((lσ : LehmerPath m) (lτ : LehmerPath n) → P (decode lσ) (decode lτ)) →
          (σ : Perm m) → Iso σ → (τ : Perm n) → Iso τ → P σ τ
on-iso₂ pf σ iσ τ iτ
  rewrite sym (decode-encode σ (Iso→IsPerm σ iσ))
        | sym (decode-encode τ (Iso→IsPerm τ iτ))
  = pf (encode σ (Iso→IsPerm σ iσ)) (encode τ (Iso→IsPerm τ iτ))
