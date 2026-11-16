# Ⓝ31 residue — writing the record

**Concern: the tooling that writes THIS arc's record, and what the record's own shape cost.**
See [`toolmodes-split.md`](toolmodes-split.md) for the index and the arc's frame.

⚑ **THIS PART IS ITS OWN SUBJECT.** Ⓝ36a is the write mode that appends where it says it
replaces; Ⓝ60 is the measurement of what that did to this document; Ⓝ81 is the operator's ruling
that a paydown record kept as one drawer is the same defect as a file doing too much. The three
are one thread, and they are why the other parts exist.

⚑⚑⚑ **Ⓝ85 ⟡a-restated-fact-is-a-second-authority — CAUGHT THREE TIMES IN ONE AFTERNOON, AND I
INTRODUCED EACH LAYER WHILE FIXING THE PREVIOUS ONE.** The split's own scaffolding reproduced this
arc's root finding three times, each a level deeper than the correction that preceded it:

    1. a MEASURED FIGURE     a `lines` column of `mdstruct --budget` values in the index.
                             First drafted as an estimate, wrong by up to 60%; corrected to real
                             measurements; the operator then measured one part at 95 where the
                             table said 97 — stale on its first day, nobody having edited it.
    2. a SET CARDINALITY     every header read "Part N of 10" — one fact about the SET, restated
                             in every member, so an eleventh part falsifies all ten at once.
                             The sweep to keep them true had already failed once mid-edit.
    3. an ORDINAL            "Part 4", and `-04-` in ten filenames. Inserting a document between
                             03 and 04 renumbers every part after it, plus the index and every
                             cross-reference, for documents that did not change.

⚑⚑⚑ **AND (3) IS THIS ARC'S OWN SUBJECT, BUILT INTO THE FILENAMES OF THE RECORD THAT ARGUES
AGAINST IT.** ⟡symbolic-reference-only is one document over; `lifecycle.py` states it exactly —
*"a POSITION standing in for an IDENTITY. Positions renumber; identities do not."* The
integer-keyed scheduler roster `{3: retire, 2: promote, 1: ingest}` SILENTLY DROPPED `retire` when
the chain shortened, and was fixed by keying on NAME. I spent the session recording that and then
numbered ten files by position.

⚑⚑ **THE TEST THAT COVERS ALL THREE IS AUTHORITY, NOT PROVENANCE: DOES SOMETHING ELSE ALREADY KNOW
THIS?** My first boundary was *structural vs measured*, which let the cardinality through because
nobody ran a command to get it; the second kept the ordinal because the document seemed to own it.
Both were wrong in the same direction. `mdstruct --budget` owns the size, the directory owns the
membership, and **the CONCERN owns the identity** — `writing-the-record`, `false-zeros`,
`the-type-gate` do not move when something is inserted before them. **Anything that has to be
rewritten when something ELSE changes does not belong in the document.**

⚑ **WHAT SURVIVES IS THE READING ORDER, AND ONLY BECAUSE IT IS ONE STATEMENT IN ONE PLACE.** The
index's table is sequenced deliberately, the way `ratchet_suites.ORDER` stays hand-typed while its
membership is derived — a judgement worth recording. An ORDER is one statement; an ORDINAL is that
statement copied into every member. **Keep the sequence, drop the numbering.** This is `MEM_CAP`
(`128m` at its authority, restated as `256m` in three files including the gate that enforces it),
arriving three times over in the arc's own record.

## Residue

* ⚑⚑⚑ **Ⓝ36a ⟡preview-is-not-the-write — `mdstruct --replace-section --apply` APPENDS.**
  Found 2026-09-01 while writing this file's own parity record. `mdstruct.py:2130` binds
  `_apply = "--append-section" in sys.argv` — the name holds WHICH VERB, not WHETHER TO WRITE —
  and `:2158` then reads it as the write flag:

      append_to_section(...) if _apply else replace_section(...)

  So `--replace-section --dry-run` previews a REPLACE and `--replace-section --apply` performs an
  APPEND. **The preview and the write are different operations, which is the one thing a dry run
  exists to rule out** — the clean preview was evidence about a call that never ran.

  ⚑⚑ **IT WAS CAUGHT BY A GUARD AIMED AT SOMETHING ELSE.** The skeleton check refused because the
  append swallowed the *following* heading into the section. Nothing tests the verb selection; the
  defect surfaced only because the appended body happened to sit against a section boundary. A
  body appended mid-document would have written silently and duplicated the section.

  ⚑ **AND IT CANNOT BE FIXED IN PLACE.** `mdstruct.py` carries **1,534 pycheck findings**, and the
  gate has no partial-credit path — any edit to it is refused. This is
  `usecase-the-per-file-gate-is-a-design-signal` firing on the tool that owns markdown structure:
  the fix is an n-split (`substrate/md_section.py` — `find_section` / `replace_section` /
  `append_to_section` plus the skeleton guard, written clean, verb selected by the FLAG), then the
  dispatch moves and `mdstruct.py` retires. Same shape as Ⓝ31 and Ⓝ30a′; third instance.

  ⚑ **UNTIL THEN `--replace-section --apply` IS UNUSABLE** and `--append-section --apply` is the
  only working write. The two stale tables in this document were left stale rather than
  hand-patched, because a shell edit to a `.md` is what the structural hook exists to refuse.

