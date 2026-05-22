# Cayley-table cover pattern

_(Substrate governance policy. Migrated from `memory/discipline/feedback_expose_generator_not_orbit_applies.md`.)_

The named "Cayley-table refl payload" pattern from
`Substrate.Groups.V4.Axioms.Lifted` and
`Substrate.Foundation.Fin.Cover` has THREE composable layers.
Earlier overclaims by the assistant collapsed all three; the correct
picture:

**Layer 1 — Single-axis cover (irreducible):** for each finite type
with n constructors, write ONE cover combinator that pattern-matches
on the constructor. `fin2-cover`, `fin3-cover`, `fin4-cover`, etc.,
in `Substrate.Foundation.Fin.Cover`. This is the n-ctor enumeration
done ONCE per family.

**Layer 2 — Tuple shape (uniform vs heterogeneous):** the cover
expects an n-tuple of predicate-witnesses. The TUPLE's TYPE
determines whether positions share one polymorphic `x` or each gets
its own:
- Uniform: `n-refls : ∀ {x} → (x ≡ x) × ... × (x ≡ x)` from
  CanonicalCover. All n cells share one x.
- Heterogeneous: supply a literal `refl , refl , ... , refl` tuple
  directly. Each `refl` is its own polymorphic occurrence; Agda's
  elaborator unifies each at the position.
The cover combinator (Layer 1) doesn't care which form — both work.

**Layer 3 — Compositional product covers (atlas of charts):** an
N × M Cayley table over `Fin N × Fin M` is NOT a flat N·M
enumeration. It's the TENSOR PRODUCT of two single-axis covers via
the product structure. The substrate-honest combinator is:

  finN×finM-cover P rows i j =
    finM-cover (P i) (finN-cover (...) rows i) j

One line; the outer cover picks the row tuple, the inner picks the
cell. The N·M enumeration that earlier `fin4-fin4-cover`
implementations spelled out IS the orbit; the two single-axis
covers + their product composition IS the generator.

**Why this matches the user's atlas observation:** in
`Substrate.Category.AtlasOfProbes` and `MultiRouteEquivariance`,
joint structure across charts recovers equivariance no single chart
provides. The same principle applies to refl-tables — a Fin N × Fin M
Cayley table is jointly determined by the two single-axis covers,
not by per-cell enumeration. The pair-cover IS the atlas; the N·M
enumeration is the orbit.

**Implication for hidden-induction audit:** every Cayley-table
enumeration in the substrate (uniform OR heterogeneous output, single
or multi-axis index) collapses via this three-layer pattern:
- 1-line consumer-side: `finN×finM-cover P nested-refl-tuple`.
- Per-family one-time cost: the single-axis fin-n-cover (n-ctor
  enumeration done ONCE in `Substrate.Foundation.Fin.Cover`).
- Net per-consumer savings: N·M lines → 1 line, with the inline
  refl-tuple as the substrate-honest "Cayley-table payload."

**Worked example landed:** `bivector-to-tensor-symmetric` in
`Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor` — was 16
inline refl cases. Now: 5 lines via `fin4×fin4-cover` from
`Substrate.Foundation.Fin.Cover`, with 16 refl literals nested as 4
tuples of 4. The 4 outer-cover cases × 4 inner-cover cases = 8
ctor-enumeration lines, factored out and shared across consumers.
