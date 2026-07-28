{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.TableFaithful where

-- The general table-injectivity (L) subsumes row-inj. Parameterized on (L);
-- relational, so it names BOTH carriers explicitly rather than merging them.

import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)


------------------------------------------------------------------------
-- FROM row-inj TO embed-S₃ FAITHFULNESS (conditional reduction).
--
-- row-inj is the crux (proven above, unconditional). The full statement
--   embed-S₃-faithful : embed-S₃ a ≈ embed-S₃ b → a S₃.≈ b
-- needs one mechanical LIFT: from the six-element `Row` index to arbitrary
-- S₃ elements. That lift is:
--   (L) act-on-canonical-inj-general :
--         for all n₁ n₂ : Word Z₃-Base.Gen, h₁ h₂ : Word Z₂-Base.Gen,
--         (∀ v → act-on-canonical (Z₃-Existential.normalize n₁) (Z₂.normalize h₁) v
--              ≡ act-on-canonical (Z₃-Existential.normalize n₂) (Z₂.normalize h₂) v) →
--         (Z₃-Existential.normalize n₁ ≡ Z₃-Existential.normalize n₂) × (Z₂.normalize h₁ ≡ Z₂.normalize h₂)
-- which is row-inj precomposed with `Z₃-Existential.normalize-canonical` / `Z₂.normalize-
-- canonical` (every normalized word IS one of the six canonical shapes, via
-- canonical-cover) plus reading the actions at α and β. Given (L), the rest
-- is definitional: S₃._≈_ (n₁,h₁)(n₂,h₂) = (Z₃.≈ n₁ n₂)×(Z₂.≈ h₁ h₂), and each
-- Coxeter ≈ IS normalize-equality (Core.Operations), so (L)'s output is
-- exactly a S₃.≈ b; and embed-S₃ a ≈ embed-S₃ b unfolds (Symmetric pointwise
-- + strip axis-of-v via v-of-axis-axis-of-v) to (L)'s hypothesis.
--
-- STATUS: row-inj DONE (unconditional, 2.8). (L) = the mechanical lift via
-- canonical-cover — this module's INJECTIVITY route, left as a parameter.
--
-- ⟡embed-S₃ faithfulness is now DISCHARGED — but by the ROUNDTRIP route, not
-- via (L). Substrate.Groups.S4-Iso.EmbedS3Faithful proves
--   extract-embed-roundtrip : extract-s (embed-S₃ s) S₃.≈ s   (R, the atom)
-- by a double canonical-cover (the same 3×2 = 6 canonical shapes row-inj
-- enumerates), and derives `embed-S₃-faithful` as its two-line corollary
-- (apply extract-s to both sides, sandwich with R). The ROUNDTRIP needs no
-- separate (L) lift, so (L) below stays an un-assembled ALTERNATIVE
-- (injectivity-direction) parameter; row-inj remains the shared 6-case crux.
-- Consumed by Cocycles.V4Signature.SRecovers (s-recovers → the two-sided
-- S₄ bijection).
------------------------------------------------------------------------

module _
  (act-canonical-inj-general :
     (n₁ n₂ : Word Z₃-Base.Gen) (h₁ h₂ : Word Z₂-Base.Gen) →
     ((v : V₄) → act-on-canonical n₁ h₁ v ≡ act-on-canonical n₂ h₂ v) →
     (n₁ ≡ n₂) × (h₁ ≡ h₂))
  where

  -- Given the general table-injectivity (L), row-inj is the α,β-restricted
  -- instance; this module records that (L) subsumes row-inj and would
  -- discharge embed-S₃ faithfulness through the definitional chain above.
  table-faithful :
    (n₁ n₂ : Word Z₃-Base.Gen) (h₁ h₂ : Word Z₂-Base.Gen) →
    ((v : V₄) → act-on-canonical n₁ h₁ v ≡ act-on-canonical n₂ h₂ v) →
    (n₁ ≡ n₂) × (h₁ ≡ h₂)
  table-faithful = act-canonical-inj-general
