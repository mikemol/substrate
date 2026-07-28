------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial
--
-- F₂[x] polynomials over F₂, foundation for Slice B of the EEA-over-
-- term-algebra plan. A polynomial of degree < n is represented as a
-- `Vec F₂ n`: the i-th coefficient lives at position i.
--
-- This reading: `Vector n` ≅ F₂[x]_{<n}, the polynomial ring quotient
-- of F₂[x] by degree-bound n. Polynomial addition is `+ⱽ` (inherited
-- from Vector). Polynomial multiplication is the convolution
-- `(p · q)_k = ⊕_{i+j=k} p_i · q_j`, producing a polynomial of
-- degree < n ℕ+ m for inputs of degree < n and < m.
--
-- Per the structural conversation: F₂[x] IS a Euclidean domain
-- (polynomial division gives quotient + remainder of strictly lower
-- degree). Slice B's eventual polynomial EEA mirrors the Wedge +
-- EEATrace pattern from Substrate.Algebra.Nat.GCD lifted to
-- polynomials.
--
-- This slice lays the polynomial foundation:
--
--   * Polynomial = Vec F₂ n (with n = degree bound)
--   * degree-bound : extract "leading nonzero index + 1" or 0
--   * +P = +ⱽ (alias for polynomial addition)
--   * *P = convolution (polynomial multiplication via shift + add)
--   * x-shift : multiply by x (shift coefficients up by 1)
--   * evaluate : Horner-style evaluation at a F₂ point
--
-- Full polynomial EEA (Wedge-Poly + EEATrace-Poly) is the natural
-- follow-on, opening the dual-code bridge (Code/ImageCode ↔
-- KernelCode via polynomial GCD).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; replicate)
open import Substrate.Foundation.Function using (_∘_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

------------------------------------------------------------------------
-- N-1: Polynomial type.
--
-- A polynomial of degree < n is a Vec F₂ n: the coefficient of x^i
-- lives at position i. The zero polynomial of any degree bound is
-- `𝟎ⱽ`.
--
-- Type alias for readability; the underlying Vec F₂ n machinery
-- (lookup, +ⱽ, etc.) is fully available.
------------------------------------------------------------------------

open import Substrate.Foundation.Vec using (replicate)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-suc) renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Eq using (subst)
Polynomial : ℕ → Set
Polynomial n = Vector n

------------------------------------------------------------------------
-- N-2: Polynomial addition — alias for Vector +ⱽ.
--
-- Polynomial addition over F₂ is componentwise XOR, which IS Vector
-- componentwise +. No new infrastructure needed.
------------------------------------------------------------------------

_+P_ : ∀ {n} → Polynomial n → Polynomial n → Polynomial n
_+P_ = _+ⱽ_

infixl 6 _+P_

------------------------------------------------------------------------
-- N-3: degree-bound — the leading-nonzero-index + 1.
--
-- For a polynomial p : Polynomial n, `degree-bound p` is the smallest
-- k such that all coefficients at positions ≥ k are 𝟘. Conventions:
--
--   * degree-bound 𝟎ⱽ = 0 (zero polynomial)
--   * degree-bound of a polynomial with leading coefficient at
--     position i (and zero above) is i + 1.
--
-- Computed by scanning from the high end. For Vec F₂ n, scan starts
-- at index n-1 and decreases.
------------------------------------------------------------------------

-- Helper: given a Vec, find the position of the highest nonzero
-- coefficient + 1 (or 0 if all coefficients are zero).
-- We scan from the head, tracking the highest seen position.
degree-bound-acc : ∀ {n} → Vec F₂ n → ℕ → ℕ → ℕ
degree-bound-acc []        _   best = best
degree-bound-acc (𝟘 ∷ rest) pos best = degree-bound-acc rest (suc pos) best
degree-bound-acc (𝟙 ∷ rest) pos _    = degree-bound-acc rest (suc pos) (suc pos)

degree-bound : ∀ {n} → Polynomial n → ℕ
degree-bound p = degree-bound-acc p 0 0

------------------------------------------------------------------------
-- N-4: x-shift — multiply by x (= shift coefficients up by 1).
--
-- Given p : Polynomial n representing a₀ + a₁x + ... + a_{n-1}x^{n-1},
-- x-shift p : Polynomial (suc n) representing 0 + a₀x + a₁x² + ...
-- + a_{n-1}x^n. Coefficient at position 0 is 𝟘; coefficients at
-- positions i ≥ 1 are p[i-1].
--
-- Used by polynomial multiplication via partial-product-and-shift.
------------------------------------------------------------------------

x-shift : ∀ {n} → Polynomial n → Polynomial (suc n)
x-shift p = 𝟘 ∷ p

------------------------------------------------------------------------
-- N-5: Scalar multiplication by F₂ — multiplies every coefficient.
--
-- For c : F₂ and p : Polynomial n, c *P p is the polynomial with
-- coefficient c · p[i] at each position i.
--
-- This IS the substrate's `_*ₛ_` from Vector, but with the polynomial
-- naming convention.
------------------------------------------------------------------------