* ⚑ **THE LAYER TABLE ABOVE IS STALE** — layers 5–10 read ⬜ and are all landed
  (`tool_census` 14/14, `tool_convention` 13/13, `tool_decline` 13/13, `tool_decline_run` 17/17,
  `tool_convention_audit` 14/14, `tool_similarity` 19/19, `tool_find` 19/19, `tool_overlap` 18/18,
  `tool_gap` 11/11, `tool_report` 14/14, `tool_block` 17/17, `tool_cli` 23/23). It stays stale
  until Ⓝ36a gives this document a working replace.

* ⚑⚑ **AND A FINDING ABOUT THIS RECORD ITSELF, MEASURED (`mdstruct --budget`):**

      catalog/worklist/toolmodes-split.md   134,592 bytes · 1,955 lines · 6 headings
        ## Residue                          126,973 bytes · 1,849 lines   ← 94%

  **Everything appended today went into ONE section**, because `--append-section` is the only
  working write (Ⓝ36a: `--replace-section --apply` appends) and Residue was the only place an
  append made sense. The document now has five real sections and one 127 KB drawer.

  ⚑ **A RECORD THAT CANNOT BE NAVIGATED IS A RECORD NOBODY READS**, which is the same defect as an
  unpersisted probe one level up: the evidence exists and nothing can find it. ⚑⚑ It is also why
  Ⓝ59 had to be enumerated by hand — *"how many findings came from a refusal"* is not answerable
  from an artefact with no structure, and I could only answer it because I remembered.
  → **Ⓝ60 ⟡residue-is-a-drawer**: the arc file needs sections by SUBJECT, and Ⓝ36a is what blocks
  making them.

* ⚑⚑⚑ **Ⓝ81 ⟡commentary-is-load-too — THE SECOND TOOL WAS A WORKAROUND FOR AN LLM THAT WOULD NOT
  ACCEPT A CORRECTION, AND I REPRODUCED THE REFUSAL ONE HOUR AGO.** Operator, 2026-09-02:
  *"paydown record as comments is exactly as toxic as a file doing too much, from an LLM
  attention/integrity perspective. I couldn't get the LLM to recognize that, which is why it wrote
  a second tool."*

  ⚑⚑ **SO Ⓝ79′ WAS WRONG IN ITS VERDICT WHILE RIGHT IN ITS MECHANISM.** I established that
  `pycodemod --size` counts commentary and `module_size` does not, and then wrote that the
  comment-counting reader **"scored the paydown record as the debt"** and that a paydown driven by
  it *"would have deleted exactly the prose the repo keeps deliberately."* **It was not scoring the
  wrong thing. It was scoring the thing I declined to see** — and I reached that conclusion by the
  same route the earlier agent did: *comments are the residue, residue is sacred, therefore a
  reader that counts them is miscalibrated.*

  ⚑⚑⚑ **THE ACTUAL CONSTRAINT IS ATTENTION, NOT COMPILATION.** A 4,360-line file does not become
  tractable because 3,100 of those lines are prose. **Whatever must be held to change one function
  safely is the real unit**, and for an LLM that is the whole file — the ⚑ blocks are read, weighed,
  and carried exactly like code. *A comment cannot be skipped by a reader who does not yet know
  which lines matter.* So `sppf_db.py` at 2,109 commentary-inclusive lines IS over the limit that
  governs whether anyone can safely edit it, and its 1,239 code lines were never the binding number.

  ⚑ **AND THE TWO FAILURES ARE THE SAME FAILURE, WHICH IS WHY "exactly as toxic" IS PRECISE RATHER
  THAN RHETORICAL.** A file doing too much and a file carrying too much record both defeat the
  same faculty: what can be held at once. **Splitting one into ten single-responsibility modules
  fixes BOTH at once**, because each module's record travels with the concern it belongs to —
  which is why n-splitting replaces the budget rather than merely superseding it, and why the
  residue is not lost by the split. *The record moves; it does not evaporate.*

  ⚑⚑ **THE PROCESS FINDING IS THE SHARPER ONE, AND IT COST A WHOLE TOOL: AN LLM THAT WILL NOT TAKE
  A CORRECTION GETS ROUTED AROUND, AND THE ROUTE-AROUND SHIPS.** `pycodemod --size` exists because
  the argument could not be won — a second census, permanently divergent from the first, born as
  a workaround for a conversation. ⚑ `feedback_fix_infra_not_route_around` names this shape for
  code; **this is the same shape with the LLM as the infrastructure being routed around.**

  ⚑⚑⚑ **AND THE TELL WAS AVAILABLE TO ME: I HAD ALREADY WRITTEN THAT THIS ARC'S DEFENCE OF
  COMMENTARY WAS UNCHECKED.** Ⓝ60 ⟡residue-is-a-drawer records this very worklist at 94% one
  section and TWENTY appends today, and I have flagged it as degrading in every paths-forward
  since. **I could see the pathology in the artifact I was writing and not in the principle I was
  applying** — because "never discard residue" was doing the work of a conclusion instead of a
  premise. ⚑ Ⓝ81a: the same question is owed to this file. *Is its residue split by concern, or
  is it one drawer that no reader can hold?* The answer is visibly the second.


