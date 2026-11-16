------------------------------------------------------------------------
-- CORRECTNESS, for VARIABLE operands at every grade:
--
--   value (addBits c as bs) ℕ+ 2ⁿ · carryOut c as bs ≡ c ℕ+ (value as ℕ+ value bs)
--
-- i.e. the n result bits together with the carry-out at weight 2ⁿ are
-- exactly the sum of the two operands and the carry-in.
-- Context: Substrate/Algebra/Wedge/BinArith/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinArith.AddUCorrect where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Mul.TimesDistribRPlus
open import Substrate.Foundation.Nat.Properties.Mul.TimesIdentityL
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Shuffle
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Algebra.Wedge.BinArith.Pow2
open import Substrate.Algebra.Wedge.BinArith.SumBit
open import Substrate.Algebra.Wedge.BinArith.CarryBit
open import Substrate.Algebra.Wedge.BinArith.FullAdder
open import Substrate.Algebra.Wedge.BinArith.AddBits
open import Substrate.Algebra.Wedge.BinArith.CarryOut
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans

addU-correct :
  {n : ℕ} (c : Bool) (as bs : Bin n) →
  value (addBits c as bs) ℕ+ pow2 n * boolToℕ (carryOut c as bs)
  ≡ boolToℕ c ℕ+ (value as ℕ+ value bs)
addU-correct c [] [] =
  trans (+ℕ-identityˡ (suc zero * boolToℕ c))
  (trans (*-identityˡ (boolToℕ c))
         (sym (+ℕ-identityʳ (boolToℕ c))))
addU-correct {suc n} c (a ∷ as) (b ∷ bs) =
  let c′ = carryBit c a b
      rs = addBits c′ as bs
      co = carryOut c′ as bs
      s  = sumBit c a b
      w  = pow2 n * boolToℕ co
  in
  trans (cong ((boolToℕ s ℕ+ (value rs ℕ+ value rs)) ℕ+_)
              (*-distribʳ-+ (boolToℕ co) (pow2 n) (pow2 n)))
  (trans (+ℕ-assoc (boolToℕ s) (value rs ℕ+ value rs) (w ℕ+ w))
  (trans (cong (boolToℕ s ℕ+_) (shuffle (value rs) (value rs) w w))
  (trans (cong (λ z → boolToℕ s ℕ+ (z ℕ+ z)) (addU-correct c′ as bs))
  (trans (cong (boolToℕ s ℕ+_)
               (shuffle (boolToℕ c′) (value as ℕ+ value bs)
                        (boolToℕ c′) (value as ℕ+ value bs)))
  (trans (sym (+ℕ-assoc (boolToℕ s) (boolToℕ c′ ℕ+ boolToℕ c′)
                       ((value as ℕ+ value bs) ℕ+ (value as ℕ+ value bs))))
  (trans (cong (_ℕ+ ((value as ℕ+ value bs) ℕ+ (value as ℕ+ value bs)))
               (sym (full-adder c a b)))
  (trans (+ℕ-assoc (boolToℕ c) (boolToℕ a ℕ+ boolToℕ b)
                  ((value as ℕ+ value bs) ℕ+ (value as ℕ+ value bs)))
         (cong (boolToℕ c ℕ+_)
               (trans (cong ((boolToℕ a ℕ+ boolToℕ b) ℕ+_)
                            (shuffle (value as) (value bs) (value as) (value bs)))
                      (shuffle (boolToℕ a) (boolToℕ b)
                               (value as ℕ+ value as) (value bs ℕ+ value bs)))))))))))
