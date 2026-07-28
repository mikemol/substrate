{-# OPTIONS --safe --without-K #-}
-- ⟡cap-128-forcing: the C₄-EQUIVARIANCE half of the abstract MixColumns round-trip.
--
-- Everything here is a PLAIN TOP-LEVEL operator over its constants, NOT a
-- parameterized module: a module application COPIES, so `module G-Equiv (x01 …)`
-- would re-elaborate this whole chain inside every consumer (measured: it put 160MB
-- into the round-trip unit, over the 128MiB cap). Taking the constants as ordinary
-- arguments makes each use a REFERENCE, so the elaboration is paid exactly once.
--
-- It also needs only the LIGHT `MixColumns.Base` — never `gmul-dot4`, never `air` —
-- so nothing here pays the `GF256.MulLaws` closure that `G.Air` must.
module Substrate.Algebra.F2.MixColumns.Proof.G.Equiv where
open import Substrate.Algebra.F2.GF256.Mul
open import Substrate.Algebra.F2.MixColumns.Base

i0 : (x01 : Vector 8)
   → ((a : Vector 8) → gmul x01 a ≡ a) → ((a : Vector 8) → gmul 𝟎ⱽ a ≡ 𝟎ⱽ)
   → (a0 a1 a2 a3 : Vector 8) → dot4 x01 𝟎ⱽ 𝟎ⱽ 𝟎ⱽ a0 a1 a2 a3 ≡ a0
i0 x01 idˡ zˡ a0 a1 a2 a3 =
  trans (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (idˡ a0) (zˡ a1)) (cong₂ _+ⱽ_ (zˡ a2) (zˡ a3)))
        (trans (cong₂ _+ⱽ_ (+ⱽ-identityʳ a0) (+ⱽ-identityˡ 𝟎ⱽ)) (+ⱽ-identityʳ a0))

mixᴳ : (x01 x02 x03 : Vector 8) → Vec (Vector 8) 4 → Vec (Vector 8) 4
mixᴳ x01 x02 x03 (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  dot4 x02 x03 x01 x01 a0 a1 a2 a3 ∷ dot4 x01 x02 x03 x01 a0 a1 a2 a3 ∷
  dot4 x01 x01 x02 x03 a0 a1 a2 a3 ∷ dot4 x03 x01 x01 x02 a0 a1 a2 a3 ∷ []
invᴳ : (x09 x0b x0d x0e : Vector 8) → Vec (Vector 8) 4 → Vec (Vector 8) 4
invᴳ x09 x0b x0d x0e (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) =
  dot4 x0e x0b x0d x09 b0 b1 b2 b3 ∷ dot4 x09 x0e x0b x0d b0 b1 b2 b3 ∷
  dot4 x0d x09 x0e x0b b0 b1 b2 b3 ∷ dot4 x0b x0d x09 x0e b0 b1 b2 b3 ∷ []

-- cyclic rotation of a column (rotate right) and its head.
rot : Vec (Vector 8) 4 → Vec (Vector 8) 4
rot (a ∷ b ∷ c ∷ d ∷ []) = d ∷ a ∷ b ∷ c ∷ []
hd : Vec (Vector 8) 4 → Vector 8
hd (x ∷ _) = x

-- mixᴳ and invᴳ are CIRCULANT ⇒ C4-equivariant: each coordinate is one dot4-cyc.
mix-rot : (x01 x02 x03 : Vector 8) (col : Vec (Vector 8) 4)
        → mixᴳ x01 x02 x03 (rot col) ≡ rot (mixᴳ x01 x02 x03 col)
mix-rot x01 x02 x03 (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  cong₂ _∷_ (dot4-cyc x02 x03 x01 x01 a0 a1 a2 a3)
  (cong₂ _∷_ (dot4-cyc x01 x02 x03 x01 a0 a1 a2 a3)
  (cong₂ _∷_ (dot4-cyc x01 x01 x02 x03 a0 a1 a2 a3)
  (cong₂ _∷_ (dot4-cyc x03 x01 x01 x02 a0 a1 a2 a3) refl)))
inv-rot : (x09 x0b x0d x0e : Vector 8) (col : Vec (Vector 8) 4)
        → invᴳ x09 x0b x0d x0e (rot col) ≡ rot (invᴳ x09 x0b x0d x0e col)
inv-rot x09 x0b x0d x0e (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) =
  cong₂ _∷_ (dot4-cyc x0e x0b x0d x09 b0 b1 b2 b3)
  (cong₂ _∷_ (dot4-cyc x09 x0e x0b x0d b0 b1 b2 b3)
  (cong₂ _∷_ (dot4-cyc x0d x09 x0e x0b b0 b1 b2 b3)
  (cong₂ _∷_ (dot4-cyc x0b x0d x09 x0e b0 b1 b2 b3) refl)))

-- hence f = invᴳ ∘ mixᴳ is C4-equivariant; iterate for the 2nd/3rd rotation.
f-rot : (x01 x02 x03 x09 x0b x0d x0e : Vector 8) (col : Vec (Vector 8) 4)
      → invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 (rot col))
      ≡ rot (invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col))
f-rot x01 x02 x03 x09 x0b x0d x0e col =
  trans (cong (invᴳ x09 x0b x0d x0e) (mix-rot x01 x02 x03 col))
        (inv-rot x09 x0b x0d x0e (mixᴳ x01 x02 x03 col))
f-rot² : (x01 x02 x03 x09 x0b x0d x0e : Vector 8) (col : Vec (Vector 8) 4)
       → invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 (rot (rot col)))
       ≡ rot (rot (invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col)))
f-rot² x01 x02 x03 x09 x0b x0d x0e col =
  trans (f-rot x01 x02 x03 x09 x0b x0d x0e (rot col))
        (cong rot (f-rot x01 x02 x03 x09 x0b x0d x0e col))
f-rot³ : (x01 x02 x03 x09 x0b x0d x0e : Vector 8) (col : Vec (Vector 8) 4)
       → invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 (rot (rot (rot col))))
       ≡ rot (rot (rot (invᴳ x09 x0b x0d x0e (mixᴳ x01 x02 x03 col))))
f-rot³ x01 x02 x03 x09 x0b x0d x0e col =
  trans (f-rot x01 x02 x03 x09 x0b x0d x0e (rot (rot col)))
        (cong rot (f-rot² x01 x02 x03 x09 x0b x0d x0e col))
