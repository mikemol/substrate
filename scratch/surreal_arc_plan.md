# Conway Surreal Numbers arc — 10-slice plan

Planned per [[project-surreals-term-algebra-alignment]] and
[[feedback-q-over-r-constructive]]. Surreal numbers as the recursive
numeric carrier that goes beyond ℚ, landing on the substrate's
existing term-algebra infrastructure.

## Why this arc

Per the user's observation: Conway's surreals (`{L | R}` recursively)
are an unusually natural fit for the substrate's term-algebra
primitives ([[feedback-prefer-coxeter-backed]], [[project-rarc-lambda-vm-recognition]],
[[project-substrate-native-recursive-grammar]]). The recursive
constructor shape that the codec arc and Coxeter Word already host
extends directly to surreals when L/R bounds are carried by
Coxeter Word.

Surreals also fulfil the [[feedback-q-over-r-constructive]] discipline:
they're the universal recursive-decision-structure number system,
containing ℚ, ℝ, dyadic rationals, infinitesimals, and ordinals,
with every number carrying its construction tree as part of the
type.

## Constructive challenge: termination

Standard Conway surreals are mutually-recursive with their order
relation; constructive Agda needs a termination measure. Options:

- **Sized types** — not `--safe`.
- **Well-founded recursion** — possible but heavy.
- **Birthday-indexed types** — `SurrealFinite n` is the set of
  surreals reachable by day n; operations preserve / decrease the
  birthday. Total, decidable, and `--safe`-compatible.

This arc uses the **birthday-indexed** approach. The constructor
`⟨_∣_⟩` at birthday `suc n` takes Word-collections of `SurrealFinite n`
inhabitants (lower birthday) for L and R.

## Costructure shadows

- **`SurrealFinite n`** — birthday-bounded recursive carrier, with
  L and R bounds carried by `Substrate.Groups.Coxeter.Word`.
  Universal property: any function `Surreal-spec → SurrealFinite n`
  extends by structural induction on birthday.
- **`_≤ⁿ_`** — birthday-bounded recursive order. Universal
  property: at each finite birthday, comparison is decidable and
  the order laws (reflexivity, transitivity, antisymmetry-up-to-≡)
  hold.

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `⟨_∣_⟩` | `Word (SurrealFinite n) → Word (SurrealFinite n) → SurrealFinite (suc n)` | constructor |
| `promote` | `SurrealFinite n → SurrealFinite (suc n)` | birthday lift |
| `_≤ⁿ_` | `SurrealFinite n → SurrealFinite m → Set` | order |
| `_+ⁿ_` | `SurrealFinite n → SurrealFinite m → SurrealFinite (n + m)` | addition |
| `-ⁿ_` | `SurrealFinite n → SurrealFinite n` | negation |
| `ℤ→S` | `ℤ → SurrealFinite ⌜|n|⌝` | integer embedding |

## Entailment claim

```
RecursiveBirthdayCarrier(SurrealFinite) → BirthdayDecreasingTermination
  → ∀ (s : SurrealFinite n). DecidableComparison ∧ ComputableArithmetic
```

Birthday-strict-decreasing recursion is the termination certificate
discharged at S2; everything else follows by structural induction
over the birthday measure.

## Ten slices

Annealing discipline ([[project-annealing-methodology]]) — one
degree of freedom per slice, typecheck between each. Per
[[feedback-file-size-one-pass-rewrite]] one Write per file.
Per [[feedback-minimize-stdlib-deps]]-strengthened: substrate-native
primitives throughout, no `Data.List` (use `Substrate.Groups.Coxeter.Word`).

### Phase 1 — Carrier (S1-S3)

- **S1 `Substrate.Conway.SurrealFinite`** — the birthday-indexed
  recursive carrier. `SurrealFinite : ℕ → Set` with constructor
  `⟨_∣_⟩ : Word (SurrealFinite n) → Word (SurrealFinite n) →
  SurrealFinite (suc n)` (lower-birthday bounds). Day-0
  inhabitant: `Zero = ⟨ [] ∣ [] ⟩ : SurrealFinite 1`.

- **S2 `Substrate.Conway.Birthday`** — birthday query function +
  monotonicity lemmas. `birthday : SurrealFinite n → ℕ`;
  `birthday s ≤ n` by induction. The termination certificate that
  S4 / S6 / S7 consume.

- **S3 `Substrate.Conway.Examples`** — worked Day-0 / Day-1
  inhabitants: `Zero`, `One = ⟨ Zero ∷ [] ∣ [] ⟩`,
  `NegOne = ⟨ [] ∣ Zero ∷ [] ⟩`. Demonstrates the recursive shape
  on concrete values; smoke tests via `_≡_` against expected
  constructor patterns.

### Phase 2 — Order (S4-S6)

