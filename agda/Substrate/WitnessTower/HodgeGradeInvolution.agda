------------------------------------------------------------------------
-- Substrate.WitnessTower.HodgeGradeInvolution
--
-- CONNECTION LEAF (saturation edge 4<->3): the GRADE-LABEL involution and
-- the SPECTRAL multiplicity COUNT are the two sides of one nullity grading.
--
-- Half (4) — the LABEL side: `WitnessTower.Hodge.dual-grade` is the Hodge ★
-- on grade labels (k ↦ n−k), a structural involution `dual-grade-involution`
-- (★★ = id) at every ambient n. It NAMES the grade and its dual; it counts
-- nothing.
--
-- Half (3) — the COUNT side: the spectral per-factor degree
-- `SpectralCrossCoherent.degΦ p = p ∸ 1` (= `SpectralTower.per-factor-dim`'s
-- machine-checked dim ker Φ_p(σ_p)) and the FaceCount-fibered crossing count
-- `PhiMultiplicity.mult2` together COUNT the cells at each grade: the Φ_p-
-- isotypic nullity factors as `nullity2 = mult2 × degΦ` (the kernel-degree ×
-- multiplicity factorization, `nullity-as-mult×degΦ`). It counts the
-- multiplicity at a grade; it labels nothing.
--
-- The claim of this leaf: these two are coherent on the SAME witness. The
-- load-bearing grade is the middle one — at rung c = 2 (n = 1) the doubled
-- multiplicity `mult2 p 1` REDUCES to `p ∸ 1 = degΦ p`, so the cell-count
-- factor at the pairing rung IS the per-factor degree (`mult2-c2≡degΦ`,
-- `refl`-grade `mult2-c2`/`degΦ` agreement). On the label side that same
-- pairing rung is the Hodge self-dual middle grade: at the n = 4 ambient
-- `dual-grade 4 (grade-2) ≡ grade-2` (`★-fixes-middle`, `refl`) — the Λ²↔Λ²
-- bivector ★ that Hodge.agda §3 names as the concrete n=4 star. So the grade
-- the count picks out (c=2, multiplicand p∸1) and the grade the label fixes
-- (the self-dual middle of n=4) are the same rung of the nullity grading,
-- read once as a count and once as a label. Re-exports both halves; no
-- machinery rebuilt (reuse-before-build).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.HodgeGradeInvolution where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; _∸_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)

-- Half (4): the grade-label Hodge ★ involution.
open import Substrate.WitnessTower.Hodge
  using (dual-grade; dual-grade-involution)

-- Half (3): the spectral per-factor degree and the multiplicity count.
open import Substrate.Algebra.F2.Linear.SpectralCrossCoherent
  using (degΦ; nullity-as-mult×degΦ)
open import Substrate.WitnessTower.PhiMultiplicity
  using (mult2; nullity2; mult2-c2)

------------------------------------------------------------------------
-- 1. RE-EXPORT the two halves verbatim (the connection holds the existing
--    defs side by side; it does not redefine them).
------------------------------------------------------------------------

-- LABEL side: the Hodge ★ grade involution, ★★ = id at every ambient n.
grade-★ : (n : ℕ) → Fin (suc n) → Fin (suc n)
grade-★ = dual-grade

grade-★-involution : (n : ℕ) (i : Fin (suc n)) →
                     grade-★ n (grade-★ n i) ≡ i
grade-★-involution = dual-grade-involution

-- COUNT side: the kernel-degree × multiplicity factorization of the nullity.
nullity-factored : (n c : ℕ) → nullity2 (suc n) c ≡ mult2 (suc n) c * degΦ (suc n)
nullity-factored = nullity-as-mult×degΦ

------------------------------------------------------------------------
-- 2. THE COHERENCE on a shared witness: the count side's pairing rung.
--    At rung c = 2 the doubled multiplicity equals the per-factor degree —
--    the cell-count factor at the pairing grade IS degΦ.
------------------------------------------------------------------------

-- `degΦ p` is `p ∸ 1` definitionally; `mult2 p 1` reduces (mult2-c2) to the
-- same `p ∸ 1`. So the count at the c=2 rung agrees with the per-factor degree.
mult2-c2≡degΦ : (p : ℕ) → mult2 p 1 ≡ degΦ p
mult2-c2≡degΦ p = mult2-c2 p

------------------------------------------------------------------------
-- 3. THE COHERENCE on the LABEL side: the same pairing rung is the Hodge
--    self-dual middle grade. In the n = 4 ambient (Λ²(F₂⁴), the 6 bivectors,
--    Hodge.agda §3) the grade-2 label is ★-fixed: grade-★ 4 (grade-2) ≡
--    grade-2 — the Λ²↔Λ² self-dual middle, the concrete bivector star.
--    (`refl`: dual-grade 4 ⟨2⟩ computes to ⟨2⟩.)
------------------------------------------------------------------------

-- grade 2 as an element of Fin 5 (the grades of the n = 4 ambient).
grade-2₄ : Fin 5
grade-2₄ = suc (suc zero)

★-fixes-middle : grade-★ 4 grade-2₄ ≡ grade-2₄
★-fixes-middle = refl

-- the involution at the fixed middle grade is the trivial witness of (2):
-- ★★ on the self-dual grade returns it, consistent with ★ fixing it.
★-middle-involution : grade-★ 4 (grade-★ 4 grade-2₄) ≡ grade-2₄
★-middle-involution = grade-★-involution 4 grade-2₄
