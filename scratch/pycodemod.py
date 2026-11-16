#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Structural questions about OUR OWN PYTHON TOOLING — the level above the Agda tools.

⚑ THE ASYMMETRY THIS EXISTS TO CLOSE.  This repo mechanizes every edit to `agda/`
and makes NONE to the ~85 tools that perform them: `scratch/*.py` and
`scripts/check_*.py` are edited by hand, one call site at a time.  The same defect
class the Agda tooling was built to prevent therefore keeps recurring in the Python:

  * `split_pipeline.rewire_only()` was written, documented with its own
    354-consumer justification, and left with **ZERO CALLERS** — the dispatch
    branch was never added.  A hand edit forgets the second half.
    ⚑ REPAIRED (measured 2026-08-24 by `--calls rewire_only`): the branch now
    exists at `split_pipeline.py:720` (`if "--rewire-only" in argv`) and carries
    its own comment recording this incident, plus a delegating wrapper at
    `split_unblock.py:52`.  Census today: 2 defs (one a one-line delegator, NOT a
    name collision), 3 calls.
  * FOUR gates route through `ratchet.set_ratchet` and none can enumerate its
    census, while THREE non-family gates each hand-rolled a `--list` block
    separately: one capability, three copies, four omissions.
    ⚑ REPAIRED (measured 2026-08-24 by `--forwards set_ratchet list_keys`):
    **16 of 18** call sites now forward `list_keys`.  The 2 that do not are a
    selftest fixture (`check_divergence_ratchet.py:208`) and `run_selftests.py:1793`
    — neither is a gate enumerating a census, so the population is closed.
  * `agda_files()` once existed as FOUR different bodies under one name, two of
    them feeding pre-commit gates.
    ⚑ REPAIRED (measured 2026-08-25 by `--source agda_files` on each def, and
    `--calls _agda_files`).  A DEF COUNT ALONE READS THIS BACKWARDS: `--calls
    agda_files` reports **5 defs**, up from four, which looks like the incident
    getting worse.  It is the opposite.  One is now THE AUTHORITY
    (`agda_lex.py:636`, parameterised on `root`, `_build`-filtered, memoised) and
    the other four are ONE-LINE DELEGATORS to it — `claim_census.py:57`,
    `paydown.py:67`, `check_carrier_locality.py:128`, `check_claims.py:85`, each
    `return _agda_files(<root>)` and each carrying the incident in its docstring.
    All four resolve to one body: `--calls _agda_files` -> 4 calls, 0 defs.
    ⚑⚑ AND I REPORTED THIS AS "NOT REPAIRED — WORSE" ONE ROUND EARLIER, ON THE DEF
    COUNT ALONE.  Reading 4 -> 5 as regression is the same shape as reading
    `rewire_only`'s 3 calls as adoption: a COUNT over a name, standing in for the
    STRUCTURE under it.  The count went UP because consolidation ADDS a delegator
    per site; the metric moves opposite to the repair.  Open the bodies.

⚑⚑⚑ AND THE THREE BULLETS ABOVE ARE WHY THIS BANNER NOW CARRIES STATUS LINES AT ALL.
Two of them had ROTTED INTO FALSE PRESENT-TENSE CLAIMS — in the docstring of the tool
whose job is finding dead capabilities, `rewire_only` was still cited as having ZERO
CALLERS while `--calls` reported three.  A motivating incident is written once, in the
present tense, and then the tree moves under it; the prose is the one artifact no gate
re-derives.  `fresh-comments-are-hypotheses-too` applies to a tool's own banner, and
the instance that proves it is the banner of the tool built to catch this class.

⚑ THE LESSON IS KEPT AND THE CLAIM IS DATED — never deleted.  Each bullet still states
the defect as it was measured, because the defect is the ARGUMENT for the tool; what is
added is what the same query returns TODAY and the query that returns it.  Deleting a
repaired incident would destroy the justification and leave the tool looking arbitrary;
leaving it undated lets a reader act on a fixed problem.  A repair is residue, not an
erasure — and every status line above names the mode that re-derives it, so the next
reader checks rather than trusts.

**A shared NAME is not a shared authority, and a hand sweep is not a transform.**