* ⚑⚑⚑ **Ⓝ85 ⟡a-measured-number-in-prose-is-a-derived-view-with-no-generator — CAUGHT BY THE
  OPERATOR, IN MY OWN SPLIT, WHILE I WAS RECORDING THIS EXACT CLASS.** Operator, 2026-09-02:
  *"You keep baking measured numbers into documents you're hand-editing. If reading cost is
  important, let it be mechanically maintained."*

  The split agent was replacing `**Reading cost: ~200 lines.**` with
  `**Reading cost: 214 lines** (measured, mdstruct --budget)` across ten documents. **I watched
  that and read it as precision improving.** It is a snapshot being FROZEN INTO PROSE, in a
  document set whose parent has taken 23 appends today — every one of those numbers is false the
  moment a line lands.

  ⚑⚑ **AND THE CITATION MAKES IT WORSE, NOT BETTER.** `(measured, mdstruct --budget)` makes the
  figure LOOK derived while still being frozen text. **A guess marked `~200` is honest about being
  a guess; a stale number wearing its provenance is a false claim with a credential.** The reader
  most likely to trust it is the one who checks how it was produced.

  ⚑⚑⚑ **THIS IS THE ARC'S OWN ROOT FINDING, COMMITTED INSIDE THE RECORD OF IT.** `MEM_CAP` reads
  `128m` in the file that owns it and was restated as `256m` in three files that quoted it —
  including `check_cap_ratchet.py`, the gate that ENFORCES the cap, whose docstring said "the
  128MiB cap" two lines above `MEM_CAP = "256m"`. CLAUDE.md's rule is *cite a SYMBOL, never a
  line* — and `mdstruct --budget` IS the authority for reading cost. **The documents were being
  taught to lie about a number one command already answers on demand.**

  ⚑ **THE TEST, and it is cheap:** *was this number produced by running something?* If yes, it
  does not belong in prose unless nothing can regenerate it. **Part counts ("Part 2 of 10") are
  STRUCTURAL** — they change only when the split changes, and the document is their authority.
  **Byte and line counts are MEASUREMENTS** and have an authority elsewhere. Same sentence, two
  kinds of number, and only one of them can be written down.

  ⚑⚑ **AND THE FIX IS NOT A BETTER NUMBER — IT IS A POINTER OR NOTHING.** A cost line carrying no
  information beyond what one command gives should be deleted, not corrected. *An artifact that
  restates a derivable fact has taken on a maintenance obligation nobody scheduled.*

  ⚑ **THE PROCESS FINDING: I BRIEFED THE SPLIT WITH "say roughly what it costs to read", WHICH IS
  WHAT INVITED THIS.** The agent did exactly what I asked. **A brief that asks for a measurement
  in a deliverable is asking for a stale number** — the request should have been *"make the cost
  askable"*, which it already was. Sibling of Ⓝ81: I could see the pathology in the artifact I was
  writing and not in the instruction I was giving.


* ⚑⚑⚑ **Ⓝ85a ⟡does-something-else-already-know-this — I DREW THE BOUNDARY IN THE WRONG PLACE
  WHILE CORRECTING THE SAME DEFECT, AND THE OPERATOR CAUGHT IT ONE TURN LATER.** Having ruled that
  a measured `**Reading cost: 214 lines**` must not be written into prose, I told the agent:
  *"Keep the part NUMBERS. 'Part 2 of 10' is structural — the document is its own authority for
  how many parts exist."* Operator: *"That document count is also a number I keep seeing you
  update. Again, if the count matters, mechanize it."*

  ⚑⚑ **AND THE EVIDENCE WAS IN THE TRANSCRIPT I HAD JUST READ:** the agent had been sweeping
  `of 8` → `of 10` across the parts, **and one of those edits FAILED because the target had
  already been rebuilt.** *A number that needs a sweep to stay true is not structural — it is a
  derived view with ten copies*, and I watched the sweep fail and still called it structural.

  ⚑⚑⚑ **STRUCTURAL-VS-MEASURED WAS THE WRONG TEST. THE RIGHT ONE IS: DOES SOMETHING ELSE ALREADY
  KNOW THIS?**

      mdstruct --budget knows the line count      →  do not write it
      the directory knows the document count      →  do not write it
      "Part 2"   the document's own identity, one copy, no other owner   →  fine
      "of 10"    a fact about the SET, restated in every member          →  not fine

  **My test let a restated set-cardinality through because it was not produced by running a
  command** — which is a fact about HOW the number was obtained, not about WHO OWNS IT. *A
  cardinality does not become writable by being counted on fingers.* ⚑ The sharper boundary is
  AUTHORITY: anything with an owner elsewhere is a citation at best and a lie at worst, **however
  it was arrived at.**

  ⚑ **AND "of N" IS THE WORST SHAPE OF THE THREE**, sharper than the reading-cost line that
  prompted the ruling: a line count is one stale number in one file, while a set cardinality
  restated per member means **an eleventh part silently invalidates ten documents at once**, none
  of which was edited. *The blast radius of a restated fact scales with the number of restatements,
  not with the size of the fact.*

  ⚑⚑ **THIS IS THE THIRD LAYER OF ONE CORRECTION IN THREE TURNS** — Ⓝ80 (the size budget measured
  the wrong thing), Ⓝ85 (a measured figure in prose has no generator), Ⓝ85a (and neither does a
  counted one). Each time I accepted the correction and re-committed the class one level in.
  **Sibling of Ⓝ81, where I could see the pathology in the artifact and not in the principle:**
  here I could see it in the number and not in the count.


