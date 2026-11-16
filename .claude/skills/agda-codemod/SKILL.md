---
name: agda-codemod
description: >-
  Fire this BEFORE performing or planning any mechanized edit to Agda source in this repo —
  splitting a module, rewiring or pruning imports, renaming at source, paying down the import
  ban — and before answering how to repair a `NotInScope`, `ClashingDefinition`, `AmbiguousName`
  or dangling-import error, or how far the tree is from a green build. It routes to the
  `agda-oracle` agent, which re-derives every mode from the tool that owns it. Fire it on your
  own tells too: *"I'll just edit the import block"*, *"let me add a `using` to fix the clash"*,
  *"I'll rename it everywhere"*, *"`--dry-run` will show me first"*, *"there are N errors left"*,
  *"no tool covers this"*. It exists because this surface punishes recall twice over. Mode names
  here are guessed wrong routinely — `toolmodes` was built after an operator burned five calls on
  flags that do not exist on the tool invoked, and the session that commissioned this agent burned
  eight more. And unlike the other oracles' surfaces, most of these tools WRITE: six have no dry
  run at all, four cannot self-describe (two of those are unconditional writers), and the one that
  rewires the entire tree does it from a single positional argument. A wrong answer here does not
  mislead a reader — it mutates the tree, and nothing in the toolkit reverts.
---

# The Agda codemod oracle

**Route the question; do not answer it from this file.** Dispatch the `agda-oracle` agent
(`Agent` tool, `subagent_type: "agda-oracle"`). It starts fresh, runs the tools bare against the
tree as it is *now*, and re-derives every mode. This file carries only what a reader must not get
wrong on the way there.

## When this fires

- **Any mechanized Agda edit** — split, rewire, prune, dedup, hoist, narrow, rename, strip,
  retire, collapse. All of it is tooled; none of it is hand-edited.
- **A build error you are about to repair** — the four kinds have four different repairs, and
  three of them are the *wrong* fix for at least one of the others.
- **"How far is the tree from building?"** — the number has four verdicts and collapsing them is
  wrong in both directions.
- **Anything touching the import ban** — including, especially, an idea for making the count fall.
- **Before quoting any figure from this surface** — three of its central counts are FLOORS whose
  own tools say so.
- **On your own tells:** *"I'll just add the import by hand"*, *"a `using` list will fix the
  ambiguity"*, *"rename it at every call site"*, *"the tool is dry-run by default"*, *"run it bare
  to see its modes"*, *"that's N errors"*, *"the unused-import count is N"*, *"I'll grep for who
  defines this"*, *"there's no mode for that"*, *"I'll revert if it goes wrong"*.

## The five facts to not get wrong

**1. Most of these tools WRITE, and the safety contract is NOT uniform — it is four different
contracts.** Dry-by-default with `--apply` is the common one and it is *not* the rule. Six tools
have **no dry run at all** (`agda_imports`, `split_upstream`, `narrow_leaf_imports`, `strip_using`,
`prune_imports`, and `scope_fix`, which **writes by DEFAULT** and inverts the convention outright).
`drop_dead_renames` refuses to default either way and states the reason — "a default-dry silently
does nothing when you meant to write; a default-apply silently writes when you meant to look" —
which is the contract the toolkit is converging on. ⚑ **And nothing here reverts.** Per repo policy
a *stash*, not a revert, is the way back; `edit_snapshot.guard` by its own docstring never restores
anything, and several write paths do not even arm it. Ask the agent for the contract of the
specific tool, in the same breath as its name.

**2. "Run the tool bare to read its modes" — this repo's own instruction to every reader —
silently fails on the four tools where it matters most.** `agda_imports`, `split_lemmas` and
`split_upstream` raise a bare `IndexError` traceback with no usage; `scope_fix` exits **0 printing
nothing** (its docstring sits below its imports, so it is a bare string expression, not `__doc__`).
Two of those four are unconditional writers, and `split_upstream` rewires **every**
`agda/Substrate/**/*.agda` from one positional argument. A reader who obeys the pointer gets a
traceback from the tree-wide rewiring tool and a silent exit 0 from the writes-by-default tool.

**3. Decompose the PROVIDER first, re-measure, and only then rename what survives — and
"split only when the names COLLIDE" is a fiction that keeps getting written back in.** Most
collisions **evaporate** under decomposition, because the two names stop entering the same
interface. But collision is a *symptom*, never the reason to split: the ban exists to minimise the
information each file imports and holds, so a module with zero collisions and forty definitions
still over-imports by forty. The corollary is the one to watch for in your own plans —
**deleting a filter without splitting the upstream is metric-gaming**: the ban count falls while
the same information is imported and scope gets WIDER.

