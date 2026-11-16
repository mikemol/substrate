------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.IsReserved
--
-- IsReserved cw : the load-bearing decidable predicate.
-- Reserved iff the high-two bits are both zero. Equivalent to "the
-- codeword's ordering-selector is in the signed-singleton subspace."
-- isReserved? : decision procedure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.IsReserved where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Negation.Dec
open import Substrate.Cocycles.V4Signature.Codeword.Type using (Codeword; bit₃; bit₄)
open import Substrate.Foundation.Eq

IsReserved : Codeword → Set
IsReserved cw = (bit₃ cw ≡ false) × (bit₄ cw ≡ false)

isReserved? : (cw : Codeword) → Dec (IsReserved cw)
isReserved? (_ , _ , _ , false , false) = yes (refl , refl)
isReserved? (_ , _ , _ , true  , false) = no (λ { (() , _) })
isReserved? (_ , _ , _ , false , true)  = no (λ { (_ , ()) })
isReserved? (_ , _ , _ , true  , true)  = no (λ { (() , _) })