_·c_ : ∀ {n} → F₂ → Polynomial n → Polynomial n
_·c_ = _*ₛ_

infixl 7 _·c_

------------------------------------------------------------------------
-- N-5b: Tensor product factorization of polynomial multiplication.
--
-- Polynomial multiplication factors through the tensor product
-- F₂[x]_{<n} ⊗ F₂[x]_{<m}:
--
--   outer        : F₂[x]_{<n} × F₂[x]_{<m} → F₂[x]_{<n} ⊗ F₂[x]_{<m}
--   anti-diag-sum : F₂[x]_{<n} ⊗ F₂[x]_{<m} → F₂[x]_{<n+m}
--   _*P_         = anti-diag-sum ∘ outer
--
-- The substrate's tensor product representation: `Vec (Polynomial m) n`
-- (n rows of m-vectors) ≅ F₂^(n × m) ≅ Polynomial n ⊗ Polynomial m
-- at the F₂-vector-space level.
--
-- `outer` is the UNIVERSAL bilinear map (Polynomial n × Polynomial m
-- → tensor product); `anti-diag-sum` is the SPECIFIC linear projection
-- from the tensor product to Polynomial (n + m).
--
-- Per the structural conversation: this separates the bilinear-lifting
-- (outer, universal) from the polynomial-specific recombination
-- (anti-diag-sum). Future TensorProduct primitive would make
-- the universal property explicit; for now, outer + anti-diag-sum
-- give the cleaner decomposition than convolution-mashing.
------------------------------------------------------------------------


-- The outer product: the universal bilinear map.
-- Given p : Polynomial n and q : Polynomial m, outer p q : Vec (Polynomial m) n
-- has at row i the polynomial (p_i ·c q).
--
-- No length arithmetic — just nested Vecs.
outer : ∀ {n m} → Polynomial n → Polynomial m → Vec (Polynomial m) n
outer []      q = []
outer (a ∷ p) q = (a ·c q) ∷ outer p q

-- pad-end: append k zeros at the high-position end of a polynomial.
-- Used by anti-diag-sum to align row contributions.
pad-end : ∀ {n} (k : ℕ) → Polynomial n → Polynomial (n ℕ+ k)
pad-end k []      = replicate k 𝟘
pad-end k (x ∷ p) = x ∷ pad-end k p

-- A helper: m ℕ+ suc n' = suc n' ℕ+ m via +-comm, packaged via subst.
shift-to-suc-on-left :
  ∀ {m n'} → Polynomial (m ℕ+ suc n') → Polynomial (suc n' ℕ+ m)
shift-to-suc-on-left {m} {n'} p = subst Polynomial (+ℕ-comm m (suc n')) p

