------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.EkeyRoundtrip
--
-- Defines: parse-render-kids
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.EkeyRoundtrip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lifecycle.Fragment.Ekey
open import Substrate.Lifecycle.Fragment.EkeyCodec


------------------------------------------------------------------------
-- THE SERIALIZER-INVERSE LEMMA, prefix-closed.
--
-- ⚑⚑⚑ THIS IS THE LEMMA THE ARC SAID WAS "STATED NOWHERE", and the honest
-- version of it is narrower than the phrase suggested. What was missing is
-- `render ∘ parse ≡ id` for the ekey codec; what is provable — and what
-- `TmDBGodel.parse-godel` proves for its own codec — is the PREFIX-CLOSED
-- form:
--
--     parsing (render x ++ rest) returns (x , rest)
--
-- The bare form is the special case at `rest = []`. Stating it prefix-closed
-- is not a technicality: it is what makes the induction available at the
-- concatenation point, and a proof of the bare form alone does not compose.
--
-- ⚑ NO FUEL IS NEEDED HERE, AND THE REASON IS STRUCTURAL. `TmDBGodel` needs
-- `parse-fuel` because its grammar is RECURSIVE — `app f x` nests terms, so
-- the parser must recurse on unknown depth and Agda cannot see termination.
-- The child list is FLAT: a length then that many words, one level, no
-- nesting. `takeWords` recurses on the ℕ it was handed, which is structural,
-- so the whole codec is total by construction. **The simpler grammar is what
-- removes the fuel** — not a cleverer proof.
--
-- ⚑ WHAT THIS DOES AND DOES NOT CERTIFY, said plainly:
--   DOES — the STRUCTURAL codec is a retraction: a rendered child list parses
--          back to itself, with the following tokens intact and untouched.
--   NOT  — that the STORE's rendering is. This models a length-prefixed
--          encoding; the store delimits with `", "` and closes with `]`. The
--          length prefix is the stronger choice (see `EkeyCodec`), so this
--          proof does not transfer to a delimiter scan for free — a
--          delimiter-based reader is injective only if no payload can contain
--          the delimiter, which is a separate obligation about the ALPHABET.
--   NOT  — anything about postgres's `to_json` escaping or base64 wrapping.
--          Those are byte-layer concerns, deliberately left as a named
--          hypothesis rather than modelled.
--
-- ⚑⚑ AND THE DIRECTION MATTERS FOR WHAT IT PROTECTS. `TmDBGodel`'s header:
-- *"godel is INJECTIVE-not-surjective, so it is the SECTION and ungodel the
-- retraction — the reverse of a naive `split-Canonical godel ungodel`."*
-- Render is the section. Injectivity of render is the property that stops two
-- structurally distinct sources rendering identically — which is exactly the
-- failure a byte-comparison drain check could not detect, since it would
-- compare equal and pass.
------------------------------------------------------------------------

-- The word-payload prefix a child list renders to, followed by `rest`.
take-words : (ks : List ℕ) (rest : List Tok) → List Tok
take-words []       rest = rest
take-words (k ∷ ks) rest = word k ∷ take-words ks rest

-- The list's length — the count the renderer writes as its prefix.
-- ⚑ TOP-LEVEL, NOT A `where` ON THE SIGNATURE. The first draft put it in a
-- `where` attached to the TYPE of the lemma below, which is not Agda: a
-- `where` scopes over a definition's clauses, never over its signature. The
-- measure has to be in scope for the type to mention it at all.
lenOf : List ℕ → ℕ
lenOf []       = zero
lenOf (_ ∷ xs) = suc (lenOf xs)

-- The prefix-closed round-trip for the child-list codec.
parse-render-kids :
  (ks : List ℕ) (rest : List Tok) →
  takeWords (lenOf ks) (take-words ks rest) ≡ (ks , rest)
parse-render-kids []       rest = refl
parse-render-kids (k ∷ ks) rest
  rewrite parse-render-kids ks rest = refl
