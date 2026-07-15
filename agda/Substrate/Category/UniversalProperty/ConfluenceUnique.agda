------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ConfluenceUnique — ⟡x8a-uniqueness-graded: the
-- Church-Rosser ⟹ unique-normal-form principle, tier-independent.
--
-- Extracted verbatim from the flat X8aUnique's layer ② (which was ALWAYS abstract — parameterized
-- over any reduction with a multi-step closure + convergence, no BackedUP/UPArrow dependency), so the
-- flat X8aUnique/X8aBacked/Unique/WedgeUP tier can retire while this genuine content survives. The
-- run-value uniqueness (layer ①) was the TRIVIAL unconditional corner — x8a's witness `v ≡ run fs`
-- self-determines v (the functional-witness = equality, the μ-corner the graded Contentfulᴳ already
-- encodes), so it needs no separate lemma.
--
-- CR ⟹ uniqueness of normal forms: if a term reduces to two NORMAL forms, they coincide. Instantiated
-- at the real branching SKI reduction by X8aSkiInstance (FUSep's Newman frame); the ℕ demonstrator's
-- deterministic `next` makes its own confluence trivial — the content lives at SKI's multi-redex reduction.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ConfluenceUnique where

open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans)

module CRUnique
  {Tm : Set}
  (_⇒*_ : Tm → Tm → Set)
  (Converge : Tm → Tm → Set)
  (conv-witnesses : (b c : Tm) → Converge b c → Σ Tm (λ d → (b ⇒* d) × (c ⇒* d)))
  (CR : {a b c : Tm} → a ⇒* b → a ⇒* c → Converge b c)
  where

  -- a term is NORMAL when every reduction from it is trivial (returns it): b ⇒* d ⟹ d ≡ b.
  Normal : Tm → Set
  Normal b = (d : Tm) → b ⇒* d → d ≡ b

  -- CR ⟹ uniqueness of normal forms: two normal forms of one term coincide.
  cr-nf-unique :
    {a b c : Tm} → a ⇒* b → a ⇒* c → Normal b → Normal c → b ≡ c
  cr-nf-unique {a} {b} {c} a⇒*b a⇒*c nb nc with conv-witnesses b c (CR a⇒*b a⇒*c)
  ... | d , (b⇒*d , c⇒*d) = trans (sym (nb d b⇒*d)) (nc d c⇒*d)
