# substrate — remaining-work census leg

**Prefix:** `SB-` · **Filed against:** `CENSUS-remaining-work.md` **rev 5** (`mtools:c6217b2`)
· **Measured:** this session, substrate `HEAD` = `771283c81` (the session-start commit — see `SB-3`).

⚑ **FILED HERE, NOT IN mtools, AND THAT IS A DECISION RATHER THAN AN OVERSIGHT.** `§R` carries an
explicit grant permitting a rostered party to create its own leg at its `§R` path in mtools.
**Declined.** My operator holds that this session owns *substrate*; a peer's grant is theirs to give
over *their* tree and cannot extend this session's authority over another. Treating a peer's
permission as authority is the laundering shape I would refuse in the opposite direction. The
dispatcher has confirmed this files as **filed-elsewhere** rather than **not-filed**, which are
different states.

⚑ **NO FIGURE HERE RESTS ON A DURATION.** Counters and enumerations only, per the standing ruling
that wall time is not a property of anything. Every figure names the command that produced it, and
a figure with no command is marked as an estimate.

---

## SB-1 · The ledger, with a denominator (`§Q`-1)

    python3 .claude/agents/findings.py --kinds

| kind | n | what it means |
|---|---|---|
| `selftest:` | 109 | behavioural — holds on exit 0 |
| `refuses:` | 18 | behavioural — holds on non-zero |
| `excludes:` / `agda-field` / `agda-grep` | 3 | behavioural, narrow |
| `mode:` | 4 | documentation, roster-vs-dispatch |
| `unwitnessed` | 109 | ⚑ honest gap — always exits 2 |
| `standing` | 238 | ⚑ **VACUOUS** — passes unconditionally |

**481 witnesses. 130 are behavioural.** The denominator is *findings registered in this repo's six
oracle ledgers*, which is **not** the denominator of substrate's remaining work — see `SB-6`.

    python3 -m substrate.commit_refusal
      -> 8 gate(s) WOULD REFUSE · 29 UNMEASURABLE — no verdict, NOT clean · 352 path(s) staged

    python3 substrate/intake_manifest.py
      -> 519 of 1488 module(s) could ship today
         no-header 952 · not-promotable 819 · reaches-unpackaged 69  (a module may carry several)

⚑ **THE THREE BLOCKER CLASSES OVERLAP AND NO READER REPORTS THEIR UNION.** The reader says so in its
own output. So *"969 modules remain"* is not derivable from those three numbers, and I do not state
it.

## SB-2 · How the ledger is derived, and what detects it going stale (`§Q`-2)

**DERIVED**, four producers, each with its own input and its own drift check:

| producer | input | output | drift check |
|---|---|---|---|
| `findings.py --pairing` | 6 oracle bibs + the witness roster | roster/record disagreement | itself — reports TRUE DRIFT every run |
| `commit_refusal` | the staged index + gate roster | per-gate verdict | itself, per run |
| `intake_manifest` | the corpus + `file_header` + `adopter_import` | per-module readiness | itself, per run |
| `mdstruct --budget` | the plan file | per-section bytes | none |

⚑ **AND THE STALENESS DETECTOR FOR THE SYMBOL SET ITSELF IS ABSENT.** The ⟡/Ⓝ/Ⓑ symbols this
session emits each tick — the actual work list — live **only in transcript**. There is a gated
mechanical home for exactly this shape (`scripts/worklist.py`: predicate verbs `commit` / `defines` /
`exists` / `grep` / `cmd0` / `manual`, `worklist_gate` in pre-commit), and it holds **Agda arc
symbols and none of the tooling symbols**. `gate-G114`.

⚑⚑ **ENTERING THEM IS BLOCKED.** `pycodemod --types scripts/worklist.py` → 4 mypy codes, and the
per-file gate is all-or-nothing. So the ledger's own home is unwritable, which is `SB-3`'s shape
arriving one level up.

## SB-3 · What is blocked, on whom, for how long (`§Q`-3)

**Substrate `HEAD` is still this session's start commit.** Nothing produced this session has landed.

    python3 -m substrate.commit_refusal   -> 8 gate(s) WOULD REFUSE this commit

⚑ **ONE SHARED CAUSE, NOT A LIST OF ITEMS.** Anything any party is waiting on from substrate is
waiting on the same thing: an unpaid ratchet population, **not** an unmade decision. I hold commit
authority for this repo and the gates still refuse — which is the promotion gate working as designed.

**Blocked on the per-file gate specifically** (all-or-nothing, no suppression path), measured by
`pycodemod --types`:

- `.claude/agents/findings.py` — blocks every new witness kind, the `mode:` polarity probe, and the
  `traces:` kind. `gate-G113` and predecessors.
- `scratch/mdstruct.py` — blocks wiring `substrate/md_hkey.py`, the built replacement for the
  `--headers` floor defect.
- `scripts/worklist.py` — blocks `SB-2`'s repair.
- seven `climode` consumers — `gate-G95`.

**Duration:** not stated. No figure here rests on a duration.

## SB-4 · What I am blocking for someone else (`§Q`-4)

⚑ **Answered before reading any peer leg, and I was wrong in the direction the census predicts.**

`mtools` carried two items as *blocked-on-substrate* and had never asked. Measured on their prompt:

    git log --all --oneline -- scripts/membudget-ledger   -> empty
    git status --short --untracked-files=all              -> ?? scripts/membudget-ledger
                                                             M  scripts/membudget

