{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEvalCD — ⟡jac-lit1-cd-normpoly.
--
-- A MEMORY-CHEAP common-denominator evaluator for the sparse polynomial
-- `MPoly`, and its soundness against the literal ℚ evaluator `evalℚ`.
--
-- ⚑ THE PROBLEM.  `evalℚ x y z p = evalT t +ℚ evalℚ p'` folds `_+ℚ_`, whose
-- `den = b·d` cross-multiplies the ~204 term denominators into a
-- degree-~34 ℤ product inside `+ℚ-cong` — ~730 MB for f₁'s cube.
--
-- ⚑ THE FIX.  Put every monomial numerator over ONE fixed denominator
--   D = qx^Dx · qy^Dy · qz^Dz   (qᵥ = the point's denominator for v),
-- sum the PADDED ℤ numerators with `_+ℤ_` (NEVER `_+ℚ_`), and build the ℚ
-- exactly ONCE:  `evalCD p = mkℚ (sumNum p) (D − 1)`.  Soundness is a chain
-- of STUCK-NEUTRAL ≈ℚ congruences over an abstract `p`, so instantiating it
-- at a concrete polynomial never forces the `_+ℚ_` fold.
--
-- ⚑ THE BOX HYPOTHESIS.  `padNum` uses truncated subtraction `Dᵥ ∸ a`, exact
-- only when `a ≤ Dᵥ`.  So `evalCD-sound` takes `Bounded p` — every monomial
-- inside the box (Dx,Dy,Dz).  `buildB` reflects the check: `allB p ≡ tt`
-- (a boolean over ℕ ≤) discharges `Bounded p` for a concrete `p`.
--
-- ⚑ SCOPE (honest).  `evalCD-sound` is FULLY GENERAL in the point (x,y,z).
-- The bridge to the curried ℚ map `C.f₁` (`evalCD-leg₂`) is `refl` ONLY at a
-- CONCRETE evaluation point (both sides close to concrete ℤ); it is NOT the
-- symbolic polynomial identity, so this route gives `literal₁` cheaply
-- AT A POINT, not the ∀-quantified `identify₁ : (x y z) → …` that
-- `JacobianCounterexample` consumes (that stays with `JacobianLiteral1`'s
-- Assemble route).  What is new here is the reusable cheap evaluator + its
-- general soundness, and the point-wise literal₁ at the collision points.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEvalCD where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _*_; _^_; _∸_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityˡ)
open import Substrate.Foundation.Nat.Properties.Order using (≤-trans; m≤m+n; *-monoˡ-≤)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-distribʳ-+; *ℤ-zeroˡ; *ℤ-identityˡ; quadℤ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)
open import Substrate.Algebra.Q.JacobianEvalNormalize
  using (powℚ; monoval; evalT; evalℚ; ≡→≈ℚ)
open import Substrate.Algebra.Z.JacobianResidue
  using (MPoly; Mono; mono; Term; term; 𝔹; tt; ff; and)
import Substrate.Algebra.Z.JacobianResidue as R
import Substrate.Algebra.Q.JacobianCollision as C
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Empty using (⊥)

------------------------------------------------------------------------
-- Positivity helpers (collapse `suc (D ∸ 1)` back to `D`).
------------------------------------------------------------------------

1≤* : {a b : ℕ} → 1 ≤ a → 1 ≤ b → 1 ≤ a * b
1≤* {a} {b} 1≤a 1≤b =
  ≤-trans 1≤b (subst (_≤ a * b) (*-identityˡ b) (*-monoˡ-≤ b 1≤a))

1≤pow : (q n : ℕ) → 1 ≤ suc q ^ n
1≤pow q zero    = s≤s z≤n
1≤pow q (suc k) = 1≤* {suc q} {suc q ^ k} (s≤s z≤n) (1≤pow q k)

sucpred : (m : ℕ) → 1 ≤ m → suc (m ∸ 1) ≡ m
sucpred (suc m) _ = refl

------------------------------------------------------------------------
-- Boolean box-check → build a Bounded proof by reflection.
------------------------------------------------------------------------

So : 𝔹 → Set
So tt = ⊤
So ff = ⊥

