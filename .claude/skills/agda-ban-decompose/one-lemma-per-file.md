# The one-lemma-per-file split — repeatable procedure

Formalized from the ⟡nat-fin-rebase execution (2026-07-31): `Bin`, `BinArith`,
`BinTrim`, `BinBridge`, `BinMul`, `CayleyDickson.Curve` → 67 leaves, tree green
at every step.

## What this is FOR (P1–P5 are means; this is the end)

**Minimise the information each file IMPORTS, and the information each file
HOLDS.** One lemma per file, so a consumer needing a lemma imports the file
where that lemma is the only thing in it. **An import must never pull in a file
holding more than the import requires.** Every refactor pressure therefore
points UPSTREAM, at whichever module holds too much.

**Filters, qualifiers and barrels are THE ANTIPATTERN.** A `using` list does not
reduce what is imported — it reduces what is VISIBLE while the whole module is
still imported and, if parameterised, still APPLIED and ELABORATED. This is why
the ban and the memory cap are one constraint seen twice: importing 40
definitions to use 1 is exactly the elaboration cost an `Error 251` is made of.

Judge any proposed shortcut against the criterion above, not against the ban's
key count. If a move leaves the same information imported, it did not pay down
anything (see F3).

## Policy

```
P1  A file declares exactly ONE top-level definition or lemma.

P2  A file with >1 declaration becomes a DIRECTORY; each declaration becomes a
    leaf file inside it. The monolith is DELETED — never retained as a
    re-export barrel. (A barrel is the conduit ⟡public-policy exists to remove;
    the paydown is bind-at-owner + delete, not a thinner tip.)

P3  CONTAGION. The obligation propagates to every file we TOUCH (modify) and
    every file we IMPORT. Deliberate: it makes the policy self-propagating
    from real work, without a big-bang tree-wide refactor.

P4  Imports are BARE (⟡ban-decompose: no using / renaming / hiding / as on
    Substrate imports).
    COROLLARY, and the reason P3 covers imports: the ONLY way to import less
    is to SPLIT THE UPSTREAM. The ban is the forcing function — it exists to
    make a fat import IMPOSSIBLE TO HIDE, not to make filters tidy. A bare
    import of a fat module is therefore NOT compliance; it is the same debt
    with the evidence removed. Compliance is the upstream split (see F3).

P5  Shared rationale lives in dir(F)/README.md — ONCE. A leaf header states
    what is true of THAT leaf, at whatever length that leaf earns.
    (Not for comment:code ratio — that was the ergonomic objection that eroded
    this policy. The reason is that one rationale repeated across N headers IS
    duplication, which is what the policy attacks.)
```

## Tooling (mechanized; updated 2026-07-31)

The four stages below are each mechanized; `split_pipeline.py` chains them so a
straightforward split is one command; `enforce_ban.py` drives THAT across the
whole tree in dependency-free priority order. Each component tool remains
callable on its own when a split hits one of the known gaps (see Rewire).

