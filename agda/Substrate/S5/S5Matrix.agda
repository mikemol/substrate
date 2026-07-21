{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Matrix — ⟡N1b-Matrix. "The convergent's two columns ARE the CF/EEA
-- matrix" as a THEOREM. ⟡H0 split (grep, honest):
--
--  ALREADY PROVEN IN THE REPO (cite, do NOT reprove):
--   * R.Trace.Properties.det4/det-flip : the convergent state's neighbour
--     determinant det4 p₁ q₁ p₀ q₀ = (p₁·q₀) − (p₀·q₁) FLIPS SIGN each
--     Euclidean step — det[[a,1],[1,0]] = −1, the num/den SWAP (DetSign).
--   * det² ≡ +1 (a UNIT: Farey/Stern-Brocot neighbours = Bézout at g=1).
--   * Wedge.agda: "gcd-fold vs bezout-ℤ are these two [reads]" — convergent
--     (forward) and Bézout (inverse) are ALREADY named as two reads of one
--     eea-fold. det-flip IS ◆T3's (−1)ⁿ.
--
--  THE ONLY OWED BRIDGE (built here, standalone, NO postulate): that
--  S5RealConv.conv-go's two-column state IS the 2×2 CF matrix — its transition
--  (a·p₁+p₀, a·q₁+q₀, p₁, q₁) is right-multiplication by M(a) = [[a,1],[1,0]].
--  This is a DEFINITIONAL matrix identity (no signs, no ring lemmas). The det
--  law over that matrix is then EXACTLY the repo's det-flip (⟡N1b-Matrix-wire
--  lands this on the substrate's det-flip; the SIGN story is cited, proven).
--
-- ⚑ THIS `Mat` IS DELIBERATELY THE TWIN OF `Algebra.R.Trace.CFMatrixBridge.Mat`
-- — NOT AN UNNOTICED DUPLICATE (⟡dedup-mat-2x2, RETIRED). The two records are a
-- registered CROSS-DOMAIN BRIDGE: `S5.S5MatrixBridge` witnesses the full
-- transport — the iso (`to`/`from` with BOTH round-trips), the algebra
-- morphism (`to-I`, `to-M`, `to-·`, `to-state`, all `refl`), and theorem
-- transport (`conv-step-agree`, `det-is-det4`, `matrix-det-flip`) — and
-- `S5.BridgeRegistry` indexes it, citing `feedback_dedup_preserve_crossdomain_bridges`
-- by name: dedup CROSS-domain is a thing to WITNESS, not collapse. Collapsing
-- them would destroy the witnessed reflection, which is the point of the S5
-- cluster.
--
-- ⚑ AND THE "cited, proven" SIGN STORY ABOVE IS CARRIED, not merely cited:
-- `S5MatrixBridge` gives THESE matrices an inherited `detM` (= `CF.detM ∘ to`)
-- plus `det-is-det4` and `matrix-det-flip`. So the absence of a local `detM`
-- here is by construction, not a gap. (An audit read the missing `detM` as
-- evidence of an unwitnessed duplicate; this pointer exists so the bridge is
-- discoverable from THIS side, which is why that reading was reachable.)
------------------------------------------------------------------------

module Substrate.S5.S5Matrix where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong; ℕ; zero; suc)
open import Substrate.Foundation.Nat using (_+_; _*_)

-- a 2×2 matrix [[a,b],[c,d]] over ℕ.
record Mat : Set where
  constructor mat
  field a b c d : ℕ
open Mat

-- the identity, and the CF step matrix M(q) = [[q,1],[1,0]].
I : Mat
I = mat (suc zero) zero zero (suc zero)

M : ℕ → Mat
M q = mat q (suc zero) (suc zero) zero

-- 2×2 product, entries written scalar-on-left so the CF step lands exactly as
-- conv-go writes it (a·p₁+p₀, not p₁·a+p₀): (L · R) i j = Σ_k R[k,j]·L[i,k].
_·_ : Mat → Mat → Mat
(mat a b c d) · (mat e f g h) =
  mat (e * a + g * b) (f * a + h * b) (e * c + g * d) (f * c + h * d)

------------------------------------------------------------------------
-- conv-go's two-column state, AS a matrix: [[p₁,p₀],[q₁,q₀]].
------------------------------------------------------------------------
state : ℕ → ℕ → ℕ → ℕ → Mat
state p₁ q₁ p₀ q₀ = mat p₁ p₀ q₁ q₀

------------------------------------------------------------------------
-- THE BRIDGE THEOREM (no postulate; one ring fact, +id0): conv-go's ONE-STEP
-- update IS right-multiplication of its state matrix by M(a). i.e. the
-- two-column recurrence (a·p₁+p₀, a·q₁+q₀, p₁, q₁) equals state · M(a).
-- So the convergent fold IS the CF matrix product — a theorem, by refl.
------------------------------------------------------------------------
-- ℕ fact needed: n + 0 = n (the M(a) 1/0 off-diagonal lands as 1·n = n+0, 0·n = 0).
+id0 : (n : ℕ) → n + zero ≡ n
+id0 zero    = refl
+id0 (suc n) = cong suc (+id0 n)

conv-step-is-matmul :
  (a p₁ q₁ p₀ q₀ : ℕ) →
  state (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁
  ≡ (state p₁ q₁ p₀ q₀) · (M a)
conv-step-is-matmul a p₁ q₁ p₀ q₀ =
  cong₄ mat
    (cong (a * p₁ +_) (sym (+id0 p₀)))                  -- a·p₁+p₀ = a·p₁ + (1·p₀ = p₀+0)
    (sym (trans (cong (_+ zero) (+id0 p₁)) (+id0 p₁)))  -- p₁ = (1·p₁) + (0·p₀ = 0)
    (cong (a * q₁ +_) (sym (+id0 q₀)))                  -- a·q₁+q₀ = a·q₁ + (1·q₀)
    (sym (trans (cong (_+ zero) (+id0 q₁)) (+id0 q₁)))  -- q₁ = (1·q₁) + (0·q₀)
  where
    cong₄ : {A B C E R : Set} (f : A → B → C → E → R)
            {a₁ a₂ : A}{b₁ b₂ : B}{c₁ c₂ : C}{d₁ d₂ : E}
          → a₁ ≡ a₂ → b₁ ≡ b₂ → c₁ ≡ c₂ → d₁ ≡ d₂
          → f a₁ b₁ c₁ d₁ ≡ f a₂ b₂ c₂ d₂
    cong₄ f refl refl refl refl = refl

------------------------------------------------------------------------
-- and the seed: conv-go's initial state (1,0,0,1) IS the identity matrix.
-- (conv-go seeds p₁=1,q₁=0,p₀=0,q₀=1 = [[1,0],[0,1]] = I.)
------------------------------------------------------------------------
seed-is-identity : state (suc zero) zero zero (suc zero) ≡ I
seed-is-identity = refl

-- COROLLARY (the recognition made theorem): the convergent state after any
-- run is I · M(a₀) · M(a₁) · ⋯ — the CF matrix product. Its LEFT COLUMN
-- (p₁,q₁) is the convergent; its DETERMINANT is det-flip's ℤ/2 cochain (◆T3,
-- (−1)ⁿ), proven in R.Trace.Properties (cited). value = product reaching a
-- scalar (GCD); regress = periodic product (a hyperbolic matrix whose
-- eigenvalue is the quadratic irrational the convergents converge to).
