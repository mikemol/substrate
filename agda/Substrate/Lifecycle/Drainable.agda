------------------------------------------------------------------------
-- Substrate.Lifecycle.Drainable
--
-- Defines: drainable
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Drainable where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lifecycle.Reflection


------------------------------------------------------------------------
-- DRAINING LOSES NOTHING: if the tier is a reflection, then two staged
-- records with the same durable image are equal.
--
-- That is the property the drain actually needs. "The data is elsewhere" is
-- not enough — the durable form must DETERMINE the staged one, or two
-- distinct records could share an image and deleting either would silently
-- change what the other reconstructs to.
--
-- `project` being INJECTIVE is exactly that, and it follows from the
-- round-trip with no further hypothesis: `reconstruct` is a retraction, and
-- anything with a retraction is injective. So the reflection record carries
-- one field and the safety argument is a two-line consequence rather than a
-- second obligation someone has to remember to discharge.
--
-- ⚑ AND IT IS WHY THE CHECK IS PER-CORE AND CONSTRUCTIVE. `drainable` takes
-- the two records and an equality of their images; the store's version of
-- this is: rebuild the core's `obs`/`edge` from the SPPF + reverse index,
-- compare to the live rows, delete ONLY on equality. A core that fails is
-- retained and reported. Nothing is deleted on the strength of an argument.
------------------------------------------------------------------------

drainable : {S D : Set} {project : S → D} {reconstruct : D → S}
          → Reflection project reconstruct
          → (s₁ s₂ : S) → project s₁ ≡ project s₂ → s₁ ≡ s₂
drainable {project = project} {reconstruct = reconstruct} refl-pf s₁ s₂ eq =
  trans (sym (Reflection.round-trip refl-pf s₁))
        (trans (cong reconstruct eq) (Reflection.round-trip refl-pf s₂))
