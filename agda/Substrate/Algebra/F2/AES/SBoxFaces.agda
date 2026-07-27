------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.SBoxFaces
--
-- Ⓐ.sbox-faces — the AES S-box read as FACES of one structure (Cryptographic-
-- Total-Space discipline), with the EEA/CF-trace face made explicit: the
-- by-hand extended-Euclidean method from a crypto course, surfaced as a theorem.
-- Eliminates nothing; assembles the existing faces + names the trace.
--
--   FACE 1 — construction : `sbox = affine ∘ pinv` (Wedge.SBox)
--   FACE 2 — table        : `sbox-is-aes`, byte-val(sbox a) ≡ SBOX[byte-val a]
--                           (Wedge.SBoxTable — "the table IS the verified S-box")
--   FACE 3 — EEA/CF trace : `W a = fuel-bezout 10 (8,a) 7 m-lo` — the EXACT
--                           extended Euclidean run of byte `a` against the AES
--                           modulus m, the by-hand computation. The inverse is
--                           READ OFF its Bézout cofactor: `inv a = reduce-mod-f
--                           (cofactor (W a))`, certified `a · inv a ≡ 𝟙`.
--
-- THE BY-HAND RECIPE AS A THEOREM (`sbox-via-eea`): for a nonzero byte,
--   S(a) = affine( reduce( Bézout cofactor of EEA(a, m) ) )
-- — run the EEA, take the cofactor, reduce mod m, apply the affine map. This is
-- the "I'd have to run the extended Euclidean algorithm by hand" step (user),
-- now a face: the EEA/CF trace is where AES *divides*, and the only place it does
-- (ShiftRows is a permutation; its inverse is combinatorial). The trace is also a
-- FreeUP.extend (eea-fold-unique): the cofactor is the unique fold over the trace,
-- so this face is simultaneously the by-hand method AND by-construction.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.SBoxFaces where

open import Substrate.Foundation.Bool using (Bool; false)
open import Substrate.Foundation.Eq using (_≡_; cong)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo; is-zero8)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D
open F.Over F₂-CommRing using (Poly)
open M.Over F₂-CommRing 7 m-lo using (oneC)
open Q.Over F₂-CommRing 7 m-lo using (_*Q_)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBox using (sbox; affine; pinv-nonzero)
open import Substrate.Algebra.F2.Polynomial.Wedge.Inverse using (inv; inv-law; W)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties using (sbox-is-aes)

------------------------------------------------------------------------
-- The three faces, named in one place.
------------------------------------------------------------------------

-- FACE 1 — construction (GF(2⁸) inversion + affine).
face-construct = sbox

-- FACE 2 — table (the FIPS lookup, certified ≡ the construction).
face-table = sbox-is-aes

-- FACE 3 — the EEA / continued-fraction trace: the by-hand extended-Euclidean run.
sbox-eea-trace = W

------------------------------------------------------------------------
-- The EEA-Bézout cofactor IS the inverse — by construction (the Bézout
-- certificate), not by a 256-byte check.
------------------------------------------------------------------------

eea-certifies-inverse : (a : Poly 8) → is-zero8 a ≡ false → a *Q (inv a) ≡ oneC
eea-certifies-inverse = inv-law

------------------------------------------------------------------------
-- THE BY-HAND RECIPE, AS A THEOREM: for a nonzero byte, S(a) is the affine map
-- of the EEA-Bézout inverse (inv a = reduce the cofactor of W a). Run EEA, take
-- the cofactor, reduce, affine — exactly the crypto-course hand method.
------------------------------------------------------------------------

sbox-via-eea : (a : Poly 8) → is-zero8 a ≡ false → sbox a ≡ affine (inv a)
sbox-via-eea a z = cong affine (pinv-nonzero a z)
