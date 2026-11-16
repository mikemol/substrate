# bazel and the cross-repo surface

The make→bazel evaluation, the three-repo audit that informed it, and the hook family that
turned out to be the same arc seen from the other end.

⚑ THIS SHARD EXISTS BECAUSE THE INDEX COULD NOT NAME ITS CONCERN. `toolmodes-split.md`
routes ten shards, every one about this repo's own tooling; nothing covered a question whose
subject is FOUR REPOS. A concern invisible to the index is one nobody can decide is too
large — the same finding Ⓝ133a recorded when the derived-interface arc was buried in a shard
whose title did not name it.

## Ⓝ133h ⟡bazel-shard — the audit, and what survived cross-feeding it

Three read-only audits (linux-sources, paperkit, cassian-observability), then each auditor
was given the other two reports and asked for a second pass. Two operator corrections landed
mid-flight: that remote executors would be in play, and that the agents needed to study the
Starlark itself rather than the configuration around it.

**The three repos sit at three granularities, all generated, none hand-written.** paperkit
per-CLAIM from a bib at fetch time; linux-sources per-FILE with a checked-in BUILD; cassian
per-CHECK-UNIT. ⚑ Substrate's natural unit is per-MODULE, and linux-sources' shape is the
direct precedent — its "file plus transitive import closure as `data`" is structurally what
`Flat.mk` already computes from parsed `open import` lines. Its generator's own docstring
names substrate's makefile-generator pattern as its model.

### What the load phase does: nothing

| phase | what runs | what happens |
|---|---|---|
| GENERATION (Python) | `ast.parse`, closure fixpoint, f-string emission | all graph shape |
| LOADING (Starlark) | `load()` plus the rule calls | nothing computed |
| ANALYSIS (Starlark) | the rule impl | per-target action wiring |
| EXECUTION | the check command | the verdict |

⚑ So linux-sources is not a counterexample to substrate's generate-everything habit — it IS
that habit, ported, with a real action graph out the other end. The emitter is f-string
concatenation, and it renders explicit targets rather than calling a macro.

⚑⚑ AND THE MACRO IS NOT THE FIX FOR SUBSTRATE'S SCALE. Starlark has no file I/O outside
repository rules, so it cannot parse an import line; a macro would still have to be PASSED
each module's dependency list, and those edges are nearly all of the bytes. The file shrinks
by boilerplate only. The real options are sharding BUILD files per directory — which also
serves the analysis-heap concern by letting a gate target a subtree — or computing deps in a
`repository_rule` at fetch, which is paperkit's branch.

### `ctx.info_file` is a depset input and nothing more

The command never reads it. Declaring it an input puts the workspace-status file's content
hash into the action key, so bumping a tool changes those bytes and every dependent action
re-runs. ⚑ That is precisely why the `toolchain` tier can omit `no-cache` where `local`
cannot: `local`'s unpinned state has no file to hash. **The stamp converts "uncacheable" into
"cacheable with an explicit fingerprint."**

⚑⚑ CASSIAN KEPT THE OMISSION AND DROPPED THE THING THAT EARNS IT, on the ground that it has
no corpus to stamp — sound about the CORPUS stamp, and it does not reach the TOOL stamp.
Blast radius is currently zero because only two targets are toolchain-tier; the hazard ARMS
at the convergent-checker commit, whose whole purpose is cache reduction. Cassian confirmed
this from its side and is closing it with pinning and the stamp together.

⚑ For substrate: agda's version, backend and RTS options govern every `.agdai` and none is
hashable through PATH or the shim. **Hash a content digest, not a version label** — a label
is identical across differing builds, measured here and independently next door. And hash
what the verdict READS, reachable in the workspace-status command's own environment, which
is more sanitized than a toolchain action's.

### The staleness gate, and the adversary substrate has pre-made

Adding an import that introduces a NEW edge leaves a checked-in `data` list wrong; bazel
re-runs the action but with a too-narrow key. Only a whole-tree-keyed staleness slice catches
it. ⚑ Theirs failed once: the generator writes TWO files, `--check` reds on either, but the
slice keyed only one — so a hand edit to the other went **cache-hit green over the very file
it exists to check**.

⚑⚑ I TOLD THEM SUBSTRATE HAD THIS PRE-MADE AND THAT WAS WRONG. `gen_build_makefiles --check`
iterates the SAME `targets` dict it would write from, so there is no enumeration to desync,
and the deeper reason is that substrate's gate has no cache key at all — it recomputes and
byte-compares every run. The proxy has a re-gate cheap enough to run unconditionally. The
finding transfers only IF substrate migrates, which is exactly when a key appears. Corrected
to them in writing.

