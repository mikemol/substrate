------------------------------------------------------------------------
-- Substrate.Algebra.F2.Vector.Universal
--
-- M-2.5 of the Cocycles structural-migration plan. The free-module
-- characterisation of Vec F₂ n: the basis vectors form a basis (every
-- vector decomposes uniquely as a linear combination of basis vectors,
-- and basis vectors are orthogonal at distinct indices).
--
-- Content:
--   * sum   : (Fin n → Vector m) → Vector m  (finite indexed sum).
--   * basis-lookup-other : i ≢ j ⇒ lookup (basis i) j ≡ 𝟘.
--   * basis-decomp       : v ≡ sum (λ i → lookup v i *ₛ basis i).
--
-- Together with M-2's `≡-from-lookup` (Vec equality from lookup
-- equality), these make Vec F₂ n a free F₂-module. The pair becomes
-- the precursor to M-3.5 (linear-map extensionality: a linear map's
-- behaviour is determined by its behaviour on basis vectors).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Vector.Universal where

open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Negation.Not

open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans

------------------------------------------------------------------------
-- Finite indexed sum: Σᵢ f i for i : Fin n.
--
-- Folded leftward: sum {0} f = 𝟎ⱽ; sum {n+1} f = f 0 +ⱽ sum (f ∘ suc).
------------------------------------------------------------------------

sum : ∀ {n m} → (Fin n → Vector m) → Vector m
sum {zero}  _ = 𝟎ⱽ
sum {suc _} f = f zero +ⱽ sum (f ∘ suc)

------------------------------------------------------------------------
-- Fin n disequality helpers — pattern-matches on the constructor
-- difference. Used by basis-lookup-other.
------------------------------------------------------------------------

suc-≢ : ∀ {n} {i j : Fin n} → suc i ≡ suc j → i ≡ j
suc-≢ refl = refl

cong-suc-≢ : ∀ {n} {i j : Fin n} → ¬ (i ≡ j) → ¬ (suc i ≡ suc j)
cong-suc-≢ neq eq = neq (suc-≢ eq)

------------------------------------------------------------------------
-- Basis orthogonality: lookup (basis i) j ≡ 𝟘 whenever i ≢ j.
--
-- Together with `basis-lookup-same` (M-2: lookup (basis i) i ≡ 𝟙),
-- this is the structural orthogonality of the basis.
------------------------------------------------------------------------

basis-lookup-other :
  ∀ {n} (i j : Fin n) → ¬ (i ≡ j) → lookup (basis i) j ≡ 𝟘
basis-lookup-other zero    zero    neq = ⊥-elim (neq refl)
basis-lookup-other zero    (suc j) _   = lookup-𝟎 j
basis-lookup-other (suc i) zero    _   = refl
basis-lookup-other (suc i) (suc j) neq =
  basis-lookup-other i j (λ eq → neq (cong suc eq))

------------------------------------------------------------------------
-- Finite F₂-scalar sum.
------------------------------------------------------------------------

sum-F₂ : ∀ {n} → (Fin n → F₂) → F₂
sum-F₂ {zero}  _ = 𝟘
sum-F₂ {suc _} g = g zero +F sum-F₂ (g ∘ suc)

-- Congruence of sum-F₂ over pointwise equality. Promoted to
-- module-level: forward-reference within a `where` block isn't
-- supported in Agda, and this lemma is generic enough to merit
-- its own name.
sum-F₂-cong : ∀ {n} {f g : Fin n → F₂} →
              (∀ i → f i ≡ g i) → sum-F₂ f ≡ sum-F₂ g
sum-F₂-cong {zero}  _  = refl
sum-F₂-cong {suc _} eq = cong₂ _+F_ (eq zero) (sum-F₂-cong (eq ∘ suc))

------------------------------------------------------------------------
-- Sum-lookup: lookup commutes with sum componentwise.
--
-- This is the key auxiliary lemma. From it the atomic decomposition
-- follows pointwise via ≡-from-lookup.
------------------------------------------------------------------------

lookup-sum :
  ∀ {n m} (f : Fin n → Vector m) (j : Fin m) →
  lookup (sum f) j ≡ sum-F₂ (λ i → lookup (f i) j)
