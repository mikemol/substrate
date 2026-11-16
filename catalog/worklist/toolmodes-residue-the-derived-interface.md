# Ⓝ31 residue — the derived interface

**Concern: what a `.pyi` can be COMPUTED from the sources, what only an author can state, and
the stub gates that keep both honest.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **Ⓝ104 ⟡the-pyi-is-a-function-of-the-sources IS THE LOAD-BEARING ENTRY**, and its answer is
*not yet* rather than *no*. The engine bottoms out on stated types, literals, typed surfaces and
body requirements, refuses to write `Any` where it cannot, and reports WHICH WAY it failed — so
the floor is a work queue rather than a verdict. ⚑ Ⓝ104f ⟡witness-provenance is the named
blocker: a slot witnessed only by test fixtures is not computed, and a CONFLICT fires only when
the fixtures happen to disagree.

⚑ **THE RECURRING SHAPE HERE IS A JOIN OVER A POPULATION THE INSTRUMENT NEVER ESTABLISHED IT
HAD** — a foreign witness, a majority vote over understood arms, fixture data entering a
contract, and a false CONFLICT from partial refinement. Four instances, each caught by a
discriminator rather than by review.

⚑⚑ **AND THE GATES ARE TWO DECORRELATED ORACLES, WHICH IS WHY NEITHER RETIRES THE OTHER.**
`stubtest` walks RUNTIME→STUB and structurally cannot see a name the stub invents; `stub_reexport`
is that missing direction, and it found eleven false re-exports across two stubs — one a latent
`ImportError` with a live consumer. Ⓝ94a′ ⟡the-gate-gates-nothing is the counterpart: a census
defect repaired inside a gate that no phase ran.

⚑ Ⓝ129 ⟡inp001-is-a-location retires a premise the whole arc leaned on — the location was never
the wall — and it changes SCOPING rather than only the record: a location wall is binary, a
finding count is rankable.

## Residue

* ⚑⚑⚑ **Ⓝ94a ⟡audit-the-stubs — THE GATE COULD SEE 5 OF 17, AND THE 12 IT COULD NOT SEE ARE THE
  DRIFTED ONES.** `check_stub_authority.stubs()` globbed `stubs/*.pyi` — top-level FILES — so it
  printed **`clean (5 stub(s) match)`** while `stubs/` held five more PACKAGES. Verified by me:
  `find stubs -name '*.pyi'` → **17**, of which 12 live in `networkx/`, `panflute/`, `paperkit/`,
  `psycopg/`. **The green was true and was a fact about the GLOB** — `census-green-is-a-fact-about-
  the-census`, in the gate whose subject is stub authority.

  ⚑⚑ **AND THE CORRELATION IS THE ARGUMENT, NOT THE COUNT.** All five stubs the gate COULD reach
  are honest full-surface ADDITIONS, each carrying its own caught-defect history. Both NARROWINGS
  the audit found — `panflute` (51 stubtest findings) and `networkx` (6) — are in the unseen
  twelve. **Unverifiable is where drift accumulates, because nothing contradicts it.**

  ⚑ **ONE OF THEM IS A LIVE LATENT BREAK, NOT A STRICTNESS COMPLAINT:** `panflute.load` declares
  `source=` where the runtime spells it `input_stream` — *any keyword call breaks*. A stub that has
  drifted is worse than no stub: callers type-check against a fiction.

  ⚑ **FIXED (`rglob` + package-by-directory naming): 5 → 17 seen, and the gate now reports
  BROKEN, 11 of 17.** ⚑⚑ **THE DEBT DID NOT EVAPORATE — it was occluded by buggy tooling**, which
  is the operator's ruling holding on its first test. **But the 11 are not one population**, and
  sorting them (genuine drift · deliberate partiality · unverifiable-on-this-machine) is dispatched:
  a partial stub that NAMES what it declines is legitimate; stubtest's default demands completeness
  and cannot tell the two apart. **Do not make it green — make the verdict mean something.**

* ⚑⚑⚑ **Ⓝ94 ⟡the-psycopg-stub — NOT THE UNTYPED-DEP CASE, AND THE REFUSAL WAS NOT ABOUT ROWS.**
  psycopg ships `py.typed`. Only two expressions refused under `disallow_any_expr`, and the second
  is the instructive one: **`except psycopg.Error` is an `Any` expression because referring to the
  CLASS drags its `*args: Sequence[Any]` constructor along** — nothing to do with row factories.
  *The obvious diagnosis (untyped rows) was wrong about half the population.*

  ⚑ **EVERY GENERIC KEEPS ITS PARAMETER** — the opposite of the networkx retreat. The one
  substitution is `Any` → `object` in a row VALUE: strictly STRONGER, same values admitted,
  unchecked uses refused. What it declines (AsyncConnection, Copy, Pipeline, the adapter layer) is
  **absent, not narrowed**, and said out loud.

  ⚑⚑ **THE LAYOUT IS LOAD-BEARING AND A FLAT STUB SILENTLY FAILED.** A stub resolves BY IMPORT
  PATH: `dict_row` declared only at the root left `from psycopg.rows import dict_row` resolving to
  the LIBRARY, with no error. ⚑ And `connect` had to be written TWICE — as the runtime alias
  `connect = Connection.connect` it leaks the class's `Row` into the free function and every call
  fails.

  ⚑ **AN IRREDUCIBLE 3-FINDING RESIDUE, DOCUMENTED AT THE SITE RATHER THAN NARROWED AWAY.** All
  four spellings of psycopg's pre-PEP-570 dunder positional-onlys were measured; **the ZERO-finding
  option is the one that REFUSES EVERY CALLER.** *Going green there would have been exactly the
  withdrawal-under-correction the operator overturned.* **`substrate/` imports psycopg for the
  first time** (`sandbox_connect.py`, 7/7) — the seam Ⓝ92b named as the hard ordering constraint.

* ⚑⚑⚑ **THE MOST VALUABLE FINDING CAME FROM A SUITE NOBODY ASKED IT TO TOUCH.** Its first cut built
  the index **eagerly in `__init__`**, and `iface_cost --selftest` went **red 4/5** on *"a fully
  annotated module sweeps the corpus ZERO times."* ⚑⚑ **That case was right and the fix was wrong:
  an eager index charges a FULL SWEEP to modules with NOTHING OWED — taxing precisely the annotated
  modules this arc exists to produce.** ***A cost fix that regressed the good case while improving
  the bad one***, caught by a discriminator written for a different purpose. Made lazy; 5/5
  restored, **and `walked` is now OBSERVABLE so the property is checkable in `iface_dataflow`'s own
  suite rather than only through another module's instrument.**

  ⚑ **Two further self-catches, both by discriminators rather than by review:** an index case using
  `from_source` paths **that do not exist on disk** was *green while measuring an EMPTY index* —
  **green for the wrong reason**; rewriting it disk-backed with a three-way arm then exposed that it
  compared **totals** where `sites` always prepends `calls_in(here, …)`.

* ⚑⚑⚑ **Ⓝ104e′ ⟡invert-the-call-index — `agda_lex` WENT FROM EXIT 124 AT 600s TO 10.46s, VERDICTS
  BYTE-IDENTICAL.** The cost law is closed. Verified by me: `check_carrier_locality` **31.3s → 5.17s**,
  and **redundancy 6.0× → 1.0× — 1272 parses over 1272 files, each read EXACTLY ONCE.** *The tool's
  own note now reads as a completion rather than a diagnosis:* **"a walk near 1.0 cannot be made
  faster by caching trees."** ⚑ `CallIndex` is one corpus pass, `name → [(where, Call, Module)]`,
  with **`binds` deliberately NOT folded into the key** — reachability depends on the defining
  module, so it stays at lookup.

  ⚑⚑ **AND THE VERDICTS DID NOT MOVE — `diff` EMPTY ON ALL FOUR MODULES**, re-verified after every
  subsequent change. *`FIXTURE`, union-vs-conflict, `DEFAULTED`/`UNCALLED`/`OMITTED`, coarse
  abstention — every hard-won semantic survived a rewrite of the walk underneath it.*
  ⚑ And the residual memo speedup **fell to 1.3× from the measured 1.7×/2.1×** — *because the index
  already removed the re-parsing the memo was serving.* **The palliative shrank as the fix landed,
  which is what a real fix does to its own workaround.**

* ⚑⚑⚑ **Ⓝ128c ⟡typeengine-false-export — I UNDERSTATED IT 3×, THEN 11×, AND ONE HAD A LIVE
  CONSUMER.** Not one false re-export but **three** in the sqlalchemy stub (`TypeEngine`,
  `ReadOnlyColumnCollection`, `KeyedColumnElement`) — **and that stub's OWN DOCSTRING correctly
  named all three as not-re-exported, THREE LINES ABOVE the block that re-exported them.** *Prose
  and code contradicting each other in one file since its first commit.*

  ⚑⚑ **THE MISSING INSTRUMENT FOUND EIGHT MORE.** `substrate/stub_reexport.py` (`hasattr` on the
  imported module — the EXPORTED-FROM reader nothing owned) immediately surfaced a **sixth
  instance** in `stubs/psycopg`: `ConnDict`, `ConnParam`, `Params`, `Query`, `ConnectionTimeout`,
  `DictRow`, `RowFactory`, `TupleRow`. **Eleven total.** Verified by me: **clean (26 of 26)**.

  ⚑⚑⚑ **AND ONE WAS A LATENT `ImportError` WITH A LIVE CONSUMER.** `substrate/sandbox_connect.py:67`
  wrote `from psycopg import Connection, DictRow` — **`Connection` real, `DictRow` fabricated, in
  ONE statement.** *It never raised only because it sits under `if TYPE_CHECKING:`* — an absent
  failure rather than a nonexistent one. ⚑ Removing the sqlalchemy exports also exposed a
  **second-order consumer**: the postgresql stub imported `TypeEngine` **from `sqlalchemy`,
  resolving only via the false re-export.**

  ⚑⚑ **WHY STUBTEST MISSED IT IS STRUCTURAL, AND PROVED BY POSITIVE CONTROL RATHER THAN INFERRED.**
  ***stubtest walks RUNTIME→STUB***: it enumerates the runtime module's attributes and asks what the
  stub says about each. **A name in the stub but NOT in the runtime is never in the population it
  iterates.** Proof: a fabricated `GhostExport` was added and `check_stub_authority` reported
  **`clean (10 of 10)`**. Confirmed by exhaustion — all 16 findings on a bare run read *"is not
  present in stub"*; **not one reads the converse.** ⚑ `--ignore-missing-stub` is NOT the cause; it
  silences the direction stubtest DOES check. **A blind spot, not a config miss.**

* ⚑⚑⚑ **Ⓝ128d ⟡column-invariance — I WAS WRONG IN THE DIRECTION THAT WOULD HAVE CAUSED DAMAGE.**
  `sqlalchemy/sql/type_api.py:62` declares `_T = TypeVar("_T", bound=Any)` **and line 63 declares
  `_T_co` COVARIANT immediately beside it.** `TypeEngine` and `Column` both take the **invariant**
  one. ***Upstream has the covariant TypeVar in hand and deliberately does not use it.*** **So our
  stub transcribed the library CORRECTLY, and widening it would be a FORK, not a repair** — typing
  call sites the library itself refuses.

  ⚑ **AND THE WORKAROUND WAS ALREADY EXPLAINED — its explanation was just WRONG ON ITS KEY CLAIM**,
  calling it *"a fact about the STUB's precision, not about the library"*: **the exact inversion,
  and the thing that invited the bad repair I was about to authorise.** Corrected with source
  citations; the local subclass is now documented as **THE honest pattern**, not a workaround
  awaiting removal.

