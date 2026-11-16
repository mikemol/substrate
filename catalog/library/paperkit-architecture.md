# paperkit — architecture, capabilities, and what substrate duplicates

⚑ **PROVENANCE.** A research agent's survey of `~/github/paperkit` and the
`fuel-series` archive, 2026-08-02, dispatched under the struct-tools rule (fix the
tooling rather than grep). Findings carry witnesses (`path:line`); figures are the
agent's measurements, not recollection. Stashed here because the survey cost ~148k
tokens and existed only in a tool result — a finding that lives in a transcript is
lost at the next compaction, which is the same defect `OBS` is about one domain over.

⚑ **NOT INDEPENDENTLY RE-VERIFIED BY ME.** The agent reported the tooling fixes it
made and the counts it measured; I have not re-run each witness. Treat every figure
as a hypothesis at a later tree state (the standing rule) and re-measure before it
becomes a dependency.

---

## THE LOAD-BEARING ANSWER: foreign references

The question was whether a **computed edge** (derived, not hand-authored) can enter
the claim graph through a supported mechanism, rather than the bespoke merge file
this session was about to build.

**Yes — and the merge file must not be built.** Three layers:

### 1. Foreign bib import

`paper.toml`'s `warrants` list accepts a **Bazel label**, resolved repo-root-relative
by `bib._bibpath` (`bib.py:53-61`). The only worked example in either corpus:

```toml
# paperkit/paper.toml
warrants = ["warrants.bib", "//paper:adequacy_pitch.bib"]
```

The root project imports a bib the `paper` project owns. That bib holds one claim,
`adequacy-pitch`, with `check = concept:adequacy-pitch`.

### 2. Provenance is carried AND consumed

`bib.parse` stamps every claim `_src = <filename>` (`bib.py:41`). Two consumers:

- `sentence()` (`project.py:122`) — `_src == primary` renders the claim as **your own
  assertion**; otherwise it appends author+year, so a foreign claim is **cited as
  someone else's**.
- `weave()` (`project.py:334`) reads it twice more, suppressing the prose "glue"
  connective across a source boundary.

⚑ That is exactly the marker I said derived edges would need so a computed edge does
not read as something hand-authored. It already exists.

### 3. `crosses` verbs verify across the boundary rather than re-deriving

`resolver.VERBS` (`resolver.py:80-91`) carries a **`crosses`** flag; `CROSSING` is
*derived* from it (`resolver.py:95`) and three sites consume the derived set rather
than re-listing verbs (`footdeps.py:135`, `:194`, `boundaries_dispatch.py:52`).

For a crossing verb:

- `grader.grade_check` returns `grade: "imported"` **without running the sibling**
  (`grader.py:331`, `:344`) — "composition, not re-derivation";
- `footdeps` **skips footprint tracing** — "a crossing check is an EDGE, not a leaf"
  (`footdeps.py:130-132`);
- soundness is by composition: the owning project gates it independently.

### The route for a derived edge

Author the derived claim in its own bib; the consuming project imports it by label;
the claim carries `check = concept:<key>`.

⚑ **`concept:` over `result:`** — `result:` imports a whole sibling **gate verdict**,
`concept:` imports **one keyed witness**, and a per-edge derived claim is the latter.

⚑ **`boundaries_references.py` IS A FALSE LEAD.** `project.references()`
(`project.py:244`) is *intra-document* cross-referencing — projecting a claim's
non-adjacent `rests-on` edges as prose citations by signed distance. Not
cross-project. The name collides with the concept; the mechanism is elsewhere.

---

## Resolver / gate / grade contracts

### Verbs

`resolver.py:80` — the dict OWNS the enumeration; no consumer may re-declare it.

| verb | does | crosses |
|---|---|---|
| `file` | exists | |
| `cmd` | execs | |
| `result` | parses a sibling's gate verdict | ✅ |
| `agree` | ≥2 independent producers must exit 0 **and** emit identical output | |
| `concept` | imports one keyed witness | ✅ |

### `concept:<key>`

`resolver.py:179-199` runs `<library>/concepts.py <key>` as a subprocess.
Two-level resolution (`_library_for`, `resolver.py:36`): the **consuming** project's
library first (`<project>/library/`, then `<repo>/library/`), else the engine's.

