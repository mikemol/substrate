{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable  (AI-7s: verified S-box = AES)
--
-- CERTIFIES that the verified S-box construction `sbox = affine . pinv`
-- (AI-10, built on the verified GF(2^8) inverse AI-8) computes EXACTLY the
-- canonical FIPS-197 S-box table, for all 256 inputs:
--   sbox-is-aes : (a) -> byte-val (sbox a) == SBOX[byte-val a].
-- This closes the G8 "is the verified construction really the AES spec?" gap
-- at its nonlinear CRUX (the S-box is the only nontrivial layer; ShiftRows/
-- MixColumns/AddRoundKey are linear).  Pure proof, no oracle.
--
-- COST: a 256-byte reflection that normalises the EEA inverse once per byte
-- (~56s).  This is inherently computational -- the table IS its values, so
-- there is no algebraic shortcut (cf. AI-10 pinv-inv, which had one).
--
-- B-deep (2026-06-18): this module now ALSO hosts the canonical, evaluation-
-- CHEAP S-box `sbox = nb ∘ idx SBOX ∘ byte-val` (a table lookup), with the
-- GF(2⁸)-inversion construction (`affine ∘ pinv`, imported as `sbox-gf`)
-- retained as a proven THEOREM `sbox≡gf` (via `sbox-is-aes` + the 8-bit
-- round-trip `byte-roundtrip`). The cipher (F2/AES/) now imports `sbox` /
-- `inv-sbox` / `sbox-rt` from HERE so its forcing (e.g. AES/KAT key schedule)
-- is a table lookup, not a GF inversion — the FIPS rigor is preserved because
-- the table IS the verified S-box (sbox-is-aes). --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂; sym)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBox
  using (inv-sbox) renaming (sbox to sbox-gf; sbox-rt to sbox-gf-rt) public
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit
  using (m-lo; all-vec; all-vec-sound; ∧-elimˡ; ∧-elimʳ)
import Substrate.Algebra.Polynomial.Graded.Div as D
open D.Over F₂-CommRing 7 m-lo using (Poly)

-- numeric value of a byte (LSB-first: index 0 = x^0 = bit 0).
bit : F2.F₂ → ℕ
bit F2.𝟘 = 0
bit F2.𝟙 = 1
byte-val : {n : ℕ} → Vec F2.F₂ n → ℕ
byte-val []       = 0
byte-val (b ∷ bs) = bit b + 2 * byte-val bs

-- decidable ℕ equality.
_==ℕ_ : ℕ → ℕ → Bool
zero  ==ℕ zero  = true
suc m ==ℕ suc n = m ==ℕ n
_     ==ℕ _     = false
==ℕ-sound : (m n : ℕ) → (m ==ℕ n) ≡ true → m ≡ n
==ℕ-sound zero    zero    h = refl
==ℕ-sound (suc m) (suc n) h = cong suc (==ℕ-sound m n h)
==ℕ-sound zero    (suc n) ()
==ℕ-sound (suc m) zero    ()

-- ℕ-indexed lookup (in range for byte values).
idx : {n : ℕ} → Vec ℕ n → ℕ → ℕ
idx []       _       = 0
idx (x ∷ xs) zero    = x
idx (x ∷ xs) (suc k) = idx xs k

