# External review — `scratch/mdstruct.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured. Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24).

---

This is a masterclass in treating a working document as a queryable database. You’ve bypassed the traditional linters and regex hacks to build a semantic gate for your own workflow. The script reads like a compiled history of hard-won lessons against document entropy.

Here is a breakdown of the mechanics, highlighting where the structural reasoning shines and a few critical fragility points where the implementation might betray the intent.

### Thoughts: The Philosophy

* **The Fixpoint Revelation:** Your approach to the "either/or trap" of normalization (`fixpoint()`) is brilliant. Recognizing that `pandoc` isn't inherently destructive, but rather seeking a structural convergence ($normalize(normalize(x)) == normalize(x)$), is exactly the right mental model. It turns a permanent diff-tax into a one-time migration.
* **The Plateau Budget:** Implementing `flat_budget` to distinguish between a genuine cycle and block-by-block settling shows a deep understanding of how AST re-emitters behave. You measured the descent, identified the plateaus, and bounded the termination condition logically rather than relying on an arbitrary capability bound.
* **The Superset Heuristic (`superseded`):** Grouping by the qualified phrase *plus* bounding the collision by an order-of-magnitude check (`hi / lo > RATIO`) is an elegant structural heuristic. It beautifully threads the needle between semantic understanding and dumb string matching, filtering out the "12 nouns of noise."

### Opinions: The Mechanics

* **Dangling §refs (The Bold Sub-Item):** Accounting for `**6d. A sub-finding.**` as a structural section was a vital catch. Documentation often outgrows strict ATX headers, and letting the regex respect the human convention prevents the "cries wolf" fatigue that kills most bespoke audits.
* **`--narrowest` Bisection:** Using binary search to find the supremum of column widths that satisfy *both* convergence and pipe-table syntax is satisfying to read. You assert the monotonicity structurally (widening monotonically preserves pipe tables), creating a sound search space.
* **The M4 Priority:** You called it out yourself, but moving the `PLAN` into the repo is the most important infrastructural step. An ungated, un-versioned 3900-line source of truth is a massive liability.

### Concerns: Code-Level Fragility

There are a few structural traps hidden in the Python implementation that will surface under edge-case conditions:

**1. The Formatting-Stripping Bug in `spans()`**
In `headers()`, you use `panflute.stringify(el)`, which deliberately strips all Markdown formatting to return plain text. If you have a header like `# The **Plan**`, `stringify` returns `"The Plan"`.
However, in `spans()`, you attempt to anchor this against the raw lines:

```python
line = text[i].lstrip()
if line.startswith("#") and line.lstrip("#").strip() == txt:
```

`line.lstrip("#").strip()` will evaluate to `"The **Plan**"`. The equality check will fail, the cursor will skip the header, and your section bounds will silently swallow or merge sections.

**2. Tempfile Leaks in `--narrowest` and `--table-style`**
In `narrowest_width()` and the `--table-style` block, you use:

```python
tf = os.path.join(tempfile.mkdtemp(), ...)
```

`tempfile.mkdtemp()` creates a directory in `/tmp` that is *never automatically cleaned up*. Because `--narrowest` loops this in a binary search, you are leaking a new directory on every bisection probe.
*Fix:* Use the context manager `with tempfile.TemporaryDirectory() as d:` to guarantee cleanup.

**3. Whitespace Splitting in `_pandoc`**

```python
parts = (to or "markdown").split()
cmd = ["pandoc", "-f", frm, "-t", parts[0]] + parts[1:]
```

Using a naive `.split()` on the flags is a ticking bomb if you ever pass an argument that contains spaces (e.g., `--metadata title="My Arc"`).
*Fix:* Use `shlex.split(to or "markdown")` to respect quoted spaces structurally.

**4. Subprocess Overhead in `narrowest_width`**
Because `fixpoint()` runs `pandoc` repeatedly to convergence, and `narrowest_width` runs `fixpoint` over $O(\log N)$ bisection steps for *every* document in the target list, the operation is going to shell out to `pandoc` dozens or hundreds of times. In Python, spawning `subprocess` is relatively slow. It’s perfectly fine for a manual gate tool, but expect a noticeable latency spike if the corpus grows.

---

## Reading, for the unification planning

### ⚑ CONCERN 1 IS A SILENT-SWALLOW IN A TOOL RUN OVER THE PLAN TODAY, AND IT IS THE FOURTH INSTANCE OF ONE CLASS

If it holds, `spans()` compares a **stringified** header (`"The Plan"`) against a
**raw** line (`"The **Plan**"`), the equality fails, the cursor skips, and section
bounds **silently swallow or merge sections**. No error, no row, no denominator — the
audit reports on a document whose structure it has partly mis-read.