```
scratch/enforce_ban.py [--apply] [--max=N] [--status] [--stop-on-fail]
    THE DRIVER — Enforce() below, executable. Everything else here is
    PER-MODULE; this is the only thing that decides WHICH module is next.

    THE QUEUE IS THE BAN CENSUS, INVERTED.  A ratchet key is
    `<consumer>::<upstream module>::<directive>` = "this consumer imports a
    module holding more than it needs".  Group by the MODULE column, sort
    descending, and the split order falls out — the count is CONSUMERS FREED,
    and ONE split discharges all of them at once.  So the unit of work is the
    MODULE, never the key: ~12k `using` keys sit over ~1.2k modules and the top
    12 modules carry 46% of the debt.  "What order?" is a SORT, not a judgement
    call — do not re-derive it as one.

    RESUMABLE BY CONSTRUCTION.  State is appended to
    `scratch/enforce_ban.journal.tsv` after EVERY module, never held across a
    step, so a crash / timeout / compaction / ^C costs exactly the module in
    flight; re-running resumes with no argument and no recollection required.
    The journal is the authority — not the process, not a context window.

    PARK, DON'T STALL.  `split_pipeline.die()` raises SystemExit; the driver
    catches it per module, journals `fail`, and moves on, so one hard module
    cannot block the other 1163.  A parked module is skipped on re-run until
    its journal line is removed.  `--stop-on-fail` opts into halting instead.
    It never reverts, never commits, never pushes, and never edits a baseline.

    Costs one FULL BUILD per module (that is what green-at-every-step buys),
    so `--max=N` for a bounded bite.

scratch/split_pipeline.py <file.agda> [--apply]
    split → isolate-typecheck each leaf → prune → gen_build_makefiles →
    rewire_to_leaves → check_indented_imports (post-rewire sweep) →
    IMPORT-CYCLE GUARD (fix_stale_using.check_cycles, F13 — before the
    expensive build, since Agda only reports CyclicModuleDependency when the
    offending module is next typechecked) → remove orphan .agdai →
    gen_build_makefiles → full build (F15: cap kills ≠ Agda errors) → STALE
    `using` SWEEP (fix_stale_using.sites over agda/_build's per-module logs,
    F12 — last, because the logs only exist after a build; warning-only, so it
    never turns the build red and MUST be swept explicitly).
    Dry run by default; --apply executes. Run from the REPO ROOT. A failing
    stage STOPS and prints the tool's own output — nothing here reverts a
    partial split (stash, don't revert, per repo policy).

scratch/fix_stale_using.py agda/_build [--apply]
    POST-REWIRE, POST-BUILD sweep (its input is build LOGS, so it runs
    AFTER a build, not before one). Repairs `using (...)` lists that still
    name names the module no longer exports after a split — see F12.
    POINT IT AT THE PER-MODULE LOG DIRECTORY `agda/_build` (it walks
    `**/*.agdai.log`). NEVER at a `make -j` console log: that log interleaves
    concurrent jobs and corrupts the tool by construction (F12).
    Dry run by default; --apply executes. Run to a FIXPOINT: fix, rebuild,
    re-run on the FRESH logs, until the warning class is empty.
```

Component tools (also directly usable): `split_lemmas.py` (Split, below),
`prune_imports.py` (Prune, below — F8 applies), `rewire_to_leaves.py` and
`check_indented_imports.py` (Rewire, below — the gaps apply to the pipeline
too; it does not paper over them, it surfaces the same failures), and
`fix_stale_using.py` (post-build; F12, and `--check-cycles` below).

```
python3 scratch/fix_stale_using.py --check-cycles
    STANDING TREE-WIDE GUARD, independent of any log. Reports every
    `open import M` whose target M transitively imports the importing module.
    Run it after ANY import codemod — see F13.
```

## Driver — MECHANIZED as `scratch/enforce_ban.py` (spec below)

Two seedings of the same loop, and the tool implements the second:

* **arc-seeded** (the original) — QUEUE starts from the files an arc TOUCHED,
  and P3 contagion grows it. Use when you are already working somewhere and the
  policy propagates out of real work.
* **debt-seeded** (`enforce_ban.py`) — QUEUE starts from the BAN CENSUS inverted
  onto the module column, richest first. Use to pay the ratchet down directly.
  Same Split/Rewire/Verify body; only the seed and the ordering differ.

The ordering below (`sort by |importers(F)|`) is why: it is *consumers freed*,
so it is both the cheapest-feedback order AND the biggest-paydown order. The
tool reads that count from the census instead of recomputing importers.

```
PROCEDURE Enforce(seed):
    QUEUE ← seed                                  # files this arc touched
    DONE  ← ∅
    while QUEUE ≠ ∅:
        LEVEL ← drain(QUEUE)                      # BFS: whole level, then next
        sort LEVEL ascending by |importers(F)|    # cheapest rewire first ⇒
                                                  # fastest feedback, smallest blast
        for F in LEVEL:
            if F ∈ DONE: continue
            leaves ← Split(F)
            DONE  ← DONE ∪ {F}

            for G in importers(F):                # G must now bind leaves
                Rewire(G, F, leaves)
                QUEUE ← QUEUE ∪ {G}               # P3: G is TOUCHED

            for I in ⋃ imports(leaves):
                QUEUE ← QUEUE ∪ {I}               # P3: I is IMPORTED

            Verify()                              # green tree at EVERY step
```

## Split

```
PROCEDURE Split(F) → leaves:
    D ← DeclGroups(F)                             # see DeclGroups below
    if |D| ≤ 1: return {F}                        # already atomic

    assert ∀ d ∈ D : named(d)                     # NAME every `_ : T` first —
                                                  # a nameless decl cannot be a
                                                  # leaf, and cannot be cited
    mkdir dir(F)
    Write(dir(F)/README.md, shared_rationale(F))  # P5

    for d in topological_order(D):                # a leaf may import siblings
        L ← dir(F)/CamelCase(name(d))
        Write(L, {
            header  : one line on d + pointer to dir(F)/README.md
                      (long ONLY where d earns it — e.g. d's honest debts),
            pragma  : same OPTIONS as F,
            imports : minimal(d),                 # BARE (P4); siblings for d's deps
            body    : d })
        assert IsolateTypechecks(L)               # membudget, REAL exit code:
                                                  #   cmd > log 2>&1; echo $?
                                                  # never read a pipeline's status
    Prune(leaves)                                 # minimal(d) is a first cut, not the
                                                  # fixpoint — see below
    Delete(F)
    Delete(orphan_core(F))                        # F1 below — part of Split
    return leaves
```

```

```
PROCEDURE Prune(leaves):
    # A leaf inherits its parent's import block; `minimal(d)` written by hand is
    # a first cut. Run the mechanical prune and let the build arbitrate.
    run scratch/prune_imports.py <leaves…>       # FROM THE REPO ROOT — see F8
    assert make -j == 0 errors                   # an over-prune shows as NotInScope;
                                                 # restore that one import, re-prune
```

```
FUNCTION DeclGroups(F) → set of declaration groups:
    # A GROUP, not a declaration: mutually recursive definitions, and a
    # signature with its clauses, are ONE indivisible unit ⇒ one leaf.
    # A `where`-local stays with its host.
    # A `private` helper used by ≥2 groups becomes its own leaf and loses
    # `private` (it now has consumers by name).
    # If the dependency graph of F's decls has a cycle, that cycle is one leaf.
```

## Rewire

Mechanized by `scratch/rewire_to_leaves.py <Parent.Module> [...]`, run from the
REPO ROOT. It reads each leaf's own `-- Defines:` header to build the
name→leaf map (never hand-written, so it cannot drift from the split), then
rewrites every importer's `open import Parent` (bare, or `using (...)`) onto
the owning leaves — errs WIDE on the bare form (opens all leaves; Prune cuts
it down). Column-0-anchored; tolerant of arbitrary whitespace before
`using`/EOL (a hand-aligned import block with padded spaces used to silently
miss the tool entirely — fixed at source, not worked around per caller).

```
PROCEDURE Rewire(G, F, leaves):
    used   ← names of F that G actually references
    chosen ← { L ∈ leaves : provides(L) ∩ used ≠ ∅ }

    replace in G:   `open import F`   or   `import F as A`
    with:           { `open import L` : L ∈ chosen }        # BARE (P4)
    strip:          `A.` qualifiers                          # drops a banned
                                                             # `as` ⇒ ban-ratchet
                                                             # PAYDOWN
    assert used ⊆ ⋃ provides(chosen)                         # nothing lost silently
```

**Known gaps (1–2 open; 3–5 FIXED AT SOURCE, recorded so the defect class is
not reintroduced) — none is silent once you know to check for it (see Verify):**

1. **No support for the combined `using (...) renaming (...)` form.** The
   tool's regexes match a bare `using (...)` clause OR a bare import, not
   both directives on one statement. A combined-form importer is left
   untouched; `check_indented_imports.py` (below) still flags it as a
   surviving reference, but the fix is manual: map each `using`-name to its
   owning leaf, split into one `open import <leaf>` per owner, and re-attach
   the `renaming (...)` clause to whichever import supplies the renamed name.
2. **Structurally excludes importers nested inside the parent's own new leaf
   directory.** The tool computes `outside = [p for p in files if not
   p.startswith(d + os.sep)]` — correct for the common case (a sibling
   directory can't already import a directory that didn't exist before the
   split), but wrong when a split PRODUCES leaves under a directory that a
   DIFFERENT existing subdirectory already nests inside of (e.g. splitting
   `Foundation/Bool.agda` into `Foundation/Bool/*.agda` while
   `Foundation/Bool/Properties/*.agda` already exists as a sibling nested
   tree). Those importers are silently skipped by the directory filter, not
   flagged by the tool at all — `check_indented_imports.py` catches them
   because it has no directory-exclusion logic, so always run it after any
   rewire whose new leaf directory could contain a pre-existing subdirectory.
3. **MULTI-LINE `using` (FIXED AT SOURCE).** Both regexes were single-line, so

   ```
   open import Parent
     using (a; b; c)
   ```

   with `using` on a CONTINUATION line missed the `using`-branch and fell
   through to the BARE-form branch: it replaced only the module line with the
   fan-out of leaf imports and ORPHANED the `using (...)` list onto whichever
   leaf import landed last — a stale `using` naming names that leaf does not
   export, i.e. it silently manufactures the exact F12 defect the other tool
   exists to repair. Fixed: the `using` regex allows a newline plus indent
   between the module name and `using`, and the bare-form regex carries a
   negative lookahead so it will not fire when an indented continuation follows.
4. **NEWLINE-SWALLOWING TAIL (FIXED AT SOURCE).** The trailing-comment capture
   group was `(\s*--.*)?$`. `\s` matches newlines, so it swallowed the blank
   line AND the following `-----` banner comment, splicing them onto the
   rewritten import line. Fixed by restricting to same-line whitespace:
   `([ \t]*--.*)?$`.
5. **RECORD FIELDS UNMAPPED (FIXED AT SOURCE).** `leaf_map` reads each leaf's
   `-- Defines:` header, falling back to the first top-level signature. Record
   FIELDS (e.g. `rem`, `wedge-eq` on a `GradedWedge` record) are therefore
   absent from the name→leaf map, so the rewire REFUSED with `UNMAPPED` on any
   consumer using a field name in its `using` list. A bare import of the
   record's leaf brings its fields into scope, so fields now map to that leaf:
   `leaf_map` also scans the indented `field` block and maps each field name to
   the leaf via `setdefault`, so a real top-level definition always wins.
7. **THE REPAIR MUST NOT RETAIN `public` — A CORRECT CONDUIT IS STILL A CONDUIT
   (`fix_stale_using.py`, FIXED AT SOURCE).** The tool preserved the statement's
   `public` flag, on the reasoning that dropping it would shrink the module's
   exported surface. That reasoning keeps the very thing P2/F23 delete: a
   `public` on an IMPORT makes a module export names it does not define, and a
   split MULTIPLIES it (the parent's prelude is copied into every leaf). ⚑ WE DO
   NOT RETAIN `public`. Bind the owner BARE; a consumer reaching a name THROUGH
   the module is rewired to bind at the owner itself — that rewire is the P3
   contagion, not a reason to keep the conduit alive.
   MEASURED: `Groups/V4-Normality.agda:34`,
   `open import …S4-Iso using (V₄-normal-compositional) public`, was a DEAD
   conduit on all three counts — the barrel names `V₄-normal-compositional` only
   in a COMMENT, the module already imported the owning leaf `S4-Iso.V4Normal`
   bare at :47 for its own body, and its sole consumer (`Subgroup.agda:39`)
   wants the locally-DEFINED `V₄-normal`. Deleting the statement outright left
   both the module and its consumer isolate-clean (exit 0). An intermediate cut
   of this fix merely re-pointed the flag at the owning leaf — a correct
   conduit, which is still a conduit, and was itself reverted.
   REMAINING DEBT, measured while fixing this: **87 `open import Substrate… public`
   statements tree-wide.** Each is a P2 violation whose consumers need binding at
   the owner; they dissolve as the queue reaches their modules.
   GENERAL LESSON: a repair that makes a banned construct *correct* has not paid
   anything down. Ask whether the construct should exist, not whether it points
   at the right target.

8. **THE STATEMENT'S PREFIX IS NOT ALWAYS WHITESPACE — AND THE SWEEP THAT WOULD
   CATCH IT SHARED THE BLIND SPOT (`rewire_to_leaves.py` +
   `check_indented_imports.py`, BOTH FIXED AT SOURCE).** An import can be
   preceded on its own line by a block-opening KEYWORD:
   `where open import M using (…)`. Every regex anchored `^[ \t]*` — the
   rewriter's two, and the F19 sweep's one — steps over the keyword and does not
   match. So the rewrite skipped the statement, the split deleted its target,
   the build died `[FileNotFound]` — and the sweep, whose whole job is to catch
   what the column-0 rewriter cannot see, reported **clean** over the live broken
   reference. A verifier with the same blind spot as the thing it verifies reads
   as proof of absence; that is worse than the rewriter miss.
   FIX: both now match an optional `(?:where|private|abstract)[ \t]+` prefix. The
   rewriter re-emits the keyword on the FIRST leaf import only and indents the
   rest under it (repeating `where` would open a second block); the sweep counts
   a keyword prefix as `indented`.
   MEASURED: `Algebra/Q/Embeddings.agda:74` was the surviving reference that
   failed the Q split; **13 files carry keyword-prefixed imports tree-wide**, so
   this hid a class, not one site.
   GENERAL LESSON: when a sweep and the codemod it audits are written from the
   same mental model of "what an import line looks like", the sweep cannot catch
   the codemod's blind spot. Give the verifier the WIDER pattern.

9. **`module X` IN A `using` LIST IS TWO TOKENS, NEITHER OF THEM A DEFINITION
   (`rewire_to_leaves.py`, FIXED AT SOURCE).** `using (module ℚ)` names the
   RECORD's own module — its projections — and Agda writes it as the keyword
   `module` followed by the name. The name-splitter put BOTH tokens in the list;
   neither is in the `Defines:`-derived name→leaf map, so the consumer was
   refused as unmapped and kept importing the parent the split then deleted.
   FIX: drop the `module` keyword from the token list. A record's module lives in
   the same leaf as the record, so the bare name resolves it correctly (`ℚ` →
   `Rat`) — no new map entry needed.
   MEASURED: **59 `module X` occurrences across 41 files** tree-wide.

10. **`opaque` MEMBERS WERE INVISIBLE TO THE DEF-INDEX, SO THE PRUNE DELETED
   LIVE IMPORTS (`agda_defs.py`, FIXED AT SOURCE).** An `opaque` block's members
   are ordinary TOP-LEVEL EXPORTS — the keyword seals their *definitions* from
   reduction, it does not make them private — but they are INDENTED, and
   `def_index`'s signature branch is column-0 anchored. So a module whose entire
   public surface sits inside `opaque` read as **providing nothing**, and
   `prune_imports.py` correctly-by-its-lights dropped every import of it. The
   consumer then failed `[NotInScope]` on a name that was never missing.
   MEASURED: `Linear/FromImages.agda:168` seals `linear-from-images`; the prune
   dropped its import from FIVE consumers in one run (`Codes/Hamming/H-7-4-3`,
   `Codes/ReedMuller/RM-1-3`, `Geometry/HodgeDim3/ChiralityAxis`,
   `Geometry/HodgeDim3/V4Plane`, `WitnessTower/Codeword`). Fix recovers **45
   names, 0 lost** (purely additive); **26 files** open an `opaque` block.
   ⚑ THIS CLASS GROWS. The cap-paydown discipline (⟡cap-384) tells a module over
   the heap cap to SEAL its heavy neutrals `opaque`. So every cap paydown adds
   `opaque` members — i.e. the two arcs actively feed this defect. The fix has to
   live in the index, never in a per-consumer exemption.
   GENERAL LESSON: a tool that decides "is this import dead?" is only as good as
   its notion of what a module PROVIDES. When it drops a live import, suspect the
   provides-side index before the use-side tokenizer — the tokenizer is easy to
   test in isolation (it saw the name here), the index is not.

11. **THE SPLIT DESTROYS THE PARENT'S `public` CONDUITS AND DID NOT TELL ANYONE
   (`split_lemmas.py` + `split_pipeline.py`, FIXED AT SOURCE).** `strip_using`
   correctly removes every `public` from an inherited import — a leaf must
   re-export only what it defines (P2), and the parent's prelude is copied into
   EVERY leaf, so leaving the keyword multiplies one conduit into N. But the
   parent had been PROVIDING those names to the rest of the tree, and stripping
   the keyword silently withdraws that provision. Every module reaching such a
   name THROUGH the parent is a P3 contagion site, and nothing enumerated them:
   the breakage surfaced later, as a far-away `[NotInScope]` in a file the split
   never touched, and got hand-patched one at a time.
   ⚑ NO DOWNSTREAM STAGE CAN CATCH THIS. `prune_imports` judges an import by the
   file's own BODY tokens, and a re-export's use site is by definition in another
   module — so the prune sees a `public` conduit as dead no matter how good its
   index is. The decision has to be made where the conduit is destroyed.
   FIX: `strip_using` now CAPTURES each conduit `(owner, names)` before either
   strip runs (the `using (…)` is deleted a few lines above the `public`, so a
   later capture sees neither and reports every conduit as whole-surface);
   `split()` prints `# CONDUIT: <owner> <names…>`; the pipeline parses those
   lines and rebinds each consumer at the OWNER, bare, keeping any other names
   the statement carried bound where they were.
   MEASURED: `GL3F2/GaugeGenerators.agda` re-exported `singer-Linear` from
   `Algebra.F2.FanoPlane`; two consumers (`MultiRouteEquivariance/SingerInv`,
   `…/SingerGL`) broke. A conduit that re-exported the owner's WHOLE surface
   (no `using` list) is reported as `*` and flagged for hand-binding — there is
   no name list to match against, and guessing would be worse than saying so.
   GENERAL LESSON: when a codemod REMOVES a provision, the consumers of that
   provision are part of the edit. A tool that only rewrites the file in front
   of it will keep producing breakage that looks unrelated to the change.

6. **DUPLICATE IMPORT ON REPAIR (`fix_stale_using.py`, FIXED AT SOURCE).** When
   a stale `using` name's owning leaf was ALREADY bare-imported elsewhere in
   the file, the repair re-emitted `open import <leaf>` beside the existing
   one. Not cosmetic: a parameterized module imported twice is APPLIED twice
   and elaborated twice, so a duplicate is a real cap cost (F5 in reverse).
   Fixed: before emitting, scan every line outside the statement being
   replaced for `open import <owner>` and drop owners already present — the
   common case then reduces to *deleting the stale `using` clause and adding
   nothing*, which is the correct P4 paydown.

**⚑ A GREEN `make -j` DOES NOT MEAN EVERY MODULE TYPECHECKS.** `make` rebuilds
only STALE targets, so a module whose `.agdai` is current is never rechecked —
and a `[FileNotFound]` from a since-deleted parent sits there invisibly. This
is the F4 orphan-core hazard read from the other side: there, a stale core
makes a DELETED module look alive; here, it makes a BROKEN importer look green.
Measured: a full build reported 0 errors while `Semiring/Instances.agda` still
imported the retired `Foundation.Bool`; the isolate-check found it in seconds.
So an isolate-typecheck of each touched file (Verify, below) is not redundant
with the full build — it is the only thing that sees a cached module at all.

## Verify — after every file, not at the end

```
PROCEDURE Verify():
    run   gen_build_makefiles.py                  # makefiles are GENERATED;
    assert gen_build_makefiles.py --check == OK   # hand-editing fails --check
                                                  # the generated recipe also captures
                                                  # a PER-MODULE log next to each core:
                                                  # agda/_build/**/<mod>.agdai.log
                                                  # (replayed to stderr on failure, so
                                                  # `make` output is unchanged; gitignored)

    run   check_indented_imports.py <Parent...>   # POST-REWIRE, before the build:
    assert clean (no remaining references)        # catches what rewire_to_leaves.py's
                                                   # column-0-anchored regex structurally
                                                   # cannot see — indented `open import
                                                   # <parent>` (inside a `module … where`
                                                   # body) and importers the directory-
                                                   # exclusion filter skipped (see Rewire).
                                                   # `[indented]` = a genuine miss to fix
                                                   # by hand; `[top-level]` should never
                                                   # fire — it means rewire's own map was
                                                   # wrong, treat as a tool bug.

    assert make -C agda -j  == 0 errors           # the authoritative meter
    assert no -W[no]ModuleDoesntExport warnings   # CHECK THE WARNING STREAM, not
                                                  # just the exit code: this class is
                                                  # a decomposition defect (a stale
                                                  # `using` list, F12) that NEVER turns
                                                  # the build red. Read warnings from the
                                                  # PER-MODULE logs agda/_build/**/*.agdai.log
                                                  # — the authoritative, interleave-free
                                                  # source. Clear with
                                                  # fix_stale_using.py agda/_build.

    run   fix_stale_using.py --check-cycles       # after ANY import codemod: no
    assert no leaf→ancestor / mutual edges        # module may import one that
                                                  # transitively imports it back
                                                  # (F13). Parent→leaf barrel
                                                  # edges are legitimate; leaf→
                                                  # parent edges are the defect.

    assert def_proof_separation == clean          # F4
    assert import_shape_ratchet ≤ baseline
    assert ban_ratchet          ≤ baseline        # `as`/`using` removal PAYS DOWN
    assert set1_ratchet         ≤ baseline
    assert cap_ratchet          ≤ baseline        # a split should MOVE THIS DOWN:
                                                  # elaboration peak is per-MODULE,
                                                  # so splitting is also the cap fix.
                                                  # But a PRE-EXISTING over-cap module
                                                  # is not this split's failure — see
                                                  # F15; the build stage lets an
                                                  # Error-251-only build through.
    assert carrier_locality     ≤ baseline        # F14 — the split CHOOSES this:
                                                  # an operator over carrier T must
                                                  # live under T's home directory
