{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Foundation.RewriteConfluence — NEWMAN'S LEMMA: a terminating and
-- locally-confluent abstract rewrite system is confluent (Church-Rosser).
--
-- ⟡newman-upstream: this is the ONE result the extruder-soundness tower
-- contributed that the substrate lacked (re-verified THREE times: no Newman /
-- Church-Rosser / WCR / confluence / reflexive-transitive closure anywhere,
-- including the WitnessTower). It is upstreamed here as a proper, relation-generic
-- Foundation module, built on the substrate's own `Acc` (Foundation.WellFounded),
-- consuming it by hand-recursion — the substrate's idiom (compute-trace-acc) for
-- well-founded recursion without a generic recursor.
--
-- The classic diamond-tiling proof: split each multistep into first-step + rest,
-- local-confluence the two first steps, recurse via the IH at the strictly-smaller
-- successors (`rec b`), tile the diamonds closed. Structurally terminating on the
-- Acc witness (no TERMINATING pragma).
------------------------------------------------------------------------

module Substrate.Foundation.RewriteConfluence
  {ℓ ℓ′}
  {A   : Set ℓ}
  (_⇒_ : A → A → Set ℓ′)      -- the one-step reduction of an abstract rewrite system
  where

open import Substrate.Foundation.Level     using (_⊔_)
open import Substrate.Foundation.Eq        using (_≡_; refl)
open import Substrate.Foundation.Product   using (Σ; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.WellFounded using (Acc; acc)

------------------------------------------------------------------------
-- The reflexive-transitive closure ⇒* (multi-step reduction) and its composition.
------------------------------------------------------------------------
data _⇒*_ : A → A → Set (ℓ ⊔ ℓ′) where
  done : ∀ {a}          → a ⇒* a
  _◅_  : ∀ {a b c} → a ⇒ b → b ⇒* c → a ⇒* c

infixr 5 _◅_

_++*_ : ∀ {a b c} → a ⇒* b → b ⇒* c → a ⇒* c
done     ++* q = q
(r ◅ rs) ++* q = r ◅ (rs ++* q)

------------------------------------------------------------------------
-- Joinability: two terms CONVERGE when they have a common reduct.
------------------------------------------------------------------------
Converge : A → A → Set (ℓ ⊔ ℓ′)
Converge b c = Σ A (λ d → (b ⇒* d) × (c ⇒* d))

------------------------------------------------------------------------
-- WCR (weak / local confluence): one-step peaks converge.
-- CR  (Church-Rosser / confluence):  multi-step peaks converge.
-- SN  (strong normalization): Acc on the FORWARD step (x accessible below y iff y⇒x).
------------------------------------------------------------------------
WCR : Set (ℓ ⊔ ℓ′)
WCR = ∀ {a b c} → a ⇒ b → a ⇒ c → Converge b c

CR : Set (ℓ ⊔ ℓ′)
CR = ∀ {a b c} → a ⇒* b → a ⇒* c → Converge b c

SN : A → Set (ℓ ⊔ ℓ′)
SN = Acc (λ x y → y ⇒ x)

------------------------------------------------------------------------
-- NEWMAN'S LEMMA: WCR + SN ⟹ CR, by well-founded induction on the peak apex.
------------------------------------------------------------------------
newman : WCR → ∀ {a} → SN a → ∀ {b c} → a ⇒* b → a ⇒* c → Converge b c
newman wcr accA done              a⇒*c = _ , (a⇒*c , done)
newman wcr accA (a⇒b ◅ b⇒*b')     done = _ , (done , (a⇒b ◅ b⇒*b'))
newman wcr (acc rec) (_◅_ {b = b} a⇒b b⇒*x) (_◅_ {b = c} a⇒c c⇒*y) =
  let e     = proj₁ (wcr a⇒b a⇒c)
      b⇒*e  = proj₁ (proj₂ (wcr a⇒b a⇒c))
      c⇒*e  = proj₂ (proj₂ (wcr a⇒b a⇒c))
      jx    = newman wcr (rec b a⇒b) b⇒*x b⇒*e
      d₁    = proj₁ jx
      x⇒*d₁ = proj₁ (proj₂ jx)
      e⇒*d₁ = proj₂ (proj₂ jx)
      jy    = newman wcr (rec c a⇒c) (c⇒*e ++* e⇒*d₁) c⇒*y
      d₂     = proj₁ jy
      d₁⇒*d₂ = proj₁ (proj₂ jy)
      y⇒*d₂  = proj₂ (proj₂ jy)
  in d₂ , ((x⇒*d₁ ++* d₁⇒*d₂) , y⇒*d₂)

------------------------------------------------------------------------
-- Church-Rosser for a system that is locally confluent and terminating: the
-- three ingredients (WCR, SN-everywhere) assemble to global confluence.
------------------------------------------------------------------------
church-rosser : WCR → (∀ a → SN a) → CR
church-rosser wcr sn a⇒*b a⇒*c = newman wcr (sn _) a⇒*b a⇒*c
