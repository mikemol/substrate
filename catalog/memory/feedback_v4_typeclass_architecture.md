---
name: feedback-v4-typeclass-architecture
description: "Canonical architecture for V₄ and other finitely-presented small groups in Substrate is the COXETER FRAMEWORK (Substrate.Groups.Coxeter.{Core, ListPresentation, DirectProduct, Word}). New presentations instantiate Coxeter.Core via a wrapper. V4-Generic + V4-Index (the original F₂² typeclass) were retired in Slice 5. DO NOT pattern match on V₄/Axis ctors for algebraic property proofs."
metadata:
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Rule:** For any finitely-presented small group in Substrate, ALGEBRA goes through the **Coxeter framework**:

- `Substrate.Groups.Coxeter.Word` — self-contained `Word`/`[]`/`_∷_`/`_++_`/`++-assoc` (avoids Data.List clash friction).
- `Substrate.Groups.Coxeter.Core` — abstract parametric module over `(Word, ++, ε, Canonical, normalize, normalize-distrib)`. Provides `_·_`, `_≈_`, `_≉_`, `ε`, `normalize-{idem,append,append-right,cong-right,distrib,triple,quad}`, `≉-idem`, `clash`, `++-assoc-4`.
- `Substrate.Groups.Coxeter.ListPresentation` — List-Gen wrapper for direct Coxeter presentations (Z/2, V₄ via ⟨A,B | A²=B²=ε, AB=BA⟩).
- `Substrate.Groups.Coxeter.DirectProduct` — combinator producing the Core for a product of two Cores (Z/2 × Z/2 = V₄, etc.).

**For a new finite-group instance, the work is:**
1. Define `Gen` (data type).
2. Define `Canonical : Word Gen → Set` (the normal-form predicate).
3. Define `insert : Gen → Word Gen → Word Gen` (the relation-driven canonicalisation step).
4. Define `insert-canonical`, `canonical-is-fixed`, `insert-append-lemma` (proof obligations encoding the specific Coxeter relations).
5. `open import Substrate.Groups.Coxeter.ListPresentation <atoms> public` and `open WithLemmas <proofs> public`. Inherits the full Core surface.

**Existing instances** (use as templates):
- `Substrate.Groups.Z2-Coxeter` — Z/2 = ⟨a | a²=ε⟩. Smallest non-trivial. Includes `self-inverse` theorem.
- `Substrate.Groups.V4-Coxeter` — V₄ = ⟨A,B | A²=B²=ε, AB=BA⟩. Includes `V₄-4-product` theorem (124-pattern enumeration of 4 distinct V₄ elements).
- `Substrate.Groups.V4-as-Z2xZ2` — V₄ as direct product, via DirectProduct combinator. Demonstrates compositionality.

**`Substrate.Groups.V4` (the user-facing V₄)** is now a thin adapter:
- Keeps the 4-ctor `data V₄ : Set with e/α/β/γ` (preserves downstream pattern matches).
- Routes all algebra (`_·_`, axioms, Group bundle) through V4-Coxeter via a `to-c`/`from-c` bijection.
- `V₄-4-product` is delegated to V4-Coxeter's version via the bijection (~25-line wrapper vs the previous 124-pattern enumeration).
- No more F₂² index typeclass; no more V4-Generic; no more V4-Index.

**Why:** the original F₂²-based V4-Generic was a single-group abstraction. The Coxeter framework abstracts the PATTERN (presentation → group), so adding S₃, S₄, D_n, (Z/2)ⁿ, etc., is a 80-150 line per-instance cost vs duplicating the entire group construction. The framework was extracted in Slices 1-4 of the Coxeter migration; V4-Generic + V4-Index were retired in Slice 5. See [[feedback-composable-primitives-over-flat-enumeration]] for the meta-principle.

**For NEW algebraic proofs about V₄-symmetric spaces:**
- Use the operations exported by V4 (which come from V4-Coxeter via the adapter).
- Pattern matching on V₄ ctors is fine in the V4.agda adapter itself (4 ctors, exhaustive case analysis is small). For DOWNSTREAM proofs about V₄ or Axis, prefer composing through the V4-Coxeter foundation when the theorem is non-V₄-specific.

**Reduction caveat:** under the Coxeter-backed `_·_`, equalities like `e · h ≡ h` (h abstract) are NO LONGER definitional — they require applying `ε-left h`. Direct `refl` proofs of `act-id` etc. need to be replaced with `cong` chains through `ε-left` / `ε-right`. (This was already the case for V4-Generic's F₂² backend; the situation is unchanged after the Coxeter migration.)

**Methodology lesson:** when stuck on a many-case Agda proof, the LLM-natural workaround is Python codegen / meta-programming that emits flat enumeration. That's a workaround for not having the native algebraic foundation. The user's correction: build the foundation in Agda via module parameterization + composable combinators, do not generate enumeration via Python. Per [[feedback-agreement-without-yielding]]: this directive applies forward in ALL substrate symmetry-group work.

Related: [[feedback-expose-generator-not-orbit]] (same anti-pattern for orbit enumeration). [[feedback-rotation-of-modular-spaces]] (the F₂² structural insight that originally motivated this; the Coxeter framework subsumes it as the abelian-exponent-2 case). [[feedback-composable-primitives-over-flat-enumeration]] (the meta-principle: prefer composable abstractions over flat enumeration even when line count grows).
