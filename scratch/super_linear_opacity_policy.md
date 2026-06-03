# Super-Linear Opacity Policy

**Status: POLICY + linter sketch. NOT a migration.** Executing the seals is
high-variance (every consumer that *forces* a sealed power breaks — this is
exactly how the FromImages seal broke SingerOrder). So: adopt the rule for
new code now; migrate existing definitions only one-at-a-time with per-case
consumer verification.

## The rule

> A definition whose **normal form grows super-linearly** in its argument
> should be sealed in an `opaque` block, exporting a **characterizing
> lemma** for how consumers use it — so the typechecker never forces the
> blown-up concrete form.

Concretely, by growth rate of the operation:

| operation | growth | policy |
|---|---|---|
| `_+_`, successor, `lookup` | linear | **transparent** (cheap; thousands of refls depend on reduction) |
| `_*_` | quadratic | **seal** |
| `_^_` (power, iterate-to-a-count) | exponential | **seal** |
| tetration / nested powers | non-elementary | **seal** |
| dense linear maps, matrix powers (`linear-from-images`, `L-iterate`, `*-Linear`) | (dim)^k | **seal** (already done: linear-from-images, cyclic-Linear) |

Addition is the computational floor; multiplication and up are sealed.

## Why (the evidence)

Both memory/OOM incidents this arc were **powers being normalized**:
- Cycle7: `cyclic-HasOrder {6}` forced a 7×7 matrix to the 7th power.
- SingerOrder: `HasOrder-singer` proved order-7 by `refl` = `singer-Linear^7`.

The disease is always "a super-linear operation's concrete normal form
gets forced." Sealing the operation at its source converts the only
typechecker action on it from *force* (eager, blows up) to *compare*
(spine equality, cheap). See memory:
- `feedback_opacity_tracks_blowup_not_layer` — the line is growth-rate,
  not module layer.
- `feedback_sparse_concrete_transparent_metadata` — opacity = laziness +
  metadata interface; in Agda the seal IS how you buy laziness from an
  eager checker.
- `project_cyclen_opacity_fix`, `project_oom_load_bound_finding_2026_06`.

## The metadata-interface obligation (the actual work)

Sealing is cheap; the **characterizing lemma interface is the work, and its
completeness is the policy's real content.** A consumer forced to write
`opaque unfolding X` is a **metadata gap** — the seal didn't export enough
to reason about X without forcing it. (SingerOrder needed a whole
Point-bridge because `linear-from-images` exported `apply-on-basis` and
stopped — no "order / action" metadata.)

Rule of thumb: **for every seal, export enough lemmas that no consumer ever
needs `unfolding`.** When `unfolding` appears, treat it as a signal to
enrich the interface, not a normal cost.

## Migration discipline (high-variance — do NOT batch)

Sealing an existing super-linear definition can break any consumer that
banked transparent reduction through it (definitional `refl` on a concrete
power). Therefore:

1. Before sealing X, grep consumers for `refl`-through-X / concrete-instance
   proofs (the reduction-bankers). Each is a break risk.
2. Seal X; verify the *reduction-consumers* (not just X's compile) capped.
3. Any breakage → either add the missing metadata lemma (preferred,
   structural) or `opaque unfolding X` at that one site (patch). Prefer the
   lemma; an `unfolding` is recorded debt.
4. One definition per change, committed separately. Never a batch seal.

## Linter sketch (not built)

A `check_super_linear_opacity.sh` could flag: a **transparent** definition
whose body applies `_*_` / `_^_` / `iterate`-with-a-numeral / a `*-Linear`
to a recursively-or-power-built argument (the blow-up shape). High false-
positive rate likely (many `_*_` uses are harmless), so it would be an
*advisory* report, not a hard gate — unlike def/proof separation, which is
name-based and exact. The super-linear rule is a judgment policy with linter
*assistance*, not a mechanical invariant.

## Scope line

ENFORCEABLE NOW: the rule for new super-linear definitions (seal + metadata
lemmas). DONE: linear-from-images, cyclic-Linear/cyclic-HasOrder sealed;
SingerOrder restructured to need no forcing. NOT DONE: a sweep of existing
`*-Linear` / power definitions (per-case migration, deferred). The linter
is a sketch, advisory if built.