* ⚑⚑ **Ⓝ124a ⟡dep-gate-ignores-its-operand — REFUSING WOULD HAVE BEEN WRONG, AND THE SHAPE IS
  `rewire_only`.** `requirements(manifest)` and `declared(manifest)` were **already parameterised,
  each with a docstring ARGUING FOR the parameter**; only `main` called them bare. ***Nothing was
  missing but the wire.*** **Refusing would have frozen a reader that already answers about ANY
  manifest into answering about one.** ⚑ `check_argv` — the authority — *sat unused two imports
  away.* The gate now **prints which manifest it read**: *the drop survived precisely because the
  output was byte-identical either way.*

  ⚑ Suite 18 → **23/23**, and the regression pin goes **through `main(argv)` asserting an exit
  code** — *every prior case called the reader directly, which is WHY the defect shipped past a
  green suite* — using a fixture **not named `pyproject.toml`** so a future filename-guessing `main`
  cannot pass it. Positive-controlled by injecting the regression.

* ⚑⚑⚑ **Ⓝ94a′ ⟡the-gate-gates-nothing — THE CENSUS DEFECT I FIXED WAS IN A GATE NOTHING RUNS.**
  `scripts/check_stub_authority.py` says **"Blocking gate"** in its own docstring and appears in
  NEITHER `build_census.py --gates` NOR `gate_census.py --successors`. Verified by me:
  `--successors` lists **35 gate scripts** and it is not one of them. *So every verdict it has
  ever produced — including this morning's `clean (5 stub(s) match)` — was advisory to whoever
  ran it by hand.* ⚑⚑ **A green census inside a gate that gates nothing is two layers of
  nothing**, and the widening only made the unenforced verdict honest. **Wiring it is a policy
  act with a firing gate attached and was deliberately NOT done unasked.**

  ⚑ Also removed: `--check` sat in `_FLAGS` with no branch — **accepted and silently a no-op**,
  the flag-shaped instance of the same class.

* ⚑⚑⚑ **CORRECTION TO MY OWN RECORD ABOVE, ON TWO COUNTS — AND THE SECOND IS THE ONE THAT
  MATTERS.** The entry a few bullets up reads *"both NARROWINGS — `panflute` (51 stubtest
  findings) and `networkx` (6)"*. **`networkx` has ZERO drift.** All 6 of its findings are
  DECLINED OPTIONAL PARAMETERS (`**attr` dicts, `backend=` dispatch); its 3668-line report
  collapses to those 6 under relief, and **not one is a contradiction.** Of `panflute`'s 51,
  exactly **2** were drift. *I wrote a finding count down as a drift count* — the same
  ⟡count-is-a-query-fact shape the sql skill records five instances of, committed while
  recording someone else's instance of it.

  ⚑⚑ **AND "11 of 17" USED TWO WRONG DENOMINATORS.** 17 counts FILES; the population is **9
  STUBS**. `stubtest` on a package ALREADY RECURSES — running `paperkit` reports *"checked 3
  modules"* — so my per-submodule enumeration re-ran the same work and reported one root cause
  as two failures. **The dedup instinct was right and the mechanism was broader than
  duplication.** Files and stubs are different denominators; the gate now says which it quotes.

* ⚑⚑ **THE DRIFT WAS ONE STUB, AND ONLY POSITIONAL CALLS HID IT.** `panflute.load` declared
  `source` where the runtime spells `input_stream` (`panflute/io.py:28`). Both call sites
  (`substrate/md_ast.py:50`, `scratch/mdstruct.py:665`) pass POSITIONALLY, *which is the only
  reason it had not fired*. ⚑ Repaired to the runtime's own default (`IO[str] | None = None`),
  **not the required arg the stub had invented** — a second fiction in the repair would have
  been the first defect again.

* ⚑⚑⚑ **THE VERDICT IS THREE-VALUED NOW, BECAUSE COLLAPSING IT WAS THE BUG.** `not verified` is
  not `verified broken`: `paperkit.bib` needs `bibparse`, absent on this machine, which is a
  fact about THE MACHINE. **Rendering it identically to a contradicted signature is
  `report-presence-never-absence` at gate granularity.** UNVERIFIABLE is reported and does NOT
  fail; DRIFT fails. Verdict `BROKEN — 11 of 17` → **`clean (8 of 9)`**, every exemption printed
  beside its result.

  ⚑ **RELIEF IS ENUMERABLE AND CANNOT OUTLIVE ITS CAUSE.** `--allowlist` with individually named
  entries, and `--ignore-unused-allowlist` deliberately NOT passed — **so an exemption that stops
  matching becomes a finding.** ⚑⚑ `--ignore-positional-only` was REFUSED though it makes
  psycopg green in one word (measured: `Success: no issues found in 83 modules`): *it is a
  blanket suppression of a finding CLASS across all 83, including contradictions nobody has
  looked at.* **A positive control proves the relief cannot hide drift** — a renamed `load`
  parameter reintroduced with all 14 panflute exemptions active was still caught.

  ⚑ **AND THE `rows.pyi` RESIDUE WAS RE-MEASURED RATHER THAN TRUSTED.** Applying the
  zero-finding spelling (dropping `/`) produced **3 errors** in `sandbox_connect.py`, including
  the row type collapsing to `Any` — *the exact `Any` the stub exists to remove.* The prior
  agent's measurement holds; restored, with the re-measurement recorded in the file.

* ⚑ **Ⓝ94a″ ⟡wire-the-stub-gate — the named next cut.** A gate declaring itself blocking, that
  no phase runs, is a promise with no mechanism. ⚑ It should land only once the three-valued
  verdict is trusted, since wiring it makes UNVERIFIABLE-on-a-fresh-checkout a real question:
  `paperkit` cannot be verified without `bibparse`, and a gate that fails there fails a clean
  checkout — the `selftest_mk` shape (Ⓝ95) exactly.


* ⚑⚑⚑ **Ⓝ100a ⟡declines-by-ast — TWO AGENTS ON ONE FILE UNDER A ONE-WRITE RULE, AND IT CAME
  WITHIN ONE READ OF A SILENT REVERT. THE DISPATCH ERROR WAS MINE.** I fenced the agent off
  `check_stub_authority.py` and then asked it for a deliverable that lives IN that file. The
  other agent rewrote the file AFTER its first read; a multi-hunk edit composed from that read
  would have **silently reverted their work**, which is precisely what the fence existed to
  prevent. ⚑⚑ **It was caught only because LINE NUMBERS SHIFTED between two Reads** — not by any
  mechanism. **There is no locking**; the agent waited ~20 minutes of confirmed mtime stability
  before writing. *A convention with no enforcement held because someone happened to look twice.*

  ⚑ **AND THE DELIVERABLE WAS ALREADY BUILT WHEN IT ARRIVED** — `stub_sources()`,
  `declared_surface()`, `declared_signatures()` already union across every `.pyi` in a package.
  My brief described built work as work to do. **It verified rather than rebuilt**, which is the
  only reason there is one implementation and not two.

* ⚑⚑⚑ **AN UNPARSEABLE `.pyi` READ AS ZERO DECLINES, AND I CONFIRMED THE FIX BY POSITIVE
  CONTROL.** I dropped a deliberately-broken `_probe_broken.pyi` into `stubs/psycopg` and ran the
  gate: **exit 1, naming the file and the line**, with the reason stated —
  *"a `.pyi` IS a Python file, and one that cannot be read declares NOTHING — which is
  indistinguishable from declining nothing, so every exemption in it is silently withdrawn and
  its findings resurface as drift in the MODULE."* On the PRE-change code the same file produced
  **nothing, in neither `--list` nor the verdict, exit 0.** ⚑ Probe removed; verdict re-verified
  clean. **The failure mode was not merely a missing error — it INVERTED the artifact's meaning**,
  turning a stub's every exemption into drift without saying so.

  ⚑ The suite's discriminator is the complementary arm (the live tree has zero unreadable stubs),
  *so a predicate that flagged everything would fail* — the case that makes the green mean
  something.

* ⚑⚑ **`ast`, NOT REGEX — AND THE MARKERS SPLIT BY SCOPE, WHICH IS THE ANSWER TO WHETHER A
  MEMBER MAY DECLARE.** `read_source()` parses the module and walks `ClassDef`/`FunctionDef`/
  `AsyncFunctionDef` for member docstrings. The asymmetry is load-bearing and was BUILT that way:

      ⟡declines-signature:   names a DOTTED PATH to one member  → its home is that member
      ⟡declines:             grants --ignore-missing-stub over the WHOLE UNIT
                             → a single class must NOT be able to widen a package's surface

  ⚑ **THE EVIDENCE WAS ALREADY IN THE TREE:** `stubs/psycopg/rows.pyi` carries three
  `⟡declines-signature:` entries beside ~40 lines of measured rationale for the three protocols
  they excuse — *already file-local before anyone asked whether it should be.*

  ⚑ **VERIFIED BY THE DISCRIMINATING TEST, not by adding a new declaration:** moving
  `psycopg.rows.RowMaker.__call__` OUT of the module docstring and INTO the `class RowMaker`
  docstring left the verdict **byte-identical** (`clean (8 of 9)`, all three psycopg entries
  present; only list order moved, set semantics). *A test that only ADDED a declaration would
  have passed on a build where the root was still the only file read.*

* ⚑ **PROVENANCE IS HALF-DONE, AND THE HALF THAT IS MISSING IS THE SUCCESSFUL HALF.**
  `Unreadable` names its declaring file; the printed `declines:` / `signature exemptions:` lines
  still name the UNIT, not which `.pyi` each declaration came from. **Ⓝ100b ⟡stub-declaring-file**
  — carry the `Path` alongside each collected declaration and print `(from rows.pyi)` beside each
  entry. Left undone deliberately: it means restructuring a render the other agent had just
  written, and the output is correct today.

  ⚑ Selftests: `stub_declines` **12 → 21**, `check_stub_authority` **12 → 13**. ⚑ The first write
  was refused on three `FBT003` (bare `True` positional); replaced with `UNREADABLE`/`PARSED`
  state words rather than seeking relief — **the gate improved the cases it refused.**


* ⚑⚑⚑ **Ⓝ103 ⟡infer-the-interface — THE REUSE-SEARCH DELETED THE BUILD, WHICH IS THE OUTCOME THE
  RULE EXISTS FOR.** `stubgen` ships WITH mypy (already a declared dependency) and does ALL of
  reader 1's generation. Verified by RUNNING it: `--no-import` parses without executing, emits
  `Stmt(NamedTuple)` with its `Literal[…]` field and the `match = search` alias correctly, and is
  **byte-stable** (two runs, `cmp` silent) — so it is gateable for drift. **No generator was
  built.** ⚑ `--include-docstrings` carries the ⚑ commentary through, which in this tree is the
  more valuable half.

* ⚑⚑⚑ **AND THE DEPENDENCY RUNS THE OPPOSITE WAY FROM HOW I DISPATCHED IT: READER 1 CANNOT RUN,
  AND READER 3 IS ITS SCHEDULER.** Verified by me — `iface_readers --eligible`:

      0 of 5 repo-local stub(s) can be GENERATED today
        agda_lex 8/80 · tsdbprobe 37/55 · gen_build_makefiles 0/15
        check_carrier_locality 0/13 · check_scratch_independence 0/5

  **`stubgen` emits `Incomplete` for every unannotated slot, and under `disallow_any_expr`
  `Incomplete` IS `Any`.** So regenerating `check_carrier_locality.pyi` today would replace the
  authored `Iterable[str] | None` with `paths=None` — **DELETING working type information** — and
  be refused by the gate that admits `substrate/`. ⚑⚑ *I dispatched the three readers as
  parallel deliverables; they are a chain.* **Annotate the module, then the stub generates
  itself.** The report names each owed site with a line number, so the floor is a WORK QUEUE, not
  a verdict.

