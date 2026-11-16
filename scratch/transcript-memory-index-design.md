# A transcript-derived compaction-recovery index — design

**Status.** Design, plus a measured prototype over one small transcript. Nothing here was run
against `memory/`; every apparatus module named below was *imported as a library* or read, never
executed as a generator.

**Revised** after an operator reframe: the deliverable is a **recovery mechanism for framings lost
in compaction**, not a status cache and not a keyword index. That reframe changed the unit (§1),
recast the retraction operator from classifying to **linking** (§5), added §9, and is the reason
tool traffic is now IN. The findings that survive it unchanged are marked ⊨.

**Verdict up front, because it changes what follows.**

- ⊨ **Grammar-induced clustering DOES survive the change of corpus** — measured, §3. It finds real
  threads without a seed vocabulary, which is a strict improvement on the hand-built index.
- ⊨ **The graded curve over sharing-breadth DOES NOT survive** — measured, §3, and the reason is
  structural (independently-authored vs self-quoting corpora), so the reframe does not touch it.
- **Tool traffic belongs in the unit, but NOT for the reason given, and NOT unnormalised** —
  measured, §1. Admitting it raw restores a graded histogram, but the new breadth is *path
  boilerplate*. Normalisation recovers the warrant and drops the junk.
- **The claim→warrant join is NOT intra-exchange.** Measured: the tool named in a claim was
  invoked in the same exchange only **24%** of the time (§1.4). The join key is real but it is
  **the artefact reference**, not adjacency. This is the one place the reframe's mechanism needs
  correcting, and correcting it makes the design simpler.
- **Retraction linking is the right shape, and cheaper than classifying** — §5. Recall now
  dominates precision, which changes the cue set and removes the hardest design problem.

So: **take the apparatus's clusterer, drop its grader, normalise tool traffic into the unit, and
add a temporal LINK operator it does not have.**

---

## 0. Where the brief is wrong

The brief already self-corrected the embeddings premise. Four more:

**0.1 "~250,000 envelopes" is the wrong denominator, but ⚑ NOT in the way I first said — and the
correction is mine, not the coordinator's.** I originally reported this as a *population bound on
the design*. It is not. It measures **human prose only**, which under the reframe is one component
of the unit rather than the whole of it. What it actually bounds is **the number of THREAD ANCHORS**
— the points where an operator framing enters the record. Measured on `28df5f75` (1.6 MB, 796
envelopes):

```
796 envelopes
  role assistant  337    role user  189    role queue-operation  86
  role system      72    role last-prompt 42   role ai-title 30 ...
  block text 246   block tool_use 160   block tool_result 157
13 envelope(s) carry genuine HUMAN prose (of 189 with role=user)
```

**13 of 796.** `transcriptstruct.human_text` already does this filtering, and its header records
why: three envelope classes carry `role=user` and are not the human (tool results, system-reminder
injections, task-notifications). If the ratio holds on the 1.19 GB file, there are on the order of
**thousands of thread anchors** across the corpus — the same order as the memory corpus the
apparatus was built for.

⚑ **Restated honestly: 13 of 796 is the number of EXCHANGES, not the number of units of content.**
Under the reframe an exchange is a *container* whose body includes everything the operator's
sentence caused. So this figure sizes the INDEX (how many rows a reader scans), while §0.2 sizes
the CORPUS (how much text the grammar sees). Conflating those two is what made my first draft
exclude the larger half.

**0.2 "Tool-call JSON and pasted code will dominate any naive tokenisation" — the ratio is real;
⚑ the CONCLUSION I drew from it was wrong.** Measured on the same file, content-tokens after
`G.words`:

| source | envelopes | content tokens |
|---|---|---|
| human prose | 13 | **189** |
| assistant text | 179 | 7,240 |
| tool_use + tool_result | 317 | **29,119** |

Tool traffic is **154× the human prose by token count**. I read that as grounds for exclusion. The
coordinator is right that this is a keyword-index reflex: for *recovery*, the tool traffic is where
the warrant lives. But the ratio is not therefore harmless — §1.3 measures what admitting it raw
actually does, and the answer is that it must be **normalised**, not merely admitted. The 154× is
neither a reason to exclude nor a free lunch; it is a reason to compress.

**0.3 The apparatus's *first-stage* grammar is not what you want, and its *second-stage* grammar
is not either — but for opposite reasons.** The brief treats "the apparatus" as one thing. It is
two grammars (corpus-wide → clusters; cluster-local → graded apex). The first survives the corpus
change. The second does not (§3). Reusing the pipeline wholesale would ship the half that breaks.

**0.4 `scratch/eliza/sequitur.py` does not exist.** The design doc (§1.1, §3.1) names that path;
the file is at `scratch/eliza/eliza/sequitur.py` — a nested package directory. The apparatus's own
`ELIZA` path computation resolves to `scratch/eliza`, which works only because the import is
`from eliza.sequitur import ...`. A reimplementer following the doc's path literally gets
`ModuleNotFoundError`. Minor, but it is a `[gap]` the clean-room doc did not catch.

---

## 1. WHAT IS THE UNIT? — re-answered with tool traffic IN

**The unit is an EXCHANGE whose body is `operator prose + assistant prose + NORMALISED tool
traffic`.** An exchange = one genuine-human envelope, plus everything emitted before the next one.
Named `turn<NNNNN>`, so the name *is* the citation.

The coordinator's unit is right in shape. The measurement adds one qualifier — normalisation —
and corrects one mechanism — the join key.

### 1.1 The measurement: three unit constructions, head to head

`cluster_phrases` over the same 13 exchanges, three bodies (`tmi_probe4.py`):

| | body | tokens | clusters | band histogram (members → n clusters) |
|---|---|---|---|---|
| **A** | prose only | 6,172 | 19 | `{2:13, 4:6}` |
| **B** | + raw tool traffic | 25,031 | 23 | `{2:15, 3:4, 4:2, 5:1, 9:1}` |
| **C** | + normalised tool traffic | 9,854 | 22 | `{2:15, 4:3, 5:2, 6:1, 7:1}` |

**The band histogram recovers.** A is two-valued; B and C are five-valued with a populated middle.
That is a real and somewhat surprising result — admitting tool traffic partly *undoes* the band
collapse of §3.2.

⚑ **But read what the new breadth is made of, because it is not warrant.** B's top cluster is
`«home mikemol github substrate»` at breadth 9 — a filesystem path. Classifying B's 17
gained clusters (`tmi_probe5.py`):

```
clusters gained by admitting tool traffic: 17
  [ 9] BOILERPLATE «home mikemol github substrate»
  [ 3] warrant?    «every work predicate residue read»
  [ 3] BOILERPLATE «list run con»
  [ 2] BOILERPLATE «file path tmp claude- …-ace tasks bjxpc goh output»
  [ 2] warrant?    «shards size-skewed because hashtext knows nothing about core size»
  [ 2] warrant?    «work mem framing»
  …
  boilerplate 5   candidate-warrant 12
```

**12 of 17 gained clusters are candidate warrant; 5 are boilerplate — but the boilerplate holds the
top of the distribution.** So the graded curve "recovers" largely by grading paths. Normalisation
(C) is what keeps the 12 and demotes the 5: keep the command line, the tool name, and the head/tail
of a result; drop the payload. C reaches nearly B's cluster count at **39% of B's token cost**.