-- Anti-diagonal sum: collapse the n × m tensor to a polynomial of
-- degree < n + m. The specific linear projection.
--
-- Structurally: anti-diag-sum [] gives the zero polynomial at length m;
-- anti-diag-sum (row ∷ rows) places row at low positions and recurses
-- with x-shift to position the rest at higher positions.
--
-- Length arithmetic via subst at the +-comm boundary (pad-end produces
-- m + suc n' shape but we need suc n' + m).
anti-diag-sum : ∀ {n m} → Vec (Polynomial m) n → Polynomial (n ℕ+ m)
anti-diag-sum {.0}       {m} []           = replicate m 𝟘
anti-diag-sum {.(suc _)} {m} (row ∷ rows) =
  -- row : Polynomial m. Pad with (suc n') zeros → Polynomial (m + suc n').
  -- Re-shape to Polynomial (suc n' + m) via +-comm.
  -- x-shift (anti-diag-sum rows) : Polynomial (suc (n' + m)) = Polynomial (suc n' + m).
  -- Sum the two.
  shift-to-suc-on-left (pad-end _ row) +ⱽ x-shift (anti-diag-sum rows)

-- Polynomial multiplication: composition of outer + anti-diag-sum.
_*P_ : ∀ {n m} → Polynomial n → Polynomial m → Polynomial (n ℕ+ m)
_*P_ p q = anti-diag-sum (outer p q)

infixl 7 _*P_

------------------------------------------------------------------------
-- N-6: Polynomial evaluation at a point — Horner's method.
--
-- evaluate p α = a₀ + a₁·α + a₂·α² + ... + a_{n-1}·α^{n-1}.
-- Via Horner: p(α) = a₀ + α·(a₁ + α·(a₂ + α·(...))).
--
-- For F₂: α ∈ {𝟘, 𝟙}; evaluation reduces to specific arithmetic.
------------------------------------------------------------------------

evaluate : ∀ {n} → Polynomial n → F₂ → F₂
evaluate []      _ = 𝟘
evaluate (a ∷ p) α = a + α · evaluate p α

------------------------------------------------------------------------
-- N-7: Capstone — F₂[x] polynomial foundation lands.
--
-- After this slice, F₂[x]_{<n} is a first-class substrate object
-- via the `Polynomial n = Vec F₂ n` reading. Operations:
--
--   * +P (= +ⱽ alias)
--   * ·c (scalar multiplication)
--   * x-shift (multiply by x)
--   * pad-end (extend degree bound by appending high-position zeros)
--   * outer (universal bilinear map; unit of ⊗-Hom adjunction at (p, q))
--   * anti-diag-sum (specific Hom-element giving polynomial structure)
--   * _*P_ = anti-diag-sum ∘ outer (factored via tensor product)
--   * degree-bound (find leading nonzero)
--   * evaluate (Horner at a F₂ point)
--
-- **Categorical reading** — polynomial multiplication via the
-- ⊗-Hom adjunction:
--
-- Tensor product ⊗ is LEFT-ADJOINT to internal-hom in a closed
-- symmetric monoidal category. The homset isomorphism
--
--   Hom(V ⊗ W, U)  ≅  Hom(V, Hom(W, U))  ≅  Bilinear(V × W, U)
--
-- IS the universal property: bilinear maps factor uniquely through
-- the tensor product.
--
-- For polynomial multiplication:
--   outer p q   = unit of ⊗-Hom adjunction at (p, q); the universal
--                 bilinear lifting (p, q) ↦ p ⊗ q.
--   anti-diag-sum = a specific element of Hom(V ⊗ W, Polynomial (n+m));
--                   the linear map chosen by the polynomial algebra
--                   structure.
--   _*P_          = anti-diag-sum ∘ outer; composition through the
--                   homset bijection.
--
-- The "more universal substrative move" the structural conversation
-- pointed at: a future **TensorProduct primitive** (Category #7?)
-- would name this ⊗-Hom adjoint pair categorically. The substrate's
-- existing Adjunction primitive (#4) handles single-argument linear
-- extension; TensorProduct extends it to bilinear / tensor.
--
-- Future primitives in dependency order:
--   * Bivector / exterior algebra (Λ²(V) = antisymmetric quotient
--     of V ⊗ V; substrate's HodgeDim4.Bivector implicitly uses this).
--   * Symmetric algebra (Sym²(V) = symmetric quotient of V ⊗ V;
--     SymBilinForm-n implicitly uses this).
--   * Free algebra (T(V) = full tensor algebra; F₂[x] is a quotient).
--
-- Path to full polynomial EEA:
--
--   1. **Polynomial wedge** (Wedge-Poly): for polynomials p, q (q ≠ 0),
--      define a Wedge structure analogous to ℕ's Wedge:
--        Wedge-Poly p q packages: quotient, remainder, p ≡ quotient *P q +P remainder,
--        degree-bound remainder < degree-bound q.
--
--   2. **Polynomial long division** (construct-wedge-poly):
--      implement the polynomial division algorithm. At each step,
--      subtract (leading-coefficient-ratio) · (q shifted to align
--      with p's leading). At F₂, "leading-coefficient-ratio" is just
--      whether both leading coefficients are 𝟙.
--
--   3. **EEATrace-Poly**: data type for polynomial EEA, mirroring
--      ℕ's EEATrace structure (base + step with wedge).
--
--   4. **compute-trace-poly** (with well-founded recursion on
--      degree-bound).
--
--   5. **gcd-Poly** extraction + divisibility properties (via
--      structural induction on EEATrace-Poly).
--
--   6. **Bezout polynomial coefficients**: structural fold on the
--      polynomial trace.
--
-- Opens the dual-code arc:
--
--   * **ImageCode ↔ KernelCode**: at the polynomial level, an
--     `ImageCode k n` with generator polynomial g(x) corresponds to
--     `KernelCode n (n - k)` with parity-check polynomial
--     `(x^n - 1)/g(x)` (over F₂, x^n + 1 since char 2). The
--     polynomial Bezout coefficients give the explicit isomorphism.
--
--   * **Cyclic codes**: codes of length n that are ideals in
--     F₂[x]/(x^n + 1). Polynomial EEA in this quotient ring is the
--     foundational machinery.
--
--   * **Hamming, RM codes**: cyclic; their generator polynomials
--     have specific factorisations that polynomial EEA can compute.
--
-- Deferred follow-ons (in dependency order):
--
--   * `Substrate.Algebra.F2.Polynomial.Division` — long division
--     algorithm + Wedge-Poly structure.
--   * `Substrate.Algebra.F2.Polynomial.GCD` — EEATrace-Poly +
--     gcd-Poly + Bezout.
--   * `Substrate.Algebra.F2.Code.Dual` — dual-code bridge via
--     polynomial GCD.
--   * `Substrate.Algebra.F2.Code.Cyclic` — cyclic codes as F₂[x] /
--     (x^n + 1) ideals.
--
-- Per [[project-composite-torsion-euler-substrate]]: the F₂[x] EEA
-- is the substrate's natural Euclidean-domain instance; this slice
-- lays the polynomial foundation. The trace+wedge pattern from
-- Slice A (ℕ) translates directly once polynomial division is in
-- place.
------------------------------------------------------------------------