* ⚑⚑⚑ **I WAS WRONG THAT ALL THREE THIRD-PARTY STUBS ARE NARROWINGS OVER A TYPED SURFACE — ONLY
  `psycopg` SHIPS `py.typed`.** `networkx` and `panflute` do not, so they are stubs over UNTYPED
  deps — **the category this repo's own rule says legitimately ADDS types.** *Same error as
  calling networkx's 6 declined parameters "drift": I generalized from the one case I had read.*
  ⚑ Measured deltas against the real installed upstreams (declared / upstream):

      psycopg.rows        5 / 20     (Row, DictRow, class_row, scalar_row, all async unreachable)
      psycopg.connection  1 / 7
      psycopg.cursor      1 / 2
      panflute (io)       1 / 6      (dump, run_filter, toJSONFilter…)

  ⚑ **A NEGATIVE RESULT RECORDED AS A FACT ABOUT THE METHOD:** `--narrowing` against networkx's
  `__init__.py` returned a useless 3 names, because that file is **pure re-export machinery**. The
  delta for a lazily-re-exporting package needs the SUBMODULE TREE, which this cut does not walk.
  **Ⓝ103a ⟡narrowing-submodules.**

* ⚑⚑ **THE UNDER-ANNOTATION CENSUS, AND ITS POSITIVE CONTROL IS THE FINDING.** Verified by me:
  **615 of 1226 modules owe slots — and `substrate/` owes 0 of 352.** *The instrument
  discriminates populations rather than reporting "unannotated" at everything*, and the zero is
  what the per-file gate has been buying all along, measured for the first time. ⚑ Ranked by
  **SLOTS OWED, not ratio** — a 50%-annotated 2-slot module and an 80-slot one are the same ratio
  and vastly different work.

* ⚑⚑⚑ **INFERENCE'S FLOOR, AND THE REFUSAL THAT DEFINES IT.** *Inference propagates the types a
  source STATES; it does not manufacture types the source never stated.* An unannotated parameter
  is `Incomplete` in the derived stub, so **a derived stub is exactly as strong as its module's
  annotations and no stronger.** ⚑⚑ **mypy's BODY-inference was deliberately NOT used to fill the
  gaps** — *a body-inferred return is a fact about today's IMPLEMENTATION, not a declared
  CONTRACT, and promoting one into a published interface would manufacture exactly the claim this
  engine exists to stop manufacturing.* ⚑ The floor is **itemized, not scalar** (`Interface.hollow`
  returns symbols with line numbers), which is what makes it a queue rather than an excuse.

* ⚑ **LANDED:** `substrate/iface_infer.py` (15/15) — the engine, symbol-level, annotations as
  written via `ast`; `substrate/iface_readers.py` (5/5) — `--eligible` / `--narrowing` /
  `--census`. Discovery is automatic (318 suites), so no roster edit. Scope fence held: the two
  files under contention were untouched.

  ⚑ **Ⓝ103b ⟡iface-gate — NAMED, NOT WIRED, AND CORRECTLY SO.** With 0 of 5 eligible it would
  fire on everything today. ⚑ And `stubs/`' flat layout is keyed on BARE MODULE NAMES while
  `stubgen` mirrors SOURCE DIRS (`scripts/…`), so generation needs `-o` per module rather than a
  bulk run — a layout mismatch that would have surfaced as mysterious misplacement.


* ⚑⚑⚑ **Ⓝ104 ⟡the-pyi-is-a-function-of-the-sources — COMPUTED AND AUTHORED AGREE, AND THE
  AGREEMENT VERIFIES A CLAIM `stubtest` CANNOT REACH.** The operator's framing retired the write:
  *"You don't have to write into anything; you can recursively read and import the sources into
  ast or cst and find out what a .pyi file would NEED TO BE. Something will bottom out somewhere,
  eventually."* On the worked case (`check_scratch_independence`), every computed parameter type
  matches the hand-authored stub — and **that stub's own docstring flags those types as *"a
  READING of the implementation, not a transcription"*, which `stubtest` is structurally unable
  to check.** *The corpus now verifies both, with file:line evidence.* That is the arc's result.

  ⚑ **VERIFIED BY ME, AND THE LIVE NUMBER IS NARROWER THAN THE REPORT: 4 of 5 computed, 1 did NOT
  bottom out** (`main#<return>` — 2 of 6 return arms unresolved). *The report said 5 of 5; the
  second soundness fix below is why running it says 4.* **The narrower answer is the trustworthy
  one.**

* ⚑⚑⚑ **TWO SOUNDNESS BUGS IN THE READER ITSELF, BOTH CAUGHT BY RUNNING IT, AND BOTH PRODUCE A
  WELL-FORMED ANSWER WITH EVIDENCE ATTACHED.** Neither looks like a failure — which is the whole
  danger:

  * **A FOREIGN WITNESS.** `pycodemod --calls scan` reports **3 defs / 35 calls**; the first cut
    credited every call to whichever def it was resolving, so `check_carrier_locality.scan#paths`
    came back witnessed by `_pycodemod_placement.py` — *a module calling a DIFFERENT `scan`.* **A
    confident wrong type carrying a `file:line` that reads as proof.** `census-keyed-on-one-
    spelling`, now producing a positive claim rather than a false zero. Fixed with a `binds`
    predicate (defining module, or one importing it) — conservative, so it UNDER-reports.
  * **A MAJORITY VOTE OVER THE ARMS IT UNDERSTOOD.** `carrier_of` returns `parts[0].split()[0]`
    **or `None`**. Filtering the unresolved arm away left unanimous survivors and reported a
    confident **`NoneType`** — **inverting the truth, since `None` is the FALLBACK.** *The module
    refuses to pick among disagreeing witnesses everywhere else and was silently picking here.*
    A partially-resolved return is now UNRESOLVED, and `.computed` is gated on status so a reader
    cannot be handed a fragment.

  ⚑⚑ **THEY ARE ONE FAILURE IN TWO CLOTHES: A JOIN OVER A POPULATION THE INSTRUMENT DID NOT
  ESTABLISH IT HAD.** One joined over the wrong callers, the other over the wrong arms.

* ⚑⚑⚑ **MY STATED FLOOR WAS WRONG, AND MORE SPECIFICALLY THAN "INPUTS VS OUTPUTS".** I recorded
  *"inference does not MANUFACTURE types the source never stated."* The live counterexample is
  `promotion_report#candidate` → **`str` from the BODY ALONE**, no call site needed (`:76` passes
  it to `join()`). **So the floor fails for ANY slot constrained by USE** — the real distinction
  is **STATED vs DETERMINED**, and determination has two independent directions.

  ⚑ **BUT THE ASYMMETRY SURVIVES, SHARPENED:** a computed RETURN is a fact about today's body; a
  computed PARAMETER is a fact about the contract **every caller must meet**. Both are reported
  and `Witness.kind` carries the difference — *so a reader weighs them rather than the tool
  weighing them for it.*

  ⚑⚑ **AND ONE CORRECTION AGAINST THE OPERATOR'S FRAMING, MEASURED RATHER THAN ARGUED:** *"if
  everything were `Any`, mypy would tell you what it ought to be"* — **it does not.** Run on the
  worked case, `--disallow-any-expr` emits 227 findings, all *"Expression has type Any"* / *"Call
  to untyped function"*: a **FORWARD propagation trace** naming where `Any` ARRIVED. It never runs
  the reverse direction, *because a checker types `scan_file(p)` by reading the parameter's
  declaration — with none it writes `Any` and never asks what `p` WAS.* The information is in the
  corpus; **mypy is not its reader.** Kept as `--sites` (still the best answer to *which sites are
  poisoned*), but it is not the engine.

* ⚑⚑ **THE BOTTOMING-OUT SET, AND THE TWO DIRECTIONS ARE NOT AVERAGED.** B1 literals
  (grammar-given) · B2 already-annotated slots · B3 typed surfaces (typeshed-given) · B4 body
  requirements, in two arms — receiver position (`p.endswith(…)`) and argument position
  (`join(root, p)`). **B1/B3 are FORWARD (a value of this type arrives); B4 is BACKWARD (whatever
  arrives must support this).** They are separate evidence and **may disagree — reported as
  `CONFLICT`, never averaged.** ⚑ Cycles: an in-progress set keyed by slot, re-entry returns
  `CYCLE` naming the loop; memoised to one visit per slot. **A slot that does not bottom out is
  NEVER filled with `Any`** — it is reported with WHICH way it failed.

  ⚑ **THE DISAGREEMENT WAS THE MOST VALUABLE PART, AND IT WAS A GAP IN THE BOTTOM, NOT THE STUB.**
  `promotion_report#candidate` first came back UNRESOLVED against the stub's `str`. **The stub was
  right**: B4 read only *method calls on* a parameter, never a parameter *passed as an argument*.
  *Which is exactly why comparing against a hand-authored artifact was worth running.*

* ⚑⚑⚑ **THE REPO-LOCAL / THIRD-PARTY SPLIT DISSOLVES MECHANICALLY AND SURVIVES AS REACHABILITY.**
  `psycopg` (typed): **6/6 all STATED** — bottoms out instantly on B2, *the recursion never
  starts*. `panflute` (untyped): **6 of 40**, and it bottoms out **in the library's own source
  exactly as repo-local code does** — same machinery, same witness kinds. **So the discriminator
  is not repo-local-vs-third-party but ANNOTATED-vs-NOT**, which retires a distinction I built
  two dispatches around.

  ⚑⚑ **WHAT DOES NOT DISSOLVE, AND IT IS A LIVE AMBIGUITY IN THE OUTPUT:** panflute's public
  entry points report *"no call site passes this parameter"* because their callers are OUTSIDE the
  corpus (pandoc filters). **For repo-local code that verdict means DEAD; for a library it means
  the callers are not in scope. One output string, two different facts** — and the reader cannot
  currently tell them apart. **Ⓝ104a ⟡reach-vs-dead.**