_≤ᵇ_ : ℕ → ℕ → 𝔹
zero  ≤ᵇ _     = tt
suc _ ≤ᵇ zero  = ff
suc a ≤ᵇ suc b = a ≤ᵇ b

≤ᵇ→≤ : (a b : ℕ) → So (a ≤ᵇ b) → a ≤ b
≤ᵇ→≤ zero    b       _ = z≤n
≤ᵇ→≤ (suc a) (suc b) h = s≤s (≤ᵇ→≤ a b h)

andˡ : (u v : 𝔹) → So (and u v) → So u
andˡ tt v h = record {}
andʳ : (u v : 𝔹) → So (and u v) → So v
andʳ tt v h = h

------------------------------------------------------------------------
-- ℤ-power and its laws.
------------------------------------------------------------------------

powℤ : ℤ → ℕ → ℤ
powℤ b zero    = + 1
powℤ b (suc n) = b *ℤ powℤ b n

powℤ-add : (b : ℤ) (m n : ℕ) → powℤ b (m + n) ≡ powℤ b m *ℤ powℤ b n
powℤ-add b zero    n = sym (*ℤ-identityˡ (powℤ b n))
powℤ-add b (suc m) n =
  trans (cong (b *ℤ_) (powℤ-add b m n)) (sym (*ℤ-assoc b (powℤ b m) (powℤ b n)))

powℤ-pos : (q n : ℕ) → powℤ (+ suc q) n ≡ + (suc q ^ n)
powℤ-pos q zero    = refl
powℤ-pos q (suc k) = cong ((+ suc q) *ℤ_) (powℤ-pos q k)

-- 6-factor commutative regrouping in ℤ (via the middle-swap `quadℤ`).
regroup6 : (X′ X Y′ Y Z′ Z : ℤ) →
           (X′ *ℤ (Y′ *ℤ Z′)) *ℤ (X *ℤ (Y *ℤ Z))
         ≡ (X′ *ℤ X) *ℤ ((Y′ *ℤ Y) *ℤ (Z′ *ℤ Z))
regroup6 X′ X Y′ Y Z′ Z =
  trans (quadℤ X′ (Y′ *ℤ Z′) X (Y *ℤ Z))
        (cong ((X′ *ℤ X) *ℤ_) (quadℤ Y′ Z′ Y Z))

-- powℚ ↔ mkℚ of ℤ-powers: (pw/qw)^n = pw^n / qw^n.
powℚ-mkℚ : (w : ℚ) (n : ℕ) →
           powℚ w n ≈ℚ mkℚ (powℤ (num w) n) (suc (den-1 w) ^ n ∸ 1)
powℚ-mkℚ w zero    = ≈ℚ-refl (powℚ w zero)
powℚ-mkℚ w (suc k) =
  ≈ℚ-trans {powℚ w (suc k)}
           {w *ℚ mkℚ (powℤ (num w) k) (suc (den-1 w) ^ k ∸ 1)}
           {mkℚ (powℤ (num w) (suc k)) (suc (den-1 w) ^ suc k ∸ 1)}
    (*ℚ-cong {w} {w} {powℚ w k} {mkℚ (powℤ (num w) k) (suc (den-1 w) ^ k ∸ 1)}
             (≈ℚ-refl w) (powℚ-mkℚ w k))
    (≡→≈ℚ (cong (λ t → mkℚ (num w *ℤ powℤ (num w) k) (t ∸ 1))
                (cong (suc (den-1 w) *_)
                      (sucpred (suc (den-1 w) ^ k) (1≤pow (den-1 w) k)))))

------------------------------------------------------------------------
-- The common-denominator evaluator, at a point (x,y,z) with a fixed box.
------------------------------------------------------------------------

