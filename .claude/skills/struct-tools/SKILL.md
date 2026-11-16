# Structural tools — the entrypoint

**Never `grep` a structured artifact.** (This tooling is borrowed by several repos now, so
the rule is not scoped to one checkout — a `.py` is owned by `pycodemod` wherever it sits.)
Agda, Python, markdown and BibTeX each
have a tool that reads their *structure*; a line-regex answers structural questions by
accident or not at all. This file is the entrypoint: it names the tools that exist today and
how to ask each one what it can do. It carries no **hand-written** mode table — a table
someone maintains is a derived view that rots the first time a mode is added. That reasoning
is kept and is exactly why the mode census near the bottom is **generated** from the tools
themselves (`toolmodes.py --sync`) and **gated** against drift (`--check`), rather than absent.

## The rule: a missing mode is WORK, not a finding

> If you have a question the tooling does not answer directly, **fix the tooling so it answers
> your question.**

This is the whole point, and it is stronger than "route your question to the right tool."
When you hit a question no mode answers, the response is to **add the mode** — not to grep
around it, and not to file it as a wall and move on. A named-but-unbuilt gap is the weak half
of this rule; the tooling only compounds if each session leaves it able to answer something it
could not answer before.

**Where the capability goes: a MODE first, a new TOOL only for a new artifact kind.** Most
missing capabilities belong in a tool that already exists — the artifact has a reader, and
that reader simply cannot answer this question yet. Ask: *does a tool already parse this
artifact?* If yes, the work is a **new mode on that tool**. Only when the artifact kind itself
has no reader do you add one.

Both halves are measured. Three of four gaps found in one recent survey were modes on existing
tools — a `--dead` that cannot see callbacks passed as values, a `--superseded` that takes one
file where the corpus is fifteen, an `--items` blind to another repo's marker glyphs. The
fourth was a genuine new kind: a `.tsv` label registry that is the *authority* for its repo,
with no reader at all. An HTTP/OTLP metrics surface was a second such kind — **now built**
as `scratch/tsdbprobe.py`, so `curl` at cassian's store is no longer the route. So if you are
reaching for `curl` or a delimited-file parse, you have found the next **tool**; if you are
reaching for `grep` at an artifact one of these tools already reads, you have found the next
**mode**.

**The tool set is OPEN.** The list below is what exists today, not a closed inventory. The
pattern is *one structural reader per artifact kind* — so an artifact kind with no reader is a
build, not a dead end.

Corollaries, each learned the hard way:

- **A false positive in a query you act on is a bug, not a caveat.** `--dead` counts syntactic
  call sites, so a function passed *as a value* (an OTLP callback, a decorator target, a
  registry entry) reports as dead. That is a defect in the mode, owed a fix.
- **Fixed arity is a capability bound.** A mode that takes one file cannot answer a question
  about an append-only corpus of fifteen. Widen it; do not run it 105 times and diff by hand —
  that is the output-manipulation this rule forbids.
- **Hardcoded vocabulary rots.** A label matcher that knows only this repo's prefixes cannot
  see another's marker glyphs. Parameterize it.

## The tools that exist today