⚑ WHAT THIS MODULE DELIBERATELY DOES NOT DO — `python -m libcst.tool` ALREADY OWNS IT.
The reuse-search fired here (user: *"I do notice that the search AI response pointed
at libcst's own CLI"*) and deleted most of a first draft.  The shipped CLI provides:

    python -m libcst.tool codemod -u <mod>.<Class> <paths>   # unified DIFF preview
    python -m libcst.tool codemod -j <N> ...                 # parallelism
    python -m libcst.tool list                               # discover codemods
    python -m libcst.tool print <file>                       # dump the CST

so a `--dry-run`, a worker pool, a file walker and a preview mode would ALL be
re-derived infrastructure — `feedback_fix_infra_not_route_around` exactly (conform
to the tool; do not rebuild its core).  Two of its built-ins are the Python twins
of tools this repo hand-wrote for Agda: `rename.RenameCommand` ≙ `rename_at_source`,
`remove_unused_imports` ≙ `prune_imports`.  **Use those; do not re-implement them.**

What is NOT in the CLI, and is therefore what lives here:
  1. the LOSSLESSNESS precondition for *this* corpus, as a gate; and
  2. the repo-specific structural QUESTIONS (dead capability, call sites),
     which the CLI has no notion of because they are not transforms.

⚑ WHY LOSSLESSNESS IS A GATE AND NOT A PROBE.  These files are the arc's incident
log — nearly every line carries a ⚑ comment recording the measured defect that put
it there.  A transform that keeps code and drops commentary destroys the more
valuable half, so "does parse→emit reproduce this byte-for-byte" must be answerable
for every file before any codemod runs, including files not yet written.  (`libcst`
and not `ast` for the same reason: `ast` discards comments by construction.)

    pycodemod.py --roundtrip [paths]     # LOSSLESSNESS GATE over the tool corpus
    pycodemod.py --calls <name> [paths]  # def/call sites; 0 calls = dead capability
                                         # ⚑⚑ A `--dead` VERDICT IS SCOPE-DIRECTIONAL, AND THE
                                         # NATURAL QUERY IS THE ONE THAT LIES. An API reached
                                         # through an aliased module (`import store as _s`;
                                         # `_s.tenant(...)`) is invisible to a bare-token probe,
                                         # so scoping to the DEFINER reports dead while scoping
                                         # to the CALLERS reports live. MEASURED on the tenant
                                         # resolver: `--calls tenant store.py` → "1 def, 0 calls,
                                         # ⚑ DEAD CAPABILITY"; the same query over sppf_db.py +
                                         # schema_rows.py → "0 def, 7 calls". Same name, same
                                         # tool, opposite verdicts, and the difference is only
                                         # which file you asked about.
                                         # ⚑ THIS REPO DELETES ON `--dead`. A sweep over
                                         # `store.py` would propose removing the function that
                                         # fixes tenant drift, on a census that cannot see its
                                         # own callers. Cross-check with `--aliases` (which
                                         # module is imported under an alias) before acting —
                                         # same two-spelling shape as the `q_<name>` /
                                         # `QB.run("<name>")` warning below, one layer up.
    pycodemod.py --guarded <name> [paths]# WHERE a call SITS, not what it is passed —
                                         # calls to <name> partitioned by the enclosing
                                         # `if` conditions, grouped by condition.  Every
                                         # other reading here answers a question about
                                         # ARGUMENTS; this is the axis that hid a defect
                                         # in a GATE: `edit_snapshot.guard` — the
                                         # mutation-intent guard — has 61 call sites, and
                                         # at `drop_dead_renames.py:143` it sits inside
                                         # `if apply:`.  So the guard that forces an
                                         # operator to STATE intent is reached only after
                                         # intent is stated as apply, and the UNSTATED
                                         # case (the whole population the ratchet
                                         # measures) is the one branch it cannot reach —
                                         # a WRITE guard where a DECISION guard was
                                         # specified.  ⚑ Conditions are SOURCE TEXT:
                                         # "written under this test", never "reachable
                                         # only when true"; `if apply:` and
                                         # `if args.apply:` are different keys, and an
                                         # `else` body is reported under its `if`
                                         # (over-report, never inverted).  Both sides are
                                         # printed so a guarded list cannot read as the
                                         # whole population
    pycodemod.py --placement [paths]     # WHEN a mutation guard FIRES — the OTHER AXIS of
                                         # `--guarded`, and the one that decides whether a
                                         # bare invocation is refused (Ⓐ48).
                                         # ⚑⚑ `--guarded guard` classifies by SOURCE
                                         # POSITION and reports 41 `top` sites; ZERO of
                                         # them refuse a bare invocation, because 30 are
                                         # the `_snapshot_once(path)` idiom — a FIRST-WRITE
                                         # helper a read-only mode, a restoring dry run, or
                                         # a `nothing droppable` run never reaches.  Source
                                         # position is the HOLDER; execution order is the
                                         # WORKER, and a census keyed on the holder scores
                                         # the two identically.
                                         # Four verdicts, PER TOOL (a tool legitimately
                                         # does both, and a per-site census would report
                                         # the paid-down tool as an offender — the false
                                         # positive `intent_census` records):
                                         #   entry       reached unconditionally on a bare
                                         #               invocation — REFUSES
                                         #   dispatched  written, but some mode reaches the
                                         #               body without it
                                         #   first-write consulted only at a pending write
                                         #   unguarded   no recognised form called
                                         # ⚑ NOT A FOURTH SPELLING.  `--guarded` reads
                                         # position, `check_snapshot_guard.intent_census`
                                         # reads whether the contract is NAMED, and
                                         # `require_at_entry` IS the runtime authority.
                                         # This asks the question none of them asks — is it
                                         # REACHED — and consumes `--guarded`'s own visitor
                                         # output rather than re-walking.
                                         # ⚑ IT PRINTS WHAT IT CANNOT DECIDE at the
                                         # verdict, not only in a docstring: a two-hop
                                         # helper, a runtime-computed condition, an
                                         # import-side-effect path, and whether a tool NEEDS
                                         # a guard at all (placement, never necessity)
    pycodemod.py --aliases [paths]       # THE BARE-IMPORT BAN, by FORM — the `.py` twin of
                                         # `agda_defs --qualified`.  `from x import y` is what
                                         # lacking a bare import looks like in python: it
                                         # SELECTS names out of a module and binds them where
                                         # the definition site carries `x.y` (agda's `using`).
                                         # So `import x` is the only compliant form, graded
                                         # BARE / AS-MOD / FROM / FROM-AS / FROM-STAR /
                                         # RELATIVE.  ⚑ SCOPE IS A COLUMN, NOT AN EXCUSE: the
                                         # ban extends into function bodies for the `from`
                                         # shapes, while a func-scoped `import x` stays
                                         # COMPLIANT — so the deferred sites (cycle-breaks,
                                         # lazy deps) are re-expressed, never deleted.
                                         # `--all` includes foreign modules; `--sites` lists
                                         # the violations
    pycodemod.py --collisions [paths]    # every name with 2+ REIMPLEMENTING defs, PARTITIONED
                                         # BY WHAT RESOLVES IT — `local` (one file; python
                                         # scopes them apart), `sibling` (one directory; a
                                         # candidate lift or a real per-file entry point), and
                                         # `crossing` (different trees — ONE NAME, TWO
                                         # CONTRACTS, the class that bit).  ⚑ DELEGATING
                                         # WRAPPERS DO NOT COLLIDE: four one-liners around one
                                         # authority are a CONVERGED family, and counting
                                         # `def` sites finds the defect and its repair without
                                         # telling them apart.  `--kind K` selects one part
                                         # (an unknown kind REFUSES); `--sites` lists them
    pycodemod.py --ambient [paths]       # ⟡ambient-root — WHAT DEPENDS ON AMBIENT CWD, as
                                         # ONE query.  ⚑⚑ A PROPERTY census, not a name
                                         # census, and that is the whole point: ambient-cwd
                                         # dependence was tracked by `--calls getcwd` (20
                                         # sites), while `os.path.exists(mod.replace(".","/")
                                         # + ".agda")` is the SAME dependence under a
                                         # different name and calls no `getcwd` at all.
                                         # `--calls exists` (153) is not a bound either —
                                         # `open`/`listdir`/`glob`/`Path`/`subprocess` are
                                         # further spellings again.  No name-keyed census can
                                         # bound the union, so the predicate is two-part: a
                                         # path-RESOLVING callee (5 families) whose path
                                         # argument is UNANCHORED (not absolute, not flowing
                                         # from a root name, not joined onto one).
                                         # ⚑ CLASSIFIED, NOT JUST COUNTED — SCOPED (the
                                         # directory IS the question; a FEATURE) / REPO (a
                                         # repo-relative path resolved ambiently; the DEFECT
                                         # class) / UNKNOWN (the classifier's honest
                                         # boundary, folded into NEITHER) / MUTATES (an
                                         # `os.chdir`, which alters the thing under study).
                                         # ⚑ THE COUNT IS A FLOOR AND THE MODE SAYS SO:
                                         # `--misses` prints the 7 DECLARED blind spots (a
                                         # census cannot derive its own).  `--sites` lists
                                         # rows; `--verdict REPO` selects one class
    pycodemod.py --swallows [paths]      # every `except` that DISCARDS the exception —
                                         # a handler whose whole body is `continue`/`pass`
                                         # /bare `return`, split bare-except / broad
                                         # (`except Exception`) / narrow.  ⚑ A POPULATION,
                                         # NOT A DEFECT LIST: one unparseable file must not
                                         # abort a corpus query, so the swallow is usually
                                         # right.  What is never right is a swallow with NO
                                         # ACCOUNTING — the population silently shrinks and
                                         # no number says so.  Measured 2026-08-18: a
                                         # `NameError` in a visitor, swallowed per-file,
                                         # made EVERY `--calls` query answer `0 def, 0
                                         # call, 0 ref` and `--dead` read GREEN on a file
                                         # with 18 defs — the census this repo DELETES on.
                                         # ⚑ Exists because `continue`/`pass` are
                                         # STATEMENTS: `--guarded continue` returns `0 of
                                         # 0`, a fact about the METHOD (a call-site reader
                                         # cannot see a statement) that reads as a fact
                                         # about the code.  Corpus today: 244 sites — 3
                                         # bare-except, 88 broad, 153 narrow
    pycodemod.py --exits [paths]         # ⟡exit-and-swallow — PROCESS-EXIT OWNERSHIP, and
                                         # the `--swallows` question from the OTHER SIDE.
                                         # `SystemExit` derives from `BaseException`, NOT
                                         # `Exception`, so `except Exception` FAILS OPEN on
                                         # an exit while bare `except:` FAILS CLOSED on it —
                                         # both wrong, and which you get turns on a
                                         # distinction nobody writing the handler had in
                                         # mind.  Three lenses in ONE dispatch because they
                                         # answer each other:  EXIT SITES classified
                                         # LIBRARY / dispatch / main-only / hard (a raw
                                         # `sys.exit` count is useless — the population is
                                         # mostly a CLI legitimately exiting its own
                                         # process; the DEFECT is an exit in a def another
                                         # module IMPORTS, since no script owns the pid);
                                         # HANDLERS that catch SystemExit (`bare-except` /
                                         # `base` / `named`, where `named` is deliberate BY
                                         # CONSTRUCTION and never a defect — the spelling IS
                                         # the accounting, which is why no carve-out list is
                                         # needed); and INTERLOCK, the census neither half
                                         # sees: an `except Exception` guarding a call that
                                         # reaches an exit, so the site LOOKS defended and
                                         # is not.  ⚑ `raise SystemExit` is counted beside
                                         # `sys.exit` — auditing one spelling is the
                                         # `--calls emit` / `_emit_one` defect again.
                                         # ⚑⚑ The LIBRARY join is DEF-LEVEL, not module-
                                         # level: the coarse version reported 174, of which
                                         # 130 were `pycodemod._dispatch` (7 importers, none
                                         # naming it).  Corpus today over scratch/ scripts/
                                         # jea/: 844 exits (18 LIBRARY, 206 dispatch, 620
                                         # main-only), 34 SystemExit-catchers, 36 interlock
                                         # sites — 25 of them the copy-pasted
                                         # `_snapshot_once()` idiom
    pycodemod.py --check-contracts       # GATE: every mode declaring `scans=True` in
                                         # `MODES` must call `_report_skipped()`.  The
                                         # `Arm`/`Convention` model applied to BEHAVIOUR
                                         # rather than argument shape — `Mode` declared
                                         # operand/paths/opts and nothing about what a
                                         # branch OWES, so cross-cutting properties were
                                         # hand-threaded through ~20 dispatch branches.
                                         # Measured cost: a visitor defect emptied
                                         # `scan()`, every `--calls` answered `0 def, 0
                                         # call, 0 ref`, and `--dead` — what this repo
                                         # DELETES on — read GREEN on a file with 18
                                         # defs.  Fixing it meant editing two branches by
                                         # hand with nothing saying the other eighteen
                                         # needed it.  Declared and FALSIFIABLE: flip a
                                         # mode to `scans=True` without the call and this
                                         # exits 1 naming it (verified).  An empty roster
                                         # exits 2 — zero contracts and zero violations
                                         # must not render alike.
    pycodemod.py --dead [paths]          # every def in the corpus with no caller
    pycodemod.py --artifacts [paths]     # which tools READ build artifacts, split
                                         # by whether the artifact can carry a
                                         # FAILURE — a tool reading failure records
                                         # emits commit-blockers by construction
    pycodemod.py --forwards <name> <kw>  # which callers pass <kw>, which DO NOT
    pycodemod.py --asserted <name> <kw>  # of those, which pass a LITERAL vs a
                                         # COMPUTED value — presence is not
                                         # measurement, and a size that cannot
                                         # vary is a boolean typed as an integer
    pycodemod.py --values <name> <kw>    # of those, WHICH literal — grouped by the
                                         # constant each caller wrote.  The third
                                         # member of the family, and the one that
                                         # answers "is this call DANGEROUS":
                                         # `sandbox_connect(reset=…)` has 23 sites,
                                         # `--asserted` says "23 of 23 LITERAL", and
                                         # `reset=True` DROPS EVERY RELATION in the
                                         # tenant.  A non-literal reports UNKNOWN —
                                         # never a guessed value
    pycodemod.py --sqlname <query> [paths]# a REGISTERED QUERY's definition and its
                                         # references.  The store defines `def q_<name>`
                                         # and invokes `QB.run(con, "<name>")`, so the two
                                         # spellings NEVER MEET: `--calls q_obs_core`
                                         # reports `1 def, 0 calls, ⚑ DEAD CAPABILITY` on
                                         # a query `sppf_db.py:1023` runs every fold.
                                         # Every registered query is therefore a FALSE
                                         # POSITIVE in `--dead` — the census this repo
                                         # uses to decide what to delete.  Takes either
                                         # spelling (`obs_core` or `q_obs_core`), because
                                         # a reader arriving from a traceback has the
                                         # string and one arriving from source has the def
    pycodemod.py --binding <name> [paths]# where a name is BOUND and where it is LIVE
    pycodemod.py --types [paths]         # mypy census, keyed error-code::file
    pycodemod.py --attr <name> [paths]   # ATTRIBUTE reads `.name` — what a field
                                         # rename must reach; invisible to --binding
    pycodemod.py --attr <Recv>.* [paths] # the INVERSE: every attribute reached off the
                                         # bare receiver NAME <Recv>.  `--attr leaf` is
                                         # deliberately receiver-blind (an arbitrary
                                         # receiver expression is not decidable), but a
                                         # receiver written as a bare name IS — so
                                         # "what does `import scope_fix as SF` actually
                                         # reach for" is exact, and was the question a
                                         # module SPLIT could not otherwise answer
    pycodemod.py --importers <module>    # every file that IMPORTS <module>, with the
                                         # NAMES it binds — the population `--imports`
                                         # only counts (`6 file(s)`, one example) and
                                         # `--attr <Recv>.*` cannot see at all, because
                                         # `from m import q_x` reads no attribute.  The
                                         # `_`-prefixed names are reported separately:
                                         # those are exactly what a `import *`
                                         # re-export drops while the suites stay green
    pycodemod.py --projects              # every paperkit PROJECT in the corpus
                                         # (a dir with paper.toml), its warrants
                                         # and which of them are FOREIGN bibs
    pycodemod.py --source <name> [paths] # the SOURCE TEXT of a def/class, CST
                                         # extents — reading a body inside a
                                         # scope (--archive) that has no path
    pycodemod.py --sql <ident> [paths]   # SQL LITERALS mentioning <ident>, split
                                         # by STYLE: raw `con.execute("...")` vs
                                         # the compiled-builder layer.  A SQL
                                         # string inside a .py was structured
                                         # text this tool could not parse, so
                                         # "is this relation already a table,
                                         # and does anything query it
                                         # recursively" took three probes and
                                         # still answered `0 of 750` — a fact
                                         # about --key's mode, not the repo
    pycodemod.py --relname [<rel>] [paths]
                                         # where <rel> is used AS A RELATION — in a SQL
                                         # GRAMMAR POSITION (FROM / JOIN / INSERT INTO /
                                         # UPDATE / CREATE|DROP TABLE|VIEW), role `sql`,
                                         # plus string literals EXACTLY equal to it, role
                                         # `name` (the `_T("node", …)` shim spelling that
                                         # carries no SQL at all).  `--sql` and `--literal`
                                         # are both SUBSTRING: `--sql node` returns 82
                                         # sites almost all of which are `node_child` /
                                         # `obs_node` / `orbit_node`, and discarding those
                                         # by eye is the judgement that belongs in a
                                         # program.  CTEs and table FUNCTIONS are excluded
                                         # structurally.  With NO <rel> it censuses every
                                         # relation the corpus references — the form a
                                         # REMOVAL needs, since "is it gone" cannot be
                                         # asked by naming the name you expect to be absent
    pycodemod.py --snapshots [paths]     # ONE VALUE BUILT FROM SEVERAL WORLD-STATES: ≥2
                                         # store reads inside ONE expression, so the reads
                                         # cannot be concurrent and the value is a composite
                                         # of distinct instants (`return (scalar(a),
                                         # scalar(b), scalar(c))` — a store state that never
                                         # existed).  Reports `sequential` (≥2 reads in a
                                         # function, different statements) SEPARATELY and
                                         # never in the headline: a loop reading once per
                                         # core is correct, and collapsing the two would
                                         # report correct code as broken.  `--calls scalar`
                                         # cannot answer it — it has no enclosing scope
    pycodemod.py --key <string> [paths]  # STRING-KEY reads `d["k"]`/`.get("k")`/
                                         # `"k" in d`, split from the schema
                                         # DECLARATION — the dict-shaped record's
                                         # `--attr`, invisible to --attr/--binding
    pycodemod.py --literal <text> [paths]# every STRING LITERAL whose VALUE contains
                                         # <text>, split by ROLE: `compare` (the
                                         # branch that dispatches on it) / `arg` /
                                         # `decl` / `other` / `doc`.  `--key` asks
                                         # about a string used as a dict KEY; this
                                         # asks about a string used as a VALUE, which
                                         # is what a retired enum member is — and
                                         # what `back == "sqlite"` is.  Written for
                                         # the sqlite→postgres drop: "which sites
                                         # still NAME the retired backend" had no
                                         # mode, and grep cannot separate the four
                                         # dispatch sites from the 60 ⚑ notes that
                                         # explain why they exist
    pycodemod.py --rivals <name> [paths] # per def: REIMPLEMENTS or DELEGATES —
                                         # a duplicated NAME is not a duplicated BODY
    pycodemod.py --collision-apex [paths]# ⟡apex-over-collisions — `--rivals`' thesis applied
                                         # to the WHOLE collision census at once, keyed on BODY
                                         # STRUCTURE and graded by sharing-breadth.
                                         # ⚑ `--collisions` GROUPS BY SPELLING and never opens
                                         # a body (`by_name.setdefault(name, ...)`), so its 239
                                         # rows cannot be RANKED: 78 defs named `check` and 6
                                         # named `alphabet_size` are the same kind of row to
                                         # it.  That is `census-keyed-on-one-spelling` a third
                                         # time, and the other key already existed —
                                         # `jea_extrude_ir.templatize` groups units by
                                         # `full_skeleton` and returns the HOLE COUNT, so
                                         # IDENTICAL (0 holes) vs a 12-hole coincidence is a
                                         # COMPUTED verdict where the alternative was a
                                         # judgement in the turn.
                                         # ⚑ THE BANDS ARE `catalog/memory/synth_apex.py`'s —
                                         # universal / broad / pairwise-residue — because the
                                         # question is the same one that tool grades: how
                                         # broadly is this structure corroborated.  A candidate
                                         # witnessed twice is residue; one witnessed 78 times
                                         # is a skeleton.
                                         # ⚑ `nskel > 1` IS A BRIDGE, NOT A LIFT: several
                                         # contracts sharing a spelling, reported rather than
                                         # resolved (the fragment-gate `cluster_memories`
                                         # applies with its MARGIN test).  And `no-shared-
                                         # skeleton` is NOT `IDENTICAL` — None means no two
                                         # sites shared a skeleton at all, the WEAKEST result,
                                         # while 0 means byte-identical structure, the
                                         # strongest; collapsing them inverts the verdict
    pycodemod.py --available <module>... # is this library importable HERE, and which
                                         # one — the reuse-search's first question
    pycodemod.py --archive <t.tar.gz>    # defs inside an archive, WITHOUT extracting —
                                         # reading a reference implementation

⚑ THIS LIST WAS SEVEN MODES SHORT, AND THE OMISSION DEFEATED THE RULE THAT POINTS AT IT.
The struct-tools skill says "run the tool bare and read its mode list — THAT output is the
authority", and a dispatched agent following that instruction correctly reported modes as
absent that `_dispatch` implements.  A stale index is worse than no index here: it is the
one artifact a reader is told to trust.  Backfilled and verified by running each:

    pycodemod.py --state [paths]         # process-local CACHES vs accumulators vs const
                                         # tables — module-scope mutable state, and the
                                         # ONLY mode that distinguishes module scope from
                                         # a function body (see the FunctionDef walk)
    pycodemod.py --diagnose [paths]      # why a file failed to parse, per file
    pycodemod.py --crossings [paths]     # imports that cross a declared boundary
    pycodemod.py --rawreads [paths]      # raw `con.execute` reads vs the builder layer
    pycodemod.py --relalg [paths]        # RELATIONAL ALGEBRA performed in Python over rows
                                         # the store returned — join / group-by / filter /
                                         # sort / set-op / distinct, ranked BY FUNCTION
                                         # (the migration unit).  `--rawreads` asks whether
                                         # a row's SHAPE survives the driver, one call site
                                         # at a time; this asks what the enclosing function
                                         # DOES to the rows, which is the defect
                                         # `schema.lifecycle_census`'s docstring names and
                                         # `schema.reclaim` then committed anyway
    pycodemod.py --control [paths] [--summary]
                                         # EVERY PIECE OF CONTROL FLOW, TYPED by what the
                                         # engine could take it as.  Ladder logic has none:
                                         # a rung's predicate IS the WHERE, so control flow
                                         # is the MEASURE OF WORK NOT YET MOVED to SQL.
                                         # Kinds: row-iteration / row-branch / mode-branch /
                                         # external (the ε boundary, irreducible) /
                                         # early-exit (break/continue/return inside a loop —
                                         # ordering dependencies, printed AGAIN separately)
                                         # / unclassified.  The headline is the RATIO
                                         # external : everything-else, not a total.
                                         # NOT `--relalg` deeper: that mode gates on the
                                         # function reading the store and, by its own
                                         # module docstring, CANNOT SEE A LOOP WITH AN
                                         # EARLY BREAK — the class whose canonical witness
                                         # (`_unreflected_floor`) is now RETIRED, 0 defs /
                                         # 0 calls, while 45 siblings remain.  The `sqlform`
                                         # column is allowed to say `unknown`; a plausible
                                         # guess there is noise that reads like analysis.
    pycodemod.py --control <paths> --kind <K>
                                         # narrow to ONE kind.  An unknown kind REFUSES
                                         # rather than reporting an empty table, which
                                         # would read exactly like "this corpus has no
                                         # control flow of that kind".
    pycodemod.py --control <paths> --constructs
                                         # the construct ROSTER with its counts, INCLUDING
                                         # THE ZEROES — "the corpus does not use this form"
                                         # and "the walker stopped seeing it" are different
                                         # facts, and only the zero rows keep them apart.
    pycodemod.py --fingerprint [paths]   # A PRIME PER DISTINCT REFERENT, and the
                                         # REMAINDER IS THE FINDING.  `--control` types
                                         # every site and leaves 1,130 of 2,034
                                         # `unclassified` — an undifferentiated pile with
                                         # no ordering, no grouping and no progress
                                         # metric, so nothing can say which sites matter,
                                         # which are related, or whether attacking them
                                         # is working.  This gives that pile structure
                                         # WITHOUT CLASSIFYING ANYTHING: each referent a
                                         # site's governing expression mentions (a
                                         # relation, a column, a callee, a bound name)
                                         # gets a prime — asserting only that it is
                                         # DISTINCT AND COUNTABLE, never what it IS — and
                                         # the site's fingerprint is the product.  Then
                                         # `gcd` is shared structure and `%` is
                                         # containment, so *is A inside B* is ONE MODULO
                                         # with nothing decoded.  Decoding against the
                                         # referents we already model (`schema_decl.py`,
                                         # `query_decl.py`; `--seed` widens it) returns
                                         # the keys you understand AND AN EXACT INTEGER
                                         # REMAINDER for the ones you do not.  ⚑ The
                                         # rigid mode is one keyword away and is OFF: a
                                         # system that survives unknown fill is one whose
                                         # DEFAULT returns a remainder rather than
                                         # raising.  Σ Ω(remainder) is a MONOTONE
                                         # progress metric — growing the modelled set can
                                         # only remove factors, so it falls and cannot
                                         # rise.  Lifted from gabion's
                                         # `type_fingerprints.py`; the code is NOT
                                         # imported and its four-name seed is left behind.
    pycodemod.py --fingerprint --from <entry.py>
                                         # scope the population to the TRANSITIVE LOCAL
                                         # IMPORT CLOSURE of an entry point, rather than a
                                         # path list typed by hand.  `toolmodes --find
                                         # closure` reports `--closure` on `agda_defs` and
                                         # "⚑ NOT on: scratch/pycodemod.py" — so the
                                         # population every control-flow count is quoted
                                         # over ("the SPPF import closure, 22 files") could
                                         # be NAMED and not COMPUTED, and a population that
                                         # exists only in a sentence is not reproducible.
    pycodemod.py --fingerprint <paths> --kind <K>
                                         # narrow to ONE control-flow kind — `unclassified`
                                         # is the 1,130 this mode exists for.  An unknown
                                         # kind REFUSES, as `--control`'s does.
    pycodemod.py --fingerprint <paths> --top <N>
                                         # how many rows of the residual ordering to print
                                         # (`--top 0` suppresses it).
    pycodemod.py --fingerprint <paths> --keys <N>
                                         # which MODELLED referents are doing the
                                         # explaining, with their site counts.  The seed is
                                         # deliberately WIDE — a token like `select` enters
                                         # it because the declaration mentions it — so the
                                         # over-credit has to be READABLE rather than
                                         # argued about; narrowing it by hand would take a
                                         # rule about which referents "really" count, i.e.
                                         # the taxonomy this mode exists to avoid.
    pycodemod.py --fingerprint <paths> --seed <a.py,b.py>
                                         # WIDEN the modelled set with more authority
                                         # files.  This is how the metric is driven down:
                                         # paying down the remainder is modelling more
                                         # referents, and nothing else moves it.
    pycodemod.py --fingerprint <paths> --monotone
                                         # the seed LADDER, as ONE command: Ω / bits /
                                         # explained-% at each rung, PLUS the per-site
                                         # divisibility `r_wider | r_narrower` that makes
                                         # the fall a law rather than an observation.  ⚑ A
                                         # FALLING TOTAL IS NOT THE PROOF — two totals can
                                         # both fall while individual sites move the wrong
                                         # way — and running the census three times to
                                         # compare by eye is the judgement-in-the-turn
                                         # shape: it evaporates when the session ends.
    pycodemod.py --fingerprint <paths> --groups N
                                         # the gcd CLASSES: sites sharing UNKNOWN
                                         # structure, attackable together BEFORE either is
                                         # understood.  A bare residual ordering is half
                                         # the value — it says which site is least
                                         # understood and nothing about which sites are the
                                         # SAME problem.
    pycodemod.py --portable [paths]      # SQL that will NOT bind on postgres, by
                                         # EXPLAIN against the sandbox — a real gate.
                                         # ⚑ RAW LITERALS ONLY: a Core-built statement is
                                         # never a string, so this reads GREEN over
                                         # `func.group_concat` — use --funcnames for that half
    pycodemod.py --funcnames [paths]     # every SQLAlchemy `func.<name>(...)`, graded
                                         # `generic` (SQLAlchemy owns the per-dialect
                                         # spelling — genuinely ports for free) vs `verbatim`
                                         # (passed through UNCHANGED, so dialect-SPECIFIC and
                                         # unchecked by Core).  ⚑ THE VERDICT IS "UNVERIFIED
                                         # BY CORE", NEVER "WRONG": measured, an INVENTED name
                                         # compiles identically on postgres and sqlite, and
                                         # `string_agg` (valid postgres) sits in the same
                                         # bucket as the invented one — SQLAlchemy has ONE
                                         # registry (52 names) and no per-dialect list, so a
                                         # mode claiming "does not exist" would invent a
                                         # verdict.  This is the half `store.py`'s
                                         # "Core is dialect-agnostic" guarantee does not
                                         # reach, and it is where `group_concat` hid
    pycodemod.py --funcnames --verbatim  # only the unchecked ones — a migration's work-list
    pycodemod.py --shape / --shape-all   # the record shape a dict-keyed reader assumes
    pycodemod.py --discards [paths]      # computed-then-thrown-away values
    pycodemod.py --reifies [paths]       # defs that RETURN A MATERIALIZED COLLECTION — the
                                         # set/dict/list a STREAM would serve.  ⚑ The row
                                         # that matters is `returns-sorted`: a def that sorts
                                         # and returns has PAID for an order and then dropped
                                         # the fact, so callers re-sort defensively.  That
                                         # double payment is witnessed one hop apart in this
                                         # corpus — `agda_defs.import_index()` sorts at :1732
                                         # and SAYS SO in its docstring, and `importers_of()`
                                         # re-sorts at :1757 anyway, because there was nowhere
                                         # on the VALUE to put the claim.
                                         # `jea/metalanguage/sorted_stream.py` is where it
                                         # goes: `Sorted(it, key, origin)` carries the order,
                                         # and its combinators REFUSE rather than re-sort.
                                         # ⚑ REPORTS A SHAPE, NEVER A VERDICT — a reification
                                         # is not a defect (somebody must pay the sort once,
                                         # at a named producer); the census finds where it is
                                         # paid MORE THAN ONCE along a chain
    pycodemod.py --reifies --sorted      # narrow to one kind: --set/--dict/--list/--sorted/
                                         # --accum
    pycodemod.py --resorts [paths]       # the CONSUMER arm of --reifies: a `sorted(f(...))`
                                         # whose callee `f` is itself in the returns-sorted
                                         # census — the SAME order paid for twice.  ⚑ A SPAN
                                         # QUERY, not a site query: "is this sort redundant"
                                         # is a property of the PAIR (producer, consumer), so
                                         # no per-site predicate can answer it — which is why
                                         # it could not be a column on --reifies.  Reports
                                         # re-keyed sorts SEPARATELY and never as debt: a
                                         # `key=`/`reverse=` is a different order and real
                                         # work (I misread `swallows()` that way and the
                                         # split is what caught it)
    pycodemod.py --layout [paths]        # every TOP-LEVEL def/class/stmt of a module with
                                         # its line extent and code size, in source order —
                                         # the mode `--size` needed and did not have: the
                                         # census named a file too big to edit and then
                                         # left WHERE-does-it-cut to `grep '^def '`
    pycodemod.py --size [paths]          # modules too large to READ WHOLE before editing,
                                         # and modules with MORE THAN ONE `__main__` guard —
                                         # the defect that made a mid-file entry point
                                         # unfindable in a 2800-line file
    pycodemod.py --commentary [paths]    # the ⚑ INCIDENT LOG census: how many marker lines
                                         # each module carries, and which texts are DUPLICATED.
                                         # The preservation gate for a SPLIT, which
                                         # `--roundtrip` structurally cannot be: losslessness
                                         # is per-file, and a decomposition is precisely the
                                         # transform that moves a line to a different file —
                                         # so both halves round-trip green while a ⚑ block
                                         # that explained a moved def is silently gone.
    pycodemod.py --commentary [paths] --blocks
                                         # the INCIDENT-BLOCK reader: each ⚑ paragraph as ONE
                                         # record, with its LINE SPAN, the def or class that
                                         # ENCLOSES it, and the backticked SYMBOLS it cites —
                                         # then a tail of every symbol cited from more than one
                                         # file.  ⚑ THE LINE IS NOT THE UNIT OF AN INCIDENT and
                                         # every other reader here splits one: `--lines` is
                                         # line-granular, and a continuation line carries no ⚑
                                         # by construction, so a five-line incident reports as
                                         # its first line and the other four are invisible to a
                                         # mark-keyed census entirely.  ⚑⚑ AND THE CITED SYMBOL
                                         # IS THE EDGE FROM A DEFECT TO ITS REMEDY.  This corpus
                                         # writes the incident and the fix in one paragraph
                                         # (*"`--roundtrip` GUARDS THE WRONG BOUNDARY … the
                                         # preservation question is a SET question"* names both
                                         # the inadequate tool and the adequate one), so the
                                         # join from a recurring shape to the mode that already
                                         # handles it was present in 10,958 lines of prose and
                                         # reachable by no query.  `prose_apex` clusters these
                                         # by PARAPHRASE and therefore finds restated CONVENTION
                                         # ("act, state intent, snapshot" — 19 files correctly
                                         # saying the same true thing); this finds shared
                                         # CITATION, which is the other half and does not
                                         # require the sentences to resemble each other.
    pycodemod.py --commentary <paths> --since <ref>
                                         # the GATE form: name the original AND every sibling
                                         # the split created, and it reports which ⚑ TEXTS
                                         # were in `<ref>` and are in none of them now (exit 1).
                                         # `<ref>` defaults to `:` — the INDEX, i.e. "before I
                                         # started" in a working tree; `HEAD` is wrong for a
                                         # staged-added file, which reads as an empty baseline
                                         # and so measures nothing.  A bare total cannot be the
                                         # gate: a split that drops one note and adds another
                                         # keeps the total.  Each LOST line names its origin
                                         # file, because a ref that predates OTHER uncommitted
                                         # work will report that work's removals here too.
    pycodemod.py --commentary <paths> --marks <s>
                                         # widen the mark set (comma-separated).  `--marks ''`
                                         # makes EVERY line a marker line, which turns the
                                         # `--since` gate into a total preservation gate — the
                                         # form a corpus with no ⚑ glyph needs, and the one a
                                         # SPLIT wants: a relocation must lose no line at all,
                                         # not merely no flagged line.  The census function
                                         # always took this; only the CLI froze it, which is the
                                         # hardcoded-vocabulary defect one level up.
    pycodemod.py --split <file> [--max N] [--max-defs N] [--prefix P] [--keep a,b]
                                 [--export all|public|a,b] [--apply]
                                         # PERFORM the cut `--size` demands and `--layout`
                                         # locates: pack the top-level statements into SIBLING
                                         # modules under a per-file line bound, byte-identically.
                                         # Siblings and not a subpackage BY NECESSITY — a body
                                         # reading `Path(__file__).resolve().parent` is asking
                                         # which DIRECTORY it is in, and a subpackage silently
                                         # re-answers it.  Parts are packed out of a TOPOLOGICAL
                                         # order of the statements, so the sibling imports are
                                         # acyclic by construction and a cyclic source is a
                                         # refusal naming the SCC rather than an import-time
                                         # crash.  Reports, and refuses to write, unless every
                                         # relocated statement is reproduced byte-for-byte;
                                         # statements reading `__file__` as SOURCE TEXT are
                                         # named as HAZARDS, because after a split such a scan
                                         # SHRINKS and still passes.  `--apply` writes.
                                         # `--max-defs` is a SECOND, INDEPENDENT bound that
                                         # composes with `--max`: the count of top-level
                                         # definitions per part.  It exists because that is the
                                         # quantity an ADDITION's blast radius scales with — a Δ
                                         # grade cache keys each check on a hash of the module's
                                         # sorted qualname SET, so adding one definition
                                         # invalidates EVERY reader of that module while editing
                                         # one body invalidates only the check sensitive to it.
                                         # N definitions is therefore N× the blast radius, and a
                                         # LINE bound cannot see it: measured on gcalculus,
                                         # `concepts_05.py` holds 8 defs in 143 lines and is
                                         # fully line-compliant, while a 1156-line 8-def module
                                         # (one 316-line body) is the mirror case.  Neither
                                         # bound subsumes the other, so a part satisfies BOTH.

⚑ AND A MODE THIS TOOL DOES NOT YET HAVE, recorded here rather than in a plan file because
this docstring is where the next reader looks: **`--import-cost`** — which modules do
expensive work merely by being imported.  `run_selftests` imports every module defining
`_selftest` (59 today), so import-time work is paid by every suite run.  `--calls` cannot
answer it: its `_Scan` visitor records call sites with NO scope tracking, so a module-level
`build_index()` and one inside `def main()` are indistinguishable.  `--state` already walks
`tree.body` and already separates module scope from function bodies, and its own docstring
names the phenomenon as noise it had to suppress ("every script whose whole body runs at
import") — so the mode is a SIBLING of `--state`, not a new instrument.
"""
# ⚑ `ast` ALONGSIDE `libcst`, AND THE DIVISION IS PRINCIPLED.  This module argues
# at length for libcst over ast — because `ast` DISCARDS COMMENTS, and these files
# are the arc's incident log, so any REWRITE must be lossless.  A read-only SCOPE
# query has no such requirement: it asks where a name is bound, never reproduces
# the source.  Using the heavier tool for the lighter question would be reaching
# past the stdlib for nothing; using `ast` to rewrite would destroy the ⚑ comments.
import ast
import functools
import inspect
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import libcst as cst
    # ⚑ EXPLICIT SUBMODULE IMPORT — mypy reported `Module has no attribute
    # "metadata"` on `cst.metadata.PositionProvider`, and it was RIGHT about the
    # import graph even though the attribute exists at runtime: `libcst.metadata`
    # is a submodule, populated only when something imports it.  The code worked
    # because `libcst/__init__.py` happens to pull it in transitively — i.e. it
    # depended on an implementation detail of a third-party package.  Importing it
    # by name is the fix, not a suppression comment.
    import libcst.metadata  # noqa: F401
except ImportError:  # pragma: no cover - environment probe
    cst = None

# ⚑ THIS FILE REMAINS THE ENTRY POINT, THE MODE INDEX AND THE PUBLIC API — the
# split moved BODIES, not the surface.  Other tools do `import pycodemod` and
# reach for `py_files` (3 external call sites, measured by `--calls py_files`:
# `shared_cache.py`, `check_mypy_ratchet.py`, `check_scratch_independence.py`),
# and `run_selftests.py` discovers this module by finding a def named
# `_selftest`.  Re-exporting is therefore not tidiness, it is the contract.
#
# ⚑ AND `ROOT` IS RE-EXPORTED AS A MODULE ATTRIBUTE, NOT COPIED.  `corpus`
# rebinds `_pycodemod_core.ROOT` at runtime so `--archive` / `--in` swap the
# corpus under every mode at once.  A plain `from _pycodemod_core import ROOT`
# here would freeze a snapshot, and the envelope would go inert while still
# reporting success — the silent wrong-corpus read.  Code in THIS file that
# needs the live value reads `_c.ROOT`; the module-level name below exists only
# so an external `pycodemod.ROOT` still resolves.
import _pycodemod_core as _c
from _pycodemod_core import (  # noqa: F401,E402
    DISCARD_LEDGER, _GENERATED_DIRS, _SKIP_DIRS, _roots, _shape_of, _value_of,
    UNKNOWN, PopulationError, corpus, escapes, flagged_argv, operand_tail,
    package_root, py_files, roundtrip, _per_file,
)
# ⚑ `_DERIVER` / `_SCHEMA` / `_PARSE_CACHE` / `_ignore_cache` ARE IMPORTED BACK,
# AND THAT IS A SEAM CORRECTION RECORDED RATHER THAN HIDDEN.  The first cut moved
# them with the censuses because they LOOK like census memo tables; `--calls`
# then showed `_cached_defs` (which stayed) is their only consumer, and the
# selftest failed with `NameError: _DERIVER`.  A memo separated from the sole
# thing that reads it is exactly the shape `--state` exists to detect, so the
# grouping was wrong, not the code.  They are re-imported here rather than moved
# back so the cache-invalidation reasoning in their ⚑ blocks stays in one file.
# ⚑ `_selftest` IS RE-EXPORTED, AND THAT IS A HARD CONTRACT, NOT TIDINESS.
# `scripts/run_selftests.py` discovers this tool's suite by importing the module
# and looking for a def NAMED `_selftest`.  Move it to another file without
# re-exporting and the suite does not fail — it silently STOPS BEING FOUND,
# taking 123 cases out of the run while the totals still look plausible.
from _pycodemod_selftest import _selftest  # noqa: F401,E402
from _pycodemod_query import (  # noqa: F401,E402
    KwIndex, _Scan, _attr_reads_one, _bare_calls, _cached_defs,
    _print_bindings, _rivals_one, _scan_defs, asserted, attr_reads,
    available, bindings, callgraph, collision_apex, collision_kinds, collisions, dead, discards,
    forwards, funcnames, guarded, key_reads, literal_sites, reaches, reifies, resorts,
    rivals, scan, shape_sites, swallows, alias_hint, fix_owes_callers,
    source_of, sqlnames, values, values_many, verdict_returners,
)
# ⚑ THE OTHER AXIS OF `--guarded`, IN ITS OWN FILE.  `--guarded` classifies a call by
# SOURCE POSITION and reports 41 `top` sites, ZERO of which refuse a bare invocation
# (Ⓐ48 ⟡guard-placement-predicate).  `--placement` answers WHEN the guard fires.  It
# lives in a sibling because all three candidate homes (`pycodemod`, `_pycodemod_query`,
# `toolmodes`) are already OVER the 1200-line `--size` cap, and adding to an over-cap
# module grows the debt the cap exists to measure.
# ⚑ ⟡exit-and-swallow, IMPORTED AS A MODULE for the same reason `--ambient` is: its
# three public names are reached from ONE dispatch branch, and the `--importers` census
# already records 12 names a star-re-export cannot carry.
import _pycodemod_exit  # noqa: F401,E402
from _pycodemod_placement import (  # noqa: F401,E402
    ENTRY_FORMS, FIRST_WRITE_FORMS, SNAPSHOT_FORMS, STORE_SUBSTITUTE,
    STORE_WRITE_FORMS, UNDECIDABLE, disagreement, placement, print_disagreement,
    print_placement, writes_store,
)
# ⚑ IMPORTED AS A MODULE, NOT star-lifted. `--ambient`'s two public names
# (`ambient`, `KNOWN_MISSES`) are only reached from one dispatch branch, and the
# `--importers` census above already records 12 names a star-re-export CANNOT carry
# — adding to that surface is debt for one caller.
import _pycodemod_ambient  # noqa: F401,E402
from _pycodemod_census import (  # noqa: F401,E402
    _DERIVER, _PARSE_CACHE, _SCHEMA, _deriver_tag, _ignore_cache,
    FAILURE_BEARING, OVERLARGE_LINES, ROUTE, SUCCESS_ONLY, _artifact_readers,
    _code_lines, _corpus_key, _declared_deps, _deriver_tag, _ignore_cache,
    _l2_cached, _print_crossings, _print_diagnose,
    ALIAS_COMPLIANT, aliases,
    build_artifact_readers, crossings, discriminates, imports, importers,
    module_size, module_size_all,
    module_state, paperkit_projects, touches, type_errors, writes_by_default,
)
# ⚑ THE ⚑-COMMENTARY CENSUS IS ITS OWN MODULE, and the reason is the census module's own seam
# rule applied to the file that states it: everything in `_pycodemod_census` reads code
# STRUCTURE, these read the incident LOG — and `commentary_lost` is a GATE (it exits 1), not a
# report. The immediate cause was `--size` firing on the file I had just added them to: 1,201
# lines against its own 1,200 cap. Paying it down is what the census is for.
from _pycodemod_commentary import (  # noqa: F401,E402
    COMMENTARY_MARKS, commentary_blocks, commentary_census, commentary_kinds, commentary_lost,
)
# ⚑ THE CUT ITSELF IS A MODE, AND UNTIL NOW IT WAS THE ONE STEP LEFT TO HAND.  `--size` names
# a file too big to read whole, `--layout` says where its statements are, `--commentary
# --since` gates what the move dropped — and nothing PERFORMED the move, so a split meant
# string surgery on the corpus whose comments are the argument.
from _pycodemod_split import (  # noqa: F401,E402
    argflag, argopt, plan, statements, verify, _print_split,
)
from _pycodemod_sql import (  # noqa: F401,E402
    RELALG_KINDS, _PORT_REMEDY, _pg_probe_con, _pg_sandbox_con, pg_probe_status,
    _print_portable, _print_rawreads, _print_relalg, _print_relname,
    _print_snapshots, _print_sql,
    portable_sites, rawread_sites, relalg_sites, relname_sites, snapshot_sites,
    sql_kind, sql_rel_roles, sql_relnames, sql_rw, sql_sites,
)
# ⚑ `--control` IS A SIBLING OF `--relalg`, NOT AN EXTENSION OF IT, and the reason is
# recorded in `_pycodemod_sql.py`'s own docstring: `relalg_sites` CANNOT SEE A
# LOOP-WITH-EARLY-BREAK, and the site it missed (`_unreflected_floor`) is the worst
# offender in the corpus.  `--relalg` gates every hit on the enclosing function reading
# the store — right for "what algebra happens to rows", wrong for "where is the control
# flow", which must also count the mode-branches and the ε boundary that no rung reaches.
# They SHARE the row-provenance predicates (`store_reader_fns` &c., now module-level in
# `_pycodemod_sql`) rather than each carrying a copy.
from _pycodemod_control import (  # noqa: F401,E402
    CONSTRUCT_GROUPS, CONSTRUCTS, CONTROL_KINDS, SQL_FORM,
    _print_control, control_sites, census as control_census,
)
# ⚑ `--fingerprint` IS WHAT `--control` LEAVES BEHIND, and it is a MODE here rather than a
# tool because the artifact already has a reader — the rule `struct-tools/SKILL.md` states
# as *"a MODE first, a new TOOL only for a new artifact kind"*.  It subclasses
# `_pycodemod_control._Census` to keep the governing expression each verdict was formed on,
# so the two modes cannot disagree about what a site IS while disagreeing about what it
# touches.
from _pycodemod_fingerprint import (  # noqa: F401,E402
    PrimeRegistry, _print_fingerprint, decode, decode_with_remainder, fingerprint,
    local_closure, referents, site_referents,
)

ROOT = _c.ROOT



# ⚑ ONE TUPLE, TWO READERS — the arg-stripper in `_dispatch` and the entry point
# both consume it, so adding a scope flag cannot leave one of them behind.  It
# already did once: `--in` landed three minutes after `--archive` and the
# stripper still named only `--archive`, so `--in persistqueue --calls ack`
# silently answered about `persistqueue`.
SCOPE_FLAGS = ("--archive", "--in")

# ⚑⚑⚑ THE ARGUMENT MODEL IS DECLARED HERE, AND ITS ABSENCE WAS A GENERALITY DEFECT — not a
# series of bugs (user, 2026-08-17): *"pycodemod's arguments and behaviors are not being added
# in a composable way, they're being added in ad-hoc ways that lead to valid-but-wrong
# expectations about parallel behaviors."*  MEASURED: `--attr argv` reports **135 direct
# `sys.argv` reads inside `_dispatch`**, i.e. 135 independent parses of one command line, each
# branch deciding for itself what a token means.  Every symptom below is that one cause:
#
#   * `--since` subtracted `--marks`'s operand privately; the sibling `--commentary` branch did
#     not, so `--marks record` read `record` as a PATH and refused with "no such path".
#   * `--lines` was tested only INSIDE the `--commentary` branch, so `modes()` never saw it and
#     an unknown flag fell through to the banner with exit 1.
#   * `--corpus` ate `--bib`'s operand; `--key` ate `--archive`'s.  Same class, twice more.
#
# ⚑ AND DERIVING ARITY FROM IMPLEMENTATION SPELLINGS IS WHAT MAKES IT UNBOUNDED. `modes()` reads
# `sys.argv[i + 1]`/`args[0]`; `--marks` uses `argopt(...)` and was therefore called NULLARY.
# Each new way of spelling "read the next token" silently creates a new blind spot, found by a
# peer rather than by the suite.  A DECLARATION cannot have that failure mode: a flag absent
# from this table is absent everywhere, visibly, and the coherence gate below fails.
#
# `operand` is the token the flag itself consumes (None = nullary).  `paths` says the mode also
# takes a trailing path population.  `opts` are the modifier flags that mode accepts, so a
# modifier is owned by ONE mode rather than being globally true.
class _ModeDocs:
    """⚑ THE CLASS MOVED TO `scripts/climode.py`; THIS DOCSTRING IS THE INCIDENT RECORD.

    ⟡mode-shared — `Mode` was born here and is now imported from `scripts/climode.py`,
    because the four `_MODES` rosters awaiting conversion (`schema.py`, `lifecycle.py`,
    `reconstruct.py`, `jea_pydecode.py`) all live in `jea/metalanguage/` — the PROMOTED
    side. Importing this class from `scratch/` there would add an 8th runtime coupling to
    `check_scratch_independence` (Λ8), already red at 7, whose refusal text says to fix it
    by PROMOTING the module rather than repathing. `scripts/` is where `ratchet.py`
    already sits for the same reason: machinery both sides consume.

    ⚑ THE RATIONALE BELOW IS WHY THE SHAPE IS WHAT IT IS, kept at the site that grew it.

    One CLI mode's argument shape AND the reporting contracts it owes.

    ⚑⚑⚑ `scans` IS THE `Arm` FIELD, and it exists because a hand-threaded contract is
    not a contract.  `Mode` declared ARGUMENT SHAPE (operand, paths, opts) and nothing
    about BEHAVIOUR, so every cross-cutting property lived as a hand-written line inside
    one of ~20 `if "--x" in sys.argv:` branches.  On 2026-08-18 that cost the corpus its
    most-trusted verdict: a visitor defect emptied `scan()`, every `--calls` query
    answered `0 def, 0 call, 0 ref`, and `--dead` — the census this repo DELETES on —
    read GREEN on a file with 18 defs.  Fixing it meant editing two branches by hand,
    and NOTHING STRUCTURAL said the other eighteen needed it or that the next mode
    would.

    ⚑⚑ THE FIELD IS FALSIFIABLE, WHICH IS WHAT MAKES IT A DECLARATION RATHER THAN A
    COMMENT.  This is the `Arm(key, file, find, replace, expect, why)` model from
    gcalculus `farm.py` and the `Convention(flag, invoker, contract, why)` this session
    already landed: the load-bearing field is the one a discriminator can CHECK.  An
    `Arm` declares the message its mutation must provoke; a `Mode` declares that its
    branch consumes `scan()` and therefore owes an incomplete-scan report.
    `--check-contracts` runs the discriminator, so a mode that claims `scans=True` and
    never reports is a GATE FAILURE, not a code review note.

    ⚑ AND IT IS DECLARED, NOT INFERRED, for the reason `declared_operand_flags` already
    records: `modes()` and `argopt_flags()` read the dispatch source and can only report
    the spellings they know, which is exactly what made them incomplete.  A behavioural
    contract inferred from the body would be satisfied BY the body by construction —
    it could never fail, so it could never find anything.

    ⚑ `writes` is the field the operator's objection produced: a boolean could not say
    WHICH of the things a tool touches it mutates, and `mutates` survives only as a
    derived projection so two spellings of one fact cannot drift.
    """


# ⚑ ONE AUTHORITY, IMPORTED — not a second copy. `scripts/` is on `sys.path` here via the
# header's path setup, the same route `ratchet` reaches its 16 gates by.
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from climode import Mode  # noqa: E402


#: Modifier flags that consume the token after them, wherever they appear.
#: ⚑ COMPLETED FROM THE COHERENCE GATE'S OWN FIRST FAILURE, which is the point of declaring:
#: my hand-written first cut named 9 and the gate immediately reported 18 more that the
#: derivers could see. Under the inference-only design those 18 were invisible until a peer
#: tripped one — here the residue arrived in a single verdict line, in this tree, before any
#: borrower ran it.
OPT_OPERANDS = ("--marks", "--since", "--max", "--max-defs", "--prefix", "--keep",
                "--export", "--bib", "--pattern", "--seed", "--top", "--kind", "--from",
                "--key", "--keys", "--shape", "--source", "--relname", "--sql",
                # ⚑ `--rev` IS A MODIFIER OPERAND (Ⓝ10) — `--fix-owes-callers <name> --rev
                # WORKING` reads the revision by `argopt`, so `WORKING` must NOT survive in
                # `args` or it reads as a PATH and the population refuses on "no such path".
                # That is the operand-ownership class this tuple exists to close, and it has
                # fired five times in this ecosystem.
                "--groups", "--rev",
                # ⚑ `--verdict SCOPED` narrows `--ambient`; without declaring it here
                # the operand reads as a PATH and the population refuses on "no such
                # path" — the operand-ownership class, sixth instance.
                "--verdict")

MODES = {
    # ⚑ THE MIGRATION ENGINE FOR ⟡mode-standardize, and the first entry to carry
    # `writes`. It is a pure READ — it prints skeletons to stdout and edits nothing —
    # so `writes=()` is a claim, not an omission, and `--check-contracts` will hold it
    # to that. Its own coherence selftest caught it undeclared one minute after it was
    # written, which is the table doing its job on its own author.
    "--declare-modes": Mode(operand="path", paths=True, scans=False, writes=(),
                            why="projects modes() arity into Mode(...) skeletons"),
    "--commentary": Mode(paths=True,
                         opts=("--marks", "--since", "--lines", "--kinds", "--blocks")),
    # ⚑ THE INCIDENT-BLOCK READER. `--lines` is line-granular by construction and a ⚑ paragraph
    # is not one line, so every multi-line incident in this corpus was reported as fragments —
    # and only the first fragment carries the mark, so the rest were invisible. This reads the
    # BLOCK, its enclosing def, and the backticked symbols it cites, which is the edge from a
    # recorded defect to the mode that already addresses it.
    "--blocks": Mode(paths=True, scans=False, writes=(),
                     why="⚑ incidents as blocks, with enclosing scope and cited symbols"),
    # ⚑ THE TWO MODES WHOSE VERDICT RESTS ON `scan()` — declared, so the contract is a
    # fact about the ROSTER rather than a line someone remembered to write in a branch.
    # `--dead` is the sharper of the two: it reads CLEAN when the scan is broken, because
    # zero rows means zero unreachable rows, and it is what this repo DELETES on.
    "--calls": Mode(operand="name", paths=True, scans=True,
                    why="counts def/call/ref rows straight out of scan()"),
    "--guarded": Mode(operand="name", paths=True, scans=True,
                      why="partitions scan() call rows by enclosing condition"),
    # ⚑⚑ THE OTHER AXIS OF `--guarded` (Ⓐ48). That mode reads SOURCE POSITION and
    # reports 41 `top` sites, ZERO of which refuse a bare invocation — 30 are the
    # `_snapshot_once` first-write idiom. This reads EXECUTION ORDER. NO OPERAND: the
    # recognised guard forms are the subject, so a name would narrow a census.
    "--placement": Mode(paths=True, scans=True,
                        why="reads scan() call rows against the __main__ entry span"),
    # ⚑⚑ THE RELATION BETWEEN THE TWO GUARDS, WHICH IS NOT A PROPERTY OF EITHER. The
    # intent gate and the snapshot are two calls with two placements and nothing binds
    # them; `intent_census` reads one, `--guarded` reads the other, and the dangerous
    # shape lives in the edge — `the-fact-may-be-an-edge-not-a-property`.
    "--unbound-snapshot": Mode(paths=True, scans=True,
                               why="joins the intent-guard and snapshot placements"),
    # ⚑ `--swallows` does NOT declare `scans=True`: it walks `ast` directly and never
    # calls `scan()`, so `_report_skipped` would print another query's accounting. A
    # contract claimed where it does not apply is worse than one not claimed.
    # ⚑⚑ ⟡ambient-root — THE UNION CENSUS, and the reason it is not `--calls`-shaped.
    # Ambient-cwd dependence was tracked by `--calls getcwd` (20 sites) while the
    # RELATIVE-PATH READ — `os.path.exists(mod.replace(".","/") + ".agda")` — is the
    # same dependence and calls no `getcwd` at all. `--calls exists` (153) is not a
    # bound either; `open`/`listdir`/`glob`/`Path`/`subprocess` are further spellings.
    # The union is keyed on a PROPERTY (a path-resolving callee with an unanchored
    # argument), which no name-keyed mode can express. `scans=False`: it walks `ast`
    # directly with its OWN accounting, so `_report_skipped` is called on
    # `ambient` rather than on `scan` — claiming the contract here would print another
    # query's population, which is the defect `_report_skipped`'s `where` closes.
    "--ambient": Mode(paths=True, opts=("--sites", "--misses", "--verdict"),
                      why="property census of unanchored path resolution"),
    "--swallows": Mode(paths=True),
    # ⚑ `scans=True` IS CLAIMED DELIBERATELY, AND IT IS THE STRICTER CHOICE.  The
    # contract it buys — `_report_skipped()` — is the accounting a corpus census owes,
    # and this census is ABOUT swallowed failures: declaring `scans=False` would have
    # let the module silently drop unparseable files while censusing others for exactly
    # that.  Note `--swallows` above does NOT claim it; that is pre-existing debt, not
    # a precedent to copy.
    # ⚑⚑⚑ `--sites` IS WHAT MAKES THE VERDICT COLUMN FALSIFIABLE, AND IT IS NOT A
    # CONVENIENCE BESIDE THE COUNT.  The default view lists `LIBRARY` and `hard` per-site
    # and prints `dispatch`/`main-only` ONLY as totals — so the two buckets that ABSORB a
    # join error are exactly the two a reader cannot audit.  A def wrongly read as
    # `main-only` (the `__main__`-guard test) or as `dispatch` (the importer-name join)
    # vanishes into a number, and a wrong join is then unfalsifiable from the output:
    # `check_snapshot_guard --sites` exists for the same reason (*"`--list` said WHICH
    # TOOLS; nothing said WHICH LINE, so every paydown re-derived the predicate by hand"*).
    # ⚑ MEASURED THE OTHER WAY TOO (2026-08-26): a report that `edit_snapshot`'s exits
    # were mis-read as `main-only` was checked by listing them and found CORRECT — all 5
    # are genuinely under the `__main__` guard.  The listing settles a disputed verdict in
    # both directions, which a bucket total cannot do at all.
    "--exits": Mode(paths=True, opts=("--sites",), scans=True,
                    why="⟡exit-and-swallow: process-exit ownership + the handlers that "
                        "catch (or fail to catch) SystemExit, and the interlock between "
                        "them"),
    "--binding": Mode(operand="name", paths=True),
    "--attr": Mode(operand="name", paths=True),
    "--literal": Mode(operand="name", paths=True),
    "--forwards": Mode(operand="name", paths=True),
    # ⚑⚑ THE JOIN BETWEEN `--calls` AND A CHANGE — Ⓝ10. `--calls` knows where the callers
    # are and `git diff` knows what the change touched; nothing joined them, so "which
    # call sites did I forget" was answered by hand. It fired TWICE in one hour in the
    # memory generators (a `_load()` return tuple widened 2 -> 4, with four call sites and
    # three updated). `scans=True` because the verdict rests on `scan()`, and a silently
    # shrunken population here reports a caller as ALREADY-UPDATED.
    "--fix-owes-callers": Mode(operand="name --rev REV", paths=True, scans=True,
                               opts=("--rev",),
                               why="joins scan() call rows against git's changed-file set"),
    "--asserted": Mode(operand="name", paths=True),
    "--values": Mode(operand="name", paths=True),
    "--reaches": Mode(operand="name", paths=True),
    "--importers": Mode(operand="name", paths=True),
    # ⚑ NO OPERAND, UNLIKE `--importers`. That mode asks "who imports THIS module" and needs a
    # subject; this one is a CENSUS over every import in the corpus, so a name would narrow it
    # to the question already answered. The `.py` twin of `agda_defs --qualified`.
    "--aliases": Mode(paths=True, opts=("--all", "--sites")),
    # ⚑ THE CAPABILITY EXISTED AND HAD NO CLI ROUTE — `collisions`/`collision_kinds` are
    # defined in `_pycodemod_query`, IMPORTED at the header of this file, and called only
    # from `catalog/library/items.py`. This module's own docstring names that exact shape
    # (`rewire_only`: written, documented, zero callers, dispatch branch never added), so
    # the fix is a branch, not a reader. I reported the collision count as "not quotable
    # today" one turn before finding it already computed.
    "--collisions": Mode(paths=True, opts=("--sites", "--kind")),
    # ⚑ THE STRUCTURE-KEYED TWIN, AND THE TWO ARE NOT REDUNDANT. `--collisions` keys on
    # the SPELLING (`by_name.setdefault(name, ...)`, never opening a body), so its rows
    # cannot be ranked: 78 defs named `check` and 6 named `alphabet_size` are the same
    # kind of row to it. `--collision-apex` keys on BODY STRUCTURE via
    # `jea_extrude_ir.templatize` and grades by sharing-breadth, so a real lift and a
    # coincidence sharing a name separate. Keeping both is deliberate — the two
    # DISAGREEING is the finding (a `crossing` with 0 holes is a lift; a `sibling` with
    # 12 holes is a coincidence that happens to share a directory).
    "--collision-apex": Mode(paths=True),
    "--rivals": Mode(operand="name", paths=True),
    "--sqlname": Mode(operand="name", paths=True, scans=True,
                      why="sqlnames() carries the same skip accounting as scan(); a "
                          "silent zero here re-creates the false-dead verdict this "
                          "mode exists to prevent"),
    "--discards": Mode(paths=True),
    # ⚑ `scans=True` THOUGH IT DOES NOT CALL `scan()`. The contract is about the SKIP
    # ACCOUNTING, not about which enumerator produced it: `reifies()` runs its own CST walk
    # and carries `reifies.skipped`/`reifies.population`, so its branch owes the same
    # incomplete-scan report and `_report_skipped(reifies)` is what discharges it. Reading
    # the field as "calls scan()" would exempt exactly the modes that roll their own walk —
    # i.e. the ones whose swallow nobody has audited.
    "--reifies": Mode(paths=True, opts=("--set", "--dict", "--list", "--sorted", "--accum"),
                      scans=True,
                      why="a reification census that read 0 of 810 files reports "
                          "'nothing materializes here', which is the confident-zero the "
                          "whole arc is about"),
    "--resorts": Mode(paths=True, scans=True,
                      why="a span query over (producer, consumer) — an unread file drops "
                          "one END of a pair, so the join silently reports fewer double "
                          "payments than exist"),
    "--funcnames": Mode(paths=True, opts=("--verbatim",), scans=True,
                        why="the dialect-portability question `--portable` structurally "
                            "cannot answer; an unread file hides exactly the kind of "
                            "sqlite-ism that made a whole capability dark"),
    "--split": Mode(operand="file", opts=("--max", "--max-defs", "--prefix", "--keep",
                                          "--export", "--apply")),
    "--banner": Mode(),
    "--check-contracts": Mode(),
    "--size": Mode(paths=True),
    "--layout": Mode(paths=True),
    "--roundtrip": Mode(paths=True),
    "--dead": Mode(paths=True, scans=True,
                   why="reads CLEAN on a broken scan — zero rows means zero "
                       "unreachable rows; this is the census the repo deletes on"),
    "--imports": Mode(paths=True),
    "--artifacts": Mode(paths=True),
    "--types": Mode(paths=True),
    "--selftest": Mode(),

    # ⚑⚑ ⟡mode-standardize / Ⓢ1a — THE 19 THAT DISPATCHED WITHOUT A DECLARATION.
    # `--check-contracts` reported 25; `--declare-modes` split them into these 19
    # genuinely-missing entries and 6 DUAL-ROLE flags (below), which are a different
    # defect and are not fixed by adding a row.
    #
    # ⚑ EVERY FIELD HERE IS READ, NOT GUESSED, and the two derivable ones came from
    # the tools rather than from me:
    #   · `operand` — `modes()`, the same derivation `--banner` renders;
    #   · `scans`   — `--guarded _report_skipped` returns EXACTLY the 7 modes already
    #                 declared `scans=True`, so all 19 of these are `False` as a
    #                 measured fact about the dispatch, not an assumption;
    #   · `writes`  — `--literal "w"` finds ONE `open(…, "w")` in the whole file
    #                 (`:1967`, the `--discards` ledger), so every mode here is a pure
    #                 read. `writes=()` is therefore a CLAIM the gate now holds them to.
    "--available": Mode(paths=True, scans=False, writes=(),
                        why="reports which modes run without libcst"),
    "--control": Mode(paths=True, scans=False, writes=(),
                      opts=("--kind", "--summary"),
                      why="types every control-flow site by what the engine could take it as"),
    "--crossings": Mode(paths=True, scans=False, writes=(),
                        why="imports that cross a declared boundary"),
    "--diagnose": Mode(paths=True, scans=False, writes=(),
                       why="why a file failed to parse, per file"),
    "--discriminates": Mode(paths=True, scans=False, writes=(),
                            why="whether a predicate can separate its population"),
    "--escapes": Mode(paths=True, scans=False, writes=(),
                      why="invalid string escapes — a lint over .py"),
    "--fingerprint": Mode(paths=True, scans=False, writes=(),
                          why="a prime per distinct referent; the remainder is the finding"),
    "--kinds": Mode(paths=True, scans=False, writes=(),
                    why="the kind roster INCLUDING zeroes, so absent and unseen stay apart"),
    "--last": Mode(scans=False, writes=(),
                   why="replays the persisted census and says when its predicate went stale"),
    "--lines": Mode(paths=True, scans=False, writes=(),
                    why="line-granular commentary rows"),
    "--package": Mode(paths=True, scans=False, writes=(),
                      why="where an installed module's source lives"),
    "--portable": Mode(paths=True, scans=False, writes=(),
                       why="raw SQL literals a dialect may not carry"),
    "--projects": Mode(paths=True, scans=False, writes=(),
                       why="projection sites over returned rows"),
    "--rawreads": Mode(paths=True, scans=False, writes=(),
                       why="raw con.execute reads that bypass the builder layer"),
    "--relalg": Mode(paths=True, scans=False, writes=(),
                     why="relational algebra performed in python, ranked by function"),
    "--sites": Mode(paths=True, scans=False, writes=(),
                    why="per-site detail for a census that otherwise reports counts"),
    "--snapshots": Mode(paths=True, scans=False, writes=(),
                        why="the recorded before/after groups for a relocation"),
    "--state": Mode(paths=True, scans=False, writes=(),
                    why="module-scope mutable state vs accumulators vs const tables"),
    "--touches": Mode(paths=True, scans=False, writes=(),
                      why="item pairs whose witnesses read a common file"),

    # ⚑⚑ ⟡mode-consolidation / Ⓜ9 — THE FIVE REMAINING `--check-contracts` DISAGREEMENTS,
    # AND ALL FIVE WERE ALREADY IN `OPT_OPERANDS`. That is the whole reason they survived
    # the Ⓢ1a sweep: the arg-stripper knew they consume a token, so nothing MISBEHAVED,
    # and only `--check-contracts` — which compares the DISPATCH against the ROSTER rather
    # than against behaviour — could see that the roster never said so. A flag can be
    # correct in one authority and absent from the other, and the absence is the finding.
    #
    # ⚑ EVERY ARITY HERE IS READ OFF ITS OWN DISPATCH BRANCH, not inferred from the
    # `OPT_OPERANDS` membership that would have made all five look identical:
    #   · `--source`  :2668  `sys.argv[i+1]` required, usage on absence     → operand, paths
    #   · `--sql`     :2729  `sys.argv[i+1]` required, usage on absence     → operand, paths
    #   · `--key`     :2822  `sys.argv[i+1]` required, usage on absence     → operand, paths
    #   · `--shape`   :3016  `sys.argv[i+1]` required, usage on absence     → operand, paths
    #                        and it OWNS a modifier, `--shape-all` (:3026)
    #   · `--relname` :2738  operand OPTIONAL — the bare form is the removal check, and a
    #                        first token naming an existing PATH is a path, not a relation
    #                        (:2745). Spelled `[rel]` so the roster carries the optionality
    #                        the other four do not have; a bare `"rel"` here would declare
    #                        a requirement the dispatch deliberately does not enforce.
    #
    # ⚑ `scans=False` FOR ALL FIVE IS MEASURED, NOT ASSUMED — none of these branches
    # reaches `scan()`; they route to `source_of`, `_print_sql`, `_print_relname`,
    # `key_sites` and `shape_sites`. `writes=()` likewise: every one prints and exits.
    "--source": Mode(operand="name", paths=True, scans=False, writes=(),
                     why="the SOURCE TEXT of a definition, by name"),
    "--sql": Mode(operand="identifier", paths=True, scans=False, writes=(),
                  why="SQL literals mentioning <ident>, split by style"),
    "--key": Mode(operand="string-key", paths=True, scans=False, writes=(),
                  why="sites subscripting or getting a literal string key"),
    "--shape": Mode(operand="regex", paths=True, scans=False, writes=(),
                    opts=("--shape-all",),
                    why="where a source shape occurs; comments/docstrings excluded "
                        "unless --shape-all"),
    "--relname": Mode(operand="[rel]", paths=True, scans=False, writes=(),
                      why="where <rel> is used AS A RELATION; bare form is the "
                          "removal check"),
}

# ⚑⚑⚑ ⟡mode-dual-role — SIX FLAGS ARE BOTH A MODIFIER AND A MODE, AND ADDING A `Mode`
# ROW WOULD HAVE HIDDEN IT.  `--key`, `--relname`, `--shape`, `--since`, `--source` and
# `--sql` are declared in `OPT_OPERANDS` (so their operand is read by `argopt` and
# STRIPPED from `args`) and ALSO open a dispatch branch (so `args[0]` is read
# positionally).  `_dispatch`'s own ⚑ records what that conflation costs: unioning the
# two kinds "broke every query mode for ten minutes" — `--calls modes <path>` silently
# became a whole-corpus scan for nothing.
#
# ⚑ THE HONEST STATE IS UNRESOLVED, SO IT IS RECORDED RATHER THAN DECLARED.  Each needs
# a decision about which role it plays; `--declare-modes` lists them apart from the
# skeletons for exactly that reason, and `--check-contracts` still counts them, so the
# residue cannot be banked as done.  Filed ⟡mode-dual-role.


def declared_operand_flags():
    """{flag} — every flag DECLARED to consume the token after it, from `MODES` + `OPT_OPERANDS`.

    ⚑ THE DECLARATION IS THE AUTHORITY; `modes()` AND `argopt_flags()` ARE NOW WITNESSES. They
    read the dispatch's source and can only ever report the spellings they know, which is what
    made them incomplete. This function is what `_dispatch` consumes, so a flag's arity is a
    fact stated once rather than inferred three ways.
    """
    out = set(OPT_OPERANDS)
    for _flag, _m in MODES.items():
        if _m.operand:
            out.add(_flag)
    return out


def declare_modes(path=None):
    """[(flag, operand, declared, modifier)] — the `Mode(...)` roster entries a file OWES.

    ⚑⚑ THE MIGRATION ENGINE FOR ⟡mode-standardize, AND IT EXISTS BECAUSE THE PAYDOWN
    WAS ABOUT TO BE DONE BY HAND.  `--check-contracts` reports 25 dispatched modes
    absent from `MODES`; the obvious next step is to type 25 entries, and typing them
    is how the roster drifted in the first place.  Arity is ALREADY derived — `modes()`
    reads it out of the dispatch and `--banner` renders it for all 56 — so the entries
    are a projection of an existing authority, not new information.

    ⚑ WHAT IS DERIVED AND WHAT IS NOT, kept apart on purpose.  `operand` is structural
    (the branch indexes past the flag) and is emitted.  `paths`, `opts`, `scans` and
    `why` are NOT: `scans` is the whole point of the model — a contract inferred from
    the body would be satisfied by the body by construction and could never fail
    (`Mode.__doc__`), and `why` is the `Arm.why` field, which is a human's sentence or
    it is nothing.  So this emits a SKELETON that a reader completes, and the gate
    stays able to bite.  Emitting a confident `scans=False` for 25 modes would clear
    the gate while removing its power to find anything — metric-gaming, mechanized.

    ⚑ `declared` says whether `MODES` already carries the flag, so the caller can show
    the residue without a second pass.

    ⚑⚑ AND IT REPORTS THE DUAL-ROLE FLAGS SEPARATELY, BECAUSE THEY ARE NOT A MISSING
    DECLARATION.  Six flags (`--key`, `--since`, `--shape`, `--source`, `--relname`,
    `--sql`) are declared MODIFIERS in `OPT_OPERANDS` *and* open a dispatch branch.
    `_dispatch`'s own comment records why that distinction is load-bearing: a MODE's
    operand is read positionally out of `args[0]`, a MODIFIER's is read by `argopt` and
    must be stripped from `args` or it reads as a path — and conflating the two "broke
    every query mode for ten minutes".  Emitting a `Mode(...)` skeleton for a modifier
    would re-commit that conflation in the table built to end it, so they are listed
    apart and left for a decision.

    ⚑⚑⚑ AND IT READS ANY TOOL, NOT JUST THIS ONE — WHICH IT DID NOT UNTIL Ⓢ1e.  `modes()`
    parses a function literally named `_dispatch`, so pointing this at `mdstruct.py`
    returned `0 of 0 dispatched` — a tool with eleven live flags reported as having none.
    That is a fact about the READER stated as a fact about the tool, the same shape as the
    `\\w*argv` miss, and it would have made the migration's own instrument report every
    unconverted tool as already clean.  `climode.branch_bounds` is the general reader, so
    a foreign file goes through it and only THIS file keeps the `_dispatch` path (whose
    `_takes_operand` arity inference `branch_bounds` does not attempt).
    """
    path = path or os.path.abspath(__file__)
    _here = os.path.abspath(__file__)
    if os.path.abspath(path) == _here:
        derived = modes(path)
        roster, opts = MODES, OPT_OPERANDS
    else:
        import climode as _cm
        src = open(path, encoding="utf-8").read()
        # ⚑ ARITY IS UNKNOWN FOR A FOREIGN FILE AND IS REPORTED AS SUCH, never as nullary.
        # `branch_bounds` locates branches; it does not read what they consume. Emitting
        # `operand=None` for all of them would be a confident wrong answer in the field
        # that binds argv — exactly the `--key --archive f.py` crash.
        derived = {f: None for f in _cm.branch_bounds(src)}
        roster, opts = {}, ()
    return [(f, derived[f], f in roster, f in opts) for f in sorted(derived)]


def modes(path=None):
    """Every mode the CLI dispatches, DERIVED from the dispatch body.

    ⚑ THE ROSTER LIVES IN ONE PLACE AND WAS READ FROM TWO OTHERS.  A mode exists
    because `_dispatch` tests for it; the module docstring RE-STATES that list by
    hand, and the arg-stripper guesses at arity.  Both copies drifted:

      * the banner listed 15 modes while the dispatch handled 20 -- `--imports`,
        `--escapes`, `--package`, `--in`, `--discards`, `--last`, `--discriminates`
        and `--binding` shipped without ever reaching it, and `--archive`'s entry
        still described the member-walk that `corpus` DELETED.  Four commands were
        spent hunting a mode name that the banner should have answered.
      * `--key --archive f.py` CRASHED: the entry point takes the first non-flag
        token after a scope flag, so it bound `--key`'s operand as a tarball path.
        `_dispatch` has a guard for exactly this, but it runs AFTER `corpus()` has
        already opened the archive.

    Both are the same missing fact -- **the CLI could not say what its own modes
    are, or which of them take an operand** -- so every consumer re-derived it and
    each got it wrong differently.  This is the authority; `--banner` gates the
    docstring against it and the entry point reads arity from it.

    A mode is `"--x" in sys.argv`; it TAKES AN OPERAND if the branch indexes
    `sys.argv` past the flag or reads `args[0]`.  Both are structural facts about
    the dispatch, so a new mode is covered the moment it is written -- there is no
    list to update, which is the whole point."""
    path = path or os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    # ⚑⚑ THIS RUNS AT IMPORT, SO ITS DEPENDENCY WAS EVERY MODE'S DEPENDENCY. `_arity = modes()`
    # sits at module scope (the entry point needs operand-ownership before dispatch), and this
    # body parsed with libcst — so in a checkout without it, `--size` died in `cst.metadata`
    # despite `module_size_all` being pure `ast` + `splitlines`. A peer running this tooling by
    # symlink hit exactly that and reported the tool as unavailable; it was available and
    # unreachable, which is the worse failure because it looks like absence.
    #
    # ⚑ THE FALLBACK IS `ast`, AND THE PREDICATE IS UNCHANGED — it was always TEXTUAL
    # (`"args[0]" in body`) over the emitted source, so only the TRAVERSAL needed libcst.
    # `ast.get_source_segment` returns the same body text `cst.Module(...).code` did. This is
    # not a second implementation of the rule; it is the same rule reached by a stdlib road.
    if cst is None:
        return _modes_ast(src)
    tree = cst.metadata.MetadataWrapper(cst.parse_module(src))

    class _V(cst.CSTVisitor):
        METADATA_DEPENDENCIES = (cst.metadata.ParentNodeProvider,)

        def __init__(self):
            self.found = {}
            self.depth = 0

        def visit_FunctionDef(self, node):
            self.depth += node.name.value == "_dispatch"

        def leave_FunctionDef(self, node):
            self.depth -= node.name.value == "_dispatch"

        def visit_If(self, node):
            if not self.depth:
                return
            # `"--x" in sys.argv`
            test = node.test
            if not isinstance(test, cst.Comparison) or len(test.comparisons) != 1:
                return
            op = test.comparisons[0].operator
            if not isinstance(op, cst.In):
                return
            if not isinstance(test.left, cst.SimpleString):
                return
            flag = test.left.evaluated_value
            if not isinstance(flag, str) or not flag.startswith("--"):
                return
            body = cst.Module(body=[node.body]).code
            # An operand is read either positionally (`args[0]`) or by index past
            # the flag (`sys.argv[i + 1]`).  Both spellings appear in the dispatch
            # and BOTH must count -- keying on one would have called half the
            # modes nullary, which is the arity half of the same defect.
            self.found[flag] = _takes_operand(body)

    v = _V()
    tree.visit(v)
    return dict(sorted(v.found.items()))


def cst_modes(path=None):
    """{mode} — the modes whose dispatch branch REACHES libcst, derived from the dispatch.

    ⚑ DERIVED FOR THE REASON `modes()` IS DERIVED. The precondition "this mode needs a CST" is
    a structural fact about the branch and its callees, so a literal set here would be a second
    roster beside the dispatch — stale the first time a mode gained or dropped the dependency,
    and stale SILENTLY, since the only symptom is a wrong refusal in a checkout nobody here
    runs.

    ⚑ IT FOLLOWS ONE HOP INTO CALLEES, WHICH IS WHERE THE DEPENDENCY ACTUALLY LIVES. Almost no
    branch names `cst` itself; it calls `roundtrip`/`binding_sites`/`values`, and THOSE parse.
    A branch-text-only scan would report nearly every mode as CST-free and re-open the crash
    this exists to close. Resolved against the module's own source, so it cannot drift from it.
    """
    path = path or os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    # which top-level defs in THIS module touch `cst` in their own body
    cst_fns = set()
    for fn in ast.walk(tree):
        if isinstance(fn, ast.FunctionDef):
            seg = ast.get_source_segment(src, fn) or ""
            if re.search(r"\bcst\.", seg):
                cst_fns.add(fn.name)
    # ⚑ THE IMPORTED HELPERS COUNT TOO — the CST work mostly lives in the `_pycodemod_*`
    # siblings, so a name this module merely CALLS can still be the thing that parses. Their
    # sources are read the same way rather than assumed.
    for _mod in ("_pycodemod_core", "_pycodemod_census"):
        _p = os.path.join(os.path.dirname(path), _mod + ".py")
        try:
            _s = open(_p, encoding="utf-8").read()
            _t = ast.parse(_s)
        except (OSError, SyntaxError):
            continue
        for fn in ast.walk(_t):
            if isinstance(fn, ast.FunctionDef):
                seg = ast.get_source_segment(_s, fn) or ""
                if re.search(r"\bcst\.", seg):
                    cst_fns.add(fn.name)
    out = set()
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or fn.name != "_dispatch":
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            if not isinstance(test, ast.Compare) or len(test.ops) != 1:
                continue
            if not isinstance(test.ops[0], ast.In):
                continue
            if not isinstance(test.left, ast.Constant):
                continue
            flag = test.left.value
            if not isinstance(flag, str) or not flag.startswith("--"):
                continue
            body = "\n".join(
                ast.get_source_segment(src, s) or "" for s in node.body)
            called = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", body))
            if re.search(r"\bcst\.", body) or (called & cst_fns):
                out.add(flag)
    return out


def _takes_operand(body):
    """Does this dispatch branch READ an operand? The arity predicate, shared by both roads.

    ⚑ ONE BODY BECAUSE TWO WOULD DRIFT. `modes()` reaches its branch text via libcst and
    `_modes_ast` via `ast.get_source_segment`; if each carried its own copy of these four
    spellings, a fifth spelling added to one road would silently give the two roads different
    answers about the same CLI — and the fallback road is the one nobody runs here, so the
    drift would surface only in a borrowing checkout.
    """
    return ("args[0]" in body or "args[1]" in body
            or "sys.argv[i + 1]" in body or "sys.argv[_i + 1]" in body
            or "len(args) <" in body)


def argopt_flags(path=None):
    """{flag} — every flag read through `argopt`, which consumes the token after it.

    ⚑⚑ `modes()` DERIVES ARITY FROM INDEXING (`sys.argv[i + 1]`) AND MISSES THIS ENTIRE
    SPELLING. `--marks` is read as `argopt(sys.argv, "--marks")`, so the arity map called it
    NULLARY and its operand fell through into `args` as a PATH: `--marks record` refused with
    *"no such path: record"* for a token that was never a path. Measured by a peer, and it is
    the fifth operand-ownership instance in this ecosystem.

    ⚑ THE ACCESSOR IS THE AUTHORITY, NOT A LIST. Any `argopt(argv, "--x")` call anywhere in
    this module declares that `--x` takes a token, so the flags are read out of those call
    sites rather than enumerated — the same reason `modes()` reads the dispatch instead of
    carrying a roster. A flag added tomorrow through `argopt` is covered on the first run.
    """
    path = path or os.path.abspath(__file__)
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return set()
    return set(re.findall(r"argopt\(\s*sys\.argv\s*,\s*['\"](--[a-z-]+)['\"]", src))


def _modes_ast(src):
    """`modes()` without libcst — the stdlib road, same predicate, same answer.

    ⚑ IT WALKS `_dispatch` ONLY, matching the CST visitor's `depth` guard: a `"--x" in
    sys.argv` test elsewhere in the file is not a mode declaration, and counting one would
    invent a flag the dispatch does not honour.
    """
    found = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or fn.name != "_dispatch":
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            if not isinstance(test, ast.Compare) or len(test.ops) != 1:
                continue
            if not isinstance(test.ops[0], ast.In):
                continue
            if not isinstance(test.left, ast.Constant):
                continue
            flag = test.left.value
            if not isinstance(flag, str) or not flag.startswith("--"):
                continue
            body = "\n".join(
                ast.get_source_segment(src, s) or "" for s in node.body)
            found[flag] = _takes_operand(body)
    return dict(sorted(found.items()))


def banner_drift(path=None):
    """(missing, stale) -- modes the docstring omits, and modes it invents.

    ⚑ BIDIRECTIONAL BY CONSTRUCTION.  A one-way check ("is every dispatched mode
    documented?") passes a banner that still advertises a DELETED mode, which is
    how `--archive`'s entry survived describing the member-walk `corpus` retired.
    The stale half is the half that actively misleads: a reader trusts it and
    invokes something that no longer behaves that way."""
    path = path or os.path.abspath(__file__)
    live = set(modes(path))
    doc = cst.parse_module(open(path, encoding="utf-8").read()).get_docstring() or ""
    # a documented mode is one the banner writes as `pycodemod.py --x`
    documented = set(re.findall(r"pycodemod\.py\s+(--[a-z-]+)", doc))
    return sorted(live - documented), sorted(documented - live)


def layout(path):
    """[(kind, name, first_line, last_line, code_lines)] for every TOP-LEVEL
    statement group in one module, in source order.

    ⚑ WRITTEN BECAUSE `--size` NAMES A VIOLATION IT CANNOT HELP YOU FIX.  `--size`
    reports "4178 code lines > 1200" and stops; the very next question -- WHERE
    does this file cut -- had no mode, and the fallback was `grep '^def '`, which
    the structural-query hook correctly refuses.  A census that reports a defect
    without exposing the structure needed to pay it down leaves the paydown to be
    re-derived by hand, differently, every time.

    ⚑ TOP-LEVEL ONLY, AND THAT IS THE POINT.  A split moves top-level statements;
    a nested def travels with its parent and is noise here.  `--dead` lists nested
    visitor methods (`visit_Call` &c.) precisely because it does not track scope,
    which is why it could not answer this question either."""
    src = open(path, encoding="utf-8").read()
    mod = cst.parse_module(src)
    pos = cst.metadata.MetadataWrapper(mod, unsafe_skip_copy=True)
    ranges = pos.resolve(cst.metadata.PositionProvider)
    # resolve() runs against a COPY unless unsafe_skip_copy -- the nodes we hold
    # must be the same objects the provider keyed on, or every lookup misses.
    out = []
    for stmt in mod.body:
        r = ranges[stmt]
        if isinstance(stmt, cst.FunctionDef):
            kind, name = "def", stmt.name.value
        elif isinstance(stmt, cst.ClassDef):
            kind, name = "class", stmt.name.value
        elif isinstance(stmt, cst.If):
            kind, name = "if", "__main__ guard"
        else:
            kind, name = "stmt", _layout_label(stmt)
        code = sum(1 for ln in cst.Module(body=[stmt]).code.splitlines()
                   if ln.strip() and not ln.lstrip().startswith("#"))
        out.append((kind, name, r.start.line, r.end.line, code))
    return out


def _layout_label(stmt):
    """A short name for a non-def top-level statement (import block, constant)."""
    try:
        small = stmt.body if hasattr(stmt, "body") else []
        for s in small:
            if isinstance(s, cst.Assign) and s.targets:
                t = s.targets[0].target
                if isinstance(t, cst.Name):
                    return t.value
            # ⚑ AN ANNOTATED ASSIGN IS A BINDING TOO, AND OMITTING IT COST A
            # BREAKAGE.  `_BARE_CACHE: dict = {}` is an `AnnAssign`, not an
            # `Assign`, so this returned "-" and the module-level memo showed up
            # in `--layout` as an unnamed group.  Planning a split from that
            # census, I moved its only consumer and left the cache behind;
            # `--discards` then died with `NameError: _BARE_CACHE`.  A census
            # that cannot NAME a thing silently excludes it from every decision
            # made by reading the census — the same fact-about-the-method
            # defect `--key`'s empty results kept producing.
            if isinstance(s, cst.AnnAssign) and isinstance(s.target, cst.Name):
                return s.target.value
            if isinstance(s, (cst.Import, cst.ImportFrom)):
                return "import"
            if isinstance(s, cst.Expr) and isinstance(s.value, cst.SimpleString):
                return "docstring"
    except Exception:
        pass
    return "-"


def opt_key_collisions(roster=None):
    """[(flag, [owner…], harmful, why)] — spellings that are BOTH a `MODES` key and an opt.

    ⚑ `roster` IS INJECTABLE SO THE HARMFUL ARM CAN BE STARVED. The live roster has ZERO
    harmful collisions — correctly — so a suite that could only read `MODES` would
    exercise the BENIGN branch and nothing else, and a discriminator that answers
    "benign" for every input passes a "does it classify" case while being a constant
    function. The parameter is a test seam, not a second authority: every caller in the
    tree passes nothing and gets `MODES`.

    ⚑⚑⚑ ⟡mode-opt-key-collision — THE ONE HOLE LEFT IN THE OPT-VALIDATION CHECK, DERIVED
    RATHER THAN QUOTED.  `_dispatch`'s validator builds `_known` from `set(MODES)` plus
    every invoked mode's `opts`, so a spelling in BOTH sets is in `_known` for EVERY
    invocation: `--swallows --sites` runs silently where `--swallows --misses` correctly
    refuses.  The population was named as "`--sites`, and do not assume it is the only
    one" — and a count nobody derives is a count nobody can trust, so this derives it.

    ⚑⚑ THE HARM VERDICT IS THE POINT, NOT THE COUNT.  A collision is only a DEFECT when
    the two roles mean DIFFERENT things.  The discriminator is whether the mode-role
    takes an operand: a nullary mode whose name also appears as a per-site detail
    modifier is the SAME REQUEST at two scopes (`--exits --sites` narrows `--exits`;
    `--sites` alone censuses every site), so admitting it everywhere costs a reader
    nothing.  An operand-taking mode colliding with a bare modifier is two different
    requests sharing a spelling, and THAT is the rename.

    ⚑ SO THIS REPORTS, IT DOES NOT REFUSE.  Narrowing `_known` to "the first invoked mode
    wins" was tried and REVERTED — dispatch order is BRANCH order, not argv order, so
    that rule refuses correct invocations.  The residue stands declared; what changes is
    that its population is now a query instead of a sentence, so a roster edit that adds
    a harmful collision is VISIBLE rather than inheriting a comment that names one flag.
    """
    roster = MODES if roster is None else roster
    owners = {}
    for _flag, _m in roster.items():
        for _o in (_m.opts or ()):
            owners.setdefault(_o, []).append(_flag)
    out = []
    for _o in sorted(owners):
        if _o not in roster:
            continue
        _mode = roster[_o]
        if _mode.operand:
            out.append((_o, sorted(owners[_o]), True,
                        "the MODE takes <%s> but the OPT is bare — two different requests "
                        "sharing a spelling; the repair is a RENAME of one role"
                        % _mode.operand))
        else:
            out.append((_o, sorted(owners[_o]), False,
                        "both roles are nullary and mean the same thing (per-site detail); "
                        "admitting it on any mode costs a reader nothing — BENIGN, and the "
                        "opt-validation hole it leaves is the declared ⟡mode-opt-key-"
                        "collision residue"))
    return out


def scan_contract(path=None):
    """[(flag, ok, why)] — does every `scans=True` mode actually report its skips?

    ⚑⚑ THE DISCRIMINATOR THAT MAKES `Mode.scans` A DECLARATION AND NOT A COMMENT.  This
    is the `Arm.expect` half of the gcalculus model: an `Arm` names the message its
    mutation must provoke, and an Arm that stops biting is VACUOUS.  Here the claim is
    "this branch's verdict rests on `scan()`", and the check is that the branch calls
    `_report_skipped()`.  A mode that claims the contract and does not honour it is a
    GATE FAILURE — which is the whole difference between declaring a property and
    hoping for it.

    ⚑ IT READS THE DISPATCH SOURCE, WHICH IS THE ONE PLACE INFERENCE IS RIGHT.  The
    ROSTER must be declared (`declared_operand_flags` records why: a deriver reports
    only the spellings it knows, and a contract inferred from the body would be
    satisfied by the body by construction — it could never fail).  But CONFORMANCE is
    exactly the question "does the body do what the roster says", so the body is the
    correct thing to read HERE and only here.  Same split as `modes()`-as-witness.

    ⚑ THE BRANCH IS BOUNDED BY THE NEXT TOP-LEVEL `if "--…" in sys.argv:`, matching how
    `modes()` already segments the dispatch.  A mode whose branch cannot be located is
    reported UNKNOWN rather than passed — an unlocatable branch is a fact about this
    reader, and silently passing it is the confident-zero shape this function exists to
    close.
    """
    path = path or os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines()
    starts = {}
    # ⚑⚑ BOTH SPELLINGS, AND THE SECOND ONE IS WHY. A branch is written either
    # `if "--x" in sys.argv:` or `if "--x" in flagged_argv():` — the latter being the
    # POSIX-`--`-aware accessor this file grew for `--literal`, so that `--literal -- --selftest`
    # treats the operand as an operand. Keying this reader on `sys.argv` alone made it
    # UNABLE TO SEE the newer spelling: `--reifies` declared `scans=True`, discharged the
    # contract correctly, and was reported `UNK branch not located`.
    # ⚑ THAT IS `census-keyed-on-one-spelling` FOR THE SECOND TIME IN THIS FILE — the first
    # was `--selftest` reported as declared-never-dispatched, whose FIX also keyed on one
    # spelling and missed `"--selftest" in flagged_argv()`. A reader that knows one of two
    # live spellings reports a fact about ITSELF as a fact about the dispatch. The UNK
    # verdict is what kept it honest; had this returned FAIL or silently passed, the
    # disagreement would have been banked either way.
    for i, line in enumerate(lines):
        m = re.match(r'\s*if "(--[a-z-]+)" in (?:sys\.argv|flagged_argv\(\)):', line)
        if m and m.group(1) not in starts:
            starts[m.group(1)] = i
    order = sorted(starts.items(), key=lambda kv: kv[1])
    bounds = {}
    for n, (flag, i) in enumerate(order):
        end = order[n + 1][1] if n + 1 < len(order) else len(lines)
        bounds[flag] = (i, end)
    out = []
    for flag, m in sorted(MODES.items()):
        if not m.scans:
            continue
        if flag not in bounds:
            out.append((flag, None, "branch not located in the dispatch"))
            continue
        i, end = bounds[flag]
        body = "\n".join(lines[i:end])
        ok = "_report_skipped(" in body
        out.append((flag, ok, "reports skips" if ok else
                    "declares scans=True but never calls _report_skipped()"))
    # ⚑⚑⚑ THE ROSTER AND THE DISPATCH DISAGREE IN BOTH DIRECTIONS, AND NOTHING SAW IT.
    # `MODES` is the declared authority (`declared_operand_flags` says so) and the
    # dispatch is what actually runs — so a flag in one and not the other is a defect
    # whichever way it points, and neither `--banner` nor `modes()` reports it as such.
    #
    # ⚑⚑ MEASURED 2026-08-19: `--package` and `--touches` are DISPATCHED and UNDECLARED,
    # and each prints a usage string that exists ONLY as a runtime `print` inside its own
    # branch — never in the module docstring the census parses.  So `toolmodes --find
    # touches` reports *"dispatched by pycodemod.py, in no usage line — UNDOCUMENTED"*
    # while the tool will happily print `usage: pycodemod.py --touches [<item-key> ...]`
    # if you fail it.  **The help exists and is reachable only by getting the call
    # wrong** — `friction-capability-legible-only-after-paying-for-it`, in my own tool.
    #
    # ⚑ THE OTHER DIRECTION IS THE DANGEROUS ONE: a flag DECLARED and never dispatched
    # is a promise the CLI does not keep, and `Mode.operand` feeds the entry point's
    # arity resolution — so a phantom declaration can bind a real operand as a flag's
    # argument.  That is the `--key --archive f.py` crash `modes()`'s docstring records.
    # ⚑ A FLAG TESTED ANYWHERE IN THE FILE IS DISPATCHED, NOT ONLY ONE INSIDE
    # `_dispatch`.  My first cut compared against `bounds` alone — the branches
    # `_dispatch` opens — and reported `--selftest` as DECLARED-never-dispatched.  It IS
    # dispatched, at the `__main__` guard (`:2559`), which is outside `_dispatch` by
    # construction because the suite must run without the CLI's argument binding.  A
    # false positive in the DANGEROUS direction, from a reader that mistook one
    # function's shape for the file's.
    # ⚑⚑ AND MY FIRST FIX KEYED ON ONE SPELLING OF `argv` AND MISSED THE ONE CASE.
    # `--selftest` is tested as `"--selftest" in flagged_argv()` (`:2568`) — the
    # POSIX-`--`-aware accessor, not the bare list — so a `(?:sys\.)?argv` pattern found
    # nothing and the false positive survived the repair. That is
    # `census-keyed-on-one-spelling`, committed inside the reader written to find roster
    # spelling disagreements. Match any `in <something>argv…` receiver.
    # ⚑⚑ THE SECOND DISCRIMINATOR — `writes` MUST BITE OR IT IS DECORATION.  `scans`
    # earned its place by having `_report_skipped` to check against; `writes` names the
    # artifact kinds a mode mutates, and the contract the corpus ALREADY declares for
    # that is `--apply`'s: *"a mutating tool invoked with NEITHER `--apply` nor
    # `--dry-run` must REFUSE, never guess"* (`toolmodes --conventions`, and its
    # `--declines` record guards precisely the "should default to dry" misreading).
    #
    # ⚑ MEASURED, AND IT IS WHY THE FIELD EXISTS: 39 of the corpus's tools are
    # HALF-PAIRED — 32 accept `--apply` with no `--dry-run`, 3 the reverse — so each
    # still has a silent default in the direction its own declared convention forbids.
    # A `Mode` that could not express "this branch writes" could not carry that
    # contract, and standardizing on the shape would have frozen the gap into every
    # file that adopted it.
    for flag, m in sorted(MODES.items()):
        if not m.writes or flag not in bounds:
            continue
        i, end = bounds[flag]
        body = "\n".join(lines[i:end])
        if "--apply" not in body and "--dry-run" not in body:
            out.append((flag, False,
                        "declares writes=%r but its branch tests neither --apply nor "
                        "--dry-run — a mutating mode with a silent default"
                        % (m.writes,)))
    _tested = set(re.findall(r'"(--[a-z-]+)"\s+in\s+\w*argv\w*\(?\)?', src))
    # ⚑⚑⚑ ⟡since-roster-disagreement — A FLAG DECLARED AS SOME MODE'S `opts` IS A
    # MODIFIER, NOT AN UNDECLARED MODE, AND THIS READER WAS THE LAST COPY WITHOUT THE
    # EXEMPTION.  `climode.contract_rows` — the GENERALISATION of this function — has
    # carried it since `schema.py --coverage`'s owned `--emit`/`--reap` were reported as
    # two top-level modes nobody declared.  This local copy never got it, so it reported
    # `FAIL --since`: a flag declared in `--commentary`'s `opts` (:945) AND in
    # `OPT_OPERANDS` (:923), whose branch (:3037) is NESTED INSIDE `--commentary`'s
    # (:3025).  It is correctly declared in both authorities; the FAIL was manufactured
    # by the reader.
    #
    # ⚑⚑ AND THE WIRED GATE WAS RIGHT ALL ALONG, WHICH IS THE INVERSION WORTH RECORDING.
    # `check_mode_contracts --where scratch/pycodemod.py` reports 0 findings over this
    # same roster and this same file, because it routes through `contract_rows`.  The
    # briefing read the split as "a real disagreement a green gate does not report" —
    # the repo's own distrust-the-green-gate reflex, fired at the one instrument that
    # was accurate.  The disagreement was between two READERS, and the stale one was the
    # one shouting.  A green gate is a fact about the census; so is a red one.
    #
    # ⚑ THE HONEST REPAIR IS THE EXEMPTION, NOT A ROSTER ROW.  Declaring `--since` in
    # `MODES` would silence this by making a modifier claim to be a mode — inverting the
    # roster exactly as the `--emit`/`--reap` incident did, and adding a NEW key to the
    # divergence ratchet for a mode that does not exist.
    _owned = {o for _m in MODES.values() for o in (_m.opts or ())}
    for flag in sorted(set(MODES) | set(bounds)):
        if flag in _owned and flag not in MODES:
            continue
        if flag in MODES and flag not in bounds and flag not in _tested:
            out.append((flag, False,
                        "DECLARED in MODES, never dispatched — a promise the CLI does "
                        "not keep, and its arity still feeds the entry point"))
        elif flag in bounds and flag not in MODES:
            i, end = bounds[flag]
            body = "\n".join(lines[i:end])
            hint = (" (its usage exists only as a runtime print — reachable only by "
                    "FAILING the mode)" if "usage: pycodemod.py" in body else "")
            out.append((flag, False,
                        "DISPATCHED, absent from MODES — undeclared arity" + hint))
    return out


def _report_skipped(where=None):
    """Name the files the last `scan()` could not read — or say nothing if none.

    ⚑⚑⚑ A ZERO FROM A SCAN THAT READ NOTHING LOOKS EXACTLY LIKE A ZERO FROM A CLEAN
    TREE, and on 2026-08-18 that was not hypothetical: a `NameError` in `_Scan.visit_If`
    was swallowed per-file, every `--calls` query in the corpus answered `0 def, 0 call,
    0 ref`, and `--dead` read GREEN on a file with 18 defs.  No warning, no exit code —
    a confident zero.  `--dead` is what this repo DELETES on.

    ⚑⚑ THE SKIP ITSELF IS CORRECT AND STAYS: one unparseable file must not abort a
    corpus query.  What was wrong is that it was INVISIBLE, so the population silently
    shrank and no number said so — SKILL.md:274, *a bare list can't distinguish "no
    matches" from "no file read"*.

    ⚑ `visit-failed` ON EVERY FILE IS A BROKEN QUERY, NOT A BROKEN TREE, and it is
    called out separately because the two read identically in the rows.  An unreadable
    file is a property of that file; a visitor defect is a property of the QUERY, so it
    empties the whole corpus while each individual skip looks routine.
    """
    # ⚑ `where` NAMES THE QUERY FUNCTION THAT GATHERED, defaulting to `scan`.  Two
    # functions carry this accounting now (`scan`, `sqlnames`), and reading `scan.skipped`
    # after a `sqlnames` run would report a DIFFERENT query's population — the stale-context
    # defect `KwIndex`'s stamp exists to prevent, reintroduced through the reporter.
    src = where or scan
    skipped = getattr(src, "skipped", None)
    if not skipped:
        return
    pop = getattr(src, "population", 0)
    kinds = {}
    for _p, why, exc in skipped:
        kinds.setdefault(why, []).append(exc)
    print(f"   ⚑ INCOMPLETE SCAN — read {pop - len(skipped)} of {pop} file(s); "
          f"{len(skipped)} skipped:")
    for why in sorted(kinds):
        excs = sorted(set(kinds[why]))
        print(f"     {why}: {len(kinds[why])} ({', '.join(excs)})")
    for p, why, exc in sorted(skipped)[:10]:
        print(f"       - {os.path.relpath(p, ROOT)}  [{why}: {exc}]")
    if len(skipped) > 10:
        print(f"       … and {len(skipped) - 10} more")
    if pop and len(skipped) == pop:
        print("   ⚑⚑ EVERY file was skipped — this is a BROKEN QUERY, not an empty "
              "result.\n      Do not read the counts above as a fact about the tree.")


def _print_layout(paths):
    files = py_files(*paths) if paths else py_files()
    for p in files:
        rows = layout(p)
        if not rows:
            continue
        print(f"── {os.path.relpath(p, ROOT)}")
        for kind, name, lo, hi, code in rows:
            print(f"  {kind:<6} {lo:>5}-{hi:<5} {code:>5} code  {name}")
        print(f"   {len(rows)} top-level group(s), {sum(r[4] for r in rows)} code lines")
    return 0


def _opt(flag):
    """Is this MODIFIER present? — the spelling that is invisible to the locator.

    ⚑ IT EXISTS FOR `scan_contract`, NOT FOR CONVENIENCE.  That reader finds a
    mode's branch by matching `if "--x" in sys.argv:` / `in flagged_argv():` at the
    head of a line, which is correct for MODES and wrong for MODIFIERS — a modifier
    written in that shape registers as a top-level mode absent from `MODES`, and
    `--check-contracts` FAILS it as undeclared arity.  Measured on `--misses` the
    minute `--ambient` was wired.  A modifier is declared in its owning `Mode`'s
    `opts`; this is how it is READ, so the two spellings cannot be confused by a
    reader that must distinguish them.
    """
    return flag in flagged_argv()


def _dispatch():
    """Every query, run against whatever `ROOT` currently is.

    ⚑ EXTRACTED SO `--archive` CAN ENCLOSE IT.  As long as the dispatch was
    module-level, an archive could only be another BRANCH inside it -- which is
    why `--archive` grew its own member-walk and then a `--show` bolt-on.  As a
    function it can be called inside `with corpus(...)`, and every mode answers
    about the archive with no per-mode work."""
    args = [a for a in flagged_argv() if not a.startswith("-")] + operand_tail()
    # ⚑ THE SCOPE TARGET IS CONSUMED BY THE ENVELOPE and must not also read as a
    # query argument -- otherwise `--archive X --calls foo` searches for `X`.
    # ⚑ AND IT MUST COVER EVERY SCOPE FLAG: I wrote this for `--archive`, added
    # `--in` three minutes later, and `--in persistqueue --calls resume_unack_tasks`
    # silently answered about `persistqueue` instead.  A guard listing the flags
    # it was written for is the frozen-roster shape; the flags come from one
    # tuple that both this and the entry point read.
    for _f in SCOPE_FLAGS:
        if _f in sys.argv:
            i = sys.argv.index(_f)
            rest = [a for a in sys.argv[i + 1:] if not a.startswith("-")]
            if rest and rest[0] in args:
                args = [a for a in args if a != rest[0]]
    # ⚑⚑ EVERY OPERAND-TAKING FLAG, NOT ONLY THE SCOPE ONES — and the loop above is the
    # frozen-roster shape it warns about, one flag family narrower. `--marks record` sent
    # `record` into `args` as a PATH, so the census refused with "no such path: record" for a
    # token that was never a path: the fifth instance of the operand-ownership class in this
    # ecosystem, and the third in MY tools after `--corpus` ate `--bib`'s operand and `--key`
    # ate `--archive`'s. `--since` grew a private subtraction (`a != argopt(...,"--marks")`)
    # which fixed ONE branch and left its sibling broken — the per-instance repair that leaves
    # the class alive.
    #
    # ⚑ `modes()` ALREADY KNOWS WHICH FLAGS CONSUME A TOKEN, derived from the dispatch itself,
    # so ownership is computed once here rather than re-derived per branch. A flag added
    # tomorrow is covered the moment it reads `sys.argv[i + 1]` — there is no list to update,
    # which is the whole reason `modes()` exists.
    # ⚑ THE DECLARATION FIRST, THE DERIVERS AS A WIDENING. `MODES`/`OPT_OPERANDS` state arity;
    # `modes()` and `argopt_flags()` still contribute so a mode not yet declared is not made
    # WORSE than before the table existed. The coherence selftest is what drives the union to
    # zero difference — a flag the derivers see and the table does not is a FAILURE, not a
    # silent fallback, which is the property the inference-only design could never have.
    # ⚑⚑ ONLY THE *MODIFIER* OPERANDS ARE STRIPPED, AND CONFLATING THE TWO KINDS BROKE EVERY
    # QUERY MODE FOR TEN MINUTES. A mode's own operand (`--calls <name>`) is read POSITIONALLY
    # out of `args[0]`, so removing it leaves the mode with no subject: `--calls modes <path>`
    # silently became "scan the whole corpus for nothing" and hung. A MODIFIER's operand
    # (`--marks <s>`) is read by `argopt` and must NOT survive in `args`, or it reads as a path.
    #
    # ⚑ THE DECLARATION IS EXACTLY WHAT SEPARATES THEM — `OPT_OPERANDS` versus `Mode.operand` —
    # and my first cut unioned both into one set, which is the same ad-hoc conflation the table
    # exists to end. The derivers cannot make this distinction at all: `modes()` reports only
    # THAT a flag consumes a token, never whether the consumer is the mode or a modifier.
    for _f in OPT_OPERANDS:
        if _f in sys.argv:
            _i = sys.argv.index(_f)
            if len(sys.argv) > _i + 1:
                _operand = sys.argv[_i + 1]
                if not _operand.startswith("-"):
                    args = [a for a in args if a != _operand]

    # ⚑⚑⚑ A FLAG-SHAPED OPERAND IS SILENTLY REBOUND, AND THE RESULT IS A FALSE ZERO — the
    # single worst failure this dispatch can produce, because every other defect in this
    # file announces itself. MEASURED (agda-F13, 2026-08-24):
    #
    #     pycodemod --literal "--builders" scratch/pipeflow.py
    #       → "'scratch/pipeflow.py': 0 literal site(s) in 0 of 824 file(s)"
    #
    # `--builders` starts with `-`, so the `args` comprehension above drops it as a flag;
    # `args[0]` is then the PATH, which becomes the needle, and the needle's own file
    # becomes the (empty) population. The tool reports a confident zero for a question it
    # was never asked. That zero PROPAGATED TWO DISPATCHES DEEP as established fact.
    #
    # ⚑ THE CAPABILITY WAS NEVER MISSING — `--` ALREADY ANSWERS THIS, and `_pycodemod_core`
    # documents it at length as the POSIX convention, added 2026-08-18 for exactly this
    # question. `pycodemod --literal -- --builders scratch/pipeflow.py` returns the correct
    # `compare scratch/pipeflow.py:2833`. So this is NOT a missing feature and the fix is
    # NOT a new parsing rule: it is that the working escape is UNDISCOVERABLE at the moment
    # you need it, because the failure mode is a plausible answer rather than an error.
    #
    # ⚑⚑ SO THE REPAIR IS A REFUSAL THAT NAMES ITS OWN SUCCESSOR. The roster is what makes
    # it decidable: `MODES[m].operand` says this mode consumes a token, so if the token
    # actually sitting after `m` in the flag slice is flag-shaped, the operand was eaten.
    # That is a fact about the ARGV, not a guess about intent — and it cannot fire on a
    # correct invocation, because a correct one either has a non-flag operand there or put
    # it after `--` (where `flagged_argv` never looks).
    #
    # ⚑ WHY THE ROSTER AND NOT `OPT_OPERANDS`: these are MODE operands, not modifier
    # operands, and the two are the distinction the block above nearly died on. Reading
    # arity from `MODES` also means a mode declared today is guarded today, with no second
    # list to update — the property that put `MODES` here in the first place.
    _flags = flagged_argv()
    for _m in _flags:
        _spec = MODES.get(_m)
        if _spec is None or not _spec.operand:
            continue
        # An OPTIONAL operand (spelled `[rel]`) has a legitimate bare form, so a missing
        # or flag-shaped next token is not an error for it — `--relname` is the case.
        if _spec.operand.startswith("["):
            continue
        _j = _flags.index(_m)
        _nxt = _flags[_j + 1] if _j + 1 < len(_flags) else None
        if _nxt is not None and _nxt.startswith("-"):
            print("pycodemod: %s expects <%s>, but the next token %r is flag-shaped and "
                  "was dropped." % (_m, _spec.operand, _nxt))
            print("  ⚑ REFUSING rather than rebinding. Without this, the following path "
                  "would have\n     silently become the operand and the answer would be a "
                  "CONFIDENT ZERO for a\n     question you did not ask (measured: "
                  "agda-F13).")
            print("  to ask about a flag-shaped operand, end the flags with `--`:")
            print("      pycodemod.py %s -- %s %s"
                  % (_m, _nxt, " ".join(a for a in _flags[_j + 2:]
                                        if not a.startswith("-")) or "[paths]"))
            sys.exit(2)

    # ⚑⚑⚑ AN UNRECOGNISED FLAG REFUSES, AND IT IS ONE CHECK FOR EVERY MODE.  `Mode.opts`
    # declared which modifiers a mode accepts and NOTHING READ THE FIELD — `--attr opts`
    # reports its only readers in `climode` itself, so the roster was a declaration with
    # no enforcement.  The consequence is the worse half of a blind spot: `--exits --list`
    # and `--exits --sites` were both SILENTLY DROPPED, and the mode printed its ordinary
    # confident output.  *"A flag that does nothing looks like a mode that ran."*  A wrong
    # NUMBER a reader can doubt; an ignored FLAG returns a confident answer to a question
    # the tool was never asked, and nothing in the output says so.
    #
    # ⚑⚑ THE PRECEDENT IS `toolmodes`, WHICH ALREADY REFUSES: *"Refusing rather than
    # running with a flag you did not mean; a silently ignored `--quiet` is a gate that
    # looks like it ran."*  Same repair, moved to where the shape is — this is ONE check
    # over `MODES`, not a per-branch `if` in ~60 dispatch bodies, because a per-mode patch
    # is the many-judgements-that-happen-to-agree failure the roster exists to end.
    #
    # ⚑ AND IT IS SCOPED SO IT CANNOT REFUSE A CORRECT INVOCATION.  It fires only when the
    # invoked mode IS declared (an undeclared mode has no roster to check against and is
    # already `--check-contracts`' business), and a token counts as known if ANY declared
    # mode, the scope flags, the modifier-operand tuple, or the modes-in-flight name it.
    # Anything after `--` is invisible to `flagged_argv`, so a flag-shaped OPERAND is
    # untouched. The cost of the narrow rule is that a flag belonging to mode A passed to
    # mode B still slips through; that is declared in the KNOWN-MISSES text rather than
    # closed by a wider rule, because widening here turns actionable rows into unactionable
    # refusals — the route-around invitation, in the check built to close it.
    # ⚑⚑ A SPELLING CAN BE BOTH A MODE AND ANOTHER MODE'S OPT, AND THAT COLLISION IS THE
    # ONE HOLE LEFT IN THIS CHECK.
    # ⚑⚑⚑ THE POPULATION IS A QUERY NOW, NOT THIS SENTENCE — `opt_key_collisions()`,
    # rendered by `--check-contracts`. This paragraph used to name `--sites` and warn "do
    # not assume it is the only one", which is a reader's homework rather than a fact; the
    # derivation returns THREE (`--sites`, `--kinds`, `--lines`) and grades each. It also
    # corrected this comment's own arithmetic: `--sites` is an opt of FOUR modes, not five.
    # A count restated in prose beside the roster that owns it is the drift shape this
    # file records one layer down, and it had already drifted here.
    # ⚑ ALL THREE ARE GRADED BENIGN, WHICH IS WHY THE RESIDUE STANDS RATHER THAN CLOSING.
    # The harm test is whether the two roles MEAN different things: all three are nullary
    # in both positions and both mean "per-site detail", so admitting the spelling on any
    # mode returns the reader what they asked for. A HARMFUL collision (an operand-taking
    # mode colliding with a bare modifier) would be a rename, and there are none.
    # `--sites` is declared as a MODE (`MODES["--sites"]`)
    # and ALSO in the `opts` of four other modes, so it is in `_known` for every
    # invocation: `--swallows --sites` still runs silently where `--swallows --misses`
    # correctly refuses.  Narrowing to "the first invoked mode wins" was tried and
    # REVERTED — dispatch order is branch order, not argv order, so that rule refuses
    # correct invocations, which is the widen/narrow trap this file records elsewhere
    # (*"each widening turned actionable rows into unactionable refusals"*).  The honest
    # move is to DECLARE the residue rather than close it with a rule that misfires: the
    # real repair is making a spelling be a mode XOR an opt, which is a roster change
    # that moves `toolmodes`' census and belongs to its own item.
    _invoked = [f for f in _flags if f in MODES]
    if _invoked:
        _known = set(MODES) | set(SCOPE_FLAGS) | set(OPT_OPERANDS)
        for _m in _invoked:
            _known |= set(MODES[_m].opts or ())
        # ⚑ `flagged_argv()` IS THE PRE-`--` SLICE, NOT THE FLAGS IN IT — it carries the
        # operands and paths that sit before the separator too.  Testing the whole slice
        # refused a correct invocation on its own PATH argument the first time this ran,
        # which is exactly the over-refusal the scoping paragraph above warns about.
        _unknown = [f for f in _flags if f.startswith("--") and f not in _known]
        if _unknown:
            print("pycodemod: unrecognised flag(s): %s" % " ".join(_unknown))
            print("  invoked mode(s): %s" % " ".join(_invoked))
            for _m in _invoked:
                _o = MODES[_m].opts
                print("      %-22s accepts: %s"
                      % (_m, " ".join(_o) if _o else "(no modifier flags)"))
            print("  ⚑ REFUSING rather than dropping it. A silently ignored flag returns a\n"
                  "     CONFIDENT answer to a question the tool never asked — worse than a\n"
                  "     wrong number, which a reader can at least doubt.")
            print("  if it was meant as an OPERAND, end the flags with `--`:")
            print("      pycodemod.py %s -- %s" % (_invoked[0], " ".join(_unknown)))
            sys.exit(2)

    # ⚑⚑ THE GATE WAS BLANKET AND MOST MODES DO NOT NEED THE DEPENDENCY. It refused EVERY mode
    # when libcst was absent, so `--size` (pure `ast` + `splitlines`), `--commentary` (pure
    # `splitlines`) and the rest reported as unavailable in a borrowing checkout — measured, by
    # a peer running this by symlink who concluded the tool could not answer a question it
    # answers fine. A capability that exists and is refused reads exactly like one that does
    # not exist, which is the absent-vs-empty distinction inside my own CLI.
    #
    # ⚑ SO THE PRECONDITION IS PER-MODE, AND IT IS DERIVED, NOT LISTED. `CST_MODES` names the
    # modes whose BODIES touch `cst`; a hand-maintained roster here would be the frozen-roster
    # shape this file retires everywhere else, and it would go stale the first time a mode
    # stopped needing the CST.
    _need = sorted(m for m in cst_modes() if m in sys.argv)
    if cst is None and _need:
        print("libcst is not importable — install it or use `uv run --with libcst`")
        print("  needed by: %s" % " ".join(_need))
        print("  ⚑ other modes DO run without it (`--size`, `--commentary`, `--imports`, …) —")
        print("     this refusal is scoped to the modes that parse a CST, not to the tool.")
        sys.exit(2)

    if "--binding" in sys.argv:
        if not args:
            print("usage: pycodemod.py --binding <name> [paths]")
            sys.exit(2)
        sys.exit(_print_bindings(args[0], args[1:]))

    if "--layout" in sys.argv:
        sys.exit(_print_layout(args))

    if "--literal" in sys.argv:
        if not args:
            print("usage: pycodemod.py --literal <text> [paths]")
            sys.exit(2)
        text, rest = args[0], args[1:]
        files = py_files(*rest) if rest else py_files()
        sites = literal_sites(text, files)
        # ⚑ THE ROLE ORDER IS THE WORK ORDER, not alphabetical.  `compare` first
        # because a dispatch branch is what a retirement DELETES; `doc` last
        # because a prose mention never blocks the code change.  Sorting these
        # by name would bury the four sites that matter under sixty that do not.
        _ORDER = ("compare", "arg", "decl", "other", "doc")
        by_role = {}
        for p, line, role, ctx, val in sites:
            by_role.setdefault(role, []).append((p, line, ctx, val))
        for role in _ORDER:
            for p, line, ctx, val in sorted(by_role.get(role, [])):
                v = val if len(val) <= 48 else val[:45] + "…"
                print(f"  {role:<8} {os.path.relpath(p, ROOT)}:{line}"
                      f"  {ctx}()  {v!r}")
        if by_role:
            print("  roles: " + ", ".join("%s=%d" % (r, len(by_role[r]))
                                          for r in _ORDER if r in by_role))
        hit = len({p for p, _l, _r, _c2, _v in sites})
        print(f"{text!r}: {len(sites)} literal site(s) in {hit} of "
              f"{len(files)} file(s)")
        sys.exit(0)

    if "--roundtrip" in sys.argv:
        files = py_files(*args) if args else py_files()
        bad = []
        for p in files:
            ok, detail = roundtrip(p)
            if not ok:
                bad.append(p)
                print(f"FAIL  {os.path.relpath(p, ROOT)}  {detail}")
        print(f"{len(files)} file(s); {len(files)-len(bad)} round-trip losslessly, "
              f"{len(bad)} do not")
        sys.exit(1 if bad else 0)

    if "--reaches" in sys.argv:
        # ⚑⚑⚑ THE MODE `--calls` STRUCTURALLY CANNOT BE. `--calls` records call sites
        # with no scope tracking, so it answers "where is this name called" and never
        # "which function does the calling" — which makes every REACHABILITY question
        # unanswerable, and reachability is what a dataflow trace needs. Measured need:
        # a python function that runs a SQL builder and writes through a HELPER has its
        # read and its write in two different bodies, so a same-body join reports no
        # round trip where there is one.
        if len(args) < 2:
            print("usage: pycodemod.py --reaches <caller> <callee>[,<callee>…] [paths]")
            sys.exit(2)
        start, targets, rest = args[0], set(args[1].split(",")), args[2:]
        files = py_files(*rest) if rest else py_files()
        cg = callgraph(files)
        # ⚑ A BARE `start` IS RESOLVED AGAINST THE GRAPH'S KEYS, so a caller may be given
        # as `pack_core_sql` or `sppf_db.pack_core_sql`. An unresolvable name is a
        # REFUSAL naming the population, never an empty result read as "reaches nothing".
        cands = [k for k in cg if k == start or k.rsplit(".", 1)[-1] == start]
        if not cands:
            print("pycodemod --reaches: no function named %r among %d caller(s) in "
                  "%d file(s) — this is 'not found', NOT 'reaches nothing'."
                  % (start, len(cg), len(files)))
            sys.exit(1)
        for c in sorted(cands):
            hits = reaches(cg, c, targets)
            for t in sorted(targets):
                path = hits.get(t)
                print("  %-34s %-14s %s" % (c, t, " → ".join(path) if path
                                            else "not reached within depth 6"))
        print("%d caller(s) named %r; %d target(s)" % (len(cands), start, len(targets)))
        sys.exit(0)

    if "--calls" in sys.argv:
        if not args:
            print("usage: pycodemod.py --calls <name> [paths]")
            sys.exit(2)
        name, rest = args[0], args[1:]
        rows = scan(py_files(*rest) if rest else None, name)
        nd = sum(1 for _p, k, _n, _l in rows if k == "def")
        nc = sum(1 for _p, k, _n, _l in rows if k == "call")
        # ⚑⚑ THE REF COUNT WAS IN HAND AND THE VERDICT IGNORED IT — and `dead()`,
        # reading the SAME `scan()` rows, has counted `ref` as a use since the
        # callbacks incident (`_pycodemod_query.dead`, "a use-as-value is a use").
        # Two consumers of one scan disagreed, and only this one prints a verdict
        # an operator DELETES on.  Measured 2026-08-18: `--calls test
        # scratch/verify_shadows.py` printed ⚑ DEAD CAPABILITY over 64 `@test`
        # decorator references listed IN ITS OWN OUTPUT, and `--calls _reflected
        # jea/metalanguage/lifecycle.py` did the same for a `.then("reflected", fn)`
        # table entry — in the file where two sibling links had ALREADY BEEN
        # DELETED on this evidence.  A verdict that contradicts the rows above it
        # is worse than a missing one: the rows look like the audit that confirms it.
        nr = sum(1 for _p, k, _n, _l in rows if k == "ref")
        for p, kind, _n, line in sorted(rows):
            print(f"{kind:<5} {os.path.relpath(p, ROOT)}:{line}")
        print(f"{name}: {nd} def(s), {nc} call(s), {nr} ref(s)")
        _report_skipped()
        if nd and not nc and nr:
            # ⚑ REACHED AS A VALUE, NOT INVOKED HERE.  A decorator target, a
            # registry entry, a `key=fn`, a `.then(…, fn, …)` link.  The def is
            # LIVE; what is absent is a syntactic call, which is a fact about the
            # SPELLING and not about the capability.
            print(f"   ⚑ NOT DEAD — reached as a VALUE at {nr} site(s) above "
                  f"(decorator, registry entry,\n     callback or table link). "
                  f"No syntactic call is not no caller.")
        elif nd and not nc:
            # ⚑⚑ A `q_`-PREFIXED DEF IS NOT DEAD JUST BECAUSE NOTHING CALLS ITS
            # PYTHON NAME.  The store's queries are invoked by STRING — `QB.run(con,
            # "obs_core")` — so `--calls q_obs_core` correctly finds zero calls and
            # the dead-capability verdict is FALSE.  Measured 2026-08-18: every
            # registered query in `query_decl.py` reports as dead here, and `--dead`
            # is the census this repo uses to decide what to delete.
            if name.startswith("q_"):
                _n_ref = len([r for r in sqlnames(name) if r[3] == "ref"])
                print(f"   ⚑ NOT DEAD — `{name}` is a REGISTERED QUERY, invoked by "
                      f"string, not by name.\n     `--sqlname {name[2:]}` finds "
                      f"{_n_ref} reference(s); this mode is blind to them "
                      f"by construction.")
            else:
                print(f"   ⚑ DEAD CAPABILITY — defined and never called "
                      f"(the rewire_only class)")
        sys.exit(0)

    if "--sqlname" in sys.argv:
        # ⚑ THE MODE THAT BRIDGES `def q_<name>` TO `QB.run(con, "<name>")`.  Two
        # spellings for one relation, and no reader joined them — the survey that
        # found this could only reach `core_fp_mtimes`'s call site by way of a
        # NEIGHBOURING name (`--binding stale`), i.e. by accident.
        if not args:
            print("usage: pycodemod.py --sqlname <query-name> [paths]\n"
                  "   (the name as INVOKED — `obs_core` — or as DEFINED — `q_obs_core`)")
            sys.exit(2)
        name, rest = args[0], args[1:]
        rows = sqlnames(name, py_files(*rest) if rest else None)
        nd = sum(1 for _p, _l, _q, k in rows if k == "def")
        nr = sum(1 for _p, _l, _q, k in rows if k == "ref")
        for p, line, _q, kind in rows:
            print(f"{kind:<5} {os.path.relpath(p, ROOT)}:{line}")
        bare = name[2:] if name.startswith("q_") else name
        print(f"{bare}: {nd} definition(s), {nr} reference(s)")
        # ⚑ THE THIRD ZERO-CASE, AND IT OUTRANKS THE OTHER TWO.  The branch below reads
        # `0 definitions` / `0 references` as facts about the CODE; a scan that read
        # nothing produces both and means neither.  `sqlnames` is the bridge that stops a
        # registered query reading as a DEAD CAPABILITY, so a silent zero here restores
        # exactly the false-dead verdict it exists to prevent.
        _report_skipped(sqlnames)
        # ⚑ THE TWO ZERO-CASES MEAN OPPOSITE THINGS and must not print alike.
        if nd and not nr:
            print("   ⚑ DEFINED AND NEVER REFERENCED — a genuinely unwired query "
                  "(this IS the dead-capability\n     verdict `--calls` cannot "
                  "reach for a registered query).")
        elif nr and not nd:
            print("   ⚑ REFERENCED WITH NO `q_` DEFINITION FOUND — either the "
                  "definition is spelled\n     differently, or this string is not "
                  "a query name at all.  A fact about the SEARCH.")
        sys.exit(0)

    if "--forwards" in sys.argv:
        if len(args) < 2:
            print("usage: pycodemod.py --forwards <name> <keyword> [paths]")
            sys.exit(2)
        name, kw, rest = args[0], args[1], args[2:]
        has, lacks = forwards(name, kw, py_files(*rest) if rest else None)
        for p, line in has:
            print(f"  ok      {os.path.relpath(p, ROOT)}:{line}")
        for p, line in lacks:
            print(f"  MISSING {os.path.relpath(p, ROOT)}:{line}")
        print(f"{name}(…{kw}=…): {len(has)} of {len(has)+len(lacks)} call site(s) "
              f"forward it; {len(lacks)} do NOT")
        sys.exit(0)

    if "--fix-owes-callers" in sys.argv:
        # ⚑⚑⚑ THE REVISION IS REQUIRED AND HAS NO DEFAULT — Ⓝ10, and this refusal IS the
        # scoping decision. "Call sites not updated in the same change" needs a change to
        # compare against; `HEAD` would be a GUESS AT THE AUTHOR'S INTENT, and the guess
        # is wrong in the commonest case (the widening is uncommitted, so HEAD contains
        # neither the def change nor the caller updates and every call site reads owed).
        # A confident answer to a question nobody asked is worse than a refusal.
        rev = argopt(sys.argv, "--rev")
        if not args or not rev:
            print("usage: pycodemod.py --fix-owes-callers <name> --rev <REV> [paths]\n"
                  "   <REV> is REQUIRED and has no default — the question needs a change\n"
                  "         to compare against, and assuming HEAD would guess at intent.\n"
                  "     --rev WORKING    the uncommitted diff against HEAD (the usual one:\n"
                  "                      the widening and the un-updated callers are both\n"
                  "                      in the working tree)\n"
                  "     --rev <range>    any expression `git diff --name-only` takes —\n"
                  "                      HEAD~1, abc123..def456, main...topic\n"
                  "   ⚑ reports a FLOOR. See the notes it prints.")
            sys.exit(2)
        name, rest = args[0], args[1:]
        owed, meta = fix_owes_callers(name, rev, py_files(*rest) if rest else None)
        if owed is None:
            print(f"CANNOT ANSWER — no census taken: {meta['refused']}")
            sys.exit(2)
        # ⚑⚑ A MALFORMED QUESTION IS REFUSED, NOT ANSWERED. If the change touched no file
        # containing a `def <name>`, then "callers not updated with it" has no referent —
        # and printing the un-touched call sites anyway would render as an alarming list
        # of real findings about a def that never changed.
        if not meta["defs_changed"]:
            print(f"{name}: the change ({meta['desc']}) touched NO file defining this "
                  f"name.\n  {meta['defs']} definition(s) found in the scanned population, "
                  f"0 of them in the change.\n"
                  f"  ⚑ 'callers not updated with it' has no referent — the def did not "
                  f"change. Not answered.")
            _report_skipped(scan)
            sys.exit(2)
        for p, line, kind in owed:
            print(f"  OWED {kind:<4} {os.path.relpath(p, ROOT)}:{line}")
        # ⚑ `n of m` — THE DENOMINATOR IS PRINTED. A bare list of owed sites cannot
        # distinguish "three callers were missed" from "three callers exist and none were
        # touched", and this arc has recorded four times that a tally without its
        # population becomes a stale dependency.
        print(f"{name}: {len(owed)} of {meta['uses']} use site(s) are in files the change "
              f"did NOT touch;\n  {meta['covered']} sit in changed files (presumed seen). "
              f"{meta['defs_changed']} of {meta['defs']} definition(s) changed.\n"
              f"  change = {meta['desc']} ({meta['changed_py']} .py file(s)); "
              f"scanned {meta['population']} file(s).")
        _report_skipped(scan)
        # ⚑⚑⚑ THE FLOOR IS NAMED EVERY TIME, and each clause is a measured blind spot
        # rather than boilerplate caution. Printing it only when something is found would
        # make the ZERO the misleading output — and a zero here reads as "nothing to fix".
        print("  ⚑ THIS IS A FLOOR, NOT A COUNT. Three blind classes, none closable here:")
        print("    1. NAME-SCOPED, not capability-scoped: an aliased call "
              "(`import m as _m; _m.f()`) is\n       invisible to a bare-token probe. "
              "MEASURED: `--calls tenant store.py` -> '0 calls, DEAD',\n"
              "       the same name over its real callers -> '7 calls'. See the "
              "alias cross-check below.")
        print("    2. A NAME IS NOT A DEFINITION: several unrelated defs may share this "
              "spelling, and\n       their call sites are all reported together.")
        print("    3. TOUCHED IS NOT UPDATED: a changed file is EXCLUDED on the "
              "assumption its author\n       looked at it — which is exactly what fails "
              "when a change edits it for another reason.")
        hint = meta["alias_hint"]
        if hint:
            # ⚑ A SITE COUNT AND A FILE COUNT ARE DIFFERENT FACTS — Ⓝ19. Before the
            # narrowing a row WAS a file (one aliasing import); now a row is a CALL SITE,
            # and three sites in one file printed as "3 file(s)" would overstate the
            # spread of the finding. Both numbers are reported because both are asked.
            _files = len({f for f, _l, _a, _m in hint})
            print(f"  ⚑ ALIAS CROSS-CHECK — {len(hint)} aliased call site(s) in "
                  f"{_files} file(s), recovered by joining the alias census against "
                  f"`--attr {name}`.\n    These are REAL reads of `.{name}` through an "
                  f"aliased module — blind-class-1 sites the bare-token census above "
                  f"cannot see:")
            for f, line, alias, module in hint:
                print(f"      {os.path.relpath(f, ROOT)}:{line}  via {alias}  (from {module})")
            # ⚑⚑ THE NARROWING DOES NOT MAKE THE CENSUS CAPABILITY-SCOPED, and saying so
            # here is load-bearing: a quieter, more precise arm reads as a stronger claim
            # unless it states its own residue. `--attr` matches `.name` on ANY receiver,
            # so a COMMON name over-reports; and this arm only ever reaches files that
            # alias a DEFINING module, so a call through some other indirection is still
            # invisible. Blind class 1 is NARROWED, never closed.
            print(f"    ⚑ still a floor: `--attr` matches `.{name}` on ANY receiver "
                  f"(exact for a distinctive name,\n      over-reporting for a common "
                  f"one), and only files aliasing a DEFINING module are reachable here.")
        else:
            # ⚑ AN EMPTY CROSS-CHECK IS A FACT ABOUT THE PROBE. `report presence, never
            # absence`: this found no aliased CALL of the name, which is not the same as
            # the call census being complete.
            # ⚑ AND THE TWO WAYS OF BEING EMPTY ARE NOT DISTINGUISHED HERE — no file
            # aliases a defining module, versus files do but none reads `.name`. Both are
            # honest zeros about this probe; neither licenses "the census is complete".
            print("  ⚑ ALIAS CROSS-CHECK found no aliased CALL of this name in this "
                  "population.\n    That is a fact about the PROBE (either nothing "
                  "aliases a defining module, or nothing\n    aliasing one reads "
                  "`.name`) — NOT a warrant that the call census is complete.")
        # ⚑ EXIT 0 REGARDLESS, and for the reason `--asserted` does: an owed call site is
        # not automatically a defect (a widened return may be backward-compatible). This
        # REPORTS. Exiting non-zero would make it a gate over an unsettled predicate —
        # the false-positive-into-a-ratchet hazard this arc has recorded twice.
        sys.exit(0)

    if "--asserted" in sys.argv:
        if len(args) < 2:
            print("usage: pycodemod.py --asserted <name> <keyword> [paths]")
            sys.exit(2)
        name, kw, rest = args[0], args[1], args[2:]
        lit, comp = asserted(name, kw, py_files(*rest) if rest else None)
        for p, line in lit:
            print(f"  LITERAL  {os.path.relpath(p, ROOT)}:{line}")
        for p, line in comp:
            print(f"  computed {os.path.relpath(p, ROOT)}:{line}")
        # ⚑ THE DENOMINATOR IS PRINTED, never a bare count of the interesting
        # half.  This arc recorded four times that a tally without its population
        # becomes a stale dependency.
        print(f"{name}(…{kw}=…): {len(lit)} of {len(lit)+len(comp)} call site(s) "
              f"pass a LITERAL; {len(comp)} compute it")
        # ⚑ EXIT 0 REGARDLESS.  A literal is not automatically a defect (a
        # genuinely singular population is honestly 1), so this REPORTS.  Exiting
        # non-zero would make it a gate over a predicate that has not been
        # settled — the false-positive-into-a-ratchet hazard, twice recorded.
        sys.exit(0)

    if "--values" in sys.argv:
        if len(args) < 2:
            print("usage: pycodemod.py --values <name> <keyword> [paths]")
            sys.exit(2)
        name, kw, rest = args[0], args[1], args[2:]
        sites, total = values(name, kw, py_files(*rest) if rest else None)
        # ⚑ GROUPED BY VALUE, because the population is the deliverable.  A flat
        # per-site list re-poses the question it answers — a reader auditing a
        # DESTRUCTIVE keyword wants "which sites pass the dangerous constant",
        # and counting 23 lines by eye to find the two that say `True` is the
        # arithmetic-by-eye the whole family exists to replace.
        groups = {}
        for p, line, v, ctx in sites:
            groups.setdefault(repr(v), []).append((p, line, ctx))
        for shown in sorted(groups):
            rows = groups[shown]
            print(f"  {kw}={shown}   ({len(rows)} site(s))")
            for p, line, ctx in rows:
                print(f"      {os.path.relpath(p, ROOT)}:{line}  in {ctx}()")
        n_unknown = len(groups.get("UNKNOWN", ()))
        # ⚑ `n of m` OVER THE CALL POPULATION.  A bare list cannot distinguish
        # *no site passes it* from *no file was read*, and this arc has recorded
        # four times that a tally without its denominator becomes a stale
        # dependency.
        print(f"{name}(…{kw}=…): {len(sites)} of {total} call site(s) pass it; "
              f"{len(sites) - n_unknown} carry a readable literal, "
              f"{n_unknown} are UNKNOWN (not a simple literal — NOT guessed)")
        # ⚑ EXIT 0 REGARDLESS, and for the same reason `--asserted` does: a value
        # is not automatically a defect.  Which constant is dangerous is a fact
        # about the CALLEE, and encoding a guess at it here would make this a gate
        # over an unsettled predicate — the false-positive-into-a-ratchet hazard.
        sys.exit(0)

    if "--types" in sys.argv:
        rows = type_errors(py_files(*args) if args else None)
        if rows is None or "__unrunnable__" in (rows or {}):
            why = (rows or {}).get("__unrunnable__", ["mypy not importable"])[0]
            print(f"CANNOT RUN — no census taken (an unmeasured tree is not a "
                  f"clean one):\n{why}\n"
                  f"  try:  uv run --with mypy python3 scratch/pycodemod.py --types")
            sys.exit(2)
        by_code = {}
        for key in rows:
            by_code.setdefault(key.split("::", 1)[0], 0)
            by_code[key.split("::", 1)[0]] += 1
        for code, n in sorted(by_code.items(), key=lambda kv: -kv[1]):
            print(f"  {code:<24} {n:>4} file(s)")
        print(f"{len(rows)} key(s) across {len(by_code)} error code(s)")
        sys.exit(0)

    if "--reifies" in flagged_argv():
        # ⚑ THE CENSUS THE ⟡sorted-stream-carrier ARC RAN BY HAND BEFORE THIS EXISTED.
        # A `--layout` + `--calls` + two reads, with the judgement about what counts as a
        # reification happening in the turn — exactly the shape the standing rule forbids,
        # committed while planning the arc about it.  A missing mode is WORK.
        # ⚑ USE THE DISPATCH-LEVEL `args`, NEVER `operand_tail()`. My first cut wrote
        # `args = operand_tail()`, which returns tokens after a POSIX `--` and NOTHING
        # otherwise — so `--reifies <path>` silently censused the whole 810-file corpus
        # and reported a confident answer to a question nobody asked. `_dispatch` already
        # computes operands once (:1194), with flag-operand ownership subtracted; a branch
        # that recomputes them is the per-branch parsing this file records five instances
        # of. `py_files` raises PopulationError on an unresolvable path, so a typo refuses.
        pop = py_files(*args) if args else None
        rows = reifies(pop)
        want = None
        for sel in ("set", "dict", "list", "sorted", "accum"):
            if f"--{sel}" in flagged_argv():
                want = sel
        shown = [r for r in rows if want is None or r[3] == want or r[4].endswith(want)]
        by_why = {}
        for _p, _l, _n, _k, why in rows:
            by_why[why] = by_why.get(why, 0) + 1
        for p, line, name, kind, why in shown:
            print(f"  {why:<14} {kind:<6} {os.path.relpath(p, ROOT)}:{line}  {name}()")
        print(f"{len(shown)} of {len(rows)} reification(s) over "
              f"{reifies.population} file(s)")
        for why, n in sorted(by_why.items(), key=lambda kv: -kv[1]):
            print(f"  {why:<16} {n:>4}")
        if by_why.get("returns-sorted"):
            # ⚑ THE ACTIONABLE ROW, AND THE ONLY ONE THAT NAMES A DOUBLE PAYMENT.  A def
            # that sorts and returns has paid for an order and then dropped the fact, so
            # its callers re-sort defensively.  Witnessed one hop apart in this corpus:
            # `agda_defs.import_index()` sorts AND says so in its docstring; `importers_of()`
            # re-sorts anyway.  There was nowhere on the value to put the claim.
            print(f"   ⚑ {by_why['returns-sorted']} def(s) RETURN sorted(...) — an order "
                  f"paid for and then discarded, so callers re-sort defensively.")
            print(f"     jea/metalanguage/sorted_stream.py carries the order ON the value; "
                  f"`Sorted(it, key, origin)` makes the claim survive the call.")
        _report_skipped(reifies)
        sys.exit(0)

    if "--funcnames" in flagged_argv():
        # ⚑ THE MODE `--portable` CANNOT BE. It EXPLAINs raw SQL literals; a Core statement is
        # never a string, so the file that raised `UndefinedFunction: group_concat` on every
        # invocation reported `0 blocking site(s)`.
        pop = py_files(*args) if args else None
        rows = funcnames(pop)
        verb = [r for r in rows if r[4] == "verbatim"]
        gen = [r for r in rows if r[4] == "generic"]
        only = "--verbatim" in flagged_argv()
        for p, line, caller, name, kind in (verb if only else rows):
            print(f"  {kind:<9} {name:<22} {os.path.relpath(p, ROOT)}:{line}  {caller}()")
        by_name = {}
        for _p, _l, _c, name, kind in verb:
            by_name[name] = by_name.get(name, 0) + 1
        print(f"{len(verb)} verbatim + {len(gen)} generic = {len(rows)} func.<name> call(s) "
              f"over {funcnames.population} file(s)")
        for name, n in sorted(by_name.items(), key=lambda kv: -kv[1]):
            print(f"  verbatim  {name:<22} {n:>4} site(s)")
        if verb:
            # ⚑ "UNVERIFIED BY CORE", NEVER "WRONG" — the instrument cannot support the
            # stronger claim. MEASURED: `func.totally_made_up_xyz` compiles identically on
            # postgres and sqlite, and `string_agg` (valid postgres) sits in the same bucket
            # as the invented name. SQLAlchemy has ONE registry (`_default`, 52 names) and no
            # per-dialect list to check against, so a mode claiming "this function does not
            # exist" would be inventing a verdict. Report presence, never absence.
            print(f"   ⚑ {len(verb)} call(s) pass a name through VERBATIM — Core does not "
                  f"translate these, so they are dialect-SPECIFIC and unchecked.")
            print(f"     This is what `store.py`'s 'Core is dialect-agnostic' guarantee does "
                  f"NOT reach, and what `--portable` cannot see.")
            print(f"     A verbatim name is NOT a defect — it is the population a migration "
                  f"must re-read. `group_concat` was one of these.")
        _report_skipped(funcnames)
        sys.exit(0)

    if "--resorts" in flagged_argv():
        # ⚑ THE CONSUMER ARM. `--reifies` sees producers; this sees the OTHER END, and the
        # pair is what makes "redundant" sayable at all — a span query, not a site query.
        pop = py_files(*args) if args else None
        rows = resorts(pop)
        dup = [r for r in rows if r[4] == "resort-of-sorted"]
        rek = [r for r in rows if r[4] == "resort-rekeyed"]
        for p, line, caller, callee, why in rows:
            print(f"  {why:<16} {os.path.relpath(p, ROOT)}:{line}  "
                  f"{caller}() re-sorts {callee}()")
        print(f"{len(rows)} re-sort(s) over {resorts.population} file(s) "
              f"— {len(dup)} redundant, {len(rek)} re-keyed")
        # ⚑⚑ A ZERO FROM THIS MODE MUST NOT READ AS "NOTHING DOUBLE-SORTS HERE", and until
        # 2026-08-19 it did. This is a SPAN query: it joins the walked files against a
        # PRODUCER census of defs that return sorted(...). If that census is thin — a narrow
        # corpus, an unreadable file, a libcst-less environment — the join finds nothing and
        # the summary line above is byte-identical to a genuinely clean result.
        #
        # ⚑ THE FAILURE MODE OF A BOUNDS-SHAPED READER IS SILENCE (linux-sources, 2026-08-19,
        # from building the same shape): a reader that finds nothing reads as "the claim is
        # unbounded" — the exact over-broad reading it exists to prevent — and NOTHING IN ITS
        # OWN OUTPUT CONTRADICTS THAT. So an empty result must state the basis it searched
        # against, not merely the count. Reported ALWAYS on a zero, never only on error.
        if not rows:
            print(f"   ⚑ ZERO IS A FACT ABOUT THIS JOIN, NOT A CLEAN BILL. Matched against a "
                  f"producer census over {resorts.producer_population} file(s)"
                  + (f" ({len(resorts.producer_skipped)} unread)"
                     if resorts.producer_skipped else "") + ".")
            print("     A callee outside that census cannot be joined against, so this is a "
                  "FLOOR. Only a DIRECT `sorted(callee(...))` is seen — a value bound to a "
                  "name and sorted later is invisible here.")
        if rek:
            # ⚑ REPORTED, NEVER COUNTED AS DEBT. A `key=`/`reverse=` is a DIFFERENT order,
            # so the second sort is real work. I read `swallows()` as a redundant re-sort of
            # a py_files() walk and was wrong — it sorts on the whole row tuple, not the path.
            # Folding these into one number would have banked that error as a finding.
            print("   ⚑ a re-keyed sort is NOT redundant — a different order is real work")
        if dup:
            print(f"   ⚑ {len(dup)} site(s) sort a value the callee ALREADY sorted, on the "
                  f"SAME key — the double payment ⟡sorted-stream-carrier exists to retire.")
        _report_skipped(resorts)
        # ⚑ BOTH ENDS OF THE SPAN OWE A REPORT.  A complete consumer walk over an INCOMPLETE
        # producer census silently reports fewer double payments than exist — the join lost
        # an endpoint, not a row. `_report_skipped` reads one function's accounting, so the
        # producer's is named on its own rather than folded in.
        if resorts.producer_skipped:
            print(f"   ⚑ INCOMPLETE PRODUCER CENSUS — read "
                  f"{resorts.producer_population - len(resorts.producer_skipped)} of "
                  f"{resorts.producer_population} file(s) when deriving which defs return "
                  f"sorted(...); a callee this walk could not read cannot be joined against, "
                  f"so this count is a FLOOR.")
        sys.exit(0)

    if "--discards" in sys.argv:
        # ⚑ NO NAME => SWEEP THE DERIVED POPULATION.  Naming one function answers one
        # question; the ITEM is "which verdicts does nobody read", and answering that
        # from a remembered list is the §69 miss (a hand-drawn population where the
        # repo can derive one).  `verdict_returners` discovers them.
        # ⚑ REPORT THE COST, DO NOT LEAVE IT TO BE INFERRED.  A corpus-wide CST sweep
        # is slow enough that a silent run is indistinguishable from a hung one — I
        # killed one working run and then GUESSED TWICE at which phase was expensive
        # (§55: *before reaching for concurrency, check whether the work is REPEATED*
        # — a rule about measuring, which I then failed to apply to my own tool).
        # Each phase announces itself and its elapsed time, so the next reader sees
        # where the time went instead of theorising.
        import time as _t
        _t0 = _t.time()
        if args:
            targets = {args[0]: None}
            rest = args[1:]
        else:
            print("scanning for verdict-returning defs …", flush=True)
            targets = verdict_returners()
            print(f"  {len(targets)} verdict-returner(s)  [{_t.time()-_t0:.1f}s]",
                  flush=True)
            rest = []
        pop = py_files(*rest) if rest else None
        # ⚑ ONLY NAMES WITH A BARE CALL NEED THE SECOND WALK.  `discards` computes the
        # USING side with `scan`, which is per-name; asking it about a function nobody
        # drops is a full corpus walk to report zero.  The bare-call index already
        # knows which names can possibly have a finding, so the expensive half runs
        # only for those — the same repeated-work correction as `_bare_calls` itself.
        _t1 = _t.time()
        bare = _bare_calls(tuple(pop) if pop else None)
        # ⚑ ONLY NAMES THIS CORPUS DEFINES.  The first sweep reported 362 discarding
        # sites across 3 names — and 361 were `print`, whose bare call IS its purpose.
        # A builtin that returns `None` on one path and a value on another satisfies
        # the verdict SHAPE while being the opposite of a verdict, and 361 noise rows
        # bury the 1 real one: §60's rule that a predicate carrying false positives
        # does not merely over-report, it HIDES the true positives among them.
        # `verdict_returners` already yields only defs found in the corpus, so the
        # intersection is the fix — no allow-list, nothing to rot.
        # (the single-name path stores `None` as its value, so gate on the SWEEP,
        # not on the value — a truthiness test here would silently make
        # `--discards <name>` find nothing, which is the guard-degrades class again)
        cand = [n for n in sorted(targets) if n in bare]
        if not args:
            print(f"  {len(bare)} name(s) called bare; {len(cand)} of "
                  f"{len(targets)} verdict-returner(s) among them "
                  f"[{_t.time()-_t1:.1f}s]", flush=True)
        total_drop, rows = 0, []
        for nm in cand:
            using, dropped = discards(nm, pop)
            if not dropped:
                continue
            total_drop += len(dropped)
            rows.append((nm, using, dropped))
        for nm, using, dropped in rows:
            print(f"{nm}(): {len(using)} of {len(using)+len(dropped)} site(s) use it")
            for p, line in dropped:
                print(f"    DISCARDS  {os.path.relpath(p, ROOT)}:{line}")
        if args and not rows:
            using, _d = discards(args[0], pop)
            for p, line in using:
                print(f"  ok       {os.path.relpath(p, ROOT)}:{line}")
            print(f"{args[0]}(): all {len(using)} call site(s) USE the return value")
        else:
            print(f"{len(targets)} verdict-returning def(s) examined; "
                  f"{len(rows)} have a DISCARDING call site ({total_drop} site(s))")
        if total_drop:
            print(f"   ⚑ a returned verdict that nobody reads is an INERT GUARD — "
                  f"present, greppable, and doing nothing")
        # ⚑ THE SWEEP PERSISTS ITS OWN CENSUS.  A multi-minute corpus walk whose
        # result lives only in a terminal is one the next reader must re-run, and the
        # reflex is to redirect it to a scratch file the tool knows nothing about —
        # which §44 already recorded as the reprocessing loop wearing a different
        # shape.  Same fix as `.leaf-verify.tsv` + `--last`: the ledger is the tool's.
        # Written only for a FULL sweep; a scoped run answers a scoped question and
        # must not overwrite the population's record (§51's scoped-run clobber).
        if not args:
            with open(DISCARD_LEDGER, "w", encoding="utf-8") as fh:
                # ⚑ STAMP THE PREDICATE, NOT JUST THE COUNTS.  A ledger read after the
                # predicate changed describes the OLD predicate — the stale-baseline
                # hazard at ledger granularity, and it cost me a wrong reading within
                # minutes of writing this file (I attributed 361 rows to a name the
                # current predicate excludes).  The hash is over the two functions
                # that decide the population, so `--last` can say when it is stale.
                import hashlib as _h
                _pred = _h.sha1(
                    (inspect.getsource(verdict_returners)
                     + inspect.getsource(_bare_calls)).encode()).hexdigest()[:12]
                fh.write(f"# verdict-returners={len(targets)}\tcandidates={len(cand)}"
                         f"\telapsed={_t.time()-_t0:.1f}s\tpredicate={_pred}\n")
                for nm, using, dropped in rows:
                    for p, line in dropped:
                        fh.write(f"{nm}\t{os.path.relpath(p, ROOT)}\t{line}\n")
            print(f"  census → {os.path.relpath(DISCARD_LEDGER, ROOT)}  (read with --last)")
        sys.exit(0)

    if "--last" in sys.argv:
        if not os.path.exists(DISCARD_LEDGER):
            print("no --discards census recorded; run: pycodemod.py --discards")
            sys.exit(1)
        import hashlib as _h
        now = _h.sha1((inspect.getsource(verdict_returners)
                       + inspect.getsource(_bare_calls)).encode()).hexdigest()[:12]
        lines = open(DISCARD_LEDGER, encoding="utf-8").read().splitlines()
        for ln in lines:
            print("  " + ln if not ln.startswith("#") else ln)
        # ⚑ REFUSE TO PRESENT A CENSUS TAKEN UNDER A DIFFERENT PREDICATE AS CURRENT.
        was = next((p.split("=", 1)[1] for l in lines if l.startswith("#")
                    for p in l.split("\t") if p.startswith("predicate=")), None)
        # ⚑ STATE THE VERDICT IN THE OUTPUT, NOT ONLY IN THE EXIT CODE.  A reader who
        # has to run `echo $?` to learn whether a census is trustworthy is reading a
        # program's status by hand — the same reasoning-not-codified shape as piping
        # to `tail`.  The exit code stays for scripts; the LINE is for people.
        if was != now:
            print(f"VERDICT: STALE — recorded under predicate "
                  f"{was or '(unstamped)'}, the code now computes {now}.")
            print("  These rows describe the OLD population; re-run --discards.")
            sys.exit(1)
        print(f"VERDICT: CURRENT — predicate {now} matches the recorded census.")
        sys.exit(0)

    if "--discriminates" in sys.argv:
        # ⚑ BARE = SWEEP THE DISCOVERED POPULATION (2026-08-05).  Fixed arity made
        # this a CAPABILITY bound: the question T18 asks is *"which of our suites
        # are decoration"*, which is about every selftest-bearing module, and the
        # only way to ask it was a shell `for` loop — a composition the toolkit
        # forbids, and one whose result nobody could re-run.  The population is
        # DISCOVERED (defines `_selftest`), never listed, so a tool that grows a
        # suite is swept without editing anything here.
        paths = [os.path.abspath(p) for p in args]
        if not paths:
            for f in py_files():
                try:
                    if re.search(r'^def _selftest\(', open(f, encoding="utf-8").read(), re.M):
                        paths.append(f)
                except OSError:
                    continue
        blind, quiet = 0, len(paths) > 1
        for p in paths:
            rows = discriminates(p)
            # ⚑ IN A SWEEP, PRINT THE ROWS THAT SAY SOMETHING.  A per-file dump of
            # four `n/a` lines across ~30 modules buries the finding in its own
            # output — which is what makes a reader reach for `| grep`, i.e. the
            # judgement leaving the program again.  A single-file run stays verbose.
            shown = rows if not quiet else [r for r in rows if r[1] != "n/a"]
            if shown:
                print(f"{os.path.relpath(p, ROOT)}")
            for name, verdict, detail in shown:
                mark = {"DISCRIMINATES": "ok  ", "BLIND": "BLIND", "n/a": "  - "}[verdict]
                print(f"  {mark}  {name:<26} {detail}")
            blind += sum(1 for r in rows if r[1] == "BLIND")
        # ⚑ `n of m`: how many suites were SWEPT, not only what was found.
        print(f"{len(paths)} selftest-bearing module(s) swept")
        # ⚑ BLIND IS REPORTED, NEVER EXIT-CODED.  A mutator names ONE defect class and a
        # suite may legitimately not cover it; failing the run would make this a coverage
        # gate over a hand-written mutator list — an allow-list that rots.  The verdict
        # pair is the finding; the operator decides which blind spots are owed a case.
        print(f"{blind} blind spot(s) — a BLIND row is 'not covered', not 'defective'")
        sys.exit(0)

    if "--available" in sys.argv:
        i = sys.argv.index("--available")
        mods = [a for a in sys.argv[i + 1:] if not a.startswith("-")]
        if not mods:
            print("usage: pycodemod.py --available <module> [module ...]")
            sys.exit(2)
        rows = available(mods)
        for m, verdict, detail in rows:
            print("  %-9s %-16s %s" % (verdict, m, detail))
        absent = [m for m, v, _d in rows if v == "ABSENT"]
        # ⚑ ABSENT IS REPORTED, NEVER EXIT-CODED AS FAILURE.  A missing library
        # is a fact about this environment, not a defect -- and `uv run --with`
        # can supply one on demand.  Exit 1 would make "we do not vendor numpy"
        # look like a broken tool.
        print("%d of %d importable here" % (len(rows) - len(absent), len(rows)))
        sys.exit(0)

    if "--escapes" in sys.argv:
        # ⚑ FOUND BY THE CLASS GUARD, NOT BY ME.  I fixed `--key` and `--attr` and
        # would have stopped there; the scan over `_dispatch` named FOUR more
        # sites.  That is the whole argument for guarding a class rather than its
        # instances — §7b-bis, which this arc recorded three times in one day.
        files = py_files(*args) if args else py_files()
        rows = escapes(files)
        for p, ln, text, seq in rows:
            print("  %-4s %s:%d\n       %s"
                  % (seq, os.path.relpath(p, ROOT), ln, text[:100]))
        print("%d invalid escape(s) in %d of %d file(s)"
              % (len(rows), len({p for p, _l, _t, _s in rows}), len(files)))
        sys.exit(1 if rows else 0)

    if "--imports" in sys.argv:
        rows = imports(py_files(*args) if args else py_files())
        for top, verdict, n, example in rows:
            print("  %-11s %-24s %3d file(s)  e.g. %s"
                  % (verdict, top, n, example))
        # ⚑ REPORT THE POPULATION BY VERDICT, NOT A TALLY.  "48 imports" hides the
        # only two rows that are work: an UNDECLARED dep breaks a fresh clone, a
        # MISSING one is already broken here.
        counts = {}
        for _t, v, _n, _e in rows:
            counts[v] = counts.get(v, 0) + 1
        print("  ".join("%s=%d" % (k, counts[k]) for k in sorted(counts)))
        owed = counts.get("UNDECLARED", 0) + counts.get("MISSING", 0)
        print("%d of %d import(s) are undeclared or missing" % (owed, len(rows)))
        sys.exit(0)

    if "--importers" in sys.argv:
        if not args:
            print("usage: pycodemod.py --importers <module> [paths]")
            sys.exit(2)
        name, rest = args[0], args[1:]
        files = py_files(*rest) if rest else py_files()
        rows = importers(name, files)
        for p, line, form, bound in rows:
            print("  %-7s %s:%d  %s"
                  % (form, os.path.relpath(p, ROOT), line, ", ".join(bound)))
        # ⚑ THE UNDERSCORE HALF IS CALLED OUT, because it is the half a
        # `from <mod> import *` re-export SILENTLY DROPS — and a suite that reads
        # green afterwards is measuring the drop, not refuting it.
        # ⚑ ONLY THE `from` FORMS. `import query_defs as _qd` binds a `_`-prefixed
        # LOCAL ALIAS and reaches nothing through a re-export surface — reporting it
        # here would be a false positive in a query someone acts on, which this
        # toolkit's own rule calls a bug rather than a caveat. Caught by running it.
        priv = sorted({n for _p, _l, f, b in rows if f.startswith("from")
                       for n in b if n.startswith("_")})
        print("%s: %d import site(s) in %d of %d file(s)"
              % (name, len(rows), len({p for p, _l, _f, _b in rows}), len(files)))
        if priv:
            print("   ⚑ %d name(s) a star-re-export CANNOT carry: %s"
                  % (len(priv), ", ".join(priv)))
        sys.exit(0)

    if "--aliases" in sys.argv:
        files = py_files(*args) if args else py_files()
        rows = aliases(files, local_only="--all" not in sys.argv)
        by_form = {}
        for _p, _l, form, _m, _b, _s in rows:
            by_form[form] = by_form.get(form, 0) + 1
        bad = [r for r in rows if r[2] not in ALIAS_COMPLIANT]
        if "--sites" in sys.argv:
            for p, line, form, mod, bound, scope in bad:
                print("  %-9s %-6s %s:%d  %s  (%s)"
                      % (form, scope, os.path.relpath(p, ROOT), line, mod,
                         ", ".join(bound)))
        print("  ".join("%s=%d" % (k, by_form[k]) for k in sorted(by_form)))
        # ⚑ THE COMPLIANT COUNT IS PRINTED BESIDE THE VIOLATIONS, never the violations
        # alone. A bare "N violations" cannot distinguish a corpus that is mostly compliant
        # from one where nothing is — and the ratio is the whole question when deciding what
        # adopting the policy costs.
        ok = sum(by_form.get(f, 0) for f in ALIAS_COMPLIANT)
        infunc = sum(1 for r in bad if r[5] == "func")
        print("%d of %d local import(s) violate bare-import; %d compliant (BARE)"
              % (len(bad), len(rows), ok))
        # ⚑ SCOPE IS REPORTED, NOT EXCUSED. `import x` in a function body is COMPLIANT (the
        # operator banned the `from` form there, not the bare one), so this line counts only
        # violations that are also deferred — the sites where a cycle-break or a lazy
        # dependency has to be re-expressed as a bare import rather than removed.
        if infunc:
            print("   %d of those sit inside a function body (deferred: cycle-break or "
                  "lazy dep — re-express as `import x`, do not delete)" % infunc)
        print("   forms: BARE compliant; FROM/FROM-AS/FROM-STAR select names; "
              "AS-MOD relabels the module; RELATIVE is positional")
        sys.exit(0)

    if "--collision-apex" in sys.argv:
        files = py_files(*args) if args else py_files()
        bands = collision_apex(files)
        shown = 0
        for band, rows in bands:
            print("== %s: %d name(s)" % (band, len(rows)))
            for name, nsites, nskel, holes, labels, nspine, spine_shared in rows:
                shown += 1
                # ⚑ `holes is None` IS NOT `holes == 0`, AND COLLAPSING THEM INVERTS THE
                # VERDICT.  None means no two sites shared a skeleton at all — the
                # weakest possible result — while 0 means they were structurally
                # IDENTICAL, the strongest.  Printed as distinct tokens for that reason.
                # ⚑ THE LABEL NAMES THE KEY THAT FAILED, NEVER AN ABSENCE.  This column
                # read `no-shared-skeleton`, and I turned that into the prose claim "202
                # distinct entry points, no lift at all" — an absence-claim built on ONE
                # discriminator, which the spine rung then refuted (81/202 share a shape).
                # `report presence, never absence`: `full_skeleton` not matching is a fact
                # about `full_skeleton`, and the column now says so in its own name.
                verdict = ("IDENTICAL" if holes == 0 else
                           "deep-key-no-match" if holes is None else
                           "%d hole(s)" % holes)
                # ⚑ THE SIGNAL IS THE COLLAPSE RATIO, NOT `nskel > 1`.  A first cut
                # flagged BRIDGE on every row, because a name with many sites almost
                # always has more than one skeleton — a predicate true of everything
                # separates nothing.  14 sites collapsing to 11 skeletons is weak
                # sharing (a convention name); 14 to 2 is a lift.  `covered` is how many
                # sites actually sit in a >=2-member cluster, which is the ONLY number
                # that says how much of the name the verdict speaks for.
                covered = len(labels)
                # ⚑ TWO RUNGS OF ONE GRADED KEY, AND THE DISAGREEMENT IS THE FINDING.
                # `deep` is `full_skeleton` (every child, operators included — what
                # `templatize` needs to emit a re-parseable template).  `spine` is
                # `head_spine` (the wedge quotient chain, children dropped).  A row that
                # is 0/N deep and high on spine is a SHARED SHAPE WITH DIVERGENT DETAIL
                # — parameterisable, and precisely what "convention name" wrongly
                # dismissed.  Reporting only the strict rung called 202 `main`s "no two
                # bodies alike", which was a fact about the discriminator.
                flag = ""
                if covered and covered < nsites:
                    flag = "  ⚑ BRIDGE (some sites share deeply, others do not)"
                elif not covered and spine_shared:
                    flag = "  ⚑ SHAPE-SHARED, DETAIL-DIVERGENT (parameterisable)"
                elif not covered and not spine_shared:
                    # ⚑ NOT "unrelated" — two rungs were tried and neither matched.  A
                    # third (unhold / carrier-abstracted, jea_pysim --shape) is not run
                    # here, so this is the boundary of what was MEASURED, not a verdict
                    # about the bodies.
                    flag = "  — neither rung matched (2 keys tried, not a verdict)"
                print("   %-30s %3d site(s)  deep %3d/%-3d (%2d skel, %s)   "
                      "spine %3d/%-3d (%2d)%s"
                      % (name, nsites, covered, nsites, nskel, verdict,
                         spine_shared, nsites, nspine, flag))
        print("%d colliding name(s) over %d file(s), graded by sharing-breadth"
              % (shown, len(files)))
        print("   ⚑ keyed on BODY STRUCTURE, not the name — `--collisions` keys on the "
              "spelling and cannot rank these")
        print("   deep = full_skeleton (every child + operators; templatize's key)  ·  "
              "spine = head_spine (the wedge quotient chain)")
        print("   ⚑ A LOW deep WITH A HIGH spine IS NOT 'NOTHING IN COMMON' — it is one "
              "shape with divergent detail, i.e. the parameterisable case")
        print("   ⚑ TWO RUNGS ARE TRIED, NOT ALL OF THEM: a carrier-abstracted key "
              "(jea_pysim --unhold / --shape) is NOT run here, so a row matching neither")
        print("     bounds what was MEASURED and is not a verdict that the bodies differ")
        sys.exit(0)

    if "--collisions" in sys.argv:
        files = py_files(*args) if args else py_files()
        kinds = collision_kinds(files)
        want = argopt(sys.argv, "--kind")
        known = [k for k, _v in kinds]
        # ⚑ AN UNKNOWN KIND REFUSES, as `--control`'s and `--fingerprint`'s do. Silently
        # returning nothing for a typo is the false-zero shape this toolkit files against.
        if want and want not in known:
            print("pycodemod.py --collisions --kind: no such kind %r; known: %s"
                  % (want, ", ".join(known) or "(none — corpus has no collisions)"))
            sys.exit(2)
        total = 0
        for kind, rows in kinds:
            if want and kind != want:
                continue
            total += len(rows)
            print("== %s: %d name(s)" % (kind, len(rows)))
            if "--sites" in sys.argv:
                for name, sites in rows:
                    print("   %s" % name)
                    for p, line in sites:
                        print("       %s:%d" % (os.path.relpath(p, ROOT), line))
        # ⚑ THE KINDS NAME DIFFERENT REPAIRS, which is why the partition is the answer and a
        # bare total is not. `local` is python-scoped apart and ambiguous to nobody; `sibling`
        # is a candidate lift OR a genuine per-file entry point; `crossing` is the class that
        # bit — a reader who finds one assumes the other's contract.
        print("%d colliding name(s) in %d file(s)"
              % (total, len(files)))
        print("   local=python-scoped apart · sibling=candidate lift or per-file entry "
              "point · crossing=one name, two contracts")
        # ⚑ DELEGATING DEFS ARE NOT COUNTED, and that is load-bearing: four one-line
        # wrappers around one authority are a CONVERGED alias family, not four rivals.
        # Counting `def` sites finds the defect AND its repair and cannot tell them apart.
        print("   (reimplementing defs only — delegating wrappers are a converged family)")
        sys.exit(0)

    if "--package" in sys.argv:
        i = sys.argv.index("--package")
        rest = [a for a in sys.argv[i + 1:] if not a.startswith("-")]
        if not rest:
            print("usage: pycodemod.py --package <module> [defname]")
            print("  where an INSTALLED module's source lives, and its defs —")
            print("  the reuse-search's route to a dependency, which py_files()")
            print("  excludes by construction (site-packages is not our corpus).")
            sys.exit(2)
        modname = rest[0]
        base, detail = package_root(modname)
        if base is None:
            print("  ABSENT    %s  %s" % (modname, detail))
            # ⚑ ABSENT IS A FACT ABOUT THIS ENVIRONMENT, NOT A DEFECT — the same
            # reasoning `--available` records; `uv run --with` can supply one.
            print("0 of 1 resolvable here")
            sys.exit(0)
        print("  PRESENT   %s  %s" % (modname, detail))
        want = rest[1] if len(rest) > 1 else None
        files = py_files(base)
        rows = []
        for p in files:
            # ⚑ `_cached_defs` YIELDS (name, line, delegating) -- THREE fields, and
            # my first unpack invented a `kind` to filter on, so every row was
            # discarded and a populated package reported `0 def(s)`.  Read the
            # producer before writing the consumer; a plausible tuple shape is
            # still a guess.
            for defname, line, delegating in _cached_defs(p):
                if want and defname != want:
                    continue
                rows.append((os.path.relpath(p, base), defname, line, delegating))
        for rel, defname, line, delegating in sorted(rows)[:200]:
            print("  %-11s %-34s %s:%d"
                  % ("DELEGATES" if delegating else "def", defname, rel, line))
        print("%d def(s) across %d file(s)%s"
              % (len(rows), len(files),
                 " (first 200 shown)" if len(rows) > 200 else ""))
        sys.exit(0)

    if "--rivals" in sys.argv:
        i = sys.argv.index("--rivals")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --rivals <name> [paths]")
            sys.exit(2)
        name = sys.argv[i + 1]
        _scope = [a for a in args if a != name]
        rows = rivals(name, py_files(*_scope) if _scope else py_files())
        for p, line, verdict, callee, n in rows:
            extra = f"-> {callee}" if callee else f"{n} statement(s)"
            print(f"  {verdict:<13} {os.path.relpath(p, ROOT)}:{line}  {extra}")
        _re = [r for r in rows if r[2] == "REIMPLEMENTS"]
        print(f"{name}: {len(rows)} def(s) — {len(_re)} reimplementing, "
              f"{len(rows) - len(_re)} delegating")
        # ⚑⚑⚑ `REIMPLEMENTS` IS A PER-DEF FACT ("has a body of its own"), AND THE SUMMARY
        # LINE ABOVE READS AS A CROSS-DEF ONE ("these are rivals").  Measured 2026-08-19:
        # `--rivals scan` reported `3 def(s) — 3 reimplementing`, and the three are a
        # libcst corpus scanner, an Agda import-collision walker, and an Agda carrier-decl
        # extractor.  Three unrelated jobs sharing a common English verb — and one of
        # them EXISTS to prevent duplication (`check_carrier_locality.scan`'s own
        # docstring: *"Carved out of main() so a pre-flight can reuse the exact extraction
        # rather than re-implement"*).  `--rivals ping` is the recorded first instance
        # (`tsdbprobe.ping` is a TSDB write-then-read heartbeat, not a valkey RESP ping).
        #
        # ⚑⚑⚑ AND THIS IS THE THIRD PATCH OF ONE PATTERN, WHICH MEANS THE PATTERN IS THE
        # THING (operator, 2026-08-19: *"there's a pattern at play that's not getting
        # properly lifted"*).  `--calls emit` missed `_emit_one`; `--sqlname` exists
        # because `def q_x` and `QB.run("x")` never meet; `--rivals ping` grouped a TSDB
        # heartbeat with a valkey RESP ping; `--rivals scan` groups three unrelated jobs;
        # `--literal log_fallthrough` reported 0 of 3 files holding its call sites.  Every
        # one is: A CENSUS KEYED ON A SPELLING, REPORTING ITS KEY AS THE RELATION.
        #
        # ⚑⚑ THE RULE IS ALREADY WRITTEN SIX TIMES AND ENFORCED ZERO.  `--literal 'a fact
        # about the METHOD'` finds it in six separate docstrings — `commentary_kinds`,
        # `swallows`, `applied_imports`, `pycodemod`'s own banner, `shared_cache.stats`,
        # `_argv_aliases` — each added AFTER an instance bit that author.  Six independent
        # statements of one law is not documentation; it is six people paying the same
        # toll.  The lift is a shared DISCRIMINATOR every name-keyed census consults, not
        # a seventh prose paragraph.  Filed as ⟡spelling-census-lift; the per-mode fix
        # below stays because withdrawing a false claim now beats withdrawing it later.
        #
        # ⚑ SIGNATURE IS SOUND IN ONE DIRECTION ONLY.  Two defs with disjoint parameters
        # cannot substitute for one another, so they are NOT rivals — safe.  Matching
        # signatures prove nothing, so this never claims rivalry, only withdraws it.
        # Same asymmetry as `--guarded`'s else-branch: over-report, never invert.
        if len(_re) > 1:
            import inspect as _insp
            _sigs = {}
            for p, line, _v, _c, _n in _re:
                try:
                    _src = open(p, encoding="utf-8").read()
                    _t = ast.parse(_src)
                    for _d in ast.walk(_t):
                        if isinstance(_d, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                                and _d.name == name and _d.lineno == line:
                            _sigs[(p, line)] = tuple(
                                a.arg for a in _d.args.args)
                except Exception:
                    _sigs[(p, line)] = None      # unresolved → claims nothing
            _shapes = {v for v in _sigs.values() if v is not None}
            if len(_shapes) > 1:
                print("   ⚑ THESE MAY NOT BE RIVALS — the definitions take DIFFERENT "
                      "parameters:")
                for (p, line), sg in sorted(_sigs.items()):
                    print(f"     {os.path.relpath(p, ROOT)}:{line}  "
                          f"({', '.join(sg) if sg else '?'})")
                print("     A def cannot substitute for one it cannot be called like, so\n"
                      "     these share a NAME, not necessarily a JOB. `REIMPLEMENTS` is a\n"
                      "     per-def fact (has a body of its own) — read it that way, and\n"
                      "     open the docstrings before calling this duplication.")
        # ⚑ THE VERDICT NAMES THE POPULATION THAT IS ACTUALLY DEBT.  A count of
        # `def` sites conflates the divergence with its repair; only the
        # reimplementing rows are the convergence work.
        if not _re and rows:
            print("   every definition delegates — the bodies have CONVERGED; "
                  "what remains is\n   aliases binding a root, which is not the "
                  "duplication the item names.")
        sys.exit(0)

    if "--attr" in sys.argv:
        i = sys.argv.index("--attr")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --attr <name> [paths]")
            sys.exit(2)
        name = sys.argv[i + 1]
        # ⚑ THE SAME TWO DEFECTS AS `--key`, ONE MODE OVER — which is why F5 is a
        # CLASS and not an instance.  Row-derived denominator (cannot tell "no
        # matches" from "no files searched") and `or None` (an empty scoped
        # population silently widens to the whole corpus).
        scope = [a for a in args if a != name]
        files = py_files(*scope) if scope else py_files()
        rows = attr_reads(name, files)
        for p, line, ctx in rows:
            # the receiver-scoped form `Recv.*` already carries the WHOLE name in `ctx`
            # (`SF._module_params`); printing it as `.Recv.* in SF._module_params` reads
            # as if the receiver were the attribute. Report the reached name directly.
            print(f"  {os.path.relpath(p, ROOT)}:{line}  {ctx}" if name.endswith(".*")
                  else f"  {os.path.relpath(p, ROOT)}:{line}  .{name}  in {ctx}")
        print(f"{name}: {len(rows)} attribute read(s) in "
              f"{len({p for p, _, _ in rows})} of {len(files)} file(s)")
        if not files:
            print("   ⚑ NO FILES SEARCHED — a fact about the QUERY, not the name.")
        sys.exit(0)

    if "--size" in sys.argv:
        _all, nfiles = module_size_all(py_files(*args) if args else None)
        rows = [r[:5] for r in _all if r[4]]
        # ⚑⚑ PHYSICAL LINES ARE PRINTED BESIDE CODE LINES, AND ONLY CODE IS COMPARED TO THE
        # CAP. Measured 2026-08-11: `sppf_db.py` read `1060 code — OK, 140 under its cap`
        # at ~1800 physical lines, so the mode reported a pass on a file past the point the
        # rule names ("too large to read whole and write back out"). The cap stays on code
        # — `module_size`'s docstring is right that counting ⚑ commentary as bulk would
        # flag the best-documented modules as the worst — but a number that is never shown
        # cannot inform the reader either. Printed, not enforced.
        _phys = {r[0]: r[7] for r in _all}
        for p, code, defs, entry, why in sorted(rows, key=lambda r: -r[1]):
            flag = "⚑" if entry > 1 else " "
            print(f" {flag} {os.path.relpath(p, ROOT):<52} {code:>5} code  "
                  f"{_phys[p]:>5} phys  {defs:>4} defs   {why}")
        # ⚑ A NAMED FILE THAT PASSES MUST STILL REPORT, or the mode cannot answer the question
        # a SPLIT asks. Filtering to violations means a module just cut from 1,208 to 1,068
        # comes back as an empty list — which reads identically to "no file was read", the
        # absent-as-finding collapse. Naming a path IS asking about it, so a named path always
        # gets a line; the unscoped corpus run still reports only the violations.
        if args:
            for p, code, defs, _e, why, cap, hits, phys in sorted(_all,
                                                                  key=lambda r: -r[1]):
                if why:
                    continue
                # ⚑ THE RATIO IS THE READABLE FORM OF THE GAP. `1800 phys / 993 code` says
                # "this file is 45% commentary" — which in THIS corpus is a virtue, and is
                # exactly why the cap must not move; what it also says is how much a reader
                # must scroll past, which is the quantity the reading rule is about. Two
                # raw numbers make that comparison possible without asserting a verdict on
                # it, and there is deliberately no threshold on the second.
                print(f"   {os.path.relpath(p, ROOT):<52} {code:>5} code  {phys:>5} phys  "
                      f"{defs:>4} defs   "
                      f"OK — {cap - code} line(s) under its {cap} cap"
                      f"{' (halved ×%d)' % hits if hits else ''}")
        # ⚑ THE DENOMINATOR IS THE POPULATION, NOT THE MATCHES — the shape the class-guard
        # in `_selftest` refuses, and the reason it is written `of {len(`.
        _multi = sum(1 for _p, _c, _d, e, _w in rows if e > 1)
        print(f"{len(rows)} over-large or multi-entry module(s) of {nfiles} scanned "
              f"(threshold {OVERLARGE_LINES} code lines)")
        if _multi:
            print(f"  ⚑ {_multi} with MORE THAN ONE `if __name__` guard — a module has one "
                  f"entry point;\n    a second is dead code that looks live, and if the "
                  f"first exits, everything after\n    it is unreachable as a CLI.")
        sys.exit(0)

    if "--split" in sys.argv:
        # ⚑ THE OPERAND IS ONE FILE, NOT A CORPUS, AND THAT IS NOT A FIXED-ARITY DEFECT.
        # Every other census here answers about a population; a cut is performed on a single
        # module, and the parts it writes are decided by THAT module's own dependency graph.
        i = sys.argv.index("--split")
        if i + 1 >= len(sys.argv) or sys.argv[i + 1].startswith("-"):
            print("usage: pycodemod.py --split <file> [--max N] [--max-defs N] [--prefix P]")
            print("                    [--keep a,b] [--export all|public|a,b] [--apply]")
            print("  Cut one module into SIBLING modules under per-file bounds.")
            print("  --max     the LINE bound, counted the way a size gate counts (default 1200)")
            print("  --max-defs the DEFINITION bound — top-level def/class per part.  COMPOSES")
            print("            with --max rather than replacing it: a part must satisfy both.")
            print("            It is the bound an ADDITION's blast radius scales with (a Δ cache")
            print("            keys on a module's qualname SET, so adding a def invalidates every")
            print("            reader), which a line bound is structurally blind to.  Default:")
            print("            unbounded, so existing plans are unchanged.")
            print("  --prefix  sibling basename prefix (default '<stem>_')")
            print("  --keep    names whose statement stays in the entry module; the __main__")
            print("            guard always does")
            print("  --export  what the entry module re-exports so `import <mod>` still")
            print("            resolves the same attributes (default: every public name)")
            print("  --apply   write it.  Without this it only reports the plan.")
            sys.exit(2)
        _ex = argopt(sys.argv, "--export", "public")
        sys.exit(_print_split(
            os.path.abspath(sys.argv[i + 1]),
            max_lines=int(argopt(sys.argv, "--max", 1200)),
            max_defs=(int(argopt(sys.argv, "--max-defs"))
                      if argopt(sys.argv, "--max-defs") is not None else None),
            prefix=argopt(sys.argv, "--prefix"),
            keep=[x for x in (argopt(sys.argv, "--keep", "") or "").split(",") if x],
            export=_ex if _ex in ("all", "public") else set(_ex.split(",")),
            apply_it=argflag(sys.argv, "--apply")))

    if "--commentary" in sys.argv:
        # ⚑ THE MARK SET IS THE CALLER'S, AND FREEZING IT IN THE CLI WAS THE HARDCODED-
        # VOCABULARY DEFECT.  `commentary_census` takes `marks` precisely so a borrowing repo
        # can name its own glyphs; the CLI passed the default and no invocation could reach
        # the parameter.  A corpus that writes its incident log in plain `#` prose (gcalculus'
        # claim ledger) measured as ZERO marker lines — an empty result reading as a clean
        # split.  `--marks ''` is the degenerate and most useful case: every line is a marker,
        # so `--since` becomes a TOTAL preservation gate over the group.
        _marks = argopt(sys.argv, "--marks")
        _marks = COMMENTARY_MARKS if _marks is None else tuple(_marks.split(","))
        # ⚑ THE `--since` FORM IS THE GATE; THE BARE FORM IS ONLY A CENSUS. A split that drops
        # one note and adds another keeps the total, so the total alone cannot refuse it.
        if "--since" in sys.argv:
            _i = sys.argv.index("--since")
            _ref = sys.argv[_i + 1] if len(sys.argv) > _i + 1 else ":"
            _paths = [a for a in args if a != _ref and a != argopt(sys.argv, "--marks")]
            if not _paths:
                print("usage: pycodemod.py --commentary <paths...> --since <git-ref>")
                print("  <git-ref> defaults to ':' (the index) — 'before I started' in a")
                print("  working tree.  Name the ORIGINAL file AND every sibling the split")
                print("  created; the comparison is over the GROUP, which is the only level")
                print("  at which a relocation is distinguishable from a deletion.")
                sys.exit(2)
            _lost, _new, _b, _a, _where = commentary_lost(_paths, _ref, _marks, _origins=True)
            # ⚑ A LOST LINE MUST NAME THE FILE IT LEFT, or the gate cannot separate "my split
            # dropped it" from "it was already gone before I started". Measured on the very
            # first real run: `--since :` over a file with UNSTAGED in-flight edits compares
            # against the INDEX, which is older than the split's actual starting point, so two
            # lines removed by someone else's uncommitted work were reported against the split.
            # The ref is the caller's to choose; naming the origin is what makes the report
            # readable when the choice is imperfect.
            for t in _lost:
                print(f"  LOST   [{', '.join(sorted(set(_where.get(t, []))))}]  {t[:96]}")
            for t in _new:
                print(f"  new    {t[:110]}")
            print(f"{_b} ⚑ line(s) at {_ref!r} → {_a} now over {len(_paths)} file(s); "
                  f"{len(_lost)} LOST, {len(_new)} new")
            if not _b:
                print("   ⚑ THE BASELINE IS EMPTY — a fact about the REF, not the split. None of "
                      "these\n     paths exist at %r, so nothing was compared." % _ref)
            elif not _lost:
                print("   ⚑ every ⚑ line present before is present somewhere in the group now — "
                      "the\n     relocation preserved the incident log.")
            sys.exit(1 if _lost else 0)
        # ⚑ THE MIGRATABLE POPULATION IS NOT THE CENSUS. A mark inside a `check(...)` name or a
        # `lines.append(...)` refusal message is not documentation of behaviour — it IS the
        # behaviour, argument welded to the code that runs it, which is the end state a
        # claim-migration is trying to reach. Counting those as prose overcounts what can move.
        # ⚑ THE BLOCK FORM IS THE ONE A CLUSTERING CAN READ. A line-keyed census fragments a
        # paragraph and drops every continuation line (they carry no mark), so a corpus scan
        # over `--lines` clusters on sentence fragments. This reports the extent, the owning
        # def, and the symbols the incident CITES — the last being the join from a defect to
        # the tool that already handles it, which existed only in prose.
        if "--blocks" in sys.argv:
            _b = commentary_blocks(py_files(*args) if args else None, _marks)
            _cited = {}
            for _p, _s, _e, _own, _syms, _t in _b:
                _rel = os.path.relpath(_p, ROOT)
                _span = f"{_s}-{_e}" if _e > _s else f"{_s}"
                print(f"  {_rel}:{_span}  in {_own or '<module>'}")
                if _syms:
                    print(f"      cites  {' '.join(_syms[:12])}")
                print(f"      {_t[:150]}")
                for _sym in _syms:
                    _cited.setdefault(_sym, set()).add(_rel)
            _multi = {k: v for k, v in _cited.items() if len(v) > 1}
            print(f"{len(_b)} ⚑ incident block(s) over "
                  f"{len({r[0] for r in _b})} file(s); {len(_cited)} distinct symbol(s) cited, "
                  f"{len(_multi)} cited from MORE THAN ONE file")
            # ⚑ A SYMBOL CITED FROM SEVERAL FILES IS THE SHAPE→REMEDY EDGE, and it is the only
            # row here that is not already visible per-file. Several unrelated modules recording
            # an incident that names the SAME tool is what "one law, six tolls" looks like from
            # the code side — the paraphrase clustering cannot see it, because the sentences
            # differ and only the citation is shared.
            for _sym, _where in sorted(_multi.items(), key=lambda kv: -len(kv[1]))[:25]:
                print(f"  {len(_where):>3}×  {_sym:<28} {' '.join(sorted(_where)[:4])}")
            return
        if "--kinds" in sys.argv:
            _k = commentary_kinds(py_files(*args) if args else None, _marks)
            for _kind in ("comment", "docstring", "executable", "unparsed"):
                _v = _k[_kind]
                print(f"  {_kind:<12} {len(_v):>5} mark(s)")
                if "--lines" in sys.argv:
                    for _p, _ln, _t in _v:
                        print(f"      {os.path.relpath(_p, ROOT)}:{_ln}  {_t[:80]}")
            _tot = sum(len(v) for v in _k.values())
            _mig = len(_k["comment"]) + len(_k["docstring"])
            print(f"{_tot} mark(s); {_mig} in prose, {len(_k['executable'])} ALREADY EXECUTABLE"
                  f" — the executable ones are not migratable, they are the target state.")
            return
        _rows, _texts, _nf = commentary_census(py_files(*args) if args else None, _marks)
        for p, n, distinct in sorted(_rows, key=lambda r: -r[1]):
            print(f"  {os.path.relpath(p, ROOT):<52} {n:>5} ⚑ line(s)"
                  f"{'' if n == distinct else f'   ({distinct} distinct)'}")
        # ⚑ A COUNT IS NOT A LISTING, AND READING ONE AS THE OTHER COST AN EXCHANGE. The census
        # reported `15 ⚑ line(s), 15 distinct` and I concluded a specific sentence was ABSENT from
        # the file — from a total I had never expanded.  The mode had the texts in hand the whole
        # time (`_texts` maps normalized line → sites) and no way to print them, so its only
        # answer was HOW MANY while its reader believed they had read WHICH.  A peer had to open
        # the file by hand to produce the line I said was not there; it was, at line 116.
        if "--lines" in sys.argv:
            for _k, _v in sorted(_texts.items(), key=lambda kv: kv[1][0]):
                for _p, _ln in _v:
                    print(f"  {os.path.relpath(_p, ROOT)}:{_ln}  {_k[:96]}")
        _total = sum(n for _p, n, _d in _rows)
        print(f"{_total} ⚑ commentary line(s), {len(_texts)} distinct, across "
              # ⚑ JOINED ON `,`, NOT ON NOTHING. `''.join` rendered a widened set as
              # `NBRACE.PROVENANCE.Counter-intuitively` — unreadable, and NOT the string the
              # caller passed to `--marks`, so the one line reporting the census's scope could
              # not be read back as its input. A census that cannot state its own denominator
              # legibly is the `n of m` rule failing on the `m`.
              f"{len(_rows)} of {_nf} file(s)   marks={','.join(_marks) or '<every line>'}")
        # ⚑ THE VERDICT MUST NAME THE TREE IT SCANNED. A wrong-population answer is well-formed,
        # plausible, and carries no signal that it is wrong — a peer nearly banked my 6,005
        # flags as their own repo's, caught only by recognising my filenames. `n of m` was
        # never enough: it states the denominator without stating WHOSE. Printed only for a
        # DEFAULT-corpus scan, since that is the case where the caller named no path.
        if not args:
            print(f"  scanned the default corpus under {ROOT}")
        # ⚑ THE SUM IS THE PRESERVATION NUMBER FOR A SPLIT, and it is only readable over the
        # WHOLE GROUP.  Run it on the module before, then on the module AND its new siblings
        # after: the totals must match.  `--roundtrip` cannot answer this — it is per-file, and
        # a decomposition is exactly the transform that changes which file a line lives in.
        _dupes = {k: v for k, v in _texts.items() if len(v) > 1}
        if _dupes and args:
            print(f"  ⚑ {len(_dupes)} marker text(s) appear in MORE THAN ONE place — after a "
                  f"split that is a COPY,\n    not a move, and the two copies drift "
                  f"independently:")
            for k, v in sorted(_dupes.items(), key=lambda kv: -len(kv[1]))[:10]:
                print(f"    {len(v)}×  {k[:88]}")
                for p, ln in v[:4]:
                    print(f"          {os.path.relpath(p, ROOT)}:{ln}")
        if not _nf:
            print("   ⚑ NO FILES SEARCHED — a fact about the QUERY, not the corpus.")
        sys.exit(0)

    if "--projects" in sys.argv:
        rows = paperkit_projects()
        for rel, cfg, warrants, foreign in rows:
            if "_error" in cfg:
                print(f"  BROKEN  {rel}  paper.toml unparseable: {cfg['_error']}")
                continue
            print(f"── {rel}")
            print(f"     title    {cfg.get('title', '(untitled)')!r}")
            print(f"     out      {cfg.get('out', 'paper.md')}   "
                  f"rubric {cfg.get('rubric', 'rubric.tsv')}")
            print(f"     warrants {warrants}")
            for tok, dest, who in foreign:
                print(f"     FOREIGN  {tok}  ->  {dest}   owned by: {who}")
        nf = sum(1 for _r, _c, _w, f in rows if f)
        print(f"{len(rows)} paperkit project(s); {nf} import a FOREIGN bib")
        sys.exit(0)

    if "--source" in sys.argv:
        i = sys.argv.index("--source")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --source <name> [paths]")
            sys.exit(2)
        name = sys.argv[i + 1]
        _scope = [a for a in args if a != name]
        _files = py_files(*_scope) if _scope else py_files()
        rows = source_of(name, _files)
        for p, line, end, text in rows:
            print(f"── {os.path.relpath(p, ROOT)}:{line}-{end}  {name}")
            print(text)
        # ⚑ I FIXED THIS MODE'S `or None` AND LEFT ITS DENOMINATOR — the class
        # guard caught the half I did not look at, which is the whole reason it
        # scans a SHAPE rather than asserting the sites I remembered.
        print(f"{name}: {len(rows)} definition(s) in "
              f"{len({p for p, _, _, _ in rows})} of {len(_files)} file(s)")
        sys.exit(0)

    if "--state" in sys.argv:
        # ⚑ THE POPULATION FOR "WHICH CACHES ARE PROCESS-LOCAL", asked
        # structurally rather than from memory.  A row is module-level mutable
        # state; a `const` row is a lookup table nothing writes and is NOT a
        # cache — printed anyway, because excluding it silently would make the
        # denominator a judgement.
        _scope = [a for a in args]
        _files = py_files(*_scope) if _scope else py_files()
        _rows, _n = module_state(_files)
        _cache = [r for r in _rows if r[3] == "cache"]
        _accum = [r for r in _rows if r[3] == "accum"]
        _const = [r for r in _rows if r[3] == "const"]
        for p, nm, line, klass, muts, kind in _cache:
            print(f"  {kind:<5} {os.path.relpath(p, ROOT)}:{line}  {nm}"
                  f"   mutated by {{{', '.join(muts)}}}")
        # ⚑ THE SET-ASIDE POPULATIONS ARE COUNTED, NOT HIDDEN.  A census that
        # silently dropped `accum`/`const` would make its own denominator a
        # judgement — and the first cut of this mode reported 145 rows of which
        # ~134 were accumulators, so the size of what is excluded is exactly the
        # number a reader needs to sanity-check the predicate.
        print(f"{len(_cache)} process-local CACHE(s) in "
              f"{len({r[0] for r in _cache})} of {_n} file(s)"
              f"   ({len(_accum)} accumulator(s), {len(_const)} const table(s) "
              f"set aside)")
        if not _files:
            print("   ⚑ NO FILES SEARCHED — the scope matched nothing.")
        sys.exit(0)

    if "--diagnose" in sys.argv:
        i = sys.argv.index("--diagnose")
        rest = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        # ⚑ A CLASS NARROWS THE ROUTING, and it is checked against `ROUTE` so a
        # typo refuses rather than silently routing nothing.
        k = rest[0] if rest and rest[0] in ROUTE else None
        sys.exit(_print_diagnose([a for a in rest if a != k], key=k))

    if "--crossings" in sys.argv:
        i = sys.argv.index("--crossings")
        sys.exit(_print_crossings([a for a in sys.argv[i + 1:]
                                   if not a.startswith("--")],
                                  summary="--summary" in sys.argv))

    if "--sql" in sys.argv:
        i = sys.argv.index("--sql")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --sql <identifier> [paths]")
            sys.exit(2)
        sys.exit(_print_sql(sys.argv[i + 1],
                            [a for a in sys.argv[i + 2:]
                             if not a.startswith("--")]))

    if "--relname" in sys.argv:
        i = sys.argv.index("--relname")
        args = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        # ⚑ THE OPERAND IS OPTIONAL AND THE BARE FORM IS THE REMOVAL CHECK — see
        # `_print_relname`. A first non-flag token that names an existing PATH is a
        # path, not a relation: `--relname jea/` must census the subtree rather than
        # hunt a relation called `jea/`.
        nm = args[0] if args and not os.path.exists(args[0]) else ""
        sys.exit(_print_relname(nm, args[1:] if nm else args))

    if "--snapshots" in sys.argv:
        i = sys.argv.index("--snapshots")
        sys.exit(_print_snapshots([a for a in sys.argv[i + 1:]
                                   if not a.startswith("--")]))

    if "--relalg" in sys.argv:
        i = sys.argv.index("--relalg")
        sys.exit(_print_relalg([a for a in sys.argv[i + 1:]
                                if not a.startswith("--")]))

    if "--control" in sys.argv:
        i = sys.argv.index("--control")
        # ⚑ THE `in sys.argv` TEST IS NOT REDUNDANT WITH `argopt` — it is what makes the
        # sub-flag VISIBLE to `toolmodes`.  That census reads accepted flags off the AST
        # by anchoring a `--flag` literal to the argument vector; a flag reaching argv
        # only through a HELPER CALL is dispatched and invisible, which is the same
        # can't-say-what-its-own-modes-are defect `--banner` exists to close, one level
        # down.  Measured here: `--constructs` (a Compare) was seen, `--kind` was not.
        _k = argopt(sys.argv, "--kind") if "--kind" in sys.argv else None
        # ⚑ A TYPO IN `--kind` MUST REFUSE, NOT SILENTLY REPORT ZERO.  An unknown kind
        # filtered against every row yields an empty table that reads exactly like "this
        # corpus has no control flow of that kind" — the absent-as-finding collapse, and
        # the roster is right here to check against.
        if _k is not None and _k not in CONTROL_KINDS:
            print("unknown kind %r; the roster is: %s" % (_k, ", ".join(CONTROL_KINDS)))
            sys.exit(2)
        sys.exit(_print_control([a for a in sys.argv[i + 1:]
                                 if not a.startswith("--") and a != _k],
                                summary="--summary" in sys.argv,
                                kind=_k,
                                constructs="--constructs" in sys.argv))

    if "--fingerprint" in sys.argv:
        i = sys.argv.index("--fingerprint")
        # ⚑ THE SUB-FLAG NAMES ARE SPELLED AS `in sys.argv` TESTS FOR THE SAME REASON
        # `--control`'s are: `toolmodes` reads accepted flags off the AST by anchoring a
        # `--flag` literal to the argument vector, so a flag reaching argv only through a
        # helper call is dispatched and INVISIBLE to the mode census.
        _fk = argopt(sys.argv, "--kind") if "--kind" in sys.argv else None
        # ⚑ THE SAME REFUSAL `--control` MAKES, and for the same reason: an unknown kind
        # filtered against every row yields an empty table that reads exactly like "this
        # corpus has no control flow of that kind" — absence wearing a finding's clothes.
        if _fk is not None and _fk not in CONTROL_KINDS:
            print("unknown kind %r; the roster is: %s" % (_fk, ", ".join(CONTROL_KINDS)))
            sys.exit(2)
        _from = argopt(sys.argv, "--from", "") if "--from" in sys.argv else ""
        _seed = argopt(sys.argv, "--seed", "") if "--seed" in sys.argv else ""
        _top = int(argopt(sys.argv, "--top", 10)) if "--top" in sys.argv else 10
        _grp = int(argopt(sys.argv, "--groups", 8)) if "--groups" in sys.argv else 0
        _keys = int(argopt(sys.argv, "--keys", 20)) if "--keys" in sys.argv else 0
        # ⚑ EVERY SUB-FLAG'S OPERAND IS SUBTRACTED FROM THE PATH LIST, and missing one is
        # how `--key --archive f.py` once bound a mode operand as a corpus path.  The
        # operands are stripped by VALUE rather than by position because `argopt` already
        # resolved them, so the two readings cannot drift.
        _consumed = {_fk, _from, _seed} | {str(_top), str(_grp), str(_keys)}
        sys.exit(_print_fingerprint(
            [a for a in sys.argv[i + 1:]
             if not a.startswith("--") and a not in _consumed],
            from_entries=[x for x in _from.split(",") if x],
            kind=_fk, top=_top,
            seed=[x for x in _seed.split(",") if x],
            groups=_grp, keys=_keys,
            monotone="--monotone" in sys.argv))

    if "--rawreads" in sys.argv:
        i = sys.argv.index("--rawreads")
        sys.exit(_print_rawreads([a for a in sys.argv[i + 1:]
                                  if not a.startswith("--")]))

    if "--portable" in sys.argv:
        i = sys.argv.index("--portable")
        sys.exit(_print_portable([a for a in sys.argv[i + 1:]
                                  if not a.startswith("--")]))

    if "--key" in sys.argv:
        i = sys.argv.index("--key")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --key <string-key> [paths]")
            sys.exit(2)
        name = sys.argv[i + 1]
        # ⚑ `n of m`, ALWAYS — AND THIS MODE WAS THE ONE THAT DID NOT.  The count
        # was `len({p for p, _, _, _ in rows})`, DERIVED FROM THE MATCHED ROWS, so
        # an empty result is structurally `0 file(s)` and "no matches" is
        # indistinguishable from "no files searched".  `_print_bindings` states the
        # rule verbatim ten mode-blocks away, and its comment calls this "the exact
        # failure this session kept hitting" — after which this mode went on to
        # mislead me three more times in one day, most sharply on `RESULT`, where
        # `--binding` answered `1 of 1` for the same question.
        #
        # ⚑ AND THE `or None` WAS A SECOND, WORSE DEFECT.  `py_files(...) or None`
        # turns an EMPTY scoped population into `None`, which `key_reads` reads as
        # THE WHOLE CORPUS — so a scoped query that matches no files silently
        # widens to everything and reports the result as if it were scoped. The
        # population is now computed ONCE, passed explicitly, and printed.
        scope = [a for a in args if a != name]
        files = py_files(*scope) if scope else py_files()
        rows = key_reads(name, files)
        for p, line, kind, ctx in rows:
            print(f"  {kind:<5} {os.path.relpath(p, ROOT)}:{line}  "
                  f"[{name!r}]  in {ctx}")
        reads = [r for r in rows if r[2] == "read"]
        decls = [r for r in rows if r[2] == "decl"]
        hit = len({p for p, _, _, _ in rows})
        print(f"{name!r}: {len(reads)} read(s), {len(decls)} declaration(s) in "
              f"{hit} of {len(files)} file(s)")
        # ⚑ AN EMPTY POPULATION IS A FINDING ABOUT THE QUERY, NOT ABOUT THE CODE.
        # Without this, `--key foo nosuchdir/` prints a confident `0 of 0` that
        # reads exactly like "this key is unused".
        if not files:
            print("   ⚑ NO FILES SEARCHED — the scope matched nothing, so this is "
                  "a fact about the\n     QUERY, not about the key. Check the paths.")
        # ⚑ THE DICT-SHAPED DEAD FIELD.  Declared in a schema tuple and never
        # read is the same verdict `--dead` gives a def with no caller; without
        # the split it would hide inside the total.
        if decls and not reads:
            print("   ⚑ DECLARED BUT NEVER READ — a dead field: the schema names "
                  "it, no consumer\n     projects it.")
        sys.exit(0)

    if "--banner" in sys.argv:
        target = os.path.abspath(args[0]) if args else os.path.abspath(__file__)
        live = modes(target)
        missing, stale = banner_drift(target)
        for flag, takes in live.items():
            mark = "MISSING" if flag in missing else "ok"
            print("  %-8s %-18s %s" % (mark, flag,
                                       "<operand>" if takes else ""))
        for flag in stale:
            print("  %-8s %-18s advertised, not dispatched" % ("STALE", flag))
        print("%d mode(s) dispatched; %d undocumented, %d stale"
              % (len(live), len(missing), len(stale)))
        if missing or stale:
            print("   ⚑ THE BANNER IS A DERIVED VIEW OF THE DISPATCH — a hand-kept "
                  "roster drifts,\n     and a reader who trusts it spends commands "
                  "hunting a mode that is not there.")
        sys.exit(1 if (missing or stale) else 0)

    if "--declare-modes" in sys.argv:
        # ⚑ ⟡mode-standardize — the `Mode(...)` skeleton for every dispatched flag the
        # roster does not carry. Arity is DERIVED (`modes()`); `scans`/`paths`/`opts`/`why`
        # are deliberately left for a reader, because a mechanically-emitted contract is
        # one the gate can never fail. See `declare_modes.__doc__`.
        target = args[0] if args else os.path.abspath(__file__)
        # ⚑ WHETHER THE TARGET IS THIS FILE decides which authority the count is against —
        # `declare_modes` resolves the roster to `MODES` for self and to `{}` for anything
        # else, so a foreign file's "undeclared" count is a tautology and the basis line
        # below must say so rather than let it read as debt.
        _self = os.path.abspath(target) == os.path.abspath(__file__)
        rows = declare_modes(target)
        owed = [r for r in rows if not r[2] and not r[3]]
        dual = [r for r in rows if not r[2] and r[3]]
        for flag, operand, _d, _m in owed:
            # ⚑ `None` IS UNKNOWN AND `False` IS NULLARY, AND THEY MUST NOT RENDER ALIKE.
            # A foreign file's arity is not derived (see `declare_modes`), so it prints
            # `operand=?` — a reader must open the branch. Rendering it as absent would be
            # a confident wrong answer in the one field that binds argv.
            arity = ('operand=?, ' if operand is None else
                     'operand="name", ' if operand else "")
            print('    %-22s Mode(%spaths=?, scans=?, writes=?, why=""),'
                  % ('"%s":' % flag, arity))
        if dual:
            print("\n   ── DUAL-ROLE, NOT A MISSING ENTRY (%d)" % len(dual))
            for flag, _o, _d, _m in dual:
                print("      %-20s declared in OPT_OPERANDS as a MODIFIER, and also "
                      "opens a dispatch branch" % flag)
            print("      ⚑ A MODIFIER'S OPERAND IS READ BY `argopt` AND STRIPPED FROM "
                  "`args`;\n        a MODE'S IS READ POSITIONALLY FROM `args[0]`. "
                  "Conflating them 'broke every\n        query mode for ten minutes' "
                  "(`_dispatch`). Emitting a Mode(...) here would\n        re-commit "
                  "that conflation in the table built to end it — decide the ROLE.")
        print("\n%d of %d dispatched mode(s) undeclared in MODES; %d dual-role"
              % (len(owed), len(rows), len(dual)))
        # ⚑⚑ THE BASIS LINE, BECAUSE THE OBVIOUS CROSS-CHECK IS A FALSE DISAGREEMENT.
        # This mode and `toolmodes --divergence` both answer "which modes are undeclared",
        # against DIFFERENT AUTHORITIES — the `MODES` table here, the USAGE TEXT there —
        # so their rosters differ legitimately and a reader comparing them concludes one
        # is broken. MEASURED (agda-F12, 2026-08-24): for `pipeflow.py` this reports 11
        # and `--divergence` reports 5, overlapping in exactly one element, and that was
        # filed as "mis-reports another file's roster" when BOTH READINGS WERE CORRECT.
        # A census that does not name its own authority invites that inference, and the
        # cheapest place to stop it is the output itself.
        print("   basis: DISPATCH vs the `MODES` table%s."
              % ("" if _self else " (this file declares none — a foreign file has no "
                                 "roster, so every\n     dispatched mode is reported "
                                 "undeclared by construction)"))
        print("     NOT the same statistic as `toolmodes --divergence`, which compares "
              "DISPATCH\n     vs the USAGE TEXT. The two rosters differ legitimately; a "
              "disagreement between\n     them is not evidence that either is wrong.")
        if owed:
            print("   ⚑ SKELETONS, NOT ENTRIES. `paths`/`scans`/`why` are left blank on "
                  "purpose:\n     a `scans=False` emitted by a program satisfies "
                  "`--check-contracts` by\n     construction, which would clear the gate "
                  "by removing its power to bite.")
        sys.exit(0)

    if "--touches" in sys.argv:
        items_py = os.path.join(ROOT, "catalog", "library", "items.py")
        names = [n for n, _l, _d in _cached_defs(items_py)]
        # ⚑ THE ROSTER IS THE ITEMS DICT, NOT THE FUNCTION SET.  Measured
        # elsewhere today: `def D0_KERNEL(` existed while `--items D0-kernel`
        # said `unknown item key(s)`.  Reading the dict keeps this aligned with
        # what the ordering can actually resolve.
        src = open(items_py, encoding="utf-8").read()
        keyed = dict(re.findall(r'(?m)^\s*"([\w.-]+)"\s*:\s*(\w+),', src))
        if args:
            want = {k: f for k, f in keyed.items() if k in args or f in args}
            if not want:
                print("usage: pycodemod.py --touches [<item-key> ...]")
                print("  with no key: every pair of items whose witnesses read a")
                print("  common file — the CODE-warranted edges, which prose")
                print("  evidence (bibstruct --mentions) cannot see.")
                sys.exit(2)
            for key, fn in sorted(want.items()):
                t = touches(fn, items_py)
                print(f"── {key}  ({fn})")
                for f in t["files"]:
                    print(f"     reads    {f}")
                for u in t["unresolved"]:
                    print(f"     UNRESOLVED {u}   (a non-literal path part)")
                print(f"     symbols  {', '.join(t['symbols'][:12])}"
                      + (" …" if len(t["symbols"]) > 12 else ""))
            sys.exit(0)
        # ⚑ THE SHARED FILE IS ONE RELATION OVER ITS READERS, NOT k*(k-1)/2 PAIRS.
        # This block used to emit every pair of co-readers and hand them to a
        # 2-colouring.  That shattering turned `pycodemod.py`'s SIX readers into a
        # 6-clique, and a clique on >=3 nodes is never bipartite -- so the tool
        # reported two "conflicts" that were artifacts of the encoding and
        # oriented nothing.  A hyperedge keeps the k-ary question intact.
        by_item = {k: touches(f, items_py) for k, f in keyed.items()}
        shared = {}
        for k, t in by_item.items():
            for f in t["files"]:
                shared.setdefault(f, []).append(k)
        hyper = [(f, sorted(ms)) for f, ms in sorted(shared.items())
                 if len(ms) >= 2]
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import dagcone as _dc
        sol = _dc.orient_hyper(hyper)
        if sol.get("unmeasured"):
            for f, ms in hyper:
                print("  %-28s %s" % (f, ", ".join(ms)))
            print("%d co-read hyperedge(s); ORIENTATION UNMEASURED (%s)"
                  % (len(hyper), sol["unmeasured"]))
            sys.exit(0)
        for f, ms in sol["oriented"]:
            print("  ORIENTED  %-28s %s" % (f, " → ".join(ms)))
        for f, ms in sol["free"]:
            print("  free k=%-2d %-28s %s" % (len(ms), f, ", ".join(ms)))
        for cyc in sol["conflict"]:
            print("  ⚠ CONFLICT %s   (a DIRECTED cycle in the evidence)"
                  % " → ".join(cyc))
        pairs_implied = sum(len(ms) * (len(ms) - 1) // 2 for _f, ms in hyper)
        print("%d co-read hyperedge(s) over %d item(s): %d oriented, %d free, "
              "%d in conflict" % (len(hyper), len(by_item),
                                  len(sol["oriented"]), len(sol["free"]),
                                  len(sol["conflict"])))
        print("   ⚑ %d hyperedges, NOT %d pairs — the pairwise projection is "
              "what\n     manufactured the odd cycles (a k-clique is never "
              "bipartite)." % (len(hyper), pairs_implied))
        print("   ⚑ FREE is a measurement, not a gap: a co-read is a COUPLING, "
              "and no\n     precedence evidence exists, so the ordering is "
              "genuinely absent (a ∧ a = 0).")
        sys.exit(0)

    if "--artifacts" in sys.argv:
        rows = build_artifact_readers(py_files(*args) if args else None)
        for rel, arts, bearing in rows:
            print(f"  {bearing:<7} {rel:<44} {', '.join(arts)}")
        by = {}
        for _r, _a, b in rows:
            by[b] = by.get(b, 0) + 1
        print("  ".join(f"{k}={by[k]}" for k in sorted(by)))
        blockers = by.get("FAILURE", 0) + by.get("BOTH", 0)
        print(f"{blockers} of {len(rows)} build-artifact reader(s) read a "
              f"FAILURE-BEARING artifact")
        # ⚑ THE VERDICT IS THE SPLIT, NOT A COUNT.  If the two populations do not
        # separate, that is the finding — the predicate is measuring one thing
        # where it claimed two, and the output must show it rather than a tally
        # that reads the same either way.
        if not by.get("SUCCESS") and blockers:
            print("   ⚑ NO SUCCESS-ONLY READERS — the distinction did not divide "
                  "this population.\n     Either every reader touches failures, or "
                  "the vocabulary missed the success side.")
        elif blockers:
            print("   ⚑ a tool reading a FAILURE-bearing artifact emits "
                  "commit-blockers BY CONSTRUCTION —\n     the row's provenance "
                  "carries it; no gate-reachability query is needed.")
        sys.exit(0)

    if "--shape" in sys.argv:
        i = sys.argv.index("--shape")
        if i + 1 >= len(sys.argv):
            print("usage: pycodemod.py --shape <regex> [paths]")
            print("  WHERE a source shape occurs — comments and docstrings")
            print("  excluded (--shape-all includes them).")
            sys.exit(2)
        pat = sys.argv[i + 1]
        _scope = [a for a in args if a != pat]
        files = py_files(*_scope) if _scope else py_files()
        every = "--shape-all" in sys.argv
        rows = shape_sites(pat, files, in_code_only=not every)
        for p, ln, text in rows:
            print(f"  {os.path.relpath(p, ROOT)}:{ln}  {text[:110]}")
        print(f"{pat!r}: {len(rows)} site(s) in "
              f"{len({p for p, _l, _t in rows})} of {len(files)} file(s)"
              f"{'' if every else '  [code only]'}")
        if not files:
            print("   ⚑ NO FILES SEARCHED — a fact about the QUERY, not the code.")
        sys.exit(0)

    if "--swallows" in sys.argv:
        rows = swallows(py_files(*args) if args else None)
        # ⚑ TRIAGE ORDER, NOT FILE ORDER.  A flat 244-row list is a list nobody works;
        # the whole point of the discriminator is that the first rows are the ones to
        # open.  Verdict-feeding first, then broadest handler.
        _rank = {"bare-except": 0, "broad": 1, "narrow": 2}
        rows = sorted(rows, key=lambda r: (not r[4], _rank[r[2]], r[0], r[1]))
        for p, line, kind, h, feeds in rows:
            mark = "VERDICT" if feeds else "output "
            print(f"{mark} {kind:<12} {h:<9} {os.path.relpath(p, ROOT)}:{line}")
        byk = {}
        for _p, _l, kind, _h, feeds in rows:
            byk[kind] = byk.get(kind, 0) + 1
        nfeed = sum(1 for r in rows if r[4])
        print(f"{len(rows)} silent exception discard(s)")
        for k in ("bare-except", "broad", "narrow"):
            if byk.get(k):
                print(f"   {k:<12} {byk[k]}")
        print(f"   {'VERDICT-feeding':<15} {nfeed}   "
              f"(output-only: {len(rows) - nfeed})")
        # ⚑ A POPULATION, NOT A VERDICT.  A swallow is usually CORRECT — one unparseable
        # file must not abort a corpus query.  What is never correct is a swallow that
        # leaves no trace: the population silently shrinks and no number says so. Each
        # row is a site that OWES an accounting; whether it has one is the reader's call.
        print("   ⚑ NOT A DEFECT LIST — a swallow is usually right; a swallow with no\n"
              "     accounting is not. Measured 2026-08-18: one `except Exception:\n"
              "     continue` turned a broken visitor into `0 def, 0 call, 0 ref` across\n"
              "     the whole corpus, and `--dead` read GREEN on a file with 18 defs.")
        # ⚑ THE DISCRIMINATOR'S OWN LIMITS, PRINTED WITH IT.  `VERDICT` means the try
        # body grows an accumulator or assigns a name the function returns — the shape
        # measured at `reuse_check.py:68`, where a reference file that fails to intern
        # silently shrinks the corpus whose SIZE becomes the "no prior art" answer (and
        # `:71`, eleven lines later, does the same call and EXITS with the reason).
        # `output` means the body only printed. Unresolvable bodies report VERDICT:
        # over-report, never invert — the same asymmetry `--guarded` takes on `else`.
        print("   ⚑ VERDICT = the swallowed work fed a COUNT or a RETURNED value, so a\n"
              "     silent drop becomes a fact-claim (reuse_check.py:68 truncates the\n"
              "     corpus its 'no prior art' verdict is computed from). output = only a\n"
              "     diagnostic is lost. UNRESOLVABLE BODIES REPORT VERDICT — this is a\n"
              "     TRIAGE ORDER, not a verdict; open the site before acting.")
        # ⚑⚑ AND THE DISCRIMINATOR IS WEAK — SAID HERE BECAUSE A RATIO NOBODY STATES IS A
        # RATIO NOBODY CHECKS.  Over `scripts/` it calls 46 of 50 VERDICT, which is barely
        # an ordering.  The known over-fire is a RECEIVER MUTATED BY A WRITE:
        # `buildtime.py:43` (`f.write(row)` inside `except OSError: pass`) is correctly
        # benign — the handle is read nowhere — and still reports VERDICT, because the
        # receiver rule cannot tell "grows a corpus someone counts" from "writes a file
        # and forgets it".  Three cuts have been built; each fixed one control case and
        # broke another (assign-only missed the receiver; receiver-aware over-fires on
        # writes).  Reported as a known bound rather than tuned to flatter the ratio: a
        # fourth guess with no new control case is how a discriminator becomes decoration.
        if nfeed and len(rows) and nfeed / len(rows) > 0.8:
            print(f"   ⚑⚑ {nfeed}/{len(rows)} are VERDICT — at this ratio the split is a\n"
                  f"      WEAK ordering, not a filter. Known over-fire: a MODULE-LEVEL\n"
                  f"      CONSTANT read inside the try and again elsewhere in the file\n"
                  f"      (buildtime.py:43 touches LEDGER/AGDA) counts as an escape,\n"
                  f"      because the downstream test spans the whole module scope.\n"
                  f"      Treat `broad` + VERDICT as the head of the list, not all of it.")
        sys.exit(0)

    if "--exits" in sys.argv:
        # ⟡exit-and-swallow.  ONE dispatch, THREE lenses, because they answer each
        # other's question: `SystemExit` derives from `BaseException`, so an
        # `except Exception` FAILS OPEN on an exit and a bare `except:` FAILS CLOSED
        # on it.  Splitting these into separate modes would let a reader run either
        # one and get a confident half-answer.
        _files = py_files(*args) if args else None
        _ex = _pycodemod_exit.exits(_files)
        _ca = _pycodemod_exit.catchers(_files)
        _il = _pycodemod_exit.interlock(_files)
        _nfiles = len(_files if _files is not None else py_files())

        # ⚑⚑⚑ `--sites` PRINTS EVERY ROW, AND THE DEFAULT VIEW PRINTS TWO BUCKETS.  The
        # default is a TRIAGE ORDER — `LIBRARY`/`hard` are the actionable ones — but a
        # triage view is not an auditable one: `dispatch` and `main-only` are precisely
        # where a wrong join lands, and as bare totals nothing about them can be checked.
        # Both classifications rest on a predicate a reader may dispute (the `__main__`
        # guard test, the importer-NAME join), and a disputed verdict is settled by
        # opening the row, never by re-reading the count.
        _sites = "--sites" in sys.argv
        print("── EXIT SITES  (a script assuming it owns the pid)"
              + ("  [--sites: every row]" if _sites else ""))
        _order = {"LIBRARY": 0, "hard": 1, "dispatch": 2, "main-only": 3}
        for p, ln, sp, _d, verdict, why in sorted(
                _ex, key=lambda r: (_order[r[4]], r[0], r[1])):
            if _sites or verdict in ("LIBRARY", "hard"):
                print(f"  {verdict:<9} {sp:<16} "
                      f"{os.path.relpath(p, ROOT)}:{ln}  {why}")
        _byv = {}
        for r in _ex:
            _byv[r[4]] = _byv.get(r[4], 0) + 1
        _bysp = {}
        for r in _ex:
            _bysp[r[2]] = _bysp.get(r[2], 0) + 1
        print(f"{len(_ex)} exit site(s) in "
              f"{len({r[0] for r in _ex})} of {_nfiles} file(s)")
        for k in ("LIBRARY", "hard", "dispatch", "main-only"):
            if _byv.get(k):
                print(f"   {k:<10} {_byv[k]}")
        for k in sorted(_bysp):
            print(f"   spelled {k:<16} {_bysp[k]}")
        # ⚑⚑ THE JOIN IS DEF-LEVEL, AND SAYING "a module another file imports" WOULD BE
        # THE MODULE-LEVEL CLAIM IT REPLACED.  That coarser join reported 174 LIBRARY
        # rows of which 130 were `pycodemod._dispatch` — 7 files import `pycodemod`,
        # none of them name the dispatcher.  The narrowed predicate reported 18 when it
        # was built and 22 on 2026-08-26; the figure that is load-bearing is the 130 it
        # REMOVES, not the total, which moves with the tree (`fresh-comments-are-
        # hypotheses-too`: the count is re-derived by running the mode, never quoted).
        print("   ⚑ LIBRARY is the defect the census exists for: an exit in a def another\n"
              "     file NAMES (or reaches through this module's own calls) terminates\n"
              "     the CALLER's process. main-only/dispatch own their pid — CORRECT.\n"
              "   ⚑ `dispatch` is NOT 'unimported' — it is 'no importer reaches this def'.\n"
              "     A module-level join reported 174 here, 130 of them one CLI dispatcher.")
        if not _sites:
            # ⚑⚑ THE AUDIT PATH, NAMED WHERE THE UNAUDITABLE NUMBERS ARE PRINTED.  The two
            # buckets above appear as TOTALS ONLY, and they are exactly the two a wrong
            # join lands in — a def mis-read as `main-only` or `dispatch` disappears into
            # a number.  A count nobody can open is a count nobody can falsify, so the
            # view that cannot be audited must NAME the one that can.
            print(f"   ⚑ `dispatch` ({_byv.get('dispatch', 0)}) and `main-only` "
                  f"({_byv.get('main-only', 0)}) are TOTALS HERE — the two buckets a\n"
                  "     wrong join lands in, and neither is auditable from this view.\n"
                  "     `--exits --sites` lists EVERY row with its verdict and reason:\n"
                  "     a disputed classification is settled by opening the row.")

        print()
        print("── HANDLERS THAT CATCH SystemExit  (the fails-CLOSED direction)")
        for p, ln, kind, _d, silent, reraises in _ca:
            _t = "silent" if silent else ("re-raises" if reraises else "handled")
            print(f"  {kind:<12} {_t:<10} {os.path.relpath(p, ROOT)}:{ln}")
        _byk = {}
        for r in _ca:
            _byk[r[2]] = _byk.get(r[2], 0) + 1
        print(f"{len(_ca)} handler(s) catching SystemExit in "
              f"{len({r[0] for r in _ca})} of {_nfiles} file(s)")
        for k in ("bare-except", "base", "named"):
            if _byk.get(k):
                print(f"   {k:<12} {_byk[k]}")
        # ⚑⚑ THE DISCRIMINATOR THAT REPLACES A CARVE-OUT LIST.  `named` means the source
        # SPELLS `except SystemExit` — a reader cannot write that by accident, so naming
        # the class IS the accounting, and it is separated structurally rather than by an
        # exemption file.  A frozen ALLOW-list is the shape this repo refuses; a property
        # of the source text is not.
        print("   ⚑ `named` (`except SystemExit`) is DELIBERATE BY CONSTRUCTION — the\n"
              "     spelling is the accounting. Listed for completeness, never a defect.\n"
              "     `bare-except`/`base` catch it WITHOUT the author deciding to.")

        print()
        print("── INTERLOCK  (`except Exception` guarding a call that can EXIT)")
        for p, ln, d, callee in _il:
            print(f"  {os.path.relpath(p, ROOT)}:{ln}  "
                  f"in {d or '<module>'}()  reaches {callee}()")
        print(f"{len(_il)} site(s) where a handler READS as containment and is not")
        print("   ⚑⚑ A FLOOR, NOT A BOUND. The call graph is same-module-transitive plus\n"
              "      ONE import hop — `reaches`' own refusal to fabricate cross-module\n"
              "      edges (26 of 29 reported round trips were that fabrication). A\n"
              "      longer chain reads as NOT REACHED: under-report, never invent.")

        print()
        print("⚑ SPELLINGS THIS CENSUS KNOWS IT MISSES  (declared, never computed —")
        print("  a census cannot derive its own blind spots):")
        for m in _pycodemod_exit.KNOWN_MISSES:
            print(f"   · {m}")
        # ⚑ THE `scans=True` CONTRACT, HONOURED BY THE CENSUS' OWN READER.  `--exits`
        # does not go through `scan()`, so `_report_skipped()` would read a DIFFERENT
        # query's population — the stale-context defect its own `where=` parameter
        # exists to prevent. This reports the files `_pycodemod_exit._parse` skipped.
        _pycodemod_exit.report_skips(_nfiles)
        sys.exit(0)

    if "--unbound-snapshot" in sys.argv:
        print_disagreement(py_files(*args) if args else None)
        _report_skipped()
        sys.exit(0)

    if "--placement" in sys.argv:
        print_placement(py_files(*args) if args else None)
        _report_skipped()
        sys.exit(0)

    if "--guarded" in sys.argv:
        if not args:
            print("usage: pycodemod.py --guarded <name> [paths]")
            sys.exit(2)
        name, rest = args[0], args[1:]
        under, top = guarded(name, py_files(*rest) if rest else None)
        for p, line, cs in under:
            print(f"under {os.path.relpath(p, ROOT)}:{line}  if {' / if '.join(cs)}")
        for p, line in top:
            print(f"top   {os.path.relpath(p, ROOT)}:{line}")
        tot = len(under) + len(top)
        print(f"{name}: {len(under)} of {tot} call(s) sit under an `if`")
        _report_skipped()
        if under:
            # ⚑ THE GROUPING IS THE POINT, NOT THE LIST.  One site under `if apply:` is
            # an observation; the same condition across many is a CLASS, and the class
            # is what says whether a contract is positioned wrong everywhere or once.
            byc = {}
            for _p, _l, cs in under:
                byc.setdefault(" / ".join(cs), 0)
                byc[" / ".join(cs)] += 1
            print("   by condition:")
            for c, n in sorted(byc.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f"     {n:>3}  if {c}")
        # ⚑ SOURCE TEXT, NOT REACHABILITY — say so with the verdict, not only in the
        # docstring nobody reads at the terminal.  `if apply:` and `if args.apply:` are
        # different keys here, and an `else` body is reported under its `if`.
        print("   ⚑ CONDITIONS ARE SOURCE TEXT — 'written under this test', never "
              "'reachable only when true'.\n     An `else` body is reported under its "
              "`if` (over-report, never inverted). Open a site before acting.")
        sys.exit(0)

    if "--check-contracts" in sys.argv:
        rows = scan_contract()
        for flag, ok, why in rows:
            mark = "ok  " if ok else ("UNK " if ok is None else "FAIL")
            print(f"  {mark} {flag:<20} {why}")
            # ⚑ A ROSTER-DISAGREEMENT ROW HAS NO `Mode` TO QUOTE, AND ASSUMING IT DID
            # CRASHED THIS PRINTER ON ITS FIRST RUN (`KeyError: '--available'`).  The
            # rows I added report flags DISPATCHED-but-undeclared — i.e. precisely the
            # ones absent from `MODES` — so indexing `MODES[flag]` is guaranteed to fail
            # for exactly the finding.  A reporter that cannot render its own new verdict
            # is the shape this file keeps recording one layer down.
            if not ok and flag in MODES and MODES[flag].why:
                print(f"       why declared: {MODES[flag].why}")
        bad = [r for r in rows if not r[1]]
        _contract = [r for r in rows if r[0] in MODES and MODES[r[0]].scans]
        _roster = [r for r in rows if r not in _contract]
        print(f"{len(_contract) - len([r for r in _contract if not r[1]])} of "
              f"{len(_contract)} scans=True mode(s) honour the incomplete-scan contract")
        if _roster:
            # ⚑ REPORTED AS ITS OWN LINE, NOT FOLDED INTO THE CONTRACT COUNT.  They are
            # different debts: one is "a declared contract is unmet", the other is "the
            # roster and the dispatch disagree about what exists". Summing them would
            # make a paydown of either look like progress on both.
            print(f"{len(_roster)} roster/dispatch disagreement(s) — MODES is the "
                  f"declared authority and the dispatch is what runs")
        # ⚑⚑ ⟡mode-opt-key-collision — REPORTED, AND DELIBERATELY NOT SCORED. These are a
        # KNOWN-MISS in `_dispatch`'s opt validator, not a roster/dispatch disagreement:
        # folding them into `bad` would fail the gate on a residue that was measured,
        # judged benign, and declared. What the section buys is that the population is
        # DERIVED on every run — the comment in `_dispatch` names `--sites` and says "do
        # not assume it is the only one", which is a sentence a reader must re-verify by
        # hand. Now they do not.
        _coll = opt_key_collisions()
        if _coll:
            _harm = [c for c in _coll if c[2]]
            print("%d spelling(s) are BOTH a MODES key and another mode's opt "
                  "(⟡mode-opt-key-collision — in `_known` for EVERY invocation):"
                  % len(_coll))
            for _f, _own, _h, _why in _coll:
                print("  %-4s %-16s opt-of %s" % ("HARM" if _h else "ok", _f,
                                                  " ".join(_own)))
                print("       %s" % _why)
            print("  %d harmful (different meaning per role) — 0 is the paydown target; "
                  "the rest are BENIGN and stay." % len(_harm))
        if not rows:
            # ⚑ AN EMPTY ROSTER MUST NOT READ AS A PASS.  Zero declared contracts and
            # zero violations render identically in a bare count — the confident-zero
            # shape this whole family exists to close.
            print("   ⚑ NO mode declares scans=True — this gate measured NOTHING.")
            sys.exit(2)
        sys.exit(1 if bad else 0)

    if "--ambient" in flagged_argv():
        # ⟡ambient-root — see `_pycodemod_ambient`'s docstring for why this is a
        # PROPERTY census and not a name census.
        # ⚑⚑ THE MODIFIER IS TESTED THROUGH A HELPER, NOT AS A BARE `if "--x" in
        # flagged_argv():`, AND THE GATE IS WHY.  `scan_contract`'s branch-locator
        # matches that exact line shape to find where a MODE's branch begins, so
        # spelling a MODIFIER that way registers `--misses` as a top-level mode and
        # `--check-contracts` reported "DISPATCHED, absent from MODES — undeclared
        # arity" one minute after this branch was written.  The flag IS declared —
        # in `--ambient`'s `opts`, which is where a modifier belongs — so the roster
        # was right and the SPELLING was the defect.  `_opt()` keeps the two
        # distinguishable to the locator by construction, rather than by my
        # remembering to indent it out of the pattern's reach.
        if _opt("--misses"):
            print("── what `--ambient` structurally CANNOT see")
            for kind, why in _pycodemod_ambient.KNOWN_MISSES:
                print(f"  {kind:<18} {why}")
            print(f"{len(_pycodemod_ambient.KNOWN_MISSES)} declared blind spot(s) "
                  f"— DECLARED, not computed: a census cannot derive its own.")
            sys.exit(0)
        rows = _pycodemod_ambient.ambient(py_files(*args) if args else None)
        want = argopt(sys.argv, "--verdict")
        shown = [r for r in rows if want is None or r[3] == want.upper()]
        if _opt("--sites"):
            for p, ln, kind, verdict, txt, ctx in shown:
                print(f"  {verdict:<8} {os.path.relpath(p, ROOT)}:{ln}  "
                      f"{kind:<18} {ctx}  {txt!r}")
        else:
            per = {}
            for p, _ln, _k, verdict, _t, _c in shown:
                per.setdefault(os.path.relpath(p, ROOT), {}).setdefault(verdict, 0)
                per[os.path.relpath(p, ROOT)][verdict] += 1
            for f in sorted(per):
                bits = "  ".join(f"{v}={n}" for v, n in sorted(per[f].items()))
                print(f"  {f:<46} {bits}")
        tally = {}
        for _p, _ln, _k, verdict, _t, _c in rows:
            tally[verdict] = tally.get(verdict, 0) + 1
        files = len({r[0] for r in rows})
        print(f"{len(rows)} ambient site(s) in {files} of "
              f"{_pycodemod_ambient.ambient.population} file(s)  "
              + "  ".join(f"{v}={n}" for v, n in sorted(tally.items())))
        _report_skipped(_pycodemod_ambient.ambient)
        # ⚑⚑ THE COUNT IS A FLOOR AND SAYING SO IS PART OF THE VERDICT.  This mode
        # was built because `--calls getcwd` (20) and `--calls exists` (153) were
        # each read as bounds on one dependence; a union that hid ITS blind spots
        # would repeat that one level up.
        print("   ⚑ A FLOOR, NOT A BOUND — run `--ambient --misses` for the "
              "spellings this reader\n     cannot see (indirection, runtime argv, "
              "and the whole non-python surface).")
        print("   ⚑ SCOPED is the FEATURE (the directory IS the question); REPO is "
              "the DEFECT\n     class (a repo-relative path resolved ambiently); "
              "UNKNOWN is the classifier's\n     honest boundary and is folded into "
              "NEITHER.")
        sys.exit(0)

    if "--dead" in sys.argv:
        rows = dead(py_files(*args) if args else None)
        for p, n, l in sorted(rows):
            print(f"{os.path.relpath(p, ROOT)}:{l}  {n}")
        print(f"{len(rows)} def(s) with no caller and no CLI dispatch")
        # ⚑⚑ THE MOST IMPORTANT CONSUMER OF THIS REPORT, because `--dead` reads CLEAN
        # when the scan is broken: zero rows means zero unreachable rows.  Measured
        # 2026-08-18 — `--dead scratch/_pycodemod_core.py` printed "0 def(s) with no
        # caller" on a file with 18 defs while a visitor defect emptied every scan.
        # Every other caveat below describes what this mode cannot RESOLVE; this one
        # describes what it did not READ, and only the second can be silently total.
        _report_skipped()
        if args:
            print("   ⚑ SCOPED RUN — 'dead' means 'no caller IN THE SCANNED FILES'. "
                  "A cross-file\n     caller is invisible here; run without paths for "
                  "a DEAD-CAPABILITY verdict.")
        # ⚑⚑ WHAT THIS CENSUS STRUCTURALLY CANNOT SEE, PRINTED WITH EVERY VERDICT.
        # The mode already caveated the SCOPE of the population; it said nothing
        # about the KINDS of reachability it cannot resolve, and that is where the
        # false positives lived.  Three shapes have no static call site by
        # construction — a name built at runtime (`f"qb.{k}"` in
        # `query_registry.py:90` appears in no source literal anywhere), an
        # invocation across a process boundary (`run_selftests.py` runs each suite
        # as `python <path> --selftest`), and a caller in a library outside this
        # corpus.  Prefix contracts are handled above; the other two cannot be.
        #
        # ⚑ AND THIS IS THE `--values` STANCE APPLIED TO REACHABILITY: a non-literal
        # reports UNKNOWN, never a guessed value.  `--dead` is the census this repo
        # DELETES on, so a row it cannot resolve must read as unresolved rather
        # than as a verdict — absence of a static path is a fact about the METHOD.
        print("   ⚑ NOT A DELETION LIST — these are defs with no caller this mode "
              "can RESOLVE.\n     Blind by construction to: names built at runtime "
              "(`f\"qb.{k}\"`), invocation\n     across a process boundary "
              "(`python <path> --selftest`), and callers in\n     libraries outside "
              "this corpus. Confirm a row before acting on it.")
        sys.exit(0)

    print(__doc__)
    sys.exit(2)


if __name__ == "__main__":
    # ⚑ THE SLICE, NOT `sys.argv` — `--literal -- --selftest` RAN THE SUITE instead of
    # searching for the string, because this guard read past the end-of-flags marker.
    if "--selftest" in flagged_argv():
        sys.exit(0 if _selftest() else 1)
    # ⚑ THE ARCHIVE ENCLOSES THE QUERY; it is not one of them.  Every mode below
    # answers about whatever `ROOT` is, so opening the archive around the SAME
    # dispatch gives `--dead`, `--calls`, `--imports`, `--rivals` over a reference
    # implementation with no per-mode work -- and the temp tree is removed by the
    # `with`, on the error path too.
    # ⚑ `--archive` AND `--in` ARE THE SAME ENVELOPE OVER DIFFERENT ROOTS, and
    # keeping them as one dispatch is the point: an archive, a directory and an
    # INSTALLED PACKAGE are three ways of naming a corpus, not three questions.
    # `--package` was left as a leaf when the envelope landed, so it could locate
    # a def and not read one -- the same half-step that made `--archive` grow a
    # `--show` bolt-on an hour earlier.
    # ⚑ THE OPERAND MUST BE THE SCOPE FLAG'S OWN, NOT THE NEXT MODE'S.  This took
    # `_rest[0]` -- the first non-flag token ANYWHERE after the flag -- so
    # `--key --archive f.py` bound `--key`'s operand as a tarball and crashed in
    # `tarfile.open`.  `_dispatch` guards the mirror image of this (subtracting the
    # scope target from the query args) but runs AFTER `corpus()` has opened it.
    # `modes()` knows which flags consume an operand, so the scan stops at the next
    # ARGUMENT-TAKING mode instead of reading through it.
    _arity = modes()

    def _owned(argv):
        """{index of each operand: the flag that owns it}.

        ⚑ OWNERSHIP IS A PROPERTY OF THE WHOLE ARGV, NOT A FORWARD SCAN.  A scan
        rightward from the scope flag cannot answer `--key --archive f.py`, where
        the owner sits to the LEFT: `--key` consumes the token that follows
        `--archive`.

        ⚑ AND AN OUTSTANDING CLAIM IS NOT DISPLACED BY A LATER FLAG -- the defect
        that made my second attempt fail identically to my first.  Walking that
        same argv, `--key` set `pending` and `--archive` OVERWROTE it before any
        operand appeared, so `f.py` was assigned to the later flag: exactly
        backwards, and it crashed in `tarfile.open` just as before.  A flag whose
        operand has not arrived still owns the next one; `pending` is a QUEUE, and
        treating it as a single slot silently re-assigns operands whenever two
        argument-taking flags are adjacent."""
        owner, pending = {}, []
        for _j, _a in enumerate(argv):
            if _a.startswith("-"):
                if _arity.get(_a) or _a in SCOPE_FLAGS:
                    pending.append(_a)
                continue
            if pending:
                owner[_j] = pending.pop(0)
        return owner

    _own = _owned(sys.argv[1:])
    _scope = None
    for _flag in SCOPE_FLAGS:
        if _flag in sys.argv:
            _rest = [a for _j, a in enumerate(sys.argv[1:])
                     if _own.get(_j) == _flag]
            if not _rest:
                print("usage: pycodemod.py %s <path|module> <query...>" % _flag)
                print("  the target is a SCOPE: any query runs inside it, e.g.")
                print("    --archive ref.tar.gz --dead")
                print("    --in persistqueue --calls ack")
                print("    --in opentelemetry.exporter.otlp.proto.http --imports")
                sys.exit(2)
            _target = _rest[0]
            if _flag == "--in" and not os.path.exists(_target):
                # a MODULE name, not a path: resolve it the way `--package` does
                _root, _detail = package_root(_target)
                if _root is None:
                    print("  ABSENT    %s  %s" % (_target, _detail))
                    sys.exit(2)
                _target = _root
            _scope = _target
            break
    # ⚑ AN UNRESOLVABLE ROOT IS A USER-FACING REFUSAL, NOT A TRACEBACK. The population error is
    # the most likely thing a caller in ANOTHER checkout hits (a path that exists in neither
    # tree), and a stack dump answers "the tool broke" when the fact is "your path named
    # nothing". Same class as the gate message that named an unrunnable tool: the only text a
    # blocked reader sees has to carry the next move.
    try:
        if _scope is not None:
            with corpus(_scope):
                _dispatch()
        else:
            _dispatch()
    except PopulationError as _pe:
        print("pycodemod: %s" % _pe)
        print("  ⚑ a RELATIVE path resolves against your CWD first, then the tool's tree.")
        print("     Nothing matched either, so NO population was scanned — this is a fact")
        print("     about the QUERY, not about the code. Pass an absolute path to be sure.")
        sys.exit(2)
