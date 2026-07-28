------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold
--
-- THE FOLD `bezout-poly` over the polynomial EEA trace, plus the fuel-EEA glue
-- (`bezout-cong-b`, `unit-bezout`). TIP: re-exports Base ⊕ Step (its own).
--
-- ⟡mod-content-squeeze (propagation): BezoutFold measured 151MB. A first split left the
-- step-bearing tip at 137, so the char-2 back-substitution step is separated from the
-- fold + fuel-EEA glue. Each part carries its own content over the shared ~90MB floor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold where
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base using (BezoutNthWitness; base-bezout-poly; convCoeff-cong-r; convCoeff-one)

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-assoc to +ℕ-assoc; +-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEAFold using (eea-fold-poly)

open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Step
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

-- the gcd-is-unit base: s·b + 𝟙·u = u (s = 0), the Bézout for the terminal
-- unit remainder.  (The EEA over an irreducible modulus ends here, g = u.)
unit-bezout : (b u : QPoly) → BezoutNthWitness b u u
unit-bezout b u =
  zero-q , (suc zero , (𝟙 ∷ [])) ,
  (λ k → trans (+-identityˡ (convCoeff (𝟙 ∷ []) (proj₂ u) k)) (convCoeff-one (proj₂ u) k))

