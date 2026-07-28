{-# OPTIONS --safe --without-K #-}
-- ⟡cap-128-forcing / bind-at-the-owner: `gmul-dot4` is the ONLY definition in
-- MixColumns.Base that needs GF256.MulLaws, and MulLaws is the tier-wide floor
-- (99MB alone, vs 62-73 for every other import — measured). Splitting it out lets
-- every consumer that needs only `dot4`/`dot4-cyc`/`dot4-cong` bind the LIGHT Base
-- and escape that floor entirely.
module Substrate.Algebra.F2.MixColumns.Base.GmulDot4 where
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.GF256.MulLaws
open import Substrate.Algebra.F2.GF256.Mul
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Eq

gmul-dot4 : (k c0 c1 c2 c3 a0 a1 a2 a3 : Vector 8) → gmul k (dot4 c0 c1 c2 c3 a0 a1 a2 a3)
          ≡ dot4 (gmul k c0) (gmul k c1) (gmul k c2) (gmul k c3) a0 a1 a2 a3
gmul-dot4 k c0 c1 c2 c3 a0 a1 a2 a3 =
  trans (gmul-distribˡ k (gmul c0 a0 +ⱽ gmul c1 a1) (gmul c2 a2 +ⱽ gmul c3 a3))
        (cong₂ _+ⱽ_ (trans (gmul-distribˡ k (gmul c0 a0) (gmul c1 a1))
                 (cong₂ _+ⱽ_ (sym (gmul-assoc k c0 a0)) (sym (gmul-assoc k c1 a1))))
          (trans (gmul-distribˡ k (gmul c2 a2) (gmul c3 a3))
                 (cong₂ _+ⱽ_ (sym (gmul-assoc k c2 a2)) (sym (gmul-assoc k c3 a3)))))