```

## Termination

```
measure  μ = |{ F reachable : |DeclGroups(F)| > 1 }|

Split(F) makes F atomic and emits only atomic leaves        ⇒ μ decreases by 1
Rewire(G, …) does not change |DeclGroups(G)|                ⇒ μ unchanged
DONE is monotone; the reachable set is finite               ⇒ QUEUE drains

FIXPOINT: every reachable file declares exactly one thing.
```

## Why it pays (observed, not asserted)

```
W1  minimal(d) forces you to name d's TRUE dependencies, which surfaces
    reinventions that a fat import hides.
      → `half-lt`'s `where`-local `unpack` WAS `Foundation.Nat.s≤s-injective`.

W2  Rewire strips `as` aliases and `using` clauses ⇒ ban-ratchet paydown.
      → `Wedge/Sphere.agda`'s `import … as Curve`.

W3  A leaf's closure is its own, so a consumer stops paying for a neighbour's
    imports.
      → `BinBridge.ToBinValue` needs `pow2`; the monolith would have handed it
        the entire ripple adder.

W4  Naming the anonymous witnesses makes them citable, so a residue that was an
    in-file check becomes a term other files can consume.
      → `BinMul.MulThreeFiveResidue` reads BinTrim's exact-width against
        BinMul's predicted width.
