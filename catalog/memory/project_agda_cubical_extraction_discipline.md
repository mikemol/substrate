---
name: project-agda-cubical-extraction-discipline
description: "The Agda port has a Python-extraction goal — the proof structures should serve as a mold for a Python rewrite. Cubical Agda is allowed only in its extractable subset (Path + Iso + transport); HITs, hcomp, and Glue are forbidden because they don't extract cleanly."
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

The substrate Agda port ([../../agda/](/home/mikemol/github/substrate/agda/))
has a downstream goal: serve as a mold from which a Python rewrite
can be mechanically reconstructed. This constrains which Agda
features are permissible.

**Why:** The user's framing (2026-05-15): *"I wonder if we'll
sacrifice being able to export the constructive-proof structures in
order to mechanically reconstruct a python script using the proof
structures as a mold."* The mold property requires that every
`--safe` Agda declaration produce a clear Python correlate (records →
dataclasses, types → classes, functions → functions). Proofs are
auxiliary — they extract to discarded correctness witnesses, not to
runtime code. But the *structural skeleton* (data declarations, type
signatures, record fields) must be Python-translatable.

**Which cubical features are extractable**:

- **Path types** (replacing `_≡_`): extract by elision. Equality
  proofs are erased at runtime.
- **transport**: extract as conversion-via-isomorphism, often as a
  no-op if the underlying data is identical at the implementation
  level.
- **`Cubical.Foundations.Isomorphism` / `.Equiv`**: extract as
  bidirectional conversion functions paired with witnesses.
- Functions and records that USE these primitives but don't expose
  Kan operations in their public API.

**Which cubical features are forbidden** (don't extract cleanly):

- **Higher Inductive Types (HITs)** with path constructors. A
  quotient HIT has constructors of multiple kinds (point + path)
  that Python can't represent natively. The Python equivalent
  forces a canonical-representative choice, which **reintroduces
  Type-D rigidification at the extraction boundary** — the exact
  failure mode the substrate is designed to avoid.
- **`hcomp` (homogeneous composition)** inside data: Kan-filling has
  computational content with no simple Python translation.
- **`Glue` types** for univalence: meaningful in cubical type
  theory, alien at extraction.

**Discipline rule** for the Agda port:

1. **All type declarations live in `--safe --without-K`-compatible
   syntax.** This is the public API and the extraction boundary.
2. **Cubical is a proof technique, not a data-structure choice.**
   Cubical modules can prove properties OF `--safe` types via
   path-equality and transport, but cannot introduce new data shapes
   (HITs forbidden).
3. **Where symmetry-transport saves substantial proof effort**
   (e.g., compressing the 40-case `act-axis-∙` via S₃-orbit
   isomorphism, or the 13,824-case M40 aggregator), cubical Agda is
   permitted — but ONLY using Path + Iso + transport.
4. **Test the extraction property concretely** when introducing
   cubical: prototype both `--safe` enumeration and cubical
   transport for the same theorem; verify that the extracted record
   shapes are identical and the cubical version is smaller in proof
   body. If the cubical version changes the data declarations, it
   has crossed the extraction boundary and should be refactored or
   rejected.

**How to apply:**

- Tier B (already done: V₄ + CocycleStructure + V₄Signature) is
  `--safe --without-K`. Maintain this; do not retroactively cubical-
  ise.
- Slice 2 (S7 + S8: S₄ + V₄ embedding) is `--safe`. The 40-case
  `act-axis-∙` is irreducible at this scope, accepted as the cost of
  the extraction discipline.
- Slice 3 onwards: when a theorem's case-count would exceed ~100,
  introduce cubical (Path + Iso + transport only) in a separate
  module that proves the theorem; the underlying data types remain
  in `--safe` modules.
- Document the extraction discipline at the top of every cubical
  module: *"This module uses cubical for proof technique only.
  All exported types are extractable via the `--safe` correlate at
  [...]."*

**Cross-references**:

- [[project-retrospective-as-navigation-aid]] — the substrate Agda
  port's place in the project.
- catalog/cocycles.md § Isomorphic storage — the discipline this
  extraction property protects.
- catalog/clarified_foundation.md rule 11 (strong) — the rule the
  Python rewrite is meant to satisfy.
