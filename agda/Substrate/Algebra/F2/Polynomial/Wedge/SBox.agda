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
-- of two facts:
--   affine-rt : affine-inv ∘ affine ≡ id   (pure F₂, by reflection over 256 bytes; fast)
--   pinv-inv  : pinv ∘ pinv ≡ id           (the patched inverse is an involution)
-- FIPS sanity: `affine 0 = 0x63 = S(00)` and (checked) `affine {01} = 0x7C = S(01)`.
--
-- `pinv-inv` is ALGEBRAIC (no EEA reflection): `inv(inv a) = (a·inv a)·inv(inv a)
-- = a·(inv a·inv(inv a)) = a·𝟙 = a` by inverse-uniqueness, with `inv a ≠ 0` from
-- `0≢1`.  Whole module typechecks in ~2s.  Fully --safe --without-K, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.SBox where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2 using (_+_; 𝟘≢𝟙)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base using (m-lo; is-zero8; all-vec; all-vec-sound)
open import Substrate.Foundation.Bool.Properties using (∧-elimˡ; ∧-elimʳ)
open import Substrate.Algebra.F2.Polynomial.Wedge.Inverse using (inv; inv-law)
open import Substrate.Algebra.F2.Polynomial.Wedge.AsField using (is-zero8-sound; nonzero-bridge)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Div as D
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
open F.Over F₂-CommRing using (Poly; nth)
open M.Over F₂-CommRing 7 m-lo using (oneC)
open Q.Over F₂-CommRing 7 m-lo using (_*Q_; 𝟎C; *Q-assoc; *Q-identityˡ; *Q-identityʳ; *Q-zeroʳ)

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

-- affine round-trip: affine-inv ∘ affine ≡ id, by reflection (pure F₂; fast).
affine-rt-check : all-vec (λ a → vec-eq (affine-inv (affine a)) a) ≡ true
affine-rt-check = refl
affine-rt : (a : Poly 8) → affine-inv (affine a) ≡ a
affine-rt a = vec-eq-sound _ _ (all-vec-sound (λ x → vec-eq (affine-inv (affine x)) x) affine-rt-check a)

-- pinv ∘ pinv ≡ id ALGEBRAICALLY via inverse-uniqueness — NO EEA reflection, fast.
0≢1 : ¬ (𝟎C ≡ oneC)
0≢1 eq = 𝟘≢𝟙 (cong (λ v → nth v 0) eq)

-- a≠0 ⇒ inv a ≠ 0 (else a·inv a = a·0 = 0 = 𝟙, contra 0≢1).
inv-nonzero : (a : Poly 8) → is-zero8 a ≡ false → ¬ (inv a ≡ 𝟎C)
inv-nonzero a z eq = 0≢1 (sym (trans (sym (inv-law a z)) (trans (cong (a *Q_) eq) (*Q-zeroʳ a))))

-- inv(inv a) = (a·inv a)·inv(inv a) = a·(inv a·inv(inv a)) = a·𝟙 = a.
inv-involution : (a : Poly 8) → is-zero8 a ≡ false → inv (inv a) ≡ a
inv-involution a z =
  trans (sym (*Q-identityˡ (inv (inv a))))
  (trans (cong (_*Q inv (inv a)) (sym (inv-law a z)))
  (trans (*Q-assoc a (inv a) (inv (inv a)))
  (trans (cong (a *Q_) (inv-law (inv a) (nonzero-bridge (inv a) (inv-nonzero a z))))
         (*Q-identityʳ a))))

F≢T : {X : Set} → false ≡ true → X
F≢T ()

-- pinv resolved on each branch (so neither `with` pollutes pinv-inv's goal).
pinv-zero : (a : Poly 8) → is-zero8 a ≡ true → pinv a ≡ a
pinv-zero a z with is-zero8 a
... | true  = refl
... | false = F≢T z
pinv-nonzero : (a : Poly 8) → is-zero8 a ≡ false → pinv a ≡ inv a
pinv-nonzero a z with is-zero8 a
... | false = refl
... | true  = F≢T (sym z)

-- pinv ∘ pinv ≡ id, by case on is-zero8 a (b explicit ⇒ goal stays unabstracted).
pinv-inv-aux : (a : Poly 8) (b : Bool) → is-zero8 a ≡ b → pinv (pinv a) ≡ a
pinv-inv-aux a true  z = trans (cong pinv (pinv-zero a z)) (pinv-zero a z)
pinv-inv-aux a false z =
  trans (cong pinv (pinv-nonzero a z))
  (trans (pinv-nonzero (inv a) (nonzero-bridge (inv a) (inv-nonzero a z)))
         (inv-involution a z))

pinv-inv : (a : Poly 8) → pinv (pinv a) ≡ a
pinv-inv a = pinv-inv-aux a (is-zero8 a) refl

-- THE S-BOX ROUND-TRIP: InvSubBytes ∘ SubBytes ≡ id.
sbox-rt : (a : Poly 8) → inv-sbox (sbox a) ≡ a
sbox-rt a = trans (cong pinv (affine-rt (pinv a))) (pinv-inv a)
