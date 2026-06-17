------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.SBox  (AI-10: the AES S-box)
--
-- The Rijndael S-box as a STRUCTURAL composition (not a table):
--   sbox     a = affine     (pinv a)        -- SubBytes
--   inv-sbox b = pinv (affine-inv b)        -- InvSubBytes
-- where `pinv` is the verified GF(2⁸) inverse patched with 0 ↦ 0 (AI-8), and
-- `affine`/`affine-inv` are the fixed F₂ affine maps of FIPS-197 §5.1.1/§5.3.2.
--
-- ROUND-TRIP `inv-sbox ∘ sbox ≡ id` (InvSubBytes ∘ SubBytes) is the composition
-- of two finite F₂ facts, each by REFLECTION over all 256 bytes:
--   affine-rt : affine-inv ∘ affine ≡ id   (pure F₂; fast)
--   pinv-inv  : pinv ∘ pinv ≡ id           (the patched inverse is an involution)
-- FIPS sanity: `affine 0 = 0x63 = S(00)` and (checked) `affine {01} = 0x7C = S(01)`.
--
-- COST NOTE: `pinv-inv-check` normalises the EEA twice per byte (~512 runs, ~90s).
-- A future optimisation replaces it with the ALGEBRAIC involution (inv(inv a) = a
-- by inverse-uniqueness: inv(inv a) = (a·inv a)·inv(inv a) = a·(inv a·inv(inv a)) = a),
-- which needs no reflection — left as a fast-build follow-up.  Fully --safe, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.SBox where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2 using (_+_)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit
  using (m-lo; is-zero8; all-vec; all-vec-sound; ∧-elimˡ; ∧-elimʳ)
open import Substrate.Algebra.F2.Polynomial.Wedge.Inverse using (inv)
import Substrate.Algebra.Polynomial.Graded.Div as D
open D.Over F₂-CommRing 7 m-lo using (Poly)

-- decidable equality on bit vectors, and its soundness.
_==F_ : F2.F₂ → F2.F₂ → Bool
F2.𝟘 ==F F2.𝟘 = true
F2.𝟙 ==F F2.𝟙 = true
_    ==F _    = false
==F-sound : (x y : F2.F₂) → (x ==F y) ≡ true → x ≡ y
==F-sound F2.𝟘 F2.𝟘 h = refl
==F-sound F2.𝟙 F2.𝟙 h = refl
==F-sound F2.𝟘 F2.𝟙 ()
==F-sound F2.𝟙 F2.𝟘 ()

vec-eq : {n : ℕ} → Vec F2.F₂ n → Vec F2.F₂ n → Bool
vec-eq []       []       = true
vec-eq (x ∷ xs) (y ∷ ys) = (x ==F y) ∧ vec-eq xs ys
vec-eq-sound : {n : ℕ} (a b : Vec F2.F₂ n) → vec-eq a b ≡ true → a ≡ b
vec-eq-sound []       []       h = refl
vec-eq-sound (x ∷ xs) (y ∷ ys) h =
  cong₂ _∷_ (==F-sound x y (∧-elimˡ {x ==F y} h)) (vec-eq-sound xs ys (∧-elimʳ {x ==F y} h))

-- FIPS-197 §5.1.1 affine: bᵢ = aᵢ ⊕ a₍ᵢ₊₄₎ ⊕ a₍ᵢ₊₅₎ ⊕ a₍ᵢ₊₆₎ ⊕ a₍ᵢ₊₇₎ ⊕ cᵢ,  c = 0x63.
affine : Poly 8 → Poly 8
affine (a0 ∷ a1 ∷ a2 ∷ a3 ∷ a4 ∷ a5 ∷ a6 ∷ a7 ∷ []) =
   (a0 + a4 + a5 + a6 + a7 + F2.𝟙) ∷
   (a1 + a5 + a6 + a7 + a0 + F2.𝟙) ∷
   (a2 + a6 + a7 + a0 + a1 + F2.𝟘) ∷
   (a3 + a7 + a0 + a1 + a2 + F2.𝟘) ∷
   (a4 + a0 + a1 + a2 + a3 + F2.𝟘) ∷
   (a5 + a1 + a2 + a3 + a4 + F2.𝟙) ∷
   (a6 + a2 + a3 + a4 + a5 + F2.𝟙) ∷
   (a7 + a3 + a4 + a5 + a6 + F2.𝟘) ∷ []

-- FIPS-197 §5.3.2 inverse affine: aᵢ = b₍ᵢ₊₂₎ ⊕ b₍ᵢ₊₅₎ ⊕ b₍ᵢ₊₇₎ ⊕ dᵢ,  d = 0x05.
affine-inv : Poly 8 → Poly 8
affine-inv (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
   (b2 + b5 + b7 + F2.𝟙) ∷
   (b3 + b6 + b0 + F2.𝟘) ∷
   (b4 + b7 + b1 + F2.𝟙) ∷
   (b5 + b0 + b2 + F2.𝟘) ∷
   (b6 + b1 + b3 + F2.𝟘) ∷
   (b7 + b2 + b4 + F2.𝟘) ∷
   (b0 + b3 + b5 + F2.𝟘) ∷
   (b1 + b4 + b6 + F2.𝟘) ∷ []

-- patched GF(2⁸) inverse: 0 ↦ 0, else the multiplicative inverse (AI-8).
pinv : Poly 8 → Poly 8
pinv a with is-zero8 a
... | true  = a
... | false = inv a

sbox     : Poly 8 → Poly 8
sbox a = affine (pinv a)
inv-sbox : Poly 8 → Poly 8
inv-sbox b = pinv (affine-inv b)

-- FIPS-197 sanity: S(00) = 0x63 = [1,1,0,0,0,1,1,0].
sbox-00 : sbox (F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ [])
        ≡ (F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ [])
sbox-00 = refl

-- the two finite F₂ facts, by reflection over all 256 bytes.
affine-rt-check : all-vec (λ a → vec-eq (affine-inv (affine a)) a) ≡ true
affine-rt-check = refl
pinv-inv-check : all-vec (λ a → vec-eq (pinv (pinv a)) a) ≡ true
pinv-inv-check = refl

affine-rt : (a : Poly 8) → affine-inv (affine a) ≡ a
affine-rt a = vec-eq-sound _ _ (all-vec-sound (λ x → vec-eq (affine-inv (affine x)) x) affine-rt-check a)
pinv-inv : (a : Poly 8) → pinv (pinv a) ≡ a
pinv-inv a = vec-eq-sound _ _ (all-vec-sound (λ x → vec-eq (pinv (pinv x)) x) pinv-inv-check a)

-- THE S-BOX ROUND-TRIP: InvSubBytes ∘ SubBytes ≡ id.
sbox-rt : (a : Poly 8) → inv-sbox (sbox a) ≡ a
sbox-rt a = trans (cong pinv (affine-rt (pinv a))) (pinv-inv a)
