# External review — `scratch/bibstruct.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured. Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24).

---

This is a fascinating piece of tooling. The script is highly opinionated, heavily context-aware, and explicitly designed to bridge a gap between two different philosophies of parsing: **The Engine's Truth** (what is strictly allowed/rendered) vs. **The File's Truth** (what the author actually wrote).

Here are thoughts, opinions, and concerns broken down by architecture, implementation, and edge cases.

### Thoughts & Opinions

**1. The Philosophy is Spot-On**
Your commentary regarding the "division of labour" is the strongest part of this tool. The realization that an engine's whitelist parser is fundamentally at odds with a structural linter is a classic domain-driven insight. Tools that fail to make this distinction end up either bloating the engine with linter-specific logic or missing vital structural data (like the dropped `enables` field). Building a "census" tool to explicitly read the diff between the two is excellent architecture.

**2. The `mentions` Heuristic is Brilliant**
Using substring proximity to find *implicit* edges (warrants in prose) is a great feature. It acknowledges that human reasoning often precedes structural codification. Extracting a ±40 character window to provide evidence of an edge before it is formally declared is a highly pragmatic workflow accelerator.

**3. Inline Context (The ⚑ Flags)**
The inline philosophical notes are fantastic. They act as "Chesterton's Fences" for future developers (or future you), explaining *why* something was done a certain way so it isn't accidentally "refactored" back into a previous failure state.

### Implementation Concerns

While the architecture is sound, the reliance on Regular Expressions to parse BibTeX creates a few brittle edges that might bite you as the file grows or if other contributors format things differently.

**1. The Entry Regex is Anchor-Fragile**

```python
_ENTRY = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.S)
```

The explicit `\n\}` at the end of this regex means that an entry will **only** be matched if the closing brace is on its own line (or immediately follows a newline). If a user writes a compact entry like `@misc{key, claim={alpha}}` (no newline), this parser will silently drop the entire entry.

* **Fix:** Use `\}` instead of `\n\}`, or `[\r\n]+\}` if you truly want to enforce a line break.

**2. The Field Regex Assumes Braces**

```python
_FIELD = re.compile(r"([\w-]+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
```

This assumes all BibTeX fields are wrapped in `{...}` and allows exactly one level of nested braces. It will completely miss fields that use quotes (`name = "value"`) or bare integers (`year = 2026`). If your internal `.bib` style strictly enforces braces via a formatter, this is fine. If humans are writing this by hand, it is a ticking time bomb for missed data.

**3. Algorithmic Complexity in `mentions()`**

```python
# Inside the loops over every entry and every field:
if any(k != key and key in k and k in raw for k in have):
    continue
```

To avoid matching `R14-v1` when the text actually says `R14-v1-rederive`, you iterate over the *entire list of keys* for every field that contains a substring match. If your DAG scales to thousands of entries, this $O(K^2)$ operation might cause noticeable latency.

* **Optimization:** Instead of looping over all keys, you could pre-compile a regex of all keys, or check character boundaries. Since you noted `\b` fails on hyphens, you could use negative lookaheads/lookbehinds: `(?<![\w-])R14-v1(?![\w-])`.

**4. `sys.path` Mutation**
Dynamically injecting `PAPERKIT` into `sys.path` based on environmental variables or hardcoded `~/github` paths is standard for internal scripts, but it makes the script difficult to share or run in a CI environment. Wrapping that block in a clear `try/except ImportError` with instructions on how to set the `PYTHONPATH` might be slightly cleaner than doing the path-munging internally.

### Summary

The tool solves a deep, architectural problem effectively without bloating the main engine. The primary risk lies in the regex parsing—if a valid BibTeX construct enters `warrants.bib` that doesn't perfectly match your expected brace/newline formatting, this script will silently drop it. As long as your formatting remains entirely consistent (or is enforced by a pre-commit hook), this is a highly effective piece of engineering.

---

## Reading, for the unification planning

### ⚑ CONCERNS 1 AND 2 ARE THE TOOL'S OWN THESIS TURNED ON ITSELF

`bibstruct` exists to report **what the engine's whitelist parser DROPS** — measured,
14 fields across 42 entries. The reviewer's finding is that `bibstruct`'s OWN parser
drops too, on two axes:

  * `\n\}` — a compact entry (`@misc{key, claim={alpha}}`) matches nothing, so the
    **whole entry** vanishes;
  * `= "value"` / `= 2026` — a quoted or bare field vanishes, so the entry is present
    with a **hole in it**, which is worse: a partial answer reads as a complete one.

**A census tool with a silent-drop parser reports a clean bill of health for the
population it cannot see.** That is not a degraded answer; it is the failure mode the
tool was built to expose, one level up. And the standing rule already covers it —
*report the population, not the tally* — but a parser that never emits a row for a
dropped entry cannot report the denominator it missed.

⚑ **THIS IS EXACTLY THE GAP THE STRUCT-TOOLS STUDY MEASURED INDEPENDENTLY.** That
survey found `bibstruct` is *"the only file-reading family member with no
losslessness/fixpoint gate"*, and argued the right guarantee is `--roundtrip`
(byte-lossless) because BibTeX is being READ, not normalized. **Two instruments, two
methods, same conclusion** — the outside reviewer reasoning from the regexes, the
agent reasoning from the family's parallel structure. That is corroboration, not
repetition.

