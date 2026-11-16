---
name: feedback-ordering-is-chirality-choice
description: "When formalising a bijection between sets where one side has an intrinsic ordering, any 'standard order' choice for indexing the other side is itself a chirality-level rigidification. The user pointed this out 2026-05-15 in the Stab(anchor) ↔ Fin 3 bridge — calling the ordering 'standard' would privilege one of 6 valid orderings, replicating Type-D drift at the chirality layer."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When formalising a bijection f : A ↔ B where:
- B is an indexed set (like Fin n) with intrinsic ordering, and
- A is a set whose elements have a NATURAL declaration order or
  alphabetical order or any "canonical" listing,

**writing "standard order" or "canonical order" for the index choice
IS A CHIRALITY-LEVEL RIGIDIFICATION** of the same shape as Type-D
drift at higher layers.

**Why:** A bijection f : A ↔ B with |A| = |B| = n is unique only up
to composition with an S_n permutation. Any of the n! orderings of
A gives an equally-valid bijection to B. Calling one "standard"
privileges that ordering as if it were structural fact, but it's a
chirality-level choice.

The user articulated this 2026-05-15 in the slice 14a context:

> "We have a standard order? I feel like that should be either
>  parameterized, or the ordering allowed to 'float'; having a
>  standard order is structural privileging at a chirality level."

**The rule:**

1. **Never call an indexing/ordering choice "standard" or "canonical".**
   These are CONVENTIONS, like the bit-position layout in
   `clarified_foundation.md` rule 7.

2. **Either parameterise the ordering** (let the caller supply it
   as an explicit ordering argument), **or document explicitly that
   the choice is a convention** that downstream code MUST NOT rely
   on, OR **let it float** (define the iso only up to S_n action).

3. **The bijection is unique up to S_n inner automorphism** — that's
   the structural fact. Any specific ordering choice that pretends
   otherwise inherits the rigidification.

**How to apply:**

- When writing a bridge like `Fin n → A` with multiple equally-valid
  orderings: name it `fin-to-A` (a specific convention), document
  that the convention is a choice, do NOT name it `canonical-fin-to-A`
  or `standard-fin-to-A`.
- Comments should explicitly say "this is a convention; downstream
  code MUST NOT depend on which one".
- When two such bridges exist (e.g., for two different anchors), the
  resulting isos differ by an inner automorphism — note this in
  comments to make the chirality-floating visible.

**Connection to other discipline rules:**

- This is a finer-grained version of
  [[feedback-multi-reading-ambient-discipline]]: the multi-reading
  rule says "don't privilege one reading"; the chirality-choice rule
  says "don't privilege one ordering within a reading".
- Compare with `clarified_foundation.md` rule 7 (bit-position layout
  convention) — same shape, lower layer.
- And [[feedback-choice-rigidification-in-substrate]] — sister rule
  for "the canonical" digests; this is the indexing-layer analogue.

**Examples in the substrate:**

- Slice 14a `Stab-S3.agda`: the Fin 3 ↔ non-anchor-axis bridge
  uses one specific ordering. Comments now call this a convention
  per this rule, not "standard order".
- The 6 named Stab(D) elements in slice 4's `S4Iso.agda` follow a
  similar naming convention (stab-id, stab-sw, stab-cs, etc.). The
  names imply an ordering. They are conventions.
- The bit-layout in slice 10's `Codeword.agda` (b₀ b₁ axis,
  b₂ sign, b₃ b₄ reserved-marker) is also a convention; the
  Codeword module's header documents this explicitly.
