{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalPolishDerivative — ⟡diagonal-polish-derivative:
-- the CB-derivative (isolated-point removal) as the concrete DECREASING derivative D for the
-- CB-rank schema (227), for a Polish space, STAYING AT `Set` and dodging the LimitPoint universe
-- blowup — with NO coinduction, so it builds `--safe --without-K` CLEAN (no --guardedness).
--
-- THE UNIVERSE DODGE (grounded from the repo): the naive "x is a limit point" quantifies over
-- OPENS (Set₁+). The substrate never takes topological limits — convergence is finite observation
-- / bisimilarity, "NOT 'in the limit'". BUT a coinductive RECORD (RealTrace-style) is for a lazy
-- GENERATOR and needs --guardedness. A COMPLETED point of Baire space is just a FUNCTION ℕ → ℕ —
-- plain `Set`, NO coinduction, NO --guardedness. Prefix-agreement is finite index-agreement;
-- accumulation is a sequence of distinct points converging by prefixes. ALL `Set`, --safe clean.
-- (The earlier coinductive `Point` was an over-reach; the guardedness WARNING was the tell.)
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalPolishDerivative where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: D, D-dec, Converges, Accumulates, Distinct. Everything else in these comments — 'the CB-derivative', 'Polish', 'the universe dodge', 'accumulation' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require coincidence with the classical topological CB-derivative (⟡diagonal-polish-faithful).

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; z≤n; s≤s)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)

------------------------------------------------------------------------
-- ① POINTS = BAIRE SPACE ℕ → ℕ (a completed sequence — a FUNCTION, plain Set, NO coinduction).
------------------------------------------------------------------------
Point : Set
Point = ℕ → ℕ

-- prefix-agreement to depth n: agree on all indices below n — FINITE observation, Set, no opens.
_=[_]_ : Point → ℕ → Point → Set
x =[ n ] y = (k : ℕ) → k < n → x k ≡ y k

-- observational convergence: for every depth n, some stage m of the sequence agrees to depth n.
Converges : (ℕ → Point) → Point → Set
Converges s x = (n : ℕ) → Σ ℕ (λ m → s m =[ n ] x)

------------------------------------------------------------------------
-- ② ACCUMULATION (the sequential limit-point notion — valid for Polish/first-countable — at Set,
--    NO opens): x accumulates in S iff some sequence of S-points, each DISTINCT from x, converges.
------------------------------------------------------------------------
Sub : Set₁
Sub = Point → Set

-- observably distinct: differ at SOME finite index (witnessed finitely, Set).
Distinct : Point → Point → Set
Distinct x y = Σ ℕ (λ k → ¬ (x k ≡ y k))

Accumulates : Sub → Point → Set
Accumulates S x = Σ (ℕ → Point) (λ s →
    ((k : ℕ) → S (s k))                 -- the sequence lands in S
  × ((k : ℕ) → Distinct (s k) x)        -- each member observably distinct from x
  × Converges s x)                       -- and converges to x (observationally)

------------------------------------------------------------------------
-- ③ THE CB-DERIVATIVE: D S = {x ∈ S : x accumulates in S} — remove the isolated points.
--    DECREASING (D S ⊆ S) by the first projection. The concrete D for the CB-rank schema (227).
------------------------------------------------------------------------
D : Sub → Sub
D S x = S x × Accumulates S x

D-dec : (S : Sub) (x : Point) → D S x → S x
D-dec S x (x∈S , _) = x∈S

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the CB-derivative concrete at Set, dodging LimitPoint, with NO
-- coinduction so --safe --without-K is CLEAN): the either/or "topological limit-point (opens,
-- Set₁) vs the universe dodge" bottoms out in the substrate's strategy — finite observation, not
-- topological limits. AND the finer either/or "coinductive record (needs --guardedness) vs
-- function (plain Set)" bottoms out: a COMPLETED point is a FUNCTION ℕ → ℕ (Baire), NOT a lazy
-- generator — so NO coinduction, NO --guardedness, --safe --without-K CLEAN. Points are functions
-- (Set); prefix-agreement =[ n ] is finite index-agreement (Set); accumulation is a distinct
-- sequence converging by prefixes (Set); the CB-derivative D S = {x ∈ S : x accumulates in S} is
-- decreasing (D-dec). So D instantiates the 227 CB-rank schema at Set, no universe blowup, no
-- guardedness — the depth-window (226 no-largest) covers the Polish adversary's topological
-- complexity. The guardedness WARNING on the earlier coinductive `Point` was the TELL that the
-- coinduction was an over-reach; the function encoding is the clean form.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the concrete Set-level CB-derivative (D, D-dec) via
-- observational convergence, NO coinduction, --safe --without-K clean, plugging into the 227
-- schema. SCOPED: (a) that this Baire-function model D coincides with the CLASSICAL topological
-- CB-derivative (sequential = topological, first-countability) — ⟡diagonal-polish-faithful; (b)
-- stabilization-existence (227's ⟡diagonal-cb-exists). Borel-rank still distinct (227).
------------------------------------------------------------------------
