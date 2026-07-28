{-# OPTIONS --safe --without-K #-}
-- AI-9 MixColumns round-trip, CIRCULANT-FACTORED. M⁻¹ and M are both circulant, so
-- mix and inv are C4-equivariant: they commute with the cyclic rotation `rot` of a column.
-- The round-trip is therefore proven ONCE at coordinate 0 (`rt-head`, the only place the
-- 8 GF products + 4 collapse representatives are used) and the other three coordinates are
-- `rt-head` transported by `rot` — so rt1/rt2/rt3 and 12 of the 16 collapses EVAPORATE.
--
-- The whole proof is ABSTRACT over the constants (every gmul symbolic ⇒ no const×const
-- normalization), instantiated cheaply below. The 8 GF products are now `xtime`+XOR of
-- constants (Mul02/Mul03 via Scale) — NO const×const normalization remains anywhere.
module Substrate.Algebra.F2.MixColumns.Proof where
open import Substrate.Algebra.F2.GF256.MulLaws
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Mul02  -- pe2 pb2 pd2 p92 (= xtime of inv-coeffs)
open import Substrate.Algebra.F2.MixColumns.Mul03  -- pe3 pb3 pd3 p93 (= xtime ⊕ id)
open import Substrate.Algebra.F2.MixColumns.Collapse

open import Substrate.Algebra.F2.MixColumns.Proof.G
open import Substrate.Algebra.F2.MixColumns.Proof.G.Equiv
open G c01 c02 c03 c09 c0b c0d c0e b1c b12 b16 b1d b1a b17 b1b pe2 pe3 pb2 pb3 pd2 pd3 p92 p93 gmul-identityˡ gmul-identityʳ gmul-zeroˡ k00 k01 k02 k03


-- the concrete MixColumns / InvMixColumns: the generic operators of .Proof.G.Equiv
-- APPLIED to the AES constants. Named here (rather than re-exported) so the whole
-- downstream — Fast.Properties, AES.Round, AES.Round.RoundTrip — keeps addressing
-- `mix`/`inv` exactly as before.
mix : Vec (Vector 8) 4 → Vec (Vector 8) 4
mix = mixᴳ c01 c02 c03
inv : Vec (Vector 8) 4 → Vec (Vector 8) 4
inv = invᴳ c09 c0b c0d c0e

-- the concrete MixColumns round-trip (InvMixColumns ∘ MixColumns ≡ id per column).
mixcolumns-round-trip : (col : Vec (Vector 8) 4) → inv (mix col) ≡ col
mixcolumns-round-trip = round-trip

