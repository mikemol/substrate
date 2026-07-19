------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.EmbedS3Faithful
--
-- ⟡embed-s3-faithful — DISCHARGED (was CompSideRoundtrip's "ONE
-- genuinely-missing lemma"). Two results:
--
--   extract-embed-roundtrip : extract-s (embed-S₃ s) S₃.≈ s
--   embed-S₃-faithful       : embed-S₃ a ≈ embed-S₃ b → a S₃.≈ b
--
-- The roundtrip `extract-embed-roundtrip` (R) is the atom. It sidesteps the
-- CanonicalFaithful `row-inj`/(L) INJECTIVITY route entirely: instead of
-- "same action ⇒ same word", it computes "extract-then-re-embed recovers s".
-- Proof = a double `canonical-cover` over Z₃/Z₂ `normalize-canonical`
-- (3 × 2 = 6 canonical shapes); in each leaf nn,hh are LITERAL, so
-- `act-on-canonical`, `axis-of-v`, `extract-s-from` all compute, and the
-- goal is a normalize-equality that holds by `refl`. No new mathematics —
-- the "canonical-cover plumbing" CanonicalFaithful flagged, assembled via
-- the ROUNDTRIP (R) rather than the injectivity (row-inj), which needs no
-- separate lift.
--
-- Then embed-S₃-faithful is the two-line corollary: apply `extract-s`
-- (which respects ≈ pointwise) to `embed-S₃ a ≈ embed-S₃ b`, sandwich with
-- R on both ends.
--
-- Co-apex: this is the home of CompSideRoundtrip's `s-recovers` obligation.
-- See CanonicalFaithful (`row-inj` — the injectivity crux) and
-- Cocycles.V4Signature.Codeword.LiveS4Bijection (`Live≃Permutation` — the
-- PARALLEL fully-proven two-sided S₄ bijection in the axis-selector
-- parametrization).
--
-- --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.EmbedS3Faithful where

open import Substrate.Axes using (Axis; C; S; axis-of-v; v-of-axis)
open import Substrate.Groups.V4 using (V₄; α; β)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Groups.S4 using (Permutation; _≈_)
open Permutation
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.S4-Iso.Embedding using (embed-S₃)
open import Substrate.Groups.S4-Iso.Extract using (extract-s; extract-s-from)

------------------------------------------------------------------------
-- The extracted words of a canonical (nn, hh), as read through the action.
------------------------------------------------------------------------

extracted : Word Z₃.Gen → Word Z₂.Gen → S₃.Carrier
extracted nn hh =
  extract-s-from (axis-of-v (act-on-canonical nn hh α))
                 (axis-of-v (act-on-canonical nn hh β))

------------------------------------------------------------------------
-- R-canonical: for canonical nn, hh, the extracted words re-normalize to
-- nn, hh.  6 computational cases via nested canonical-cover.
------------------------------------------------------------------------

R-canonical :
  (nn : Word Z₃.Gen) (hh : Word Z₂.Gen)
  (cn : Z₃.Canonical nn) (ch : Z₂.Canonical hh) →
  (Z₃.normalize (proj₁ (extracted nn hh)) ≡ nn)
  × (Z₂.normalize (proj₂ (extracted nn hh)) ≡ hh)
R-canonical _ _ (Z₃.c-pos zero)             (Z₂.c-pos zero)       = refl , refl
R-canonical _ _ (Z₃.c-pos zero)             (Z₂.c-pos (suc zero)) = refl , refl
R-canonical _ _ (Z₃.c-pos (suc zero))       (Z₂.c-pos zero)       = refl , refl
R-canonical _ _ (Z₃.c-pos (suc zero))       (Z₂.c-pos (suc zero)) = refl , refl
R-canonical _ _ (Z₃.c-pos (suc (suc zero))) (Z₂.c-pos zero)       = refl , refl
R-canonical _ _ (Z₃.c-pos (suc (suc zero))) (Z₂.c-pos (suc zero)) = refl , refl

------------------------------------------------------------------------
-- R: extract-s (embed-S₃ s) S₃.≈ s.
------------------------------------------------------------------------

extract-embed-roundtrip : (s : S₃.Carrier) → extract-s (embed-S₃ s) S₃.≈ s
extract-embed-roundtrip (n , h) =
  R-canonical (Z₃.normalize n) (Z₂.normalize h)
              (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)

------------------------------------------------------------------------
-- embed-S₃-faithful: the corollary.
-- extract-s respects ≈ (reads apply values, which are ≡), so from
-- embed-S₃ a ≈ embed-S₃ b we get extract-s (embed-S₃ a) ≡ extract-s (embed-S₃ b),
-- then sandwich with R on both sides.
------------------------------------------------------------------------

extract-s-cong : {σ τ : Permutation} → σ ≈ τ → extract-s σ ≡ extract-s τ
extract-s-cong {σ} {τ} eq =
  cong₂ extract-s-from (eq C) (eq S)
  where
    cong₂ : {A B D : Set} (f : A → B → D) {a₁ a₂ : A} {b₁ b₂ : B} →
            a₁ ≡ a₂ → b₁ ≡ b₂ → f a₁ b₁ ≡ f a₂ b₂
    cong₂ f refl refl = refl

embed-S₃-faithful : {a b : S₃.Carrier} → embed-S₃ a ≈ embed-S₃ b → a S₃.≈ b
embed-S₃-faithful {a} {b} eq =
  S₃.≈-trans {a} {extract-s (embed-S₃ a)} {b}
    (S₃.≈-sym {extract-s (embed-S₃ a)} {a} (extract-embed-roundtrip a))
    (S₃.≈-trans {extract-s (embed-S₃ a)} {extract-s (embed-S₃ b)} {b}
      (subst-≈ (extract-s-cong {embed-S₃ a} {embed-S₃ b} eq))
      (extract-embed-roundtrip b))
  where
    subst-≈ : {x y : S₃.Carrier} → x ≡ y → x S₃.≈ y
    subst-≈ {x} p = subst (λ z → x S₃.≈ z) p (S₃.≈-refl x)
