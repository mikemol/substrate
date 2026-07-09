{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSelfInterpUniversal — ⟡extrude-self-interp-universal: a
-- NON-TRIVIAL universal encoding beyond 266's homoiconicity, staying POSITIVE (the decode is a REDUCTION,
-- not a decision — D-no-classical-spook). Per D-model-the-coset, we do NOT pick one encoding: we model the
-- CODEC COSET as a UniversalEncoding interface {⌜·⌝ : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ the quote; eval : Tm⟦533ef80d⟧ the universal
-- interpreter; decode : eval ∙ ⌜M⌝ ⇒* M the universal decode LAW}, derive the self-interpreter properties
-- (self-decode, carries-confluence) FROM the interface, then instantiate — NON-TRIVIALLY (K-wrap) and
-- trivially (homoiconic, 266).
--
-- THE NON-TRIVIAL INSTANCE (K-wrap): ⌜M⌝ = K ∙ M (a DISTINCT quote, ⌜M⌝ ≠ M), eval = S ∙ I ∙ (K ∙ I)
-- (= λy. y I). Then eval ∙ ⌜M⌝ = (S∙I∙(K∙I)) ∙ (K∙M) ⇒* M by an EXPLICIT 4-step reduction (β-S, β-I under
-- cong-l, β-K under cong-r, β-K). This is a genuine universal interpreter — it decodes ANY M, including its
-- OWN code (self-decode: eval ∙ ⌜eval⌝ ⇒* eval), the metacircular self-interpreter.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: the UniversalEncoding
-- record (⌜·⌝/eval/decode) with derived self-decode + carries-confluence; the K-wrap instance (the explicit
-- decode reduction); the homoiconic instance (266). The framing ('models the codec coset', 'Lawvere at
-- Lawvere's fixed point') is (prose: D-model-the-coset + 266's thesis; a full structural Scott encoding with
-- a recursive eval over the term structure is scoped — K-wrap is a non-trivial universal eval, not the
-- structural one).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSelfInterpUniversal where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-I; β-K; β-S; cong-l; cong-r)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_; Converge; CR)

