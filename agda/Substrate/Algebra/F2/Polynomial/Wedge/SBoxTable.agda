{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable  (lean / DEF half)
--
-- The evaluation-CHEAP, table-driven S-box `sbox = nb ∘ idx SBOX ∘ byte-val`
-- (a lookup) plus the cheap decoder machinery (`nb`, `byte-val`, `SBOX`, the
-- 8-bit round-trip `byte-roundtrip`). GF-FREE by construction — this module
-- does NOT import `Wedge.SBox` / `Wedge.Inverse` (the EEA GF-inversion), so a
-- consumer that FORCES the table (the AES key schedule / cipher / KAT) never
-- deserializes the ~89 MB GF-inverse closure.
--
-- The FIPS certification that this table IS the verified `affine ∘ pinv` S-box
-- (`sbox-is-aes`, the 256-byte GF reflection) and the decrypt round-trip
-- (`sbox-rt`, via `inv-sbox`) live in `SBoxTable.Properties` — the algebra is
-- preserved, just routed so the forward path (this module) is Inverse-free.
-- --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base
  using (m-lo; all-vec; all-vec-sound; ∧-elimˡ; ∧-elimʳ)
import Substrate.Algebra.Polynomial.Graded.Base as GB
open GB.Over F2.𝟘 using (Poly)

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

------------------------------------------------------------------------
-- The canonical, evaluation-CHEAP S-box = the proven table lookup.
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

-- THE CANONICAL S-BOX: the table lookup (cheap to force; GF-free).
sbox : Poly 8 → Poly 8
sbox b = nb (idx SBOX (byte-val b))