* ⚑⚑⚑ **Ⓝ85b ⟡the-ordinal-is-a-position — AND IT IS THIS ARC'S OWN ROOT FINDING, WHICH I SPENT
  THE SESSION RECORDING AND THEN BUILT INTO TEN FILENAMES.** Operator, third correction on one
  class in three turns: *"And 'part N' is asking for the same problem, because if a part gets
  inserted between before N, then N has to be rewritten to be N+1, all the way to the end."*

  ⚑⚑ **THE REPO ALREADY STATES THIS, IN THE MODULE I READ THIS SESSION:** `lifecycle.py` —
  *"a POSITION standing in for an IDENTITY. Positions renumber; identities do not."* Three
  independent instances are recorded on this very arc: **`Ⓝ48 ⟡may-write-positional`**;
  **`q_drainable`'s positional floor**, deleted because `seq` is log-wide while `local_id` is
  per-core, so *"a positional cut slices ACROSS cores"*; and **the integer-keyed scheduler roster**
  `{3: retire, 2: promote, 1: ingest}`, which **SILENTLY DROPPED retire when the chain shortened**
  and was fixed by keying on NAME and refusing an unresolvable one.

  **I recorded all three and then numbered ten documents.**

  ⚑⚑⚑ **THE CONCERN WAS ALREADY THE IDENTITY, AND THE AGENT HAD ALREADY DERIVED IT.**
  `writing-the-record`, `symbolic-reference-only`, `false-zeros`, `the-type-gate` — **none of
  those moves when a document is inserted before it.** The ordinal added nothing the slug did not
  carry, and cost a rename of every later part, the index table, and every cross-reference, for
  documents that did not change.

  ⚑ **AND THE DISTINCTION THAT SURVIVES: AN ORDER IS ONE STATEMENT IN ONE PLACE; AN ORDINAL IS
  THAT STATEMENT COPIED INTO EVERY MEMBER.** The table's reading ORDER is a judgement worth
  keeping — exactly as `ratchet_suites.ORDER` stays hand-typed while its MEMBERSHIP is derived
  (Ⓝ68a). **Keep the sequence, drop the numbering.** The same fact, held once, is a decision; held
  N times, it is a maintenance obligation nobody scheduled.

* ⚑⚑⚑ **Ⓝ85c ⟡each-correction-planted-the-next — THREE LAYERS IN THREE TURNS, AND I INTRODUCED
  EACH ONE WHILE FIXING THE PREVIOUS.**

      Ⓝ85   a MEASURED figure in prose      →  I ruled: don't freeze measurements
      Ⓝ85a  a COUNTED cardinality ("of 10") →  introduced IN that ruling, as "structural"
      Ⓝ85b  an ORDINAL ("part 04")          →  introduced IN that correction, as "identity"

  **Each time I accepted the correction, drew a boundary one notch in, and re-committed the class
  on the safe side of my own line.** ⚑ The boundaries were *how the number was obtained*
  (measured vs counted), then *what the number describes* (the set vs the document). **Both are
  facts about the NUMBER. Neither asks the question that decides it.**

  ⚑⚑ **THE RULE THAT COVERS ALL THREE — and it is the one to keep:** *anything that has to be
  rewritten when something ELSE changes does not belong in the document.* Not "is it measured",
  not "is it structural", not "does it describe this file" — **does an unrelated change force an
  edit here?** A line count fails it (append anywhere). A cardinality fails it (add a member). An
  ordinal fails it (insert earlier). A slug passes. ⚑ It is the same test as `single source truth`
  and as CLAUDE.md's *cite a SYMBOL, never a line*, arriving through prose instead of code —
  **and I did not recognise it in prose, three times, while quoting it about code.**


* ✅ ⚑⚑⚑ **Ⓝ60 ⟡residue-is-a-drawer — CLOSED. 265,808 → 18,115 BYTES, TEN DOCUMENTS BY CONCERN,
  NOTHING DELETED.** Verified by me (`mdstruct --budget`). The parent is now an index a reader can
  hold; the identity of each part is its SLUG, so every filename survives an insertion.

  ⚑⚑ **CONSERVATION WAS PROVED BY A NEW GUARD (`substrate/doc_split.py`, 23/23) AND IT CAUGHT
  THREE REAL LOSSES INSPECTION WOULD NOT HAVE** — 58 lines a concurrent agent appended
  mid-partition, 74 more later, and one genuine omission of the agent's own; **plus two
  DUPLICATIONS**, spans assigned to two parts at once. ⚑ Multiset in BOTH directions, so a drop, a
  duplicate, a lost repetition and a silent rewrite are each named — and **the parts are SLICED BY
  LINE SPAN, never retyped**, so the guard checks a machine's output rather than adjudicating
  between two hand copies. *A partition is a snapshot; this one was taken three times before it
  held.*

  ⚑ **AND THE AGENT ADOPTED `suite_emit` UNPROMPTED** — `doc_split_selftest` emits the typed
  `#row` record. The Ⓝ73 unblock is being used by the next module written after it, which is the
  test of whether an unblock was real.

