------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigResidue
--
-- ⟡rig-UP-residue — the counit-defect (hypothesis − actual of the rig's
-- ⊗ᶜ-step) realised as a PROPER OBJECT: an instance of the generic
-- `Substrate.Algebra.Wedge.Wedge`, with the `DivStr` manufactured from the
-- orientation rig's own ⊗ˢ / ⊕ on the flattened carrier Σ ℕ LehmerPath.
--
--   z        = (0 , start)                                  -- no residue
--   recon (gq,q) (gb,b) (gr,r) = (gq*gb+gr , (q ⊗ˢ b) ⊕ r)   -- "q·b then r", in the rig
--
-- and the `=`-corner (quot = (1,X), rem = z, X = start ◂ zero) reconstructs b:
-- `recon (1,X) (n,b) (0,start) ≡ (n,b)` — the RESIDUE `rem` is exactly z (=(0,start)),
-- i.e. no orientation defect, precisely at the identity corner.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigResidue where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ)
open import Substrate.Foundation.Nat.Properties.Cancel using (+-cancelˡ)
open import Substrate.Foundation.Fin using (Fin; zero; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; Σ-≡,≡→≡)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.Wedge using (DivStr; recon; z) renaming (Wedge to Wedge⟦9e8d371e⟧)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_; 0#)
open import Substrate.WitnessTower.Wedge.OrientationSumLaws using (⊕-unit-right; ◂-subst)
open import Substrate.WitnessTower.Wedge.OrientationProductStructural
  using (_⊗ˢ_; replay-aux; replayOffset; offsetDigit)
open import Substrate.WitnessTower.Wedge.OrientationFixedPoint using (decode-injective)

------------------------------------------------------------------------
-- 0. The multiplicative unit X = start ◂ zero : LehmerPath 1 (oneᶜ).
------------------------------------------------------------------------

X : LehmerPath (suc zero)
X = start ◂ zero

------------------------------------------------------------------------
-- S1. divᴸ : DivStr (Σ ℕ LehmerPath) — the rig recon (NOT flatten's power-recon).
--     z = (0 , start); recon (gq,q) (gb,b) (gr,r) = (gq*gb+gr , (q ⊗ˢ b) ⊕ r).
------------------------------------------------------------------------

divᴸ : DivStr (Σ ℕ LehmerPath)
divᴸ = record
  { z     = zero , start
  ; recon = λ { (_ , q) (_ , b) (_ , r) → _ , ((q ⊗ˢ b) ⊕ r) }
  }

------------------------------------------------------------------------
-- Small transport lemmas (Foundation had no subst-over-trans / toℕ-subst).
------------------------------------------------------------------------

-- subst over a composite equality = the two substs, in order.
subst-trans : {A : Set} {B : A → Set} {x y w : A}
              (p : x ≡ y) (q : y ≡ w) (b : B x) →
              subst B (trans p q) b ≡ subst B q (subst B p b)
subst-trans refl q b = refl

-- toℕ is invariant under a grade-`subst` through `Fin ∘ suc` (eq-induction).
toℕ-subst-suc : ∀ {a b} (eq : a ≡ b) (x : Fin (suc a)) →
                toℕ (subst (λ z → Fin (suc z)) eq x) ≡ toℕ x
toℕ-subst-suc refl x = refl

------------------------------------------------------------------------
-- S2. ⊗ˢ-unit-left : subst LehmerPath (*-identityˡ n) (X ⊗ˢ b) ≡ b.
--     X ⊗ˢ b = replayOffset zero b (start ⊗ˢ b) = replay-aux zero n b start
--     (definitionally). The fiddly enabler: replay the length-n fragment of b
--     onto the empty base with digit offset 0·n, then transport the 0-grade away.
------------------------------------------------------------------------

-- the offset digit at p = zero carries value 0·n + toℕ q = toℕ q.
toℕ-offsetDigit-zero : ∀ (n : ℕ) {k} (q : Fin (suc k)) →
                       toℕ (offsetDigit {0} zero n q) ≡ toℕ q
toℕ-offsetDigit-zero n q = toℕ-fromℕ< _

-- and after transporting the +0 grade away, the offset digit IS q.
offsetDigit-zero-unit : ∀ {n k} (q : Fin (suc k)) →
  subst (λ z → Fin (suc z)) (+-identityʳ k) (offsetDigit {0} zero n q) ≡ q
offsetDigit-zero-unit {n} {k} q =
  toℕ-injective
    (trans (toℕ-subst-suc (+-identityʳ k) (offsetDigit {0} zero n q))
           (toℕ-offsetDigit-zero n q))

-- the core induction: replaying l onto the empty base, then dropping +0, is l.
replay-aux-zero-unit : ∀ {n k} (l : LehmerPath k) →
  subst LehmerPath (+-identityʳ k) (replay-aux {m = 0} zero n l start) ≡ l
replay-aux-zero-unit         start    = refl
replay-aux-zero-unit {n} {suc k} (l ◂ q) =
  trans (◂-subst (+-identityʳ k) (replay-aux {m = 0} zero n l start)
                 (offsetDigit {0} zero n q))
        (cong₂ _◂_ (replay-aux-zero-unit l) (offsetDigit-zero-unit {n} q))

⊗ˢ-unit-left : ∀ {n} (b : LehmerPath n) →
               subst LehmerPath (*-identityˡ n) (X ⊗ˢ b) ≡ b
⊗ˢ-unit-left {n} b = replay-aux-zero-unit {n} {n} b

------------------------------------------------------------------------
-- S3. corner-eq : recon divᴸ (1 , X) (n , b) (0 , start) ≡ (n , b).
--     The (1,z) corner reconstructs b; the residue rem = z = (0 , start).
--     Σ-equality: grade 1·n+0 ≡ n, and value (X ⊗ˢ b) ⊕ start ≡ b (via S2 + ⊕-unit-right).
------------------------------------------------------------------------

corner-eq : ∀ {n} (b : LehmerPath n) →
            recon divᴸ (suc zero , X) (n , b) (zero , start) ≡ (n , b)
corner-eq {n} b = Σ-≡,≡→≡ (grade-eq , value-proof)
  where
    grade-eq : suc zero * n + zero ≡ n
    grade-eq = trans (+-identityʳ (suc zero * n)) (*-identityˡ n)

    value-proof : subst LehmerPath grade-eq ((X ⊗ˢ b) ⊕ start) ≡ b
    value-proof =
      trans (subst-trans (+-identityʳ (suc zero * n)) (*-identityˡ n) ((X ⊗ˢ b) ⊕ start))
            (trans (cong (subst LehmerPath (*-identityˡ n)) (⊕-unit-right (X ⊗ˢ b)))
                   (⊗ˢ-unit-left b))

------------------------------------------------------------------------
-- The RESIDUE object: the wedge of b against itself at the identity corner,
-- with rem = z (no orientation defect). wedge-eq is sym corner-eq.
------------------------------------------------------------------------

residue-wedge : ∀ {n} (b : LehmerPath n) → Wedge⟦9e8d371e⟧ divᴸ (n , b) (n , b)
residue-wedge {n} b = record
  { quot     = suc zero , X
  ; rem      = zero , start
  ; wedge-eq = sym (corner-eq b)
  }

------------------------------------------------------------------------
-- S4. couple-is-corner (the payoff). The canonical ⊗ᶜ-step block-insert
--     `replay-aux p n · base` is INJECTIVE in its driver path: it agrees on l₂
--     and y iff l₂ ≡ y — and, through decode-injective, iff the decode-traces
--     coincide. So the coupling obligation of ⊗ᶜ-step holds EXACTLY when the
--     driver sits at the identity corner over the multiplicand, i.e. rem ≡ z.
------------------------------------------------------------------------

-- the offset digit's underlying value is p·n + q, for any p (general form of
-- toℕ-offsetDigit-zero).
toℕ-offsetDigit : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k} (q : Fin (suc k)) →
                  toℕ (offsetDigit p n q) ≡ toℕ p * n + toℕ q
