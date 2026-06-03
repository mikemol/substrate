# The wedge groupoid: consolidation map

This session built one foundation in two arcs that meet at a groupoid. This is
the map of what's there, how it fits, and what's deliberately left open.

## The foundation: `Substrate.Algebra.Wedge.*`

The wedge `a = q·b + r` as a carrier-generic operator, and everything that
falls out of it. All `--safe --without-K`, zero postulates, one process per
file (the directory makefile builds the arc green).

| module | role |
|---|---|
| `Algebra/Wedge` | `DivStr` (carrier interface), generic `Wedge`, the three reads (`forget`/`cell`/`Trace`); ℕ wedge & `EEATrace` fall out as instances |
| `Wedge/Adjunction` | `Free ⊣ Forgetful` uniform; `=` is the wedge's `(1,z)` corner |
| `Wedge/Reads` | the reads **are** `gcd-fold` / `mod` / `bezout-ℤ` |
| `Wedge/Shape` | carrier-free operator = `List ℕ` (the continued fraction) |
| `Wedge/Coalgebra` | constructive coinduction via SPPF-dedup (no Agda `coinductive`) |
| `Wedge/Cross` | synchronized cross-combination (`_⊗ᴰ_`, the span/lockstep) |
| `Wedge/Mul` | multiplicative carrier ⇒ nilpotency = computable `dᴺ` degree; `ε²=z` is the differential |
| `Wedge/CrossMul` | bilinear mixing (cospan into a common carrier); coherence = cross-term nilpotency degree |
| `Wedge/Correspondence` | `fwd × bwd`; areas + correspondences form a category |
| `Wedge/Iso` | **the groupoid**: codomain = inverse of domain, mediated by the wedge `(1,z)` corner |

Reading order for a newcomer: `Wedge` → `Adjunction`/`Reads` (what it is) →
`Shape` (carrier-free) → `Coalgebra` (coinduction) → `Cross`/`Mul`/`CrossMul`
(combining carriers) → `Correspondence`/`Iso` (the groupoid).

## The other arc: `Substrate.Category.UniversalProperty.*`

The same idea — non-vacuous, bridge-returning cross-silo correspondence — at
the **universal-property** layer rather than the carrier layer:

- `Vacuity` (the ⊤-collapse recognizer) → `Recognized` (gated UP) → `Backed`
  (`BackedUP` = solve + solves + content) → `Interop` (`⊗`, the ring identity
  `[ℤ/3]⊗[ℤ/5]=[ℤ/15]`) → `Registry` (the reality anchor: a `List BackedUP`
  whose compilation certifies non-vacuity).

## How the two arcs relate (and why they aren't forced together)

Both are "the wedge of a pair returns the bidirectional bridge." They differ
in **base type**, and that difference is real, not incidental:

- `UniversalProperty.*` works on `BackedUP` (Source / Target / Witness — the
  problem↛solution span). Its `Interop._⊗_∣_` is the wedge-of-a-pair on
  *universal properties*.
- `Algebra.Wedge.*` works on `DivStr` (carrier + `recon`). Its
  `Cross`/`CrossMul`/`Iso` is the wedge-of-a-pair on *carriers*.

They are **parallel instantiations**, not one reducible to the other: a
`DivStr` does not canonically give a `BackedUP` or vice versa, and forcing a
map between them would be exactly the rigidification the project disciplines
against. The wedge groupoid (`Iso`) is the *operational* foundation; the topos
ring (`Interop`/`Registry`) is the *universal-property* view. Keep them
parallel; let a future bridge be discovered, not imposed.

## The frontiers, named (not gaps — deliberate)

1. **The producer** `wedge(capstoneA, capstoneB) → WedgeIso` — the self-hosted
   wedge (operator-as-carrier). Per the reframe, its codomain is the
   inverse-mediated groupoid (`Iso`, built); the self-hosting `recon` taking
   capstones as operands is the remaining engine. This is where a specific
   **cross-field finding** would be the *instance*, run through the machinery —
   intentionally not built, to keep the machinery unbiased by the target.
2. **The container iso** `Wedge ≅ ⟦shape⟧ C` (from `Shape`) — stated, unproven.
3. **Graded coherence witness** — a common carrier where the cross-term
   nilpotency degree genuinely *varies* (CRT: orthogonal idempotents coherent,
   non-coprime obstructed). Numeral; deferred per the no-numerals preference.

## Invariants this arc respects (so consolidation stays honest)

- No Agda `coinductive` — coinduction is the wedge unfold + SPPF cycle-dedup.
- No persistent carrier/carried distinction baked as a *nature* (it's a read);
  the `ℕ`-quotient is the carrier-free shadow, not a privileged sort.
- Obstructions are **graded nilpotent residues** (degree = cost = quantity),
  never annihilating failure flags; `d²≠0` is a computed degree, not an axiom.
- `=` is the wedge's `(1,z)` corner; the groupoid's round-trips are that corner.
