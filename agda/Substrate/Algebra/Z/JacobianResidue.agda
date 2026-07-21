{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.JacobianResidue — ⟡jac-det.
--
-- HALF (ii) of the claimed counterexample to the JACOBIAN CONJECTURE, and the
-- half that carries ALL the risk: is `det Jac F` a nonzero CONSTANT?
--
-- ⚑⚑ THIS IS A **WEDGE COMPUTATION, NOT AN EQUALITY TEST.** The repository does
-- not discard residues. We do NOT ask "does det + 2 normalize to 0?" — that
-- question has a BOOLEAN answer, and a boolean throws away everything that
-- makes a negative result useful. Instead we compute the wedge
--
--     det Jac F  =  recon q b r        with q = −2, b = 1, r = the residue
--
-- and DELIVER `r`: its coefficient at every monomial in the degree box. If the
-- claim holds, `r` is identically zero and that is a theorem ABOUT THE RESIDUE.
-- If it does not, `residue-coeffs` is a concrete graded object naming EXACTLY
-- which monomials survive and at which degree — the finding, not a failure.
-- (Same shape as `R.Trace.PeriodicCover.orbit-discriminates` and
-- `R.Trace.EventualPeriod`: read the observable; never assume-and-refute.)
--
-- COEFFICIENTS ARE INTEGERS — F's coefficients are 1,2,3,4, so `det Jac F` lives
-- in ℤ[x,y,z] and no ℚ is needed here. (The COLLISION, half (i), is genuinely
-- rational and lives in `Algebra.Q.JacobianCollision`.)
--
-- DEGREE BOX. Measured, not guessed: F's components have degrees (3,4,1),
-- (3,3,1), (3,1,1); the Jacobian entries therefore have degrees ≤ (3,4,1), and
-- the determinant is a sum of 3-fold products, so every monomial of `det Jac F`
-- lies in x ≤ 9, y ≤ 12, z ≤ 3. The box below is exactly that, so the residue
-- vector is COMPLETE — no monomial of the determinant escapes it.
--
-- ⚑ PROVENANCE + BOUNDARY. The map is attributed to Levent Alpöge (2026-07-19)
-- via Wikipedia; I have no independent knowledge of it. Together with
-- `JacobianCollision` (half (i), non-injectivity) this module completes the
-- verification: a counterexample needs BOTH, and a polynomial map with constant
-- nonzero Jacobian that is not injective is exactly what the conjecture forbids.
--
-- ⚑⚑ HONEST DEBT — `MPoly` IS A BESPOKE REBUILD (⟡jac-det-via-sppf).
-- The substrate's COMMON term algebra is `Algebra.Semiring.SPPF` — the FREE
-- SEMIRING on generators, with `inside` folding it into ANY semiring and
-- `inside-unique` making that fold the unique hom. A polynomial in three
-- variables IS a term over generators {x,y,z}, so `SPPF` is the principled home
-- and `MPoly` below re-rolls it. I built bespoke because it was the fastest
-- thing to get typechecking, which is a reason and not a justification.
-- ⚑ BUT THE MIGRATION IS NOT A SWAP, and I have NOT worked it out: `SPPF` is a
-- SEMIRING (no negation) while `det Jac F` has negative coefficients, so it
-- needs the negation story first — either `CommutativeRing`'s `neg`
-- (`Polynomial/Graded/FromCommRing.agda:66-71`) or the log/antilog transport
-- (`ExpLogCodec`; `GValueLSpace/Properties.agda:41-56` carries additive
-- inverses to multiplicative ones; `ℤ-power-codec`, `Primes.agda:209`).
-- ⚑ ALSO NOTE the carrier-locality gate fired here on the name `Poly` and
-- pointed at `Category/Poly/` — which is the polynomial FUNCTOR (Positions /
-- Directions), a different object. Renamed to `MPoly`; that resolves the
-- collision but does NOT discharge the reuse debt above.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.JacobianResidue where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)

------------------------------------------------------------------------
-- 0. Local scaffolding (kept local: these are list/Bool utilities, not
--    substrate structures, and importing a `.Properties` here would trip the
--    def/proof separation gate since this module declares `data`).
------------------------------------------------------------------------

data 𝔹 : Set where
  tt ff : 𝔹

and : 𝔹 → 𝔹 → 𝔹
and tt b = b
and ff _ = ff

