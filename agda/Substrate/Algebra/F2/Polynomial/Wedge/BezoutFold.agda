------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold
--
-- THE FOLD `bezout-poly` over the polynomial EEA trace, plus the fuel-EEA glue
-- (`bezout-cong-b`, `unit-bezout`). TIP: re-exports Base ⊕ Step (its own).
--
-- ⟡mod-content-squeeze (propagation): BezoutFold measured 151MB. A first split left the
-- step-bearing tip at 137, so the char-2 back-substitution step is separated from the
-- fold +F fuel-EEA glue. Each part carries its own content over the shared ~90MB floor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold where
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base using (BezoutNthWitness; base-bezout-poly; convCoeff-cong-r; convCoeff-one)

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
-- ⚑⚑ AND THE REPLACEMENT `open import …F2.F2` IS ITSELF REMOVED: `F.Over
-- F₂-CommRing` below re-exports the coefficient names (`𝟘 𝟙 _+_` and the ring
-- laws, `FromCommRing:45-79`), so opening the F₂ leaf too gave `𝟙` TWO routes and
-- [AmbiguousName] at :68. Same theorem, two paths — which agda cannot choose
-- between and the ban forbids disambiguating with `using`.
--
-- ⚑ THIS IS THE COHORT FIX, NOT A ONE-OFF: 35 modules apply `F.Over`, and any
-- that also opens an F₂ leaf collides identically. `BezoutFold/Base` was the
-- first; the operator's framing is that the durable answer is to SPLIT
-- `FromCommRing` upstream so bare imports carry individual symbols — at which
-- point `as` becomes permissible for disambiguation. This is the interim.
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEAFold using (eea-fold-poly)

open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Step
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Polynomial.Graded.Laws.Conv
open import Substrate.Algebra.Polynomial.Graded.Base
open import Substrate.Algebra.F2.F2
private variable n m l : ℕ

-- THE FOLD: the Bézout bridge over the polynomial EEA trace.
bezout-poly : {a b g : QPoly} → PolyEEATrace a b g → BezoutNthWitness a b g
bezout-poly t = eea-fold-poly {T = BezoutNthWitness} base-bezout-poly
                  (λ {a} {g} d f-lo rec → step-bezout-poly {a} {g} d f-lo rec) t

------------------------------------------------------------------------
-- glue for the fuel-EEA (the buildable, divisor-q-free path to the inverse):
-- transport a witness across a VALUE-EQUAL divisor (for the trim), and the
-- gcd-is-unit base.
------------------------------------------------------------------------

-- the b-index of a Bézout witness can be swapped for any VALUE-EQUAL poly
-- (same nth) — convCoeff reads its 2nd argument only through nth.
bezout-cong-b : {a b b′ g : QPoly} → ((j : ℕ) → nth (proj₂ b) j ≡ nth (proj₂ b′) j)
              → BezoutNthWitness a b g → BezoutNthWitness a b′ g
bezout-cong-b {a} h (s , t , eq) =
  s , t , (λ k → trans (cong (convCoeff (proj₂ s) (proj₂ a) k +_)
                             (convCoeff-cong-r (proj₂ t) (λ j → sym (h j)) k))
                       (eq k))

-- the gcd-is-unit base: s·b +F 𝟙·u = u (s = 0), the Bézout for the terminal
-- unit remainder.  (The EEA over an irreducible modulus ends here, g = u.)
unit-bezout : (b u : QPoly) → BezoutNthWitness b u u
unit-bezout b u =
  zero-q , (suc zero , (𝟙 ∷ [])) ,
  -- ⚑ `convCoeff …` is a COEFFICIENT (F₂), not a ℕ, so this is the CARRIER's
  -- left-identity — `F.Over`'s `+-identityˡ`, not `+ℕ-identityˡ`. The ban sweep
  -- spelled it ℕ-ward while the ambiguity was hiding the mismatch; removing the
  -- duplicate route exposed it. Bidirectional collapse, exactly as this file's
  -- sibling `Base.agda:48-51` records: only the argument types decide.
  (λ k → trans (+-identityˡ (convCoeff (𝟙 ∷ []) (proj₂ u) k)) (convCoeff-one (proj₂ u) k))

