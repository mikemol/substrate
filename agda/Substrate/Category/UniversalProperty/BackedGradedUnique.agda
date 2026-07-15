------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedGradedUnique — ⟡C2g-retire-part2 P1a: the graded
-- uniqueness API. The `Determines`-valued uniqueness readings for the graded backings, obtained by
-- INSTANTIATING the witness tower's already-proven tier-free uniqueness engines (NOT by re-porting the
-- flat Set₁ `WitnessUnique`/`solver-unique`).
--
-- `Determines u g` (UPArrowGraded) = `{n}(x) → g x ≡ solve u x` — "any candidate graded map g we can
-- prove agrees with the backing's solve on the generating structure IS the solve." This is exactly the
-- conclusion type of the witness tower's initial-algebra uniqueness (foldR-initial / trace-fold-unique),
-- so the graded backing's `solve` plugs straight in and `Determines` is discharged.
--
-- P1a (this file) attaches the low-risk consumable readings; the unified `UniquenessStencil` instance +
-- Lawvere/divᴸ diagonal grounding is P1b.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.BackedGradedUnique where

open import Substrate.Foundation.Nat using (ℕ; suc; _<_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge
  using (DivStr; Trace; done; more; rem; recon; collapse-fold; trace-fold-unique; ℕ-div)
  renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Algebra.Wedge.BoundedIso using (recon-bounded-unique)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal using (base; step)
open import Substrate.WitnessTower.Wedge.OrientationRigInitial using (RigAlgebra; foldR; foldR-initial; alg)
open import Substrate.WitnessTower.Wedge.OrientationRigInstance using (LehmerRig)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; solve; Determines)
open import Substrate.Category.UniversalProperty.BackedGraded using (arrowᴳ)
open import Substrate.Category.UniversalProperty.OrientationRigBackedGraded using (orientationRig-backedᴳ)
open import Substrate.Category.UniversalProperty.MuBackedGraded using (SomeTraceℕ; mu-backedᴳ)

------------------------------------------------------------------------
-- ① orientation-rig: solve = foldR LehmerRig; uniqueness IS Mac Lane rigidity (foldR-initial) — any g
--    agreeing with (base, step) of the rig algebra on start/◂ IS the solve. Cleanest reading: verbatim.
------------------------------------------------------------------------

orientationRig-determinesᴳ :
  (g : ∀ {n} → LehmerPath n → LehmerPath n) →
  (g start ≡ base (alg LehmerRig)) →
  (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≡ step (alg LehmerRig) (g l) p) →
  Determines (arrowᴳ orientationRig-backedᴳ) g
orientationRig-determinesᴳ g gs gp = foldR-initial LehmerRig g gs gp

------------------------------------------------------------------------
-- ② μ initial-algebra ≡-uniqueness. The preserved theorem (was MuBacked.mu-fold-unique) IS
--    trace-fold-unique specialised to the collapse algebra (base = id, step = drop) — tier-free
--    (Algebra.Wedge), so it re-homes here verbatim; then the packaged `Determines` reading for the
--    graded backing follows by eta on the SomeTrace Σ (mu-solve st = collapse-fold (proj₂³ st)).
------------------------------------------------------------------------

module _ {C : Set} (D : DivStr C) where
  mu-fold-uniqueᴳ :
    (h : {a b g : C} → Trace D a b g → C)
    (h-done : (a : C) → h (done a) ≡ a)
    (h-more : {a g : C} (b : C) (w : Wedge⟦478f66a6⟧ D a b) (tr : Trace D b (rem w) g) →
              h (more b w tr) ≡ h tr) →
    {a b g : C} (t : Trace D a b g) → h t ≡ collapse-fold t
  mu-fold-uniqueᴳ h h-done h-more t = trace-fold-unique (λ a → a) (λ _ _ rec → rec) h h-done h-more t

-- the packaged reading: any bare-trace fold h agreeing with collapse Determines the graded μ solve
-- (which reads the trace out of the SomeTraceℕ Σ).
mu-determinesᴳ :
  (h : {a b g : ℕ} → Trace ℕ-div a b g → ℕ)
  (h-done : (a : ℕ) → h (done a) ≡ a)
  (h-more : {a g : ℕ} (b : ℕ) (w : Wedge⟦478f66a6⟧ ℕ-div a b) (tr : Trace ℕ-div b (rem w) g) →
            h (more b w tr) ≡ h tr) →
  Determines (arrowᴳ mu-backedᴳ) (λ {n} st → h (proj₂ (proj₂ (proj₂ st))))
mu-determinesᴳ h h-done h-more {n} st = mu-fold-uniqueᴳ ℕ-div h h-done h-more (proj₂ (proj₂ (proj₂ st)))

------------------------------------------------------------------------
-- ③ ν-step BOUNDED ≡-uniqueness. The content is exactly the tier-free `recon-bounded-unique`
--    (← divmod-unique): two SMALL wedge witnesses (q,r) to the same value a coincide. This is the
--    flat `wedge-witness-unique` body, migrated verbatim over ℕ × ℕ (the graded ν backing's Sol) —
--    the r<b bound is essential (drop it and (q,r), (q−1,r+b) both decompose a). The frame is the
--    ν-step layer of the µ⊣ν picture (P1b's `ν-step`); the bound is the halting/finite window
--    (unbounded ⇒ the whole-ν coinductive `~`, NuWholeBisim). NOT a `Determines` (which is
--    unconditional) — it is uniqueness RELATIVE TO the smallness admissibility.
------------------------------------------------------------------------

nu-step-uniqueᴳ :
  (a b : ℕ) (t₁ t₂ : ℕ × ℕ) →
  proj₂ t₁ < suc b → proj₂ t₂ < suc b →
  a ≡ recon ℕ-div (proj₁ t₁) (suc b) (proj₂ t₁) →
  a ≡ recon ℕ-div (proj₁ t₂) (suc b) (proj₂ t₂) →
  t₁ ≡ t₂
nu-step-uniqueᴳ a b (q₁ , r₁) (q₂ , r₂) lt₁ lt₂ w₁ w₂ =
  cong₂ _,_ (proj₁ u) (proj₂ u)
  where u = recon-bounded-unique q₁ q₂ b r₁ r₂ lt₁ lt₂ (trans (sym w₁) w₂)
