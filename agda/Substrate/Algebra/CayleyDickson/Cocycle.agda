------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Cocycle
--
-- ⊙.morton (foundation): the F₂ⁿ-indexing of the Cayley-Dickson basis — the
-- structure conjecture C3 (Morton ≅ Cayley-Dickson via the cocycle) rests on.
--
-- The 2ⁿ-dimensional algebra `Carrier n` has a basis indexed by F₂ⁿ: a bit
-- string is the doubling PATH (false = real half, true = imaginary half), and
-- `e n idx` is the unit with 1ℚ at that leaf. The index group op is XOR (F₂ⁿ
-- addition), and the basis product carries a SIGN-COCYCLE: eᵢ·eⱼ = ε(i,j)·e_{i⊕j}.
--
-- Built here: the index→basis map `e`, the index XOR, and the cocycle at the ℂ
-- corner (ε(1,1) = −1, i.e. i² = −1 recast in the F₂ⁿ frame). The cocycle's
-- NONTRIVIALITY is already `CommuteEdge.mul-noncomm-ℍ` (ε(i,j) ≠ ε(j,i) at
-- level 2). OPEN (the deep cell): the GENERIC product law eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j}
-- for all n, the explicit ε, its 2-cocycle identity, and Morton (trivial ε) vs
-- CD (nontrivial ε).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Cocycle where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Bool using (Bool; true; false; _xor_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; zipWith)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.CayleyDickson
  using (Carrier; mul; neg; conj; ≈#; zero#; one#; i; i²≈−1)
open import Substrate.Algebra.CayleyDickson.Setoid
  using (≈#-refl; ≈#-sym; ≈#-trans; neg-zero#; conj-zero#)

-- F₂ⁿ index → CD basis unit: 1ℚ at the leaf addressed by the n bits.
e : (n : ℕ) → Vec Bool n → Carrier n
e zero    []           = one# 0                  -- the scalar unit 1
e (suc n) (false ∷ bs) = e n bs , zero# n        -- real half
e (suc n) (true  ∷ bs) = zero# n , e n bs        -- imaginary half

-- The index group operation is F₂ⁿ addition = pointwise XOR, i.e. the
-- carrier-home `Vec.zipWith _xor_` (reused, no new Vec operator).

-- THE SIGN-COCYCLE at the ℂ corner: e[1]·e[1] ≈# −e[1⊕1] = −e[0] — so ε(1,1) = −1
-- (i² = −1 in the F₂ⁿ-cocycle frame; the index adds via XOR (zipWith _xor_), the
-- sign is ε). The cocycle's nontriviality is `CommuteEdge.mul-noncomm-ℍ` (level 2).
ℂ-sign-cocycle :
  ≈# 1 (mul 1 (e 1 (true ∷ [])) (e 1 (true ∷ [])))
       (neg 1 (e 1 (zipWith _xor_ (true ∷ []) (true ∷ []))))
ℂ-sign-cocycle = i²≈−1

------------------------------------------------------------------------
-- CONJUGATION ON A BASIS UNIT: conj eᵢ = ±eᵢ — the scalar is fixed, every
-- imaginary unit is negated. (The first prerequisite of the recursive product
-- law: the CD doubling product conjugates one factor.) `imag?` = "index has a
-- true bit" (= an imaginary unit); `sgn` applies the resulting ± sign.
------------------------------------------------------------------------

imag? : {n : ℕ} → Vec Bool n → Bool
imag? []           = false
imag? (true  ∷ _)  = true
imag? (false ∷ bs) = imag? bs

sgn : Bool → (n : ℕ) → Carrier n → Carrier n
sgn true  n x = neg n x
sgn false n x = x

conj-on-basis : (n : ℕ) (idx : Vec Bool n) →
                ≈# n (conj n (e n idx)) (sgn (imag? idx) n (e n idx))
conj-on-basis zero    []           = ≈#-refl 0 (e 0 [])
conj-on-basis (suc n) (true  ∷ is) =
    ≈#-trans n (conj-zero# n) (≈#-sym n (neg-zero# n))
  , ≈#-refl n (neg n (e n is))
conj-on-basis (suc n) (false ∷ is) with imag? is | conj-on-basis n is
... | false | ih = ih , neg-zero# n
... | true  | ih = ih , ≈#-refl n (neg n (zero# n))