```

## Failure modes (each cost us once)

```
F1  Orphan `.agdai` for a deleted module → census reports UNDECODABLE and the
    commit is refused. Deleting the core is PART OF Split, not later cleanup.

F2  Leaving the monolith as a re-export barrel. Forbidden by P2 — it is exactly
    the conduit the policy removes, and it lets consumers keep over-importing.

F3  Narrowing with `using` instead of splitting the upstream. Banned by P4 —
    and the two rationalisations that get re-derived AROUND that ban:
      (a) "the names don't COLLIDE, so the filter is safe to just delete."
          Collision is a SYMPTOM that forces a filter to exist, never the
          criterion for splitting. A module with zero collisions and 40 defs
          still over-imports by 40 when a consumer needs 1. Globally-unique
          names do not make a fat import cheap — they make it QUIET.
      (b) "deleting the filter pays down the ban ratchet." It pays down the
          KEY COUNT while the same information is still imported, still
          ELABORATED, and scope is now WIDER than before. That is
          metric-gaming, and it is strictly worse on the axis P4 exists to
          serve. The debt a filter records is UPSTREAM; the filter is where
          it shows.
    Both were written into `scratch/strip_using.py` and the plan as doctrine
    and had to be retracted (2026-07-31). The tool is legitimate ONLY as an
    intermediate step inside a split, immediately narrowed to the owning leaf.

F4  A `data`/`record` leaf importing a `.Properties`/`.Laws`/`.Proofs` module →
    def/proof separation gate. Put the datatype in a leaf whose imports are
    proof-free.

F5  Bare imports can collide (AmbiguousName). For a genuinely ambiguous name
    the repo convention is `renaming (X to X⟦shape⟧)` — check the existing
    consumers' spelling before inventing one.

F6  Forcing mutually recursive definitions apart. They are ONE group (see
    DeclGroups); splitting them does not typecheck.

F7  Reading a pipeline's exit code (`cmd | tail; $?`) instead of the command's.
    Redirect, then read `$?`.

F8  Running `prune_imports.py` from `agda/`. `agda_defs.AG = "agda"` globs
    repo-root-relative, so the definition index comes back EMPTY and the tool
    reports "0 dropped" for every file — a silent no-op that reads as a clean
    result. Run from the REPO ROOT, paths as `agda/Substrate/…`. Sanity-check
    the tool by adding a known-unused import and confirming it is dropped.

F9  Trusting the prune without a build. `agda_defs.def_index` was blind to
    INDENTED `data`/`record` heads (a record inside `module _ (C)(R) where` —
    the ⟡set1-paydown idiom), so `Wedge.Graded` provided neither `GradedDivStr`
    nor `recon` and the prune dropped a LIVE import in four leaves. FIXED AT
    SOURCE (the head regex now allows leading whitespace) — but the standing
    rule is: the prune is a proposal, the typechecker is the arbiter.

F10 `split_lemmas.py`'s glyph-transliteration table ordered a single-character
    glyph before a multi-character one that CONTAINS it (`+`→`Plus` checked
    before `++`→`Append`), so `_++_` sanitized through the `+` rule first and
    produced a garbled name instead of `Append`. FIXED AT SOURCE: multi-
    character glyphs (`++`, `⁻¹`, …) are checked BEFORE any single-character
    glyph they contain. General form: a substring-replace transliteration
    table must be ordered longest-match-first, or checked with the sanitized
    name from a real declaration (not assumed correct from reading the table).

F11 `split_lemmas.py`'s name sanitizer stripped `-`/`_` as noise instead of
    treating them as WORD SEPARATORS, so `or-xor-and` sanitized to
    `Orxorand` instead of the intended `OrXorAnd` — a real corruption, not a
    style nit, because the collapsed name could collide with an unrelated
    declaration's sanitized name. FIXED AT SOURCE: split on `[-_]+` first,
    transliterate and capitalize each segment independently, then join.
    Verify a sanitizer against the repo's OWN prior hand-chosen leaf names
    (e.g. `ReconIsCons`, `VecUncons`) before trusting it on names it hasn't
    seen — a plausible-looking output is not the same as a correct one.