eqℕ : ℕ → ℕ → 𝔹
eqℕ zero    zero    = tt
eqℕ (suc m) (suc n) = eqℕ m n
eqℕ _       _       = ff

mapL : {A B : Set} → (A → B) → List A → List B
mapL f []       = []
mapL f (x ∷ xs) = f x ∷ mapL f xs

concatMapL : {A B : Set} → (A → List B) → List A → List B
concatMapL f []       = []
concatMapL f (x ∷ xs) = f x ++ concatMapL f xs

-- 0 ∷ 1 ∷ … ∷ n
upto : ℕ → List ℕ
upto zero    = zero ∷ []
upto (suc n) = upto n ++ (suc n ∷ [])

------------------------------------------------------------------------
-- 1. Sparse multivariate polynomials over ℤ in three variables.
--    A term is a monomial xⁱyʲzᵏ with an ℤ coefficient; a polynomial is a list
--    of terms, NOT normalized (like terms are summed only when read off by
--    `coeff`). 204 terms before cancellation — measured — so this computes.
------------------------------------------------------------------------

data Mono : Set where
  mono : ℕ → ℕ → ℕ → Mono

data Term : Set where
  term : Mono → ℤ → Term

MPoly : Set
MPoly = List Term

addM : Mono → Mono → Mono
addM (mono a b c) (mono d e f) = mono (a + d) (b + e) (c + f)

eqM : Mono → Mono → 𝔹
eqM (mono a b c) (mono d e f) = and (eqℕ a d) (and (eqℕ b e) (eqℕ c f))

mulT : Term → Term → Term
mulT (term m c) (term n d) = term (addM m n) (c *ℤ d)

_+P_ : MPoly → MPoly → MPoly
_+P_ = _++_

scaleT : Term → MPoly → MPoly
scaleT t []       = []
scaleT t (u ∷ us) = mulT t u ∷ scaleT t us

_*P_ : MPoly → MPoly → MPoly
[]      *P q = []
(t ∷ p) *P q = scaleT t q ++ (p *P q)

infixl 6 _+P_
infixl 7 _*P_

-- THE COEFFICIENT READ-OFF: sum the coefficients of every term at a monomial.
coeff : Mono → MPoly → ℤ
coeff m []              = 0ℤ
coeff m (term n k ∷ p) with eqM m n
... | tt = k +ℤ coeff m p
... | ff = coeff m p

------------------------------------------------------------------------
-- 2. Formal partial derivatives. ∂/∂v drops terms of v-degree 0 and otherwise
--    decrements the exponent, scaling by it.
------------------------------------------------------------------------

∂x ∂y ∂z : MPoly → MPoly
∂x [] = []
∂x (term (mono zero    b c) k ∷ p) = ∂x p
∂x (term (mono (suc a) b c) k ∷ p) = term (mono a b c) (k *ℤ (+ suc a)) ∷ ∂x p
∂y [] = []
∂y (term (mono a zero    c) k ∷ p) = ∂y p
∂y (term (mono a (suc b) c) k ∷ p) = term (mono a b c) (k *ℤ (+ suc b)) ∷ ∂y p
∂z [] = []
∂z (term (mono a b zero)    k ∷ p) = ∂z p
∂z (term (mono a b (suc c)) k ∷ p) = term (mono a b c) (k *ℤ (+ suc c)) ∷ ∂z p

------------------------------------------------------------------------
-- 3. The map F.
--   F(x,y,z) = ( z(1+xy)³ + y²(1+xy)(4+3xy)
--              , y + 3x(1+xy)²z + 3xy²(4+3xy)
--              , 2x − 3x²y − x³z )
------------------------------------------------------------------------

X Y Z₁ 𝟙P : MPoly
X  = term (mono 1 0 0) 1ℤ ∷ []
Y  = term (mono 0 1 0) 1ℤ ∷ []
Z₁ = term (mono 0 0 1) 1ℤ ∷ []
𝟙P = term (mono 0 0 0) 1ℤ ∷ []

kP : ℤ → MPoly
kP k = term (mono 0 0 0) k ∷ []

u v : MPoly                       -- u = 1+xy ,  v = 4+3xy
u = 𝟙P +P (X *P Y)
v = kP (+ 4) +P (kP (+ 3) *P X *P Y)