⚑ Their visibility half stands and would bite: keying the second artefact exposed that it was
not in its package's `exports_files`, a cross-package dependency failure. Substrate's
generator writes into a subpackage, so the same wall arrives the moment the second artefact
is keyed.

### Resource bounding: two repos landed independently on "a cgroup, outside bazel"

paperkit measured that `resource_set` bounds nothing and VENDORED SUBSTRATE'S `cgroup-scope`.
Cassian's real bound is a `MemoryMax` on a systemd unit, after measuring that its configured
task size is not read at all. ⚑ Cassian quotes paperkit's "bazel schedules within a generous
budget" constraint while shipping no `resource_set` — a constraint quoted but not exercised,
which it confirmed.

⚑⚑ MEMBUDGET SURVIVES THE PORT, and the mechanism is the reason: the cap resolves into a
shell VARIABLE at EXECUTION time behind a `probe` guard, so the same command runs either way
and **the action key does not vary by machine**. A capability check at analysis time would
fork the cache across boxes. The retry-on-OOM ladder then lives inside the tool, below
bazel's visibility, which is what preserves it.

⚑⚑⚑ BUT REMOTE EXECUTION AND RESOURCE BOUNDING ARE MUTUALLY EXCLUSIVE IN EVERY MODEL SEEN.
Cassian's port lease survives `--config=remote` only by accident of colocation — its executor
runs `Network=host` with isolation `none`, so one netns, one filesystem, one `$HOME`. Change
any of those and the ledger forks, and worse, `pid:starttime` liveness reads a live holder as
dead and GCs its lease. What actually saves it is `no-remote` on both host-coupled tiers, so
every leasing arm is pinned local and the lease never meets the executor. Cassian confirmed
this was arrived at implicitly and is banking it as a declared partition, and confirmed its
executor has no committed plan to go off-box.

⚑ FOR SUBSTRATE THE COST IS EXPLICIT: every action here is resource-bound, so this partition
puts the entire Agda graph on the local side. Bazel would buy the DAG, per-gate caching and
granularity — **not distribution.**

⚑⚑⚑ AND SUBSTRATE SHIPPED THE OPPOSITE CLAIM INTO EVERY GENERATED BUILD FILE UNTIL IT WAS
CORRECTED [@bz-double-bound-corrected]. `bazel_emit.UNRESOLVED[0]` read *"the two together would
double-bound"* — filed as an open design question when its premise was already false. There is no
double-bounding to fear, because the two layers answer DIFFERENT QUESTIONS: the scheduler decides
HOW MANY run at once, the cgroup lease decides WHETHER THIS ONE FITS. Neither is redundant, and
membudget was never the thing bazel might replace.

⚑⚑ CASSIAN ADOPTED THAT AS THE INTERFACE CONTRACT FOR ITS OWN RBE INTEGRATION, and returned a fact
that narrows it further: its executor runs `default_isolation_type=none`, so an action shipped over
REAPI runs in the EXECUTOR's cgroup under the executor's limits. Our lease is then PRE-SUBMISSION
admission — it decides whether we submit, not whether the action fits where it lands. ⚑ The
self-healing retry ladder does not survive that trip: it works because we own the cgroup that kills
us, and remotely the kill is someone else's and the ceiling is fixed.

⚑ SO THE LADDER MOVES CLIENT-SIDE AND NEEDS A TERMINAL CASE — a module whose peak exceeds the
runner is not a slow remote action but a never-remote one, which makes this a PARTITION of the
census rather than a retry policy. Cassian's runner size is a tunable rather than a law, so where
that line falls is a joint decision. **Unmeasured here**: nobody has read `buildtime.py --mem`
against it, and that read decides whether remoting is a whole-tree move or a subset one.

### What substrate adopts, ranked by the source's own reason

The three peers rank their own mechanisms, and the ranking survives being read from outside. **Two
of them decide open questions in substrate's emitter rather than merely informing it.**

⚑ **The tier ladder is directly instantiable** [@ado-tier-ladder] — sandbox hermetic and cached,
toolchain host-coupled but cacheable, `local` uncached and always re-run. That last tier is the
sound placement for an action over unpinnable live state, which is what substrate's `.ingested`
stamp chain is: a cached verdict there would bank a die-roll.

⚑⚑ **And the toolchain tier is adopted WITH CARE, which settles Ⓑ9's first question rather than
leaving it inherited** [@ado-fingerprint]. Its category is principled and its implementation caches
on an incomplete fingerprint — *derive the fingerprint from the invocations, or do not cache*.
Substrate's compile shells out to `agda` through the membudget PATH shim, resolved off `PATH` and
unhashed, so an inputs depset would carry the sources and **not the compiler version**. The compile
is sandbox-tier ONLY with the toolchain pinned into the key; otherwise toolchain-tier with the pin
as deferred debt.

