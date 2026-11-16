------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.Instances
--
-- Concrete instantiations of the dormant `Semiring` record at the
-- four "job gauges" of the semiring-VM layer (conjecture #6,
-- scratch/commuting_sphere.md):  one tensor over a chosen semiring
-- *is* the job gauge.
--
--   * ℕ            — the COUNTING gauge   (ℕ+ , * , 0 , 1)
--   * F₂           — the GF(2)/CARRIER gauge (XOR , AND , 𝟘 , 𝟙)
--   * Bool         — the ROUTING gauge   (∨ , ∧ , false , true)
--   * ℕ∞ (tropical)— the COST/PLACEMENT gauge (min , ℕ+ , ∞ , fin 0)
--
-- The semiring records are *packaging* moves over laws proven
-- elsewhere (Foundation.Nat.Properties.*, Algebra.F2, and — for the
-- Bool routing laws, which had no prior home — small exhaustive
-- case-splits in §3 below).  Nothing is postulated.
--
-- F₂'s Semiring already lives at Substrate.Algebra.F2.AsField
-- (F₂-Semiring); it is re-exported here so that all four gauges sit
-- behind one import.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.Instances where


open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Magma
open import Substrate.Algebra.Semigroup

------------------------------------------------------------------------
-- 0. The shared costructure: build a Monoid from carrier ℕ+ op ℕ+ ε
--    ℕ+ the three laws.  Used 6× below (one additive ℕ+ one
--    multiplicative monoid for each of ℕ, Bool, ℕ∞).
------------------------------------------------------------------------

mk-monoid :
  {A : Set}
  (op : A → A → A)
  (e  : A)
  (assoc : (a b c : A) → op (op a b) c ≡ op a (op b c))
  (idˡ : (a : A) → op e a ≡ a)
  (idʳ : (a : A) → op a e ≡ a)
  → Monoid A
mk-monoid op e assoc idˡ idʳ = record
  { semigroup = record { magma = record { _·_ = op } ; ·-assoc = assoc }
  ; ε         = e
  ; ε-left    = idˡ
  ; ε-right   = idʳ
  }

------------------------------------------------------------------------
-- 1. ℕ — the counting gauge.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-identityˡ; *-identityʳ;
         *-distribˡ-+; *-distribʳ-+; *-zeroˡ; *-zeroʳ)

ℕ-+-Monoid : Monoid ℕ
ℕ-+-Monoid = mk-monoid _ℕ+_ zero +ℕ-assoc +ℕ-identityˡ +ℕ-identityʳ

ℕ-*-Monoid : Monoid ℕ
ℕ-*-Monoid = mk-monoid _*_ (suc zero) *-assoc *-identityˡ *-identityʳ

ℕ-semiring : Semiring ℕ
ℕ-semiring = record
  { +-monoid          = ℕ-+-Monoid
  ; *-monoid          = ℕ-*-Monoid
  ; distrib-left      = *-distribˡ-+
  ; distrib-right     = λ a b c → *-distribʳ-+ c a b
  ; zero-absorb-left  = *-zeroˡ
  ; zero-absorb-right = *-zeroʳ
  }

------------------------------------------------------------------------
-- 2. F₂ — the GF(2)/carrier gauge.
--
-- The full Semiring (in fact Field) instance already exists; we
-- simply re-export it so all four gauges are reachable here.
------------------------------------------------------------------------