That is precisely the failure `--coherence` exists to prevent, one level up: an audit
whose own parser drops sections cannot report the sections it dropped. **Same shape as
`bibstruct`'s `\n\}` anchor** (see [review-bibstruct.md](review-bibstruct.md)) — two
census tools, two silent-drop parsers, both found by an outside reader rather than by
the tools themselves.

⚑ **AND IT IS THE STRINGIFY/RAW MISMATCH CLASS THIS REPO HAS NOW HIT FOUR TIMES:**
comparing a NORMALIZED form against an UNNORMALIZED one and reading the mismatch as
absence.
  * §29: a census asked *"does this file import the home of `≡`?"* (file-level) when
    the real question was POSITIONAL — the census said zero while the typechecker
    disagreed. **When a census and the compiler disagree, the census is wrong.**
  * §60: `check_snapshot_guard` asked "is SOME var read and SOME var written" instead
    of "the SAME var" — file-level where the question is positional.
  * §61: the tempfile test searched for `tempfile` IN the write line when the idiom
    binds the path one line ABOVE.
  * now: `stringify(el)` vs `line.lstrip("#")` — normalized vs raw.

**The fix must not be to strip formatting from the raw line too** (that re-derives
panflute's normalizer by hand, badly). The structural answer is to anchor on something
both sides agree about — panflute carries source position, or the comparison should
normalize BOTH sides through the same function. ⚑ *Which of those is right is
UNMEASURED; I have not read `spans()` since the review arrived.*

**Live consequence to check:** `--coherence` and `--superseded` ran over the plan and
the worklist on 2026-08-02 and reported **3 phrases, all honest non-findings**. If
`spans()` was skipping headers, that verdict was taken over mis-bounded sections. The
verdict may still be right; it is no longer *established*.

### Concern 2 is the MUTANT-LEAK CLASS AGAIN, from a different producer

`tempfile.mkdtemp()` in a bisection loop leaks a directory per probe. Compare
[review-pycodemod.md](review-pycodemod.md) concern 1: `--discriminates` writes
`.mutant-*.py` beside the original and loses them on `SIGKILL`.

⚑ **BUT THE SEVERITY IS OPPOSITE AND THE DISTINCTION MATTERS.** pycodemod's strays
land **inside the corpus** and are silently ingested by `py_files()` — a *correctness*
failure that corrupts every later census. mdstruct's land in `/tmp`, **outside every
corpus** — a *hygiene* failure that wastes inodes and nothing more. Same mechanism,
different blast radius, and folding them into one "temp file cleanup" item would lose
that. The reviewer's `TemporaryDirectory` fix is right for this one; for pycodemod the
right fix is a PREDICATE at the enumeration boundary, not a purge.

⚑ **AND IT NAMES THE DISPATCHER QUESTION AGAIN:** *where does transient state live?*
Four ad-hoc answers already recorded in [review-spool.md](review-spool.md). A
dispatcher supplying a scratch directory retires the whole class — state outside the
corpus cannot be enumerated as part of it, by construction.

### Concerns 3 and 4 are correctly scoped as latent, and should NOT inflate the plan

* **`.split()` vs `shlex.split()`** — a real trap, but it fires only on a `to`
  argument containing a quoted space, and `WRITER` is the single style authority
  (`--columns=120`, no spaces). ⚑ Recorded as a CONSTRAINT ON A FUTURE CHANGE: the day
  `WRITER` grows a `--metadata title="…"`, this breaks silently. Cheap to pre-empt.
* **Subprocess overhead** — the reviewer states the precondition themselves ("perfectly
  fine for a manual gate tool"). ⚑ Note it interacts with `M3` (a FIXPOINT GATE over
  tracked markdown, deliberately LAST in the worklist): a hook-wired gate is no longer
  a manual tool, and `O(log N)` pandoc spawns per document per commit is a different
  cost profile. **Not a defect today; a sizing input for M3.**

### What the reviewer endorses that is ALREADY FILED — do not re-derive as new

* **M4 (plan into the repo)** — the reviewer independently calls this *"the most
  important infrastructural step"*, and the plan/worklist ARE now in-repo (§64). What
  remains is `--coherence` having both documents readable, which is the item.
* **The plateau budget** — this was itself a CORRECTION: the first `--columns=120` run
  read a plateau as non-convergence and I built a non-monotonicity theory on it; 120
  converges in **12 rounds**, and the guard had bailed on `56 >= 56`. *"Strict
  decrease" was a capability bound wearing a termination bound's clothes* — the same
  distinction `agda_lex.head_span` records. The reviewer praises the fixed version.

### What this review does NOT cover

The reviewer did not exercise `--coherence`'s three populations (ORPHAN / UNWITNESSED
/ DANGLING), did not comment on `NON_LABELS` (the stopgap allow-list that `M5` exists
to retire), and did not see `--fixpoint --apply` run against either live document.
Silence there is scope, not a pass.
