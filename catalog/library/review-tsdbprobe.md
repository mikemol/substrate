# External review — `scratch/tsdbprobe.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim here is a hypothesis until it
is re-measured against the live tree. This repo's standing rule is that a second
party's number is exactly as unreliable as my own (§14: an agent wrongly reported
`scope_fix._rename_pairs` ABSENT and I nearly built a fourth copy on its word; §46:
two worklist figures were wrong in OPPOSITE directions). Do not cite a figure from
this file as measured — run the command first.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24). This review
describes `tsdbprobe.py` as it stood on 2026-08-02. If the file has moved underneath
it, the review ages the way this arc's own prose findings have — three of four
dependency errors in the §24 topology audit were claims TRUE WHEN WRITTEN and false
when acted on.

## Why this is stashed rather than summarised

The findings feed the struct-tools unification planning. A review paraphrased into a
worklist item loses the reviewer's reasoning, which is the half that survives when the
figure goes stale — the same reason `catalog/library/paperkit-architecture.md` holds
the agent survey verbatim.

## Reviewer's own framing of the tool's premise

The reviewer endorses the separate-tool justification (shell pipelines cannot
distinguish store-down / bad-syntax / not-yet-indexed).

⚑ **ONE PREMISE UNDER THAT ENDORSEMENT IS ALREADY REFUTED, BY THE USER, 2026-08-02.**
The module docstring claims *"The other tools read FILES: same input, same answer,
forever."* That is false, and the counterexamples are in this repo:

  * `pycodemod --types` shells out to mypy — the same source with `.venv` present and
    absent yields different censuses (which is exactly why `claim_census.py:69`
    missing the `.venv` exclusion is a defect);
  * `--discriminates` MUTATES a file and runs its suite, so its answer is a function
    of execution, not of text;
  * `--available` is explicitly a question about the environment, not about a file;
  * the `--last` PREDICATE HASH exists precisely because a census's input is the
    corpus AND the predicate, and the predicate is code that changes under a recorded
    answer — a staleness axis with no live service anywhere near it;
  * `modes()` derives from `_dispatch`'s body, so `pycodemod` reading ITSELF has an
    answer that changes when the reader is edited (it did, three times in one
    session). A tool whose corpus includes the tool is a fixpoint question.

The real distinction is **the cause-cardinality of an empty answer**, and that is a
property of the QUESTION, not of the artifact kind. `--reachable` has three causes;
`--types` has at least two and already handles it (`__unrunnable__`, refusing to
report a clean census on the stated ground that an unmeasured tree is not a clean
one). **So `Unreachable` and `__unrunnable__` are siblings, not unrelated special
cases** — which is load-bearing for the unification: the struct-tools study ranked
"tsdbprobe's precondition vs everyone else's" as a rhyme that should NOT be unified,
and argued it from the live-vs-file boundary. That argument rests on the refuted
premise. The conclusion may still hold on cause-cardinality grounds; it must be
RE-DERIVED, not inherited.

---

This is a deeply pragmatic, battle-scarred piece of SRE tooling. The justification for writing a dedicated script rather than relying on `curl | jq` is spot on: shell pipelines are notoriously terrible at distinguishing between "store is down," "query syntax is invalid," and "the store is up, but the data hasn't indexed yet."

Here is a breakdown of my thoughts, opinions, and a few minor concerns regarding the implementation.

### The Triumphs (Thoughts & Opinions)

**1. The Pure/Impure Split**
Separating the extraction logic (`extract_values`, `extract_rows`, etc.) from the live network calls (`_get`) is the best architectural decision in this file. It makes the parser logic completely deterministic and allows the `_selftest()` to run without spinning up a mock VictoriaMetrics instance. Mocks often just codify our incorrect assumptions about the API anyway, which would defeat the purpose of this tool.

**2. Handling `-search.latencyOffset`**
The documentation and logic around the 45-second deadline for `--verify` is excellent. Most people assume TSDB ingestion is instant and build flaky CI pipelines because they don't account for VictoriaMetrics' 30-second default latency offset or index-creation time. Baking this measured floor into the tool's defaults saves endless false-negative debugging.

**3. Float-Tolerant Read-Your-Write**
Comparing the queried values using `abs(v - expected) < tol` rather than relying on string equality is incredibly smart. Time-series databases frequently munge precision and format (scientific notation vs. trailing zeros). A strict string compare here would absolutely cause false ingestion failures.

