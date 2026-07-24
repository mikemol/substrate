{-# OPTIONS --safe --without-K #-}
-- Pre-whiten (FIPS "round 0" AddRoundKey): X0 = AddRoundKey(pt, rk0) ≡ S0.
module Substrate.Algebra.F2.AES.KAT.Pre where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (State; addKey)
open import Substrate.Algebra.F2.AES.KAT.Trace
X0 : State
X0 = addKey K0 Spt
pre : X0 ≡ S0
pre = refl
