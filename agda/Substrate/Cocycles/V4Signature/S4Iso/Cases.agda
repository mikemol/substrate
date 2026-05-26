------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso.Cases
--
-- The 6 per-case lemmas (case-α-even, case-α-odd, case-β-even,
-- case-β-odd, case-γ-even, case-γ-odd) that close the σ ≈ stab-X
-- relationship for each of the 6 valid (σ(C), σ(S)) configurations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso.Cases where

open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; trans-sym)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4
  using (Permutation; _≈_)
  renaming (apply to applyₛ)
open import Substrate.Groups.SemidirectProduct using (Stab)

open import Substrate.Cocycles.V4Signature.S4Iso.Injective
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements

------------------------------------------------------------------------
-- (α-pair, even): σ(D)=D, σ(C)=C, σ(S)=S ⇒ σ ≈ stab-id.
------------------------------------------------------------------------

case-α-even :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ C → applyₛ σ S ≡ S →
  σ ≈ stab-id
case-α-even σ σ-stab pC pS D = σ-stab
case-α-even σ σ-stab pC pS C = pC
case-α-even σ σ-stab pC pS S = pS
case-α-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = ⊥-elim (W≢C (σ-injective σ W C (trans-sym pW pC)))
... | S = ⊥-elim (W≢S (σ-injective σ W S (trans-sym pW pS)))
... | W = refl

------------------------------------------------------------------------
-- (α-pair, odd): σ(D)=D, σ(C)=C, σ(S)=W ⇒ σ ≈ stab-sw.
------------------------------------------------------------------------

case-α-odd :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ C → applyₛ σ S ≡ W →
  σ ≈ stab-sw
case-α-odd σ σ-stab pC pS D = σ-stab
case-α-odd σ σ-stab pC pS C = pC
case-α-odd σ σ-stab pC pS S = pS
case-α-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = ⊥-elim (W≢C (σ-injective σ W C (trans-sym pW pC)))
... | S = refl
... | W = ⊥-elim (S≢W (σ-injective σ S W (trans-sym pS pW)))

------------------------------------------------------------------------
-- (β-pair, odd): σ(D)=D, σ(C)=S, σ(S)=C ⇒ σ ≈ stab-cs.
------------------------------------------------------------------------

case-β-odd :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ S → applyₛ σ S ≡ C →
  σ ≈ stab-cs
case-β-odd σ σ-stab pC pS D = σ-stab
case-β-odd σ σ-stab pC pS C = pC
case-β-odd σ σ-stab pC pS S = pS
case-β-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = ⊥-elim (S≢W (σ-injective σ S W (trans-sym pS pW)))
... | S = ⊥-elim (C≢W (σ-injective σ C W (trans-sym pC pW)))
... | W = refl

------------------------------------------------------------------------
-- (β-pair, even): σ(D)=D, σ(C)=S, σ(S)=W ⇒ σ ≈ stab-csw.
------------------------------------------------------------------------

case-β-even :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ S → applyₛ σ S ≡ W →
  σ ≈ stab-csw
case-β-even σ σ-stab pC pS D = σ-stab
case-β-even σ σ-stab pC pS C = pC
case-β-even σ σ-stab pC pS S = pS
case-β-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = refl
... | S = ⊥-elim (C≢W (σ-injective σ C W (trans-sym pC pW)))
... | W = ⊥-elim (S≢W (σ-injective σ S W (trans-sym pS pW)))

------------------------------------------------------------------------
-- (γ-pair, even): σ(D)=D, σ(C)=W, σ(S)=C ⇒ σ ≈ stab-cws.
------------------------------------------------------------------------

case-γ-even :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ W → applyₛ σ S ≡ C →
  σ ≈ stab-cws
case-γ-even σ σ-stab pC pS D = σ-stab
case-γ-even σ σ-stab pC pS C = pC
case-γ-even σ σ-stab pC pS S = pS
case-γ-even σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = ⊥-elim (S≢W (σ-injective σ S W (trans-sym pS pW)))
... | S = refl
... | W = ⊥-elim (C≢W (σ-injective σ C W (trans-sym pC pW)))

------------------------------------------------------------------------
-- (γ-pair, odd): σ(D)=D, σ(C)=W, σ(S)=S ⇒ σ ≈ stab-cw.
------------------------------------------------------------------------

case-γ-odd :
  (σ : Permutation) (σ-stab : Stab D σ) →
  applyₛ σ C ≡ W → applyₛ σ S ≡ S →
  σ ≈ stab-cw
case-γ-odd σ σ-stab pC pS D = σ-stab
case-γ-odd σ σ-stab pC pS C = pC
case-γ-odd σ σ-stab pC pS S = pS
case-γ-odd σ σ-stab pC pS W with applyₛ σ W in pW
... | D = ⊥-elim (W≢D (σ-injective σ W D (trans-sym pW σ-stab)))
... | C = refl
... | S = ⊥-elim (S≢W (σ-injective σ S W (trans-sym pS pW)))
... | W = ⊥-elim (C≢W (σ-injective σ C W (trans-sym pC pW)))
