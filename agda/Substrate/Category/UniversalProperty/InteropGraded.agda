------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.InteropGraded — ⟡C2g-ring: the K₀ ⊗-ring as a Set₀
-- GradedProductOver over the MODULUS grade — THE APEX CASE.
--
-- THE REPLACEMENT for the flat `Interop` (a `record Interop (A B : BackedUP) : Set₁` + `_⊗_∣_` +
-- the extensional `crt-ring-identity : (Z3-backed ⊗ Z5-backed ∣ crt-interop) ≡ crt-backed`). The
-- session's apex insight applied to the ⊗-ring: the residue systems are graded by their MODULUS
-- M (the residues mod M are `Fin M`), and the CRT ⊗ is the Fin-PRODUCT combine
-- `combine : Fin m → Fin n → Fin (m * n)` (the very map the witness tower's factorSwap/remQuot is
-- built on, Foundation.Fin.Combine — so this is built ON the witness tower, per the reframe).
--
-- THE RING IDENTITY IS THE TYPE, not an extensional proof: `[ℤ/3] ⊗ [ℤ/5] = [ℤ/15]` is literally the
-- signature `C 3 → C 5 → C 15` of `_∧_` at 3,5 (3 * 5 reduces to 15). The flat form needed a `refl`
-- witness `crt-ring-identity`; here the identity is the grade arithmetic itself.
--
-- TOTAL, not partial: the flat Interop was PARTIAL (coprimality side-condition). `combine` is TOTAL
-- for ANY m, n — the "partiality IS the content" dissolves into a MEASURED residue: coprime ⇒ combine
-- is a bijection (the CRT iso, remQuot its inverse); shared factors ⇒ non-injective (the graded
-- obstruction). The residue is a DERIVED characterization (remQuot round-trips), not a field — so the
-- carrier stays Set₀ and `_∧_` never blocks.
--
-- ⊕ is NOT re-based: the additive seed was the `List BackedUP` registry, dropped in ⟡C2g-registry —
-- so ⊕-as-++ is moot. Only ⊗ (the multiplicative K₀ structure) re-bases here.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.InteropGraded where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.Combine.Assoc using (combine-assoc)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; GradedAssocOver; u; _∧_)

------------------------------------------------------------------------
-- The modulus-graded residue family: C M = the residues mod M = Fin M (modulus IN the type).
------------------------------------------------------------------------

C : ℕ → Set
C = Fin

------------------------------------------------------------------------
-- The K₀ ⊗-ring: u = the single residue mod 1 (ℤ/1's carrier is Fin 1 = {zero}); _∧_ = the CRT/
-- Fin-product combine. A GradedProductOver over (_*_, 1) — the modulus multiplication IS the grade op.
------------------------------------------------------------------------

⊗-ringᴳ : GradedProductOver _*_ 1 C
⊗-ringᴳ = record { u = zero ; _∧_ = combine }

------------------------------------------------------------------------
-- THE RING IDENTITY, as a TYPE: [ℤ/3] ⊗ [ℤ/5] = [ℤ/15] is the signature C 3 → C 5 → C 15
-- (since 3 * 5 ≡ 15 definitionally). No `refl` witness needed — the grade arithmetic IS the identity.
------------------------------------------------------------------------

crt-productᴳ : C 3 → C 5 → C 15
crt-productᴳ = _∧_ ⊗-ringᴳ

------------------------------------------------------------------------
-- The one generic law: ⊗ is associative up to the *-assoc grade transport. This is EXACTLY
-- Foundation's combine-assoc (the Fin associator, proven arithmetically via toℕ) — the witness
-- tower's ⊗-assoc (OrientationProductLaws) lifts the same lemma to Perm; here it is the ring's law.
------------------------------------------------------------------------

⊗-assoc-ringᴳ : GradedAssocOver *-assoc ⊗-ringᴳ
⊗-assoc-ringᴳ = combine-assoc