lookup-sum {zero}  f j = lookup-𝟎 j
lookup-sum {suc _} f j =
  trans (lookup-+ⱽ (f zero) (sum (f ∘ suc)) j)
        -- ⚑ A SECTION CARRIES THE OPERATOR'S SPELLING TOO.  The decomposed F₂
        -- leaves name it `_+F_`; a whole-module `open import Substrate.Algebra.F2`
        -- used to supply a bare `_+_`.  Same class as `SpectralCycleDim/PlusCancelR`.
        (cong (lookup (f zero) j +F_) (lookup-sum (f ∘ suc) j))

------------------------------------------------------------------------
-- Atomic decomposition: lookup form.
--
-- For j : Fin n, lookup v j ≡ sum-F₂ (λ i → lookup v i · lookup (basis i) j).
-- The RHS singles out i = j (the other terms vanish by basis-lookup-other).
------------------------------------------------------------------------

-- Auxiliary: the sum sum-F₂ (λ i → c i · δᵢⱼ) reduces to c j alone
-- when the only non-zero δᵢⱼ is at i = j. Proved by induction on j.
lookup-decomp-aux :
  ∀ {n} (v : Vector n) (j : Fin n) →
  sum-F₂ (λ i → lookup v i · lookup (basis i) j) ≡ lookup v j
lookup-decomp-aux {suc _} (x ∷ xs) zero =
  -- i = 0 contributes lookup v 0 · 𝟙 = x; i = suc i' contributes
  -- lookup v (suc i') · 𝟘 = 𝟘.
  trans (cong₂ _+F_ (·-identityʳ x) (vanish-suc-from-zero xs))
        (+-identityʳ x)
  where
    -- For the tail terms: lookup (basis (suc i')) zero ≡ 𝟘 by def
    -- (basis (suc i') = 𝟘 ∷ basis i'); each summand is 0; total 0.
    vanish-suc-from-zero :
      ∀ {n} (ys : Vector n) →
      sum-F₂ (λ i → lookup ys i · lookup (basis (suc i)) zero) ≡ 𝟘
    vanish-suc-from-zero []       = refl
    vanish-suc-from-zero (y ∷ ys) =
      trans (cong₂ _+F_ (·-absorbʳ y) (vanish-suc-from-zero ys)) refl
lookup-decomp-aux {suc _} (x ∷ xs) (suc j) =
  -- i = 0 contributes x · lookup 𝟎ⱽ j ≡ x · 𝟘 ≡ 𝟘; recurse on the tail.
  -- ⚑ THE LEFT SECTION, the mirror of :131's right one.  `--at 771283c8~1` shows
  -- the ban commit converted every APPLIED `_+_` to `_+F_` here and missed both
  -- SECTIONS — so the file's operator spelling is right everywhere except where
  -- an argument slot is left open.
  cong-trans (_+F sum-F₂ (λ i → lookup xs i · lookup (basis (suc i)) (suc j)))
             (cong-trans (x ·_) (lookup-𝟎 j) (·-absorbʳ x))
             (trans (+-identityˡ _)
                    (lookup-decomp-aux xs j))

------------------------------------------------------------------------
-- The atomic decomposition itself.
--
-- Every vector equals the sum of (its components × the basis vectors).
-- This is the "every vector is a unique linear combination of basis
-- vectors" property that makes (basis : Fin n → Vector n) a basis.
------------------------------------------------------------------------

basis-decomp :
  ∀ {n} (v : Vector n) →
  v ≡ sum (λ i → lookup v i *ₛ basis i)
basis-decomp v = ≡-from-lookup v (sum (λ i → lookup v i *ₛ basis i)) goal
  where
    goal : (j : _) →
           lookup v j ≡ lookup (sum (λ i → lookup v i *ₛ basis i)) j
    goal j =
      sym-trans (lookup-decomp-aux v j)
      (trans (sym-sum-cong j)
             (sym (lookup-sum (λ i → lookup v i *ₛ basis i) j)))
      where
        sym-sum-cong : ∀ (j : _) →
          sum-F₂ (λ i → lookup v i · lookup (basis i) j) ≡
          sum-F₂ (λ i → lookup ((lookup v i) *ₛ basis i) j)
        sym-sum-cong j = sum-F₂-cong
                           (λ i → sym (lookup-*ₛ (lookup v i) (basis i) j))