A `--roundtrip` for `bibstruct` is precisely the guard that would have caught both:
parse → re-emit → compare bytes, and a dropped entry or field cannot survive it.
**Population: 42 entries in the default bib** — small enough that the gate is cheap
and the paydown is bounded.

### ⚑ A MEASUREMENT THAT LOOKED LIKE IT RETIRED THIS, AND DOES NOT (2026-08-02)

The `WORKLIST.md`-vs-bib audit measured, on the CURRENT bib: raw `@`-headers **42**,
bibstruct-visible **42**, duplicate keys **0**, quoted fields **0**, bare-integer
fields **0**. I recorded that as *"both alleged instrument hazards are inert here —
parser-confirmed, not assumed."*

**That claim is withdrawn. It collapses ∀-over-inputs into ∃-at-this-input** (user,
2026-08-02: *"That's assuming the data is never corrupted. There's a difference
between the homology and the cohomology, the algebra and the coalgebra."*).

  * What was measured is **the algebra**: at this point, the parser's output agrees
    with a second reading of the same bytes. A statement about an INSTANCE.
  * What the reviewer alleged is **the coalgebra**: what the map DOES TO inputs it has
    not seen. `\n\}` is a claim about the parser's KERNEL, and "no quoted field exists
    today" says the kernel is currently UNWITNESSED — not that it is empty.

⚑ **AND AN UNWITNESSED KERNEL IS THE DANGEROUS CASE, NOT THE SAFE ONE.** Nothing
exercises it, so its first firing is invisible — the same reason `agda_defs`'
`errors="replace"` is most dangerous exactly when a decode failure is "impossible"
(see [review-agda-defs.md](review-agda-defs.md) concern 1). The moment a hand-written
`year = 2026` or an inline closing brace enters `warrants.bib`, the drop fires and
every downstream count shifts silently — in the tool whose entire thesis is reporting
what ANOTHER parser drops.

**Correct reading of the audit's number:** *the hazard has zero population on the bib
as of 2026-08-02.* A fact with a timestamp, not a property of the tool.

⚑ **THIS IS WHY A CENSUS CANNOT SUBSTITUTE FOR A ROUND-TRIP, and the distinction
generalises past this file.** A census asks *what did you see*; a round-trip asks *is
your reading TOTAL* — parse, re-emit, compare bytes. The first measures the instance,
the second probes the map. Same asymmetry as `mdstruct --fixpoint` (not "does this
document look fine" but "is normalize idempotent"), and the same asymmetry the arc
already paid for once: **`--verify --from-build` read 2802 clean until freshness was
tested and it became 1036** — the instrument was total on what it could see, and what
it could see was not the question.

**Standing form: every "the census is clean" result in this arc is an instance
measurement standing in for a map property, unless a totality probe says otherwise.**
`--roundtrip` remains OWED; the audit did not retire it, and reading the audit as
having retired it is the error this section exists to prevent.

### Concern 3 is REAL BUT CORRECTLY-MOTIVATED — do not "fix" it into a regression

The O(K²) is guarding against matching `R14-v1` inside `R14-v1-rederive`. That guard
exists because **`\b` does not bound these keys** — hyphens are `\w` boundaries in the
wrong places, which this repo measured in the Agda layer at **1269 of 10831 names
(11.7%) invisible to a `\b`-bounded regex** (§14), and which produced
`agda_lex.word` as the standing name-boundary authority.

So the reviewer's proposed fix — negative lookarounds `(?<![\w-])key(?![\w-])` — is
**the same construction `agda_lex.word` already implements for Agda names.** That is
the finding worth carrying: not "optimize a loop", but *the name-boundary predicate is
a SHARED capability that two artifact kinds both need and only one has*. Under a
dispatcher, boundary-aware name matching is plugin-contract machinery, not a
per-artifact regex.

⚑ **AND IT IS THE THIRD INSTANCE OF ONE CLASS TODAY.** `--attr`/`--discards` keying by
bare name (T20, corroborated in [review-pycodemod.md](review-pycodemod.md)); `def_index`
merging `_-ℤ_` and `-ℤ_` (§22); now `mentions()` needing hyphen-safe boundaries.
**A bare name is not a decidable unit** — in Python, in Agda, and in BibTeX keys.

### Concern 4 is a MIGRATION CONSTRAINT, and it is the one that binds the dispatcher

`sys.path` mutation toward a hardcoded `~/github/paperkit` is the thing that makes
this tool un-runnable in a fresh clone or CI. It is not a defect in isolation — every
struct tool has some form of environment assumption — but **it is the axis the
unification must decide**: a shared dispatcher has ONE import/resolution story, and
`bibstruct`'s current one is the least portable in the family.

Related and already filed: `pycodemod --imports` classifies STDLIB / DECLARED /
UNDECLARED / MISSING precisely to answer *"what breaks in a fresh clone"*, and the
`pyproject.toml` work retired the `uv run --with` incantations for the same reason.
The dispatcher inherits that question rather than each plugin answering it privately.

### What this review does NOT cover, stated so the absence is not read as a pass

The reviewer did not exercise `--dropped`'s correctness against the engine (only
reasoned about the parser), did not comment on the `--items <key>` DECLARED-grade
output, and did not see the `--entry`/`--items` collapse (a mode built and then
DELETED after the user's *"Isn't that just `--items <key>`? … It's the same frelling
shape."*). Silence on those is a fact about the review's scope.