module _ (x y z : ℚ) (Dx Dy Dz : ℕ) where

  qxn = suc (den-1 x)
  qyn = suc (den-1 y)
  qzn = suc (den-1 z)
  px = num x
  py = num y
  pz = num z

  Dden : ℕ
  Dden = (qxn ^ Dx) * ((qyn ^ Dy) * (qzn ^ Dz))

  1≤Dden : 1 ≤ Dden
  1≤Dden = 1≤* {qxn ^ Dx} {(qyn ^ Dy) * (qzn ^ Dz)}
               (1≤pow (den-1 x) Dx)
               (1≤* {qyn ^ Dy} {qzn ^ Dz}
                    (1≤pow (den-1 y) Dy) (1≤pow (den-1 z) Dz))

  -- abbreviations for a monomial (a,b,c).
  NUM : ℕ → ℕ → ℕ → ℤ
  NUM a b c = powℤ px a *ℤ (powℤ py b *ℤ powℤ pz c)

  Qn : ℕ → ℕ → ℕ → ℕ
  Qn a b c = qxn ^ a * (qyn ^ b * qzn ^ c)

  1≤Qn : (a b c : ℕ) → 1 ≤ Qn a b c
  1≤Qn a b c = 1≤* {qxn ^ a} {qyn ^ b * qzn ^ c}
                   (1≤pow (den-1 x) a)
                   (1≤* {qyn ^ b} {qzn ^ c}
                        (1≤pow (den-1 y) b) (1≤pow (den-1 z) c))

  -- one monomial's numerator, PADDED to Dden (single ℤ product; NO _+ℚ_).
  padNum : Term → ℤ
  padNum (term (mono a b c) k) =
      k *ℤ (powℤ px a *ℤ (powℤ py b *ℤ powℤ pz c))
        *ℤ (powℤ (+ qxn) (Dx ∸ a) *ℤ (powℤ (+ qyn) (Dy ∸ b) *ℤ powℤ (+ qzn) (Dz ∸ c)))

  sumNum : MPoly → ℤ
  sumNum []      = 0ℤ
  sumNum (t ∷ p) = padNum t +ℤ sumNum p

  evalCD : MPoly → ℚ
  evalCD p = mkℚ (sumNum p) (Dden ∸ 1)

  ----------------------------------------------------------------------
  -- fixed-D addition (numerator-wise; no _+ℚ_ blowup).
  ----------------------------------------------------------------------

  fixed-D-add : (A B : ℤ) (d : ℕ) →
                (mkℚ A d +ℚ mkℚ B d) ≈ℚ mkℚ (A +ℤ B) d
  fixed-D-add A B d =
    trans (cong (_*ℤ (+ suc d)) (sym (*ℤ-distribʳ-+ A B (+ suc d))))
    (trans (*ℤ-assoc (A +ℤ B) (+ suc d) (+ suc d))
           (cong ((A +ℤ B) *ℤ_)
                 (sym (cong +_ (sucpred (suc d * suc d)
                                        (1≤* {suc d} {suc d} (s≤s z≤n) (s≤s z≤n)))))))

  ----------------------------------------------------------------------
  -- Bounded: every monomial fits the box; buildB reflects the check.
  ----------------------------------------------------------------------

  data Bounded : MPoly → Set where
    b[] : Bounded []
    b∷  : {a b c : ℕ} {k : ℤ} {p : MPoly} →
          a ≤ Dx → b ≤ Dy → c ≤ Dz → Bounded p →
          Bounded (term (mono a b c) k ∷ p)

  allB : MPoly → 𝔹
  allB []                          = tt
  allB (term (mono a b c) _ ∷ p) =
    and (a ≤ᵇ Dx) (and (b ≤ᵇ Dy) (and (c ≤ᵇ Dz) (allB p)))

  buildB : (p : MPoly) → So (allB p) → Bounded p
  buildB []                        _ = b[]
  buildB (term (mono a b c) k ∷ p) h =
    b∷ (≤ᵇ→≤ a Dx (andˡ (a ≤ᵇ Dx) _ h))
       (≤ᵇ→≤ b Dy (andˡ (b ≤ᵇ Dy) _ (andʳ (a ≤ᵇ Dx) _ h)))
       (≤ᵇ→≤ c Dz (andˡ (c ≤ᵇ Dz) _ (andʳ (b ≤ᵇ Dy) _ (andʳ (a ≤ᵇ Dx) _ h))))
       (buildB p (andʳ (c ≤ᵇ Dz) _ (andʳ (b ≤ᵇ Dy) _ (andʳ (a ≤ᵇ Dx) _ h))))

  ----------------------------------------------------------------------
  -- monoval as a single mkℚ over Qn.
  ----------------------------------------------------------------------

  monoval-mkℚ : (a b c : ℕ) →
                monoval x y z (mono a b c) ≈ℚ mkℚ (NUM a b c) (Qn a b c ∸ 1)
  monoval-mkℚ a b c =
    ≈ℚ-trans {monoval x y z (mono a b c)}
             {mkℚ (powℤ px a) (qxn ^ a ∸ 1)
                *ℚ (mkℚ (powℤ py b) (qyn ^ b ∸ 1) *ℚ mkℚ (powℤ pz c) (qzn ^ c ∸ 1))}
             {mkℚ (NUM a b c) (Qn a b c ∸ 1)}
      (*ℚ-cong {powℚ x a} {mkℚ (powℤ px a) (qxn ^ a ∸ 1)}
               {powℚ y b *ℚ powℚ z c}
               {mkℚ (powℤ py b) (qyn ^ b ∸ 1) *ℚ mkℚ (powℤ pz c) (qzn ^ c ∸ 1)}
               (powℚ-mkℚ x a)
               (*ℚ-cong {powℚ y b} {mkℚ (powℤ py b) (qyn ^ b ∸ 1)}
                        {powℚ z c} {mkℚ (powℤ pz c) (qzn ^ c ∸ 1)}
                        (powℚ-mkℚ y b) (powℚ-mkℚ z c)))
      (≡→≈ℚ (cong (λ t → mkℚ (NUM a b c) (t ∸ 1)) den-eq))
    where
      inner-eq : suc (qyn ^ b ∸ 1) * suc (qzn ^ c ∸ 1) ≡ qyn ^ b * qzn ^ c
      inner-eq = cong₂ _*_ (sucpred (qyn ^ b) (1≤pow (den-1 y) b))
                           (sucpred (qzn ^ c) (1≤pow (den-1 z) c))
      e2 : suc (suc (qyn ^ b ∸ 1) * suc (qzn ^ c ∸ 1) ∸ 1) ≡ qyn ^ b * qzn ^ c
      e2 = trans (cong (λ w → suc (w ∸ 1)) inner-eq)
                 (sucpred (qyn ^ b * qzn ^ c)
                          (1≤* {qyn ^ b} {qzn ^ c}
                               (1≤pow (den-1 y) b) (1≤pow (den-1 z) c)))
      den-eq : suc (qxn ^ a ∸ 1)
                 * suc (suc (qyn ^ b ∸ 1) * suc (qzn ^ c ∸ 1) ∸ 1)
             ≡ Qn a b c
      den-eq = cong₂ _*_ (sucpred (qxn ^ a) (1≤pow (den-1 x) a)) e2

  ----------------------------------------------------------------------
  -- evalT as a single mkℚ.
  ----------------------------------------------------------------------

  evalT-mkℚ : (a b c : ℕ) (k : ℤ) →
              evalT x y z (term (mono a b c) k) ≈ℚ mkℚ (k *ℤ NUM a b c) (Qn a b c ∸ 1)
  evalT-mkℚ a b c k =
    ≈ℚ-trans {evalT x y z (term (mono a b c) k)}
             {mkℚ k 0 *ℚ mkℚ (NUM a b c) (Qn a b c ∸ 1)}
             {mkℚ (k *ℤ NUM a b c) (Qn a b c ∸ 1)}
      (*ℚ-cong {ℤ→ℚ k} {mkℚ k 0}
               {monoval x y z (mono a b c)} {mkℚ (NUM a b c) (Qn a b c ∸ 1)}
               (≈ℚ-refl (ℤ→ℚ k)) (monoval-mkℚ a b c))
      (≡→≈ℚ (cong (λ t → mkℚ (k *ℤ NUM a b c) t)
                  (cong (_∸ 1) (*-identityˡ (suc (Qn a b c ∸ 1))))))

  ----------------------------------------------------------------------
  -- padding: mkℚ over Qn ≈ℚ mkℚ over the fixed Dden.
  ----------------------------------------------------------------------

  pad-step : (a b c : ℕ) (k : ℤ) → a ≤ Dx → b ≤ Dy → c ≤ Dz →
             mkℚ (k *ℤ NUM a b c) (Qn a b c ∸ 1)
               ≈ℚ mkℚ (padNum (term (mono a b c) k)) (Dden ∸ 1)
  pad-step a b c k a≤ b≤ c≤ =
    trans (cong ((k *ℤ NUM a b c) *ℤ_) (cong +_ (sucpred Dden 1≤Dden)))
    (trans (cong ((k *ℤ NUM a b c) *ℤ_) dfact)
    (trans (sym (*ℤ-assoc (k *ℤ NUM a b c) PADQ (+ Qn a b c)))
           (cong (padNum (term (mono a b c) k) *ℤ_)
                 (cong +_ (sym (sucpred (Qn a b c) (1≤Qn a b c)))))))
    where
      Px′ = powℤ (+ qxn) (Dx ∸ a) ; Px = powℤ (+ qxn) a
      Py′ = powℤ (+ qyn) (Dy ∸ b) ; Py = powℤ (+ qyn) b
      Pz′ = powℤ (+ qzn) (Dz ∸ c) ; Pz = powℤ (+ qzn) c
      PADQ = Px′ *ℤ (Py′ *ℤ Pz′)
      -- powℤ Dx = powℤ(Dx∸a) · powℤ a, etc.
      ex : powℤ (+ qxn) Dx ≡ Px′ *ℤ Px
      ex = trans (cong (powℤ (+ qxn)) (sym (∸-+-id Dx a a≤)))
                 (powℤ-add (+ qxn) (Dx ∸ a) a)
      ey : powℤ (+ qyn) Dy ≡ Py′ *ℤ Py
      ey = trans (cong (powℤ (+ qyn)) (sym (∸-+-id Dy b b≤)))
                 (powℤ-add (+ qyn) (Dy ∸ b) b)
      ez : powℤ (+ qzn) Dz ≡ Pz′ *ℤ Pz
      ez = trans (cong (powℤ (+ qzn)) (sym (∸-+-id Dz c c≤)))
                 (powℤ-add (+ qzn) (Dz ∸ c) c)
      -- + Dden ≡ powℤ Dx · (powℤ Dy · powℤ Dz)
      posD : powℤ (+ qxn) Dx *ℤ (powℤ (+ qyn) Dy *ℤ powℤ (+ qzn) Dz) ≡ + Dden
      posD = cong₂ _*ℤ_ (powℤ-pos (den-1 x) Dx)
                        (cong₂ _*ℤ_ (powℤ-pos (den-1 y) Dy) (powℤ-pos (den-1 z) Dz))
      posQ : Px *ℤ (Py *ℤ Pz) ≡ + Qn a b c
      posQ = cong₂ _*ℤ_ (powℤ-pos (den-1 x) a)
                        (cong₂ _*ℤ_ (powℤ-pos (den-1 y) b) (powℤ-pos (den-1 z) c))
      dfact : + Dden ≡ PADQ *ℤ (+ Qn a b c)
      dfact =
        trans (sym posD)
        (trans (cong₂ _*ℤ_ ex (cong₂ _*ℤ_ ey ez))
        (trans (sym (regroup6 Px′ Px Py′ Py Pz′ Pz))
               (cong (PADQ *ℤ_) posQ)))

  ----------------------------------------------------------------------
  -- gen-sound: a single term evaluates to its padded numerator over Dden.
  ----------------------------------------------------------------------

  gen-sound : (a b c : ℕ) (k : ℤ) → a ≤ Dx → b ≤ Dy → c ≤ Dz →
              evalT x y z (term (mono a b c) k)
                ≈ℚ mkℚ (padNum (term (mono a b c) k)) (Dden ∸ 1)
  gen-sound a b c k a≤ b≤ c≤ =
    ≈ℚ-trans {evalT x y z (term (mono a b c) k)}
             {mkℚ (k *ℤ NUM a b c) (Qn a b c ∸ 1)}
             {mkℚ (padNum (term (mono a b c) k)) (Dden ∸ 1)}
      (evalT-mkℚ a b c k) (pad-step a b c k a≤ b≤ c≤)

  ----------------------------------------------------------------------
  -- THE SOUNDNESS: evalℚ ≈ℚ evalCD, for Bounded p.  General in (x,y,z).
  ----------------------------------------------------------------------

  evalCD-sound : (p : MPoly) → Bounded p → evalℚ x y z p ≈ℚ evalCD p
  evalCD-sound [] b[] =
    trans (*ℤ-zeroˡ (+ suc (Dden ∸ 1))) (sym (*ℤ-zeroˡ (+ 1)))
  evalCD-sound (term (mono a b c) k ∷ p') (b∷ a≤ b≤ c≤ Bp') =
    ≈ℚ-trans {evalT x y z (term (mono a b c) k) +ℚ evalℚ x y z p'}
             {mkℚ (padNum (term (mono a b c) k)) (Dden ∸ 1)
                +ℚ mkℚ (sumNum p') (Dden ∸ 1)}
             {evalCD (term (mono a b c) k ∷ p')}
      (+ℚ-cong {evalT x y z (term (mono a b c) k)}
               {mkℚ (padNum (term (mono a b c) k)) (Dden ∸ 1)}
               {evalℚ x y z p'} {mkℚ (sumNum p') (Dden ∸ 1)}
               (gen-sound a b c k a≤ b≤ c≤) (evalCD-sound p' Bp'))
      (fixed-D-add (padNum (term (mono a b c) k)) (sumNum p') (Dden ∸ 1))

------------------------------------------------------------------------
-- THE 2nd LEG + POINT-WISE literal₁, at the two collision points.
--
-- f₁ = z(1+xy)³ + y²(1+xy)(4+3xy) — measured degree box (Dx,Dy,Dz)=(3,4,1)
-- (max monomials x³y³z and x²y⁴; `Bounded-f₁` below reflects that it fits).
------------------------------------------------------------------------

-- Bounded R.f₁ at box (3,4,1), by reflection (allB R.f₁ ≡ tt).  The box is
-- point-independent, so ONE proof serves both points (built at p₀).
Bounded-f₁ : Bounded 0ℚ 0ℚ C.-1/4ℚ 3 4 1 R.f₁
Bounded-f₁ = buildB 0ℚ 0ℚ C.-1/4ℚ 3 4 1 R.f₁ record {}

Bounded-f₁-q : Bounded 1ℚ C.-3/2ℚ C.13/2ℚ 3 4 1 R.f₁
Bounded-f₁-q = buildB 1ℚ C.-3/2ℚ C.13/2ℚ 3 4 1 R.f₁ record {}

-- leg₂: the CD-evaluated polynomial IS the curried ℚ map, at a point (refl).
evalCD-leg₂-p : evalCD 0ℚ 0ℚ C.-1/4ℚ 3 4 1 R.f₁ ≈ℚ C.f₁ 0ℚ 0ℚ C.-1/4ℚ
evalCD-leg₂-p = refl

evalCD-leg₂-q : evalCD 1ℚ C.-3/2ℚ C.13/2ℚ 3 4 1 R.f₁ ≈ℚ C.f₁ 1ℚ C.-3/2ℚ C.13/2ℚ
evalCD-leg₂-q = refl

-- literal₁ at each collision point, via the common-denominator route
-- (soundness ∘ leg₂) — no _+ℚ_ fold materialized.
literal₁-cheap-p : evalℚ 0ℚ 0ℚ C.-1/4ℚ R.f₁ ≈ℚ C.f₁ 0ℚ 0ℚ C.-1/4ℚ
literal₁-cheap-p =
  ≈ℚ-trans {evalℚ 0ℚ 0ℚ C.-1/4ℚ R.f₁}
           {evalCD 0ℚ 0ℚ C.-1/4ℚ 3 4 1 R.f₁}
           {C.f₁ 0ℚ 0ℚ C.-1/4ℚ}
    (evalCD-sound 0ℚ 0ℚ C.-1/4ℚ 3 4 1 R.f₁ Bounded-f₁) evalCD-leg₂-p

literal₁-cheap-q : evalℚ 1ℚ C.-3/2ℚ C.13/2ℚ R.f₁ ≈ℚ C.f₁ 1ℚ C.-3/2ℚ C.13/2ℚ
literal₁-cheap-q =
  ≈ℚ-trans {evalℚ 1ℚ C.-3/2ℚ C.13/2ℚ R.f₁}
           {evalCD 1ℚ C.-3/2ℚ C.13/2ℚ 3 4 1 R.f₁}
           {C.f₁ 1ℚ C.-3/2ℚ C.13/2ℚ}
    (evalCD-sound 1ℚ C.-3/2ℚ C.13/2ℚ 3 4 1 R.f₁ Bounded-f₁-q) evalCD-leg₂-q