F12 STALE `using` LIST after a split. A consumer's
    `open import Parent using (a; b; c)` still names `a`,`b`,`c` after the
    monolith split moved them to sibling leaves. Agda reports this as a
    WARNING (`-W[no]ModuleDoesntExport`), NOT an error, and the names usually
    still BIND because a sibling bare import already brought them into scope —
    so the build stays green and the P4 violation is invisible outside the
    warning stream. It accumulates: 21 distinct sites in one build.
    MECHANIZED: `scratch/fix_stale_using.py agda/_build [--apply]` parses the
    warning blocks for (file, line, module, missing-names), drops the
    un-exported names from the `using` list (an emptied list becomes a bare
    import), finds each dropped name's owner by scanning for a column-0
    declaration (`name :`, `data name`, `record name`, `pattern name`,
    `name =`) — the module's own directory and leaf directory first, then a
    tree-wide index whose ties break on the longest shared dotted prefix with
    the original module — and emits a BARE `open import <Owner>`, preserving
    the statement's original indentation and its `public` flag.
    Load-bearing warnings, each of which cost real debugging:
      (a) FEED IT THE PER-MODULE LOGS, NEVER A `make -j` CONSOLE LOG. The
          generated makefiles write each module's output to its own
          `agda/_build/**/<mod>.agdai.log` (one job, one file — interleave-proof
          by construction); the tool accepts that DIRECTORY and walks
          `**/*.agdai.log`. A `make -j` console log INTERLEAVES concurrent jobs,
          so a warning block silently absorbs lines from another job and the
          parse is corrupt by construction. THE INTERLEAVE INCIDENT: one run
          against a `make -j` console log made 45 edits, several of them wrong —
          owner resolution picked a PARENT module — producing
          `CyclicModuleDependency` and `AmbiguousName` across 7 files. All
          reverted.
      (b) Apply sites BOTTOM-UP per file (descending line number). Every edit
          shifts later line numbers, so top-down application makes later sites
          in the same file miss or hit the WRONG statement. The tool does
          this; the general rule is that any log-line-driven codemod must.
      (c) Console-log parsing gotchas — these matter ONLY if someone parses a
          console log anyway (see (a); don't): Agda's warning text WRAPS, the
          missing-name list can carry a trailing `(did you mean 'X'?)` that
          parses as a name unless stripped, and the module name itself can wrap
          across lines.
      (d) An added bare import can COLLIDE with an existing APPLIED import of
          the same module. `S4-Iso/ForwardHom.agda` had a `where`-block
          `open import Substrate.Groups.S4 using (Permutation)`; the rewrite to
          the owner `Substrate.Groups.Symmetric.Permutation` was correct, but
          that module was already imported APPLIED at the top of the file
          (`… Permutation Axis`), so the new unapplied bare import gave
          `AmbiguousName` on the field `apply`. Correct resolution: both
          `where`-block imports were redundant and were deleted. Check whether
          the name is already in scope before adding an import.
      (e) The tool is LOG-DRIVEN, so one pass sees only what the last build
          reported — and a module that was NOT re-typechecked keeps its stale
          log. Run to a FIXPOINT: fix, rebuild, re-run on the fresh logs.

F13 OWNER RESOLUTION CAN PICK A MODULE THAT IMPORTS YOU BACK. Any codemod that
    resolves a name to "the module that declares it" can land on the importing
    file's OWN module (self-import), on an ANCESTOR barrel (a leaf importing
    its own parent, where the parent imports its leaves — this ALWAYS cycles),
    or on a module that reaches the importer transitively. Agda reports
    `CyclicModuleDependency`, but only when that module is next typechecked, so
    a `-j` build can go a long way before surfacing it.
    MEASURED: three separate mutual cycles inside the
    `Cocycles/V4Signature/Codeword/LiveS4Bijection` cluster, each fixed one at a
    time before the guard existed; the tree-wide scan then found seven cycle
    edges at once — of which the parent-to-leaf barrel edges were LEGITIMATE and
    only the leaf-to-parent edges were the defect.
    FIXED AT SOURCE: `fix_stale_using.py` refuses an owner that is the file's
    own module, an ancestor of it, or transitively reaches it.
    GUARD: `python3 scratch/fix_stale_using.py --check-cycles` — standing,
    tree-wide, log-independent. Run it after ANY import codemod.
    GENERAL LESSON: when a codemod adds an import, the ancestor/reachability
    check is not optional. Fix-one-reported-cycle-rebuild-find-the-next is the
    tell that the guard is missing.

F14 SPLITTING A CARRIER'S HOME SCATTERS ITS OPERATORS. `Split` names each leaf
    after its DECLARATION, which is right for lemmas and wrong for the
    operators OF a carrier: splitting `Foundation/Bool.agda` put `_∧_`, `_∨_`
    and `_xor_` in `Foundation/Bool/{And,Or,Xor}.agda` as SIBLINGS of the
    carrier leaf `Foundation/Bool/Bool.agda`, and `check_carrier_locality.py`
    flags all three — an operator over carrier T belongs under T's home.
    This is a PLACEMENT decision the split makes silently; the gate is the
    only thing that surfaces it, and it fires long after the split.
    So: when the file being split DECLARES a carrier (a `data`/`record` other
    leaves take as argument), decide up front whether the carrier's leaf is
    the directory root or a sibling, and run `check_carrier_locality.py`
    (in Verify) before moving on. Do NOT resolve a firing by adding an
    exemption — the ratchet is paydown-only, and an exemption keeps the
    scatter permanently.

F15 TREATING A CAP KILL AS A SPLIT FAILURE. `make` exits nonzero for BOTH an
    Agda error and an `Error 251` heap kill, and they mean OPPOSITE things:
    the 251 is PRE-EXISTING cap debt that no split introduces and that
    SPLITTING IS THE CURE FOR (elaboration peak is per-module). The build stage
    conflated them, so a correct split was reported as a failure whenever the
    tree already carried cap debt.
    MEASURED, on the queue's first real module: every stage passed — 4 leaves
    isolate-clean, importer rewired, 0 cycles, makefiles in sync, **0 Agda
    errors** — and the module was still parked, because 4 unrelated modules
    were over the cap. Unfixed this would have parked ALL ~1.2k modules against
    those same 4.
    FIXED AT SOURCE in `split_pipeline.py`: any `error:` line still dies; a
    build whose only failures are `Error 251` warns, names the count, and
    CONTINUES. A nonzero exit with neither still dies (do not widen this into
    "ignore build failures").
    GENERAL LESSON: before a gate treats a tool's exit code as a verdict, check
    whether that code aggregates classes with different owners. One of them is
    usually not yours to fix, and blocking on it stalls the whole queue.

F16 THE SIBLING-EDGE SCAN SAW ONLY THE *INFIX* SECTION. `split_lemmas.py`
    reconstructs an operator name from a bare token so a leaf that USES an
    operator imports the sibling that DEFINES it — but it only tried `_x_`.
    A PREFIX operator (`¬_`, written `¬ A`) and a POSTFIX one (`_!`) contribute
    the same bare token, so their edges stayed invisible one section over.
    MEASURED: `Foundation.Negation`'s `Dec` — `no : ¬ A → Dec A` — never
    imported its `Not` sibling and failed isolate-check `[NotInScope] ¬`.
    FIXED AT SOURCE: reconstruct all three sections (`_x_`, `x_`, `_x`).
    Same class as the earlier `refl`-as-constructor miss: an edge the scan
    cannot see becomes a leaf that cannot compile.

F17 INDENTATION IS NOT A STATEMENT DELIMITER. `fix_stale_using.py`'s
    `stmt_span` consumed every indented non-blank line after an import head as
    a continuation. That holds at column 0, but inside a nested `module M
    where` the FOLLOWING import is indented too — so repairing one stale name
    DELETED the neighboring imports.
    MEASURED: `Discipline.agda`'s `module Demo where` had three imports; fixing
    the first removed all three, and the build reported `[NotInScope]
    F2³-Puncturing-Cocycle` for the second. DESTRUCTIVE, not merely blocking.
    FIXED AT SOURCE: the span now stops at any line that OPENS a new statement.
    This is the standing "imports span continuations" hazard read backwards —
    treating a following STATEMENT as a TAIL.
    ⚑ SECOND DAMAGE SHAPE, and it does NOT turn the build red. The same span
    bug also SPLIT a one-line import in two and stranded its `using (...)` tail
    BELOW an intervening comment block — `ClassFunctor.agda` ended up with
    `open import …Morphism` at :26 and an orphaned `using (Free-monoid; …)` at
    :36. It still COMPILED (those names were in scope via a bare import
    elsewhere), so it surfaced only as `-W[no]ModuleDoesntExport` — the exact
    warning-only P4 violation F12 exists to sweep.
    THE DIAGNOSIS TRAP: the site was dismissed TWICE as "fixer declines, no
    owner found" and then "stale-log false positive", both times from a ~7-line
    `sed` window that ended before the orphan. The build log carried the true
    span (`27.3-37.44`) throughout. READ THE WARNING'S SPAN, not a window you
    chose — a multi-line span is telling you the statement is bigger than you
    are looking at.
    AFTER ANY `fix_stale_using` RUN THAT PREDATES THIS FIX: rebuild, re-sweep
    to a FIXPOINT (`dry-run: 0 site(s)`), and treat a site that persists across
    a rebuild as real damage rather than a stale log.

F18 A PARENT'S PRE-EXISTING SIBLINGS ARE NOT LEAVES. `rewire_to_leaves.leaf_map`
    read `Defines:` from EVERY `.agda` in the leaf directory. When the parent's
    namespace already held modules (`Algebra/Z.agda` beside 37 modules under
    `Algebra/Z/`), those were misread as leaves — and any whose BASENAME
    collided with a real leaf (`Sub`, `Mul`, `CommRing`, `Euclid`, …) was then
    excluded from the rewire as a self-import, so it kept importing the DELETED
    parent.
    MEASURED: 26 leaves inferred where the split wrote 8; 39 surviving
    references. Worse, the bare-import branch then expanded `open import
    <parent>` into all 26, handing `Add/Op.agda` 27 imports (it needs 2)
    including one that imports it back — **670 cycle edges tree-wide** across
    702 files. Recovered only from a pre-run snapshot.
    FIXED AT SOURCE: a leaf must carry the splitter's own provenance marker
    (`split horizontally out of <parent>`), not merely live in the directory.
    GENERAL LESSON: directory membership is not provenance. When a codemod
    infers a set from a filesystem layout, have it require a marker the
    codemod itself wrote.

