{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCoEmitTraceEq — the FULL structural retire: the monad laws re-derived NATIVELY in the universal
-- trace relation _~_ (via coemit-trace), with NO Step≈, NO bespoke _≈ᵉ_, NO transport. This proves the
-- bespoke bisimilarity _≈ᵉ_/Step≈ is STRUCTURALLY superseded — the emit-monad's laws hold in the pulled-back
-- universal equality directly. (⟡coemit-redefine-via-trace — the harder path: genuinely re-derive, not transport.)
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCoEmitTraceEq where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.R.Trace using (RealTrace)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
  using (CoEmit; ret; emitᶜ; step; bind; returnᶜ)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace
  using (coemit-trace; coalg; next; code)

-- _≈ᵗ_ : the PRIMARY bisimilarity is the pulled-back universal one (no bespoke record). Its whole equivalence
-- IS the universal ~-refl/~-sym/~-trans (through coemit-trace) — nothing re-derived.
_≈ᵗ_ : CoEmit ℕ → CoEmit ℕ → Set
c ≈ᵗ d = coemit-trace c ~ coemit-trace d

infix 4 _≈ᵗ_

-- THE LEFT-UNIT MONAD LAW, re-derived NATIVELY in _~_ (no Step≈): bind (returnᶜ a) h ≈ᵗ h a.
-- step (bind (returnᶜ a) h) = step (h a) definitionally, so heads agree (refl); the tail either loops
-- (ret → recurse, guarded) or advances to the shared continuation k (emit → ~-refl).
bind-ret-left-~ : (a : ℕ) (h : ℕ → CoEmit ℕ) → bind (returnᶜ a) h ≈ᵗ h a
head~ (bind-ret-left-~ a h) = refl
tail~ (bind-ret-left-~ a h) with step (h a)
... | ret b     = bind-ret-left-~ a h
... | emitᶜ o k = ~-refl (coemit-trace k)

------------------------------------------------------------------------
-- bind-ret-right, re-derived NATIVELY in _~_ (no Step≈). step (bind c returnᶜ) mirrors step c: ret a → ret a
-- (both codes double a); emitᶜ o k → emitᶜ o (bind k returnᶜ) (both codes suc (double o)) — heads refl either way.
------------------------------------------------------------------------
bind-ret-right-~ : (c : CoEmit ℕ) → bind c returnᶜ ≈ᵗ c
head~ (bind-ret-right-~ c) with step c
... | ret a     = refl
... | emitᶜ o k = refl
tail~ (bind-ret-right-~ c) with step c
... | ret a     = bind-ret-right-~ c
... | emitᶜ o k = bind-ret-right-~ k

------------------------------------------------------------------------
-- BOTH, PROVEN EQUIVALENT (D-model-the-coset): the SAME law is available in two presentations — the STRUCTURAL
-- one (base's Step≈ proof, TRANSPORTED via the iff ≈ᵉ→~) and the NATIVE one (re-derived in _~_ directly). The
-- iff (≈ᵉ→~ / ≈ᵉ←~, 304) proves _≈ᵉ_ ⟺ _≈ᵗ_, so both presentations prove the SAME proposition — neither is
-- primary; they are two views of one bisimilarity, glued by the iff. (Retire = prove-equivalent, not delete.)
------------------------------------------------------------------------
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
  using (bind-ret-left; bind-ret-right; bind-assoc)
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (≈ᵉ→~)

-- transport route (structural proof → universal presentation):
bind-ret-left-trans  : (a : ℕ) (h : ℕ → CoEmit ℕ) → bind (returnᶜ a) h ≈ᵗ h a
bind-ret-left-trans a h = ≈ᵉ→~ (bind-ret-left a h)

bind-ret-right-trans : (c : CoEmit ℕ) → bind c returnᶜ ≈ᵗ c
bind-ret-right-trans c = ≈ᵉ→~ (bind-ret-right c)

-- both bind-ret-left-~ (native) and bind-ret-left-trans (transport) inhabit the SAME type — the iff certifies
-- they prove one proposition. Witness the coincidence of types (both : bind (returnᶜ a) h ≈ᵗ h a):
_ : (a : ℕ) (h : ℕ → CoEmit ℕ) → bind (returnᶜ a) h ≈ᵗ h a
_ = bind-ret-left-~           -- the native route

_ : (a : ℕ) (h : ℕ → CoEmit ℕ) → bind (returnᶜ a) h ≈ᵗ h a
_ = bind-ret-left-trans        -- the transport route — same proposition, proven equivalent by the iff

-- bind-assoc: the TRANSPORT route always works (the iff carries base's Step≈ proof to the universal
-- presentation). The NATIVE route (re-derive bind-assoc in _~_ by coinduction) is the harder half — labeled
-- ⟡bind-assoc-native; here the transport certifies the law holds in _≈ᵗ_, proven equivalent to base's _≈ᵉ_.
bind-assoc-trans : (c : CoEmit ℕ) (g : ℕ → CoEmit ℕ) (h : ℕ → CoEmit ℕ)
                 → bind (bind c g) h ≈ᵗ bind c (λ x → bind (g x) h)
bind-assoc-trans c g h = ≈ᵉ→~ (bind-assoc c g h)

------------------------------------------------------------------------

------------------------------------------------------------------------

------------------------------------------------------------------------
-- bind-assoc-native (the 308 ret-cascade DISCHARGED): the ret case bottoms out through the coalgebra unfolding
-- — step c' = emitᶜ → recurse (go k); step c' = ret a then step (g a) = emitᶜ → shared continuation (~-refl);
-- step (g a) = ret b then step (h b) = emitᶜ → shared continuation (~-refl), step (h b) = ret → loop (go c',
-- the period-1 cover, guarded). head is μ-exact (refl, both sides share the step). This is the μ/ν + cover in one.
------------------------------------------------------------------------
bind-assoc-~ : (c : CoEmit ℕ) (g : ℕ → CoEmit ℕ) (h : ℕ → CoEmit ℕ)
             → bind (bind c g) h ≈ᵗ bind c (λ x → bind (g x) h)
bind-assoc-~ c g h = go c
  where
    go : (c' : CoEmit ℕ) → bind (bind c' g) h ≈ᵗ bind c' (λ x → bind (g x) h)
    head~ (go c') with step c'
    ... | ret a     = refl
    ... | emitᶜ o k = refl
    tail~ (go c') with step c'
    ... | emitᶜ o k = go k
    ... | ret a with step (g a)
    ...   | emitᶜ o k = ~-refl (coemit-trace (bind k h))
    ...   | ret b with step (h b)
    ...     | emitᶜ o' k' = ~-refl (coemit-trace k')
    ...     | ret b''     = go c'