⚑ **The fallthrough is PER-KEY, not per-directory**: exit code **2 is the "not mine"
sentinel**, and only then is the engine's library retried. Exit 0 = certified,
1 = FAIL. Confirmed live in fuel-series (`library/concepts.py:2332-2362`).

### Custom verbs

`[checks.<name>] cmd = "…"` in `paper.toml`, with `{target}` substituted
(`resolver.py:222-223`). ⚑ Builtins dispatch **ahead of** custom — a shadowing hazard
`_library_for`'s own docstring records.

### Gate refusals

12 conditions, including: projection drift (`out != project(cfg)`), undefined
citations, **dangling `rests-on`**, failed checks, **`--without-K` collapse** (≥2
cited claims sharing one check string — proof-irrelevance treated as a defect),
absent rubric section, missing `emit` artifact, uncited placement (a gap under
`--safe`, else advisory), uncited section-tagged claim.

`--json` emits `{document, pass, project_ok, verified, undefined, bad, dangling,
sections, gaps, postulates, collapses}`.

### Grade ladder

`grade.py:59` — `broken` < `vacuous` < `existence` < `indeterminate` < `behavioral`,
plus `imported`, which is **a delegation, not a tier**.

`behavioral` = falsifiable, established by **mutation**: corrupt an input and the
check must flip red. Every record carries `why` / `not_higher` / `not_lower` — ⚑ the
grade explains its own bounds, which is the shape a bare pass/fail cannot.

### The rest

- `discriminate.py` — the driver: footprint-keyed caching (triple-keyed on engine
  hash + resolution + sandbox root), determinism guard, resumable budget.
- `coherence.py` — the **∂² residual**: how far *declared* structure (`rests-on`,
  prose order) matches *measured* def-sensitivity, across structure / sensitivity /
  grounding / emergence. "Discharged" = claims carrying a `link` (author
  acknowledgment of divergence).

---

## What substrate DUPLICATES — the reuse-search result

⚑ **`scripts/worklist_gate.py:196` ALREADY IMPORTS `paperkit.bib`.** This is not
"should we adopt it" — it is a **partial adoption that stopped short**, which is the
harder case: the seam exists and was not followed.

| substrate | paperkit already owns | verdict |
|---|---|---|
| `worklist_gate.order()` topological layer via `depth()` (`:318`) | `bib.dep_order` (`bib.py:96`) | duplicate — substrate re-rolls the sort over `rests-on` where paperkit has it over `from` |
| `worklist_gate.cone()` / `_dependents` | `bib.rests_closure` (`bib.py:118`) returning `(reachable, dangling)` | **duplicate, and substrate LOSES the `dangling` half** — a broken grounding edge that fails paperkit's gate is invisible to substrate |
| openness by running `items.ITEMS[label]()` | the `check:`/resolver dispatch + `grade` ladder | substrate has a **boolean**; paperkit has a graded, mutation-verified verdict with caching |
| `items.SIZES`, hand-declared populations | `grade`'s measured `tests` sensitivity set | substrate **declares**, paperkit **measures** |
| `scratch/bibstruct.py` reading `enables` | — | ⚑ **legitimately NOT duplicated.** `bib._LIST` whitelists `from`/`rests-on`/`reads`; `enables` is silently DROPPED. bibstruct exists to read what the engine drops, and its docstring already says so. |

