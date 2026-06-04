# Type SPPF — motifs & isomorphisms (first pass, 2026-06-03)

Passing every `data`/`record` type through the wedge bottom-up: hash-cons the
structure (sub-type references replaced by the referenced type's structural
hash; recursion/mutual-ref = the SPPF cycle node `⟲`). Isomorphic types collapse
to one node; shared sub-shapes are motifs. Tool: `scripts/type_sppf.py`.

493 types → **411 distinct structural nodes**, **34 isomorphism classes** (≥2
types with identical structure up to sub-iso). The wedge's keep/forget reads
here: the *node hash* is the forget (collapse iso), the *class membership* is
the keep (which types share it).

## Isomorphism classes, triaged

- **Enum-by-arity (the bulk).** Finite types collapse by constructor count:
  - 2-enums (one node): `Bool`, **`F₂`** (≅ Bool — a real math iso),
    `BindingClass`, `EmissionSource`, `Permanence`, `SourceClass`, … (7).
  - 3-enums: **`Unfold`** (my `halt|loop|stop`), `Terminal`, `TenseMarker`,
    `SylowClass`, `HistoryPhase`, `LieGen` (6).
  - a 15-member small-enum/atom class (`Axis`, `Chirality`, `Gen`, `Line`,
    `Point`, `Pairing`, …).
  These are expected and mostly fine — each names a *distinct domain
  distinction* even though the carrier shape is shared. (The motif is "a finite
  set of K atoms"; the content is what the atoms *mean*.)

- **Empty-record / ⊤ class — structurally vacuous.** `TwoNaturalTransformation`,
  `TwoEquivalence`, `Preserves-CountMonoid/Ranking/Shannon/V4` collapse to `⊤`
  (no fields). Two sub-kinds:
  - *nominal tags* used as marker VALUES (`homomorphism-tag = Preserves-V4`) —
    `⊤`-content is correct for a tag (legit).
  - *signature-only stubs* ("substrate names the carrier; user supplies the
    data") — `TwoNaturalTransformation`/`TwoEquivalence`. Same family as the
    UP-topos `*-stated : Set` obligation surface / `SubstrateTopos`, but at the
    record-emptiness level. These are the broadened-vacuity finds: named
    concepts with no structural content. Decide per case (keep as declared
    placeholder, or fill).

- **Term-algebra families — generic-ization candidates.** `CascadeGen ≅ ConjGen
  ≅ LensGen` (single generator) and `CascadeTerm ≅ ConjTerm ≅ LensTerm` (free
  cons-list over it). The term-algebra-bridge construction repeated per domain
  (Cascade/Conj/Lens, and the DFT/Char/Pontryagin `*Gen` siblings). Exactly the
  pattern the generic `Coxeter.Cyclic` collapsed for `Zₙ`; a generic
  `TermAlgebra Gen` would absorb these.

- **Quantity families:** `ConditionalEntropy ≅ JointEntropy ≅ KLDivergence`
  (info-theory measures); `Cascade/Conj/Lens` Term/Gen as above.

## Top structural motifs (recurring field-shapes — the repo's DNA)

| count | shape | reading |
|---|---|---|
| 354 | `Set` | a Set-typed field — obligation slot / type parameter |
| 310 | `⟲` | self/mutual reference — recursive types |
| 214 | `→` | a function field |
| 109 | `→ ≡` | a field that is an EQUATION — a law |
| 80 | `ℕ` | a ℕ-indexed field |
| 62 | `Set₁` | a higher Set field |

So the structural DNA is: **obligations (Set) + recursion (⟲) + functions (→) +
laws (→≡)**. Records of laws over recursive carriers — the algebraic spine.

## Caveats & next

- The skeleton extractor is line-based and drops vars/implicits; **enum and
  empty-record signals are reliable**, deep-structure isos approximate. This is
  the "begin constructing the SPPF" pass.
- Next: (a) refine the parser (telescopes/implicits); (b) generic-ize the
  term-algebra `Gen`/`Term` families (one motif → one generic); (c) decide the
  empty-record signature-stubs (tag vs fill); (d) walk the SPPF *up* the dep
  chain to find cross-LAYER motifs (a foundation shape recurring at a high layer
  = an isomorphism across silos — the north-star bridge, found structurally).

## Cross-layer ranking (2026-06-03) — `scripts/type_sppf_crosslayer.py`

Ranked the 34 iso classes by the dependency-depth span their members cross
(annotated with silo-count and structural weight). The classes split into two
honest KINDS of motif — neither is noise (correction to an earlier draft that
mislabeled the enums "noise"):

- **PATTERN motifs** — one design pattern, many *independent* instances with
  *different* meanings. The widest class (span 16-17, 8 silos) is the **finite
  enum** (`Distinction-Name`, `Selector`, `SylowPrime`, `Axis`, …): a finite set
  of named atoms = a **forced distinction = a partition**. This is the
  substrate's most fundamental and most-recurring motif — the partition
  primitive ("Peano derives from partition") realized at the type level. Its
  ubiquity is the *signal of its fundamentality*, not an artifact. You CATALOG
  pattern motifs (they are the substrate's vocabulary); you do NOT collapse
  them (`Distinction-Name` and `SylowPrime` are *different* partitions).

- **CONVERGENCE motifs** — different-named things that may be the *same*
  construction (bridge candidates). These are the RICH classes: high weight,
  contentful shape, members plausibly unifiable:
  - **`Character ≅ FieldBond ≅ FreeOverBasis`** — all `record { f : A → B }`,
    a single wrapped morphism. `FreeOverBasis.η` IS the free-construction unit
    (the center); so the Pontryagin character (`chi`) and the field-tower bond
    (`bond`) are *structurally the center's unit*. A real bridge: the
    morphism-carrier / unit motif recurring across 3 silos.
  - `Dec ≅ Either` — binary sum (Dec is a specialised Either).
  - `ConditionalEntropy ≅ JointEntropy ≅ KLDivergence` — info-theory measures.
  - term-algebra `Gen`/`Term` families (weight 11, the richest) — one motif,
    a generic begging to be written.
  - the `≃`-witness shape (`Live≃Permutation`, `TotalSpace≃S₄`).

- **The level discipline (correction):** at this level **shapes are primary**,
  by design. The SPPF is the substrate's **shape algebra** — the carrier-free
  structural base (`Shape.agda` for *all* types: a type = a carrier-free shape +
  a carrier filling its positions). Same-shape *is* the primary identity; the
  differing meanings are the **fiber** over the shape, not evidence the shape is
  wrong. So:
  - Do NOT "filter" the enums or treat shape-iso as coincidence — the shapes are
    the object. The widest shape is the partition; that it is widest is the
    truth, not noise.
  - PATTERN vs CONVERGENCE is a **fiber-level** question (do two members' fibers
    coincide?) layered *over* the primary shape classes — a separate, optional
    ascent, NOT a "resolution fix" to the shape level. Typed skeletons would
    climb to the fiber, not repair the base.
  - The right primary deliverable is therefore a **catalogue of the shape
    alphabet** (each iso class = one primary shape), with the fiber (which
    meanings sit over each shape) as a second, derived layer.

## Reaction-primary inversion (POSIWID) — `scripts/type_reaction.py`

Further correction (per user): *meaning is use; a system's purpose is what it
does*. So the enumerators are NOT primary — **what reacts to them is**. Profile
each type by its eliminators (functions `f : … T … → R`: T consumed, `R` the
reaction). Evidence the inversion is right — the introduction-iso enum class
*fragments completely* by reaction:

| type (one shape) | reacts → (its meaning) |
|---|---|
| `SylowPrime` | `ℕ` (indexes a prime) |
| `Chirality` | `F₂` (a binary sign) |
| `Selector` | `Bool`, `Permutation` (selects/decides) |
| `Axis` | `V₄`, `Permutation`, `Stab≃S₃` (a geometric thing groups act on) |
| `Gen` | `Word`, `Dec`, `Canonical` (builds words, decides) |
| `Line` | `Point` (incidence) |

Identical as partitions, distinct as meanings. And reaction-keying recovers
**use-based classes introduction missed**: `{BackedUP, Interop}`, `{ℚ, ℤ}`,
`{Gen, Word}`, `{Mode, WedgeCoalg}` (all → `Bool`/decisions).

This is **Free ⊣ Forgetful one level up**: the introduction-SPPF is the
constructor/Free view (how built); the reaction-SPPF is the observation/
Forgetful view (how used). Meaning lives on the Forgetful/use side — a finite
enum is Free-trivial and means nothing until its eliminators give it behavior.
So the PRIMARY catalogue is **reaction-keyed** (the cover / "expose generator"
shape over each distinction); the introduction shape is the secondary index.
