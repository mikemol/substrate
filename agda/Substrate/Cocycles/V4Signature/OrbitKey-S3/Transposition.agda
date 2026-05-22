------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
--
-- transposition (i j : Fin 3) : SFin.Permutation 3.
-- Parametric transposition swapping i and j (fixing the third index).
-- Symmetric in (i, j); no chirality-choice generators. When i ≡ j the
-- result is the identity.
--
-- transposition-fixes-third : transposition i j fixes any index that
-- is neither i nor j.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition where

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Properties using (_≟_)
open import Substrate.Foundation.Eq using (_≡_; _≢_; refl)
open import Substrate.Foundation.Negation using (yes; no)

import Substrate.Groups.SFin as SFin

transposition : (i j : Fin 3) → SFin.Permutation 3
transposition i j = record
  { apply  = swap-fn
  ; invₐ   = swap-fn
  ; inv-l  = swap-invo
  ; inv-r  = swap-invo
  }
  where
    swap-fn : Fin 3 → Fin 3
    swap-fn k with k ≟ i
    ... | yes _ = j
    ... | no _ with k ≟ j
    ...           | yes _ = i
    ...           | no _  = k

    swap-invo : (k : Fin 3) → swap-fn (swap-fn k) ≡ k
    swap-invo k with k ≟ i
    ... | yes refl with j ≟ i
    ...               | yes refl = refl
    ...               | no _ with j ≟ j
    ...                          | yes _ = refl
    ...                          | no q = ⊥-elim (q refl)
    swap-invo k | no q1 with k ≟ j
    ... | yes refl with i ≟ i
    ...               | yes _ = refl
    ...               | no q = ⊥-elim (q refl)
    swap-invo k | no q1 | no q2 with k ≟ i
    ... | yes a = ⊥-elim (q1 a)
    ... | no _ with k ≟ j
    ...           | yes b = ⊥-elim (q2 b)
    ...           | no _ = refl

transposition-fixes-third :
  (i j k : Fin 3) → k ≢ i → k ≢ j →
  SFin.apply (transposition i j) k ≡ k
transposition-fixes-third i j k k≢i k≢j with k ≟ i
... | yes p = ⊥-elim (k≢i p)
... | no _ with k ≟ j
... | yes p = ⊥-elim (k≢j p)
... | no _ = refl