------------------------------------------------------------------------
-- ① THE CODEC COSET as an interface (D-model-the-coset — model the SPACE of encodings, don't pick one). A
--    UniversalEncoding is a quote ⌜·⌝, a universal interpreter eval, and the decode LAW (a POSITIVE
--    reduction eval ∙ ⌜M⌝ ⇒* M — NOT a decidable predicate). The self-interpreter properties DERIVE from it.
------------------------------------------------------------------------
record UniversalEncoding : Set where
  field
    ⌜_⌝    : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧                              -- the quote (an actual encoding)
    eval   : Tm⟦533ef80d⟧                                   -- the universal interpreter
    decode : (M : Tm⟦533ef80d⟧) → (eval ∙ ⌜ M ⌝) ⇒* M       -- the universal decode LAW (positive, confluence-based)

  -- the self-interpreter DECODES ITS OWN CODE (metacircular) — from the law at M = eval:
  self-decode : (eval ∙ ⌜ eval ⌝) ⇒* eval
  self-decode = decode eval

  -- it CARRIES CONFLUENCE BY CONSTRUCTION (given the system's SKI CR): eval ∙ ⌜M⌝'s reducts converge —
  -- confluence, not decidability, is the uniqueness the interpreter needs (266's method, at the interface):
  carries-confluence : CR → {M b c : Tm⟦533ef80d⟧} → (eval ∙ ⌜ M ⌝) ⇒* b → (eval ∙ ⌜ M ⌝) ⇒* c → Converge b c
  carries-confluence cr = cr

------------------------------------------------------------------------
-- ② THE NON-TRIVIAL INSTANCE (K-wrap) — beyond homoiconicity: ⌜M⌝ = K ∙ M (distinct quote), eval =
--    S ∙ I ∙ (K ∙ I). The decode is an EXPLICIT reduction: (S∙I∙(K∙I))∙(K∙M) ⇒* M.
------------------------------------------------------------------------
kwrap-decode : (M : Tm⟦533ef80d⟧) → ((S ∙ I ∙ (K ∙ I)) ∙ (K ∙ M)) ⇒* M
kwrap-decode M =
  β-S I (K ∙ I) (K ∙ M)                          -- ⇒ (I∙(K∙M)) ∙ ((K∙I)∙(K∙M))
    ◅ cong-l ((K ∙ I) ∙ (K ∙ M)) (β-I (K ∙ M))    -- ⇒ (K∙M) ∙ ((K∙I)∙(K∙M))
    ◅ cong-r (K ∙ M) (β-K I (K ∙ M))              -- ⇒ (K∙M) ∙ I
    ◅ β-K M I                                     -- ⇒ M
    ◅ done

kwrap : UniversalEncoding
kwrap = record { ⌜_⌝ = λ M → K ∙ M ; eval = S ∙ I ∙ (K ∙ I) ; decode = kwrap-decode }

------------------------------------------------------------------------
-- ③ THE TRIVIAL INSTANCE (homoiconic, 266): ⌜M⌝ = M, eval = I. Both are points of the modeled coset (①).
------------------------------------------------------------------------
homoiconic : UniversalEncoding
homoiconic = record { ⌜_⌝ = λ M → M ; eval = I ; decode = λ M → β-I M ◅ done }

-- the two instances agree on the METHOD (a universal interpreter that self-decodes), differ on the quote —
-- kwrap is genuinely non-trivial (⌜M⌝ = K∙M ≠ M), so it exercises the decode as a real reduction, not β-I:
kwrap-self-decode : ((S ∙ I ∙ (K ∙ I)) ∙ (K ∙ (S ∙ I ∙ (K ∙ I)))) ⇒* (S ∙ I ∙ (K ∙ I))
kwrap-self-decode = UniversalEncoding.self-decode kwrap

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — a universal encoding beyond homoiconicity, the codec COSET modeled, the
-- decode a POSITIVE reduction not a decision): the either/or "which non-trivial encoding? (Scott? Gödel?
-- K-wrap?)" DISSOLVED (D-model-the-coset) — model the SPACE: a UniversalEncoding interface (①, ⌜·⌝ + eval +
-- the decode LAW), from which the self-interpreter properties DERIVE (self-decode = decode at M=eval, the
-- metacircular self-decoding; carries-confluence = the system CR, 266's confluence-not-decidability method).
-- A specific encoding is one point of the coset: K-wrap (②, ⌜M⌝ = K∙M ≠ M, eval = SI(KI)) is a NON-TRIVIAL
-- one, with an EXPLICIT 4-step decode reduction (β-S/β-I/β-K/β-K) — a genuine universal interpreter that
-- decodes any M and its own code (kwrap-self-decode); homoiconic (③, 266) is the trivial point. The decode
-- is a REDUCTION (positive), NOT a decidable predicate (D-no-classical-spook) — confluence gives its
-- uniqueness. This is Lawvere at Lawvere's fixed point at a REAL encoding: the universal interpreter decodes
-- its own quote back to itself, positively, carrying confluence by construction. Chain: 266 (homoiconic
-- self-interp via confluence) → 267 (the codec coset + a non-trivial universal instance).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the UniversalEncoding interface (the codec coset) with derived
-- self-decode + carries-confluence; the NON-TRIVIAL K-wrap instance (explicit decode reduction + self-decode);
-- the homoiconic instance. SCOPED (reused-in-spirit, no spook): a FULL STRUCTURAL Scott/Mogensen encoding —
-- ⌜S⌝/⌜K⌝/⌜I⌝ distinct selectors, ⌜M∙N⌝ = a pair of ⌜M⌝/⌜N⌝, and eval = Y-of (recurse over the structure),
-- proving eval ∙ ⌜M⌝ ⇒* M BY INDUCTION on M (⟡extrude-self-interp-scott) — K-wrap is a non-trivial universal
-- eval (decodes any M uniformly) but NOT the structural one (it doesn't recurse into subterms); discharging
-- CR for R._⇒_ (⟡ski-cr-port). What's grounded: a universal encoding beyond homoiconicity exists, its decode
-- is a positive reduction, it self-decodes, and it carries confluence by construction — the codec coset,
-- non-trivially instantiated.
------------------------------------------------------------------------
