# Eliza Codec ↔ Substrate Agda

The codec's architecture mirrors specific Coxeter constructions in
`agda/Substrate/Groups/`. This bridge document records the
correspondences so the runtime types stay aligned with the formalism.

## Dimensional correspondence

| Codec dimension | Codec module | Agda construct |
|---|---|---|
| 1: input grammar | `eliza/sequitur.py` (input alphabet) | `Substrate.Groups.FreeCyclic-Coxeter` — free monoid on one generator, no relations |
| 2: + rotation grammar | `eliza/dim2_codec.py` | `DirectProduct(FreeCyclic, Z_16)` — 2-D word algebra from `Substrate.Groups.Coxeter.DirectProduct` |
| 3: + CD-rung choice | (future) | Coxeter extension order: V₄ → H → O → S sacrifice ladder |
| 4: + patch / RM rung | (future) | Reed-Muller layering as a quotient of the rotation grammar |
| 5: + B-frame back-ref | (future) | Chirality F₂ from `Substrate.Hodge.*` (time-reversal axis) |
| 6+: + multi-scale | (future) | Recursive CD doubling — suffix-array merge as the `combine` op |

## Specific correspondences

### `Sequitur_input` ↔ `FreeCyclic-Coxeter`

The input Sequitur observes a stream of input symbols and builds rules.
Its "alphabet" has no relations between symbols — every sequence is
canonical until a duplicate digram is observed. This matches
`FreeCyclic-Coxeter`'s "no relation" Coxeter presentation:
`canonical-is-fixed-Free` says every word is in canonical form by
default; rule promotion adds structure.

The Agda's `insert g w = g ∷ w` is `Sequitur.observe(g)` modulo the
digram-uniqueness rewrite.

### `Sequitur_rotations` ↔ `Z_16-Coxeter`

The rotation Sequitur observes a stream of rotation choices, each ∈ [0,16).
The alphabet has bounded order: under the F₂³ × F₂ group structure of
`eliza.octonion.ROTATIONS`, each rotation is an involution (order 2),
and the group is `(F₂)⁴ ≅ V₄ × V₄` (16 elements, abelian).

This is `Z_2 × Z_2 × Z_2 × Z_2` as a Coxeter group, which is a specific
instance of the substrate's `Zₙ-Coxeter` family. Each axis is `Z_2`;
the product is the rotation alphabet.

### `chooser` ↔ DirectProduct 2-cell

The chooser couples the two Sequiturs. Given an input window, it:
1. Computes the window's recursive-2-bin signature.
2. Asks the rotation Sequitur which rotation matches this signature.
3. The rotated window feeds back into the input Sequitur's predictor.

Algebraically, this is the universal property of `DirectProduct`:
the pair `(input_position, rotation)` is an element of the product
algebra, and the chooser is the universal map that constructs it.

In `Substrate.Groups.Coxeter.DirectProduct`, the 2-D word algebra's
`canonical` form is the pair `(input_canonical, rotation_canonical)`.
The codec's encoded stream IS this 2-D canonical form, serialized.

## Categorical type emission

`dim2_codec.encode()` returns `(encoded_bytes, stats)` where
`stats["categorical_type"]` is the string label:

```
DirectProduct(FreeCyclic_input, Z_16_rotations)
```

A future slice could promote this to a structured type that an Agda
type-checker can ingest, verifying that the codec's runtime witness
matches the algebraic shape. The structured form would be roughly:

```agda
record DimNCodecType : Set where
  field
    axes : List CoxeterPresentation
    couplings : List (Σ[ i ∈ ℕ ] (i < length axes × Σ[ j ∈ ℕ ] (j < length axes × ChooserSpec axes i j)))
```

with `dim2` being the case `axes = [FreeCyclic, Z₁₆], couplings = [(0, 1, ...)]`.

## Higher dimensions

Per the substrate's tetrative metacircularity, the dimension stack does
not terminate. Each new architectural axis (B-frames, patches, multi-
scale BWT) opens a new dimension, adds a Sequitur, and contributes a
new 2-cell. The N-th dimension's coherence is an (N-1)-cell over the
(N-2)-cells beneath.

The codec doesn't need to know its full dimension at construction time.
It can grow dimensions as `Sequitur_rotations` (or any higher rotation-
Sequitur) requests more resolution — a Sequitur rule promotion at depth
d in the recursive 2-bin signature IS a request to increase signature
depth to d+1, which IS a request to lift the chooser one dimension.

## File-level cross-references

- `eliza/octonion.py` — 16-rotation table. Substrate analog: any
  `Substrate.Groups.Coxeter.*` over 4 binary generators (V₄ × V₄
  presentation).
- `eliza/signature.py` — recursive 2-bin histogram. No direct Agda yet;
  conceptually equivalent to a Reed-Muller code's truncated information
  word.
- `eliza/sequitur.py` — input grammar. Substrate analog:
  `Substrate.Groups.FreeCyclic-Coxeter` (modulo the digram-uniqueness
  invariant which is Sequitur-specific).
- `eliza/dim2_codec.py` — encoder/decoder. Substrate analog:
  `Substrate.Groups.Coxeter.DirectProduct` applied to the two axes
  above.