F19 THE `[indented]` SWEEP RESULT WAS BEING HAND-FIXED. `check_indented_imports`
    correctly flagged imports the column-0 rewriter could not reach, and the
    pipeline told the operator to fix them BY HAND. A hand fix does not survive
    a re-run — on a retry the same files re-appear in the sweep, and under
    context pressure the knowledge of what was done is gone.
    FIXED AT SOURCE: `rewire_to_leaves` now captures the leading indent and
    rewrites in place, re-emitting each leaf import at the SAME indent (Agda's
    layout rule closes the enclosing block otherwise). The sweep remains as the
    verifier; it should now report clean rather than hand it back.

F20 THE REWIRE OVER-IMPORTS, AND AN UNWANTED NAME CAN BREAK A FILE. The rewire
    is deliberately WIDE (bare import → every leaf; `using` → every owning
    leaf). That is safe for names a file ignores — but a widened scope can make
    previously-unambiguous SYNTAX ambiguous.
    MEASURED: `CFMatrixBridge/Properties` used only `-ℤ_` (the `Int2` leaf) yet
    was also handed `Int`, whose PREFIX `+_` collides with `Foundation.Nat`'s
    `_+_` SECTION, making `cong (a * p₁ +_)` an
    `[AmbiguousParseForApplication]`. NOTE the diagnosis trap: the message
    lists two parses that LOOK identical (`(a * p₁) +_` vs the same "(section)")
    — parenthesizing does NOT help, because the ambiguity is prefix-op vs
    section, not precedence. Dropping the unused import is the fix.
    FIXED AT SOURCE: the pipeline now runs `prune_imports.py` over every
    rewired consumer (stage 6b), so over-import is removed mechanically.
    GENERAL LESSON: pair every widening step with the narrowing one. The ban
    forbids `using` filters; it does not oblige you to import what you do not
    use — pruning is how a bare import stays minimal.

F21 AN `open X` OF A LOCALLY-DECLARED X IS A BODY LINE, NOT A PRELUDE LINE.
    `split_lemmas`'s `OPN` class hoists every `open …` into the shared import
    block, because a file-scoped IMPORT is valid wherever it sits. That is
    false for an open whose target is declared IN THIS FILE: hoisting puts the
    `open` ABOVE the `record`/`data`/`module` it opens, and every leaf then
    fails scope-checking.
    MEASURED on `Substrate.Algebra.Q`: `record ℚ` + `open ℚ public` produced a
    `Q/Denominator.agda` carrying `open ℚ public` at :18 with the record's own
    leaf imported below — isolate-check exit 42, `[NoSuchModule] No module ℚ`.
    FIXED AT SOURCE: collect the file's own `data`/`record`/`module` names and
    hoist an `open` only when its head is NOT one of them.

F25 A SPLIT MOVES THE CARRIER INTO A LEAF, WHICH RELOCATES ITS CARRIER-LOCALITY
    HOME OUT FROM UNDER ITS OWN OPERATORS. `Foundation/Bool.agda` declared
    `data Bool`, so operators under `Foundation/Bool/` satisfied the gate.
    Splitting moved the carrier to `Foundation/Bool/Bool.agda`, whose home
    directory is `Foundation/Bool/Bool/` — a directory that does not exist. The
    operators did not move; the home moved. Same for ℤ (`Algebra/Z.agda` ->
    `Algebra/Z/Int.agda`). MEASURED: 8 carrier-locality violations, 7 of them
    this artifact.
    ⚑ DO NOT "fix" this by widening the gate to accept siblings, and do not
    relocate the operators into `Bool/Bool/`. Both are wrong: the gate-widening
    admits any operator dropped anywhere in a 26-file directory, and the
    relocation is UNSTABLE (split the carrier again and every operator must move
    again — the ban and carrier-locality would fight permanently).
    THE FIX IS TO COLLAPSE THE REDUNDANT NESTING: `X/X.agda` -> `X.agda`. The
    parent slot is empty precisely BECAUSE the split vacated it, so restoring
    the carrier as parent puts its operators back in its subtree. No rule is
    loosened and no operator moves. 8 -> 1 violations; three cap-debt modules
    also started passing (shorter import paths = less elaboration).
    TWO DISTINCT OPERATIONS, kept distinct in `collapse_carrier_nesting.py`:
      `X/X.agda -> X.agda`     REDUNDANT NESTING — name unchanged, safe to infer.
      `X/Leaf.agda -> X.agda`  PROMOTION — RENAMES the module (Algebra.Z.Int ->
                               Algebra.Z), every importer sees it. Requires an
                               explicit `--promote`; loosening the X/X guard to
                               cover it would let the tool flatten ANY leaf into
                               its parent, which is what that guard prevents.
    ⚑ NOT every violation is this artifact. `_mod-suc_` in `Algebra/Nat/` was a
    genuine misplacement (`data ℕ` was correctly at `Foundation/Nat.agda`) whose
    twin `_div-suc_` sat in the SANCTIONED baseline for the same reason. Homing
    both under `Foundation/Nat/` cleared the last violation AND auto-lowered the
    ratchet 6 -> 5 — paying down an exemption rather than adding one. Check the
    dependency direction before moving anything INTO Foundation: both imported
    only Foundation, so no upward edge was created.

F27 A RENAME REWRITES THE PATH BUT NOT THE NAME-SET, AND AGDA REPORTS THAT AS A
    WARNING. After `Foundation/Bool/Bool.agda -> Foundation/Bool.agda`, the
    parent holds only `Bool`; `_∧_`/`_∨_` live in sibling leaves. A consumer's
    `open import Substrate.Foundation.Bool using (Bool; _∧_)` then names
    something the module no longer exports — which Agda reports ONLY as a
    warning at the import, surfacing far away as a bare `[NotInScope] _∧_` at
    the USE site (GUnit/Base.agda:37). Silent at the point of damage: exactly
    the class the stale-`using` sweep exists for.
    THE FIX IS `rewire_using` in `collapse_carrier_nesting.py`, wired into BOTH
    apply paths (collapse/promote AND relocate): split each consumer's `using`
    list BY OWNER — names the module still defines stay, names now owned by a
    sibling leaf get their own BARE `open import <sibling>` (bare, per the ban).
    ⚑ THE SCAN MUST SEE CONSTRUCTORS AND RECORD FIELDS, NOT JUST TOP-LEVEL
    HEADS. `true`/`false` are constructors of `data Bool` — INDENTED, so a
    column-0-only scan misses them and they fall through to "keep" BY ACCIDENT.
    That is the right placement for the wrong reason: a name the scan cannot see
    is indistinguishable from one a sibling owns, so the next carrier whose
    constructors DID move would be mis-routed silently. Make the scan explicit.

F30 A RECORD SPLIT'S BARE IMPORTS EXPOSE FIELD-PROJECTION COLLISIONS — CURE
    THEM BY RENAME-AT-SOURCE, IN THE TOOL, NOT BY HAND PER SPLIT. Splitting a
    record makes its importers' imports BARE, so the record's FIELD PROJECTIONS
    enter scope wholesale. Two error shapes follow, and they are ONE defect at
    different arities:
      [ClashingDefinition]            a consumer's own top-level def collides
                                      with a projection. MEASURED on the
                                      CategoryOf split: `M40Closure.compose`
                                      (its A₄×ℤ₂ group law, 8 local uses, 5
                                      importers) vs `CategoryOf`'s field
                                      `compose`.
      [AmbiguousOverloadedProjection] an APPLIED `open Record value` binding is
                                      shadowed by that same projection.
                                      MEASURED: `Opposite.agda:39`'s `id`, from
                                      `where open CategoryOf C`.
    ⚑ THE SECOND SHAPE IS A CLASS, NOT A ONE-OFF: 403 applied-open sites across
    275 files. Every record split with many importers will hit it. Only files
    that BOTH bare-import the record AND apply-open it collide — `Iso.agda`'s
    unapplied `open CategoryOf` introduces the same projections a bare import
    does and is fine; `Opposite.agda`'s `open CategoryOf C` creates a SECOND,
    different binding and is not.
    ⚑ WHICH SIDE RENAMES — NEVER THE FIELD. The projection is the canonical
    name the split just made importable; moving it pushes the collision onto
    every other consumer. Rename the CONSUMER's local def; the error names its
    home. The ban forbids `using`/`hiding`/`as`/qualifier on the import, so
    rename-at-source is not one option among several — it is the only compliant
    cure, and `rename_at_source.py` already implements it.
    ⚑ THE APPLIED-OPEN SHAPE HAS NO LOCAL DEF TO RENAME. Cure it by QUALIFYING
    AT THE VALUE (`CategoryOf.id C`, `CategoryOf.compose C f g`). A projection
    applied to a value is not an import directive, so it stays ban-clean.
    FIXED AT SOURCE: `split_pipeline.cure_collisions` parses the build output,
    renames the consumer's def via `rename_at_source`, and rebuilds — instead
    of `die()`ing. It cures the ClashingDefinition shape (mechanical owner) and
    REPORTS the applied-open shape with the qualify recipe rather than guessing,
    because picking the wrong binding there changes what a term MEANS and only
    the typechecker can arbitrate.