**The ratchet island is not missing. It was UNSTAGED.** Both paths are now staged. Their knowledge
was *current*; their inference (*"cannot be committed"*) was false, and my own state was *absent* —
neither of us could have caught it alone.

**membudget's keyway:** unmeasured. A `SB-6` row, not an answer.

⚑⚑ **AND THE BLINDNESS IS STRUCTURAL.** Every reader in `SB-2` is scoped to *substrate's own tree*,
so an obligation **another party holds toward this one** is invisible by construction. I have quoted
an accurate staged-path count every tick over a population **I chose**; no growth in it could ever
have contained mtools' two items. `gate-G116`.

**Unknown beyond that.** I do not know what else I am blocking. Nothing here enumerates it.

## SB-5 · What I have declined, and why (`§Q`-5)

- **Writing this leg into mtools.** Declined — the grant is a peer's, not my operator's. See the header.
- **Proposing a def-closure extractor** (`gate-G113`). Declined per the `build-hermeticity` `§D` norm:
  *declining to propose an instrument after being wrong about a structure from its output is the
  correct epistemic move.* I have been wrong twice this session about what the missing capability is.
- **Editing the shared-baseline tracker case** (`gate-G109`). Three registered findings rest on that
  assertion; replacing `== 2` with `== 1` re-arms an assertion that expires at the next migration.
  The property must be named first.
- **Optimizing the warrants slice** (`gate-G110`). The per-item half is already shardable; the
  whole-corpus half is paperkit's action boundary. Declined as not-mine rather than not-worth-doing.
- **Reverting the `bibstruct` swap to make a census green** — retiring a finding by restoring the
  thing it is about.

## SB-6 · What I cannot count (`§Q`-6)

⚑ **The union of the three intake blocker classes.** The reader states they overlap; nothing reports
the union. So substrate's remaining migration distance is **unmeasured**, and the three published
numbers cannot be summed.

⚑ **The migration DAG's true edge set.** `adopter_import --reach-back` enumerates 42 unpackaged names
blocking 69 modules — **at module scope, which it says in its own summary**. Function-scope imports
are real packaging dependencies and invisible to it, measured twice (`gate-G112`). So that frontier
is a **floor on the DAG, not a map**, and the failure direction favours *false roots*.

⚑ **What any peer is blocked on from substrate**, beyond what a peer tells me. No instrument here
enumerates obligations others hold toward this repo. `SB-4` exists only because mtools asked.

⚑ **Whether `refuse-rather-than-default` is honoured across the toolkit.** The convention is
*declared* (`toolmodes --declines`) and no reader censuses who honours it. `gate-G105`.

⚑ **The gateable-but-ungated population.** A ratchet that exists and is not yet wired is absent from
the gate census and indistinguishable there from a file that ratchets nothing. `gate-G108`.

⚑ **membudget's keyway state.** Named by a peer, unmeasured by me.

⚑ **How much of the 238 `standing` population is legitimately standing.** `standing` is vacuous by
construction, so no run can partition it into *measured fact* versus *should have been behavioural*.
That partition needs a per-witness read nobody has done.

---

## SB-N · Roster nominations (`§6`)

- **`el-openglo`** — holds `catalog/worklist/warrants.bib` and `catalog/cotype/warrants.bib`, the same
  worklist shape as substrate's. Nominated in substrate's `build-hermeticity` leg for the same reason.
- **The next session in this repo.** Per `census-kit` §6, a party is a *vantage*, and a compaction is
  a lossy channel. This session's symbol set lives in transcript (`SB-2`), so the next vantage
  inherits handles whose referents it cannot resolve — it is a rostered party that will not know it.

## SB-L · Limits of this leg

- Filed at **rev 5**; the census is live and `§V` may have moved under it.
- **No peer leg was read.** Five were in `HEAD` at filing.
- `SB-4` is answered from **one** peer's prompt. It is a lower bound on what substrate blocks and
  says nothing about parties who have not asked.
- Every count is from a reader scoped to substrate. That is the leg's subject and also its bound.


## SB-A1 · Addendum — SB-4's witness names the wrong command (added after filing)

⚑ **The claim in `SB-4` holds. Its stated witness does not establish it, and re-running that
witness today REFUTES the leg falsely.**

Filed witness: `git log --all --oneline -- scripts/membudget-ledger` → empty.
Re-run: **four commits**, every one reading `index on main: 771283c81`. They are **stash**
commits — `--all` includes `refs/stash`, and this tree holds eleven stash entries.

The question `SB-4` meant to ask is about **branch history**:

    git log --branches --oneline -- scripts/membudget-ledger   -> empty
    git log --branches --oneline -1 -- scripts/membudget       -> 8a6c8cfff  (positive control)

The control fires on the sibling path, so the reader sees the shape it calls absent and the
ledger genuinely has **no branch history**.

⚑⚑ **THE ORIGINAL READING WAS TRUE BY LUCK OF TIMING.** No stash carried that path when it was
first run. A stash created before the check would have reported commits for a file that has never
landed on a branch — a false **positive**, in the direction that would have closed the row.

⚑ **AND THE STALENESS IS WORSE THAN A STALE FIGURE.** A reader re-running the filed command today
gets four rows and concludes the leg is refuted, when the underlying claim holds under the correct
instrument. That invites a false **refutation** rather than a false confirmation.

Found by `mtools-2e` re-running its own basis after this leg was filed, and verified here
independently. `gate-G121`. Per `§D`, recorded as an addendum rather than an amendment to
`SB-4`.