* ⚑ **LANDED:** `substrate/iface_bottom.py` (13/13) — the bottoming-out set isolated so the
  termination argument is ONE readable file, *deliberately unable to recurse*; and
  `substrate/iface_dataflow.py` (14/14) — `--module` / `--slot` / `--sites`. **Reuse deleted the
  call-graph builder** (`pycodemod --calls` already indexes corpus-wide) and the second AST walk
  (`iface_infer` is called, not reimplemented). No module annotation, no `stubs/` file, and
  neither contended gate file was touched.

  ⚑ **Residue:** **Ⓝ104b ⟡bottom-widen** (subscript-of-comprehension — the `args[0]` shape that
  first blocked `candidate`) · **Ⓝ104c ⟡return-shape** (`tuple[Any, ...]` is honest but coarser
  than the authored stub; element types ARE computable from the tuple's element expressions).


* ⚑⚑⚑ **Ⓝ104d ⟡compute-the-authored-five — RUN BY ME AGAINST FOUR OF THE FIVE, AND EVERY
  DISAGREEMENT IS A GAP IN THE READER, NOT A DEFECT IN A STUB.** (`agda_lex`, 80 slots, exceeded
  120s and is still running — the fifth is UNMEASURED, not clean.)

      check_scratch_independence   4 of 5   0 conflicting   1 unresolved
      check_carrier_locality       4 of 13  0 conflicting   9 unresolved
      gen_build_makefiles          4 of 15  0 conflicting  11 unresolved
      tsdbprobe                   41 of 55  1 CONFLICTING  13 unresolved

  ⚑ **`tsdbprobe`'s 41 is mostly `STATED`, not computed** — it is the annotated module, so the
  recursion bottoms out on B2 immediately. **The computed-vs-stated split is the honest reading of
  that number**, and it confirms the psycopg finding at repo-local scale: *annotated-vs-not is the
  discriminator.*

* ⚑⚑⚑ **THE SOUNDNESS FIX IS VERIFIED ON THE EXACT CASE THAT PRODUCED THE BUG.**
  `check_carrier_locality.carrier_of#<return>` now reads **UNRESOLVED (1 of 2 arms)** where the
  first cut reported a confident **`NoneType`**. The authored stub says `str | None`. *So the
  reader's refusal to join over the arms it understood is what stands between it and an inverted
  answer, and the stub is the witness that the refusal is correct.* ⚑ `scan#paths` — the slot that
  carried the FOREIGN WITNESS — now reads DEAD rather than falsely witnessed.

* ⚑⚑⚑ **THE ONE DISAGREEMENT WITH AN AUTHORED STUB IS A MISSING BOTTOMING-OUT SOURCE: A DEFAULT
  VALUE.** `scan#paths` reads *"no call site passes this parameter — the slot is DEAD"*, while the
  stub states `Iterable[str] | None = ...`. **Both are correct about what they looked at**:
  `scan()` is called with no argument, so no call site passes it, **and the DEFAULT is the only
  evidence there is.** ⚑⚑ *A default is a type witness the source states outright* — it is B1/B2
  territory, not an inference — **and the bottoming-out set does not read it.** That is
  **Ⓝ104b ⟡bottom-widen**, not Ⓝ104a: the slot is not ambiguously-reachable, it is determined by
  evidence the reader declines to look at.

* ⚑⚑ **AND A NO-VALUE RETURN IS `None`, WHICH IS DETERMINED — YET IS FILED AS A FAILURE.**
  `gen_build_makefiles.kahn_check#<return>` and `main#<return>` report *"no return statement with
  a value."* **That is not unresolved; it is the STRONGEST bottoming-out case there is.** ⚑ The
  authored stub states `main() -> int` for the sibling module, and
  `check_scratch_independence.main#<return>` computed `int` from four literal returns — *so the
  three `main`s differ genuinely, and only one of the three should read UNRESOLVED.* Filed with
  **Ⓝ104c ⟡return-shape**.

* ⚑⚑⚑ **THE FIRST `CONFLICT` IS DIAGNOSTIC, AND IT IS A POPULATION QUESTION AGAIN.**
  `tsdbprobe.extract_values#body -> dict[Any, Any] | list[Any] | str` — the `dict` and `list`
  witnesses come from **SELFTEST FIXTURES** (`:819`, `:822`, `:846`), the `str` from real callers.
  **Test data is entering the type as though it were production evidence.** ⚑⚑ *This is the third
  instance today of a join over a population the instrument never established it had* — after the
  foreign witness (35 calls, 3 different `scan`s) and the majority vote over resolved arms — and
  **the CONFLICT verdict is what kept it visible instead of averaging it into a union nobody would
  question.** A witness's PROVENANCE (production call vs fixture) is a distinction the reader does
  not carry.

* ⚑ **`tsdbprobe.main#argv` READS DEAD IN A MODULE INVOKED AS `main(sys.argv[1:])`.** Dynamic
  entry, not death — **Ⓝ104a ⟡reach-vs-dead from the third direction**, after panflute's
  out-of-corpus callers. *One verdict string, now three distinct facts.*


* ⚑⚑⚑ **Ⓝ104d, THE FIFTH MODULE — `agda_lex` TERMINATES (exit 0, >120s) AND COMPUTES 40 OF 80.**
  I had recorded it UNMEASURED after a timeout; it finished in the background. **Half the surface,
  on the module `iface_readers --census` rates 8/80 annotated — so the corpus DETERMINES five
  times what the source STATES.** *That is the arc's strongest single result*, and it is the
  number that makes the operator's framing concrete rather than plausible: the interface is in the
  sources, and reading them recursively finds it.

  ⚑ **AND THE COST IS REAL:** `agda_files#root` draws six witnesses across five files. **The
  runtime is the price of corpus-wide recursion**, not a defect — but it means a per-module reader
  is not yet a gate-speed instrument. **Ⓝ104e ⟡dataflow-cost.**

* ⚑⚑⚑ **AND IT EXPOSES THE FIXTURE-PROVENANCE DEFECT IN ITS WORST FORM — AS A CONFIDENT
  `COMPUTED`, NOT A `CONFLICT`.** In `tsdbprobe.extract_values#body` the fixture witnesses
  DISAGREED with the production ones, so the reader raised CONFLICT and stayed honest. Here they
  do not disagree, so nothing fires:

      COMPUTED  agda_lex.agda_files#include_build -> bool
            [literal] tests/test_agda_lex_paths.py:163  True        ← ONE witness, a TEST
      COMPUTED  agda_lex.binds_at#tok -> str
            [literal] scratch/agda_lex.py:1441  '_+_'  · :1444 'nope' · :1450 'q'   ← ALL selftest
      COMPUTED  agda_lex.binds_at#lineno -> int
            [literal] :1441 1 · :1443 5 · :1444 5 · :1450 5                          ← ALL selftest

  **A `bool` inferred from a single `True` in a test file is not a contract — it is the shape that
  one fixture happened to pass.** ⚑⚑ *The types here are probably RIGHT; the EVIDENCE is not the
  kind claimed*, and nothing in the output separates *"six production call sites agree"* from
  *"one test passed a literal."* **A CONFLICT is the lucky case: it fires only when the fixtures
  disagree.** Where fixture and production agree — or where fixtures are the ONLY witness — the
  defect is invisible and the answer looks strongest.

  ⚑ **FOURTH INSTANCE TODAY OF A JOIN OVER A POPULATION THE INSTRUMENT NEVER ESTABLISHED IT HAD**
  (after the foreign witness, the majority-vote-over-understood-arms, and the tsdbprobe CONFLICT)
  — **and the first where the bad population produces no visible symptom at all.**
  **Ⓝ104f ⟡witness-provenance: a witness must carry WHERE IT CAME FROM** (production call · test
  fixture · the defining module's own selftest), and a slot witnessed only by fixtures is not
  COMPUTED. *That is the same distinction as `report-presence-never-absence` and as the stub
  gate's three-valued verdict: the verdict must name what kind of thing it looked at.*


* ⚑⚑⚑ **Ⓝ104 ⟡the-pyi-is-a-function-of-the-sources — THE ANSWER IS "NOT YET", AND MY
  RECOMMENDATION TO RETIRE Ⓝ103c WAS EXACTLY BACKWARDS.** I proposed that computing types from the
  corpus makes annotating-to-satisfy-`stubgen` unnecessary work. **The opposite is true, and the
  mechanism is the part I had not seen: AN ANNOTATED SLOT IS B2 — A BOTTOMING-OUT CASE.** Every
  annotation added is a new TERMINATION POINT that collapses downstream
  *"every incoming argument is itself unresolved"* cascades (7 of them across the four measured
  modules). ⚑⚑ **`tsdbprobe` is simultaneously the MOST-ANNOTATED module and the one with the MOST
  computed slots** — *annotation FEEDS the engine rather than competing with it.* **I had them as
  substitutes; they are the same work from opposite ends.** ⟡annotate-to-generate stands.

* ⚑⚑⚑ **AND THE HEADLINE COUNT WAS INFLATED BY A DISTINCTION I SKIPPED. `tsdbprobe`'s 41 IS
  31 `STATED` + 10 COMPUTED.** I recorded it as *"mostly already-annotated"* and moved on;
  `STATED` is the tool reading back an annotation **`stubgen` also gets for free**, so the engine's
  MARGINAL contribution there is **10/55 ≈ 18%, not 75%**. Aggregated across the four measured
  modules: **22 of 88 slots ≈ 25%.** ⚑ *That 25% is the honest ceiling on what a derived stub could
  supply today* — and the 65 unresolved slots are **not filler-able**, because the engine refuses
  to write `Any` there. **The refusal is why the 25% is trustworthy.**

* ⚑⚑⚑ **THREE THINGS AN AUTHORED STUB CARRIES THAT NO COMPUTATION CAN — AND THE FIRST WOULD MAKE
  A GENERATOR *MORE* WRONG, NOT LESS.**

  * **DELIBERATE WEAKENINGS.** `DECL: object` (check_carrier_locality) and `IMPRE: object`
    (gen_build_makefiles) are `re.Pattern[str]` at runtime. **A computation reading the source
    would compute the STRONGER type and be more wrong** — the stub's own rationale is *"a stub
    that promised a richer type would be asserting a property no one verified."* **A generator has
    no input for *I know the true type and am declining to state it*.**
  * **DELIBERATE VALUE-OMISSIONS.** `MEM_CAP: str` / `AGDA_JOBS: str` declared with **no value**,
    explicitly so the stub does not become *"the fifth site to hold a stale copy"* of a build
    figure — **CLAUDE.md's cite-don't-restate law encoded IN a stub.**
  * **DECLINES MARKERS** — scope decisions about what THIS REPO calls, unknowable from the stubbed
    library's source.

  ⚑⚑ **SO THE SPLIT IS PER-SLOT WITH AN AUTHORED OVERRIDE, NOT FILE-LEVEL** — and **the
  machine-readable half ALREADY EXISTS AND ALREADY WORKS** (the gate parses declines out of the
  docstring). *More built than my framing assumed.* The shape is a generator emitting computed
  slots with witnesses plus an authored sidecar for weakenings / omissions / declines, **refusing
  to overwrite an overridden slot.**

* ⚑⚑⚑ **`stubtest` DOES NOT DISAPPEAR, AND THE UNVERIFIABLE CASE IS THE PROOF.** They are
  DECORRELATED oracles: `iface_dataflow` reads SOURCE and **cannot import**, so it would have an
  answer for `paperkit` where stubtest returns NOT VERIFIED; `stubtest` **imports the RUNTIME** and
  therefore sees `AGDA_JOBS: Literal['20']` — *a fact no source read produces, and the one that
  caught a first draft guessing `int` from the NAME.* ⚑⚑ **So the gate does not become a drift gate
  REPLACING stubtest — it becomes a TWO-ORACLE AGREEMENT GATE** (computed · authored · runtime).
  **That is where the `Flat.mk` analogy breaks: `Flat.mk` has ONE oracle; this has two, decorrelated
  in exactly the way `correlated-instruments-agreeing-is-not-coverage` asks for**, and collapsing
  to one discards the disagreement that already found a bug.

* ⚑⚑ **FIVE PRECONDITIONS BEFORE A DERIVED STUB SHIPS UNREVIEWED. NONE IS SATISFIED TODAY.**
  (1) **witness-provenance stratification** — a call site inside a selftest / `__main__` block /
  test file is not production evidence; **without it every module with an inline selftest is
  poisoned**; (2) **CONFLICT must BLOCK, not report** — same argument as UNRESOLVED-is-not-`Any`;
  (3) **the foreign-witness class needs a GATE, not a fix** — a negative fixture set reproducing
  both prior wrong answers; (4) two-oracle agreement; (5) **a termination bound.**
  ⚑ `--sites` shows the ambient noise: **126 `Any` expressions on a 13-slot module**, of which the
  engine resolves 4.

* ⚑⚑⚑ **AND THE THIRD AGENT INDEPENDENTLY REDISCOVERED THE FIXTURE DEFECT FROM THE OTHER SIDE.**
  It read `tsdbprobe.extract_values#body`'s witnesses at `:819/:821/:822/:846` as **the module's own
  SELFTEST**, concluding the true type is `str` and a derived stub would ship `dict | list | str`
  to every consumer. *Two agents, two modules, one defect* — **Ⓝ104f ⟡witness-provenance is now
  corroborated rather than suspected**, and it is the named blocker on the whole design question.

* ⚑⚑ **ONE OPEN DISAGREEMENT, MINE vs THEIRS, ON THE SAME COMMAND.** My background run of
  `--module scratch/agda_lex.py` **completed, exit 0, 40 of 80.** Theirs, given **600s (5×), exited
  124 with no output.** Same module, same tool. ⚑ Candidate causes, none established: nondeterminism;
  CONTENTION (two agents were editing `iface_dataflow.py` during their run); or a genuine cost
  straddling the boundary. **Re-running under an explicit bound.** *"It depends on what else is
  running" would itself be a finding for a gate* — **Ⓝ104e ⟡dataflow-cost**.


* ⚑⚑⚑ **CORRECTION — `agda_lex` 40 of 80 IS PROVISIONAL AND THE DISAGREEMENT RESOLVED AGAINST
  ME.** I reported it as the arc's strongest result (*"the corpus determines five times what the
  source states"*) on a background run that exited 0. **Re-run under an explicit 600s bound: exit
  124, no output** — matching the Ⓝ104 agent's independent 600s failure. **Two failures against my
  one success, so MY RUN WAS THE ANOMALY.**

  ⚑⚑ **AND I CANNOT IDENTIFY WHICH ENGINE PRODUCED IT.** Two agents were editing
  `iface_dataflow.py` during that window, so the 40/80 plausibly came from a **different version
  than the one on disk**. `git status` says both engine files are **`??` untracked** — *so there
  is no baseline to diff against and no history to ask.* **Ⓝ71i ⟡deletions-need-a-reader in a
  second form: nothing is committed, so the tree cannot answer "was this different an hour ago."**
  *A measurement whose instrument has no version is not reproducible, and I recorded it as a
  headline.*

  ⚑ **WHAT SURVIVES:** the other four modules' counts were re-measured independently by the Ⓝ104
  agent and MATCHED mine, so those stand. **`agda_lex` is UNMEASURED**, and the fixture-provenance
  finding drawn from its witness lists (Ⓝ104f) survives on the witness TEXT, which is evidence
  about shape rather than about the count.

  ⚑⚑ **THE COST FINDING SHARPENS RATHER THAN DISSOLVES: Ⓝ104e ⟡dataflow-cost IS NOW A HARD
  BLOCKER, NOT A NOTE.** The largest module in the authored-stub set does not terminate in 600s —
  *and it is exactly the module where a hand-authored stub is most expensive and a generator would
  pay for itself most.* **A gate that cannot run on the largest member cannot gate the set.**

  ⚑ **AND IT IS A THIRD KIND OF NON-REPRODUCIBILITY TODAY** — after the reader whose verdict
  depended on which spelling was queried, and the gate whose green depended on which glob it ran.
  *Here the verdict depended on WHEN it ran.* **The instrument must carry its own version before
  any figure from it is quotable.**


* ⚑⚑⚑ **Ⓝ104b + Ⓝ104c — REFINEMENT PRODUCED A FALSE `CONFLICT`, AND THAT IS THE FINDING.** Making
  `tuple[Any, ...]` more precise immediately made the reader **accuse the code of a bug that came
  from its own partial knowledge**: two REFINED witnesses beside one COARSE one read as two types,
  so **three AGREEING witnesses were reported as disagreeing.** ⚑⚑ *I filed this item as
  `tuple[Any, ...]` is "honest but coarser" — a precision nicety. It is not: a partial refinement
  is STRICTLY WORSE than the coarse answer it replaces*, because a coarse type is honest about what
  it does not know while a false conflict is a positive claim that is wrong. Fixed by making a
  coarse spelling **ABSTAIN** when a refined type of the same constructor is present, with a
  three-arm discriminator (different constructors and different scalars still conflict).

* ⚑⚑ **VERIFIED BY ME, AND THE REFINEMENT LANDS EXACTLY WHERE IT HAS EVIDENCE:**
  `promotion_report#<return> -> tuple[bool, list[str]]` — **byte-identical to the authored stub** —
  while `scan_file#<return>` correctly STAYS `tuple[Any, ...]` because its elements are bare names
  needing flow analysis. *Fires on evidence, abstains without it.* ⚑ Four sources added, each with
  a live witness: **B2d default value** (a `None` default marked PARTIAL, not the whole answer),
  **B5 element/subscript** (the `args[0]` residue), **no-valued-return → `None`** behind three
  exclusions, and **element-refined displays** only when every element bottoms out.
  ⚑ `jobs#<return>` correctly stayed unresolved — its `raise SystemExit` arms are not `None` —
  **the near-miss that justifies the exclusions.**

  Counts: `gen_build_makefiles` 4/15 → **6/15**, `tsdbprobe` 41 → **42/55**,
  `check_scratch_independence` and `check_carrier_locality` unchanged in count but both SHARPER.
  Suites `iface_bottom` 23 → **38**, `iface_dataflow` 17 → **23**. **No stub was wrong.**

* ⚑⚑⚑ **A REMAINING DEFECT I MEASURED MYSELF, AND IT IS THE SAME SHAPE ONE LAYER ON:**
  `carrier_of#<return>` now reports **`CONFLICT  NoneType | str`** — which **IS the authored stub's
  `str | None`.** *A two-arm return where one arm is `None` is a UNION, not a disagreement*, and the
  reader has no way to separate **"two witnesses contradict each other"** from **"this function
  legitimately returns two types."** ⚑ It is the honest verdict given what the reader can
  distinguish, and it is still the wrong one. **Ⓝ104g ⟡union-is-not-conflict** — a return-position
  join over arms is a UNION by construction; only a PARAMETER join is a genuine disagreement,
  because a parameter has one type while a return has as many as it has arms.

* ⚑⚑ **THE FIXTURE ANSWER IS STRUCTURAL, NOT A FILTER — AND ONE SLOT NOW CONTRADICTS AN
  INTENTIONAL STUB CHOICE.** None of the four new sources reads a CALL SITE (all read the defining
  module's own text), **so none can enlarge the fixture-witness population.** But element
  refinement sharpened two already-fixture-witnessed slots, and one is the clean instance of
  Ⓝ105′: **`tsdbprobe.transitions#pairs` → `list[tuple[int, float]]`, witnessed by four `_selftest`
  fixtures (`:835-841`) and NOTHING ELSE — while its stub deliberately says `object` to force a
  consumer to narrow.** *A sharper type derived entirely from test data, disagreeing with a
  deliberate weakening.* **Both halves of the open question, in one slot.**

* ⚑ **AND IT DELETED A DUPLICATE RATHER THAN SHIPPING ONE.** Its `default_type` initially owned the
  parameter→default lookup that the OTHER agent's `default_of` already owns (right-alignment +
  `kw_defaults` holes); it removed its copy and took the expression instead. **One alignment
  authority** — *the same-name-different-body drift caught before it landed, in a file two agents
  were editing at once.*

  ⚑ Deliberately NOT widened, each for a stated reason: `dict`/`set` element entries (a dict
  subscript is a value lookup; a set has no positional member), slice subscripts (a sequence, not
  an element), local-variable binding (**needs flow analysis** — why `scan_file#<return>` stands),
  and non-`None` unknown defaults. **A source with no witness is a hypothesis.**


* ⚑⚑⚑ **Ⓝ106 ⟡interpret-the-constructor — THE WEAKENINGS EXISTED BECAUSE MODULE-LEVEL ASSIGNMENTS
  WERE INVISIBLE TO THE ENTIRE TOOLKIT.** `iface_dataflow.module_interface` enumerates
  `mod.functions`; `iface_readers --eligible` counts only function slots. **So `DECL`, `SIG`,
  `IMPRE` appeared in NO census** — *not unresolvable, a MISSING SLOT KIND.* **Nobody declined to
  compute them; nothing ever looked.** ⚑ That is the operator's point arriving with a mechanism:
  *"a stub that promised a richer type would be asserting a property no one verified"* was written
  in a world where nothing COULD verify it, and the sentence outlived that world.

  ⚑ **VERIFIED BY ME:** `iface_construct --module scripts/check_carrier_locality.py` →
  **6 of 6**, `DECL: re.Pattern[str]` and `SIG: re.Pattern[str]`, each with a `file:line`.

* ⚑⚑⚑ **AND `agda_lex` IS MEASURED AFTER ALL — 16 OF 17 ASSIGNMENTS, CHEAPLY.** The module whose
  80-slot FUNCTION dataflow exits 124 at 600s answers its assignment slots immediately.
  **Assignments are a different cost class from parameter recursion**, which corrects my
  UNMEASURED entry: *the module was unmeasured for one KIND of slot and always answerable for the
  other.* ⚑ The single residue, `HEADER`, is the honest kind — the duck-typed stand-in the stub's
  own Protocol describes — and the verdict names its own limit: *"a fact about the probe or the
  checker, never proof the expression has no type."*

* ⚑⚑⚑ **THE Π CENSUS IS THE SHARP ARTIFACT: 13 OF 13 ORACLE-ROUTED CONSTRUCTORS ARE `re.compile` —
  100% DEPENDENT, ZERO CONSTANT-RETURN.** *For this corpus a name-keyed table would be wrong at
  EVERY slot it was asked about.* **The dependent form is not an edge case here; it is the entire
  population** — which retires my "handle it or state the restriction" framing outright. ⚑ Typeshed
  is the oracle via batched `reveal_type`; verified live in the suite, `re.compile(r"^x")` →
  `Pattern[str]` and `re.compile(rb"^x")` → `Pattern[bytes]` **in the same run** — *the case a
  table passes every other test and fails.*

  ⚑ **ROUTE CHOICE, MEASURED AGAINST TWO DISAGREEING PEER REPORTS:** batched probe (**~0.53s TOTAL
  warm**, persistent cache) over `dmypy inspect` (**one location per invocation → N × ~0.38s**).
  *The peer's cost analysis was right about the client-spawn tax and that tax is per-LOCATION, which
  the batched form pays once.* The socket route is better still and is **named, not taken** — a
  larger build than this item warrants.

* ⚑⚑ **TWO CORRECTIONS TO ME.** (1) I predicted C3's instance would be `AGDA_JOBS = str(_compute())`.
  **It is literally `AGDA_JOBS = "20"`** — a string literal C2 types with no oracle at all, so
  **`stubtest`'s `Literal['20']` was observing a LITERAL, not a computation.** The C3 line stands
  (the `os.path.dirname(os.path.abspath(__file__))` shape is real in the same module); *my example
  for it was not an instance of it.* (2) C3 is refused **STRUCTURALLY** — any argument that is a call
  or a bare name fails the purity test — *not by a blocklist that could rot.*

  ⚑ **AND ITS OWN SUITE CAUGHT IT VIOLATING ITS OWN RULE:** it asserted a bare literal reveals as
  `str`; it reveals as `Literal['x']?`. **The docstring says "treat revealed types as opaque
  strings, never string-match" and the violation was inside the suite documenting it.**

* ⚑⚑⚑ **Ⓝ105′ ⟡weakening-or-under-specification — ANSWERED: EVERY MODULE-LEVEL `object` COLLAPSES.**
  `DECL`, `SIG`, `IMPRE`, `NEXT`, `MODULE_HEAD`, `SECTION` are all **`re.Pattern[str]` by
  derivation** — *inability-to-verify, which the derivation retires.* So is `judge`'s 2nd return
  element (`object` only because no reader saw through a comprehension) and tsdbprobe's six
  `_get`-body returns (one type, unread). **The category the Ⓝ104 agent called "deliberate
  weakenings — a generator has no input for these" is, at module level, EMPTY.**

  ⚑⚑ **WHAT SURVIVES IS NOT SPELLED `object`, AND THAT IS THE DISCRIMINATOR.** `HEADER:
  _HeaderLike` in `agda_lex` — the author **refused `object` and wrote a two-member Protocol**,
  because the runtime value is a duck-typed stand-in whose `.search` does not return a `re.Match`.
  **A DECISION and an INABILITY look identical when both are spelled `object`**; this one is
  legible precisely because its author declined the lazy spelling. ⚑ *And the reader independently
  confirms it — `HEADER` is the one assignment that does not bottom out.*

  ⚑⚑ **THE NARROWING ARGUMENT FAILS HARDER THAN I ARGUED.** I said it relocates the assumption to
  the call site without checking it. **There IS no call site:** `attr_reads` reports **ZERO
  consumers** for both `check_carrier_locality.DECL` and `gen_build_makefiles.IMPRE` (bounded — the
  reader names its 7 dynamic-import blind spots). *The narrowing that was the stated safety property
  is not happening anywhere.*

  ⚑ **AND THE GATE CANNOT EVER CATCH THIS:** `object` is the TOP TYPE, so `stubtest` cannot
  contradict it. **`check_stub_authority`'s green on these slots is a fact about what `object`
  admits** — a third instance today of a green that measures the instrument. ⚑ One borderline the
  other way: `KNOWN_PRODUCERS` is stubbed `tuple[tuple[str, str], ...]` where derivation gives the
  positional 3-tuple — **here the STUB is better**, arity is not part of the contract, and *a
  generator must widen homogeneous tuples or it over-specifies.*

* ⚑ **SEAMS, NAMED NOT TAKEN** (`iface_dataflow.py` moved under it mid-task, 54026→58885 bytes; it
  built NEW rather than contending): `module_interface` should call `resolve_module` to cover
  assignments, and **`--eligible` undercounts because it never counts assignment slots.**
  **Ⓝ106a ⟡count-the-assignments.**


* ⚑⚑⚑ **Ⓝ104a ⟡reach-vs-dead — THE KIND I MOST WANTED RESTED ON A FALSE PREMISE, AND WAS
  CORRECTLY NOT SHIPPED.** I claimed a `__main__` guard is invisible to the index. **It is not:**
  `pycodemod --calls main` indexes it and `calls_in` walks it — *it is an ordinary `ast.Call`.* So
  "dynamic entry" had no basis; what would GENUINELY be dynamic (a dispatch table, `getattr`) is
  **not separable from UNCALLED with anything the corpus offers**, and is named inside UNCALLED's
  note instead of shipped as a kind. ⚑⚑ *I asked for three kinds and supplied three witnesses; two
  of them collapse into one, because `scan(paths=None)` and `main(argv=None)` are both DEFAULTS.*
  **My caveat on the first case was the general rule, and I filed it as an exception.**

  ⚑ **AND MY THIRD WITNESS WAS WRONG IN ITS DETAILS TOO** — `tsdbprobe`'s guard is `main()`, not
  `main(sys.argv[1:])`; the signature is `main(argv=None)`.

* ⚑⚑ **THREE STATUSES SHIPPED, EACH WITH A LIVE WITNESS AND AN INSTRUCTION TO THE READER:**

      DEFAULTED  determined AT THE DEF, no caller owes it — NOT dead
                 check_carrier_locality.scan#paths · tsdbprobe.main#argv · export_samples#timeout
      UNCALLED   a fact about the CORPUS BOUNDARY, never proof of death
                 7 in scratch/toolmodes.py; >=27 across 6 modules
      OMITTED    sites > 0, none bind the slot, no default — a latent TypeError
                 ZERO in the live tree; witnessed constructively in the fixture

  ⚑ **THE `panflute` WITNESS I PREDICTED DOES NOT EXIST** — that stub is fully annotated, so every
  slot returns STATED and **never reaches the classifier at all.** The corpus-boundary case is real;
  its witnesses are `toolmodes`' CLI handlers, not panflute. *A predicted witness is not a witness.*

* ⚑⚑⚑ **IT KEPT A DETECTOR WITH NO INSTANCE, AND ARGUED THE EXCEPTION PRECISELY.** My rule was *a
  kind with no live instance is a hypothesis, not a category.* It kept OMITTED anyway, on a
  distinction I accept: **dynamic-entry was unwitnessable IN PRINCIPLE; OMITTED is DECIDABLE from
  evidence in hand and merely uninstantiated in a tree whose selftests pass.** *Deleting the
  detector for a defect because the tree currently has none leaves nothing to report it when it
  arrives.* ⚑⚑ And rather than settle that on a 30-module sample — **which would be
  `report-presence-never-absence` one level up, in the decision about the fix** — it added
  `--census` **so the zero has a DENOMINATOR.** A population, not a sample.

* ⚑⚑ **BOTH AGENTS' WORK COEXISTS IN THE SHARED FILE, VERIFIED BY ME.** `export_samples#timeout` is
  **COMPUTED `float`** from a TOTAL default (Ⓝ104b's default-reading) while `main#argv` stays
  **DEFAULTED** with a partial witness (Ⓝ104a's classifier underneath) — *because `None` witnesses
  only one arm, which the note says outright.* **The layering is real, not two edits that happened
  not to collide.** ⚑ `iface_dataflow` suite 13 → 17 → **24**.

  ⚑ **THE GATE REFUSED AND REVERTED SIX TIMES**, each refusal forcing a multi-hunk change into a
  single write. *The per-file gate as a design pressure, six times in one dispatch.*

* ⚑⚑⚑ **AND THE COST FINDING IS NOW TWO-SIDED, WHICH BOUNDS Ⓝ103b ⟡iface-gate SHARPLY.**
  `--census` over all of `scripts/` **did not finish in ~10 minutes** — the walk is
  **O(slots × corpus)**. Combined with `agda_lex`'s function dataflow exiting 124 at 600s while its
  ASSIGNMENTS answer instantly (Ⓝ106), the shape is clear: **assignment resolution is gate-cheap;
  parameter/return dataflow is not.** *A gate could ship the assignment half today and could not
  ship the dataflow half at all* — **Ⓝ104e ⟡dataflow-cost is the blocker on exactly one of the two
  halves, and knowing WHICH is what makes a partial gate possible rather than a compromise.**


* ⚑⚑ **Ⓝ104a's WITNESS SWEEP — UNCALLED IS INSTANTIATED BY EXACTLY THE CASE ITS NOTE PREDICTS.**
  A read-only sub-dispatch measured 30 modules: **≥27 UNCALLED across 8**, and *the clusters are not
  random* — `toolmodes.cmd_*#rows` (7) are **CLI subcommand handlers reached by dynamic dispatch**,
  `shared_cache`'s (9) are **a library surface whose callers lie outside the corpus.** **The two
  shapes the status's own note names, found without looking for them specifically.** ⚑ Plus
  `agda_lex` 5, `schema_queue` 3, and one each in `proofcost`, `pipeflow`, `scope_store`, `vfs`.

  ⚑⚑ **AND IT REFUSED TO CONVERT ITS OWN ZERO INTO A VERDICT.** OMITTED: none in 30 modules —
  reported as *"a fact about the sample, not proof the kind is uninstantiable"*, with the missing
  **`--corpus` MODE named as the work** rather than a conclusion drawn. **That is the same
  discipline the Ⓝ104a agent reached from the other side** (keep the detector, add `--census` for a
  denominator) — *two agents, two directions, one rule: a zero needs a population before it is an
  answer.*

* ⚑⚑⚑ **AND THE ROSTER SCARE WAS A REPORTING GAP, NOT A CONTENTION ONE — THE FAILURE MODE IS WORTH
  MORE THAN THE ALARM.** I could not account for a running subagent and **held a dispatch on it for
  ~40 minutes.** It had **finished and never reported**: my first status query never reached a
  running loop, and a `SendMessage` that RESUMED it produced the full answer in ~20 seconds.
  ⚑ **An agent that finished without reporting is indistinguishable from one still working**, and
  `ListAgents` shows both as `running`. *I treated an ambiguity in the instrument as a fact about
  the work.*

  ⚑ **THE mtimes HAD ALREADY ANSWERED IT** — `iface_dataflow` 16:35, `iface_construct` 16:07,
  `iface_bottom` 15:44, each matching a reported agent's final write — **and the sub-dispatch wrote
  nothing at all.** *The evidence to dissolve the block was in hand before I raised it.*
  **Ⓝ108 ⟡finished-is-not-running.**


* ⚑⚑⚑ **Ⓝ94a″ ⟡wire-the-stub-gate — WIRED, AND THE PROBE FOUND A PERMANENT FREE PASS FOR THE
  EXACT DEFECT THE GATE EXISTS TO CATCH.** I asked whether UNVERIFIABLE should fail, warn or pass,
  and noted it *"might not be one thing."* **It is not, and the split is stronger than a treatment
  difference: one half was an UNFAILABLE STATE.** A stub for a **module that no longer exists** and
  a stub whose **third-party dep is missing** both arrive as `ModuleNotFoundError` and were
  **byte-identical to the reader** — so an orphaned stub passed forever **while still SHADOWING
  that import name, so mypy kept checking callers against a module that is gone.**
  *The defect the gate is for, wearing the one costume that walked past it.*

  ⚑ **FOUND BY PROBING, NOT BY REASONING** — a `stubs/_ghostmod.pyi` dropped in beside the real
  ones. **The verdict is now four-valued, split by WHICH module the import error names:**

      absent-dep   a third-party package is missing (paperkit needs bibparse)
                   a fact about THIS MACHINE, unfixable by the stub's author → REPORTED, PASSES
      orphaned     the missing name IS the stub's own module or a submodule
                   a fact about the STUB → FAILS

  ⚑⚑ **AND THE DISCRIMINATOR IS DOTTED, WHICH IS THE WHOLE CARE:** `f"{missing}."` against
  `f"{module}."`, so `paperkit.grade` is orphaned but the prefix-sharing sibling `paperkit_extras`
  is **not**. *A bare `startswith` would have called a healthy stub orphaned and sent a reader to
  delete it*; that case is pinned. ⚑ An import failure with **no parseable module name stays on the
  PASSING arm** — *an unparsed message is not evidence of an orphan, and inventing one would fail a
  clean checkout.* **The Ⓝ95 ⟡the-tracking-gaps hazard avoided by construction rather than by
  care.**

* ⚑⚑ **FIRE-PROBED BY ME, BOTH ARMS, IN ONE RUN.** `_ghostmod` → **exit 1,
  `✗ _ghostmod — ORPHANED: the module this stub describes is GONE`**, successor named (*delete the
  stub, or restore the module*) — **while `paperkit` stayed on the passing arm in the SAME run**,
  exercising both discriminators simultaneously. Probe removed; verdict **byte-identical to the
  pre-change baseline** (`clean (8 of 9)`). ⚑ The drift arm was probed too (renaming
  `tsdbprobe.matches#expected` → `wanted`): **exit 1, DRIFT, with stubtest's stub-vs-runtime lines
  and the repair successor.** *A gate wired but never exercised is the same class of defect as the
  one it was wired to fix.*

* ⚑ **PHASE A, JUSTIFIED AGAINST THE REFLEX.** The gate IMPORTS the runtime, which invites Phase C.
  **Rejected: Phase C's justification is POST-BUILD FRESHNESS for gates reading `.agdai` cores**,
  and this gate reads no core and measures nothing the build produces — *Phase C would buy it
  nothing and merely park it behind an expensive step.* Measured ~21s, Phase A's own scale.
  ⚑ Censuses regenerated **by the owning tool**: `gate_census --sync --apply` (35→36 blocking, also
  clearing another agent's pre-existing drift), `gen_build_makefiles --sync-census` (36→37). Lands
  in the **named-successor** column. ⚑ It **deliberately did NOT sync** the tool-mode and sql
  censuses — *both dirty from other agents' in-flight work, and syncing would bank their unfinished
  state into a gated artifact under its name.*

* ⚑⚑⚑ **AND IT CORRECTED ITS OWN REPORT AFTER A FULL SWEEP IT HAD SUBSTITUTED A LEDGER FOR.**
  `selftest-contract: BROKEN — 268 NEW suite(s) reporting by PROSE instead of a typed record`, and
  **`check_stub_authority.py` is on that list** — pre-existing (267 others share the shape,
  including every `*_selftest.py`), reading 268 NEW **because its baseline is ABSENT/EMPTY, not
  because today grew it.** ⚑ Its own words: *"I should have caught it by running `run_selftests.py`
  to completion BEFORE reporting rather than substituting the `--last` ledger."* **A stale ledger
  read as a live measurement — the ⟡fresh-comments shape, in a verification step.**
  ⚑ Paydown named, not taken unasked (it would touch a census needing re-verification):
  **⟡stub-gate-typed-record.**

  ⚑ **NOT DONE, NAMED AS A DRAIN: `gate_preflight.py` CRASHES on `ratchet._read`** — *the one tool
  that could dry-run the whole gate set is unavailable*, so every gate was verified individually.
  Owner: whoever landed `ratchet_legacy.py` today. **Ⓝ109 ⟡repair-gate-preflight.**




* ⚑⚑⚑ **Ⓝ105″ ⟡refuse-the-lazy-top-type — THE "NO CONSUMER" PREMISE WAS FALSE, AND THE SECOND
  MEASUREMENT REPRODUCED THE ERROR RATHER THAN CATCHING IT.** I relayed `attr_reads` reporting
  **zero consumers** for `check_carrier_locality.DECL` and `gen_build_makefiles.IMPRE`, and built
  an argument on it (*"the narrowing that was the stated safety property is not happening
  anywhere"*). **Both have live, load-bearing consumers** — `tests/test_declaration_visibility.py:57`
  and `tests/test_import_edge_agreement.py:59` — spelled **`from <module> import DECL`, a BARE
  NAME**, which `attr_reads` cannot see because it reads `<module>.DECL`.

  ⚑⚑ **AND THE CROSS-CHECK AGREED, WRONGLY.** The agent then queried the bare-LEAF spelling, got
  zero again, and *nearly banked it as confirmed* — **but both spellings are attribute-shaped and
  therefore CORRELATED, blind to the same thing.** `census-keyed-on-one-spelling` compounded by
  `correlated-instruments-agreeing-is-not-coverage`. ⚑ *And the seven dynamic-import blind spots
  the tool honestly names were NOT where the miss was* — **the reader's stated limits pointed away
  from its actual one.**

  ⚑ **THE CONSUMERS EACH CARRY AN `isinstance(..., re.Pattern)` NARROWING**, which after the
  repair is a **runtime confirmation of the derivation** rather than the only thing standing
  between the test and `object`.

* ⚑⚑⚑ **THE MARKER RULE I PROPOSED WAS BUILT AND REJECTED, WITH THE RIGHT REASON.** I suggested
  *"a bare `object` must carry a stated reason."* The agent's verdict: that **taxes every honest
  slot and is satisfiable by TYPING A SENTENCE**, so the check becomes *"did someone write prose"*
  rather than *"is this derivable."* ⚑⚑ **A marker is the right mechanism for a DECLINED SURFACE**
  (`stub_declines`, where the fact is editorial and nothing can compute it) **and the wrong one
  here, where the fact is mechanical.**

  ⚑⚑⚑ **THE DISCRIMINATOR WAS ALREADY IN THE SOURCE: WHETHER THE ASSIGNMENT BOTTOMS OUT.**
  `iface_construct` computes 16 of `agda_lex`'s assignments and leaves exactly one UNRESOLVED —
  **`HEADER`. The author's refusal of the top type and the reader's inability to resolve the slot
  pick out the SAME NAME, independently.** *So the rule needs no new declaration for anyone to
  maintain.* Verified by me: `stub_top_type stubs/agda_lex.pyi scratch/agda_lex.py --check` →
  **clean, zero — while that file still HOLDS the declined `object`-alternative.**

  ⚑ **THE VERDICT IS ONE-SIDED BY CONSTRUCTION, AND THE DIRECTION IS THE CLAIM.** COMPUTED +
  `object` = DEBT; UNRESOLVED + `object` = **SILENT**, *because a reader's stopping point is a fact
  about the READER, never proof the slot has no type.* **Asserting the converse would turn every
  gap in `iface_construct` into a false accusation against a stub.** The output says so in its own
  footer.

* ⚑⚑ **A STUB DOCSTRING WAS FACTUALLY WRONG, AND ONE `object` OVER SEVEN SLOTS IS WHAT HID IT.**
  `tsdbprobe.pyi` claimed all seven returns *"return `_get`'s parsed body"*. **Three do not** —
  `export_samples`, `producers`, `transitions` each build a LOCAL list. ⚑ The other four genuinely
  ARE `json.loads` passthroughs, **so `object` correctly STAYS on those four**: *an `Any` from the
  oracle is an ABSENCE, and stating a JSON shape there would invent the schema of someone else's
  store.* **My framing treated the seven as one class.**

* ⚑ **STRENGTHENED, EACH WITH A `file:line` WITNESS:** `DECL`/`SIG` and `judge`'s 2nd return
  element (check_carrier_locality) · `IMPRE` (gen_build_makefiles) · `NEXT`/`MODULE_HEAD`/`SECTION`
  (agda_lex) · three of tsdbprobe's seven. **Left unchanged and independently confirmed:**
  `HEADER: _HeaderLike`, and `KNOWN_PRODUCERS` — *where the STUB is better*, its variadic tuple
  correctly widening a derivation that is positionally 3-long **only because the literal holds
  three entries today.** ⚑ Each stub's docstring **records the reversal**, rather than silently
  flipping a line.

  ⚑⚑ **GATE BEFORE AND AFTER: BYTE-IDENTICAL** (`clean (8 of 9)`), verified by me. **No new drift
  — and the strengthened types are FALSIFIABLE for the first time**, with `stubtest` confirming
  every one. *A slot that cannot fail is not being verified by the thing that passes it.*

  ⚑ **NOT REACHED, AND SAID SO:** function RETURNS, because `iface_dataflow` exits 124 at 600s on a
  live module and **a check that sometimes times out reports a MACHINE fact as a STUB fact** — the
  exact collapse `check_stub_authority.classify` exists to refuse. ⚑ `PYI021` fires on every file
  in `stubs/` including untouched ones — **pre-existing and unfixable here, since `stub_declines`
  READS those docstrings as the declines mechanism**; verified against an untouched stub rather
  than assumed. **`substrate/stub_top_type.py` (14/14) is a READER, not wired** — the hook is red
  tree-wide, and a new finding there is indistinguishable from the standing ones.


* ⚑⚑⚑ **Ⓝ106a ⟡count-the-assignments — `--eligible` WAS BLIND TO DEBT WHILE REPORTING THOSE SLOTS
  AS FINE, AND THE MECHANISM IS A `complete`-BY-CONSTRUCTION BUG.** `iface_infer.symbols_of` DOES
  emit an `assign` Symbol — but with no params and `is_function=False`, so **`Symbol.slots` is 0
  and the slot is `complete` by construction.** An unannotated `DECL = re.compile(...)`
  contributed **nothing to the denominator** and read as fully stated.

  ⚑⚑ **THE DECISIVE MEASUREMENT, WHICH I WOULD NOT HAVE THOUGHT TO TAKE:** `stubgen --no-import`
  on `check_carrier_locality.py` emits **six `Incomplete`s for exactly those assignments** — in a
  module `--eligible` called **`0/13`**. *So the reader was not merely imprecise: it was blind to
  debt that blocks eligibility EXACTLY AS HARD as an unannotated parameter.* **A denominator that
  omits a slot kind reports the numerator as the whole story.**

  Denominators, verified by me: `agda_lex` **80→97**, `check_carrier_locality` **13→19**,
  `gen_build_makefiles` **15→24**, `tsdbprobe` **55→59**, `check_scratch_independence` **5→6** —
  **37 assignment slots surfaced, 36 derivable today.** All five stubs still read `NO`; *the
  verdict did not change, the denominator became honest.* ⚑ And `HEADER` sits in the owed list
  while only **16 of 17** are derivable — **the same one-sided verdict `stub_top_type` reaches
  independently, from the other side.**

* ⚑⚑⚑ **IT REFUSED THE SEAM I NAMED, AND THE REASON IS THE REGRESSION I HAD FLAGGED.** I asked for
  `module_interface` to call `resolve_module`. **`module_interface` is only ever reached through
  `Resolver`, whose every path runs the corpus walk** — so wiring assignments THERE makes them pay
  function-dataflow cost by construction. *I pointed at the exact place that would cause the
  regression I warned about in the same brief.* It wired `--eligible` to `iface_construct` directly
  instead. **Seam reported, not taken.**

  ⚑ **THE COST ASYMMETRY SURVIVES AND IS NOW MEASURED:** `--eligible` ~0.4s → **3.38s** for 37
  previously-invisible slots; `iface_construct` on `agda_lex` **1.49s** against `iface_dataflow`'s
  **exit 124 at 600s**. **At minimum 400×, and the true ratio is UNMEASURABLE because the expensive
  side never finished.**

* ⚑⚑⚑ **Ⓝ103b′ — THE GATE STATES ITS OWN LIMITS IN THE SAME BREATH AS ITS GREEN.** Verified by me:
  *"THIS ASSERTS A DIFFERENTIAL: every module-level assignment derives the same type it did at sync
  time, and the set is unchanged. It does NOT assert the types are correct, nor that they agree
  with `stubs/*.pyi`."* **A derivation wrong at sync time stays wrong and stays green** — said
  outright rather than discovered later. *After four greens this session that were facts about
  their instrument, this one refuses to be a fifth.*

  ⚑⚑ **AND IT ADDED A BOUND I DID NOT ASK FOR: THE ORACLE IS PART OF THE INSTRUMENT.** On a machine
  without mypy every COMPUTED derives as UNRESOLVED and **the gate fires — reporting a fact about
  THAT MACHINE as drift.** *The honest direction (false STALE, never false fresh), documented
  rather than papered over* — the same three-valued discipline `check_stub_authority` reached,
  turned on its own dependency.

  ⚑ **NO ABSENT-BASELINE FREE PASS, BY CONSTRUCTION:** no census → **exit 1, not 0**, because the
  committed block IS the baseline. *So `check_mypy_ratchet`'s failure mode — exit 0 while reporting
  116 errors — is structurally impossible here.* Fires three ways (missing, perturbed with a
  unified diff naming the slot and the paydown command, fresh in 2.97s). **Not wired**, as
  instructed.

* ⚑⚑ **FIXTURES STRUCTURALLY CANNOT REACH THIS, AND NOT BECAUSE OF A FILTER SOMEONE REMEMBERED.**
  `resolve_module` reads only the defining module's own `ast.Module` — its assignment expressions
  and import block. **It never enumerates call sites, so `corpus.py_files` never enters the walk
  and a `tests/` file has no POSITION from which to become evidence.** *Ⓝ104f cannot recur here*,
  and a fixture could only affect this gate by BEING a stub-backed module.

* ⚑⚑⚑ **A FOURTH DISAGREEMENT, AND IT MAKES TWO OF FOUR "THE STUB WINS".**
  `check_carrier_locality.ALLOW` is stubbed **`set[str]`** and derives **`set[Any]`** — *the stub
  is better*, because `iface_bottom` deliberately has **no `ELEMENT_OF` entry for sets**, so the
  derivation cannot refine a set display. **This is a SECOND instance of the `KNOWN_PRODUCERS`
  class, not a variant of the `object` weakening.** ⚑ My framing had three cases with three
  verdicts; there are four. ***That is precisely why `--vs-stubs` must be ADVISORY: a gate
  demanding agreement would demand the wrong answer twice, not once.***

  ⚑ Amendment carried: `AGDA_JOBS = "20"` is constant-folded at C2 with **no oracle** — the C3
  rule stands on `ROOT = os.path.dirname(...)` in the same module. *Worth stating because a reader
  could otherwise cite `AGDA_JOBS` as needing a runtime oracle it demonstrably does not.*


* ⚑⚑⚑ **Ⓝ104e ⟡dataflow-cost — ANNOTATION IS NOT THE COST FIX, AND THE EVIDENCE IS THE EXACT
  OPPOSITE OF THE HYPOTHESIS I CARRIED FORWARD.** `tsdbprobe` is the **most-annotated** module
  (37/55 stated) **and the most expensive** (55.6s CPU) of the four measured. **The cost tracks the
  ABSOLUTE COUNT of owed parameter slots, not the annotated RATIO** — so annotating a module
  reduces its own cost linearly and **does not change the O(slots × corpus) shape.** *A prior agent
  hypothesised annotation as the fix for `agda_lex`'s non-termination; I briefed it as the
  experiment to run; it is false.*

      check_scratch_independence   2 owed param slots ·  2 sweeps · 10.6s
      check_carrier_locality       6                  ·  6        · 30.2s
      gen_build_makefiles          6                  ·  6        · 30.7s
      tsdbprobe                   11                  · 11        · 55.6s

  **CPU ≈ (owed parameter slots) × (one full corpus sweep ≈ 5s over ~1240 files).** The mechanism is
  `iface_dataflow.py:476` — `_parameter` calls `call_sites(func, self.paths, mod)`, which `load()`s
  and `ast.walk`s **the entire corpus per slot.** ⚑ `Resolver.memo` is keyed on the SLOT, so it
  prevents re-resolving a slot **but not re-scanning the corpus.** Verified by me: 7,500 parses over
  1,250 distinct files on `check_carrier_locality`.

  ⚑⚑ **AND THE SPAWN TAX DOES NOT APPLY HERE** — no mode reached by `--module` shells out; the only
  `subprocess` is in `--sites`, a different mode. *Acting on the peer's `dmypy` measurement would
  have optimised a cost that is not present.* **Both of my hypotheses were wrong, and profiling
  rather than reasoning is what separated them.**

* ⚑⚑⚑ **THE RATIO OVERSTATES THE FIX BY 3×, AND THAT IS THE TRANSFERABLE FINDING.** `--cache`
  measures **actual end-to-end 1.7×** (`check_carrier_locality`) and **2.1×** (`tsdbprobe`) against
  a redundancy RATIO of **6× and 11×** — verdicts byte-identical in both arms. **The gap is the
  finding: a sweep re-parses AND re-walks (`calls_in`, `binds`); a memo removes only the first
  half.** ⚑⚑ ***A ratio from a counter is an UPPER BOUND on a fix, never its value*** — and the
  tool now says so in its own output, so the next reader cannot quote 6× as a speedup.

  ⚑ **THE HONEST ANSWER IS ALGORITHMIC, AND IT IS NAMED: INVERT THE LOOP.** Build the call index
  ONCE per `Resolver` — one corpus pass producing `name → [(where, Call, Module)]` — making the walk
  **O(corpus + slots)** instead of O(slots × corpus). *That is `agda_lex` from >600s to roughly one
  sweep.* **A parse memo is a 2× palliative on an algorithmic problem; the index is the fix.** Not
  implemented (another agent owned the file); **handed over as a seam, with `--cache` as the
  verifier because it compares VERDICTS, not just clocks** — so a fix that changes an answer reports
  as wrong rather than fast. **Ⓝ104e′ ⟡invert-the-call-index.**

  ⚑ **Ⓝ103c's FIVE ANNOTATION TARGETS ARE ALL DRAINS** — `check_scratch_independence` alone carries
  **133 findings** (the "cheapest", at 5 owed slots), the other four **612 combined**. `ANN001`/
  `ANN201` are among them, *so the annotations ARE part of the owed paydown* — but so are ~500
  unrelated `PTH*`/`T201`/`E501`/`C901`, and the gate reverts on any. **The experiment ran instead
  on the natural gradient the corpus already provides** (0/13, 0/15, 8/80, 37/55) **plus a
  zero-sweep control on a fully-annotated module** — *stronger than one before/after, because it
  separates RATIO from COUNT, which a single annotated file could not.*



* ⚑⚑⚑ **Ⓝ104f + Ⓝ104g — `COMPUTED` WENT DOWN 42→40 AND THAT IS THE CORRECT DIRECTION.** The
  agent states it outright: it did not chase the count, **and it did not FILTER fixture witnesses
  out** — *filtering would have made `extract_values#body`'s CONFLICT vanish, converting a real
  finding into a confident wrong answer.* **A new status `FIXTURE` sits OUTSIDE both `RESOLVED` and
  `STUCK`**: witnesses and `file:line`s are KEPT (dropping them would discard the finding *"only a
  test has ever exercised this"*) while `.computed` returns None, **so nothing can promote a
  fixture into a stub.**

  ⚑ **VERIFIED BY ME, AND THE NOTE STATES THE DISTINCTION EXACTLY:**

      FIXTURE  tsdbprobe.transitions#pairs -> list[Any] | list[tuple[int, float]]
        ⚑ every witness is TEST MATERIAL (inside a fixture def at :783) — a fixture records what
          one author chose to PASS, never what the contract REQUIRES

  ⚑⚑ **AND THAT DISSOLVES THE ONE SLOT THAT CONTRADICTED A DELIBERATE STUB CHOICE.**
  `transitions#pairs` was computing a SHARPER type than its stub's `object`, entirely from four
  selftest fixtures. **The stub was right; the reader now agrees for the RIGHT REASON rather than
  by accident.**

* ⚑⚑⚑ **`carrier_of#<return>` HAS NOW HELD THREE STATES IN ONE DAY, AND EACH TRANSITION WAS A REAL
  CORRECTION.** A confident wrong **`NoneType`** (a majority vote over only the arms the reader
  understood) → an honest-but-wrong **`CONFLICT NoneType | str`** → **`COMPUTED str | None`**,
  verified by me and **byte-identical to the authored stub.** *The intermediate state was not
  wasted: it was the honest form of a question the reader could not yet answer.*

  **THE RULE, AS STATED IN THE CODE:** *a function has as many return types as it has `return`
  arms; a parameter has exactly one.* Several types in RETURN position is **a union by
  construction** — the arms are alternatives the callee genuinely produces. Several in PARAMETER
  position is **a disagreement** — the call sites cannot all be right about one declaration.
  ⚑⚑ The deeper justification recorded with it: **a return witness is a fact about the callee's OWN
  BODY** (two are two things one author wrote on purpose); **a parameter witness is a fact about a
  DIFFERENT MODULE'S CALL** (two are two authors who cannot both be right). ⚑ **Abstention runs
  FIRST in both positions** — *the ordering is what stops this change from laundering the earlier
  false-CONFLICT bug into a false COMPUTED.*

* ⚑⚑⚑ **I WAS WRONG THAT `Witness` MUST CARRY PROVENANCE — AND THE RIGHT LAYERING IS THE FINDING.**
  I wrote *"a witness must carry where it came from."* **Provenance is a property of the CORPUS
  POSITION, derivable from `Witness.where`, not of the evidence extraction** — so `Origins` computes
  it in `iface_dataflow` with a per-file memo, **and no `iface_bottom` change is needed at all.**
  *My framing would have pushed a concern into the wrong layer and created a seam where there is
  none.*

  ⚑ **THE DELIMITER IS GROUNDED IN A MEASUREMENT, NOT A GUESSED CONVENTION:**
  `pycodemod --calls _selftest` reports **103 defs of that exact name** corpus-wide, and **both
  live defects sit inside one** (`agda_lex._selftest` at :1188 encloses :1441-1450;
  `tsdbprobe._selftest` at :783 encloses :819-846). ⚑ **What it misses, stated rather than
  papered over:** a fixture in a differently-named helper reads as production (the affix test is
  anchored at BOTH ends deliberately — *swallowing a PRODUCTION name is the dangerous direction,
  since it suppresses real evidence*); a production call INSIDE a `_selftest` reads as fixture; and
  **an unparseable witnessing file fails toward `production` on purpose** — *an I/O or syntax error
  is a fact about this machine, and downgrading on it would let the instrument report its own
  boundary as the subject.*

* ⚑⚑⚑ **A LATENT BUG MY CHANGE MADE REACHABLE, CAUGHT BY A DISCRIMINATOR — AND IT WAS A SECOND,
  WEAKER COPY OF ONE RULE.** `Computed.computed` abstained on a single refined type **WITHOUT** the
  `_consistent` constructor check `_verdict` has always had. **Unreachable while every multi-type
  slot was a CONFLICT.** The moment returns could union, `list[str]` beside `tuple[Any, ...]` hit
  that line and reported a confident **`list[str]`, silently dropping the tuple arm.** *One rule in
  two places, the weaker copy dormant behind a condition that had never been false* — fixed with a
  regression arm.

  ⚑ **AND ITS OWN DELIMITER WAS WRONG ON FIRST CUT, CAUGHT BY ITS OWN SUITE:** a tail-only affix
  test classified `_cases_given` — **this module's own test data** — as production. *The delimiter
  built to stop fixtures entering computed types was blind to the reader's own fixtures.*

  ⚑ **A FOURTH INSTANCE I HAD NOT NAMED, FOUND BY THE NEW READER RATHER THAN BY HAND:**
  `tsdbprobe.extract_names#body` was reporting a confident `COMPUTED str` from two `_selftest`
  fixtures at :915/:918, contradicting a stub that says `object`. **Invisible precisely because its
  fixtures AGREE** — exactly the shape predicted, and now surfaced mechanically. Suite 24 → **29**.

* ⚑⚑⚑ **Ⓝ73″ ⟡the-tests-seam — LANDED, AND THE +2 IS THREE CASES ENTERING THE DENOMINATOR THAT
  RUNS THEM.** Verified by me: `python3 -m pytest --rootdir … tests` → **54 passed**. Before: 52.
  **Nothing was added or lost** — `test_root_spelling_does_not_change_the_answer` ran three
  `subTest(root=…)` sub-cases inside ONE test; unittest counted the container, pytest counted 1
  test + 3 subtests OUTSIDE the total, and `parametrize` promotes them to 3 collected tests.
  *The three always ran; only the count changed.* ⚑ Ten suites converted, `ruff check tests/` and
  `mypy tests/` both clean — `test_agda_lex_names.py` alone had carried 85 findings and was
  unwritable under the per-file gate, so this was PAYDOWN, not restyling.

  ⚑⚑ **RETIRING THE `sys.path` INSERT MADE THE PRE-COMMIT LINE A FORCED EDIT, NOT AN OPTIONAL
  ONE.** The reach moved into `pythonpath`, which **only pytest reads** — so
  `python3 -m unittest discover` now fails to import all eight importing suites. *Leaving the gate
  line would have turned a green gate red at the next commit.* Rewired with root and path explicit
  rather than inherited from the hook's cwd.

  ⚑ **`tests/__init__.py` SURVIVES DELIBERATELY** — without the package marker, `from tests import
  corpus` reports no stub and every fixture becomes an `Any` that `disallow_any_expr` refuses.
  **Deleting it would have traded a checked import for an unchecked one** — the same trade the
  insert was making, from the other side. ⚑ `conftest.py` holds NO logic, on the same principle:
  reproducing the reach as a fixture would re-mint the retired mechanism inside its replacement.

  ⚑ **`mypy substrate tests` is green TODAY (360 files)** — widening `files` is zero-cost right
  now, and was left undone as out of scope. ⚑ The ~300 `*_selftest.py` are deliberately scoped OUT
  by `testpaths`: four of their capabilities have no pytest analogue.