f₁ f₂ f₃ : MPoly
f₁ = (Z₁ *P u *P u *P u) +P (Y *P Y *P u *P v)
f₂ = Y +P (kP (+ 3) *P X *P u *P u *P Z₁) +P (kP (+ 3) *P X *P Y *P Y *P v)
f₃ = (kP (+ 2) *P X) +P (kP (-suc 2) *P X *P X *P Y) +P (kP (-suc 0) *P X *P X *P X *P Z₁)

------------------------------------------------------------------------
-- 4. The Jacobian determinant. Rows are ∂F₁, ∂F₂, ∂F₃; the six permutations of
--    S₃ carry their signs (3-cycles even, transpositions odd).
------------------------------------------------------------------------

detJac : MPoly
detJac =
      (∂x f₁ *P ∂y f₂ *P ∂z f₃)                    -- (0,1,2)  +
   +P (∂y f₁ *P ∂z f₂ *P ∂x f₃)                    -- (1,2,0)  +
   +P (∂z f₁ *P ∂x f₂ *P ∂y f₃)                    -- (2,0,1)  +
   +P (kP (-suc 0) *P ∂x f₁ *P ∂z f₂ *P ∂y f₃)     -- (0,2,1)  −
   +P (kP (-suc 0) *P ∂z f₁ *P ∂y f₂ *P ∂x f₃)     -- (2,1,0)  −
   +P (kP (-suc 0) *P ∂y f₁ *P ∂x f₂ *P ∂z f₃)     -- (1,0,2)  −

------------------------------------------------------------------------
-- 5. ⚑ THE WEDGE.  det Jac F = recon q b r  with q = −2, b = 1.
--    `residue` is `r`; `residue-coeffs` DELIVERS it, graded by monomial, over
--    the complete degree box. This is the object the policy forbids discarding.
------------------------------------------------------------------------

residue : MPoly
residue = detJac +P kP (+ 2)          -- det − (−2) = det + 2

box : List Mono
box = concatMapL (λ i →
      concatMapL (λ j →
      mapL       (λ k → mono i j k) (upto 3))
                                     (upto 12))
                                     (upto 9)

-- the residue, read off at every monomial the determinant could occupy.
residue-coeffs : List ℤ
residue-coeffs = mapL (λ m → coeff m residue) box

------------------------------------------------------------------------
-- 6. THE RESULT. The residue vanishes identically, and the constant is −2.
--    Had the residue been nonzero, `residue-coeffs` would exhibit exactly where.
------------------------------------------------------------------------

residue-vanishes : residue-coeffs ≡ mapL (λ _ → 0ℤ) box
residue-vanishes = refl

constant-part : coeff (mono 0 0 0) detJac ≡ -suc 1      -- = −2
constant-part = refl

------------------------------------------------------------------------
-- 7. ⚑ NON-VACUITY POLES. `residue-vanishes` compares two computed lists; if
--    `box` were empty, or `coeff` constantly 0ℤ, it would hold VACUOUSLY and
--    say nothing. These are the refutation poles, shipped as terms.
------------------------------------------------------------------------

lengthL : {A : Set} → List A → ℕ
lengthL []       = zero
lengthL (x ∷ xs) = suc (lengthL xs)

-- (a) the box is the full 10 × 13 × 4 grid — not empty, and complete for the
--     determinant's degrees (x ≤ 9, y ≤ 12, z ≤ 3).
box-is-complete : lengthL box ≡ 520
box-is-complete = refl

-- (b) `coeff` is not constantly zero: f₃ = 2x − 3x²y − x³z really has 2 at x.
coeff-detects : coeff (mono 1 0 0) f₃ ≡ + 2
coeff-detects = refl

-- (c) the determinant is not the zero polynomial (its constant term is −2),
--     so `residue` is a genuine translate rather than 0 + 0.
detJac-nonzero : coeff (mono 0 0 0) detJac ≡ -suc 1
detJac-nonzero = refl

-- (d) THE SHARPEST POLE: the machinery DETECTS a wrong constant. Subtracting
--     −3 instead of −2 leaves a residue of 1 at the origin, not 0 — so
--     `residue-vanishes` is a real constraint, not an artefact of the read-off.
wrong-constant-detected : coeff (mono 0 0 0) (detJac +P kP (+ 3)) ≡ 1ℤ
wrong-constant-detected = refl
