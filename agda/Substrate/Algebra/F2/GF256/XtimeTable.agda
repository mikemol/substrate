{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.XtimeTable  (Ⓦᵤ-style proved table for `xtime`)
--
-- The `bd17a98` move (SBoxTable) applied ONE LAYER DOWN, to the MixColumns
-- diffusion kernel `xtime` (= ·x mod m in GF(2⁸)). CERTIFIES that the verified
-- bit-vector `xtime` (GF256.Xtime) computes EXACTLY the canonical table, for all
-- 256 bytes:
--   xtime-is-aes : (b) → byte-val (xtime b) ≡ XTIME[byte-val b].
-- Then exposes the evaluation-CHEAP, table-driven `xtime-tab = nb ∘ idx XTIME ∘
-- byte-val`, with the bit-vector construction retained as the proven THEOREM
-- `xtime-tab≡xtime` (the `sbox≡gf` analog) — so MixColumns can FORCE through a
-- table lookup (a bounded ℕ index) instead of a symbolic shift-and-conditional-
-- XOR that accumulates over ~250 GF products in a ten-round encrypt. The FIPS
-- rigor is preserved exactly as for the S-box: the table IS the verified `xtime`.
--
-- The 256-byte `refl` (`xtime-table-check`) is CHEAP (xtime is a shift + one
-- conditional XOR per byte — no GF inversion, unlike SBoxTable's ~56s reflection).
-- --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.GF256.XtimeTable where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; sym)
open import Substrate.Foundation.Bool using (Bool; true)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo; all-vec; all-vec-sound)
import Substrate.Algebra.Polynomial.Graded.Div as D
open D.Over F₂-CommRing 7 m-lo using (Poly)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable
  using (byte-val; idx; _==ℕ_; ==ℕ-sound; nb; byte-roundtrip)

-- the canonical ·x table: XTIME[b] = (b<<1 & 0xFF) ⊕ (0x1b if b≥0x80) (Rijndael ·02).
XTIME : Vec ℕ 256
XTIME =
    0 ∷   2 ∷   4 ∷   6 ∷   8 ∷  10 ∷  12 ∷  14 ∷  16 ∷  18 ∷  20 ∷  22 ∷  24 ∷  26 ∷  28 ∷  30 ∷
   32 ∷  34 ∷  36 ∷  38 ∷  40 ∷  42 ∷  44 ∷  46 ∷  48 ∷  50 ∷  52 ∷  54 ∷  56 ∷  58 ∷  60 ∷  62 ∷
   64 ∷  66 ∷  68 ∷  70 ∷  72 ∷  74 ∷  76 ∷  78 ∷  80 ∷  82 ∷  84 ∷  86 ∷  88 ∷  90 ∷  92 ∷  94 ∷
   96 ∷  98 ∷ 100 ∷ 102 ∷ 104 ∷ 106 ∷ 108 ∷ 110 ∷ 112 ∷ 114 ∷ 116 ∷ 118 ∷ 120 ∷ 122 ∷ 124 ∷ 126 ∷
  128 ∷ 130 ∷ 132 ∷ 134 ∷ 136 ∷ 138 ∷ 140 ∷ 142 ∷ 144 ∷ 146 ∷ 148 ∷ 150 ∷ 152 ∷ 154 ∷ 156 ∷ 158 ∷
  160 ∷ 162 ∷ 164 ∷ 166 ∷ 168 ∷ 170 ∷ 172 ∷ 174 ∷ 176 ∷ 178 ∷ 180 ∷ 182 ∷ 184 ∷ 186 ∷ 188 ∷ 190 ∷
  192 ∷ 194 ∷ 196 ∷ 198 ∷ 200 ∷ 202 ∷ 204 ∷ 206 ∷ 208 ∷ 210 ∷ 212 ∷ 214 ∷ 216 ∷ 218 ∷ 220 ∷ 222 ∷
  224 ∷ 226 ∷ 228 ∷ 230 ∷ 232 ∷ 234 ∷ 236 ∷ 238 ∷ 240 ∷ 242 ∷ 244 ∷ 246 ∷ 248 ∷ 250 ∷ 252 ∷ 254 ∷
   27 ∷  25 ∷  31 ∷  29 ∷  19 ∷  17 ∷  23 ∷  21 ∷  11 ∷   9 ∷  15 ∷  13 ∷   3 ∷   1 ∷   7 ∷   5 ∷
   59 ∷  57 ∷  63 ∷  61 ∷  51 ∷  49 ∷  55 ∷  53 ∷  43 ∷  41 ∷  47 ∷  45 ∷  35 ∷  33 ∷  39 ∷  37 ∷
   91 ∷  89 ∷  95 ∷  93 ∷  83 ∷  81 ∷  87 ∷  85 ∷  75 ∷  73 ∷  79 ∷  77 ∷  67 ∷  65 ∷  71 ∷  69 ∷
  123 ∷ 121 ∷ 127 ∷ 125 ∷ 115 ∷ 113 ∷ 119 ∷ 117 ∷ 107 ∷ 105 ∷ 111 ∷ 109 ∷  99 ∷  97 ∷ 103 ∷ 101 ∷
  155 ∷ 153 ∷ 159 ∷ 157 ∷ 147 ∷ 145 ∷ 151 ∷ 149 ∷ 139 ∷ 137 ∷ 143 ∷ 141 ∷ 131 ∷ 129 ∷ 135 ∷ 133 ∷
  187 ∷ 185 ∷ 191 ∷ 189 ∷ 179 ∷ 177 ∷ 183 ∷ 181 ∷ 171 ∷ 169 ∷ 175 ∷ 173 ∷ 163 ∷ 161 ∷ 167 ∷ 165 ∷
  219 ∷ 217 ∷ 223 ∷ 221 ∷ 211 ∷ 209 ∷ 215 ∷ 213 ∷ 203 ∷ 201 ∷ 207 ∷ 205 ∷ 195 ∷ 193 ∷ 199 ∷ 197 ∷
  251 ∷ 249 ∷ 255 ∷ 253 ∷ 243 ∷ 241 ∷ 247 ∷ 245 ∷ 235 ∷ 233 ∷ 239 ∷ 237 ∷ 227 ∷ 225 ∷ 231 ∷ 229 ∷ []

-- (a) THE CERTIFICATION: the verified bit-vector xtime IS the canonical ·x table (256-byte refl).
xtime-table-check : all-vec (λ b → byte-val (xtime b) ==ℕ idx XTIME (byte-val b)) ≡ true
xtime-table-check = refl

-- (b) the sbox-is-aes analog: by all-vec-sound + ==ℕ-sound.
xtime-is-aes : (b : Poly 8) → byte-val (xtime b) ≡ idx XTIME (byte-val b)
xtime-is-aes b = ==ℕ-sound _ _
  (all-vec-sound (λ x → byte-val (xtime x) ==ℕ idx XTIME (byte-val x)) xtime-table-check b)

-- the evaluation-CHEAP, table-driven xtime (a lookup), + the construction retained as theorem.
xtime-tab : Poly 8 → Poly 8
xtime-tab b = nb (idx XTIME (byte-val b))

xtime-tab≡xtime : (b : Poly 8) → xtime-tab b ≡ xtime b
xtime-tab≡xtime b = trans (cong nb (sym (xtime-is-aes b))) (byte-roundtrip (xtime b))