------------------------------------------------------------------------
-- 2b. POLYNOMIAL Semiring — pointer (not re-exported: would cycle here,
--     since MPolySemiring imports this module for `mk-monoid`).
--
-- The only in-tree Semiring on MULTIVARIATE (3-variable) ℤ-polynomials in
-- sorted/combined/no-zero-coeff normal form, with a faithful `coeff`
-- semantics, is `NormPoly-Semiring : Semiring NormPoly` at
--     Substrate.Algebra.Z.MPolySemiring
-- (built for the Jacobian-counterexample native determinant,
-- ⟡jac-poly-semiring). Reuse it there rather than rebuilding a polynomial
-- Semiring. (The univariate Vec-backed `Algebra.Polynomial.Graded` rings and
-- the F₂[x] ring are different structures — see that module's header.)
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 3. Bool — the routing gauge.
--
-- additive = ∨ (ε = false), multiplicative = ∧ (ε = true).  (Ⓓ: these Bool
-- laws now live at the Bool carrier home, Foundation.Bool.Properties — they
-- were proven here "for lack of a prior home", but 4 already lived there and
-- the other 6 belong there too. Imported below, then packaged into the records.)
------------------------------------------------------------------------

open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Properties.AndAssoc
open import Substrate.Foundation.Bool.Properties.AndDistribLOr
open import Substrate.Foundation.Bool.Properties.AndDistribROr
open import Substrate.Foundation.Bool.Properties.AndIdentityL
open import Substrate.Foundation.Bool.Properties.AndIdentityR
open import Substrate.Foundation.Bool.Properties.AndZeroL
open import Substrate.Foundation.Bool.Properties.AndZeroR
open import Substrate.Foundation.Bool.Properties.OrAssoc
open import Substrate.Foundation.Bool.Properties.OrIdentityL
open import Substrate.Foundation.Bool.Properties.OrIdentityR

Bool-∨-Monoid : Monoid Bool
Bool-∨-Monoid = mk-monoid _∨_ false ∨-assoc ∨-identityˡ ∨-identityʳ

Bool-∧-Monoid : Monoid Bool
Bool-∧-Monoid = mk-monoid _∧_ true ∧-assoc ∧-identityˡ ∧-identityʳ

Bool-semiring : Semiring Bool
Bool-semiring = record
  { +-monoid          = Bool-∨-Monoid
  ; *-monoid          = Bool-∧-Monoid
  ; distrib-left      = ∧-distribˡ-∨
  ; distrib-right     = ∧-distribʳ-∨
  ; zero-absorb-left  = ∧-zeroˡ
  ; zero-absorb-right = ∧-zeroʳ
  }

------------------------------------------------------------------------
-- 4. ℕ∞ tropical (min-plus) — the cost/placement gauge.
--
-- additive = min (ε = ∞), multiplicative = ⊕ = +∞ (ε = fin 0).
-- Carrier ℕ+ laws live in Substrate.Algebra.Semiring.NatInf.
------------------------------------------------------------------------

open import Substrate.Algebra.Semiring.NatInf
  using (ℕ∞; fin; ∞; _⊓_; _⊕_;
         ⊓-assoc; ⊓-identityˡ; ⊓-identityʳ;
         ⊕-identityˡ; ⊕-distribˡ-⊓; ⊕-absorbˡ; ⊕-absorbʳ)
open import Substrate.Algebra.Semiring.NatInf.Properties
  using (⊕-assoc; ⊕-identityʳ; ⊕-distribʳ-⊓)
open import Substrate.Foundation.Nat.Nat
  renaming (zero to ℕzero)

ℕ∞-⊓-Monoid : Monoid ℕ∞
ℕ∞-⊓-Monoid = mk-monoid _⊓_ ∞ ⊓-assoc ⊓-identityˡ ⊓-identityʳ

ℕ∞-⊕-Monoid : Monoid ℕ∞
ℕ∞-⊕-Monoid = mk-monoid _⊕_ (fin ℕzero) ⊕-assoc ⊕-identityˡ ⊕-identityʳ

tropical-semiring : Semiring ℕ∞
tropical-semiring = record
  { +-monoid          = ℕ∞-⊓-Monoid
  ; *-monoid          = ℕ∞-⊕-Monoid
  ; distrib-left      = ⊕-distribˡ-⊓
  ; distrib-right     = ⊕-distribʳ-⊓
  ; zero-absorb-left  = ⊕-absorbˡ
  ; zero-absorb-right = ⊕-absorbʳ
  }
