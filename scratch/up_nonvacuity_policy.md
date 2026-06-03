# Universal-property-backed interoperability: the checklist

The substrate unifies through one center — `Free ⊣ Forgetful`, the universal
property — and a universal property earns its place only if it is **non-vacuous
and backed by a returned bridge** (`Category.UniversalProperty.Backed.BackedUP`:
`arrow` + `solve` (returns the witness) + `solves` (coherence) + `content`
(non-vacuous)). The question this policy answers: *how do we mechanically check
conformance?* And the sharp distinction it turns on:

## Obligation vs. reality (the correction that matters)

There are two different things you can mechanically check, and they are **not
the same**:

- **The obligation** — "is this *written* as a `⊤`-stub?" A grep for
  `Witness = λ _ _ → ⊤` reads this. It is a **self-report**. It can *disagree
  with reality*: `FreeMonoid-UP` in `UniversalProperty/Instances.agda` is a
  `⊤`-stub (the grep flags it as "debt"), yet the free monoid is *really,
  non-vacuously backed* in `FreeUniversalProperty.FreeMonoid`. The stub is just
  unwired. Conversely the ~1200 modules that write no `UPArrow` at all are
  invisible to the grep while being, in reality, unbacked.

- **The reality** — "does a non-vacuous bridge *actually exist* for this
  structure?" This is checkable **only one way: a `BackedUP` term that
  typechecks.** Because `backed-non-vacuous` makes the checker *refuse* a
  `⊤`-collapse, you cannot construct a `BackedUP` over a vacuous witness. So
  *"this structure really has a non-vacuous universal-property bridge"* ⟺
  *"a compiled `BackedUP` exists for it."* The typechecker is the gate; a grep
  can never be.

The grep targets the obligation. The registry targets reality. Keep them in
their lanes.

## The mechanism (two instruments, ranked)

1. **`Category.UniversalProperty.Registry` — the reality anchor (primary).**
   A `List BackedUP` whose *compilation is the certification*: every entry is a
   genuine, content-bearing universal property because the file typechecks, and
   `every-backing-non-vacuous` is forced by typing, not asserted. To unify the
   repo is to **grow this list** until it covers the primitives that claim a UP.
   The registry cannot be padded with vacuous claims — that is its strength over
   a grep. **Coverage** (registry size vs. the primitives index) is the
   unification metric.

2. **`scripts/check_up_nonvacuity.sh` — the obligation census (secondary,
   advisory).** Flags written `⊤`-stubs outside the two sanctioned `⊤`-UPs
   (`trivial-UP` = genuine terminal; `HC/PlaceholderUP` = named placeholder).
   Useful as a *self-report consistency* signal — "these modules announce they
   are not backed here" — **not** as the reality check. Some of its hits are
   false debt (content exists elsewhere); some real unbacked structures it never
   sees. Treat its output as a to-wire / to-back worklist, cross-checked against
   the registry.

## The conformance checklist (per primitive that claims a universal property)

1. Express the property as a `UPArrow` (Source / Target / Witness). *(structural)*
2. Witness is content-bearing, not `λ _ _ → ⊤`. *(obligation grep flags failure)*
3. A `Contentful` certificate exists — `(s,t)` with `¬ (Witness s t)`. *(typechecked)*
4. A `BackedUP` exists and is **registered** — `solve` returns the bridge,
   `solves` proves coherence, `content` certifies non-vacuity. *(typechecked —
   THE reality check)*
5. The bridge composes / morphisms route through the center
   (Grothendieck-coherence). *(discipline; next-lift exposes orphans)*

Criterion 4 is the one that means anything: it is the only step a grep cannot
fake and the typechecker cannot pass on a vacuous claim.

## Current state (2026-06-02)

- **Backed & registered (reality: backed):** equality UP; CRT(3,5) — the
  `gcd → Bézout → inverse → idempotent → combine` chain as the bridge.
- **Proved, not yet registered (reality: backed; needs a `BackedUP` wrapper —
  NOT debt):** free monoid, free F₂-module, Z₂ presentation, the limit/product,
  the units (ℤ/M)*. These are the *next registry entries*.
- **Obligation-only `⊤`-stubs (self-reported; census worklist):**
  `Instances.agda` ×5, `Quotient`, `QuotientProduct`. At least one
  (FreeMonoid-UP) has real content elsewhere — wire, don't re-prove.