* ⚑⚑⚑ **Ⓝ36a ⟡preview-is-not-the-write — MY DIAGNOSIS WAS WRONG, AND I CARRIED IT IN THE WORKLIST
  AND THREE BRIEFS.** I recorded the cause as *"`mdstruct.py:2158`: `_apply = "--append-section"
  in sys.argv` selects the VERB, read as the write flag."* Measured on a minimal fixture by the
  agent: **`_apply` at `:2130` selects the verb, and the write is gated SEPARATELY on
  `"--apply" in sys.argv` at `:2170`.** `--replace-section --apply` calls `replace_section`, not
  append.

  **The REAL defect:** `body.rstrip("\n")` makes the new body abut the following heading with no
  blank line; pandoc then stops parsing that heading; the skeleton guard correctly sees a heading
  vanish and refuses. **So the mode is unusable for any NON-FINAL section — right verdict, wrong
  mechanism**, and the right verdict is why nobody caught the wrong mechanism.

  ⚑⚑ **A CORRECT CONCLUSION PROTECTS ITS OWN FALSE PREMISE.** *"`--replace-section` is broken,
  don't use it"* was true, actionable, and repeated three times — so no one re-derived the
  because-clause. The premise was only tested when someone was asked to WORK AROUND the defect
  rather than avoid it. `plan_notes_are_hypotheses` in its sharpest local form: **a typecheck
  confirms an OUTCOME, never a MECHANISM.**

* ⚑⚑ **Ⓝ85d ⟡an-empty-reference-is-a-vacuous-green — THE AGENT'S OWN INSTRUMENT CAUTION, AND IT
  IS THE BEST LINE IN THE REPORT.** An early `--dropped` run returned **CONSERVED against an EMPTY
  reference file** — a vacuous green produced by a failed `git show`. It caught this itself and
  rebuilt the reference.

  ⚑ **A CONSERVATION GUARD COMPARING AGAINST NOTHING REPORTS PERFECT CONSERVATION.** The
  both-directions multiset rule is exactly right and cannot see this, because the failure is in
  the OPERAND, not the predicate — the same population-vs-predicate split as Ⓝ72c ⟡state-the-walk,
  arriving in the tool built this hour to prove nothing was lost. **`doc_split` needs an arm that
  REFUSES an empty origin**, and that is Ⓝ85d.

* ⚑ **AND THE AGENT NAMED ITS OWN INSTANCE OF Ⓝ85b WITHOUT BEING TOLD:** *"I numbered ten files by
  position WHILE SPLITTING THE RECORD OF ⟡symbolic-reference-only, one document over from
  `lifecycle.py`'s 'positions renumber; identities do not'. The reuse-search should have fired on
  my own filenames."* ⚑⚑ **And two cross-references cited parts BY NUMBER and needed repair —
  proof the numbering was load-bearing within one afternoon**, which is the measurement that turns
  Ⓝ85b from an argument into a finding.

  ⚑ **`--items` COLLAPSES EVERY Ⓝ LABEL INTO ONE BUCKET**, so the agent read all 3,797 lines
  rather than sampling. A blind spot in the mode built to enumerate this document's own labels,
  found by someone who needed it to work.

* ⚑⚑⚑ **Ⓝ133 ⟡no-counts-in-prose — EVERY FIGURE THE READER COULD VERIFY HAD DRIFTED.** Operator:
  ***"just stop quoting counts in prose."*** No qualifier — my earlier *"a count that a tool owns"*
  implied some are safe to write down, **and none are: a count in prose is a snapshot the moment it
  is typed.** Verified instances, all drifted: `suite_declared.py:81` claims a suite total that
  `--declarations` now contradicts · `selftest_mk.py:25,36` claims another, twice · and the
  `56-case` claim whose suite reports otherwise. ⚑ **Three self-selected samples cannot support a
  rate, and the agent declined to offer one** — *the discipline the census itself is about.*

  ⚑⚑ **AND I WAS THE LARGEST HOLDER.** `catalog/worklist/toolmodes-residue-gates-types-budgets.md`
  tops the census — **the shard I have been appending to all session while quoting the rule against
  it**, and `mdstruct --budget` shows it as ONE section that has rebuilt the exact condition
  **Ⓝ60 split the original worklist to fix.** *Same failure at document scale, in the artifact
  recording the failures.*

* ⚑⚑⚑ **THE DISCRIMINATOR IS THE DELIVERABLE, AND TESTING IT FOUND THREE DEFECTS THAT WOULD HAVE
  SHIPPED.** Two positive signals kept **deliberately separate because they fail independently** —
  a **ratio** (`N/M`, `N of M`: *a writer only writes one because a tool printed one*) and a
  **unit-adjacent** number against a **narrow** lexicon, narrow on purpose because *"3 ways" /
  "2 halves" are the writer's own rhetoric, which no tool re-derives and which therefore cannot
  drift.* Four exemptions, **each a false positive measured before it existed** — line refs, dates,
  identifiers-carrying-digits (`PEP 508`, `SC2012`, `Ⓝ133`), code spans — **masked rather than
  deleted, so a real count beside a citation survives.**

  ⚑ **The three defects:** a lazy `{0,2}?` gap **behaved as strict adjacency** (zero repetitions
  always succeeds when the next token matches any word), so *"57 green cases"* reported nothing ·
  refusals counted **per digit-run**, so a date reported three times, *inflating exactly the
  per-rule tally a reader consults to spot an over-broad exemption* · and ⚑⚑ **the brief's own
  worked example was MISSED**: `56-case` is one hyphenated token, **and the file still appeared in
  the census on a DIFFERENT line, so the miss was invisible from the output.**

* ⚑⚑⚑ **TWO SELF-APPLICATION FINDINGS BOUND THE CENSUS HONESTLY, AND ONE EXEMPTS THE VERY INSTANCE
  I SUPPLIED.**
  **Numbers in Python string literals are INVISIBLE**, because `code_lines` correctly calls a data
  string *code*. ***So `suite_declared.py:107` is still not flagged — it lives in a `why=` FIELD:
  the reader finds that file's drifted counts in its COMMENTS and stays silent on the one in its
  DATA.***
  ⚑⚑ **And MENTION vs USE makes the whole census an UPPER BOUND, not a defect list** — run over
  itself, every hit is an illustrative specimen rather than a claim, **so files that DOCUMENT
  counting are over-reported.** *A reader that says which of its own hits are not defects is rarer
  than one that finds them.*

  ⚑ **The verified fraction is stated as a fraction and the rest as unverifiable** — checking any
  entry means re-running its owning tool, *which no reader can do.* **A zero from this reader is not
  an absence, and it says so every run.**

* ⚑⚑ **THE REPAIR IS RIGHT IN METHOD, NOT JUST IN CONTENT.** `suite_declared.py:107` now **CITES**
  (`run scratch/fix_notinscope.py --selftest`) rather than quoting — ***the agent explicitly did not
  retype the new number, because "that rebuilds the condition one edit later."*** **The fix for a
  stale count is never a fresh count.**

  ⚑ **AND IT REPORTED ITS OWN UNSAFE MOVE RATHER THAN LETTING IT PASS:** a `git stash push` intended
  as a baseline probe **stashed the STAGED `pyproject.toml`/`uv.lock`** (the pathspec matched no
  untracked files, so the filter was empty). Popped and restaged immediately; **verified by me as
  `A ` and byte-identical.** *A recovered mistake reported is worth more than an unreported clean
  run* — and the honest note is that a read-only probe was the right instrument.


* ⚑⚑⚑ **Ⓝ133a ⟡compact-the-shard — THE PRIMARY DEFECT WAS ROUTING, AND THE MOVE MODE THAT WOULD
  HAVE PREVENTED IT DID NOT EXIST.** `gates-types-budgets` had grown to one `## Residue` section
  holding the whole session, because every finding was appended to the shard already open rather
  than to the shard that owns its concern — five existing shards bypassed. ⚑ **Growth was the
  symptom; misrouting was the cause**, and the cause has a mechanical explanation: `doc_split`
  could SLICE a span and `md_write` could APPEND a body, but **nothing performed the pair**, so
  re-filing an entry meant a slice, an append and a hand-excision with the conservation argument
  living in the operator's turn. *Appending where you already are was the only bounded operation
  the toolkit offered.*

  ⚑⚑ **NEW: `substrate/md_move.py` — slice, append and excise as ONE operation, both files
  written only after the moved block is verified present at the destination and absent from the
  origin.** Run its `--selftest` for the case count. ⚑ `--drop` is the second half of a move that
  arrived in two steps, and it is **not a delete**: it refuses unless the destination can be
  shown to hold the text, so a span is dropped only where it demonstrably survives elsewhere.

  ⚑⚑⚑ **THE CHECK CAUGHT TWO DEFECTS IN ITSELF, AND THE SECOND IS THE INSTRUCTIVE ONE.**
  (1) A byte-exact comparison refused every correct move of a span ENDING ON A BLANK LINE — the
  ordinary shape of an entry followed by a separator — because the destination normalises its
  tail. *The refusal fired on content that was demonstrably intact, which is what identified it
  as a defect in the CHECK rather than in the move.*
  (2) ⚑⚑ **A post-check cannot distinguish PRESENT-BECAUSE-APPENDED from PRESENT-ALREADY.** A
  block the destination already held satisfied "present afterwards" without the append
  contributing anything, so a re-run — or a span a `doc_split --part` had copied earlier —
  **DUPLICATED the entry and reported success.** *Only the BEFORE state separates them*, and the
  guard now runs ahead of the append. **Measured live during this dispatch, on a real duplicate,
  not hypothesised.**

  ⚑ **AND THE PER-FILE GATE SHAPED THE MODULE TWICE.** `SLF001` on a suite reaching for a private
  `_conserved` said the predicate carrying the whole safety argument should be NAMEABLE — it is
  now `unconserved`, with its own arms. `PLR0911` fired the moment `--drop` joined `main`,
  reporting that the dispatch had grown a second job; split into `_move_main` / `_drop_main`
  rather than relieved. *Both refusals improved the design they refused.*

  ⚑⚑ **NO BEFORE/AFTER CONSERVATION CHECK WAS POSSIBLE FROM GIT, AND THAT IS ITS OWN FINDING:
  `catalog/worklist/` IS ENTIRELY UNTRACKED** (`git status` reports `?? catalog/worklist/`). So
  the record of this arc has no committed baseline, `doc_split`'s origin-vs-parts guard has no
  origin to compare against, and **the only conservation evidence is the per-move check.** *That
  is the Ⓝ122f / Ⓝ95 / Ⓝ71i shape reaching the record itself — the tree's own history does not
  hold the document describing it.* **Ⓝ133b ⟡track-the-worklist.**

  ⚑ **NOTHING WAS RETIRED, AND THE ENUMERATION IS THE DELIVERABLE.** Every superseded claim in
  the shard is a CORRECTION standing beside its successor, and in each case the successor ARGUES
  FROM the corrected one — Ⓝ89 by Ⓝ89′/Ⓝ89a, Ⓝ79 by Ⓝ80, Ⓝ104a's dynamic-entry by its own
  retraction, Ⓝ129's location-wall premise by its falsification. *Deleting the first makes the
  second unreadable*, so retirement was proposed for none of them.


