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
-- there is no algebraic shortcut (cf. AI-10 pinv-inv, which had one).  This
-- module is a standalone CERTIFICATION; the cipher (F2/AES/) does not import
-- it, so the cipher build stays fast.  --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Bool using (Bool; true; false)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBox using (sbox)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo; all-vec; all-vec-sound)
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
chk00 : byte-val (sbox b00) ≡ 99
chk00 = refl
chk01 : byte-val (sbox b01) ≡ 124
chk01 = refl
chk10 : byte-val (sbox b10) ≡ 202
chk10 = refl

-- THE CERTIFICATION: the verified S-box IS the canonical AES S-box (256-byte refl).
sbox-table-check : all-vec (λ a → byte-val (sbox a) ==ℕ idx SBOX (byte-val a)) ≡ true
sbox-table-check = refl
sbox-is-aes : (a : Poly 8) → byte-val (sbox a) ≡ idx SBOX (byte-val a)
sbox-is-aes a = ==ℕ-sound _ _
  (all-vec-sound (λ x → byte-val (sbox x) ==ℕ idx SBOX (byte-val x)) sbox-table-check a)
