{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.LeibnizDet — ⟡leibniz-det-sum.
--
-- THE DETERMINANT AS THE SIGNED SUM OF LEIBNIZ MONOMIALS:
--
--     det M  =  Σ_{σ ∈ Sₙ}  sign(σ) · Πⱼ M[j, σ j]
--
-- The monomial `Πⱼ M[j, σ j]` is `LeibnizMonomial.mono` (the LehmerAlgebra
-- fold, ⟡leibniz-det-alg); this module supplies the enumeration, the sign, and
-- the sum. Each summand is `mono (encode σ) M` at one permutation, and Sₙ is
-- walked by the tower's own enumeration `Sn.enumerate` (Fin (n!) ≅ Sₙ).
--
-- ⚑ THE SIGN IS MULTIPLICATIVE — μ₂, NOT FIELDED NEGATION. The substrate is
-- MULTIPLICATION-CENTRIC: the four job gauges (ℕ/F₂/Bool/tropical) are SEMIRINGS
-- with no additive inverse. The sign character is a homomorphism Sₙ → {±1}, and
-- {±1} = μ₂ is the MULTIPLICATIVE order-2 subgroup — the square roots of unity.
-- So the summand's ± is NOT "negate x"; it is "multiply x by ε₂", where ε₂ is
-- the order-2 root of unity. And ε₂ is obtained multiplication-centrically:
-- log to the additive side, HALVE the period (div-by-two — the order-2 element
-- sits at the halfway point of the multiplicative cycle: g^(period/2)), antilog
-- back. It is the sign codec `(−1)^·` at base (−1,−1) (`JacobianNegCodec` §4).
-- `Det` therefore takes:
--   · a `Semiring A` — the NATIVE `+`/`*`; the SUM uses `+`, the MONOMIAL uses
--     `*`; nothing is added to the carrier; and
--   · the root of unity `ε₂ : A` with `ε₂ *A ε₂ ≡ 1A` — the multiplicative
--     order-2 witness. The sign is applied as `ε₂ *A x`, a MULTIPLICATION.
-- So there is no negation operation anywhere: the "minus" of the alternating
-- sum is a multiplication by a square root of unity. (The additive monoid must
-- still CONTAIN the negatives as elements for the sum to land — ℤ's does, ℕ's
-- does not — but that is a property of the carrier, not a fielded `neg`.)
--
-- ⚑ `ε₂-sq` IS A TYPED OBLIGATION, NOT USED COMPUTATIONALLY. `det` uses only
-- `ε₂ *A x` (for odd summands). `ε₂ *A ε₂ ≡ 1A` is required so the module CANNOT
-- be instantiated with an `ε₂` that is not a genuine order-2 root of unity —
-- the same discipline the codec's `Inverse`/`Vacuity` poles follow.
--
-- ⚑ THE SIGN HALF WAS ALREADY PROVEN — this module CONSUMES it, adds none.
-- `signF = bool→F₂ ∘ sign` (TowerCocycleGraded), and any ◂-respecting mod-2
-- character IS signF ∘ decode (`SignUniqueCharacter.sign-unique-◂-character`).
-- ⟡leibniz-det-alg kept the sign OUT of the monomial as a graded residue; here
-- it is spent, through the codec, into ±1 per summand.
--
-- ⚑ WHAT THIS DOES NOT YET PROVE (labelled, not smuggled):
--   ⟡leibniz-det-of-perm-matrix — det (P σ) ≡ sign σ, which would CLOSE a
--     boundary the substrate states outright today:
--     `OrientationRigCatPermSignChirality:8-13` — "det(P_σ) = sign(σ) is a
--     NAME-COINCIDENCE here: the substrate has NO permutation matrix and NO
--     Leibniz determinant… We do NOT build a fake permutation determinant."
--     With `det` now defined, that identity is a genuine target; when it lands,
--     that header stops being a disclaimer. (Det properties needing +-comm —
--     multilinearity, det of a transpose — are also out of scope: `Det` takes a
--     plain `Semiring`, whose `+` need not be commutative for the DEFINITION.)
--
-- POLES: concrete determinants at ℤ, by `refl` — the 2×2 (`2·7 − 3·5 = −1`) and
-- a full 3×3 (all six signed terms, `−3`). Grade 3 exercises the whole
-- enumerate/encode/mono/sign/sum pipeline, not just a 2-term cancellation.
--
-- Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.WitnessTower.LeibnizDet where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.WitnessTower.Enumerate using (perms; lengthL)
open import Substrate.WitnessTower.LehmerPath using (encode)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.Sn using (enumerate; enumerate-is-perm)
import Substrate.WitnessTower.LeibnizMonomial as LM

-- the semiring machinery — the op-extraction idiom follows Algebra.Semiring.SPPF.
open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (magma)
open import Substrate.Algebra.Monoid    using (semigroup; ε)
open import Substrate.Algebra.Semiring  using (Semiring; +-monoid; *-monoid)

------------------------------------------------------------------------
-- 1. THE DETERMINANT SUM.
------------------------------------------------------------------------

module Det (A : Set) (S : Semiring A) where

  private
    _+A_ = Magma._·_ (magma (semigroup (+-monoid S)))
    0A   = ε (+-monoid S)
    _*A_ = Magma._·_ (magma (semigroup (*-monoid S)))
    1A   = ε (*-monoid S)

  -- the monomial reader, reused from ⟡leibniz-det-alg over this semiring's
  -- MULTIPLICATIVE monoid (the *-monoid — the monomial needs only a monoid).
  open LM.Mono A _*A_ 1A public using (Mat; mono)

  -- the sum over a finite index set, using the semiring's native ADDITIVE monoid.
  sumF : {k : ℕ} → (Fin k → A) → A
  sumF {zero}  f = 0A
  sumF {suc k} f = f zero +A sumF (λ i → f (suc i))

  ------------------------------------------------------------------------
  -- 2. THE SIGN AS MULTIPLICATION BY μ₂. `ε₂` is the multiplicative order-2
  --    root of unity (log / div-by-two / antilog); the sign multiplies by it.
  ------------------------------------------------------------------------

  module WithSign (ε₂    : A)
                  (ε₂-sq : (ε₂ *A ε₂) ≡ 1A) where

    -- even ↦ x, odd ↦ ε₂ · x (multiply by the order-2 root of unity).
    signVal : F₂ → A → A
    signVal 𝟘 x = x
    signVal 𝟙 x = ε₂ *A x

    -- det M = Σ_{σ ∈ Sₙ} sign(σ) · Πⱼ M[j, σ j], Sₙ walked by Sn.enumerate.
    det : {n : ℕ} → Mat n → A
    det {n} M = sumF {lengthL (perms n)}
      (λ i → signVal (signF (enumerate n i))
                     (mono (encode (enumerate n i) (enumerate-is-perm n i)) M))

------------------------------------------------------------------------
-- 3. NON-VACUITY POLES at ℤ.
--
-- The order-2 root of unity is ℤ's −1, `-suc 0`, and its `ε₂-sq` obligation
-- `(-suc 0) *ℤ (-suc 0) ≡ + 1` is DISCHARGED BY THE SEMIRING INSTANCE'S OWN
-- WITNESS — `Semiring.Instances.Z` §4 `mul-sign-computes`, which is there
-- precisely as "the SIGN rule (−1)·(−1) = 1". So the sign the determinant
-- spends here IS the semiring's own μ₂, applied by multiplication — no negation
-- operation enters. ℤ's additive monoid supplies the summation and contains the
-- negatives; nothing is fielded onto the carrier.
--
-- (WitnessTower → Algebra.Z is an established edge — cf. EEAFoldTable,
-- EEAUnitBezout — so the pole is homed here rather than off in Algebra.Z.)
------------------------------------------------------------------------

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring; mul-sign-computes)

