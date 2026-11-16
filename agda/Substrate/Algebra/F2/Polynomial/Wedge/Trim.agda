------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.Trim  (B-COMPUTE, the trim)
--
-- Present an F₂[x] polynomial as its MONIC exact-degree form (trailing zeros
-- removed), or as the zero poly.  This is what lets the EEA divide by a
-- varying-degree divisor: `divmod` needs the divisor monic of exact degree
-- (as `(d, f-lo)`), but division remainders carry trailing zeros.
--
-- The trim is STRUCTURAL recursion on the length (strip a trailing 𝟘 via
-- `vlast`/`vinit`, recurse) — NOT a `leading-position : Maybe ℕ` read, so no
-- dependent-length friction.  Correctness is value-equality (`nth`), since
-- removing trailing zeros doesn't change the polynomial — `nth-snoc-zero`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.Trim where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
-- ⚑ NOTE the OTHER `as` aliases in this file (`F`/`M`/`Q`/`D` below) are NOT the
-- same class: they name live PARAMETERIZED modules and the alias is load-bearing
-- (`F.Over`, `M.Over …`).  Only an alias pointing at a RETIRED module is this
-- transform's business.
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D
-- generic (f-lo-independent) vector ops from a dummy instance.
open F.Over F₂-CommRing using (Poly; nth)
open M.Over F₂-CommRing 0 (𝟘 ∷ []) using (vinit; vlast)
open D.Over F₂-CommRing 0 (𝟘 ∷ []) using (snoc; snoc-vinit-vlast; nth-snoc-zero)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

-- the trimmed presentation: all-zero, or a monic poly of exact degree with the
-- SAME coefficients (value-equal, trailing zeros removed).
data Trim {n : ℕ} (r : Poly n) : Set where
  is-zero  : ((k : ℕ) → nth r k ≡ 𝟘) → Trim r
  is-monic : (e : ℕ) (rr : Poly (suc e)) → vlast rr ≡ 𝟙
           → ((k : ℕ) → nth rr k ≡ nth r k) → Trim r

nth-[] : (k : ℕ) → nth {0} [] k ≡ 𝟘
nth-[] zero    = refl
nth-[] (suc k) = refl

-- stripping a trailing 𝟘 (vlast r = 𝟘) leaves the coefficients unchanged.
nth-strip : {n : ℕ} (r : Poly (suc n)) → vlast r ≡ 𝟘
          → (k : ℕ) → nth r k ≡ nth (vinit r) k
nth-strip r eq k =
  trans (cong (λ z → nth z k) (trans (sym (snoc-vinit-vlast r)) (cong (snoc (vinit r)) eq)))
        (nth-snoc-zero (vinit r) k)

-- THE TRIM: strip trailing zeros by structural recursion on the length.
trim : (n : ℕ) (r : Poly n) → Trim r
trim zero    []      = is-zero nth-[]
trim (suc n) r with vlast r in eq
... | 𝟙 = is-monic n r eq (λ k → refl)
... | 𝟘 with trim n (vinit r)
...   | is-zero h           = is-zero (λ k → trans (nth-strip r eq k) (h k))
...   | is-monic e rr hm hc = is-monic e rr hm (λ k → trans (hc k) (sym (nth-strip r eq k)))