| artifact | tool | run bare to list its modes | claims |
|---|---|---|---|
| Python (this repo's own tooling) | `scratch/pycodemod.py` | `python3 scratch/pycodemod.py` | `.py` `.pyi` |
| markdown (plan / worklist / catalog) | `uv run mdstruct` | `uv run mdstruct` | `.md` |
| BibTeX (the warrants claim-DAG) | `scratch/bibstruct.py` | `python3 scratch/bibstruct.py` | `.bib` |
| Agda source | `scratch/agda_lex.py` + `scratch/agda_defs.py` | `python3 scratch/agda_defs.py <name>` | `.agda` `.agdai` `.lagda` |
| HTTP/OTLP metrics surface (cassian's VM) | `scratch/tsdbprobe.py` | `python3 scratch/tsdbprobe.py` | — |
| Claude Code session transcript | `scratch/transcriptstruct.py` | `python3 scratch/transcriptstruct.py` | `.jsonl` |
| the postgres STORE (tiers, rows, locks, activity) | `jea/metalanguage/schema.py` | `python3 jea/metalanguage/schema.py` | — |
| CODEPOINTS — every non-ASCII character, in any file | `scratch/codepoints.py` | `python3 scratch/codepoints.py` | — |
| the SQL/relalg SURFACE (store + builders + the lift arc + the allegory) | `jea/metalanguage/sql_lift.py` | `python3 jea/metalanguage/sql_lift.py` | — |
| GENERATED MAKEFILES (the flat import-DAG build) | `substrate/make_rules.py` | `python3 substrate/make_rules.py` | `.mk` `Makefile` |

⚑ **THE MARKDOWN ROW NAMES AN INSTALLED PACKAGE, NOT A REPO FILE (operator, 2026-09-21).**
`uv run mdstruct` is mtools' `mikemol-mdstruct`, declared in `pyproject.toml` from its git
remote (`git+https://github.com/mikemol/mtools.git@main#subdirectory=mdstruct`) and spelling
its modes as SUBCOMMANDS (`spans`, `grep`, `tables`, `rows --where`, `classify`, `labels`,
`roundtrip`, `fixpoint`, `lint`, `narrowest`, `verify`). The in-repo `scratch/mdstruct.py` is
RETIRED — never invoke it; it still exists only until its suite fixtures and the two rosters
that name it as an identity (`check_mode_contracts`, `concept_bindings`) are repointed. Modes
mtools does not yet cover (`budget`, `items` with link targets, `coherence`) are mtools'
W20–W22, asked 2026-09-21 — a gap there is their queue, not grounds to reach for the retired
file.

⚑ **THE CODEPOINT ROW CLAIMS NOTHING ON PURPOSE, AND THAT IS THE INTERESTING PART.** Its
subject sits BELOW every artifact kind — the same `⟡` appears in Agda operators, markdown
labels, Python docstrings and TSV ledgers — so claiming `.agda` would put a SECOND owner on
an artifact `agda_defs` already owns, which is the roster-beside-a-roster shape this table
exists to retire. It claims `—` for the reason `tsdbprobe` does: **not every tool's subject
is a file type.** It is the first tool here whose population is the whole repo rather than a
suffix, and it exists because `--prose <regex>` can only answer about a vocabulary someone
already NAMED — a family nobody thought of is invisible to it, which is the roster defect
one level down, inside the instrument used to diagnose the roster defect.

⚑⚑ **THE STORE ROW WAS MISSING UNTIL 2026-08-14, AND ITS ABSENCE WAS MEASURED AS A
FALSE ABSENCE CLAIM.** `toolmodes.py --find locks` returned **0 hits across 93
declared modes**, and that was read — by me, in a dispatch brief — as *"the breakdown
method this repo wrote down was never built."* It is a fact about the census's
POPULATION: `routes()` builds that population from **this table**, and the table named
seven `scratch/` artifact-readers and no store reader at all. `schema.py` already had
`--activity`, `--census`, `--growth`, `--lifecycle` and seventeen more, every one of
them invisible to `--find`. **A capability nobody's index covers is functionally
absent** — the same distinction as *no consumer found* versus *no consumer exists*,
committed inside the tool built to prevent it.

⚑ **AND THE ROW IS STILL PARTIAL, WHICH IS RESIDUE AND NOT A FIX.** `scripts/sppf_*.py`
(`sppf_tree`, `sppf_drain`, `sppf_vocab`, `sppf_db`, …) are store tools too and remain
outside the census; `--find` cannot see their modes either. One row is the reachable
step, not the closure.

⚑ **THE `claims` COLUMN IS THE GATE'S AUTHORITY, NOT DECORATION.**
`scripts/hook_structural_query.py` READS this column live to decide whether a textual
command (`grep`, `sed`, `head`, `wc`, …) is reaching past a tool that owns the
artifact. **Adding a row — or an extension to an existing row — arms the gate for that
artifact in every repo that borrows this tooling, with no code change.** A tool whose
artifact has no file form (the metrics surface) claims nothing and is written `—`.

⚑ **AN ARTIFACT NO ROW CLAIMS IS NOT REFUSED — and that is deliberate.** The gate can
only route what the table declares, so an unclaimed artifact (`.tsv` ledgers, `.log`
build output, `.dot` graphs) passes today. It passes *by construction*, not
by an exemption someone wrote, and the refusal message says so: the way to close the
gap is to **add the row**, which is the same act as adding the tool. Do not add a
hardcoded suffix list anywhere else — a second roster beside this table is exactly the
frozen-roster shape the table exists to retire.

⚑⚑ **A CLAIM MAY BE A SUFFIX OR A BARE FILENAME, AND THE SECOND FORM EXISTS BECAUSE THE
FIRST COULD NOT REACH `Makefile`.** Adding the `.mk` row armed the gate for the generated
`agda/Flat.mk` and left `agda/Makefile` beside it passing — it carries **no suffix at all**,
so `Path(arg).suffix` was the empty string and no cell value could bind it however this
column was written. That was a gap in the MECHANISM, not in the table. `claims()` now reads
both forms into one map: a suffix key always begins with `.` and a filename key never does,
so the two key spaces cannot collide and no second mapping was needed.

⚑ **THE SUFFIX WINS WHEN BOTH COULD MATCH.** `Flat.mk` has suffix `.mk` and basename
`Flat.mk`; the kind claim is the general one, so a filename claim can never shadow it and
capture another row's artifact. **And the case fold is over BOTH sides** — a case asserting
`makefile` routes FAILED first, because folding only the argument compares two spellings of
it against one spelling of the claim.

**Run the tool with no arguments and it prints the mode list it CHOOSES to publish,** with
the reason each mode exists. Start there — but that output is **not the whole authority**,
and the gap is measured rather than hypothetical: flags that dispatch on `sys.argv` while
appearing in no usage line at all are common across this toolkit, so an agent obeying
*"run it bare, that output is the authority"* correctly reported existing modes as absent.
The generated census below is the **union** — what each tool publishes AND what it accepts —
and it carries its own counts, so no figure is frozen in this prose. There is no `pystruct`
— the Python tool is `pycodemod`.

## The mode census — GENERATED, do not edit

Everything between the two markers is machine-owned. `python3 scratch/toolmodes.py --sync`
rewrites it from the tools themselves; a hand edit is overwritten on the next sync;
`--check` is a pre-commit gate that refuses drift, because **a generated block nobody
regenerates is worse than no block — it reads as authoritative while being stale.**

Placement stays with the editor: `--sync` fills between the markers and **refuses** a file
whose markers are missing, rather than guessing where the block belongs.

--- BEGIN mode-census ---
⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 scratch/toolmodes.py --sync`
rewrites everything between the markers; a hand edit is overwritten on the next
sync, and `--check` is a pre-commit gate that refuses drift. Both DERIVE it — the
documented half from each tool's own bare output, the undocumented half from its
AST (`--flag` literals anchored to `sys.argv`). No roster of modes is maintained
here: a hand-written table is the thing that would rot, which is *why* this is
generated rather than absent.

**614 documented + 5 undocumented mode(s) across 105 tool(s).** A `--flag` that
appears NOWHERE below is accepted by no tool — that is what makes `pycodemod
--argstr` a guess rather than a lookup. For a mode's gloss, its owning tool, and
the near-misses by name AND by meaning: `toolmodes.py --find <name>`.

⚑ **The undocumented rows are the reason this block exists.** Those flags
dispatch, and no usage line names them — so *"run the tool bare and read its mode
list"* cannot see them, and until this block nothing else could either. Each one
is a gap in that tool's self-description: WORK, not a capability this blesses.

```
scratch/pycodemod.py  [Python (this repo's own tooling)]  78 documented, 0 undocumented
    --aliases --ambient --archive --artifacts --asserted --attr --available --banner
    --binding --blocks --calls --check-contracts --collision-apex --collisions
    --commentary --constructs --control --crossings --dead --declare-modes --diagnose
    --discards --discriminates --escapes --exits --fingerprint --fix-owes-callers
    --forwards --from --funcnames --groups --guarded --importers --imports --key
    --keys --kind --kinds --last --layout --lines --literal --marks --monotone
    --package --placement --portable --projects --rawreads --reaches --reifies
    --relalg --relname --resorts --rev --rivals --roundtrip --seed --selftest --shape
    --shape-all --since --sites --size --snapshots --sorted --source --split --sql
    --sqlname --state --swallows --top --touches --types --unbound-snapshot --values
    --verbatim

scratch/bibstruct.py  [BibTeX (the warrants claim-DAG)]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line

scratch/agda_lex.py  [Agda source]  2 documented, 0 undocumented
    --by-op --sections

scratch/agda_defs.py  [Agda source]  41 documented, 0 undocumented
    (positional) --alias-probe --alias-trace --applied-args --at --between
    --clause-audit --closure --cluster --collide --consumers --cycle-cuts --cycles
    --dangling --depends --depth --double-route --dup-variables --flags
    --flat-variable --grep --importers --imports --late-imports --lp-apply --orphans
    --prose --provides --qualified --qualified-repair --reexports --repair-telescopes
    --run --selftest --stale-sections --stranded-residue --telescope
    --telescope-imports --trust --under --unused-imports

scratch/tsdbprobe.py  [HTTP/OTLP metrics surface (cassian's VM)]  14 documented, 0 undocumented
    --base --changes --deadline --labels --names --ping --poll --producers --query
    --reachable --selftest --series --since --verify

scratch/transcriptstruct.py  [Claude Code session transcript]  7 documented, 0 undocumented
    --context --extract --grep-content --human --messages --prose --stats

jea/metalanguage/schema.py  [the postgres STORE (tiers, rows, locks, activity)]  35 documented, 1 undocumented
    --activity --arity --cancel --census --check-indexes --columns --core --coverage
    --ddl --establish --fibre --flush --growth --headroom --holes --index-size
    --lifecycle --locks --migrate-queue --migrate-views --nullity --packed --plan
    --probe --promotes --reclaim --reclaim-core --relations --sample --seed --selftest
    --spread --transport --uniqueness --widest
  ⚑ dispatched, in NO usage line:
    --sizes

scratch/codepoints.py  [CODEPOINTS — every non-ASCII character, in any file]  6 documented, 0 undocumented
    --block --char --diff --limit --selftest --where

jea/metalanguage/sql_lift.py  [the SQL/relalg SURFACE (store + builders + the lift arc + the allegory)]  1 documented, 0 undocumented
    --selftest

substrate/make_rules.py  [GENERATED MAKEFILES (the flat import-DAG build)]  6 documented, 0 undocumented
    --grep --modules --selftest --summary --target --var

jea/metalanguage/autocorr_synth.py  [—]  7 documented, 0 undocumented
    --agda --bucket-cap --emit --holes --min-instances --selftest --top

jea/metalanguage/query_defs.py  [—]  18 documented, 0 undocumented
    --check --compile --drops --equiv --equiv-sweep --estimate --explain --group
    --live --only --param --rows --sandbox --scans --selftest --sql --touching
    --verify

jea/metalanguage/store.py  [—]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line
  ⚑ dispatched, in NO usage line:
    --credential-backend

jea/metalanguage/synth_agda_prototype.py  [—]  13 documented, 0 undocumented
    --class --gens --gname --grade --law --lawname --module --out --recon-record
    --recon-source --recon-target --repo-root --target

scratch/band_sppf.py  [—]  2 documented, 0 undocumented
    (positional) --frames

scratch/bench_clause_audit.py  [—]  4 documented, 0 undocumented
    --agree --baseline --both --cached

scratch/cacheprofile.py  [—]  3 documented, 0 undocumented
    --probe --run --selftest

scratch/capstone_to_dir.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/check_indented_imports.py  [—]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line

scratch/collapse_carrier_nesting.py  [—]  5 documented, 0 undocumented
    (positional) --promote --rewrite-refs-to --selftest --to

scratch/conduit_resolve.py  [—]  5 documented, 0 undocumented
    (positional) --consumers --list --plan --selftest

scratch/convert_span_rule.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/decompose_rewrite.py  [—]  2 documented, 0 undocumented
    (positional) --selftest

scratch/dedup_imports.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/drop_dead_renames.py  [—]  3 documented, 0 undocumented
    (positional) --selftest --verdicts

scratch/edit_snapshot.py  [—]  2 documented, 0 undocumented
    --from-snapshot --holding

scratch/enforce_ban.py  [—]  5 documented, 0 undocumented
    --apply --include-renaming --max --status --stop-on-fail

scratch/fcr_direct.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/fcr_qualify.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/findings.py  [—]  3 documented, 0 undocumented
    --list --register --sweep

scratch/fix_ambiguous_import.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/fix_dead_fin_alias.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/fix_notinscope.py  [—]  6 documented, 0 undocumented
    (positional) --aliases --classify --clause-forms --summary --unresolved

scratch/fix_sections.py  [—]  3 documented, 0 undocumented
    (positional) --apply --rows

scratch/gate_wall_census.py  [—]  2 documented, 0 undocumented
    (positional) --waypoints

scratch/gen_case_no_fix.py  [—]  2 documented, 0 undocumented
    --inline --strategy

scratch/gen_fcr_slices.py  [—]  1 documented, 0 undocumented
    --apply

scratch/gen_kat.py  [—]  5 documented, 0 undocumented
    --emit-only --mb --shards --sweep --variant

scratch/hoist_telescope_imports.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/lift_pyhelper.py  [—]  4 documented, 0 undocumented
    --apply --dry-run --fn --home

scratch/mdstruct.py  [—]  20 documented, 0 undocumented
    --append-section --budget --coherence --fixpoint --headers --items
    --label-families --lint-config --lint-shape --narrowest --replace-section
    --roundtrip --rows --selftest --spans --superseded --table-forms --table-style
    --tables --why-not-pipe

scratch/narrow_leaf_opens.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/paydown.py  [—]  4 documented, 0 undocumented
    --fix --recheck --status --strip

scratch/pipeflow.py  [—]  9 documented, 0 undocumented
    --engine --help --no-builders --no-counts --out --ranks --rendered --sandbox
    --selftest

scratch/procstruct.py  [—]  11 documented, 0 undocumented
    --abandoned --chain --cost --kill --leases --orphans --reapers --running
    --selftest --stranded --tree

scratch/prose_apex.py  [—]  5 documented, 0 undocumented
    --corpora --corpus --min --selftest --top

scratch/prune_leaf_opens.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/qualify_imports.py  [—]  4 documented, 0 undocumented
    (positional) --apply --module --selftest

scratch/record_def_edit.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/recover_presplit.py  [—]  3 documented, 0 undocumented
    (positional) --restore --show

scratch/rename_at_source.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/replay_pipeline.py  [—]  2 documented, 0 undocumented
    (positional) --file

scratch/resolve_notinscope.py  [—]  2 documented, 0 undocumented
    (positional) --selftest

scratch/retire_mod_tip.py  [—]  3 documented, 0 undocumented
    (positional) --alias --apply

scratch/rewire_fcr.py  [—]  4 documented, 0 undocumented
    (positional) --apply --selftest --siblings

scratch/rewire_stale_module.py  [—]  3 documented, 0 undocumented
    --from --selftest --to

scratch/scope_fix.py  [—]  2 documented, 0 undocumented
    (positional) --selftest

scratch/seal_defs.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/shared_cache.py  [—]  3 documented, 0 undocumented
    --consumers --probe --selftest

scratch/split_inner_module.py  [—]  4 documented, 0 undocumented
    (positional) --apply --module --selftest

scratch/split_pipeline.py  [—]  13 documented, 0 undocumented
    (positional) --census --diagnose --from-build --last --leverage --retire
    --rewire-only --selftest --stale-why --unblock --verify --why

scratch/split_telescoped.py  [—]  2 documented, 0 undocumented
    (positional) --apply

scratch/strip_using.py  [—]  1 documented, 0 undocumented
    --module

scratch/swarmclaim.py  [—]  9 documented, 0 undocumented
    --apply --check --contended --dry-run --hold --note --release --selftest --who

scratch/telescope_migrate.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/telescope_migrate_gen.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/tmi_index.py  [—]  6 documented, 0 undocumented
    --gaps --index --out --selftest --thread --threads

scratch/tmi_status.py  [—]  7 documented, 1 undocumented
    --ablate --artefacts --cues --links --misses --score --selftest
  ⚑ dispatched, in NO usage line:
    --grep-content

scratch/tmi_subject.py  [—]  5 documented, 0 undocumented
    --gaps --links --posting --selftest --subjects

scratch/toolmodes.py  [—]  18 documented, 0 undocumented
    --all --autosync --base --check --collisions --conventions --declines --deps
    --divergence --find --gaps --help --nearmiss --ping --siblings --sync --top
    --verify

scratch/topup_leaves.py  [—]  1 documented, 0 undocumented
    (positional)

scratch/traceprobe.py  [—]  21 documented, 0 undocumented
    --base --deadline --emit --expect-spans --gate --gate-args --no-emit --operations
    --ping --poll --profile-clause-audit --reachable --selftest --service --services
    --stream --trace --tree-deadline --verify --verify-tree --wedge

scratch/unseal_defs.py  [—]  1 documented, 0 undocumented
    --apply

scratch/vfs.py  [—]  8 documented, 0 undocumented
    --at --census --compare --list --read --selftest --states --suffix

scripts/agda_census_cli.py  [—]  1 documented, 0 undocumented
    --run

scripts/buildtime.py  [—]  5 documented, 0 undocumented
    --compact --module --predict --stats --top

scripts/cap_diagnose.py  [—]  2 documented, 0 undocumented
    (positional) --heap

scripts/check_assign_types.py  [—]  4 documented, 0 undocumented
    --check --selftest --sync --vs-stubs

scripts/check_mode_contracts.py  [—]  4 documented, 0 undocumented
    --gone --nowhere --selftest --w

scripts/check_mypy_ratchet.py  [—]  3 documented, 0 undocumented
    --check --list --quiet

scripts/check_scratch_independence.py  [—]  3 documented, 0 undocumented
    --promotable --scope --selftest

scripts/check_scratch_runtime.py  [—]  7 documented, 0 undocumented
    --check --full --help --quiet --selftest --strict --surface

scripts/climode.py  [—]  11 documented, 0 undocumented
    --a --b --bad --census --core --cov --gone --good --guarded --nowhere --wet

scripts/gate_census.py  [—]  6 documented, 0 undocumented
    --baselines --check --init-absent --selftest --successors --sync

scripts/gate_ledger.py  [—]  3 documented, 0 undocumented
    --order --record --report

scripts/gate_status.py  [—]  4 documented, 0 undocumented
    --list --modes --peaks --selftest

scripts/gen_catalog.py  [—]  1 documented, 0 undocumented
    --render-only

scripts/glyph_report.py  [—]  1 documented, 0 undocumented
    (positional)

scripts/glyph_rewrite_file.py  [—]  1 documented, 0 undocumented
    (positional)

scripts/heading_probe.py  [—]  1 documented, 0 undocumented
    (positional)

scripts/hook_fire_probe.py  [—]  2 documented, 0 undocumented
    --report --selftest

scripts/primitive_catalogue.py  [—]  2 documented, 0 undocumented
    --audit --diff

scripts/proofcost.py  [—]  9 documented, 0 undocumented
    (positional) --emit --module --oracle --parse --reprofilable --selftest
    --structural --top

scripts/pycheck_show.py  [—]  2 documented, 0 undocumented
    (positional) --count

scripts/reuse_check.py  [—]  3 documented, 0 undocumented
    --against --propose --top

scripts/reuse_sweep.py  [—]  5 documented, 0 undocumented
    --gate --min-fanin --min-size --recursive --top

scripts/reuse_tui.py  [—]  9 documented, 0 undocumented
    --between --build --cache --cap --live --min-fanin --min-size --observe --top

scripts/roster_span.py  [—]  2 documented, 0 undocumented
    (positional) --text

scripts/run_selftests.py  [—]  7 documented, 0 undocumented
    --declarations --last --list --pragmas --reach --selftest --tenants

scripts/set1_ratchet_cores.py  [—]  3 documented, 0 undocumented
    --list --quiet --selftest

scripts/sppf_db.py  [—]  21 documented, 1 undocumented
    (positional) --argperm --converge --distribute --drain-core --full --height
    --ingest-core --ingest-source --init --orbit --pack-level --project-core
    --project-ref --promote-core --reconcile-stamps --refold --sandbox
    --source-concurrency --source-fidelity --undecodable
  ⚑ dispatched, in NO usage line:
    --selftest-demo-failure

scripts/sppf_node_index.py  [—]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line
  ⚑ dispatched, in NO usage line:
    --check

scripts/sppf_query.py  [—]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line

scripts/worklist.py  [—]  4 documented, 0 undocumented
    --check --md --open --update

scripts/worklist_gate.py  [—]  12 documented, 0 undocumented
    --discriminate --dispatch --engine --figures --items --next --no-cache --order
    --profile --project --solvers --sweep

── ONE NAME, SEVERAL TOOLS — the wrong tool ANSWERS instead of erroring
    (positional)       agda_defs  band_sppf  cap_diagnose  capstone_to_dir  collapse_carrier_nesting  conduit_resolve  convert_span_rule  decompose_rewrite  dedup_imports  drop_dead_renames  fcr_direct  fcr_qualify  fix_ambiguous_import  fix_dead_fin_alias  fix_notinscope  fix_sections  gate_wall_census  glyph_report  glyph_rewrite_file  heading_probe  hoist_telescope_imports  narrow_leaf_opens  proofcost  prune_leaf_opens  pycheck_show  qualify_imports  record_def_edit  recover_presplit  rename_at_source  replay_pipeline  resolve_notinscope  retire_mod_tip  rewire_fcr  roster_span  scope_fix  seal_defs  split_inner_module  split_pipeline  split_telescoped  sppf_db  telescope_migrate  telescope_migrate_gen  topup_leaves
    --aliases          fix_notinscope  pycodemod
    --apply            capstone_to_dir  enforce_ban  fcr_direct  fix_sections  gen_fcr_slices  lift_pyhelper  narrow_leaf_opens  prune_leaf_opens  qualify_imports  retire_mod_tip  rewire_fcr  seal_defs  split_inner_module  split_telescoped  swarmclaim  unseal_defs
    --at               agda_defs  vfs
    --base             toolmodes  traceprobe  tsdbprobe
    --between          agda_defs  reuse_tui
    --census           climode  schema  split_pipeline  vfs
    --check            check_assign_types  check_mypy_ratchet  check_scratch_runtime  gate_census  query_defs  sppf_node_index(undoc)  swarmclaim  toolmodes  worklist
    --collisions       pycodemod  toolmodes
    --consumers        agda_defs  conduit_resolve  shared_cache
    --core             climode  schema
    --deadline         traceprobe  tsdbprobe
    --diagnose         pycodemod  split_pipeline
    --diff             codepoints  primitive_catalogue
    --dry-run          lift_pyhelper  swarmclaim
    --emit             autocorr_synth  proofcost  traceprobe
    --engine           pipeflow  worklist_gate
    --from             pycodemod  rewire_stale_module
    --full             check_scratch_runtime  sppf_db
    --gaps             tmi_index  tmi_subject  toolmodes
    --gate             reuse_sweep  traceprobe
    --gone             check_mode_contracts  climode
    --grep             agda_defs  make_rules
    --grep-content     tmi_status(undoc)  transcriptstruct
    --guarded          climode  pycodemod
    --help             check_scratch_runtime  pipeflow  toolmodes
    --holes            autocorr_synth  schema
    --importers        agda_defs  pycodemod
    --imports          agda_defs  pycodemod
    --items            mdstruct  worklist_gate
    --last             pycodemod  run_selftests  split_pipeline
    --links            tmi_status  tmi_subject
    --list             check_mypy_ratchet  conduit_resolve  findings  gate_status  run_selftests  set1_ratchet_cores  vfs
    --live             query_defs  reuse_tui
    --min-fanin        reuse_sweep  reuse_tui
    --min-size         reuse_sweep  reuse_tui
    --module           buildtime  proofcost  qualify_imports  split_inner_module  strip_using  synth_agda_prototype
    --nowhere          check_mode_contracts  climode
    --order            gate_ledger  worklist_gate
    --orphans          agda_defs  procstruct
    --out              pipeflow  synth_agda_prototype  tmi_index
    --ping             toolmodes  traceprobe  tsdbprobe
    --plan             conduit_resolve  schema
    --poll             traceprobe  tsdbprobe
    --probe            cacheprofile  schema  shared_cache
    --prose            agda_defs  transcriptstruct
    --quiet            check_mypy_ratchet  check_scratch_runtime  set1_ratchet_cores
    --reachable        traceprobe  tsdbprobe
    --report           gate_ledger  hook_fire_probe
    --roundtrip        mdstruct  pycodemod
    --rows             fix_sections  mdstruct  query_defs
    --run              agda_census_cli  agda_defs  cacheprofile
    --sandbox          pipeflow  query_defs  sppf_db
    --seed             pycodemod  schema
    --selftest         agda_defs  autocorr_synth  cacheprofile  check_assign_types  check_mode_contracts  check_scratch_independence  check_scratch_runtime  codepoints  collapse_carrier_nesting  conduit_resolve  decompose_rewrite  drop_dead_renames  gate_census  gate_status  hook_fire_probe  make_rules  mdstruct  pipeflow  procstruct  proofcost  prose_apex  pycodemod  qualify_imports  query_defs  resolve_notinscope  rewire_fcr  rewire_stale_module  run_selftests  schema  scope_fix  set1_ratchet_cores  shared_cache  split_inner_module  split_pipeline  sql_lift  swarmclaim  tmi_index  tmi_status  tmi_subject  traceprobe  tsdbprobe  vfs
    --siblings         rewire_fcr  toolmodes
    --since            pycodemod  tsdbprobe
    --sql              pycodemod  query_defs
    --stats            buildtime  transcriptstruct
    --status           enforce_ban  paydown
    --summary          fix_notinscope  make_rules
    --sweep            findings  gen_kat  worklist_gate
    --sync             check_assign_types  gate_census  toolmodes
    --target           make_rules  synth_agda_prototype
    --to               collapse_carrier_nesting  rewire_stale_module
    --top              autocorr_synth  buildtime  proofcost  prose_apex  pycodemod  reuse_check  reuse_sweep  reuse_tui  toolmodes
    --verify           query_defs  split_pipeline  toolmodes  traceprobe  tsdbprobe

── DOCUMENTED, NOT DISPATCHABLE — in a usage line, no matching flag literal
    --apply            seal_defs
    --apply            unseal_defs
    --base             toolmodes
    --list             findings
    --list             gate_status
    --live             reuse_tui
    --max              enforce_ban
    --modes            gate_status
    --module           strip_using
    --peaks            gate_status
    --promotable       check_scratch_independence
    --register         findings
    --restore          recover_presplit
    --scope            check_scratch_independence
    --show             recover_presplit

── A CONVENTION, NOT A PER-TOOL MODE — accepted by every tool, or invoked by a harness
    --apply  --dry-run  --quiet  --roundtrip  --sandbox  --selftest
```
--- END mode-census ---

## What to reach for, by question

- *"who calls this function / is this capability dead?"* → `pycodemod --calls <name>`, `--dead`.
  A name in a docstring is not a call, which is exactly why `grep` fails here: it was how
  `rewire_only` sat with 1 def and 0 calls while three docstrings named it.
- *"which callers pass this flag yet?"* → `pycodemod --forwards <fn> <kw>`. Counting the flag
  *string* reports a caller as migrated when it merely mentions the migration in a comment.
- *"does this document still agree with itself?"* → `uv run mdstruct labels <file>` for the
  label population; a plan-vs-worklist `coherence` mode has NO successor yet — it is mtools' W22,
  held for a fixture pair (substrate W9). Do not reach for the retired in-repo `--coherence`.
- *"what does the bib actually say, vs what the engine reads?"* → `bibstruct --dropped`,
  `--edges`, `--orphans`.
- *"is the metrics store up / what series exist / did my push land?"* → `tsdbprobe.py
  --reachable`, `--names`, `--series`, `--query`, `--verify`. The `--verify` mode carries
  cassian's `query-readback` semantics: read-your-write on a value YOU control, never the
  shared `vm_rows_inserted_total` (which is absent from `/api/v1/query` and global across
  producers — the episode that cost two projects a false verify).
- *"what did the USER actually say, and in which turn?"* → `transcriptstruct.py
  <session.jsonl> --grep-content <regex> --human`. `grep` over the raw file matches the
  JSON-ESCAPED form (a newline is `\n`, an em-dash may be `—`), so a phrase spanning a
  line break is invisible to it — and a byte offset cannot say who said it or which turn it
  was, which is the only thing a transcript is ever asked. `--human` is a distinct query from
  `--role user`: tool_results and `<system-reminder>` injections carry role `user` and are not
  the human.
- *"where does this Agda name live?"* → `agda_defs.py <name>`. It is the name→home authority
  ~19 tools resolve through; a `^name :` scan misses constructors, record fields and
  indented declarations.
- *"what does the tree SAY about X?"* → `agda_defs.py --prose <regex> [<Prefix>]`. `--grep`
  matches definition NAMES; `--prose` reads the COMMENT TEXT, which is the other half of
  every file and where this tree records its measured findings, its retractions and its ⚑
  incident notes.

  ⚑ **This mode exists because SIX research agents independently reported its absence**, each
  falling back to raw grep (flagging it) or missing the fact outright. The sharpest witness is
  the repo's own history: `Axes/Opposite.agda`'s header preserves *"the answer to that is in
  the witness tower"* — the same question a later agent was dispatched to answer, with the
  answer already written down and unreachable by every mode it had. It is now one query:
  `--prose "answer to that is in the witness tower"` returns that line out of 3478 modules.

  It reads exactly what `def_index` discards (it skips any line starting `--`), so the two
  together cover the file instead of leaving a band nothing reads.


⚑⚑⚑ **⟡toolmode-guess-reflex — WHEN YOU DO NOT KNOW THE MODE NAME, ASK. DO NOT GUESS.**

**`toolmodes.py --find <name|description>` answers "which tool has this mode", and the reflex
that skips it costs a call per guess.** MEASURED in one session, all by the same actor, all
non-existent:

    pycodemod --defs · --literals · --enclosing · --modes · --prose <file>
    agda_defs --sigless      ratchet --fallthrough-census      schema --probe (live)

Eight refusals, each printing a multi-KB usage block — so the guess costs CONTEXT as well as a
call, which is the exact cost `toolmodes` was built to remove. Its own docstring records the
first five instances of this reflex and it still fired eight more times.

⚑ **AND THE FAILURE MODE IS NOT "I DID NOT KNOW THE TOOL EXISTED".** `toolmodes --find` was used
correctly several times in the same session, including to locate `run_rounds` and to confirm a
gap was real. The reflex is not ignorance; it is REACHING FOR THE NAME THAT FEELS RIGHT while a
census that answers the question sits one call away — and a plausible name feels like knowledge
in a way that an unfamiliar tool does not.

⚑⚑ **A GUESSED NAME AND A MISSING CAPABILITY ARE INDISTINGUISHABLE FROM THE REFUSAL.** Both
print the usage block. So a guess that misses reads as *"the toolkit cannot do this"* — which is
the toolkit-gap-as-category error the standing rule exists to stop, arrived at by typing rather
than by reasoning. TWICE this session that misreading was one call from being corrected:

- `pipeflow --consumers` (*"which function calls `QB.run(con, '<builder>')`"*) EXISTS and was
  BROKEN by a module split. Three call sites were then guessed by hand — `--ingest-core`,
  `project_ref`, `finalize_db`, all wrong — before `query_defs --touching` gave the structural
  answer. **A broken reader is not a missing capability, and it reads as one.**
- `--literals`, `--enclosing` and `--defs` were all guessed at `pycodemod` while `--sqlname`,
  `--guarded`, `--binding` and `--source` — the modes that actually answer those questions —
  were already declared.

⚑ **THE OPERATIONAL FORM:** before typing a mode you have not run in this session, either run
the tool BARE (its own output is the authority) or `toolmodes --find <what you want>`. Search by
DESCRIPTION, not by the name you expect — the fourth arm matches against ~3,000 documented
function docstrings, so a capability that is a library function rather than a mode is still
found. `literal_flags` was reinvented as `cli_flags` after four name-keyed searches each
returned a true answer and none found it.

⚑ **AND A MISS IS A FINDING TO FILE, NOT A CONCLUSION.** `--find` reporting nothing means *"no
entry carries that spelling"*, never *"no such capability"* — the same distinction `summit
capability` prints in its own refusal. Cross-check with a second spelling before concluding a
gap; two misses on `assert precondition instead of create` and `idempotent-ddl` were filed as
intake asks rather than treated as absence.

## Preconditions that differ per tool — do not assume

- **`pycodemod` is lossless** (libcst). `--roundtrip` is a *gate*: these files are the arc's
  incident log, and a transform that keeps code while dropping ⚑ commentary destroys the more
  valuable half.
- **`mdstruct` is a normalizer** (pandoc). A round-trip is *not* expected to be byte-identical;
  `--roundtrip` reports what changed so you can judge whether any of it is load-bearing.
  Its AST modes need pandoc + panflute — if you hit `ModuleNotFoundError: panflute`, that is a
  missing dependency, **not a broken tool**: run it under `uv run --with panflute python3 …`.
  The text modes (`--items`, `--coherence`, `--superseded`) need neither.
- **`bibstruct` is not a fourth parser.** It reads the file *and* the engine's whitelist and
  reports the difference — `--dropped` is the class of fact the whitelist hides.

Every mode reports `n of m`: a bare list cannot distinguish *no matches* from *no file read*.

## The standing rule this serves

> If you have a question the tooling does not answer directly, **fix the tooling so it answers
> your question.** No complex command lines, no greps, no seds, no judgements not in code.

Needing more than one tooling command, or piping a tool's output through `head`/`tail`/`grep`
to get your answer, is the signal that you are applying reasoning that belongs *in a tool*.
Build the missing mode; do not work around its absence. Reaching past a tool re-derives the
bug the tool was written to prevent — measured repeatedly, including a hand-written regex
that nearly clobbered an unrelated module because `.` matched any character.

**Do not chain shell commands.** No `&&`, no `;`, no `|` into another command, no `for` loop
over files, no command substitution to feed one tool from another. One invocation per shell
call — and if one invocation cannot answer the question, that is the missing mode, not a
reason to compose.

This one is not stylistic and not about elegance: **a chained command cannot be approved in a
way that sticks.** The operator approves tool invocations, and a one-off pipeline is a
one-off approval — so every chain you write is a permission prompt that must be re-granted
the next time, and a capability that never accumulates. A named mode on a tool is approved
once and reusable forever. Composing in the shell converts durable tooling into disposable
keystrokes, which is the same defect as answering by `grep`: the work does not compound.

## For dispatched agents

You start with no session context, so: **run the tool bare first, read its mode list, then
ask your question.** Do not infer a mode from this file.

**You are expected to GROW the tooling, not just use it.** If your question has no mode, add
the mode (or, for an unread artifact kind, the tool) — then use it to answer. That is the
task, not a detour from it. Ship it the way everything else here ships: the capability lands
in the tool that owns the artifact, with a selftest case that FAILS against the code before
your change, so the new mode is guarded rather than merely present.

Two limits on that. If you were dispatched **read-only**, you cannot write the mode — so say
precisely what is missing (question asked / owning tool / missing mode) and stop; do not grep
around it. And if building the mode would exceed your brief, name it and stop rather than
half-build it. A named-but-unbuilt gap is the weak outcome, acceptable only under those two
conditions.

Report findings as *presence with witnesses* (path + line); an empty search is a fact about
your method, not about the repo — say which you mean.
