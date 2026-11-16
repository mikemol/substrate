------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.IntParityBridge
--
-- ℤ ↠ F₂ — the parity bridge on the ℤ root, completing the parity story
-- (Algebra.Wedge.ParityBridge gave ℕ ↠ F₂; ℤ ⊃ ℕ, so this extends it). A
-- genuine cross-root wedge bridge that RAISES the bridge-degree of the founded
-- roots beyond the ℕ-centric star: ℤ-div and F₂-div each gain an edge that does
-- not route through ℕ.
--
-- parity-ℤ is SIGN-BLIND: −x ≡ x (mod 2), so the negative branch -suc n maps to
-- parity (suc n) — the magnitude's parity. The ring-hom laws (respects recon)
-- reduce to the ℕ parity laws (reused from ParityBridge) plus two F₂
-- rearrangements that hold by 4-case refl (F₂ is the decidable carrier where
-- the cancellation is computational — the LEM-faithful flip again).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.IntParityBridge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Algebra.F2.F2
-- ⚑ THE OPERATORS THEMSELVES WERE NEVER BOUND (Ⓕ-ALIAS-RESTORE) — same defect as
-- the sibling `ParityBridge`: `_·_`/`_+F_` were reached through a barrel alias
-- (`renaming (_+_ to _+₂_; _·_ to _·₂_)`, 97e567f2) that the ban paydown dropped
-- when the barrel decomposed, without rewriting the use sites below.
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.Wedge using (F₂-div)
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
-- ⚑ A FOURTH INSTANCE OF THE SAME CLASS.  `Z.Arithmetic` no longer exports
-- `_+ℤ_`/`_*ℤ_`/`_⊖_` — it is itself a conduit whose names moved to `Z.Add` and
-- `Z.Mul` (it is the Ⓑ1a⁵ retire candidate).  The `using` named three
-- non-exports, which agda reports only as a WARNING, so this bound nothing and
-- surfaced as `NotInScope: ⊖` fifty lines below.
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
-- ⚑ `parity`/`parity-+` WERE REACHED THROUGH `ParityBridge`'s `public`
-- RE-EXPORT (Ⓑ2c); the home is `Algebra.N-to-F2-Parity`.
open import Substrate.Algebra.N-to-F2-Parity
-- ⚑ ONLY `parity-*` COMES FROM HERE.  The clause also named `parity`/`parity-+`,
-- which `ParityBridge` does not define — it forwarded them from `N-to-F2-Parity`
-- via the `public` Ⓑ2c retired, and that module (imported above) is their home.
-- A `using` naming a non-export is only a WARNING, so this would have bound
-- nothing and broken far from its cause; ⚑ AND `parity-*` sitting here at all is
-- the asymmetric-home finding: the two legs of one ring hom ℕ→F₂ live in
-- different packages (Ⓐ-PARITY-HOME).
open import Substrate.Algebra.Wedge.ParityBridge using (parity-*)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. parity on ℤ — sign-blind (magnitude's parity).
------------------------------------------------------------------------

parity-ℤ : ℤ → F₂
parity-ℤ (+ n)    = parity n
parity-ℤ (-suc n) = parity (suc n)

------------------------------------------------------------------------
-- 2. F₂ rearrangements (4-case refl — the decidable cancellation).
------------------------------------------------------------------------

-- x ℕ+ y = (𝟙+x) ℕ+ (𝟙+y): the two units cancel.
f2-shift : (x y : F₂) → x +F y ≡ (𝟙 +F x) +F (𝟙 +F y)
f2-shift 𝟘 𝟘 = refl
f2-shift 𝟘 𝟙 = refl
f2-shift 𝟙 𝟘 = refl
f2-shift 𝟙 𝟙 = refl

-- 𝟙+(𝟙+(x+y)) = (𝟙+x)ℕ+(𝟙+y): the same cancellation, for the both-negative case.
f2-both : (x y : F₂) → 𝟙 +F (𝟙 +F (x +F y)) ≡ (𝟙 +F x) +F (𝟙 +F y)
f2-both 𝟘 𝟘 = refl
f2-both 𝟘 𝟙 = refl
f2-both 𝟙 𝟘 = refl
f2-both 𝟙 𝟙 = refl

------------------------------------------------------------------------
-- 3. parity of the truncated difference: m ⊖ n ≡ m ℕ+ n (mod 2).
------------------------------------------------------------------------

parity-⊖ : (m n : ℕ) → parity-ℤ (m ⊖ n) ≡ parity m +F parity n
parity-⊖ m       zero    = sym (+-identityʳ (parity m))
parity-⊖ zero    (suc n) = refl
parity-⊖ (suc m) (suc n) = trans (parity-⊖ m n) (f2-shift (parity m) (parity n))

------------------------------------------------------------------------
-- 4. parity-ℤ is additive: parity-ℤ (x +ℤ y) ≡ parity-ℤ x ℕ+ parity-ℤ y.
------------------------------------------------------------------------

parity-ℤ-+ : (x y : ℤ) → parity-ℤ (x +ℤ y) ≡ parity-ℤ x +F parity-ℤ y
parity-ℤ-+ (+ m)    (+ n)    = parity-+ m n
parity-ℤ-+ (+ m)    (-suc n) = parity-⊖ m (suc n)
parity-ℤ-+ (-suc m) (+ n)    =
  trans (parity-⊖ n (suc m)) (+-comm (parity n) (parity (suc m)))
parity-ℤ-+ (-suc m) (-suc n) =
  trans (cong (λ w → 𝟙 +F (𝟙 +F w)) (parity-+ m n)) (f2-both (parity m) (parity n))

------------------------------------------------------------------------
-- 5. parity-ℤ kills the sign: parity-ℤ (-ℤ (+ k)) ≡ parity k.
------------------------------------------------------------------------

parity-negPos : (k : ℕ) → parity-ℤ (-ℤ (+ k)) ≡ parity k
parity-negPos zero    = refl
parity-negPos (suc k) = refl

------------------------------------------------------------------------
-- 6. parity-ℤ is multiplicative (sign-blind): parity-ℤ (x ·ℤ y) = parity-ℤ x ·
--    parity-ℤ y. One case per sign pair; parity-negPos kills the sign on the two
--    mixed-sign products, then the ℕ multiplicative leg parity-* closes each.
------------------------------------------------------------------------

parity-ℤ-* : (x y : ℤ) → parity-ℤ (x *ℤ y) ≡ parity-ℤ x · parity-ℤ y
parity-ℤ-* (+ m)    (+ n)    = parity-* m n
parity-ℤ-* (+ m)    (-suc n) = trans (parity-negPos (m * suc n)) (parity-* m (suc n))
parity-ℤ-* (-suc m) (+ n)    = trans (parity-negPos (suc m * n)) (parity-* (suc m) n)
parity-ℤ-* (-suc m) (-suc n) = parity-* (suc m) (suc n)

------------------------------------------------------------------------
-- 7. THE BRIDGE: ℤ-div ↠ F₂-div (the mod-2 ring homomorphism).
------------------------------------------------------------------------

int-parity-bridge : Bridge ℤ-div F₂-div
int-parity-bridge = record
  { translate = parity-ℤ
  ; respects  = λ q b r →
      trans (parity-ℤ-+ (q *ℤ b) r)
            (cong (_+F parity-ℤ r) (parity-ℤ-* q b))
  ; z-pres    = refl
  }
