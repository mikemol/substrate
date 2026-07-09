{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalObsCode — ⟡diagonal-obs-code: tie 233's plural
-- observer (Obs, a Pred × S coalgebra) to 234's Final.Coalg (S → ℕ × S) VIA A CODE for the slice
-- — REUSING the repo's number-theoretic workhorses, NOT a hand-rolled Gödel-pairing.
--
-- GROUNDED (read the Agda, per the reground): (1) the RealTrace observation IS ALREADY a ℕ — the
-- CF digit = "the Euclidean quotient at this step" (DivStr / Gauss-map). The observation channel
-- of Final.Coalg is natively a ℕ obtained by DIVISION. (2) CRT.CRT-Witness.combine : ℕ × ℕ → ℕ is
-- the PAIRING (with modular-projection laws combine-mod-m/n for recovery) — the repo's ℕ×ℕ→ℕ code,
-- pluggable over the witness (the 230 parametric habit). So the "code for the plural slice" is:
--   * a SINGLETON slice {n} (233's `ahead`) → the digit n itself (DivStr-native, no pairing);
--   * a PAIR slice (n₁,n₂) → CRT.combine (the repo's coprime pairing).
-- The coded observer is then a Final.Coalg, so observe = Final.ana and finality (ana-unique, 234)
-- applies UNCHANGED. We commit to no coding up front — it is a PARAMETER (as the adjunction was
-- in 230). No fresh pairing; no Set₁.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalObsCode where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: Coded, coded, observe-coded, slice-recovered, Singleton, codePair. Everything else in these comments — 'closes 233→234', 'the code for the plural slice' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the CRT full round-trip under coprime bounds (⟡diagonal-obs-code-crt-roundtrip).

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.R.Trace using (RealTrace)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness; combine)

------------------------------------------------------------------------
-- ① THE CODE IS A PARAMETER (pluggable, per 230): a slice type `Slice`, its code into ℕ, and its
--    recovery. We commit to no representation — the caller supplies the coding. The Final.Coalg's
--    ℕ-channel then carries the coded slice, and observe = Final.ana of the coded coalgebra.
------------------------------------------------------------------------
module Coded
  (Slice   : Set)                        -- the plural prediction-slice (233's Pred, or any finite form)
  (encode  : Slice → ℕ)                  -- its code into the observation ℕ (DivStr digit / CRT.combine)
  (decode  : ℕ → Slice)                  -- recovery
  (rt      : (s : Slice) → decode (encode s) ≡ s)   -- round-trip: the code is faithful
  where

  -- a plural observer (Pred × S = Slice × S) coalgebra becomes a Final.Coalg by CODING the slice.
  coded : {S : Set} → (S → Slice × S) → Coalg S
  coded c s = encode (proj₁ (c s)) , proj₂ (c s)

  -- so its behaviour IS Final.ana of the coded coalgebra — finality (234 ana-unique) applies.
  observe-coded : {S : Set} → (S → Slice × S) → S → RealTrace
  observe-coded c = ana (coded c)

  -- the slice is RECOVERED from the observation (the code round-trips): decode ∘ (fst ∘ coded) = fst ∘ c.
  slice-recovered : {S : Set} (c : S → Slice × S) (s : S)
                  → decode (proj₁ (coded c s)) ≡ proj₁ (c s)
  slice-recovered c s = rt (proj₁ (c s))

------------------------------------------------------------------------
-- ② CONCRETE CODINGS (non-vacuity, the repo's discharge-with-instance habit, 230):
--    (a) the SINGLETON slice {n} (233's `ahead`) codes as the digit n itself — DivStr-native,
--        NO pairing. Slice = ℕ, encode = id, decode = id, round-trip = refl.
------------------------------------------------------------------------
module Singleton = Coded ℕ (λ n → n) (λ n → n) (λ _ → refl)

--    (b) a PAIR slice codes via CRT.combine (the repo's coprime pairing), given a witness. The
--        recovery is modular (combine-mod-m/n); here we expose the pairing as the encode — the
--        faithful (full) round-trip needs coprime bounds (⟡diagonal-obs-code-crt-roundtrip), so
--        we scope decode/rt to the caller and provide the ENCODE wiring, which is the reuse point.
codePair : {m n : ℕ} → CRT-Witness m n → (ℕ × ℕ) → ℕ
codePair w = combine w

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the code is a PARAMETER, and its instances are the repo's DivStr
-- digit + CRT pairing; the coded observer is a Final.Coalg so finality is UNCHANGED): the either/or
-- "invent a Gödel-coding for the plural slice, or stay stuck with a Pred×S functor that Final does
-- not cover" dissolves — the observation channel of Final.Coalg is ALREADY a ℕ (the CF digit, a
-- DivStr quotient), and CRT.combine is ALREADY the ℕ×ℕ→ℕ pairing. So the slice-code is a PARAMETER
-- (Coded), instantiated by the repo's workhorses: the singleton by the digit itself (id, refl),
-- a pair by CRT.combine. Then observe-coded = Final.ana (coded c) and 234's finality (ana-unique)
-- applies with NO change — the plural observer's behaviour is characterised up to ~, coded into the
-- ℕ-observation the repo already consumes. No fresh pairing was built; the coding is DivStr + CRT.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the coding PARAMETER (Coded) + observe-coded = ana ∘
-- coded + slice-recovered (the round-trip), with the SINGLETON instance concrete (id, refl,
-- reusing that the CF digit IS the code) and the PAIR encode = CRT.combine (the repo's pairing).
-- SCOPED: (a) the CRT-pairing FULL round-trip (decode via combine-mod-m/n needs coprime bounds on
-- the slice components) — ⟡diagonal-obs-code-crt-roundtrip; (b) a coding of the GENERAL ℕ→Bool
-- slice (infinite) is impossible as a single ℕ — only FINITE slices code, which is exactly what
-- 233's observer produces per step (singleton/finite), so the restriction is honest, not a gap.
-- What's grounded: the coding is the repo's DivStr digit + CRT pairing, parametric, no reinvention.
------------------------------------------------------------------------