⚑ **THE SHARPEST FINDING: `enables` IS `from`, RENAMED.** `worklist_gate.order()`'s
own comments insist `enables` (sequencing) is distinct from `rests-on` (grounding).
Paperkit has no `enables` — but it has **`from` (prose order) vs `rests-on`
(grounding)** as exactly that two-edge distinction (`bib.py:28-30`: *"the two are
often reversed"*). **Substrate reinvented the second edge under a third name**, and
the engine drops it on every read.

---

## fuel-series

**12 paperkit projects**, all siblings under `fuel-series/`, each a one-essay project
(`warrants.bib` → `NAME.md`): carrier, cotype, exterior, fast, frozen, fuel,
grassmann, kernel, **library**, morphism, parity, recarry.

⚑ **NONE use foreign bibs (0 of 12)** — so the worked example is in *paperkit*, not
here. They compose the other way: `library/` is the shared **concept library**
(`concepts.bib`, `library/concepts.py`, ~2360 lines), authoring keys with
`cmd:python3 concepts.py <key>` for consumers to import via `concept:`. Paperkit's own
library has the same shape with 29 keyed witnesses.

### `routing.py` — a correction to the brief

⚑ It is **not** a paperkit routing module and has **no `commit`/`dependents` verbs**.
Its actual contract:

- `graph()` (`routing.py:35`) — regex-scans **substrate's Agda tree** for
  `import Substrate.*`, returns `{module: {deps}}`
- `closure(seed, rev)` (`:47`) — reverse-reachability BFS
- `compute()` (`:58`) — seeds three axes E/T/X, closes each, assigns every module a
  3-bit signature `(m∈E, m∈T, m∈X)`, returns `(imports, seeds, cl, sig, members)`
- `main()` (`:150`) — projects `ROUTING.md`; under `--check`, **fails if the file
  differs from the corpus it describes**

⚑ **That last pattern is the reusable one.** `coverage.py` and
`grassmann/tablegen.py` are identical in shape — generate-or-verify a markdown
projection, `--check` gates drift. It is `gate.py`'s PROJECT invariant, hand-rolled
three times per corpus.

---

## Tooling the survey fixed

⚑ **The assigned bazel fix was INSUFFICIENT, and why is the substantive part.**
`--in paperkit --calls references` returned 135KB of hits from `bazel-bin/` —
generated mutation artifacts (`mut_project__*.mutated.py`), not source.

- `_GENERATED_DIRS` (`pycodemod.py:217`) — bazel-bin/out/testlogs, build, dist,
  `.mypy_cache`, `.tox` — matched as **whole path components**, never substrings
  (`"build" in rel` also eats `rebuild/`, `buildtools/`).
- ⚑ **That alone did nothing.** `bazel-bin` is a **top-level** entry, so `_roots()`
  (`pycodemod.py:116`) admits it as its own root; `rel` then starts *below* it and the
  component never appears. **The filter was installed and inert** — the same
  looks-wired-isn't shape as `_content_size`. Fixed `_roots()` too, plus a `bazel-*`
  prefix rule (the convenience symlink is named per-workspace, so a fixed set cannot
  enumerate it). `os.path.isdir` follows symlinks, which is why the *name* test is
  required.
- Verified: **135KB → 11 lines**; `--imports` no longer attributes `pathlib` to 1425
  mutation artifacts.

Three modes added, each because a question had no answer:

| mode | why | witness |
|---|---|---|
| `--key <string>` | `--attr _src` returned **0** on a live field — paperkit's model is **dicts** (`f["_src"]`), so its entire data model was invisible to both `--attr` and `--binding`. Splits `read` from schema `decl`, so a declared-but-never-read field stays visible. | `pycodemod.py:1770` |
| `--source <name>` | Every mode answered *where*, none *what does it say*. Inside `--archive` the tree is a temp dir deleted on exit — **there is no path left to `Read`**. CST extents, not a line window. | `pycodemod.py:1719` |
| `--projects` | Nothing enumerated a corpus's **non-Python** artifacts, so "how many paperkit projects are here" had no answer at all. | `pycodemod.py:1650` |

⚑ **A self-correction worth keeping.** The first `--projects` decided *foreign* by
CONTAINMENT ("does the resolved path escape my dir") and reported **0 foreign imports
in paperkit** — the mode built to find exactly this thing reporting its absence.
Wrong: the root project imports `//paper:adequacy_pitch.bib`, and the root *contains*
`paper/`. **Foreign is OWNERSHIP (nearest enclosing project), not containment.**

Selftest **43 → 62**; every case fails against the pre-change code.

---

## Not read

- `paperkit/mutate.py`, `layout.py`, `cache.py`, `config.py` — only through their
  consumers (`grader`, `discriminate`, `resolver.PATH`), not in full.
- `tests/boundaries_*.py` beyond `references` and `dispatch` — ~90 files; the agent
  read the load-bearing spine.
- `library/concepts.py` bodies in either corpus (~2360 lines each) — the **contract**
  is established (registry dict, exit-2 sentinel, per-key ownership); the ~200
  individual witnesses are not read.
- Output `.md` documents and `rubric.tsv` contents.
- Every project's bib cross-checked against its rubric — `--projects` reads
  `paper.toml` only.

⚑ **One named, unbuilt gap:** `--source` handles `def`/`class` but **not module-level
assignments** (`CONCEPTS = {...}` at `concepts.py:2241` was locatable by `--binding`
and not readable). A fourth mode, deliberately out of scope rather than half-built.
