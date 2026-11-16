-- ⟡leibniz-det-sum probe. (--guardedness: outside the library, no .agda-lib flags.)
{-# OPTIONS --safe --without-K --guardedness #-}

module leibniz-det-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.WitnessTower.Enumerate using (Perm; perms; lengthL)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; encode)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.Sn using (enumerate; enumerate-is-perm)
import Substrate.WitnessTower.LeibnizMonomial as LM

-- the semiring machinery — the op-extraction idiom follows Algebra.Semiring.SPPF.
open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (magma)
open import Substrate.Algebra.Monoid    using (semigroup; ε)
open import Substrate.Algebra.Semiring  using (Semiring; +-monoid; *-monoid)

------------------------------------------------------------------------
-- THE DETERMINANT SUM: a SEMIRING (multiplication-centric — native + and *)
-- PLUS the codec's negation for the sign (log/antilog, NOT a fielded ring op).
------------------------------------------------------------------------

module Det (A : Set) (S : Semiring A) where

  private
    _+A_ = Magma._·_ (magma (semigroup (+-monoid S)))
    0A   = ε (+-monoid S)
    _*A_ = Magma._·_ (magma (semigroup (*-monoid S)))
    1A   = ε (*-monoid S)

  open LM.Mono A _*A_ 1A using (Mat; mono)

  -- sum over a finite index set, using the semiring's native additive monoid.
  sumF : {k : ℕ} → (Fin k → A) → A
  sumF {zero}  f = 0A
  sumF {suc k} f = f zero +A sumF (λ i → f (suc i))

  -- The sign's NEGATION is the ExpLogCodec.Inverse interface: `neg` justified by
  -- `invˡ : x ⊕ neg x ≡ 𝟘` — the additive inverse TRANSPORTED by exp, not added
  -- to the carrier. `invˡ` is not used computationally; it is the typed
  -- obligation that keeps the negation codec-sourced (Route B).
  module WithSign (neg  : A → A)
                  (invˡ : (x : A) → (x +A neg x) ≡ 0A) where

    -- interpret the mod-2 sign: even ↦ +, odd ↦ the transported negation.
    signVal : F₂ → A → A
    signVal 𝟘 x = x
    signVal 𝟙 x = neg x

    -- det M = Σ_{σ ∈ Sₙ} sign(σ) · Πⱼ M[j, σ j].
    det : {n : ℕ} → Mat n → A
    det {n} M = sumF {lengthL (perms n)}
      (λ i → signVal (signF (enumerate n i))
                     (mono (encode (enumerate n i) (enumerate-is-perm n i)) M))

------------------------------------------------------------------------
-- POLE at ℤ: the ring is (ℤ-semiring) + (-ℤ_, +ℤ-inverseʳ). The latter is
-- EXACTLY the codec's invˡ (Semiring.Instances.Z §4 `ℤ-additive-inverse`).
------------------------------------------------------------------------

open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-inverseʳ)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring)

open Det ℤ ℤ-semiring
open Det.WithSign ℤ ℤ-semiring -ℤ_ +ℤ-inverseʳ
open LM.Mono ℤ (Magma._·_ (magma (semigroup (*-monoid ℤ-semiring)))) (ε (*-monoid ℤ-semiring)) using (Mat)

-- M2 = [[2,3],[5,7]]; det = 2*7 - 3*5 = 14 - 15 = -1.
M2 : Mat 2
M2 zero                   = + 2
M2 (suc zero)             = + 3
M2 (suc (suc zero))       = + 5
M2 (suc (suc (suc zero))) = + 7

det-M2 : det {2} M2 ≡ -suc 0
det-M2 = refl

-- M3 = [[1,2,3],[4,5,6],[7,8,10]]; det = -3.
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
