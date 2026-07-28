{-# OPTIONS --safe --without-K #-}
-- ⟡cap-128-forcing: `air` is the single heaviest definition of the abstract
-- MixColumns round-trip (116MB of the parent module's 190MB, measured). It is
-- split out here — and stated as a PLAIN TOP-LEVEL operator over its constants,
-- NOT a parameterized module: a module application COPIES, so a `module G-Air (x01
-- x02 x03)` would re-elaborate this whole term inside every consumer. Taking the
-- constants as ordinary arguments makes each use a REFERENCE instead.
module Substrate.Algebra.F2.MixColumns.Proof.G.Air where
open import Substrate.Algebra.F2.GF256.Mul
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Base.GmulDot4
open import Substrate.Algebra.F2.MixColumns.Mul02  -- pe2 pb2 pd2 p92 (= xtime of inv-coeffs)
open import Substrate.Algebra.F2.MixColumns.Mul03  -- pe3 pb3 pd3 p93 (= xtime ⊕ id)
open import Substrate.Algebra.F2.MixColumns.Collapse

air : (x01 x02 x03 e0 e1 e2 e3 a0 a1 a2 a3 : Vector 8)
  → dot4 e0 e1 e2 e3 (dot4 x02 x03 x01 x01 a0 a1 a2 a3) (dot4 x01 x02 x03 x01 a0 a1 a2 a3)
      (dot4 x01 x01 x02 x03 a0 a1 a2 a3) (dot4 x03 x01 x01 x02 a0 a1 a2 a3)
  ≡ dot4 ((gmul e0 x02 +ⱽ gmul e1 x01) +ⱽ (gmul e2 x01 +ⱽ gmul e3 x03))
         ((gmul e0 x03 +ⱽ gmul e1 x02) +ⱽ (gmul e2 x01 +ⱽ gmul e3 x01))
         ((gmul e0 x01 +ⱽ gmul e1 x03) +ⱽ (gmul e2 x02 +ⱽ gmul e3 x01))
         ((gmul e0 x01 +ⱽ gmul e1 x01) +ⱽ (gmul e2 x03 +ⱽ gmul e3 x02)) a0 a1 a2 a3
air x01 x02 x03 e0 e1 e2 e3 a0 a1 a2 a3 =
  trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (gmul-dot4 e0 x02 x03 x01 x01 a0 a1 a2 a3) (gmul-dot4 e1 x01 x02 x03 x01 a0 a1 a2 a3))
          (cong₂ _+ⱽ_ (gmul-dot4 e2 x01 x01 x02 x03 a0 a1 a2 a3) (gmul-dot4 e3 x03 x01 x01 x02 a0 a1 a2 a3)))
  (trans (cong₂ _+ⱽ_ (dot4-add (gmul e0 x02) (gmul e0 x03) (gmul e0 x01) (gmul e0 x01)
                    (gmul e1 x01) (gmul e1 x02) (gmul e1 x03) (gmul e1 x01) a0 a1 a2 a3)
          (dot4-add (gmul e2 x01) (gmul e2 x01) (gmul e2 x02) (gmul e2 x03)
                    (gmul e3 x03) (gmul e3 x01) (gmul e3 x01) (gmul e3 x02) a0 a1 a2 a3))
         (dot4-add (gmul e0 x02 +ⱽ gmul e1 x01) (gmul e0 x03 +ⱽ gmul e1 x02)
                   (gmul e0 x01 +ⱽ gmul e1 x03) (gmul e0 x01 +ⱽ gmul e1 x01)
                   (gmul e2 x01 +ⱽ gmul e3 x03) (gmul e2 x01 +ⱽ gmul e3 x01)
                   (gmul e2 x02 +ⱽ gmul e3 x01) (gmul e2 x03 +ⱽ gmul e3 x02) a0 a1 a2 a3))
  -- coordinate-0 identity: dot4 x01 𝟎 𝟎 𝟎 picks out a0.