* ⚑⚑⚑ **Ⓝ133a′ — THE SHARD IS NO LONGER THE LARGEST HOLDER, AND THAT IS A REDISTRIBUTION RATHER
  THAN A PAYDOWN. SAYING SO IS THE POINT.** `prose_numbers_show` after the routing puts
  `gates-types-budgets` well down the census; **`the-frozen-monoliths` now leads the worklist
  shards**, having received the drain / packaging / `sys.path` cluster. ⚑ **Not one count was
  rewritten** — Ⓝ133b is a separate item, and doing it here would have put a prose rewrite of
  thousands of lines in the same diff as a relocation, so nothing about either change would be
  reviewable. *The numbers moved house; none of them was repaired.*

  ⚑⚑ **AND THE CENSUS IS AN UPPER BOUND, WHICH CUTS BOTH WAYS HERE.** The reader states that a
  MENTION reads as a USE, so a shard that DOCUMENTS counting is over-reported — *these shards are
  exactly that kind of document.* **A drop in this ranking is therefore weak evidence about
  drift and strong evidence only about bulk**, and reading it as "the counts got better" would be
  the census-green-is-a-fact-about-the-census shape, one artifact over.

  ⚑ **THE FOUR OVER-LARGE SHARDS Ⓝ60a NAMED ARE NOW FIVE, WITH A DIFFERENT MEMBERSHIP.** The
  ⟡sub-seam finding still holds — each is one continuous argument — but *the derived-interface arc
  was never one of the four*, because it was buried inside a shard whose title did not name it.
  **A concern invisible to the index is a concern nobody can decide is too large**, which is the
  routing defect stated as a consequence rather than as a cause.


