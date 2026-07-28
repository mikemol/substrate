------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.ExtractCorrect
--
-- extract-s-correct: embed-S₃ (extract-s s) ≈ s for s ∈ Stab(D).
--
-- Per-axis case-split with full 16 (apply s C × apply s S) enumeration
-- at each axis, exhausting Sym({C, S, W}).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.ExtractCorrect where

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.EpsilonN
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; sym-trans; trans-sym; cong-trans)

open import Substrate.Groups.S4-Iso.Embedding using (embed-S₃)
open import Substrate.Groups.S4-Iso.Extract using (extract-s; extract-s-from)

------------------------------------------------------------------------
-- Permutation apply is injective (derived from inv-l).
------------------------------------------------------------------------

apply-inj : (s : Permutation) → ∀ {x y} → apply s x ≡ apply s y → x ≡ y
apply-inj s {x} {y} eq =
  sym-trans (inv-l s x) (cong-trans (invₐ s) eq (inv-l s y))

------------------------------------------------------------------------
-- embed-S₃ recovers D at the D-axis via act-ε-N.
------------------------------------------------------------------------

embed-S₃-D : (s' : S₃.Carrier) → apply (embed-S₃ s') D ≡ D
embed-S₃-D s' = cong axis-of-v (act-ε-N s')

------------------------------------------------------------------------
-- Distinct-constructor disequalities.
------------------------------------------------------------------------

C≢D : C ≡ D → ⊥
C≢D ()
S≢D : S ≡ D → ⊥
S≢D ()
W≢D : W ≡ D → ⊥
W≢D ()
C≢S : C ≡ S → ⊥
C≢S ()
C≢W : C ≡ W → ⊥
C≢W ()
S≢W : S ≡ W → ⊥
S≢W ()

------------------------------------------------------------------------
-- extract-s-correct: pointwise roundtrip.
------------------------------------------------------------------------

extract-s-correct : (s : Permutation) → apply s D ≡ D →
                    embed-S₃ (extract-s s) ≈ s
extract-s-correct s sD D = trans (embed-S₃-D (extract-s s)) (sym sD)

extract-s-correct s sD C with apply s C in eqC | apply s S in eqS
... | D | D = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | C = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | S = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | W = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | C | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | S | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | W | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | C | C = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | S | S = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | W | W = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | C | S = refl
... | S | W = refl
... | W | C = refl
... | S | C = refl
... | W | S = refl
... | C | W = refl

extract-s-correct s sD S with apply s C in eqC | apply s S in eqS
... | D | D = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | C = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | S = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | W = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | C | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | S | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | W | D = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | C | C = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | S | S = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | W | W = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | C | S = refl
... | S | W = refl
... | W | C = refl
... | S | C = refl
... | W | S = refl
... | C | W = refl

extract-s-correct s sD W with apply s C in eqC | apply s S in eqS | apply s W in eqW
... | D | D | _ = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | C | _ = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | S | _ = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | D | W | _ = ⊥-elim (C≢D (apply-inj s (trans-sym eqC sD)))
... | C | D | _ = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | S | D | _ = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | W | D | _ = ⊥-elim (S≢D (apply-inj s (trans-sym eqS sD)))
... | C | C | _ = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | S | S | _ = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | W | W | _ = ⊥-elim (C≢S (apply-inj s (trans-sym eqC eqS)))
... | C | S | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | C | S | C = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | C | S | S = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | C | W | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | C | W | C = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | C | W | W = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | S | C | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | S | C | S = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | S | C | C = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | S | W | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | S | W | S = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | S | W | W = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | W | C | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | W | C | W = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | W | C | C = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | W | S | D = ⊥-elim (W≢D (apply-inj s (trans eqW (sym sD))))
... | W | S | W = ⊥-elim (C≢W (apply-inj s (trans eqC (sym eqW))))
... | W | S | S = ⊥-elim (S≢W (apply-inj s (trans eqS (sym eqW))))
... | C | S | W = refl
... | S | W | C = refl
... | W | C | S = refl
... | S | C | W = refl
... | W | S | C = refl
... | C | W | S = refl