- **S4 `Substrate.Conway.Order`** — recursive `_≤ⁿ_` definition.
  At Conway's definition: `x ≤ y ⟺ no x_L ≥ y ∧ no y_R ≤ x`.
  Birthday-decreasing structural recursion; total within finite
  birthday.

- **S5 `Substrate.Conway.OrderLaws`** — reflexivity (`x ≤ x`),
  transitivity (`x ≤ y → y ≤ z → x ≤ z`), proven by structural
  induction on birthdays. The two laws together give the partial-
  order structure.

- **S6 `Substrate.Conway.Equivalence`** — surreal equivalence
  `x ≈ y ⟺ x ≤ y ∧ y ≤ x`. Equivalence classes are the actual
  surreal numbers (distinct constructions of the same value).
  Decidability of ≈ at finite birthdays.

### Phase 3 — Arithmetic (S7-S8)

- **S7 `Substrate.Conway.Add`** — surreal addition recursively.
  `x + y = ⟨ x_L + y, x + y_L ∣ x_R + y, x + y_R ⟩`. Birthday-
  bounded: `x : SurrealFinite n` + `y : SurrealFinite m` lives in
  `SurrealFinite (n + m)`. Recursive descent on either summand's
  birthday.

- **S8 `Substrate.Conway.Neg`** — surreal negation `-_`.
  `-⟨ L ∣ R ⟩ = ⟨ -R ∣ -L ⟩` (swap L and R, negate each).
  Birthday-preserving. Key identity: `x + (-x) ≈ Zero`.

### Phase 4 — Bridge (S9-S10)

- **S9 `Substrate.Conway.IntegerEmbedding`** — embed ℤ into
  surreals. Each `n : ℕ` corresponds to a surreal at birthday `n`
  built by iterated `One + ...`. Negative integers via negation.
  Demonstrates that ℤ ⊆ SurrealFinite via the recursive
  construction, and that integer arithmetic agrees with surreal
  arithmetic up to ≈.

- **S10 `Substrate.Conway.AsCone`** — categorical home: a
  `SurrealFinite (suc n)` is a Cone with two-element apex shape
  (L-bounds, R-bounds as legs) over the `SurrealFinite n` base.
  Plugs into [[project-3plus1-is-cone-instance]] /
  Substrate.Category.Cone infrastructure. Sets up the eventual
  bridge to FreeLinearization / OpcodeAlgebra — surreal arithmetic
  is recursive evaluation in a substrate-CCC. Per
  [[feedback-coalgebraic-not-consumer-driven]] the full CCC
  embedding is deferred; the Cone bridge is the immediate
  categorical home.

## Substrate primitives engaged

- Substrate.Groups.Coxeter.Word (L/R bound carriers)
- Substrate.Category.Cone ([[project-3plus1-is-cone-instance]])
- Birthday-indexed types (Data.Nat only, no stdlib heavy lifting)
- Eventually: Substrate.Category.FreeLinearization + OpcodeAlgebra
  via S10's setup

## Deferred (out of arc)

- Surreal MULTIPLICATION (definable but with much harder
  termination; deferred).
- Surreal DIVISION and inverse (similarly deferred).
- ω, infinitesimals, transfinite surreals (require birthday > ω;
  transfinite induction outside `--safe` initial scope).
- Game-as-surreal connection (Hackenbush, partizan games).
- Full ℝ embedding via Dedekind-cut-style surreal sequences.

Per [[feedback-coalgebraic-not-consumer-driven]]: these surface
when a consumer requires them; the 10-slice fragment lands the
foundational carrier + finite arithmetic + categorical home.

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. S5 proves reflexivity + transitivity at finite birthdays.
3. S8 proves `x + (-x) ≈ Zero` at finite birthdays.
4. S9 demonstrates `Two ≈ One + One` and `Three ≈ One + Two`
   etc. as worked integer-embedding examples.
5. S10 instantiates Substrate.Category.Cone with the surreal
   apex-and-bounds shape, surfacing the categorical home.

## Connection to prior arcs

The Lojban + Toki Pona linguistic Rosetta arc closed the discrete/
linear pair ([[project-linguistic-rosetta-arc]]). This Conway arc
adds a THIRD substrate-witness of the recursive-term-algebra pattern,
which per [[feedback-coalgebraic-not-consumer-driven]] is the
threshold for extracting a shared parent primitive ("Free
recursive carrier over basis"). The extraction is itself deferred;
this arc produces the third instance that licenses it.

Per [[project-tetrative-metacircularity]]: surreals are the
numeric-carrier instance of the substrate's tetrative pattern —
each surreal carries its construction tree, the construction tree
admits sub-surreals as nodes, and the recursion continues
indefinitely. The Conway arc lands the L0-L1 levels of that
tetrative tower at the numeric layer.