open Det ℤ ℤ-semiring using (Mat)
open Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det)

-- M2 = [[2,3],[5,7]]; det = 2·7 − 3·5 = 14 − 15 = −1.
M2 : Mat 2
M2 zero                   = + 2
M2 (suc zero)             = + 3
M2 (suc (suc zero))       = + 5
M2 (suc (suc (suc zero))) = + 7

det-M2 : det {2} M2 ≡ -suc 0
det-M2 = refl

-- M3 = [[1,2,3],[4,5,6],[7,8,10]]; det = 1(50−48) − 2(40−42) + 3(32−35) = −3.
-- All six signed 3×3 terms — the full enumerate/encode/mono/sign/sum pipeline.
M3 : Mat 3
M3 zero                                     = + 1
M3 (suc zero)                               = + 2
M3 (suc (suc zero))                         = + 3
M3 (suc (suc (suc zero)))                   = + 4
M3 (suc (suc (suc (suc zero))))             = + 5
M3 (suc (suc (suc (suc (suc zero)))))       = + 6
M3 (suc (suc (suc (suc (suc (suc zero)))))) = + 7
M3 (suc (suc (suc (suc (suc (suc (suc zero))))))) = + 8
M3 (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))) = + 10

det-M3 : det {3} M3 ≡ -suc 2
det-M3 = refl
