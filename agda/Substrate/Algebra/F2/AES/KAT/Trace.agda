{-# OPTIONS --safe #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT.Trace
--
-- The concrete oracle TRACE of the FIPS-197 Appendix C.1 encryption, as literals.
-- Naming each intermediate state `Sᵢ` AND each round key `Mᵢ`/`K0`/`K10` as a
-- concrete literal is what makes the full-encrypt KAT feasible: it breaks BOTH deep
-- chains (the 10-round composition AND the key-schedule word-recursion) that blow up
-- when forced monolithically. Each per-round step (KAT.RoundN) and per-key step
-- (KAT.Keys) then evaluates exactly ONE operation from a concrete input — constant
-- cost, no exponential. (Forcing the real schedule deep is exponential: ~×5 per
-- round key — 9 s, 46 s, 241 s for kb1, kb2, kb3 — because `nextRoundKey`'s word
-- recursion has no term sharing; concrete intermediates dissolve it.)
--
-- Sᵢ = state after i round applications; rkᵢ = the i-th round key (kb0 = master key).
-- M0..M8 = the 9 middle round keys kb1..kb9; K0 = kb0; K10 = kb10.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT.Trace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State)
open import Substrate.Algebra.F2.AES.KAT using (to-state; pt-C1; ct-C1)

-- the round keys (oracle-derived; the real schedule is pinned to these in KAT.Keys).
kb0 kb1 kb2 kb3 kb4 kb5 kb6 kb7 kb8 kb9 kb10 : Vec ℕ 16
kb0  = 0 ∷ 1 ∷ 2 ∷ 3 ∷ 4 ∷ 5 ∷ 6 ∷ 7 ∷ 8 ∷ 9 ∷ 10 ∷ 11 ∷ 12 ∷ 13 ∷ 14 ∷ 15 ∷ []
kb1  = 214 ∷ 170 ∷ 116 ∷ 253 ∷ 210 ∷ 175 ∷ 114 ∷ 250 ∷ 218 ∷ 166 ∷ 120 ∷ 241 ∷ 214 ∷ 171 ∷ 118 ∷ 254 ∷ []
kb2  = 182 ∷ 146 ∷ 207 ∷ 11 ∷ 100 ∷ 61 ∷ 189 ∷ 241 ∷ 190 ∷ 155 ∷ 197 ∷ 0 ∷ 104 ∷ 48 ∷ 179 ∷ 254 ∷ []
kb3  = 182 ∷ 255 ∷ 116 ∷ 78 ∷ 210 ∷ 194 ∷ 201 ∷ 191 ∷ 108 ∷ 89 ∷ 12 ∷ 191 ∷ 4 ∷ 105 ∷ 191 ∷ 65 ∷ []
kb4  = 71 ∷ 247 ∷ 247 ∷ 188 ∷ 149 ∷ 53 ∷ 62 ∷ 3 ∷ 249 ∷ 108 ∷ 50 ∷ 188 ∷ 253 ∷ 5 ∷ 141 ∷ 253 ∷ []
kb5  = 60 ∷ 170 ∷ 163 ∷ 232 ∷ 169 ∷ 159 ∷ 157 ∷ 235 ∷ 80 ∷ 243 ∷ 175 ∷ 87 ∷ 173 ∷ 246 ∷ 34 ∷ 170 ∷ []
kb6  = 94 ∷ 57 ∷ 15 ∷ 125 ∷ 247 ∷ 166 ∷ 146 ∷ 150 ∷ 167 ∷ 85 ∷ 61 ∷ 193 ∷ 10 ∷ 163 ∷ 31 ∷ 107 ∷ []
kb7  = 20 ∷ 249 ∷ 112 ∷ 26 ∷ 227 ∷ 95 ∷ 226 ∷ 140 ∷ 68 ∷ 10 ∷ 223 ∷ 77 ∷ 78 ∷ 169 ∷ 192 ∷ 38 ∷ []
kb8  = 71 ∷ 67 ∷ 135 ∷ 53 ∷ 164 ∷ 28 ∷ 101 ∷ 185 ∷ 224 ∷ 22 ∷ 186 ∷ 244 ∷ 174 ∷ 191 ∷ 122 ∷ 210 ∷ []
kb9  = 84 ∷ 153 ∷ 50 ∷ 209 ∷ 240 ∷ 133 ∷ 87 ∷ 104 ∷ 16 ∷ 147 ∷ 237 ∷ 156 ∷ 190 ∷ 44 ∷ 151 ∷ 78 ∷ []
kb10 = 19 ∷ 17 ∷ 29 ∷ 127 ∷ 227 ∷ 148 ∷ 74 ∷ 23 ∷ 243 ∷ 7 ∷ 167 ∷ 139 ∷ 77 ∷ 43 ∷ 48 ∷ 197 ∷ []