F29 PRUNE BEFORE ISOLATE-CHECK, AND A SHARED NAME IS NOT EVIDENCE FOR *THIS*
    IMPORT. Two defects, one cause: every leaf inherits the MONOLITH's whole
    import block, so a `List`-only leaf also imports `Vec`. Both are bare (per
    the ban), so the first shared operator is a genuine `[AmbiguousName]`:
    `Enumerate/ConcatMapL.agda:25` failed on `_++_`, which BOTH
    `Foundation.Vec` and `Foundation.List` provide. The leaf's own content was
    fine — `Vec` was dead.
    (a) THE PIPELINE ORDER WAS WRONG. `split_pipeline` isolate-checked at
    stage 2 and pruned at stage 3, so every leaf was typechecked while still
    carrying imports it does not use. That reports a fat-import artifact as if
    it were a content defect, and fails leaves that are correct. Prune FIRST,
    then check.
    (b) `prune_imports` KEEPS THE DEAD IMPORT, because `[]`/`_∷_`/`_++_` are
    real token hits — just hits `List` already explains. ⚑ THE OBVIOUS FIX IS
    UNSOUND; I TRIED IT AND REVERTED IT. Counting only what a module UNIQUELY
    provides among the file's other bare imports drops `Vec` from `ConcatMapL`
    correctly — and then breaks everything else, because PROVISION OVERLAP IS
    SYMMETRIC: the rule cannot tell WHICH of two overlapping modules the file
    means, so it drops whichever it scans second. MEASURED: 13 of 20 Enumerate
    leaves broke — `Perms` lost `Vec` (the module it genuinely uses, `[]` at
    type `Perm zero`), `LenMap` lost `Nat` (`suc` NotInScope) — and it did not
    even fix its target: `LengthAppend` stayed `[AmbiguousName]`. A one-file
    success is not evidence for a tree-wide rule; the isolate-check over ALL
    the leaves is.
    ⟹ Disambiguation needs the TYPE (`[]` at `List B` vs at `Vec _ zero`),
    which a token scan does not have. So the ambiguity is NOT the prune's to
    fix — it is the UPSTREAM SPLIT's obligation (F22). Splitting
    `Foundation.Vec`/`Foundation.List` so a leaf imports only the one it uses
    is the fix; a smarter prune heuristic is not.
    ⚑ THE TELL IS AN ERROR THE LEAF'S OWN CONTENT DOES NOT WARRANT. A
    one-definition leaf cannot legitimately be ambiguous about an operator it
    uses once. Reach for the inherited import block, not the definition.
    ⚑ `prune_imports.py` WRITES BY DEFAULT — it has no `--apply`. Passing one
    makes it try to open `--apply` as a file, and it dies PART-WAY THROUGH the
    list, leaving some files pruned and the rest not.

F28 A MODULE NAME IN A COMMENT IS HISTORY, NOT A REFERENCE — MASK COMMENTS
    BEFORE REWRITING. `rewrite_refs` matched the module name anywhere in the
    file, so repairing the stale `Foundation.Negation` import reported SEVEN
    files. MEASURED: 6 were comment-only ("split out of
    Substrate.Foundation.Negation") and exactly 1 was a live import. Rewriting
    all 7 is not more thorough, it is wrong in 6 places — and wrong invisibly,
    because prose does not fail to typecheck. Worse, each split leaf's comment
    names its own FORMER PARENT, so the rewrite would make every leaf claim to
    have been split out of itself (self-reference).
    THE FIX: partition each line at `--` and substitute only in the code half.
    7 -> 1 on the same input. The tell that this class exists at all: a repair
    whose file-count is much larger than the error-count the build reported —
    the build named ONE `[FileNotFound]`, the rewriter offered seven files.
    ⚑ THE ERROR NAMES THE MODULE, NOT THE LINE YOU SUSPECT — BUT NAMING THE
    MODULE IS NOT AN ALIBI. S5Fixpoint.agda:20 was `[FileNotFound]` on
    `Foundation.Negation` while the adjacent line 21 was one I had just
    edited. Reading the diagnostic body correctly redirected attention to
    line 20; I then wrongly concluded the breakage was "unrelated to my
    change" and inherited from earlier history. `git diff` showed BOTH lines
    were my own edits from the same session, and `git status` showed the
    Negation split was UNCOMMITTED working-tree state — my own work minutes
    earlier. The split had already broken line 20; my rewire on line 21 is
    what caused the module to be re-typechecked and the breakage to surface.
    ⚑ A CONTEXT COMPACTION IS HOW THIS HAPPENS. After a compaction, your own
    uncommitted work reads as inherited history — the tree looks the same
    either way. Before writing "pre-existing" / "unrelated" / "from an earlier
    arc" about ANY breakage, run `git status --porcelain <file>` and
    `git diff <file>`. Uncommitted-and-modified means it is THIS session's,
    whatever your recollection says. The diagnostic body tells you WHICH
    module; only git tells you WHOSE change.

F26 THE TWO HALVES OF A RENAME CAN COME APART, AND A REVERT IS HOW. Moving the
    file and repointing the references are separate edits; a `git checkout` that
    is broader than intended can restore an old import line whose target file
    has already moved. The result is `[FileNotFound]` at the import, far from
    the rename that caused it (ModEquiv.agda:31 naming
    `Algebra.Nat.Mod.ModSuc` after it became `Foundation.Nat.ModSuc`).
    ⚑ DO NOT HAND-PATCH THE LINE. That re-fixes one reference and leaves the
    class — if the revert touched N files it will surface N times. Run the SAME
    rewriter the rename used: `rewrite_refs` is factored out of `relocate` and
    exposed as `--rewrite-refs-to`, so a stale reference is repaired by the
    mechanism that created it, and every other stale reference goes with it.
    Two guards keep repair-mode honest: it REFUSES when the source module still
    exists (that is a live module wanting `--to`, not a stale reference) and
    when the destination does not (a typo would silently rewrite the tree onto
    a nonexistent module). The right-boundary `(?![\w.])` is load-bearing:
    `Foundation.Nat.Mod` must not match inside `Foundation.Nat.ModEquiv`.

F24 THE CONSERVATION GUARD REFUSED THE SPLIT INSTEAD OF RECORDING THE RESIDUE —
    AND A BARREL COULD THEREFORE NEVER BE SPLIT AT ALL. The guard's duty is that
    nothing vanishes SILENTLY; it is not that every line must be placeable. Prose
    the parser cannot attach to a unit (a tower summary, a trailing closing
    comment with no following definition) is real content with no home. Aborting
    leaves the conduit standing; dropping it is silent deletion. The third option
    is the right one: WRITE IT OUT with provenance.
    MEASURED: the refusal was blocking 132 modules, and 152 modules are PURE
    BARRELS (zero units — no definitions to split into leaves), which is exactly
    backwards: a barrel is the module most in need of dissolving. A barrel's
    split correctly yields 0 leaves and DELETES the file; its content was never
    lemmas, only conduit + prose.
    THE FIX: `parse` returns a 6th value `residue` = [(file_line, text)]; `split`
    writes `<outdir>/RESIDUE.md`. Two things the first cut got wrong, both caught
    by checking the output against the source rather than trusting it:
      (a) LINE NUMBERS MUST BE THE FILE'S. `body` starts at `last+1` (after the
          leading import block), so `enumerate(body,1)` reported line 2 for what
          was line 96. Provenance you cannot look up is not provenance — the
          whole point is that a reader can open the original and see context.
      (a2) THE OFFSET DRIFTS PAST A MID-FILE IMPORT. `body` is NOT contiguous
          from `last+1` — a mid-file import and its indented continuations are
          hoisted into `imports`, so every later body index is short by the
          hoisted count and `last+2+i` drifts by exactly that much. MEASURED:
          15 of 151 barrels mis-numbered; Z30JointGenViaProduct drifts 8 lines
          from its 7-line mid-file import, reporting correct residue TEXT under
          a line number pointing at an import argument. FIX: record the true
          line as each body line is appended (`bodyln[]`), never compute it.
          ⚑ Capstone has no mid-file import — validating on it alone showed
          nothing. One file is not a class.
      (a3) COMMENTS INTERLEAVED BETWEEN IMPORTS are lost by BOTH collectors:
          the leading-import loop skips them (`elif … startswith("--")`), and
          the body loop never sees them because they sit in the import region.
          Harmless in a file with definitions (they annotate imports the leaves
          inherit); in a BARREL they are the entire documentation of what each
          conduit is FOR — AES.agda's "AI-8 — GF(2⁸) is a field." labelling each
          re-export. MEASURED: 37 of 151 barrels carried such comments, all
          silently dropped.
      VERIFICATION THAT CLOSED IT: for all 151 barrels assert (i) every residue
      line number resolves to that exact text in the source, and (ii) every
      non-blank source line is accounted for — residue, hoisted import, OPTIONS,
      or module decl. Both now 0/151. Run this whenever the residue path changes;
      the one-file check passed while 37 files were losing content.
      (b) THE HEADER IS BODY TOO, WHEN THERE ARE NO LEAVES. `parse` never puts
          the pre-module header in `body`, so conservation cannot see it — fine
          for a file WITH definitions (each leaf gets a generated header, the
          original is legitimately superseded), but a BARREL has zero units so
          the header IS the entire document. On Algebra.Module.Capstone the
          first cut reported "6 unplaced lines" and silently dropped the 55-line
          M1-M10/Mod1-Mod10 tower summary and gap-closure table. Now 62 lines,
          every number verified to resolve against the source.

