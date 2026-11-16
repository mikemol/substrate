------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition
--
-- transposition (i j : Fin 3) : SFinP.Permutation 3.
-- Parametric transposition swapping i and j (fixing the third index).
-- Symmetric in (i, j); no chirality-choice generators. When i ≡ j the
-- result is the identity.
--
-- transposition-fixes-third : transposition i j fixes any index that
-- is neither i nor j.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey-S3.Transposition where

open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Negation.Dec

import Substrate.Groups.SFin.Apply as SFinA
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq

transposition : (i j : Fin 3) → SFinP.Permutation 3
transposition i j = record
  { apply  = swap-fn
  ; invₐ   = swap-fn
  ; inv-l  = swap-invo
  ; inv-r  = swap-invo
  }
  where
    swap-fn : Fin 3 → Fin 3
    swap-fn k with k ≟ᶠ i
    ... | yes _ = j
    ... | no _ with k ≟ᶠ j
    ...           | yes _ = i
    ...           | no _  = k

    swap-invo : (k : Fin 3) → swap-fn (swap-fn k) ≡ k
    swap-invo k with k ≟ᶠ i
    ... | yes refl with j ≟ᶠ i
    ...               | yes refl = refl
    ...               | no _ with j ≟ᶠ j
    ...                          | yes _ = refl
    ...                          | no q = ⊥-elim (q refl)
    swap-invo k | no q1 with k ≟ᶠ j
    ... | yes refl with i ≟ᶠ i
    ...               | yes _ = refl
    ...               | no q = ⊥-elim (q refl)
    swap-invo k | no q1 | no q2 with k ≟ᶠ i
    ... | yes a = ⊥-elim (q1 a)
    ... | no _ with k ≟ᶠ j
    ...           | yes b = ⊥-elim (q2 b)
    ...           | no _ = refl

transposition-fixes-third :
  (i j k : Fin 3) → k ≢ i → k ≢ j →
  SFinA.apply (transposition i j) k ≡ k
transposition-fixes-third i j k k≢i k≢j with k ≟ᶠ i
... | yes p = ⊥-elim (k≢i p)
... | no _ with k ≟ᶠ j
... | yes p = ⊥-elim (k≢j p)
... | no _ = refl