-- the round keys as States (concrete — so the rounds never force the schedule).
K0 K10 M0 M1 M2 M3 M4 M5 M6 M7 M8 : State
K0 = to-state kb0
M0 = to-state kb1
M1 = to-state kb2
M2 = to-state kb3
M3 = to-state kb4
M4 = to-state kb5
M5 = to-state kb6
M6 = to-state kb7
M7 = to-state kb8
M8 = to-state kb9
K10 = to-state kb10

Spt Sct : State
Spt = to-state pt-C1
Sct = to-state ct-C1

-- the intermediate states after each round (oracle; re-pinned in KAT.RoundN).
s0 s1 s2 s3 s4 s5 s6 s7 s8 s9 : Vec ℕ 16
s0 = 0 ∷ 16 ∷ 32 ∷ 48 ∷ 64 ∷ 80 ∷ 96 ∷ 112 ∷ 128 ∷ 144 ∷ 160 ∷ 176 ∷ 192 ∷ 208 ∷ 224 ∷ 240 ∷ []
s1 = 137 ∷ 216 ∷ 16 ∷ 232 ∷ 133 ∷ 90 ∷ 206 ∷ 104 ∷ 45 ∷ 24 ∷ 67 ∷ 216 ∷ 203 ∷ 18 ∷ 143 ∷ 228 ∷ []
s2 = 73 ∷ 21 ∷ 89 ∷ 143 ∷ 85 ∷ 229 ∷ 215 ∷ 160 ∷ 218 ∷ 202 ∷ 148 ∷ 250 ∷ 31 ∷ 10 ∷ 99 ∷ 247 ∷ []
s3 = 250 ∷ 99 ∷ 106 ∷ 40 ∷ 37 ∷ 179 ∷ 57 ∷ 201 ∷ 64 ∷ 102 ∷ 138 ∷ 49 ∷ 87 ∷ 36 ∷ 77 ∷ 23 ∷ []
s4 = 36 ∷ 114 ∷ 64 ∷ 35 ∷ 105 ∷ 102 ∷ 179 ∷ 250 ∷ 110 ∷ 210 ∷ 117 ∷ 50 ∷ 136 ∷ 66 ∷ 91 ∷ 108 ∷ []
s5 = 200 ∷ 22 ∷ 119 ∷ 188 ∷ 155 ∷ 122 ∷ 201 ∷ 59 ∷ 37 ∷ 2 ∷ 121 ∷ 146 ∷ 176 ∷ 38 ∷ 25 ∷ 150 ∷ []
s6 = 198 ∷ 47 ∷ 225 ∷ 9 ∷ 247 ∷ 94 ∷ 237 ∷ 195 ∷ 204 ∷ 121 ∷ 57 ∷ 93 ∷ 132 ∷ 249 ∷ 207 ∷ 93 ∷ []
s7 = 209 ∷ 135 ∷ 108 ∷ 15 ∷ 121 ∷ 196 ∷ 48 ∷ 10 ∷ 180 ∷ 85 ∷ 148 ∷ 173 ∷ 214 ∷ 111 ∷ 244 ∷ 31 ∷ []
s8 = 253 ∷ 227 ∷ 186 ∷ 210 ∷ 5 ∷ 229 ∷ 208 ∷ 215 ∷ 53 ∷ 71 ∷ 150 ∷ 78 ∷ 241 ∷ 254 ∷ 55 ∷ 241 ∷ []
s9 = 189 ∷ 110 ∷ 124 ∷ 61 ∷ 242 ∷ 181 ∷ 119 ∷ 158 ∷ 11 ∷ 97 ∷ 33 ∷ 110 ∷ 139 ∷ 16 ∷ 182 ∷ 137 ∷ []

S0 S1 S2 S3 S4 S5 S6 S7 S8 S9 : State
S0 = to-state s0
S1 = to-state s1
S2 = to-state s2
S3 = to-state s3
S4 = to-state s4
S5 = to-state s5
S6 = to-state s6
S7 = to-state s7
S8 = to-state s8
S9 = to-state s9