⚑ **And the single best warrant phrase in the corpus survives normalisation:**
`«shards size-skewed because hashtext knows nothing about core size»` — a *measured mechanism* that
appears in both B and C and in neither A. That is exactly the coordinator's case: a framing whose
trustworthiness is inseparable from the measurement beside it. Prose-only loses it.

### 1.2 Does the measurement support the exchange-shaped unit? Yes — with a compression step

Raw admission is affordable at 1.6 MB and is not at 1.19 GB — B is 4× A's tokens against a
superlinear grammar build (§6.3). Normalisation is not a nicety here; it is what makes the unit
tractable at corpus scale while keeping the half that matters.

### 1.3 What is still excluded

| excluded | why |
|---|---|
| tool_result payload body (kept: head+tail ~800 chars) | The verdict lines carry the warrant; the 20k-char body carries file content that clusters as paths. |
| `thinking` blocks | Not a claim made to anyone. A position retracted in thought was never asserted, so it cannot be a framing to recover. |
| `role=user` envelopes failing `human_text`, **as ANCHORS** | A `<task-notification>` is a subagent report injected as user prose that quotes the operator's terms back — `transcriptstruct`'s header records it as the loudest false positive. ⚑ Note this now excludes them from *anchoring* an exchange, not from its body. |
| `queue-operation` envelopes | §2.1(ii) — measured duplicates of `user` envelopes. |
| `system`, `ai-title`, `attachment`, `file-history-*` | Harness metadata. |
| harness error text (`api error overloaded…`, `permission action denied…`) | Clusters at breadth 4 in **all three** constructions. The transcript analogue of the doc's `.bak`-ingested defect (§5.9); excluded by pattern at ingest. |

### 1.4 ⚑ WHERE THIS BRIEF IS WRONG: the join key is not adjacency

The reframe says the 154× ratio "inverts into a JOIN KEY", with the unit being *"operator prose +
the tool calls and results it caused"*. The shape is right; **the causal-adjacency mechanism is
not what the corpus does.** Measured (`tmi_probe5.py`): of 195 claim-bearing assistant sentences
naming a tool or carrying a number,

```
with the named tool INVOKED in the same exchange:  47  (24%)
exchanges containing >=1 tool call:                 9 of 13
```

**76% of claims cite a tool that was not run in the same exchange.** Verified on the coordinator's
own kind of example — the `hashtext` warrant (`--grep-content hashtext`, 9 of 796):

- turn **663** `tool_result`: the source comment `⚑⚑ A PARTITION, NOT A LOCK — abs(hashtext(core_id)) % shards = shard`
- turn **664** assistant: *"That confirms your point precisely."*
- turn **670** assistant: *"the code says so explicitly. **The shard partitions cores, but the atomic unit is still a whole core.** [sppf_db.py:1989]"*
- turns **108 / 555** `tool_result`: the *same* source lines, read in two earlier exchanges

The warrant is real and recoverable — and it is bound to the claim by **the artefact reference**
(`sppf_db.py:1989`, `hashtext`), not by sitting in the same exchange. Turns 108 and 555 are
*different exchanges hundreds of turns apart* carrying the same warrant.

**This makes the design simpler, not harder.** Adjacency would require the unit to be exactly
right; artefact-reference joining is just another phrase in the grammar, which `cluster_phrases`
already handles — `«shards size-skewed because hashtext knows nothing about core size»` clustered
across exchanges *on its own*. So: admit tool traffic into the body (it is where the artefact names
live), and let the clusterer do the joining. Do not build a causal-adjacency model.

⚑ **Fenced code inside assistant prose remains unsettled** — prose by envelope, tool-output by
content. Unchanged by the reframe.

---

## 2. WHAT IS A WITNESS?

**Two envelopes are never two witnesses. Independence here is (a) different actor, or (b)
different session — and neither alone is sufficient.**

### 2.1 Why "two turns" is wrong, measured

Three separate collapses, all present in the 796-envelope test file:

**(i) The actor restating itself.** Of 24 clusters found under actor-split units, **17 were
single-actor** and 7 cross-actor. The single-actor ones include `«let check what»` [4 members],
`«let check whether»`, `«let confirm shard»`, `«sppf scripts sppf»` — the actor's own verbal tics
and repeated tool invocations, clustering perfectly. A naive turn-count witness would have
reported four independent corroborations of `«let check what»`.

**(ii) Literal envelope duplication.** Measured directly:

```
distinct long text bodies: 60;  appearing >1x: 4
  x2  [(225,'queue-operation'), (227,'queue-operation')]  '<cross-session-message …'
  x2  [(427,'queue-operation'), (431,'user')]             '<task-notification>…'
  x2  [(713,'queue-operation'), (716,'user')]             '<task-notification>…'
  x2  [(718,'queue-operation'), (746,'user')]             '<task-notification>…'
```

Every one of these is the *same body* appearing under two envelopes. `queue-operation` is a
shadow of `user`. **Counting envelopes double-counts by construction**, before any semantic
question arises.

**(iii) The three-party agreement.** The brief names this as tonight's cautionary case, and the
test file contains a textbook instance. Turn 249: the actor retracts "13 genuine holes" as a
census artifact. Turn 258/261 (same body, two envelopes): a peer session endorses the split.
Turn 279: the actor relays the retraction to a third session. Three parties, one unchecked
measurement. Then turn 280/283: *"Don't retract the whole bucket — I re-ran your four and got a
different answer on the biggest one."* And turn 305: **"My retraction of it is retracted; your
original item stands."**

Corroboration count at turn 279 would have read **3**. Population of independent measurements: **1**
(and it was wrong). The peer sessions had not re-run the tool; they had read the actor's report.

### 2.2 The proposed definition

A phrase's **witness set** is a set of `(actor, session)` pairs, not turns.

```
witness(phrase) = { (actor_id, session_id) : some unit by that actor in that session
                                             contains the phrase }
breadth = |witness(phrase)|
```

where `actor_id ∈ {operator, actor}` for local envelopes, and — critically — is the **named peer**
for cross-session messages. The test file's `<cross-session-message from-name="substrate-83">`
wrapper carries a real actor identity, and `substrate-83` is a genuinely independent party. This
is a case the memory corpus never had: a fourth actor class.

⚑ **And the definition is still not enough, which I want to state rather than paper over.**
`(actor, session)` distinguishes *who typed it*; it does not distinguish *who measured it*. In the
turn-279 case the three parties were three distinct `(actor, session)` pairs and the corroboration
was still hollow. **The independence that matters is independence of MEASUREMENT, and no property
of the transcript exposes it.** The design's answer is not to claim it: breadth is reported as a
`(actor, session)` count with the pairs *named*, never as a bare number, so a reader can see that
all three trace to one tool run. That is the same discipline as `n of m` — report the population,
do not collapse it.

### 2.3 The consequence for the ≥2 rule

The apparatus's two ≥2 rules map across cleanly, and must stay distinct:

