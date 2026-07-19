------------------------------------------------------------------------
-- Substrate.WitnessTower.VecBoolCardinality
--
-- ◆AI-1d (and the shared core of ◆AI-1b) — the cardinality |Vec Bool n| = 2ⁿ,
-- as a proved TERM, upgrading two SnVersusTwoPow co-apexes from POINTER to
-- refl-identification.
--
-- Decomposed (◆AI-D5) by querying: AI-1b (codeword |Reserved| ≡ 8) and AI-1d
-- (|Vec Bool n| ≡ 2ⁿ) share ONE core. ReservedBridge gives Reserved ↔ Vector 3
-- (= Vec Bool 3, via Axis × Bool ≅ F₂³); so |Reserved| = |Vec Bool 3| = 2³ = 8
-- is the n = 3 INSTANCE of the general |Vec Bool n| = 2ⁿ. AI-1d is the general
-- statement; AI-1b's count is its n = 3 slice composed with the Reserved ↔
-- Vec Bool 3 bijection. Proving the general fact once serves both.
--
-- The count is the length of the full enumeration allVB n (every Bool-vector of
-- length n). allVB (suc n) = (false ∷ each) ++ (true ∷ each), so the length
-- doubles: 2ⁿ + 2ⁿ = 2 · 2ⁿ = 2^(suc n). Pure induction, refl base.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.VecBoolCardinality where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _^_; _+_; _*_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.WitnessTower.Enumerate using (lengthL; mapL)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ)

------------------------------------------------------------------------
-- 1. The enumeration of all Bool-vectors of length n.
------------------------------------------------------------------------

allVB : (n : ℕ) → List (Vec Bool n)
allVB zero    = [] ∷ []
allVB (suc n) = mapL (false ∷_) (allVB n) ++ mapL (true ∷_) (allVB n)

------------------------------------------------------------------------
-- 2. Length helpers (list length under map and ++).
------------------------------------------------------------------------

length-map : {A B : Set} (f : A → B) (xs : List A) →
             lengthL (mapL f xs) ≡ lengthL xs
length-map f []       = refl
length-map f (x ∷ xs) = cong suc (length-map f xs)

length-++ : {A : Set} (xs ys : List A) →
            lengthL (xs ++ ys) ≡ lengthL xs + lengthL ys
length-++ []       ys = refl
length-++ (x ∷ xs) ys = cong suc (length-++ xs ys)

------------------------------------------------------------------------
-- 3. THE CARDINALITY: |Vec Bool n| = 2ⁿ. The enumeration has length 2ⁿ.
--    Step: length (allVB (suc n)) = 2ⁿ + 2ⁿ, and 2^(suc n) = 2 · 2ⁿ = 2ⁿ + 2ⁿ
--    (definitionally, since 2 * x = x + (1 * x) = x + (x + 0) = x + x).
------------------------------------------------------------------------

-- 2ⁿ + 2ⁿ ≡ 2^(suc n). Since 2^(suc n) = 2 * 2ⁿ = 2ⁿ + (1 * 2ⁿ), close the
-- residual 1 * 2ⁿ ≡ 2ⁿ with *-identityˡ.
double-pow : (n : ℕ) → (2 ^ n) + (2 ^ n) ≡ 2 ^ suc n
double-pow n = cong ((2 ^ n) +_) (sym (*-identityˡ (2 ^ n)))

card-VecBool : (n : ℕ) → lengthL (allVB n) ≡ 2 ^ n
card-VecBool zero    = refl
card-VecBool (suc n) =
  trans (length-++ (mapL (false ∷_) (allVB n)) (mapL (true ∷_) (allVB n)))
        (trans (cong₂ _+_
                 (trans (length-map (false ∷_) (allVB n)) (card-VecBool n))
                 (trans (length-map (true ∷_)  (allVB n)) (card-VecBool n)))
               (double-pow n))

------------------------------------------------------------------------
-- 4. ◆AI-1d instance: |Vec Bool 4| = 16, and the ceiling exponents used by
--    SnVersusTwoPow (5, 7) as basis-index counts — the 2ⁿ column of the sweep
--    is now a proved cardinality, not a bare literal.
------------------------------------------------------------------------

card-4  : lengthL (allVB 4) ≡ 16   ; card-4  = card-VecBool 4
card-5  : lengthL (allVB 5) ≡ 32   ; card-5  = card-VecBool 5

------------------------------------------------------------------------
-- 5. ◆AI-1b core: |Vec Bool 3| = 8. This is the count behind the codeword's
--    Reserved: ReservedBridge gives Reserved ↔ Vector 3 (= Vec Bool 3, via
--    Axis × Bool ≅ F₂³), so |Reserved| = |Vec Bool 3| = 2³ = 8. The bijection
--    lives in ReservedBridge; this file supplies the COUNT it transports.
------------------------------------------------------------------------

card-reserved-core : lengthL (allVB 3) ≡ 8
card-reserved-core = card-VecBool 3

------------------------------------------------------------------------
-- 6. ◆AI-1b' — the Codeword ↔ Vec Bool 5 bridge, connecting the codeword
--    tuple type to the Vec Bool cardinality machinery. Codeword = Bool⁵ (a
--    5-tuple, Codeword.Type); this bijection lets |Codeword| = |Vec Bool 5| =
--    32 (card-5) transport, and is the carrier the Reserved count rides on.
--
--    HONEST SCOPE (◆AI-D4): this bridge + card-5 give |Codeword| = 32 as a
--    TERM. The full |Reserved| ≡ 8 additionally needs a filter-count (length
--    of the isReserved-sublist of the enumeration) — a genuine build, NOT a
--    pointer-tighten. That remainder is ◆AI-1b'' below; here the counting core
--    (card-reserved-core : |Vec Bool 3| = 8) + this bridge + card-5 are the
--    pieces it composes.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (_,_; _×_)
open import Substrate.Cocycles.V4Signature.Codeword.Type using (Codeword)

cw→vec : Codeword → Vec Bool 5
cw→vec (b0 , b1 , b2 , b3 , b4) = b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ []

vec→cw : Vec Bool 5 → Codeword
vec→cw (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ []) = b0 , b1 , b2 , b3 , b4

cw→vec→cw : (cw : Codeword) → vec→cw (cw→vec cw) ≡ cw
cw→vec→cw (b0 , b1 , b2 , b3 , b4) = refl

vec→cw→vec : (v : Vec Bool 5) → cw→vec (vec→cw v) ≡ v
vec→cw→vec (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ []) = refl

-- |Codeword| = 32 : the ambient count, transported from card-5 via the bridge.
-- (allVB 5 enumerates Vec Bool 5 with length 32; mapL vec→cw enumerates Codeword.)
codeword-ambient-32 : lengthL (mapL vec→cw (allVB 5)) ≡ 32
codeword-ambient-32 = trans (length-map vec→cw (allVB 5)) card-5
