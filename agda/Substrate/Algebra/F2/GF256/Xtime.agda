------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Xtime  (was GF256 §A1)
--
-- The only kernel of the Horner reduction: `xtime` (·x mod m), reusing the
-- Rijndael modulus as data (`m-lo`). Its two linearity laws (preserves `+ⱽ`,
-- preserves `*ₛ`) are the inductive step of `reduce-mod-m`'s linearity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Xtime where

open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
  renaming (+-comm to +F-comm)
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.Medial using (medial)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.R.Trace.V4FullCocycle

m-lo : Vector 8
m-lo = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

xtime : Vector 8 → Vector 8
xtime (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
  (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ []) +ⱽ (b7 *ₛ m-lo)

-- Ⓓ·: ·-distribʳ is Algebra.F2's ·-distribʳ-+ (reordered args); it was
-- re-derived here with the identical trans/·-comm/·-distribˡ-+ chain.
·-distribʳ : (x y z : F₂) → (x +F y) · z ≡ x · z +F y · z
·-distribʳ x y z = ·-distribʳ-+ z x y
-- Ⓜ: 4-term rearrange = the medial law (Algebra.Medial) at F₂'s `+`.
rearrange : (w x y z : F₂) → (w +F x) +F (y +F z) ≡ (w +F y) +F (x +F z)
rearrange = medial _+F_ +-assoc +F-comm

-- A1a: xtime preserves +ⱽ. Per-position: distribʳ (split (u7+v7)·b) +F 4-term rearrange.
xtime-+ⱽ : (u v : Vector 8) → xtime (u +ⱽ v) ≡ xtime u +ⱽ xtime v
xtime-+ⱽ (u0 ∷ u1 ∷ u2 ∷ u3 ∷ u4 ∷ u5 ∷ u6 ∷ u7 ∷ [])
         (v0 ∷ v1 ∷ v2 ∷ v3 ∷ v4 ∷ v5 ∷ v6 ∷ v7 ∷ []) =
  cong₂ _∷_ p0 (cong₂ _∷_ (q u0 v0 𝟙) (cong₂ _∷_ (q u1 v1 𝟘) (cong₂ _∷_ (q u2 v2 𝟙)
   (cong₂ _∷_ (q u3 v3 𝟙) (cong₂ _∷_ (q u4 v4 𝟘) (cong₂ _∷_ (q u5 v5 𝟘)
    (cong₂ _∷_ (q u6 v6 𝟘) refl)))))))
  where
    q : (a b c : F₂) → (a +F b) +F (u7 +F v7) · c ≡ (a +F u7 · c) +F (b +F v7 · c)
    q a b c = trans (cong ((a +F b) +F_) (·-distribʳ u7 v7 c)) (rearrange a b (u7 · c) (v7 · c))
    p0 : 𝟘 +F (u7 +F v7) · 𝟙 ≡ (𝟘 +F u7 · 𝟙) +F (𝟘 +F v7 · 𝟙)
    p0 = trans (+-identityˡ ((u7 +F v7) · 𝟙))
         (trans (·-distribʳ u7 v7 𝟙)
                (sym (cong₂ _+F_ (+-identityˡ (u7 · 𝟙)) (+-identityˡ (v7 · 𝟙)))))

-- A1b: xtime preserves *ₛ. Per-position: ·-assoc to move c out, then ·-distribˡ-+ back.
xtime-*ₛ : (c : F₂) (w : Vector 8) → xtime (c *ₛ w) ≡ c *ₛ xtime w
xtime-*ₛ c (w0 ∷ w1 ∷ w2 ∷ w3 ∷ w4 ∷ w5 ∷ w6 ∷ w7 ∷ []) =
  cong₂ _∷_ p0 (cong₂ _∷_ (q w0 𝟙) (cong₂ _∷_ (q w1 𝟘) (cong₂ _∷_ (q w2 𝟙)
   (cong₂ _∷_ (q w3 𝟙) (cong₂ _∷_ (q w4 𝟘) (cong₂ _∷_ (q w5 𝟘)
    (cong₂ _∷_ (q w6 𝟘) refl)))))))
  where
    q : (a b : F₂) → (c · a) +F (c · w7) · b ≡ c · (a +F w7 · b)
    q a b = trans (cong ((c · a) +F_) (·-assoc c w7 b)) (sym (·-distribˡ-+ c a (w7 · b)))
    p0 : 𝟘 +F (c · w7) · 𝟙 ≡ c · (𝟘 +F w7 · 𝟙)
    p0 = trans (+-identityˡ ((c · w7) · 𝟙))
         (trans (·-assoc c w7 𝟙) (sym (cong (c ·_) (+-identityˡ (w7 · 𝟙)))))