F23 `strip_using` DROPPED THE `using` FILTER AND LEFT THE `public` — SO A SPLIT
    MULTIPLIED THE RE-EXPORT CONDUIT INSTEAD OF REMOVING IT. A `public` on an
    IMPORT makes a module export names it does not define; after a split there
    must be NO re-exports at all, because a leaf holds one definition and
    re-exports exactly what it defines. The parent's import prelude is copied
    into EVERY leaf, so a surviving `public` does not merely persist — it goes
    from one conduit to N.
    MEASURED: 36 parseable conduit-carrying modules carry 88 `open import
    Substrate… public` statements between them; before the fix all 88 survived
    `strip_using` (and would have been multiplied by each file's leaf count).
    After: 0.
    ⚑ NOT the same as `open <LocalRecord> public` — that re-exports the field
    projections of a record DECLARED IN THIS FILE, which IS "only what it
    defines" (345 such local opens tree-wide; `open ℚ public` under `record ℚ`
    is the type case, and F21 keeps it in the record's own leaf). The
    discriminator is import-vs-local, NOT the `public` keyword. Stripping the
    local form would delete a record's accessors.

F22 A LEAF'S `[AmbiguousName]` IS AN UPSTREAM-SPLIT OBLIGATION, NOT A PRUNE
    BUG. A leaf inherits the monolith's whole import block with `using` filters
    stripped, so two upstream modules that both export a name are now both in
    scope and the name is ambiguous.
    MEASURED: `Enumerate/ConcatMapL` uses `List._++_`, but the parent's block
    also carried `Foundation.Vec` (filtered to `Vec; []; _∷_; map; tabulate`).
    Bare, `Vec._++_` and `List._++_` collide — exit 42.
    ⚑ DO NOT "fix" this by teaching `prune_imports` to drop an import that is
    fully shadowed by another. It CANNOT be: if one import shadows another,
    the shadowing module HOLDS MORE THAN THE CONSUMER REQUIRES, and that is
    the P4 obligation firing — pointing UPSTREAM, exactly as designed. A
    drop-the-shadowed heuristic leaves the same information imported and
    removes the evidence: F3 metric-gaming, one layer down.
    THE FIX IS THE QUEUE: put the over-holding upstream (`Foundation.Vec`) on
    the split queue. Once it is leaves, the consumer bare-imports the leaf that
    owns `_++_` and there is nothing left to shadow. `prune_imports` narrows
    what a file does not USE; it must not adjudicate which of two providers a
    file MEANT — that question only has an answer after the upstream split.
```

## Scope note

Enforce() is seeded by an arc's touched files, not by the tree. The closure it
eventually reaches is (transitive importers ∪ transitive imports) of the seed —
which is the whole connected component, and is intended. BFS + green-at-every-
step is what makes that safe to do incrementally and abandonable at any level.

### F31 — the pattern-variable class: a MISSING constructor import silently makes a clause a catch-all

Splitting narrows a leaf's imports to what `prune_imports` sees it USE. But a
CONSTRUCTOR used only in a left-hand-side PATTERN can be missed: if its module
is absent, Agda binds the name as a fresh pattern VARIABLE rather than erroring,
so the clause becomes a CATCH-ALL that matches everything and reduces to nothing.

The symptom is never `[NotInScope]` at the pattern. It is an `[UnequalTerms]`
DOWNSTREAM, blaming a definition that is correct:

```
morton bs != boolToℕ false of type ℕ
when checking that the inferred type of an application
  value bs + value bs ≡ zero + zero
matches the expected type
  value (false ∷ bs) ≡ zero
```

Here `value (false ∷ bs)` refuses to reduce, and every plausible cause is wrong:
`value = morton` is definitional, `Bin = Vec Bool`, `bit = boolToℕ`, and there is
exactly one `_+_`, one `Vec`, one `boolToℕ` tree-wide — each of which costs a
grep to eliminate. The real cause is that `false` was a variable, so the clause
never selected `morton`'s cons case at all.

DIAGNOSTIC (do this FIRST when a definitional reduction "should" fire and does
not): probe the reduction in a scratch module with the imports you EXPECT, then
diff that import list against the failing file. If the probe is green and the
file is not, the file is missing a constructor's module — not a lemma.

```agda
chk : {n : ℕ} (bs : Bin n) → value (false ∷ bs) ≡ value bs + value bs
chk bs = refl      -- green in isolation ⇒ the failing file's scope is the bug
```

FIX: import the constructor's DEFINING leaf (`Foundation.Bool.Bool`, not
`Bool.BoolToNat`). ⚑ The rewire pulls in the leaves a file's *expression* uses;
a leaf whose only use is a PATTERN can fall out. `prune_imports` will not restore
it either — from its side the import genuinely looks unused, because the pattern
occurrence has been captured as a binder. Pattern positions are the blind spot of
both tools; the isolation probe is what closes it.

⚑ SAME CLASS, opposite direction (F30's converse): a constructor import that
arrives UNWANTED captures what was a pattern variable. `PatternShadowsConstructor`
is the warning for that one; there is NO warning for this one. A pattern name is
a constructor iff its module is in scope — the two failure modes are one fact
read from either side.

### F32 — an OPTIONAL keyword-prefix group must not also own the INDENT

`rewire_to_leaves` matched an import's optional block-keyword prefix as

```python
^([ \t]*(?:where|private|abstract)[ \t]+)?open import {P}…
```

The indent `[ \t]*` sits INSIDE the optional group, so when no keyword is
present the group does not participate and there is no whitespace matcher left
before `open`. The pattern then only matches at column 0 — every plain-indented
import is silently skipped, and the survivor keeps importing a module the split
is about to delete (`[FileNotFound]`, far from the edit).

MEASURED: `Algebra/Q/Properties/CanonicalBezout.agda:93` — an import indented
under a bare `private` block. One survivor across nine monolith retirements, so
the class is rare enough to look like an isolated typo and is not.

FIX: hoist the indent OUT of the optional group so it always applies —

```python
^([ \t]*(?:(?:where|private|abstract)[ \t]+)?)open import {P}…
```

The whole prefix (indent + optional keyword) stays ONE capture, because the
emitter re-uses it to re-indent the leaf imports; losing it breaks Agda's
layout rule and closes the enclosing block.

⚑ THE VERIFICATION LESSON, which cost more than the bug: the survivor-grep used
to confirm "0 remaining references" carried the SAME column-0 anchor as the
buggy tool, so it confirmed the tool's own blind spot and reported success. A
check that shares the suspect's assumption is not a check. Sweep for survivors
with a pattern that admits ANY indent and ANY block keyword — deliberately
WIDER than the rewriter — so the check can fail where the tool did.