**4. `rename_at_source` is guarded for importers and UNGUARDED IN THE HOME FILE.** It refuses
AMBIGUOUS importers and warns of a measured 1-in-10 false positive across them. The home file gets
**no ambiguity check at all** — every occurrence is rewritten, including ones that mean a different
provider and including text inside comment prose. Measured on `Foundation/Fin/Op2.agda`: it rewrote
the definition *and* a ℕ use on the right-hand side, which meant the other provider. Diff the home
file after every rename.

**5. Three counts here are FLOORS, and each is footnoted by the tool that prints it.**
`fix_notinscope --unresolved` says it outright: a name with no known definer is **silent** (local
binding, stdlib, or pattern variable), so it reports what it can SEE, never that nothing is
missing. `agda_defs --unused-imports` rests on a keep-biased predicate. `split_pipeline --verify`
*without* `--build-log=` under-counts, because a failed module leaves no fresh log — artifacts
alone read 41 where make said 121. Report a floor as a floor.

## Absence claims need a witness

A guessed mode name is the characteristic failure here, and it produces a false absence: the tool
prints a usage block, the flag is not in it, and the reader concludes the capability does not
exist. `toolmodes.py --find <name>` is the reader for *which tool has this mode* — and its
`--divergence` mode exists because **~160 modes dispatch while appearing in no self-description**.
`split_pipeline` was once 17 of 17 undocumented, and that cost a duplicate `distance()`, written
and then deleted on discovering `--from-build` already did it, with a better regex.

Say "no mode by that spelling," never "the toolkit cannot do that." A missing mode is WORK.

## No generated census — and that is a decision

⚑ **This skill carries no `--sync`/`--check` census block, deliberately.** Every figure one would
hold already has a gated authority elsewhere: `toolmodes.py --sync`/`--check` owns the mode roster
(a second roster beside it is exactly the duplication this toolkit retires), `gate_census.py`
owns gate health, `build_census.py --gates` owns the gate roster. The remaining figures —
unresolved-name counts, the four build verdicts, ban paydown — are **volatile local build state**
that would fail a drift gate on every machine and after every commit, the same reason
`gate-observations` and `build-observations` are ungated in their skills.

What this surface actually lacks a reader for is the **write contract** — which tool previews,
which writes by default, which arms a snapshot on which branch. That is not derivable from a bare
run (see fact 2), which is why it lives in the agent as curated, witnessed prose rather than as a
generated block nothing can regenerate. **Do not add a census here without a tool that owns it.**

## Growing this

A missing mode is WORK, not a finding.

1. **`fix_notinscope --unresolved --summary`** — today the mode emits one line per name (a 635KB
   dump over the tree) with the totals only in a footer, so reading the census figure requires
   manipulating the output: the exact shape the standing rule forbids.
2. **A mode splitting unresolved names into AMBIGUOUS vs REPAIRABLE.** The tool computes that
   distinction on every line and reports it nowhere in aggregate — it is the number that says how
   much of the migration is mechanizable.
3. **A collision-dissolution predicate** — for one collision, would decomposing the provider remove
   it? The ordering rule that governs this whole migration is stated in prose and enforced by
   nothing, and inverting it is a recorded miss.
4. **Usage output for the four tools that cannot self-describe**, and a "not a CLI" notice for
   `split_unblock`/`split_census`, which exit 0 silently where `rewire_to_leaves` prints one.
5. **A dry run for `narrow_leaf_imports`** — it writes unconditionally, takes its required config
   from an undocumented `PREFIX` env var with no default, crashes bare, and is the tool the
   `agda-ban-decompose` pipeline names.
6. **A snapshot on every write path in `retire_mod_tip`** — `_snapshot_once` is armed in one branch
   of `rewrite`; five others write without it.

## See also

- `.claude/skills/agda-ban-decompose/SKILL.md` — the 6-step decomposition pipeline itself, the
  conservation guard's seven caught silent-deletion bugs, and the known collision sets. This skill
  routes; that one prescribes.
- `.claude/skills/precommit-gates/SKILL.md` → `gate-oracle` — for what a gate checks and what its
  baseline holds. ⚑ Ban-ratchet paydown **never records while any addition is present**, so a red
  gate can be hiding enormous progress. Read the paydown line.
- `.claude/skills/build-system/SKILL.md` → `build-oracle` — for caps, leases, and why a compile
  was killed. ⚑ Several codemod tools COMPILE (`split_pipeline --census`/`--why`,
  `enforce_ban` — a full build per module, `fix_notinscope --apply`).
- `.claude/skills/struct-tools/SKILL.md` — the artifact→tool table, which is the PreToolUse hook's
  live authority, not merely documentation.