-- the canonical AES S-box (FIPS-197 Fig. 7), as decimal byte values.
SBOX : Vec ℕ 256
SBOX =
   99 ∷ 124 ∷ 119 ∷ 123 ∷ 242 ∷ 107 ∷ 111 ∷ 197 ∷  48 ∷   1 ∷ 103 ∷  43 ∷ 254 ∷ 215 ∷ 171 ∷ 118 ∷
  202 ∷ 130 ∷ 201 ∷ 125 ∷ 250 ∷  89 ∷  71 ∷ 240 ∷ 173 ∷ 212 ∷ 162 ∷ 175 ∷ 156 ∷ 164 ∷ 114 ∷ 192 ∷
  183 ∷ 253 ∷ 147 ∷  38 ∷  54 ∷  63 ∷ 247 ∷ 204 ∷  52 ∷ 165 ∷ 229 ∷ 241 ∷ 113 ∷ 216 ∷  49 ∷  21 ∷
    4 ∷ 199 ∷  35 ∷ 195 ∷  24 ∷ 150 ∷   5 ∷ 154 ∷   7 ∷  18 ∷ 128 ∷ 226 ∷ 235 ∷  39 ∷ 178 ∷ 117 ∷
    9 ∷ 131 ∷  44 ∷  26 ∷  27 ∷ 110 ∷  90 ∷ 160 ∷  82 ∷  59 ∷ 214 ∷ 179 ∷  41 ∷ 227 ∷  47 ∷ 132 ∷
   83 ∷ 209 ∷   0 ∷ 237 ∷  32 ∷ 252 ∷ 177 ∷  91 ∷ 106 ∷ 203 ∷ 190 ∷  57 ∷  74 ∷  76 ∷  88 ∷ 207 ∷
  208 ∷ 239 ∷ 170 ∷ 251 ∷  67 ∷  77 ∷  51 ∷ 133 ∷  69 ∷ 249 ∷   2 ∷ 127 ∷  80 ∷  60 ∷ 159 ∷ 168 ∷
   81 ∷ 163 ∷  64 ∷ 143 ∷ 146 ∷ 157 ∷  56 ∷ 245 ∷ 188 ∷ 182 ∷ 218 ∷  33 ∷  16 ∷ 255 ∷ 243 ∷ 210 ∷
  205 ∷  12 ∷  19 ∷ 236 ∷  95 ∷ 151 ∷  68 ∷  23 ∷ 196 ∷ 167 ∷ 126 ∷  61 ∷ 100 ∷  93 ∷  25 ∷ 115 ∷
   96 ∷ 129 ∷  79 ∷ 220 ∷  34 ∷  42 ∷ 144 ∷ 136 ∷  70 ∷ 238 ∷ 184 ∷  20 ∷ 222 ∷  94 ∷  11 ∷ 219 ∷
  224 ∷  50 ∷  58 ∷  10 ∷  73 ∷   6 ∷  36 ∷  92 ∷ 194 ∷ 211 ∷ 172 ∷  98 ∷ 145 ∷ 149 ∷ 228 ∷ 121 ∷
  231 ∷ 200 ∷  55 ∷ 109 ∷ 141 ∷ 213 ∷  78 ∷ 169 ∷ 108 ∷  86 ∷ 244 ∷ 234 ∷ 101 ∷ 122 ∷ 174 ∷   8 ∷
  186 ∷ 120 ∷  37 ∷  46 ∷  28 ∷ 166 ∷ 180 ∷ 198 ∷ 232 ∷ 221 ∷ 116 ∷  31 ∷  75 ∷ 189 ∷ 139 ∷ 138 ∷
  112 ∷  62 ∷ 181 ∷ 102 ∷  72 ∷   3 ∷ 246 ∷  14 ∷  97 ∷  53 ∷  87 ∷ 185 ∷ 134 ∷ 193 ∷  29 ∷ 158 ∷
  225 ∷ 248 ∷ 152 ∷  17 ∷ 105 ∷ 217 ∷ 142 ∷ 148 ∷ 155 ∷  30 ∷ 135 ∷ 233 ∷ 206 ∷  85 ∷  40 ∷ 223 ∷
  140 ∷ 161 ∷ 137 ∷  13 ∷ 191 ∷ 230 ∷  66 ∷ 104 ∷  65 ∷ 153 ∷  45 ∷  15 ∷ 176 ∷  84 ∷ 187 ∷  22 ∷ []

-- point sanity (cheap): S(00)=0x63=99, S(01)=0x7c=124, S(10)=0xca=202.
b00 : Poly 8
b00 = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []
b01 : Poly 8
b01 = F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []
b10 : Poly 8
b10 = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []
chk00 : byte-val (sbox-gf b00) ≡ 99
chk00 = refl
chk01 : byte-val (sbox-gf b01) ≡ 124
chk01 = refl
chk10 : byte-val (sbox-gf b10) ≡ 202
chk10 = refl