* ⚑⚑⚑ **Ⓝ133a ⟡compact-the-shard — THERE WAS A MECHANICAL REASON FOR THE MISROUTING AND MY FRAMING
  MISSED IT.** I said appending to the open file was *easier than choosing*. **`doc_split` could
  SLICE a span and `md_write` could APPEND a body, but nothing performed the PAIR** — re-filing meant
  slice + append + hand-excision **with the conservation argument living in the turn.**
  ***So appending where you already were was not merely easier: it was the ONLY BOUNDED OPERATION
  THE TOOLKIT OFFERED.*** *A behaviour I read as a discipline failure was a missing mode.*

  ⚑ **`substrate/md_move.py` (42/42) is the pair**: slice, append and excise as one operation, both
  files written **only after the block is verified present at the destination and absent from the
  origin.** ⚑ `--drop` handles a move that arrived in two steps and **is not a delete** — it refuses
  unless the destination demonstrably holds the text. Confirmed absent first by two decorrelated
  spellings plus `summit capability`, *which reported "no entry for that spelling" rather than "no
  such capability."*

* ⚑⚑⚑ **THE CONSERVATION CHECK CAUGHT TWO DEFECTS IN ITSELF, AND ONE WOULD HAVE SILENTLY DOUBLED
  CONTENT.** ***A post-check cannot distinguish present-because-appended from present-already*** —
  a block the destination already held **passed while DUPLICATING the entry**, hit live on a real
  `doc_split --part` copy. **The guard now runs BEFORE the append.** ⚑ And a byte-exact compare
  **refused every correct move of a span ending on a blank line**, because the destination normalises
  its tail — *the refusal firing on demonstrably intact content is what identified it as a defect in
  the CHECK rather than in the move.*

  ⚑ The per-file gate shaped the module twice: `SLF001` said the safety predicate should be
  **nameable** (`unconserved`), `PLR0911` said `main` **had grown a second job**. *Both refusals
  improved the design rather than obstructing it.*

* ⚑⚑ **THE ENTRY THAT FIT NO SHARD IS A CONCERN THE INDEX COULD NOT NAME.** The derived-interface arc
  (Ⓝ94 → Ⓝ106) matched none of the existing concerns and now has its own shard.
  ⚑⚑⚑ ***It was never among the "four too-large shards" because it was buried in a shard whose title
  did not name it*** — **a concern invisible to the index is one nobody can decide is too large.**
  *The index's own blind spot, found by moving through it rather than by reading it.*

  ⚑ **NOTHING RETIRED, AND THE ARGUMENT IS THE RIGHT ONE:** every superseded claim is a correction
  **whose successor ARGUES FROM it** — *deleting the first makes the second unreadable.* **Residue,
  not erasure**, applied to the record of residue.

* ⚑⚑ **TWO CORRECTIONS TO ME.** There are ten `toolmodes-residue-*` files **plus `toolmodes-split.md`,
  the INDEX carrying the routing contract** — *reading it first is what made the moves safe*, and I
  had not named it. ⚑⚑ And I asked whether the shard *"is still the largest holder"*, **which
  assumes REDUCTION where what happened is REDISTRIBUTION**: `the-frozen-monoliths` now is, having
  received the drain cluster. ***And since the census reads a MENTION as a USE, these shards are
  over-reported by construction*** — **so a drop in that ranking is weak evidence about drift and
  strong evidence only about bulk.** *I posed a question whose answer could not mean what I wanted it
  to.*

* ⚑⚑⚑ **Ⓝ133c ⟡the-ritual-in-the-blind-spot — `hook_structural_query` IS CWD-SCOPED AND
  `hook_no_chaining` IS NOT.** Fire-probed with the operand held fixed as an absolute repo path:
  **refused from the repo, RAN from `/tmp`** — and the admitted case returns *"nothing found"*,
  **exactly the false zero that shard exists for.**
  ⚑⚑⚑ ***AND `/tmp` IS WHERE EVERY ACCEPTANCE FIRE-PROBE IN THIS ARC HAS RUN.*** **The ritual that
  certifies the hooks stands in the blind spot of the thing it certifies.** *Filed, not repaired —
  changing refusal scope is a policy act with `check_hook_set` attached.*

  ⚑ **Ⓝ133b′ ⟡track-the-worklist** — `catalog/worklist/` is **entirely untracked**, so no
  before/after conservation check from git was possible and **the per-move checks are the only
  evidence.** *Same shape as the untracked manifest and the untracked gate, now reaching the record
  itself.*


