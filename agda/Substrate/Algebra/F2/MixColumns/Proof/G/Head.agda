{-# OPTIONS --safe --without-K #-}
-- ⟡cap-128-forcing: the COORDINATE-0 round-trip, the one place the 8 GF products and
-- the 4 collapse representatives are used. It is the heavy half of the abstract
-- round-trip (it applies `air`), so it is split from `round-trip` — which is the
-- purely equivariant half — to keep both units under the 128MiB cap.
--
-- Like `air` and the equivariance chain it is a PLAIN TOP-LEVEL operator over its
-- hypotheses, not a parameterized module: a module application COPIES, so a
-- `module G-Head (…)` would re-elaborate this term inside `.Proof.G` as well.
module Substrate.Algebra.F2.MixColumns.Proof.G.Head where
open import Substrate.Algebra.F2.GF256.Mul
open import Substrate.Algebra.F2.MixColumns.Base
open import Substrate.Algebra.F2.MixColumns.Proof.G.Air
open import Substrate.Algebra.F2.MixColumns.Proof.G.Equiv

rt-head : (x01 x02 x03 x09 x0b x0d x0e : Vector 8)
        → (v1c v12 v16 v1d v1a v17 v1b : Vector 8)
        → gmul x0e x02 ≡ v1c → gmul x0e x03 ≡ v12
        → gmul x0b x02 ≡ v16 → gmul x0b x03 ≡ v1d
        → gmul x0d x02 ≡ v1a → gmul x0d x03 ≡ v17
        → gmul x09 x02 ≡ v12 → gmul x09 x03 ≡ v1b
        → ((a : Vector 8) → gmul x01 a ≡ a)
        → ((b : Vector 8) → gmul b x01 ≡ b)
        → ((a : Vector 8) → gmul 𝟎ⱽ a ≡ 𝟎ⱽ)
        -- the 4 collapse REPRESENTATIVES — one per circulant offset class
        -- (row 0 of M⁻¹M = e₀); offsets 0,1,2,3 = h00,h01,h02,h03:
        → (v1c +ⱽ x0b) +ⱽ (x0d +ⱽ v1b) ≡ x01 → (v12 +ⱽ v16) +ⱽ (x0d +ⱽ x09) ≡ 𝟎ⱽ
        → (x0e +ⱽ v1d) +ⱽ (v1a +ⱽ x09) ≡ 𝟎ⱽ → (x0e +ⱽ x0b) +ⱽ (v17 +ⱽ v12) ≡ 𝟎ⱽ
        → (col : Vec (Vector 8) 4)
        → hd (invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col)) ≡ hd col
rt-head x01 x02 x03 x09 x0b x0d x0e _ _ _ _ _ _ _
        qe2 qe3 qb2 qb3 qd2 qd3 q92 q93 idˡ idʳ zˡ h00 h01 h02 h03
        (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  trans (air x01 x02 x03 x0e x0b x0d x09 a0 a1 a2 a3) (trans (dot4-cong a0 a1 a2 a3
      (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe2 (idʳ x0b)) (cong₂ _+ⱽ_ (idʳ x0d) q93)) h00)
      (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ qe3 qb2) (cong₂ _+ⱽ_ (idʳ x0d) (idʳ x09))) h01)
      (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) qb3) (cong₂ _+ⱽ_ qd2 (idʳ x09))) h02)
      (trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idʳ x0e) (idʳ x0b)) (cong₂ _+ⱽ_ qd3 q92)) h03))
    (i0 x01 idˡ zˡ a0 a1 a2 a3))
