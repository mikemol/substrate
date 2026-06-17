------------------------------------------------------------------------
-- jea/agda-emit/EmitBig.agda
--
-- Δ-Φ maturation: a refl-VOUCHED Agda term whose value EXCEEDS u128 (217 bits),
-- so the Agda-on-GPU path is driven AT A MAGNITUDE the old u64/u128 carriers cannot
-- hold. Same term algebra as Emit.agda (lf / add / mul over ℚ); here a 7-leaf mul-chain
-- of ~31-bit primes -> a 217-bit product. The apex (scripts/jea_apex_deliver) escalates
-- u128 -> byte-limb and returns this EXACT value; agda --safe vouches the literals by refl.
--
-- The point: the SUBSUMING SOLVE is fed by the term-ALGEBRA at any magnitude, not a
-- hand-built DAG and not a hardcoded carrier. scripts/jea_agda_apex.py reads these vouchers.
------------------------------------------------------------------------

{-# OPTIONS --safe #-}

module EmitBig where

open import Data.Nat using (ℕ; _+_; _*_)
open import Data.Nat.Show using (show)
open import Data.String using (String; _++_)
open import Data.Product using (_×_; _,_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

data Term : Set where
  lf  : ℕ → ℕ → Term
  add : Term → Term → Term
  mul : Term → Term → Term

-- a 7-leaf mul-chain of ~31-bit primes; unreduced value = their product (217 bits, > 2^128)
term : Term
term = mul (lf 2000000011 1) (mul (lf 2000000033 1) (mul (lf 2000000063 1) (mul (lf 2000000087 1) (mul (lf 2000000089 1) (mul (lf 2000000099 1) (lf 2000000147 1))))))

render : Term → String
render (lf n d)  = "(lf " ++ show n ++ " " ++ show d ++ ")"
render (add a b) = "(add " ++ render a ++ " " ++ render b ++ ")"
render (mul a b) = "(mul " ++ render a ++ " " ++ render b ++ ")"

eval : Term → ℕ × ℕ
eval (lf n d)  = n , d
eval (add a b) = let (an , ad) = eval a
                     (bn , bd) = eval b
                 in (an * bd + bn * ad) , (ad * bd)
eval (mul a b) = let (an , ad) = eval a
                     (bn , bd) = eval b
                 in (an * bn) , (ad * bd)

evalStr : Term → String
evalStr t = let (n , d) = eval t in show n ++ "/" ++ show d

termStr : String
termStr = "(mul (lf 2000000011 1) (mul (lf 2000000033 1) (mul (lf 2000000063 1) (mul (lf 2000000087 1) (mul (lf 2000000089 1) (mul (lf 2000000099 1) (lf 2000000147 1)))))))"

valStr : String
valStr = "128000033856003644192205284630446710982233764154798680134967628851/1"

term-serialises : render term ≡ termStr
term-serialises = refl

term-evaluates : evalStr term ≡ valStr
term-evaluates = refl