toℕ-offsetDigit p n q = toℕ-fromℕ< _

-- offsetDigit is injective in its digit (cancel the shared p·n offset).
offsetDigit-inj : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k} (q q' : Fin (suc k)) →
                  offsetDigit p n q ≡ offsetDigit p n q' → q ≡ q'
offsetDigit-inj p n q q' eq =
  toℕ-injective
    (+-cancelˡ (toℕ p * n)
      (trans (sym (toℕ-offsetDigit p n q))
             (trans (cong toℕ eq) (toℕ-offsetDigit p n q'))))

-- ◂ is injective (constructor injectivity, homogeneous — without-K safe).
◂-inj₁ : ∀ {k} {a c : LehmerPath k} {b d : Fin (suc k)} →
         (a ◂ b) ≡ (c ◂ d) → a ≡ c
◂-inj₁ refl = refl

◂-inj₂ : ∀ {k} {a c : LehmerPath k} {b d : Fin (suc k)} →
         (a ◂ b) ≡ (c ◂ d) → b ≡ d
◂-inj₂ refl = refl

-- THE INJECTIVITY: the block-insert `replay-aux p n · base` reflects equality of
-- driver paths (peel the appended offset digits, offsetDigit-inj + IH).
replay-aux-inj : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k}
                 (l₂ y : LehmerPath k) (base : LehmerPath (m * n)) →
                 replay-aux p n l₂ base ≡ replay-aux p n y base → l₂ ≡ y
replay-aux-inj p n start    start     base eq = refl
replay-aux-inj p n (l ◂ q) (l' ◂ q') base eq =
  cong₂ _◂_ (replay-aux-inj p n l l' base (◂-inj₁ eq))
            (offsetDigit-inj p n q q' (◂-inj₂ eq))

-- ⟸ : if the drivers agree, so do the block-inserts (cong).
couple-⟸ : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k}
           (l₂ y : LehmerPath k) (base : LehmerPath (m * n)) →
           l₂ ≡ y → replay-aux p n l₂ base ≡ replay-aux p n y base
couple-⟸ p n l₂ y base eq = cong (λ z → replay-aux p n z base) eq

-- ⟹ : the block-inserts agree only if the drivers do (= replay-aux-inj).
couple-⟹ : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k}
           (l₂ y : LehmerPath k) (base : LehmerPath (m * n)) →
           replay-aux p n l₂ base ≡ replay-aux p n y base → l₂ ≡ y
couple-⟹ = replay-aux-inj

-- THE DECODE-TRACE FORM (via decode-injective): coupled ⟺ decode-traces coincide.
decode-couple-⟹ : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k}
                  (l₂ y : LehmerPath k) (base : LehmerPath (m * n)) →
                  replay-aux p n l₂ base ≡ replay-aux p n y base →
                  decode l₂ ≡ decode y
decode-couple-⟹ p n l₂ y base eq = cong decode (replay-aux-inj p n l₂ y base eq)

decode-couple-⟸ : ∀ {m} (p : Fin (suc m)) (n : ℕ) {k}
                  (l₂ y : LehmerPath k) (base : LehmerPath (m * n)) →
                  decode l₂ ≡ decode y →
                  replay-aux p n l₂ base ≡ replay-aux p n y base
decode-couple-⟸ p n l₂ y base deq =
  couple-⟸ p n l₂ y base (decode-injective l₂ y deq)
