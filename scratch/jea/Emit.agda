------------------------------------------------------------------------
-- scratch/jea/Emit.agda
--
-- The Agda end of the Agda-on-GPU bridge. A term algebra defined HERE in Agda;
-- the GPU cooperative-generator evaluator (scripts/jea_generator_dag*.py) computes
-- it, exact, and must agree with Agda's own value.
--
-- The bridge needs the term's STRUCTURE and VALUE out of Agda. Rather than MAlonzo +
-- IO plumbing, the TYPECHECKER is the bridge (substrate --safe spirit): `render term`
-- and `evalStr term` are proved EQUAL to string literals by `refl`, so the literals are
-- machine-verified to be the term's faithful serialization and value. scripts/
-- jea_agda_bridge.py typechecks this file (the refls = the guarantee), reads termStr /
-- valStr, evaluates the term on the GPU, and checks the GPU root == valStr.
------------------------------------------------------------------------

{-# OPTIONS --safe #-}

module Emit where

open import Data.Nat using (ℕ; _+_; _*_)
open import Data.Nat.Show using (show)
open import Data.String using (String; _++_)
open import Data.Product using (_×_; _,_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- The term algebra: ℚ leaves (num,den) with binary + and ×. This is the
-- SPPF free-semiring term (gen / _⊗_ / _⊕_) specialised to a ℚ valuation:
-- lf = gen, mul = _⊗_, add = _⊕_.
------------------------------------------------------------------------

data Term : Set where
  lf  : ℕ → ℕ → Term            -- a leaf rational num/den (gen)
  add : Term → Term → Term      -- _⊕_  (semiring +)
  mul : Term → Term → Term      -- _⊗_  (semiring ×)

-- the example term:  (2/3 + 1/2) * (1/4 * 3/5)
term : Term
term = mul (add (lf 2 3) (lf 1 2)) (mul (lf 1 4) (lf 3 5))

------------------------------------------------------------------------
-- render: the term's structure as an S-expression (what the bridge parses
-- into the GPU DAG vN/vD/lch/rch/op).
------------------------------------------------------------------------

render : Term → String
render (lf n d)  = "(lf " ++ show n ++ " " ++ show d ++ ")"
render (add a b) = "(add " ++ render a ++ " " ++ render b ++ ")"
render (mul a b) = "(mul " ++ render a ++ " " ++ render b ++ ")"

------------------------------------------------------------------------
-- eval: Agda's OWN value of the term, UNREDUCED (num,den) — the GPU's exact
-- reduced result must equal this as a rational. (Unreduced keeps eval trivial;
-- the bridge compares via Fraction, and the GPU does the gcd reduction.)
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- THE VOUCHERS. These string literals are what the bridge reads; the refls
-- are Agda's machine-checked guarantee that they ARE the term's serialization
-- and value. If the term changes, these fail to typecheck until updated.
------------------------------------------------------------------------

termStr : String
termStr = "(mul (add (lf 2 3) (lf 1 2)) (mul (lf 1 4) (lf 3 5)))"

valStr : String
valStr = "21/120"        -- (2/3+1/2)*(1/4*3/5) unreduced = 21/120 = 7/40

term-serialises : render term ≡ termStr
term-serialises = refl

term-evaluates : evalStr term ≡ valStr
term-evaluates = refl
