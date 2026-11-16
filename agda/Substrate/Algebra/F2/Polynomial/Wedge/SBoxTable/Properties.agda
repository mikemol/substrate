{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties  (PROOF half)
--
-- The FIPS certification that the evaluation-cheap table `SBoxTable.sbox` IS
-- the verified GF(2⁸)-inversion S-box `affine ∘ pinv` (`sbox-gf`, AI-10, built
-- on the verified inverse AI-8):
--   sbox-is-aes : (a) → byte-val (sbox-gf a) ≡ SBOX[byte-val a]   (256-byte GF reflection, ~56s)
--   sbox≡gf     : (b) → sbox b ≡ sbox-gf b                        (the table IS the algebraic S-box)
--   sbox-rt     : (b) → inv-sbox (sbox b) ≡ b                     (decrypt round-trip)
-- Importing THIS module deserializes the GF inverse (Wedge.SBox → Wedge.Inverse,
-- ~89 MB); the forward path (SBoxTable) does not. The algebra is preserved here,
-- once, and re-exported alongside the lean table. --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Bool.Bool
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
-- ⚑ NOTE the NEXT statement carries `using` + `renaming` + `public` — a banned
-- re-export, one of the 48 in `--reexports`.  Different class, left for Ⓑ1;
-- this transform touches only the retired-barrel alias.
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Wedge.SBox
  using (inv-sbox) renaming (sbox to sbox-gf; sbox-rt to sbox-gf-rt) public
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVec
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.AllVecSound
import Substrate.Algebra.Polynomial.Graded.Base as GB
open GB.Over 𝟘 using (Poly)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
-- point sanity (cheap): S(00)=0x63=99, S(01)=0x7c=124, S(10)=0xca=202.
b00 : Poly 8
b00 = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b01 : Poly 8
b01 = F2.𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
b10 : Poly 8
b10 = 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ F2.𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
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

-- GF-inversion retained as a THEOREM: the table sbox EQUALS affine ∘ pinv.
sbox≡gf : (b : Poly 8) → sbox b ≡ sbox-gf b
sbox≡gf b = trans (cong nb (sym (sbox-is-aes b))) (byte-roundtrip (sbox-gf b))

-- the round-trip, re-derived for the table sbox via the equivalence +F the
-- computed round-trip (cheap; no forcing of the GF inverse in the FORWARD path).
sbox-rt : (b : Poly 8) → inv-sbox (sbox b) ≡ b
sbox-rt b = trans (cong inv-sbox (sbox≡gf b)) (sbox-gf-rt b)