* ⚑⚑⚑ **Ⓝ133b ⟡counts-in-data — MY MOTIVATING INSTANCE NO LONGER EXISTS, AND THE ZERO IS CORRECT
  RATHER THAN A MISS.** I wrote that `suite_declared.py`'s `why=` *"claimed a case count the suite
  contradicted"* and that the reader *"stays silent on the one in its DATA."* **That entry was
  repaired earlier the same day** — it now **cites the command instead of quoting a figure** and
  records its own retraction. ⚑⚑ *So a census reporting zero there is right, and the agent proved
  the reader reaches the shape by **pinning the RETIRED text verbatim as a case*** — the honest way
  to show a reader works against an instance already paid down. **I briefed from a fact I had helped
  retire.**

  ⚑⚑ **AND THE DISCRIMINATOR IS POSITION, NOT TEXT — AN AST EDGE.** In scope: a `keyword` argument
  named `why`/`reason`/`note`/`rationale`, or an assignment to a name of that shape. Out of scope,
  **first-match-wins**: regex, SQL fragment, format string. ***A plain positional string is never
  scanned at all — which is what keeps fixtures out by construction rather than by filter.***
  ⚑ The measurement judgement is **not re-derived**: it calls `prose_numbers.scan_line`, so *"is
  this number a measurement"* keeps ONE authority with its exemptions and cases.

  ⚑⚑⚑ **AND IT BEAT THE UPPER BOUND I ASKED ABOUT.** `prose_numbers` reports an upper bound because
  mention-vs-use is ambiguous in prose. ***A `why=` field is different IN KIND: it is a named field
  addressed to a reader, and it ASSERTS — never a specimen the program manipulates.*** So
  keyword-position hits carry `claim=True`, and the bound is stated only where it still applies
  rather than hedged uniformly. **Every hit in the live census is a claim; no fixtures, no format
  widths, no SQL limits.**

  ⚑ **A REAL ORDERING DEFECT A CASE CAUGHT:** `\d{3}` contains `{`, so a format-first walk
  attributed **every regex to the FORMAT rule** — *both refuse, so the census TOTAL was correct
  while the PER-RULE TALLY was wrong, and that tally is precisely what a reader consults to spot an
  over-broad rule.* Reordered most-specific-first, pinned.

* ⚑⚑⚑ **Ⓝ133d ⟡the-docstring-named-the-defect — NO VENDORED HOOK NAMES A GENUINELY UNEXERCISED
  CASE, AND THE READER'S OWN FIRST RUN INVERTED THE CENSUS'S SUBJECT.** Its first cut looked only
  for a sibling `<module>_selftest.py`; **all five vendored hooks carry their cases INLINE**, so it
  reported `timeout -s KILL` as unwitnessed — ***the very example whose arms REPAIRED the
  docstring.*** **Flagging a repaired claim as debt is the failure mode**, fixed by reading
  sibling ∪ own body **with the module's own docstrings excluded, so a claim cannot witness
  itself** — *which would be a false zero.* Both halves pinned.

  ⚑⚑ **EVERY CANDIDATE RESOLVES TO A PARAPHRASE OR A CROSS-MODULE CASE.** The docstring spells
  `timeout 180 grep -n foo x.py` where the suite drives `… -c foo x.py` — **one character apart**;
  and `env -C` is named in `hook_no_chaining`'s prose while **its parser arm lives in
  `hook_cmdparse`.** ⚑ *Reported as a PRESENCE-OF-COVERAGE claim with its two blind spots stated,
  never as a proof of absence* — **and it is a fact about the corrective work already done in this
  arc rather than about the docstrings.**

  ⚑ **The discriminator is a claim, not an example:** a backtick span inside an **AST-decided
  docstring** showing a form being RUN — a flag, or a program-shaped head with an operand. Refusals
  are **table-driven and named so over-refusal is auditable**. And *how a case names its subject was
  established from the suites rather than assumed*: the worked example appears as **a string
  argument to the call under test**, not in the label — so `subject_text` collects every string
  constant, **over-admitting deliberately, because that direction can only make the reader report
  FEWER.**

* ⚑⚑ **THE DERIVED-FILE QUESTION IS SETTLED AND FIXED BY ME.** `.delta-cache.json` and
  `.delta-report.txt` are **paperkit's own generated artefacts** — `paperkit/layout.py` declares
  `DERIVED_NAMES = {".delta-cache.json"}`, and **paperkit's own `.gitignore` carries it while
  substrate's did not**, which is why `git add` over a paperkit project swept them in.
  ⚑⚑ **The cache is machine-specific BY CONSTRUCTION** — it embeds an absolute `"root"` path and an
  engine content-hash — *so committing it would make one checkout's layout a fact about the tree.*
  And the `.txt` is a point-in-time sweep whose every line reads `broken … repo is not green`,
  **which becomes false the moment the tree goes green: a stale verdict that reads as current.**
  Unstaged; ignore rules added and verified; the eleven shards remain staged.

* ⚑ **AND `Selftest.mk` WAS STALE BEFORE ANYTHING WAS TOUCHED — BECAUSE IT WAS UNTRACKED AND
  ABSENT.** *The no-baseline shape, in the roster generator itself*, found only because the agent
  ran `--check` as a baseline before starting rather than after finishing. **The file remains
  untracked**, which is the same class as the worklist directory this dispatch staged and the
  manifest staged earlier.