⚑⚑⚑ **The adoption with the highest value during the evaluation itself was found in a directory
listing, not in any of the three reports** [@ado-path-independent]. Path-independent caching matters
most while migrating, because a migration evaluation is precisely what produces a second checkout —
and two of the three peers already share a repo-namespaced disk-cache parent. **A convention visible
in `find` output was invisible to a careful reading of the documents describing the systems that use
it.** The peer's framing is the transferable half: a document is a description by someone who
already knows what to look for; the filesystem is not.

### The sandbox contradiction resolves, and neither repo enables the flag

paperkit measured the hermetic sandbox as necessary; cassian measured it as broken. The
discriminating variable is whether a check needs writable scratch at a HOST path outside the
execroot: cassian's arms BUILD fixtures under `TMPDIR`, which the chroot pins away; paperkit's
READ a staged corpus, and its cell-venv puts everything inside the execroot by construction —
arrived at only after two other approaches failed on symlink resolution.

⚑⚑ AND CASSIAN FOUND WHAT PAPERKIT'S OWN A/B COULD NOT: writers pattern-cloned to `tier=local`
ESCAPED a sandbox that would have contained them. `local` conflates "reads live host state"
with "needs to write," and a writer wants MORE sandbox, not less. Paperkit never surfaced it
because all its `local` arms are host-probes. **Cassian's tier docstring is now the more
precise one**, and its durable form is: `local` is for arms that read unpinned live host
state; a writer goes to `sandbox` and declares its inputs. Its one genuine escape wrote
THROUGH an input symlink — which defeats every sandbox mode, and the fix is copy-then-mutate
in the arm.

⚑ Substrate's probes hardcode `/tmp` while `TMPDIR` says otherwise — cassian's exact break
class. Default sandbox, which cassian measured as sufficient for containment.

### What cannot become a bazel target, and why a bash hook survives

⚑⚑⚑ BAZEL HAS NO GIT, and an action cannot hand state to a later hook. All three repos keep a
bash hook around a residue for exactly this. The gate partition (`gate-O12`, filed
UNWITNESSED because no mode answers the coupling question and it was read by eye):

- **git-coupled** — the staged-path trigger gates. ⚑ The coupling is the DISPATCH, not the
  body, and that inverts cleanly: bazel selects by dependency, not by a staged-path regex.
  Portable bodies behind a non-portable dispatch.
- **portable as checks** — most of the roster. ⚑⚑ BUT THE RATCHETS LOSE THEIR PAYDOWN-WRITE:
  they mutate a baseline under an env flag, and a hermetic action cannot write back. They
  survive as read-only checks, and **paydown is how a ratchet descends**, so that belongs in
  the residue hook.
- **cross-hook state writers** — the tee re-exec feeding `prepare-commit-msg`, and a catalog
  regeneration that STAGES FILES INTO THE COMMIT, so a commit's final content differs from
  what was staged when the operator typed `git commit`.
- **unclassifiable** — the census syncs EXECUTE a sync then fail if anything changed. ⚑ *An
  action that repairs its own input and then fails on having done so is not expressible.*

### The principle worth more than the migration

linux-sources, after fifteen adversary rounds, unprompted:

> the gate's soundness does not rest on any enumeration being complete — it rests on
> **failing closed**.

Its enumerable side finished at round five. Every hole after that was one species: **a
mechanism keying a PROXY for what the verdict actually reads** — a suffix for "is python", a
token for behaviour, a label for bytes, a closure for the tree it examines.

⚑⚑ SUBSTRATE'S OWN LEDGER HAD ALREADY FILED THAT CLASS FOUR TIMES under different keys, plus
five memories naming it, plus a twelve-row "proxy ledger" that SELF-CORRECTED on the ground
that it presented twelve proxies as twelve lapses when *a proxy that has never diverged from
its witness in production is a working proxy*. So the organizing question is not
subject-versus-proxy — the same token is proxy at one boundary and displaced witness at
another — but **is the proxy's failure mode BOUNDED, and does anything re-gate it?**
Filed as `meta-F15` and `meta-F16`.

## Ⓝ147 ⟡hooks-package — the same arc from the other end

The four adopted hooks are the only cross-repo FILE surface, and the operator's ruling —
`scripts` should not be a package at all, but thin entrypoints calling packages — dissolves
the collision rather than renaming it.

**Preconditions, all measured** (`gate-F38`, `gate-F39`): the family is stdlib-only with zero
substrate imports; `hook_cmdparse`'s consumers are DOTTED so they already resolve for an
adopter; the routing-table path is the single config seam; `hook_pycheck` stays local because
its lint profile is repo-specific by design; all five modules are PROMOTABLE, so the per-file
gate is not an obstacle; and `check_hook_set`'s hook directory now DERIVES from the gate's own
location rather than naming one.

