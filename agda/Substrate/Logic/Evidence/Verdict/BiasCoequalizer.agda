------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.BiasCoequalizer
--
-- THE non-refl coequalizer of the verdict tier, backed for the registry.
--
-- `verdict : Evidence → Verdict` is a BIJECTION (each of the four corners
-- maps to a distinct verdict), so ITS kernel pair is the diagonal and the
-- coequalizer of that pair is the identity — refl, contentless. The genuine
-- collapse here is the NEDGE SCALAR SHADOW `bias : Evidence → Bias`
-- (.NedgeShadow): it identifies the two distinct corners eU (conflict) and
-- eV (ignorance), both ↦ net0, while `verdict` keeps them apart (U ≢ V).
--
-- This module exhibits `bias` as the coequalizer of the parallel pair
-- (const eU , const eV : ⊤ → Evidence) — with the CONCRETE 3-element carrier
-- `Bias`, not a HIT quotient ([[project-agda-cubical-extraction-discipline]]):
--
--   * EXISTENCE   `bias-factors`   : every h : Evidence → Z that collapses
--                                    eU∼eV factors through bias.
--   * UNIQUENESS  `bias-coeq-unique`: the mediating map is unique (bias is
--                                    epi — surjective onto Bias).
--
-- so `bias` satisfies the full coequalizer universal property, not just the
-- coequalising equation.
--
-- It is registered (`bias-coeq-backed : BackedUP`) so the typechecker — not a
-- comment — enforces NON-VACUITY: the `content` certificate is precisely
-- `verdict-not-coequalises` (U ≢ V), a REAL apartness, the antithesis of a
-- refl-link. Per [[feedback-domain-skin-over-category]] the bridge is proved
-- "better than refl": the collapse does work (the eV case of `bias-factors`
-- consumes the hypothesis, it is not refl) and the universal property has
-- teeth (verdict witnesses a problem the relation genuinely excludes).
--
-- Layering ([[project-bridge-indexes-algebra-category]]): the central
-- `Category.UniversalProperty.Registry` MUST stay domain-agnostic — Category
-- never imports Logic. So this Logic-tier module EXTENDS the base registry
-- downstream (`verdict-registry = bias-coeq-backed ∷ registry`); the base
-- file carries only a prose coverage pointer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.BiasCoequalizer where

open import Substrate.Foundation.Bool     using (true; false)
open import Substrate.Foundation.Eq       using (_≡_; refl; sym; cong; trans)
open import Substrate.Foundation.Unit     using (⊤; tt)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product  using (Σ; _,_)
open import Substrate.Foundation.List     using (List; _∷_)

open import Substrate.Logic.Evidence.Verdict
  using (Evidence; ⟨_,_⟩; Verdict; P; F; U; V; verdict; eP; eF; eU; U≢V)
open import Substrate.Logic.Evidence.Verdict.NedgeShadow
  using (Bias; net+; net0; net-; bias; eV; bias-conflates-U-V)

open import Substrate.Category.Coequalizer using (Coequalises)
------------------------------------------------------------------------
-- 1. The two headline facts: bias COEQUALISES the (eU, eV) pair; verdict
-- does NOT. The second is the non-refl content — a genuine apartness.
------------------------------------------------------------------------

bias-coequalises : Coequalises {A = ⊤} (λ _ → eU) (λ _ → eV) bias
bias-coequalises _ = bias-conflates-U-V

verdict-not-coequalises : ¬ Coequalises {A = ⊤} (λ _ → eU) (λ _ → eV) verdict
verdict-not-coequalises ce = U≢V (ce tt)

------------------------------------------------------------------------
-- 2. bias is THE coequalizer (concrete carrier Bias).
--
-- EXISTENCE of the mediating map: any h that collapses eU∼eV factors as
-- h = (bias-factor h q) ∘ bias. The eV case CONSUMES the hypothesis q —
-- that is where the collapse does real work (it is not refl).
------------------------------------------------------------------------

bias-factor : {Z : Set} (h : Evidence → Z) → h eU ≡ h eV → Bias → Z
bias-factor h _ net+ = h eP
bias-factor h _ net- = h eF
bias-factor h _ net0 = h eU

bias-factors :
  {Z : Set} (h : Evidence → Z) (q : h eU ≡ h eV) (e : Evidence) →
  bias-factor h q (bias e) ≡ h e
bias-factors h q ⟨ true  , false ⟩ = refl
bias-factors h q ⟨ false , true  ⟩ = refl
bias-factors h q ⟨ true  , true  ⟩ = refl
bias-factors h q ⟨ false , false ⟩ = q

------------------------------------------------------------------------
-- UNIQUENESS of the mediating map: bias is surjective (epi), so any two
-- factors agreeing after precomposition with bias agree everywhere.
------------------------------------------------------------------------

bias-surjective : (b : Bias) → Σ Evidence (λ e → bias e ≡ b)
bias-surjective net+ = eP , refl
bias-surjective net- = eF , refl
bias-surjective net0 = eU , refl

bias-coeq-unique :
  {Z : Set} (d₁ d₂ : Bias → Z) →
  ((e : Evidence) → d₁ (bias e) ≡ d₂ (bias e)) →
  (b : Bias) → d₁ b ≡ d₂ b
bias-coeq-unique d₁ d₂ agree b with bias-surjective b
... | e , be≡b = trans (sym (cong d₁ be≡b)) (trans (agree e) (cong d₂ be≡b))

------------------------------------------------------------------------
-- 3. The canonical coequalising map: bias post-composed with the decode
-- Bias → Verdict. ⟡C2g-retire-p2: the flat `bias-coeq-UP : UPArrow` /
-- `bias-coeq-backed : BackedUP` registration wrappers are DROPPED (the
-- registry itself retired in ⟡C2g-registry, so the registration was moot);
-- the coequalizer THEOREMS above (bias-coequalises, verdict-not-coequalises,
-- bias-factors, bias-coeq-unique) are the real content and are tier-
-- independent — they carry the full coequalizer universal property via
-- Category.Coequalizer.Coequalises, with no BackedUP/UPArrow debt.
------------------------------------------------------------------------

decode : Bias → Verdict
decode net+ = P
decode net- = F
decode net0 = U
