------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.NoCollapse
--
-- el-atlas §3, GENERALIZED from Boolean to an arbitrary quotient carrier
-- (el-atlas NEXT.md move #3: "full S3 over arbitrary quotients, not just
-- Boolean") and stated on the substrate's own `Quotient` record. This is
-- the substrate ↔ el-atlas proof-tier join.
--
-- el-atlas's VerdictCrossbar proved ONE instance: `verdict` factors
-- through no quotient onto a single Bool. The general fact is about ANY
-- carrier:
--
--   A quotient that IDENTIFIES two distinctly-judged evidence points
--   cannot carry the verdict. Equivalently: every quotient that `verdict`
--   factors through is at least as fine as the verdict-kernel — the
--   verdict-kernel is the COARSEST faithful quotient (and it is achieved,
--   so the bound is tight, not vacuous).
--
-- The original Boolean theorem (`no-single-rail-quotient`) then drops out
-- as a COROLLARY: Bool has only two elements, so among the three probe
-- points two must collide (pigeonhole), and the general lemma turns that
-- collision into agreement of two distinct verdicts — absurd. Specific
-- from general, with no second proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.NoCollapse where

open import Substrate.Foundation.Bool  using (Bool; true; false)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq    using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Sum   using (_⊎_; inj₁; inj₂)
open import Substrate.Algebra.Quotient using (Quotient; ≈-refl; ≈-sym; ≈-trans)

open import Substrate.Logic.Evidence.Verdict

------------------------------------------------------------------------
-- The kernel of a map: x and y are identified iff they share an image.
-- The kernel of ANY map is an equivalence — a `Quotient` of the source.
------------------------------------------------------------------------

kernel : {Q : Set} → (Evidence → Q) → Evidence → Evidence → Set
kernel f x y = f x ≡ f y

kernel-Quotient : {Q : Set} (f : Evidence → Q) → Quotient Evidence (kernel f)
kernel-Quotient f = record
  { ≈-refl  = λ _ → refl
  ; ≈-sym   = sym
  ; ≈-trans = trans
  }

------------------------------------------------------------------------
-- The verdict-kernel: the equivalence "judged alike". It is a Quotient
-- (instance of the above at f = verdict), and it is FAITHFUL — realized
-- by the pair (verdict, identity-decoder) — so it is a member of the
-- faithful family, making the coarsest-bound below tight.
------------------------------------------------------------------------

verdict-kernel : Evidence → Evidence → Set
verdict-kernel = kernel verdict

verdict-Quotient : Quotient Evidence verdict-kernel
verdict-Quotient = kernel-Quotient verdict

-- (verdict, id) is faithful-for-verdict; its kernel IS verdict-kernel by
-- definition. So verdict-kernel is achieved, not merely a lower bound.
verdict-kernel-achieved : (e : Evidence) → (λ (v : Verdict) → v) (verdict e) ≡ verdict e
verdict-kernel-achieved _ = refl

------------------------------------------------------------------------
-- THE generalization. A quotient `q : Evidence → Q` is "faithful for
-- verdict" when some decoder `d` recovers the verdict: d ∘ q ≡ verdict.
-- Any such quotient REFINES the verdict-kernel: identifying x and y
-- forces their verdicts to agree. Arbitrary carrier Q — no finiteness,
-- no decidability, no use of Q's structure beyond `cong d`.
------------------------------------------------------------------------

faithful-refines-verdict :
  {Q : Set} (q : Evidence → Q) (d : Q → Verdict) →
  (∀ e → d (q e) ≡ verdict e) →
  {x y : Evidence} → kernel q x y → verdict-kernel x y
faithful-refines-verdict q d h {x} {y} qx≡qy =
  trans (sym (h x)) (trans (cong d qx≡qy) (h y))

------------------------------------------------------------------------
-- Contrapositive — the "prohibition" reading: a faithful quotient
-- SEPARATES distinctly-judged evidence (it cannot collapse across a
-- verdict boundary).
------------------------------------------------------------------------

faithful-separates :
  {Q : Set} (q : Evidence → Q) (d : Q → Verdict) →
  (∀ e → d (q e) ≡ verdict e) →
  {x y : Evidence} → (verdict x ≡ verdict y → ⊥) → kernel q x y → ⊥
faithful-separates q d h vneq qx≡qy =
  vneq (faithful-refines-verdict q d h qx≡qy)

------------------------------------------------------------------------
-- Boolean pigeonhole: among any three Bools, some pair is equal.
------------------------------------------------------------------------

two-of-three :
  (a b c : Bool) →
  (a ≡ b) ⊎ ((a ≡ c) ⊎ (b ≡ c))
two-of-three true  true  _     = inj₁ refl
two-of-three false false _     = inj₁ refl
two-of-three true  false true  = inj₂ (inj₁ refl)
two-of-three false true  false = inj₂ (inj₁ refl)
two-of-three true  false false = inj₂ (inj₂ refl)
two-of-three false true  true  = inj₂ (inj₂ refl)

------------------------------------------------------------------------
-- The original el-atlas theorem, now a COROLLARY of the general lemma:
-- `verdict` factors through no quotient onto a single Bool. Two of the
-- three probe points collide in Bool (pigeonhole); `faithful-refines-
-- verdict` turns each collision into agreement of two distinct verdicts.
------------------------------------------------------------------------

no-single-rail-quotient :
  (q : Evidence → Bool) (d : Bool → Verdict) →
  (∀ e → d (q e) ≡ verdict e) → ⊥
no-single-rail-quotient q d h
  with two-of-three (q eP) (q eF) (q eU)
... | inj₁ qP≡qF        = P≢F (faithful-refines-verdict q d h {eP} {eF} qP≡qF)
... | inj₂ (inj₁ qP≡qU) = P≢U (faithful-refines-verdict q d h {eP} {eU} qP≡qU)
... | inj₂ (inj₂ qF≡qU) = F≢U (faithful-refines-verdict q d h {eF} {eU} qF≡qU)