- **≥2 at construction** (`synth_apex`'s `|mset| ≥ 2`) → **≥2 distinct `(actor, session)` pairs**.
  This is the rule that changes, and it is the whole safety property.
- **≥2 at the gate** (`synth_gate`'s corpus-df ceiling) → carries over unchanged in form: no word
  in a rendered thread summary unless ≥2 of that thread's witness units contain it. The
  transcript corpus makes this *more* valuable, not less, because the rendering temptation
  (summarising a thread in one's own words) is exactly what the gate was built to refuse.

---

## 3. DOES THE GRADED CURVE SURVIVE? ⊨ (unaffected by the reframe)

**The clustering survives. The curve does not.** Both measured.

⚑ **One qualifier the reframe adds.** §1.1 shows the band histogram *partially recovers* when tool
traffic is admitted (`{2:13,4:6}` → `{2:15,4:3,5:2,6:1,7:1}`). That does not rescue the graded
curve, because the recovered breadth measures **artefact reuse** (the same path or tool named in
many exchanges), not the shallow-generic skeleton the bands claim to name. The argument in §3.2 is
about what breadth *means* in a self-quoting corpus, and admitting more self-quoting text does not
change it. The band labels stay dropped; the breadth axis stays, renamed.

### 3.1 Clustering: survives, and works well

`G.cluster_phrases` over 13 exchange units, unmodified, `phrase_min=3, min_members=2, tau=0.5`:

```
exchanges=13  tokens=[241,1549,366,1505,760,413,377,50,275,582,18,18,18]
clusters=19
```

The output is not noise. It contains real, nameable threads:

```
[4] «pack core sql»
[4] «python scripts sppf converge shards shard»
[2] «cassian ruled should build headroom reader free space pgsql tmp bytes»
[2] «stale ruling corrected»
[2] «shard partitions cores but»
[2] «insert returning per-core commit»
[2] «cap memory-and-bandwidth ruling»
```

`«stale ruling corrected»` and `«cassian ruled … headroom reader free space»` are two of the
session's actual threads, surfaced with **no seed vocabulary**. That is the improvement on the
hand-built index: the miner needs to be told what to look for, this does not.

It also reproduces the apparatus's known noise: `«api error overloaded server-side issue usually
temporary try again moment persists check https status claude com»` [4] is a *harness error
message* clustering as a concept. That is the transcript analogue of §5.9's `.bak`-files-ingested
defect, and it needs the same fix in kind: exclude by pattern at ingest, not by hoping.

### 3.2 The curve: collapses, and structurally

```
cluster-size histogram (members → n clusters): {2: 13, 4: 6}
```

**Two values. No middle.** With `M = 4`, the apparatus computes `hi = max(3, M//2) = 3`, giving
bands `universal: ms ≥ 3`, `broad: 3 ≤ ms < 3` (**empty by construction**), `pairwise: ms == 2`.
The `broad` band cannot be non-empty for any cluster with `M ≤ 6`. The grading degenerates to a
binary.

This is a sample-size effect *in part*, and would soften on the 1.19 GB file. But the deeper
reason it will not recover is structural, and it is worth stating precisely:

⚑ **The graded curve's premise is an inverse relation between breadth and depth (design doc
§1.2.2): broad phrases are shallow skeletons, narrow phrases are deep co-quotes. That premise
holds because curated memories are INDEPENDENTLY AUTHORED documents about the same idea.
Transcript units are not independently authored — they are a temporal chain in which each unit
literally quotes the previous one.** So in a transcript, a phrase shared by many units is not a
shallow universal skeleton; it is *a phrase that got repeated because the conversation kept
referring back to it*, which is a **thread-persistence** signal, not a genericity signal. The
axis is real, and it is informative, but it does not mean what the apparatus's band labels say it
means.

**Design consequence: keep the breadth axis, discard the band labels and the three-band render.**
Breadth becomes **thread persistence** (how many units in the thread carry the phrase) and is
reported as a span — first unit, last unit, count — not as universal/broad/pairwise. The natural
second axis is not depth but **time**, which the memory corpus did not have and the transcript
corpus does. That replacement is the design's central move.

---

## 4. WHAT DO YOU REUSE VERSUS REBUILD?

Reuse-search run first, per the standing rule. The result is that most of this is reuse.

### Reuse as-is (import, do not copy)

| module / function | role | notes |
|---|---|---|
| `eliza.sequitur.Sequitur`, `NT` | grammar induction | **Do not reimplement.** Utility is deliberately disabled (doc §1.1.4) and that is correct for this use too: a rule seen once is a catalogued fact. Real path is `scratch/eliza/eliza/sequitur.py` (§0.4). |
| `grammar_phrase_lattice.words` | tokeniser | Order-preserving, hyphen-legal (`eea-trace` is one token). Exactly right — `⟡`-slugs survive as tokens. |
| `grammar_phrase_lattice.expand` | rule → phrase | Iterative, capped, cycle-guarded. Reuse. |
| `grammar_phrase_lattice.cluster_phrases` | **the live clusterer** | Measured working on transcripts unmodified (§3.1). The three collapses all transfer; the `PREFIX` set (`feedback/project/reference/discipline`) is memory-corpus-specific and should be re-tuned, not removed. |
| `transcriptstruct.stream / blocks / envelope_role / human_text` | the corpus reader | **This is the abstraction the brief asks for, and it already exists.** `human_text` in particular encodes three hard-won exclusions (§1). |

### Rebuild / replace

| apparatus piece | disposition |
|---|---|
| `synth_apex.build_apex` — the three-band grader | **Replace.** §3.2. Keep the maximal-phrase dedup (§1.2.3) verbatim — it is corpus-independent and correct. Fix the `names[j]` → `names[members[j]]` index-space bug (§1.2.5) rather than inheriting it. |
| `synth_apex.build_context` — the SVD gauge | **Replace with `gauge = set(vocab)`.** The design doc establishes (§1.4, divergence 4) that the live path reads only set membership and the SVD is a no-op. Do not port a no-op. Retune the `3 ≤ df ≤ 60` band — the `≤60` boilerplate cap was sized for ~250 memories and is meaningless at a different N; make it a **fraction of N**, not a constant. |
| `synth_gate` | **Port the mechanism, fix the wiring.** The `stem_match` ceiling logic is good. But run it **before** the write and **read its exit code** (§5.1: the live gate's verdict has never reached production). Implement `metadata.allow` or do not promise it (divergence 2). |
| status / retraction | **New. Nothing in the apparatus does this** — it is atemporal, and revision is a temporal relation. Recast as **linking**, §5. |
| tool-traffic normaliser | **New.** Command line + tool name + result head/tail. Not in the apparatus because the memory corpus has no tool traffic. §1.1. |

### Must not be revived

- `cluster_memories.py` — dead LSA experiment, nothing imports it, writes `MEMORY.candidate.md`.
- `grammar_phrase_lattice.main()` — **destructive**: `rmtree`s `index/` and writes `MEMORY.md`
  with a conflicting staging marker. Import the module's *functions*; never call `main()`.
- ⚑ `synth_wire` — **`import synth_wire` rewrites the live `MEMORY.md` as a module side effect**
  (no `main()`, no `__name__` guard). The prototype in `scratch/` imports
  `grammar_phrase_lattice` and `transcriptstruct` only, for exactly this reason.

---

## 5. RETRACTION AS LINKING, NOT CLASSIFYING

**Recast under the reframe.** The question was *"can status be derived?"*; it is now *"can a
reader arriving at one end of a chain be handed the other end?"* — a strictly easier question,
and the answer is yes.

⚑ **The reframe dissolves what I called the hardest problem, and the coordinator is right about
why.** My retraction-of-a-retraction (249 → pushback → 305) was a *problem* for a status field:
no single label is correct for it. For recovery **it is simply the thread** — the reader wants all
three turns in order and recovers the understanding by reading them. The chain is the deliverable.

**This inverts the error cost, and therefore the tuning.** As a classifier, a false link
*mislabels a claim* — precision-critical. As a navigation aid, **a missed link costs a reader the
recovery; a spurious one costs them a glance.** Recall now dominates. Concretely that changes three
things, all in the direction of a cheaper tool:

1. **Widen the cue set.** I had trimmed toward precise cues. Keep the noisy ones (`you're right`,
   `correction`) — 27 raw cue hits with 9 surviving the recurrence test is now an acceptable
   ratio, and cues I would have dropped for precision stay in.
2. **Drop the labels.** No `RETRACTION-CANDIDATE` / `CONTESTED` / `UNCLASSIFIED` taxonomy. A link
   is a link: *turn B re-quotes turn A under a revision cue*. Bidirectional, so arriving at either
   end finds the other.
3. **Do not attempt chain resolution.** Emit 249→305 and 305→604 as separate links and let the
   reader walk them. Computing "the current state of the claim" is the status oracle the operator
   does not want, and it is where the retraction-of-a-retraction would break the tool.

### 5.1 The mechanism, and why it is not the apparatus's

The apparatus is **atemporal**. Its clusters are sets; a rule's member set has no order.
Retraction is *inherently* a temporal relation: turn B kills turn A. No amount of grammar
induction over an unordered token stream can express it.

But the ingredients are all present, and the operator is cheap. The prototype's operator:

> A unit `B` is a **retraction candidate for thread `P`** iff `B` contains a retraction cue AND
> `B` contains cluster-phrase `P` AND some unit `A < B` contains `P`.

That is: *a later turn re-quoting an earlier turn's phrase alongside a withdrawal cue* — which is
precisely the signal the brief hypothesised. It works.

### 5.2 Measured

Cue set: `retract|withdraw|superseded|i was wrong|correction|you're right|overclaim|my
(mistake|error)`.

```
retraction-cue hits by source:
   11  assistant-text  correction        1  assistant-text  overclaim
    7  assistant-text  retract           1  assistant-text  my error
    5  assistant-text  you're right
    2  assistant-text  i was wrong
total human cues: 0     total actor cues: 27
```

Cue alone: 27 hits, unusable — `correction` and `you're right` fire on ordinary agreement.
**Cue ∧ re-quotes-an-earlier-cluster-phrase: 9 candidates**, each carrying the earlier turn index.

Hand-verified against `--grep-content`, and the result is better than expected. The 9 candidates
sit on a **single real retraction chain**, and the chain is a genuinely hard case:

| turn | what happened |
|---|---|
| 249 | *"THE '13 GENUINE HOLES' FIGURE IS ITSELF A CENSUS ARTIFACT — I RETRACT IT."* |
| 257 | *"I retracted a number I gave you and a peer."* |
| 276 | *"My whole claim was wrong, and I need to retract it immediately."* (a **second, different** retraction — the `--sqlname` one) |
| 280/283 | peer: *"Don't retract the whole bucket — I re-ran your four."* |
| **305** | ⚑ *"`Foundation/Fin/Literals` is a GENUINE HOLE. **My retraction of it is retracted; your original item stands.**"* |
| 604 | *"`Fin/Literals` holds at 33 — a real hole, surviving both my wrong retraction and the fix."* |

**A retraction of a retraction.** An index that recorded only turn 249 would report the "13
genuine holes" figure as withdrawn. It was withdrawn and then reinstated. The hand-built jsonb
index's six retractions were found by reading; this operator found this chain mechanically.

Note also two *distinct* retractions (the `--holes` one and the `--sqlname` one) running
concurrently across the same turns, with overlapping vocabulary — the design doc's "two arcs share
a vocabulary" hazard, appearing in the retraction layer.

### 5.3 What this means for the deliverable — stated plainly

The tool emits, per thread, a set of **revision links**:

```
LINK  turn 249 ──re-quotes-under-cue──► turn 305   phrase «four four zero names artifact»
```

No label, no verdict, both endpoints navigable. The reader arriving at 249 (*"I RETRACT IT"*) is
handed 305 (*"my retraction of it is retracted"*) and reads both.

⚑ **This removes the failure mode I was most worried about, rather than mitigating it.** The
asymmetric danger was a tool reporting a *reinstated* claim as retracted — a wrong verdict. With
no verdict there is nothing to be wrong; the worst case is a link a reader glances at and
dismisses. That is a genuinely different risk profile, and it is the coordinator's point.

**What the tool still must not do:** resolve a chain to a current state, or emit
`decided`/`open`/`blocked`. Not because it would be imprecise, but because *the resolved state is
the thing the reader is trying to reconstruct by reading* — precomputing it defeats recovery even
when it is correct.

---

## 6. PROPOSED DESIGN

### 6.1 Data flow

```text
*.jsonl ──[transcriptstruct.stream/blocks/human_text]──► envelopes
    │
    ├─ ANCHOR on genuine-human envelopes only (human_text)           §1.3
    ├─ EXCLUDE: thinking, system, ai-title, file-history-*,
    │           queue-operation (dup of user), harness error text
    ├─ NORMALISE tool_use  → command + tool name + key args          §1.1
    ├─ NORMALISE tool_result → head+tail (verdict lines, not body)
    ▼
UNITS: exchange = (turn_idx, session, actor,
                   operator prose + assistant prose + normalised tools)
    │   actor ∈ {operator, actor, peer:<name>}
    ▼
[grammar_phrase_lattice.words] ──► token sequences
    ▼
[grammar_phrase_lattice.cluster_phrases]  (reused unmodified)  §3.1
    ▼
THREADS: (phrase, {units})
    │
    ├──► BREADTH  = |{(actor,session)}|,  pairs NAMED not counted    §2.2
    │               drop any thread with breadth < 2
    ├──► SPAN     = (first_turn, last_turn, n_units, sessions)       §3.2
    │               ← replaces the universal/broad/pairwise bands
    ├──► WARRANT  = artefact references in the thread's units        §1.4
    │               (tool names, file:line) — the join, NOT adjacency
    └──► LINKS    = revision operator: cue ∧ phrase-recurrence ∧ A<B §5
                    bidirectional turn↔turn. No labels, no resolution.
    ▼
[gate: no rendered word without ≥2 witness units]                    §2.3
    ▼
RECOVERY INDEX — by thread, ordered, every row citing (file, turn, role)
```

### 6.2 Modules

| module | responsibility |
|---|---|
| `tmi_units.py` | envelopes → units. Owns every exclusion in §1 and the actor/session identity in §2.2, including the `<cross-session-message from-name=>` peer parse. The only module that knows about `.jsonl`. |
| `tmi_threads.py` | units → threads. Thin: calls `cluster_phrases`, computes breadth over `(actor,session)`, computes span. |
| `tmi_status.py` | the retraction operator. Owns the cue list, the recurrence test, and the three labels. Standalone and separately testable — this is the part with no prior art. |
| `tmi_index.py` | render + gate. Emits the thread index; refuses a word without ≥2 witness units. |
| `tmi.py` | CLI. Modes: `--units`, `--threads`, `--status`, `--index`, `--selftest`. Every mode prints `n of m`. |

**Read-only by construction**, per `synth_coverage`'s defended position (doc §4.5): no `--apply`,
no write mode outside an explicit `--out <path>`. It reads someone's conversation history; it
should not be able to be the thing that damages it.

**`--selftest` from the start.** The apparatus has exactly one selftest across 15 modules
(doc §5.12) and it is in the only module that has never broken. Pin: the `human_text` exclusion
count on a fixture, the duplicate-envelope collapse, and — most importantly — the retraction
operator against the turn-249→305 chain, which is a *known-answer test with a known trap* (naive
implementations report "retracted" and stop).

### 6.3 Cost

The corpus is 94% one file. `cluster_phrases` on 13 units was seconds; the corpus grammar over
~250 memories takes ~78 s (doc §3.3) with a superlinear `_find_exact_rule_for` scan. On thousands
of units that scan is the bottleneck. The doc's own note applies: **replace the linear scan with a
`{digram → rule_id}` side-map** — identical output, large speedup, and this is where it pays.

Process the 1.19 GB file with a `--since/--until` turn window (the modes exist) and build the
index incrementally per session; do not attempt one grammar over the whole corpus on the first
run.

---

## 6.4 What RECOVERY requires that an INDEX does not

The coordinator's instinct — **ordering** and **warrant adjacency** — is right on the first and
right-in-substance-but-wrong-in-mechanism on the second. Four more, from the corpus.

**(a) ORDERING — yes, and it is the cheapest thing here.** An index is a set; a recovered framing
is a *sequence*. The 249→305→604 chain is unreadable in any order but the one it happened in. The
apparatus has no ordering at all (its clusters are sets), which is why §3.2 replaces the band
grading with a temporal span. Cost: one integer per unit.

**(b) WARRANT — yes, but joined by ARTEFACT REFERENCE, not adjacency.** §1.4. The measurement says
24% intra-exchange; the `hashtext` warrant reached its claim across turns 108, 555, 663 → 670. What
a reader needs beside `"the shard partitions cores but the atomic unit is still a whole core"` is
`sppf_db.py:1989` and the comment it names — and that is retrieved by *the reference*, which the
clusterer already indexes once tool traffic is in the body.

**(c) ⚑ THE REFUTATION, WHICH THE INDEX FRAMING ACTIVELY SUPPRESSES.** This is the one I would add
most emphatically. A recovered framing is only trustworthy if you also recover *what was tried
against it*. Turn 249's retraction was itself refuted by a peer who **re-ran the tool** — and the
refutation is what makes the final state (`Fin/Literals` is a genuine hole, 33 names) believable.
An index optimises for the *claim*; recovery needs the claim plus its strongest challenge. The
revision links of §5 are exactly this, which is a second and better argument for keeping them
after the status field is dropped.

**(d) THE DISCARDED ALTERNATIVE.** Repeatedly in this corpus the operator's framing is *"not X but
Y"*, and the compaction keeps Y while losing X. `«iteratively rather atomically»` (a gained cluster
in §1.1) is literally this shape: *"the depth must be consumable ITERATIVELY rather than
ATOMICALLY"*. Recovering Y alone loses the contrast that makes Y meaningful. Practically: when a
thread's phrase contains a contrast marker (`rather than`, `not … but`, `instead of`), **both
sides belong in the recovered unit** — do not let the maximal-phrase dedup (§1.2.3 of the doc) trim
one away.

**(e) NEGATIVE RESULTS AND THEIR DENOMINATOR.** *"0 of 218,475"* is a finding; *"0"* is not. The
corpus's own `report presence, never absence` discipline applies to what gets recovered: a framing
of the form *"we looked and found nothing"* is worthless without the population it was looked for
in. If a thread's warrant is a negative measurement, the denominator is part of the warrant.

**(f) WHO SAID IT — and this is where recovery diverges hardest from an index.** §2's independence
work was built to support a *witness count*. Under recovery, breadth matters much less, but
**attribution matters much more**: an operator directive and the actor's restatement of it are not
interchangeable, and the compaction is precisely what blurs them. The `(actor, session)` tagging
already in the design serves recovery better than it served the witness count — keep it, and
surface the actor on every recovered line rather than aggregating it into a number.

---

## 7. WHAT I COULD NOT SETTLE

- ~~⚑ **Recall of the revision operator — now the load-bearing unknown**~~ — **MEASURED AND
  ACTED ON (2026-08-24), and the act changed the answer twice.** Implementation and score harness:
  `scratch/tmi_status.py` (`--score`, `--cues`, `--links`, `--misses`, `--artefacts`, `--selftest`).

  | | cue set | recurrence | fire rate | recall (recoverable labels) |
  |---|---|---|---|---|
  | before | §5.2's | cluster-phrase overlap | — | 9/30 (30%) |
  | after | + widened `was wrong`, contrast **frames**, prose self-quotation | `union` | **15%** of 494 actor units | **14/14** |

  Three corrections to the plan that produced this, each measured:

  1. **A widened cue set alone is degenerate, and reviser-recall cannot see it.** The first cut
     took bare `not` as a contrastive cue and ran quote-detection over the whole unit body: recall
     14/14 while firing on **48%** of the corpus and backlinking nearly every revision to turn 11.
     The census named both causes — 572 hits on bare `not`, and 95/88/42 "self-quotes" that were
     the `tool_use` argument **names** `description` / `command` / `file_path`. §1.4 rightly admits
     tool traffic to the body for the artefact join; the cue detector must not read it. Contrast
     now fires only on the two contrast **frames**, self-quotation only on assistant prose.
     → `tmi-F7`.
  2. **§6.4(d)'s `not X but Y` is now wired into the operator, and it is cue-and-recurrence in one
     token.** For an explicit cue ("I retract"), the cue says only *that* a revision happened and a
     separate test must find *which* turn it revises. For a contrastive negation or a
     self-quotation the **negated / quoted span IS the earlier phrasing**, marked as such by the
     writer. That is why these two classes reach paraphrased revisions where overlap cannot.
  3. **⚑ The artefact join does NOT subsume overlap — coverage is their UNION.** See below.
- ⚑ **`--score` cannot compute recall against 30, and says so.** The hand-label was reduced to a
  COUNT (27 certain + 3 uncertain) before it was externalised; only **14 of 30** have recoverable
  turn labels. A figure quoted against 30 would read the count as if it were the labels — tmi-F1's
  own error, committed by the measurement that found tmi-F1. Ground truth now lives inline in
  `tmi_status.GROUND_TRUTH` with `WHY_INCOMPLETE`. **Re-deriving the missing 16 is the next
  measurement**, and it is what gates the full §6 build. → `tmi-F6`, `tmi-F9`.
- ⚑ **§1.4's join key is the right *kind* and the wrong *sole* mechanism — this refutes the plan
  that fixed §5.** Ⓘ3 proposed replacing token overlap with the artefact join, on the witness of
  turn 383 (*"the N ≤ 3 cap is a memory-and-bandwidth ruling"*) revised at 396 (*"the fold doesn't
  lease from it"*). **The artefact join misses exactly that pair.** 396's shared referents are
  `membudget` (63 turns — universal, correctly rejected) and `N ≤ 3`, a **quantity name** no file /
  flag / symbol pattern matches; `work_mem` matches but links to turns 40/108/110. The shared
  referent is a **discourse** referent, which is a phrase — which `mode=phrase` catches. The two
  tests have complementary blind spots (artefact reaches paraphrase, phrase reaches discourse
  referents) and neither dominates, so `union` ships and `MODE_RESIDUE` keeps both. → `tmi-F8`.
- ⚑ **And "join on the artefact reference" is degenerate until fan-in is read GRADED.** Joining on
  mere co-occurrence pointed every link at turn 11, the session opener, because it names
  `obs_node` / `--holes` / `schema.py`, which then recur for 700 turns. `tmi-F5` unified Sequitur
  `uses`, SPPF fan-in and apex band-breadth as one statistic read along the sharing axis — and the
  apexes have always read that axis **graded**, universal-shallow to pairwise-deep. A universal
  artefact is the shallow end: shared by everything, discriminating nothing. Rarity weighting
  (`ARTEFACT_DF_FRAC`, a declared `[gap]` fitting constant) plus nearest-antecedent cut top-
  antecedent concentration to **3%** over 105 distinct antecedents. ⚑ Reviser-recall was 100%
  both before and after this fix: **a revision link is a PAIR, and scoring only the end the ground
  truth records measures half of it.** `--score` now prints an ANTECEDENT SPREAD census.
- ~~**The `df ≤ 60` boilerplate cap. Must become a fraction of N**~~ — **done** as
  `ARTEFACT_DF_FRAC`, but the fraction is **fitted, not derived**: it is the loosest value at which
  396 backlinks past turn 11. Still a `[gap]`; a second corpus should re-fit it, and `--score` is
  the harness that would.
- **The normaliser's key set.** `tmi_probe4.norm_tool_use` keeps `command / description / pattern /
  query / file_path / prompt / old_string / new_string`. That list is a guess that worked on one
  file; it is the new `[gap]` constant and it should be derived from a tool-name census, not hand-listed.
- **Whether the 24% intra-exchange figure holds at scale.** It is one file, and the 4 tool-call-free
  exchanges at the tail are short wrap-up turns that may be skewing it. The *mechanism* (artefact
  reference, not adjacency) is confirmed independently by the `hashtext` trace; the *ratio* is not.
- **Whether the clustering survives at 1.19 GB scale.** Everything in §3 is one 1.6 MB file. The
  band collapse I argue is structural; the *cluster quality* claim is not tested at scale.
- **Whether `cluster_phrases`'s tuning constants transfer.** `tau=0.5`, the `0.8` shortcut, the
  `≥2 shared tokens` kernel — all `[gap]` in the apparatus, all tuned for ~250 curated documents.
  They produced usable output on 13 exchanges, which is weak evidence and I am not treating it as
  more.
- **Fenced code inside assistant prose** (§1). Prose by envelope, tool-output by content.
- **The `df ≤ 60` boilerplate cap.** Must become a fraction of N; I did not derive the fraction.
- **Whether the peer-session actor identity is stable.** `substrate-83` / `substrate-45` appear as
  `from-name` attributes. Whether those names are stable across sessions, or per-session
  ephemeral, decides whether `(actor, session)` is the right key or whether actor alone suffices.
  Not checked.
- **Whether this should be built at all, versus improving the `transcript-miner` agent.** I lean
  build, on one specific ground: the skill's own "Growing this" section names *"No index
  artefact — a mining dispatch produces its index in the report and it dies with the turn"* as
  gap 2, and *"No retraction reader"* as gap 3. This design is those two gaps. But it is
  complementary to the agent, not a replacement: the agent reads and judges, this tool
  *navigates and flags*. A design that positioned it as a status oracle would be the wrong build,
  which is why §5.3 is worded the way it is.

---

## 8. PROTOTYPE ARTEFACTS

Throwaway, in `scratch/`, read-only, no memory-corpus writes:

- `scratch/tmi_probe.py` — unit-shape measurement (§0.1, §0.2), clustering over exchanges (§3.1),
  band histogram (§3.2), cue census (§5.2).
- `scratch/tmi_probe2.py` — actor-split independence (§2.1 i), the retraction operator (§5.2).
- `scratch/tmi_probe3.py` — duplicate-envelope measurement (§2.1 ii).
- `scratch/tmi_probe4.py` — **the reframe test**: three unit constructions head to head
  (prose-only / raw tool traffic / normalised), band histograms and surfaced phrases (§1.1).
- `scratch/tmi_probe5.py` — warrant adjacency (the 24% figure) and boilerplate-vs-warrant
  classification of the clusters tool traffic adds (§1.1, §1.4).

⚑ **AND ONE THAT IS NOT A PROBE.** `scratch/tmi_status.py` is the `tmi_status` module of §6.2 —
the revision operator, *"the part with no prior art"* — built and scored rather than prototyped.
It is the only §6 module that exists. Read-only by construction (no write mode at all, per §6.2),
standalone, and it carries its own ground truth (`GROUND_TRUTH` — **complete as of round 2**, 39
rows each with turn and quoted line; `WHY_INCOMPLETE` now records the resolution rather than the
gap) and its own score harness, because §7's recall unknown could not be retired by a probe that
reported a number and exited.

`--selftest` pins 36 checks including the two **measured** regressions — a JSON key read as a
self-quotation, and bare `not` read as a contrast cue — plus the §6.2 known-answer trap (the
249→305→604 chain must emit three separate links and no `resolve_chain` may exist), and one
**end-to-end** check on the real corpus asserting that no single turn holds more than 15% of all
backlinks. ⚑ That last one is the check that matters: every unit-level check passed while the
detector was degenerate.

**The remaining three modules (`tmi_units`, `tmi_threads`, `tmi_index`) are deliberately NOT
built** — see §7 and `tmi-F9`. Not because recall is poor, but because the linker is validated
against 14 of 30 labels and this corpus has already demonstrated a 100%-recall detector that was
broken.

> ⚑ **SUPERSEDED IN ROUND 3 (§8.2), and left standing rather than rewritten** — the withholding and
> its reason are the record of why the build waited two rounds, and deleting them would leave
> `tmi_index.py` looking like it could have been written on day one. `tmi_index.py` now exists;
> `tmi_units` and `tmi_threads` remain unbuilt as separate modules, their responsibilities absorbed
> into `tmi_status.load_units` and `tmi_index.build_threads` respectively — §6.2 calls the threads
> module *"thin"*, and a file whose whole body is one call to `cluster_phrases` is a module boundary
> that costs an import and buys nothing.

### 8.1 ⚑⚑ ROUND 2 — the blocker cleared, and the build is WITHHELD AGAIN

Round 2 cleared both gating measurements and then declined the build they gated. The gate was
*"Ⓘ5 is gated on Ⓘ6+Ⓘ7 clearing"*; they cleared, and **what they cleared into is the reason not
to build.**

**Ⓘ6 (`tmi-F10`) — the missing 16 were never missing.** An exhaustive re-label of every assistant
prose block in 0–712 (via `transcriptstruct --prose`, a mode added for this pass and run **before**
the detector, so the label set is not bounded by search order) finds **39** revision-bearing turns,
not 30. All 14 previously recorded are among them. The brief's framing — *recover the missing 16* —
was a hypothesis; the honest outcome was re-deriving the total. `WHY_INCOMPLETE` now records the
resolution, and every row carries its turn and quoted line.

**Ⓘ7 (`tmi-F12`) — and completing the ground truth made recall fall.**

| mode | 14-label GT | 39-label GT |
| --- | --- | --- |
| `none` | 100% | **33/39 (84%)** |
| `union` | 100% | **32/39 (82%)** |
| `artefact` | 100% | **31/39 (79%)** |
| `phrase` | 100% | **31/39 (79%)** |

The detector did not change. The ground truth stopped being a subset of what the detector already
found. **The missing labels were not a random sample** — they were disproportionately the cases the
detector misses, which is exactly what a positives-only label set drawn from a detector-assisted
pass will do.

**And pair scoring is what separates a real detector from a degenerate one** — `--score` and the
now-implemented `--ablate` report both ends:

```text
cue only (no recurrence)   links=  94  recall=33/39  ant-plausible= 35%  concentration= 75%  distinct-ant=  23
+ phrase recurrence        links=  68  recall=31/39  ant-plausible=100%  concentration=  7%  distinct-ant=  95
+ artefact recurrence      links=  70  recall=31/39  ant-plausible=100%  concentration=  3%  distinct-ant= 107
+ both (union)             links=  78  recall=32/39  ant-plausible=100%  concentration=  6%  distinct-ant= 112
```

⚑ **Read the top row against the rest.** The cue-only detector has the BEST recall and is the
WORST detector: 35% of its backlinks point forward in time, and one turn holds 75% of them. Adding
the recurrence test *costs two points of recall* and buys the antecedent end entirely. **Recall
alone ranks the recurrence test as a regression.** That is the falsification round 1 could not
perform, and it is now a standing selftest.

**Why the build is still withheld — `tmi-F14`, and it is a different reason than round 1's.**
Round 1 withheld because the linker was validated against too few labels. That is fixed. The new
reason is what the complete label set exposed: **the 8 remaining misses are not scattered, they
concentrate in one taxonomy class the cue set structurally cannot see.**

`OPERATOR-REFUTATION` — the actor conceding to a correction the operator made in the turn being
replied to. Witnesses: 401 (*"You're right to push — I took that from a source comment and never
checked it"*), 644 (*"I should have gone straight to the diagnosis"*), 664 (*"That confirms your
point precisely"*), 676, 198. The cue `you're right` fires **6 times in 507 units** and these are
phrased *around* it. The revised claim lives in the **prior turn** and the cue is a bare concession,
so the explicit set, the contrast frame and self-quotation all have nothing to match.

⚑ **This is a missing cue CLASS, not a tuning gap, and it is load-bearing for the index specifically.**
An operator-refutation is the single highest-value revision a compaction-recovery index can carry —
it is where the operator's correction entered the record — and it is the class the linker is blind
to. Building `tmi_threads` on top would produce an index whose *most* important threads are the ones
silently absent, and §5.3's reader arriving at the antecedent would be handed nothing. An absent
thread and a thread with no revisions are indistinguishable to that reader.

Also measured and unfixed: the self-quotation class is degraded by apostrophes — `it's` / `that's`
are read as quote delimiters, producing junk spans like `'s a coordination point I'` in `--cues`.

**⟡next: the cue class before the index.** Add `OPERATOR-REFUTATION` (its recurrence probe is the
prior turn, not a phrase — the antecedent is structurally adjacent for this class alone, which is
the one place §1.4's rejected adjacency join is the *right* one), fix the apostrophe boundary in
`QUOTED`, re-score. Only then Ⓘ5.

All five run against `28df5f75-745e-4963-ae8a-1431f7ace5ab.jsonl` (1.6 MB, 796 envelopes) and
import `grammar_phrase_lattice` and `transcriptstruct` as libraries. Neither `synth_wire` nor
`grammar_phrase_lattice.main()` is reachable from any of them.

---

### 8.2 ⚑⚑ ROUND 3 — Ⓘ9 closed the blocker, and the index SHIPPED

Round 2's criterion was explicit: *"Add `OPERATOR-REFUTATION` …, fix the apostrophe boundary in
`QUOTED`, re-score. Only then Ⓘ5."* All three are done, the named class is closed, and
`scratch/tmi_index.py` is built.

**Ⓘ9a — the apostrophe.** `QUOTED` admitted a bare `'` as both delimiters, so two contractions in
one sentence produced a span running from one to the next (`it's slow … it's printed` →
`s slow. Let me see what it`). A length filter cannot catch this: the junk span is exactly
quote-length. Now an ASCII/typographic `'` is a delimiter only when **not flanked by word
characters**; double and curly-open quotes are unambiguous and stay unconditional.

**Ⓘ9b — the concession cue, and the brief's warning did not hold.** The brief predicted a
concession cue would be *"at least as dangerous"* as the naive contrast list, which fired on 48%.
Measured, it is the **least** frequent of the four classes:

| class | fires in | of 494 actor units |
| --- | --- | --- |
| `explicit` | 49 | 9.9% |
| `contrast` | 40 | 8.1% |
| `selfquote` | 22 | 4.5% |
| **`concession`** | **6** | **1.2%** |

⚑ **The anchor is the whole cue, and the difference is structural rather than lucky** (`tmi-F16`).
The contrast list matched a WORD, whose rate is bounded only by prose frequency. A concession cue
anchored to the **start of an assistant prose block** matches a POSITION that occurs once per turn,
so its firing rate is bounded by the turn count *by construction*. Unanchored, `you're right` is
ordinary prose — `CUE_EXPLICIT` already carried it at 6 hits. Anchored, all 5 raw hits are
ground-truth positives. `--score` gained a **per-class firing-rate block** so this stays falsifiable.

**⚑⚑ Ⓘ9c — and the brief's recurrence probe was WRONG (`tmi-F15`).** The brief said the antecedent
is *"the PRIOR TURN — the one place §1.4's rejected adjacency join is RIGHT."* The corpus refutes
adjacency on both ends:

- **Filler envelopes sit between.** 198, 401, 644 and 676 each carry a `file-history-snapshot`
  (often a `system` too) between the human turn and the concession; 649 has two `queue-operation`
  envelopes. Turn−1 is a snapshot with no text.
- **The prior turn is often a tool_result.** 664's predecessor is a 45-line `Read` result; the
  "point" being confirmed is a human turn further back. 632's is a `pgrep` result.

The join is **nearest preceding HUMAN turn** — a *stronger* claim than adjacency, not a weaker one:
it says a concession's antecedent is the operator's last utterance, which is what "you're right"
semantically points at, and it is robust to arbitrary interleaved tool traffic. **So §1.4's measured
rejection of adjacency stands unamended — this is not the exception the brief thought it found,
because it is not adjacency.** (`load_units`' `human` tag is the predicate; `role == "user"` is not
— 189 user envelopes carry 13 human prose blocks.)

**Re-scored on the 39-label ground truth, both ends:**

| mode | recall before | recall after | ant-plausible | concentration |
| --- | --- | --- | --- | --- |
| `none` | 33/39 (84%) | **34/39 (87%)** | 40% | 67% |
| `phrase` | 31/39 (79%) | **33/39 (84%)** | 100% | 6% |
| `artefact` | 31/39 (79%) | **34/39 (87%)** | 100% | 3% |
| `union` | 32/39 (82%) | **34/39 (87%)** | 100% | 6% |

⚑ **The tradeoff round 2 reported is gone.** `artefact` now *matches* the cue-only ceiling (34/39)
while holding 100% antecedent-plausibility and 3% concentration — the recurrence conjunct no longer
costs recall. And link count went **down** (70→68) while recall went up: the apostrophe fix removed
junk while the concession cue added true positives.

**⚑ The residual is one named class, not scattered noise (`tmi-F17`).** The 4 remaining certain
misses — 38, 209, 632, 649 — are **EVIDENCE-SUPERSESSION**: the actor's *own* earlier claim revised
by **tool output**. `tmi-F14` conflated this with operator-refutation; they are distinct. The prior
envelope is a tool_result in all four and there is *no human turn to point at*, so the Ⓘ9 join is
structurally inapplicable. **The cue is not the failure** — 209, 632 and 649 all carry contrast
frames. The **recurrence probe** is: the antecedent is tens of turns back behind an artefact that is
either head-cut as universal (`sppf_db.py` is everywhere) or is a bare discourse referent (*"shard
0"*, *"it"*). The successor is an **actor-claim posting list**, not another cue class.

#### Ⓘ5 — `scratch/tmi_index.py`, built

Renders §6.1's *"RECOVERY INDEX — by thread, ordered, every row citing (file, turn, role)"*. Reuse
per §4: `cluster_phrases` / `words` / `expand` from `grammar_phrase_lattice`, `stream` / `blocks` /
`human_text` from `transcriptstruct`, units and the revision operator from `tmi_status`. **Nothing
copied**; `cluster_memories.py` is not revived and `synth_wire` is never imported — both pinned by
selftest, not by intention.

Modes: `--threads`, `--index [--limit N] [--out P]`, `--thread <phrase>`, `--gaps`, `--selftest`.
Read-only by construction — the sole write is an explicit `--out`, and the selftest asserts `main`
never branches on `--apply` and contains exactly one `open(`.

⚑ **Building it exposed §1.1's tool-traffic normaliser as SPECIFIED BUT NEVER WRITTEN.** The first
`--threads` run was mostly harness boilerplate: «file path home mikemol» (33u), «tmp claude-…»
(32u), «command did complete within timeout», «system-reminder warning file exists but contents
empty» — absolute paths, harness notifications and JSON argument keys, none of them anything an
actor said. This is the **same defect as the `selfquote 'description'` census hit** one module over
— reading tool *structure* as prose. `tmi_status` fixed it for the cue detector by splitting `body`
from `prose`; the clusterer needed the same split and did not get it, because §1.4 legitimately
wants tool traffic **in** for the artefact join. Both are right: **artefacts want the raw body,
threads want the normalised one.** With the normaliser (paths → basenames, harness furniture and
JSON keys stripped, `\uXXXX` decoded, results kept head+tail): **379 → 282 threads**, and the
surviving heads are substantive (`stale central claim`, `peer unreflected puzzle`, `plan blockers
all closed`, `temp spill zswap writeback`).

⚑ **Two more defects the render exposed, both the head-cut principle in a new place.** Turn 110
writes a *plan document* whose vocabulary recurs for 600 turns and collected **15 backlinks** — the
turn-11 pathology one layer up, so `FANOUT_CAP` truncates and *reports the count* rather than
silently dropping ("a vocabulary source, not a single claim"). And the same pair rendered three
identical `↓ revised at turn 396` arrows, once per joining artefact: how many join keys witnessed a
link is a property of the **detector**, not the history.

⚑ **`--gaps` ships with the instrument.** An index that lists only what it found lets a reader read
absence as nonexistence. `--gaps` prints the evidence-supersession class, its four turns with quoted
lines, and its successor — pinned by selftest so a later edit cannot quietly drop the disclosure and
hand the reader a clean list.

`tmi_status --selftest` 36 → **51**; `tmi_index --selftest` **33**. The concession class is pinned
in *both* directions (anchored fires, mid-sentence does not) and the human-join is pinned with a
fixture reproducing the filler layout, so a regression fails a test rather than silently losing the
index's highest-value threads again.

### 8.3 ⚑⚑ ROUND 4 — two of three commissioned items were ALREADY DONE, and the third's premise was wrong

Round 4 was briefed as Ⓘ11 (build §1.1's tool-traffic normaliser), Ⓘ12 (register a missing
`tmi-F13` witness) and Ⓘ10 (the evidence-supersession residue). **Ⓘ11 and Ⓘ12 were already
satisfied**, and both misreadings have the same shape as the ones this design has been correcting
since round 1 — a fact about a *method* reported as a fact about the *substrate*.

| item | briefed as | measured |
|---|---|---|
| Ⓘ11 | normaliser "never built through two review rounds" | `normalise_tools` is live in `tmi_index.py`, wired into **both** `build_threads` and `render`. `--threads` reports **282 of 507**, the post-fix figure. `tmi-F20` |
| Ⓘ12 | `tmi-F13` has no registered witness | registered under its **full key** `tmi-F13-census-reads-test-data-as-dispatch` and `holding`. The bare stem `tmi-F13` is a key in neither roster, and lookup is exact-match. `tmi-F22` |
| Ⓘ10 | cue fires, recurrence probe fails | **the cue does not fire.** `tmi-F19` |

⚑ **`tmi-F17` named the wrong conjunct, and the instrument that refutes it was already in the file.**
It states the four certain misses "all carry contrast frames" and that "the failing conjunct is the
RECURRENCE PROBE". Turn 632's entire prose is *"Shard 0 is **gone** — no process. It exited without
writing a step line…"* — no contrast frame, no concession, no retraction, no self-quotation.
`--score --ablate` settles it corpus-wide and predates the finding: **cue-only recall 34/39 is
identical to artefact recall 34/39**, so the recurrence conjunct costs *zero* recall. The five
misses are a **cue-set** gap.

⚑ **Ⓘ10 was built anyway, and it earns its place on the other end of the link.** `tmi_subject.py`
keys an actor claim by its **subject position** — the NP before the first finite verb — rather than
by any identifier inside it, so it reaches `shard 0` (fan-in 7) and `the fold` (5): referents that
match no file/flag/symbol pattern and are invisible to the artefact index *at any threshold*. A
closed pronoun set resolves **positionally** to the nearest preceding named subject, and `--subjects`
prints the donor turn beside every resolution, so a wrong inheritance is falsifiable rather than
buried in a score.

|  | links | recall | ant-plausible | distinct antecedents |
|---|---|---|---|---|
| artefact | 68 | 34/39 | 100% | 109 |
| **subject** | 33 | 22/39 | 100% | 44 |
| union (+subject) | 74 | 34/39 | 100% | **116** (was 109) |

**Standalone it is weaker and that is reported, not hidden.** Its value is additive on the
*antecedent* end — the half §5.3 says a reader needs and recall cannot see — and the reason is
`correlated-instruments-agreeing-is-not-coverage`: its blind spot (83 of 179 actor-prose units yield
no claim subject, printed by `--gaps`) is disjoint from the artefact probe's. The
evidence-supersession pair **638 ← 632 via «shard 0»** is emitted by this mode and by no other.

Three extraction *refusals* are load-bearing and each was measured rather than assumed: a span with
no finite verb is not an assertion; a span containing a subordinator or colon means the verb found is
not the main one (this yielded the subject «let me check whether the store» before the check
existed); and a first-person head is not a referent that tool output can supersede.

⚑ **The general lesson, and it is the complement of `tmi-F18`'s own.** That finding concluded *"a
design section marked NEW is not evidence it was built."* The inverse cost this round more: **a
finding that names a defect is not evidence the defect is still open.** `tmi-F18` reports the defect
and its fix's measurement (`379 → 282`) in one untensed entry, so its headline says a component does
not exist while its body reports that component's effect — and the headline is what a brief-writer
copies.

`tmi_subject --selftest` **15/15**; `tmi_status --selftest` **51/51** unchanged; no new rows in
`toolmodes --divergence`.