⚑⚑⚑ AND THE HOOK GATE'S GREEN VERDICT ASSERTS THE PRELUDE. Arm 2 requires a hook importing a
sibling to repair `sys.path` — right under the current arrangement, because a hook symlinked
into a repo whose `scripts/` is not a package raises `ModuleNotFoundError` at module load, and
**the harness reads a hook's empty stdout as ALLOW**: the hook denies nothing while reading as
armed. The prelude is an escape hatch for a hazard the symlinking creates. An installed
package breaks the chain and the arm's precondition becomes UNREACHABLE rather than exempted.

⚑ The gate's own docstring already states its limit: it asserts the prelude EXISTS, not that
it is CORRECT, and the arm that would catch a wrong root needs a live fire probe from outside
the repo.

**What blocks the move is a decision, not a measurement** (`gate-F41`): what the package is
called, where it lives, whether it ships with this distribution. ⚑ And the ordering constraint
is hard — an adopting repo recorded that replacing a symlink with a real file **blocked Bash
entirely**, because a configured hook whose file is momentarily absent is a hard error.

## Ⓝ147″ ⟡stale-tokenizer — a live gate hole in three repos

`hook_cmdparse`'s `programs()` skipped a wrapper's flag but never the flag's ARGUMENT, so
`env -C /tmp grep` read the program as `tmp` and every downstream hook saw no `grep`. Fixed
here; summit, cassian and gcalculus all lack the fix, and **their docstrings still name
`timeout -s KILL` as a worked example of the case that fails.**

⚑ All three notified — cassian by live session, summit and gcalculus by inbox letter. Each
letter carries the measurement, the fix, an explicit statement of what was NOT verified (the
drift was proved on `programs()` only; their other hooks differ by more than this accounts
for), and the package context, so nobody reconciles a fork twice.

## Residue — what is recorded and not resolved

- The tool stamp is **premature** until a cached verdict exists to invalidate (`Ⓝ136`).
- The ratchet paydown-write question is undecided and **bounds what fraction of the gate
  surface bazel can hold** (`Ⓝ140′`).
- `gate-O12` is UNWITNESSED: no mode answers "is this gate git-coupled?", and the partition
  above was read by eye (`Ⓝ141′`).
- cassian's `tests/gate-parallel-diff` is the best differential harness seen, and its
  element-wise-not-total refinement is load-bearing — a flip-and-flip-back nets zero on a
  count. ⚑ But both its vectors come from the same bash driver, so it proves serial-vs-parallel,
  NOT bash-vs-bazel. It must not be cited as a bazel differential.
- `◆` is a per-repo commit-prefix CONVENTION, not a shared registry — settled by
  linux-sources. Cassian's gated label registry is a genuine local invention worth copying,
  including its reserved fixture range and its status enum corrected BY DATA.


⚑ **Three bounds travel with these findings, and they are warranted rather than narrated.** A
`traces:` check proves a claim is RECORDED WHERE CITED, never that its mechanism is globally true
[@bnd-said-not-true] — a peer named that as something substrate did better than they did, because a
bound in prose gets summarised away and a bound carrying its own warrant cannot.

⚑⚑ **And the sharper half is that a green needle proves PRESENCE, not CURRENCY**
[@bnd-corpus-moves]. A citation can stay green while the cited thesis has been conceded four
sections below it in the same file — measured, on substrate reading a peer. Only a content stamp
sees the file move, so the needle and the stamp answer different questions and neither covers the
class alone.

⚑ **Nothing here has been built** [@bnd-unbuilt]. There is no workspace, no bazel in the checkout,
and the emitted rule loads a `.bzl` that does not exist — so every claim above is a design question
rather than a measurement, which is also why a peer moving its RBE endpoint costs substrate nothing
to adopt.

### What substrate owes itself, found by turning the peers' tests on this tree

⚑ **Two enumerations of one corpus with no common owner** [@fix-two-enumerations] — git's ignore and
the suite walker's name list — so a repair to one left the other wrong and the suite roster counted
every package module twice against a stale copy. Found by applying a peer's own three-counts framing
here rather than by reading their conclusion.

⚑⚑ **And substrate had already paid for the undeclared-input class before any bazel existed**
[@fix-uv-false-green]: an interpreter mismatch made a type gate's parse find no error lines, and
**zero keys was banked as clean.** The reformulated test is the transferable part — not *does an
action call uv* but *can any path an action takes REACH uv*, and those differ by one fallback.

⚑ **Hand-maintained enumerations are the peers' do-not-adopt item and substrate's defect too**
[@fix-enumerations]. A root makefile spelled its gate roster three times; a mode-coverage reader
carried hardcoded paths inside the module whose docstring condemns hardcoded rosters. Both derive
from one roster now, because a guard over an enumeration reproduces the problem one level up.
