{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCoEmitViaTrace — the COMPATIBILITY BRIDGE: CoEmit's bisimilarity _≈ᵉ_ composes from the
-- UNIVERSAL carrier RealTrace (the terminal coalgebra of S↦ℕ×S). CoEmit ℕ is a ℕ-headed coalgebra;
-- coemit-trace = unfold coalg is the coalgebra morphism into the terminal RealTrace; and the coalgebra
-- morphism PRESERVES bisimulation: c ≈ᵉ d → coemit-trace c ~ coemit-trace d. So _≈ᵉ_ need not re-derive
-- its equivalence — it factors through _~_ (whose ~-refl/~-sym/~-trans are the universal, shared ones).
-- (⟡coemit-via-realtrace — the reframe's compose-from-a-universal-property, in-tree, monad-laws untouched.)
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
  using (CoEmit; ret; emitᶜ; step; _≈ᵉ_; step≈; Step≈; ret≈; emit≈) renaming (Step to Step⟦f8c709b4⟧)

-- FAITHFUL ℕ-encoding of a CoEmit node: parity tags the constructor (even = ret value, odd = emit output),
-- so the head is injective on observations. ret a is terminal → it loops (tail = itself), giving the
-- constant stream 2a; emitᶜ o k advances to k with head 2o+1.
double : ℕ → ℕ
double zero    = zero
double (suc n) = suc (suc (double n))

-- coalg via step-level functions (so head/tail of coemit-trace reduce definitionally on the Step):
code : Step⟦f8c709b4⟧ ℕ (CoEmit ℕ) → ℕ
code (ret a)     = double a
code (emitᶜ o k) = suc (double o)

next : CoEmit ℕ → Step⟦f8c709b4⟧ ℕ (CoEmit ℕ) → CoEmit ℕ
next c (ret a)     = c
next c (emitᶜ o k) = k

coalg : CoEmit ℕ → ℕ × CoEmit ℕ
coalg c = code (step c) , next c (step c)

coemit-trace : CoEmit ℕ → RealTrace
coemit-trace = unfold coalg

------------------------------------------------------------------------
-- THE COMPATIBILITY: the coalgebra morphism PRESERVES bisimulation (≈ᵉ → ~). Arithmetic-free: matching
-- ret≈ a / emit≈ o gives the SAME head on both sides (refl); the tails recurse (guarded under tail~).
------------------------------------------------------------------------
-- head (coemit-trace c) = code (step c); tail (coemit-trace c) = coemit-trace (next c (step c)). Matching
-- step≈ p refines step c and step d to the SAME shape, so code/next reduce and the heads are refl-equal.
≈ᵉ→~ : {c d : CoEmit ℕ} → c ≈ᵉ d → coemit-trace c ~ coemit-trace d
head~ (≈ᵉ→~ {c} {d} p) with step c | step d | step≈ p
... | ret a     | ret .a      | ret≈ .a    = refl
... | emitᶜ o k  | emitᶜ .o k' | emit≈ .o q = refl
tail~ (≈ᵉ→~ {c} {d} p) with step c | step d | step≈ p
... | ret a     | ret .a      | ret≈ .a    = ≈ᵉ→~ p
... | emitᶜ o k  | emitᶜ .o k' | emit≈ .o q = ≈ᵉ→~ q

-- reflexivity now COMPOSES from the universal carrier (no re-derived step-refl):
≈ᵉ-refl-via-trace : (c : CoEmit ℕ) → coemit-trace c ~ coemit-trace c
≈ᵉ-refl-via-trace c = ~-refl (coemit-trace c)

------------------------------------------------------------------------
-- BACKWARD (~ → ≈ᵉ): the coalgebra morphism REFLECTS bisimulation too, so _≈ᵉ_ ⟺ coemit-trace-_~_ — the full
-- iff, retiring ≈ᵉ's bespoke equivalence for the pulled-back universal one. Needs code-injectivity (the
-- parity encoding is faithful): double is injective, and even (double a) ≠ odd (suc (double o)).
------------------------------------------------------------------------
open import Substrate.Foundation.Eq using (cong; sym; subst)
open import Substrate.Foundation.Nat using (suc-injective)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)

double-inj : {a b : ℕ} → double a ≡ double b → a ≡ b
double-inj {zero}  {zero}  _  = refl
double-inj {suc a} {suc b} eq = cong suc (double-inj (suc-injective (suc-injective eq)))

even≠odd : (a o : ℕ) → double a ≡ suc (double o) → ⊥
even≠odd zero    o       ()        -- zero ≡ suc _ : impossible
even≠odd (suc a) zero    eq with suc-injective eq   -- suc (double a) ≡ zero : impossible
... | ()
even≠odd (suc a) (suc o) eq = even≠odd a o (suc-injective (suc-injective eq))

≈ᵉ←~ : {c d : CoEmit ℕ} → coemit-trace c ~ coemit-trace d → c ≈ᵉ d
step≈ (≈ᵉ←~ {c} {d} p) with step c | step d | head~ p | tail~ p
... | ret a     | ret b       | h | _ rewrite double-inj h                = ret≈ b
... | ret a     | emitᶜ o k'  | h | _ = ⊥-elim (even≠odd a o h)
... | emitᶜ o k  | ret b       | h | _ = ⊥-elim (even≠odd b o (sym h))
... | emitᶜ o k  | emitᶜ o' k' | h | t rewrite double-inj (suc-injective h) = emit≈ o' (≈ᵉ←~ t)

------------------------------------------------------------------------
-- THE FULL COMPOSE-FROM: with the iff (≈ᵉ→~ / ≈ᵉ←~), _≈ᵉ_'s WHOLE equivalence is INHERITED from the
-- universal carrier's — ≈ᵉ-refl/sym/trans are ~-refl/sym/trans transported through coemit-trace. The
-- bespoke step-refl/sym-step/trans-step in ExtrudeCoEmitMonad are now SUPERSEDED (retirable).
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Bisim using (~-sym; ~-trans)

≈ᵉ-refl′ : (c : CoEmit ℕ) → c ≈ᵉ c
≈ᵉ-refl′ c = ≈ᵉ←~ (~-refl (coemit-trace c))

≈ᵉ-sym′ : {c d : CoEmit ℕ} → c ≈ᵉ d → d ≈ᵉ c
≈ᵉ-sym′ p = ≈ᵉ←~ (~-sym (≈ᵉ→~ p))

≈ᵉ-trans′ : {c d e : CoEmit ℕ} → c ≈ᵉ d → d ≈ᵉ e → c ≈ᵉ e
≈ᵉ-trans′ p q = ≈ᵉ←~ (~-trans (≈ᵉ→~ p) (≈ᵉ→~ q))

------------------------------------------------------------------------
-- THE CANONICAL EQUIVALENCE OF _≈ᵉ_ — bundled from the INHERITED (universal-carrier) refl/sym/trans, NOT the
-- retired bespoke ones. Downstream gets _≈ᵉ_'s IsEquivalence from HERE (composed through RealTrace), the
-- single canonical home for the emit-bisimilarity equivalence.
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.ExtrudeSetoidCategory using (IsEquivalence)

≈ᵉ-isEquivalence : IsEquivalence {CoEmit ℕ} _≈ᵉ_
≈ᵉ-isEquivalence = record { ≈-refl = ≈ᵉ-refl′ ; ≈-sym = ≈ᵉ-sym′ ; ≈-trans = ≈ᵉ-trans′ }
