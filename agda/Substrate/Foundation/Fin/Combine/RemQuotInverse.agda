------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.RemQuotInverse
--
-- remQuot-combine : remQuot n (combine i j) ≡ (i , j).
-- Induction on i; uses splitAt-{inject, raise} from SplitAt's lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.RemQuotInverse where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Sum using (inj₁; inj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)

remQuot-combine :
  ∀ {m n} (i : Fin m) (j : Fin n) →
  remQuot n (combine i j) ≡ (i , j)
remQuot-combine {suc m} {n} zero j with splitAt n (combine {suc m} {n} zero j)
                                      | splitAt-inject n {m * n} j
... | inj₁ _ | refl = refl
remQuot-combine {suc m} {n} (suc i) j with splitAt n (combine {suc m} {n} (suc i) j)
                                         | splitAt-raise n (combine i j)
                                         | remQuot-combine i j
... | inj₂ _ | refl | ih = cong (λ p → suc (proj₁ p) , proj₂ p) ih
  where
    open import Substrate.Foundation.Product using (proj₁; proj₂)