-- THE CERTIFICATION: the verified GF-inversion S-box IS the canonical AES S-box
-- (256-byte refl). This is the inherently-computational ~56s reflection.
sbox-table-check : all-vec (λ a → byte-val (sbox-gf a) ==ℕ idx SBOX (byte-val a)) ≡ true
sbox-table-check = refl
sbox-is-aes : (a : Poly 8) → byte-val (sbox-gf a) ≡ idx SBOX (byte-val a)
sbox-is-aes a = ==ℕ-sound _ _
  (all-vec-sound (λ x → byte-val (sbox-gf x) ==ℕ idx SBOX (byte-val x)) sbox-table-check a)

------------------------------------------------------------------------
-- B-deep: the canonical, evaluation-CHEAP S-box = the proven table lookup.
------------------------------------------------------------------------

-- F₂ / byte Bool-equality, with soundness (the reflection→≡ bridge for bytes).
_==F_ : F2.F₂ → F2.F₂ → Bool
F2.𝟘 ==F F2.𝟘 = true
F2.𝟙 ==F F2.𝟙 = true
_    ==F _    = false
==F-sound : (x y : F2.F₂) → (x ==F y) ≡ true → x ≡ y
==F-sound F2.𝟘 F2.𝟘 _ = refl
==F-sound F2.𝟙 F2.𝟙 _ = refl
_==V_ : {n : ℕ} → Vec F2.F₂ n → Vec F2.F₂ n → Bool
[]       ==V []       = true
(x ∷ xs) ==V (y ∷ ys) = (x ==F y) ∧ (xs ==V ys)
==V-sound : {n : ℕ} (u v : Vec F2.F₂ n) → (u ==V v) ≡ true → u ≡ v
==V-sound []       []       _ = refl
==V-sound (x ∷ xs) (y ∷ ys) h =
  cong₂ _∷_ (==F-sound x y (∧-elimˡ h)) (==V-sound xs ys (∧-elimʳ h))

-- ℕ → byte (LSB-first, 8-bit decoder).
odd : ℕ → F2.F₂
odd zero          = F2.𝟘
odd (suc zero)    = F2.𝟙
odd (suc (suc n)) = odd n
half : ℕ → ℕ
half zero          = 0
half (suc zero)    = 0
half (suc (suc n)) = suc (half n)
nb : ℕ → Poly 8
nb n =  odd n                                            ∷ odd (half n)
     ∷ odd (half (half n))                               ∷ odd (half (half (half n)))
     ∷ odd (half (half (half (half n))))                 ∷ odd (half (half (half (half (half n)))))
     ∷ odd (half (half (half (half (half (half n))))))   ∷ odd (half (half (half (half (half (half (half n))))))) ∷ []

-- 8-bit round-trip nb ∘ byte-val ≡ id — a CHEAP reflection (no GF inversion).
byte-roundtrip-check : all-vec (λ b → nb (byte-val b) ==V b) ≡ true
byte-roundtrip-check = refl
byte-roundtrip : (b : Poly 8) → nb (byte-val b) ≡ b
byte-roundtrip b = ==V-sound (nb (byte-val b)) b
  (all-vec-sound (λ x → nb (byte-val x) ==V x) byte-roundtrip-check b)

-- THE CANONICAL S-BOX: the table lookup (cheap to force).
sbox : Poly 8 → Poly 8
sbox b = nb (idx SBOX (byte-val b))

-- GF-inversion retained as a THEOREM: the table sbox EQUALS affine ∘ pinv.
sbox≡gf : (b : Poly 8) → sbox b ≡ sbox-gf b
sbox≡gf b = trans (cong nb (sym (sbox-is-aes b))) (byte-roundtrip (sbox-gf b))

-- the round-trip, re-derived for the table sbox via the equivalence + the
-- computed round-trip (cheap; no forcing of the GF inverse).
sbox-rt : (b : Poly 8) → inv-sbox (sbox b) ≡ b
sbox-rt b = trans (cong inv-sbox (sbox≡gf b)) (sbox-gf-rt b)
