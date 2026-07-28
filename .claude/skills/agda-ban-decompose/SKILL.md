---
name: agda-ban-decompose
description: The ban-compliant decomposition pipeline for Agda modules — split a file into definition-per-file siblings, rewire consumers, and resolve the name collisions that removing `using`/`renaming` exposes. Use when splitting a module, paying down the import ban, or fixing NotInScope/AmbiguousName/ClashingDefinition after an import change.
---

# Ban-compliant decomposition

The import ban (no `using` / `renaming` / `hiding` / `as` / qualifier on Substrate
imports) and definition-per-file decomposition are **one move**, not two: bare
imports only work once each module exports few enough names that a consumer can
take all of them. Decomposition is the precondition; the ban is the consequence.

This playbook exists because the sequence below was re-derived from scratch three
times, each time rediscovering the same failure modes.

## The pipeline

Run in this order. Each step has a tool; do not hand-edit.

| # | step | tool |
|---|---|---|
| 1 | split the file into definition-per-file siblings | `scratch/split_lemmas.py <file> --apply` |
| 2 | rewire imports of modules that no longer exist | `scratch/rewire_stale_module.py` |
| 3 | drop imports the file does not use | `scratch/prune_imports.py` |
| 4 | order imports below their binding sites | `scratch/agda_imports.py order` |
| 5 | regenerate the build manifest | `scripts/gen_build_makefiles.py` |
| 6 | build; resolve collisions by **rename at source** | `scratch/rename_at_source.py` |

For splitting an *upstream* module and rewiring its consumers in one pass:
`scratch/split_upstream.py <Module>` then `scratch/narrow_leaf_imports.py`.

**Parallelise every per-file pass** — they are independent:
`ls DIR/*.agda | xargs -P 10 -n 15 python3 scratch/<tool>.py`. Serial runs of the
topo sort took minutes; parallel took seconds.

## The conservation guard (do not remove)

`split_lemmas.py` refuses to write unless **every non-blank body line lands in
exactly one unit**. This is the only thing standing between a regex splitter and
silent deletion. It has caught seven distinct silent-deletion bugs:

- `data`/`record` declarations not matching the signature regex (6 deleted)
- body starting after the *last* import in the whole file, when imports interleave
  (2096 of 2165 lines deleted)
- unmatched col-0 lines falling through a bare `i+=1` (copattern clauses:
  `head (bar r) = …` leads with the *field*, not the def)
- trailing comment blocks with no following unit
- the safety net appending a line but not its accumulated comment block
- a leading import's `renaming (…)` continuation landing in the body
- `imports` collected as heads only, dropping every continuation clause

**Any new parse rule needs the guard re-run, not reasoning about whether it is
safe.** A splitter that "looks fine" and produces plausible output is exactly what
the guard exists to disbelieve.

## Resolving collisions: decompose UP the chain FIRST

**Before renaming anything, recursively walk *up* the dependency chain and
decompose along the way.** Most collisions evaporate, because after decomposition
the two names stop being introduced into the same interface.

`Foundation.Fin.Op` defines `_≟_`; so does the undecomposed `Foundation.Nat`. A
consumer that needs only `ℕ` is forced to import all of Nat and therefore sees
both. Decompose `Foundation.Nat` into leaves and that consumer imports
`Foundation.Nat.Nat` — Nat's `_≟_` never enters its scope, and the collision is
gone without renaming anything.

So the order is: decompose the *provider*, re-measure, and only then rename the
collisions that survive. Renaming first is premature — it churns names to solve a
problem the decomposition would have dissolved. (Measured: reaching for
`_≟ᶠ_`/`_<ᶠ_`/`_≤ᶠ_` on Fin before decomposing Nat, when Nat was the module
forcing the collision.)

## Resolving collisions that survive decomposition

Removing `using` widens scope, so names that two modules both define now clash.
The filter was *masking* the collision, not preventing it. Three error shapes:

- `AmbiguousName` — both providers in scope at a use site
- `ClashingDefinition` — a local definition collides with an imported one
- `NotInScope` — a `using` named something the module no longer exports (this is
  only a **warning** at the import; the name silently fails to bind and surfaces
  far away)

**The only ban-compliant fix is renaming at source.** Not re-adding `using`, not
qualifying, not aliasing. Give the name a unique spelling where it is *defined*,
or provide an unambiguous alternative at source (a `pattern` synonym beside a
constructor: `pattern fzero = zero`).

### Which use sites mean which definition

After decomposition, a file that imports the defining leaf and mentions the name
means *that* name. Precise but not total — measured 1-in-10 false positives (a
file imported the leaf but its use was the *other* provider's). So:

- `rename_at_source.py` renames only where the file imports the home module and
  **no other provider**;
- files importing both are reported `AMBIGUOUS` and left alone;
- the build arbitrates those: each error names a site, fix with `--site=FILE`.

Never bulk-rename by token match across importers. That is how a Nat `suc-injective`
use got renamed to `fin-suc-injective` and broke a file that had been fine.

## Known collision sets

`Foundation.Fin` vs `Foundation.Nat`: `_≟_`, `_<_`, `_≤_`, `zero`, `suc`,
`suc-injective`. **Do not rename these yet** — `Foundation.Nat` (111 lines, 1182
importers) is still undecomposed and is what forces every one of them into shared
scope. Decompose Nat (13 clean leaves: `Nat`, `Plus`, `Times`, `Pow`, `Monus`,
`Le`, `Lt`, `Sucinjective`, …) and re-measure; expect most to vanish.

`Foundation.Vec` vs `Algebra.R.Trace`: `head`, `tail`. Same treatment — Vec splits
into 13 leaves; decompose before considering a rename.

Already landed at source (these were genuinely needed, not collision artifacts):
`pattern fzero`/`fsuc` beside Fin's constructors, so no consumer needs
`renaming (zero to fzero)`.

## Cap interaction

Elaboration peak is per-module, so splitting is also the cap fix: `MEM_CAP` is
enforced at the agda param (`+RTS -M128m` in `gen_build_makefiles.py`), which makes
over-cap a *build failure* rather than a post-hoc census — the census is bimodal
(a cached-`.agdai` load row ~79MB vs a real elaboration row ~300MB) and reads
"under cap" purely because a module was not re-elaborated.

Duplicate imports are a cap issue too: a parameterized module imported twice is
applied twice and elaborated twice. `split_lemmas.strip_using` dedupes statements.

## Verification

- conservation guard passes (the splitter wrote at all)
- `make -j` from `agda/`: `errors=0`, `heap=0`
- `gen_build_makefiles.py --check` clean
- nothing pushed; the user pushes

## Tool hazards (each cost a real recovery)

- **Read before write.** `open(f,"w").write(sub(open(f).read()))` truncates the
  file before the inner read runs. It emptied three modules.
- **Operators have two spellings.** `_≟_` in a signature, bare `≟` in an infix
  clause. Rename both or the clauses become an undefined operator.
- **Import statements span continuations.** Any pass that treats an import as one
  line will orphan its `using`/`renaming` tail or drop it entirely. Consume the
  head plus its indented continuations, always.
- **`sanitize` must transliterate.** Stripping to `[A-Za-z0-9]` maps `ℕ` and `_+_`
  both to `Op`. Use the transliteration table in `split_lemmas.py`.
- **Applied-import arguments are uses.** `open import M ℕ` needs whatever binds
  `ℕ`; a prune that ignores import lines will drop it.
