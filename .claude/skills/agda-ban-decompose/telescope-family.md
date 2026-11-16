# The telescope / split family — the back-edge document

**What this is.** The one page that names every tool in the split-and-telescope family
and says which precondition selects it. It exists because of a measured loop, in the
operator's words:

> *"Some of the tools got built **after the LLMs forgot the pipeline existed.**
> Honestly, **that kept happening.**"*

and it is shaped by their requirement for the remedy:

> *"always ensure the remaining tools point to a document that points back at all of
> them, so they're **cross-discoverable**."*

⚑ **THIS DOCUMENT IS NOT THE MECHANISM — THE REFUSALS ARE.** A document nobody is
routed to loses to a refusal by construction, and that argument already sank an
earlier index proposal in this repo. So every tool below **names this file by
citing one constant** (`agda_imports.TELESCOPE_MAP`), printed at the moment a tool
declines or warns. The document is what a refusal NAMES; it is not a place a reader
is expected to already know to look. If you found this page any other way, the
routing worked by luck and that is a defect to report.

---

## The selector — which tool, by precondition

All four splitters share ONE predicate, `agda_lex.telescope_span` (14 call sites
across the family), so the boundaries below are structural, not stylistic.

| the shape you have | the tool | why the others decline |
|---|---|---|
| bare `module M where`, one lemma per leaf | `split_lemmas.py` | the baseline case |
| telescope on the **FILE HEADER** — `module M (n : ℕ) where` | `split_telescoped.py` | `split_lemmas` REFUSES: leaves would miss both the parameters and the above-header imports |
| telescope on an **INNER** `module Over … where` | `split_inner_module.py` | `split_lemmas` treats the block as one unit; `split_telescoped` sees a bare file header and refuses |
| a parameterized module to be re-homed wholesale | `split_param_module.py` | not a per-lemma split at all |

⚑ **THESE ARE FOUR INDEPENDENTLY-VIABLE ATTACKS WITH FOUR DISTINCT PRECONDITIONS —
DO NOT CONSOLIDATE THEM.** `split_inner_module.py:4-14` states the boundary in the
repo's own words: *"THE GAP BOTH EXISTING SPLITTERS DECLINE, EACH CORRECTLY… Neither
refusal is wrong and the shape has no owner."* **The refusal surfaces ARE the
selection mechanism**; merging the tools removes them and leaves a reader with a
single entry point that cannot say which case they are in.

## The repair tools — provoked BY a split, not part of one

| tool | when |
|---|---|
| `hoist_telescope_imports.py` | after a hand-split (or any hand-written telescope): an import BELOW the module header is out of scope for the telescope; surfaces as `[NotInScope]` or `[NoParseForApplication]` |
| `agda_defs.py --repair-telescopes` | restore a telescope a decomposition dropped |
| `agda_defs.py --telescope-imports` | hoist the imports a telescope needs |
| `topup_leaves.py` | widen an emitted leaf's telescope arity |
| `prune_leaf_opens.py` | narrow the leaf `open`s a split left wide |
| `telescope_migrate.py` / `telescope_migrate_gen.py` | migrate consumers onto a changed telescope |
| `recover_presplit.py` | recover the pre-split state |

## ⚑ These are DE-FACTO STAGES OF A PIPELINE THAT DOES NOT LIST THEM

`split_pipeline.py` chains: split → isolate-check → prune → rewire → sweep →
orphan-`.agdai` → makefile regen → build. **Telescope repair appears nowhere in that
chain**, yet `split_lemmas`' decline, `hoist_telescope_imports`' existence, and the
`--repair-telescopes → --telescope-imports` pair are ALL provoked by splits.

`agda_imports.stage_warning` is this family's one stage-discipline mechanism, and it
records why (user, 2026-08-01): *"the pipeline tools aren't MEANT to be run
independently"* — a stage is written against the stages around it, so **run alone,
each looks like a bug**. It has exactly **3 call sites**: `fix_stale_using:442`,
`prune_imports:472`, `rewire_to_leaves:502`. **None of the telescope family uses
it.**

⚑ **THAT IS THE LOOP THIS PAGE EXISTS TO BREAK: a tool built after the pipeline was
forgotten cannot announce itself as a stage of it, and the next reader forgets it the
same way.**

⚑ **AND THEY ARE STAGES OF SOMETHING UNNAMED, NOT OF `split_pipeline`.** Adding them
to `split_pipeline`'s chain would be wrong: they are CONDITIONAL repairs selected by a
shape (`telescope_span is not None`), not unconditional stages every split runs. The
honest description is a second, unnamed pipeline — *hand-split or telescoped-root
repair* — whose stages are the repair table above. Naming it is open work; until it is
named, this document is the only thing that groups them.

## Reachability — how each tool is found

`split_telescoped.py`, `hoist_telescope_imports.py`, `split_param_module.py`,
`split_inner_module.py`, `telescope_migrate*.py`, `prune_leaf_opens.py`,
`topup_leaves.py`, `recover_presplit.py` have **zero importers** — they are
file-level entry points reachable only by knowing the filename. Before 2026-08-26,
`toolmodes --find telescope` answered with LIBRARY FUNCTIONS
(`_close_over_siblings`, `inner_modules`, `needed`, `arity`) and **the tools
themselves never appeared as tools**; `--find "split a telescoped module"` returned
`collide`, `queue`, `inner_modules` and not `split_telescoped.py`. `--find` now
carries a **TOOL arm** that matches the tool's own name and its self-description, so
the question "how do I split a telescoped module" reaches the tool that does it.
