# The transcript miner

**Route the question; do not answer it from this file, and above all do not answer it from
memory.** Dispatch the `transcript-miner` agent (`Agent` tool,
`subagent_type: "transcript-miner"`). It starts fresh, streams the corpus as it is *now*, and
reports turn-indexed witnesses. This file carries only what a reader must not get wrong on the
way there.

## When this fires

- **"When did we decide X?" · "Is that settled or still open?" · "Have we tried this before?"
  · "Where did that number come from?" · "What happened to `⟡<arc>`?"**
- **Before treating anything found in the record as CURRENT.** The transcripts hold proposals
  that were rejected, claims that were retracted, and arcs that were superseded — all of which
  read as live to a reader who finds them and stops.
- **Before reconstructing a decision's rationale from your own recollection of it.** You were
  there; that is exactly why you will get it wrong. The compaction boundary is real and a summary
  of a summary is not a witness.
- **On your own tells:** *"I recall we decided…"*, *"that was already settled"*, *"we tried that
  and it didn't work"*, *"this is the first time this has come up"*, *"there's no record of…"*,
  *"as I mentioned earlier"* across a compaction, and any sentence attributing a position to the
  operator without a quote.

## The four facts to not get wrong

**1. `grep` over a `.jsonl` transcript gives WRONG ANSWERS, not slow ones.** The text lives
inside JSON-escaped strings, so a line-regex matches the ENCODED form — **a phrase typed with a
smart quote or an em-dash is invisible.** And a hit reports a byte offset inside a line that can
be 300 MB long: no role, no turn, so it cannot tell you who said it or when.
`scratch/transcriptstruct.py` streams, decodes, and reports `(turn index, role)`. It is the only
reader for this artifact kind, and the PreToolUse hook will refuse the alternative.

**2. THE CORPUS IS EXTREMELY SKEWED, AND THE SKEW IS A TRAP.** One file has held 1.19 GB while
five sit under 5 MB. Sweeping the small ones is fast, feels complete, and misses nearly all the
history. **A partial index labelled partial is useful; one labelled complete is worse than
nothing.**

**3. A RETRACTION IS THE HIGHEST-VALUE THING IN THE CORPUS AND THE HARDEST TO FIND.** A claim
asserted at turn 400 and withdrawn at turn 900 reads as current to anyone who finds only the
first — and the committed tree records neither. ⚑ Measured on the first dispatch of this kind:
of the jsonb arc's ~20 threads, **six were retracted or superseded**, including one the actor
had asserted as *"the honest boundary"* and the operator refuted in a single line. An index
without status is a way to be confidently wrong about your own history.

**4. TWO ARCS CAN SHARE A VOCABULARY AND SHARE NO CODE PATH.** Also measured on the first
dispatch: two `jsonb` arcs, overlapping terms, one **LANDED** and one **DESIGNED-NOT-LANDED**.
*"jsonb is in the store"* was true of one and false of the other, and the dispatcher's brief had
merged them. **If one word covers two threads, the split IS the finding.**

## What a good brief contains

The agent holds the method; you supply the target. Three things earn their space:

- **A seed vocabulary — explicitly a seed.** Say the terms you know and say *expand from what
  you find*. ⚑ This project's arcs are named `⟡lowercase-slug` and its tasks by circled letters
  (`Ⓖ2i-9`, `Ⓝ26`, `Ⓣ14`). Those are the highest-signal search terms in the corpus and are
  almost never in a brief written from memory.
- **What you believe, marked as belief.** The agent's job includes correcting you, and it cannot
  correct a framing you did not state. The first dispatch corrected two, and both mattered.
- **What "adjacent" means for this question** — the arc's neighbours, not just the word.

## Absence claims need a witness — and here they need a denominator

`0 of 218,475` in one file beside `14 of 21,314` in another is a **boundary**: it locates an arc
in one session. A bare `0` is a fact about the regex. Every mode prints `n of m` for exactly
this reason; a report that drops the denominator has thrown away the part that makes the zero
readable.

Say *"the term does not appear in N envelopes across M files"*, never *"we never discussed it"*.

## No census here, and that is deliberate

⚑ **This skill carries no generated block.** A transcript corpus is append-only local state —
file count, sizes and turn counts change every session and differ on every machine, so a gated
census would fail on every run and after every turn. That is the same reason
`build-observations` and `gate-observations` are ungated in their skills. **The corpus sizes
itself at the start of every dispatch**, which is where that figure belongs.

## Growing this

A missing mode is WORK. Named gaps as of writing, each a build rather than a wall:

1. **No cross-file sweep.** Every mode takes one file, so a corpus-wide question is N invocations
   the agent must fold by hand — the shape the standing rule forbids. `transcriptstruct.py
   --grep-content <re> <file>…` over a glob, reporting `n of m` per file and a total, is the
   mode.
2. **No index artefact.** A mining dispatch produces its index in the report and it dies with the
   turn. The findings ledger takes the *conclusions*; nothing takes the thread→turn-index map,
   which is the navigable part.
3. **No retraction reader.** *"Find every claim in this file that a later turn contradicts"* is
   the highest-value question here and is currently a hand-built alternation over
   `retract|withdraw|wrong|superseded|reopened`.
4. ⚑ **A miner cannot file what it finds.** `bibstruct --add` needs a witness registered in
   `findings.py`, and a Bash-only agent cannot write a Python body — every route is hook-refused
   (`agda-O4-bash-only-agent-cannot-write-a-body`). It reports the finding as OWED and the
   dispatcher files it. **This has now recurred in two oracles' ledgers**, which makes it a
   design problem rather than an incident: either the agents get `Edit` scoped to
   `.claude/agents/`, or `findings.py` grows a `--register <key> <kind> <note>` mode. The second
   is more in the grain — a tool, not an affordance.

## See also

- `.claude/agents/transcript-miner.md` — the agent this routes to; the method lives there.
- `scratch/transcriptstruct.py` — the instrument. Its header records why grep fails here.
- `.claude/agents/findings.py --list` — what previous dispatches established, and their status.