**4. `[]` on Garbage**
Failing open (returning `[]`) on malformed JSON bodies rather than throwing an exception is the right call for the `verify` oracle. If the payload is garbage, you can't verify the token, so treating it as "not confirmed" safely prevents the pipeline from proceeding on a false positive.

---

### Concerns & Edge Cases

**1. Argparse Short-Circuiting (The "Silent Override")**
In `main()`, you are evaluating the arguments sequentially with `if/return` blocks:

```python
if a.reachable: ... return
if a.query is not None: ... return
if a.series is not None: ... return
```

If a user (or a CI script) accidentally passes multiple flags—for example, `tsdbprobe.py --reachable --verify "my_metric" 12345`—the script will execute `--reachable`, print the result, return `0`, and silently ignore the `--verify` command.

* **Fix:** Use `argparse`'s mutually exclusive groups, or at least raise an error if more than one action flag is specified.

**2. Verify Deadlines vs. Timeout Stacking**
Your `--verify` loop relies on `time.monotonic() >= end` to enforce the 45-second deadline, and it sleeps for `poll_s` (1.5s) between loops. However, the `_get()` function has a hardcoded `timeout=8.0` for network calls.

* If the VM instance becomes a network black-hole (dropping packets rather than actively refusing connections), each iteration takes 8 seconds.
* In this scenario, your 45-second deadline will only allow for about 5 retries before timing out. This isn't necessarily a bug, but it's worth keeping in mind that your 1.5s polling interval is a *minimum* interval, not a guaranteed frequency.

**3. The `--names` Substring Logic**
Your logic here is actually quite clever, but warrants a double-check:

```python
ap.add_argument("--names", nargs="?", const="", metavar="SUBSTR")
# ... later ...
hits = [n for n in allnames if a.names in n]
```

Because of `const=""`, calling `--names` with no arguments results in `a.names = ""`, which makes `"" in n` evaluate to `True` for everything (dumping all names). If the flag is omitted entirely, `a.names` is `None`, and the block is skipped. It works perfectly, but `nargs="?", const=""` is an obscure `argparse` behavior that might trip up the next person reading the code.

### Verdict

This is a highly defensive, carefully reasoned piece of infrastructure code. It correctly identifies that observing a distributed state machine (VictoriaMetrics) requires handling ambiguity ("not yet indexed") differently than failure ("connection refused"). Addressing the `argparse` mutually exclusive flags is the only structural change I would strongly recommend.

---

## Why concern 1 is the load-bearing one FOR THE UNIFICATION

⚑ **UNVERIFIED — the reviewer's reading of `main()`, not re-measured by me.** Recorded
here because if it holds it is not a `tsdbprobe` defect at all, it is **the argv layer,
which the unification is about to make shared.**

The reviewer's silent-override is the same class as the defect measured in
`pycodemod` on 2026-08-02: `--key --archive f.py` crashed in `tarfile.open` because
the entry point bound another mode's operand as a scope target. Two tools, two
hand-rolled argv layers, two different wrong answers to *"which flag owns this
token, and may two action flags both fire?"*

That fix took THREE attempts, and the first two were guesses:
  1. scan rightward from the scope flag — fails when the owner sits to the LEFT;
  2. walk the whole argv with a single `pending` slot — the later flag OVERWRITES an
     outstanding claim, so the operand is assigned backwards and it crashed
     identically;
  3. `pending` as a QUEUE — correct, and the tool now refuses with usage instead of
     misbinding.

**A dispatcher owns this once.** Mode declaration with arity, operand ownership, and
mutual exclusion are dispatcher properties; a plugin declaring `--verify` takes two
operands is a fact the router consumes, not prose each tool re-derives. Under the
witness rule (user, 2026-08-02: *"the witness must consume it in its paid-down
form"*), that is the real fix — routing CONSUMES the declared roster, so an
undeclared mode cannot dispatch and there is no roster to diff.

Concerns 2 and 3 are `tsdbprobe`-local and do NOT generalise: the timeout-stacking
arithmetic is specific to a live-service poll loop, and `nargs="?"` is an argparse
idiom the other struct tools do not use (they hand-roll `sys.argv` tests). Recorded
so the planning agent does not fold them into the shared contract.
