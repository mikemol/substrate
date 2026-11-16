# Ⓝ31 residue — the store and its tenants

**Concern: what the SPPF store actually holds, and the tenant-scoped refusal that read as an
outage for a whole session.** Index and arc frame:
[`toolmodes-split.md`](toolmodes-split.md).

⚑⚑ **THIS PART ARRIVED DURING THE SPLIT AND THE CONSERVATION GUARD IS WHAT FOUND IT.** These
entries were appended by a concurrently-dispatched agent after the initial partition was
derived; the guard reported them as dropped content, which is exactly the case it exists for — a
partition is a snapshot, and the document moved underneath it. *The same "re-read the census at
dispatch time" discipline this arc records elsewhere, arriving as a property of its own record.*

⚑ Ⓝ83 ⟡tenant-scoped-refusal-is-not-an-outage is the sibling of `wrong-tenant-read-is-silent`
with the failure mode INVERTED: that one returns plausible wrong rows, this one a plausible wrong
ABSENCE. Ⓝ29a closes as stale — the premise had no referent.

## Residue

* ✅ ⚑⚑⚑ **Ⓝ29a ⟡store-drain-cause — CLOSES AS STALE. THE PREMISE HAS NO REFERENT: THERE IS
  NOTHING DRAINING.** Verified by me (`schema.py --growth --live`), not from the report:

      core_decoded   932.5 MB        ← the only surviving data
      obs · edge · event · obs_node · _node · node_child · _unit · unit_node
      terms · path_text · every dec_* / orbit_* / graded_orbit_*      ALL 0.0 MB

  The census records `obs` 72.8M / `edge` 72.8M / `event` 19.0M and `obs_node` at ~950k.
  **Those figures are gone from this tenant.** A drain-RATE question presupposes staged residue
  growing or shrinking; **`--growth` is byte-identical across two samples, so the rate is exactly
  0.** 45 indexes at the 8192 B empty-relation floor; 25/25 declared indexes PRESENT; `--activity`
  reports no other connections; `--locks` QUIESCENT.

  ⚑⚑ **AND THE AGENT SEPARATED MEASURED FROM INFERRED RATHER THAN NAMING A CAUSE.** MEASURED: no
  event/SPPF data, schema fully intact, nothing running, rate zero. INFERRED and explicitly NOT
  established: that this is a *drained or never-refilled* store rather than a corrupt one — **a
  successful `--flush`, a tenant recreate, and "ingest never re-ran after a rebuild" are
  indistinguishable from the state alone.** ⚑ It named `set1_ratchet_cores`' read-path prune as
  *"a plausible mechanism… consistent with is not established by"* and refused to assert it. That
  is the unestablished-cause discipline held under pressure to close an item.

  ⚑ **PERISHABILITY: UNSUPPORTED, AFTER FOUR SESSIONS OF CARRYING IT AS URGENT.** Nothing degrades
  on a clock — quiescent, zero backends, static across samples. **There is no comparison window to
  lose because `--packed` reports there is no window at all**: both `--equiv` arms read `obs_node`,
  which is empty, so the gate is vacuous either way rather than endangered. *The urgency described
  a condition that no longer exists, and no one re-derived it for four sessions — including me,
  who listed it as "perishable" in every paths-forward today.*

  ⚑⚑ **WHAT SURVIVES IS A DIFFERENT, WELL-POSED QUESTION** — Ⓝ29b: *why did the store lose 3,208
  cores' worth of ingest, and is the refill path (`make all` ingest → `sppf_db --converge`) still
  wired?* That is live. "Drain cause" is not. ⚑ And the one genuinely perishable thing is NOT this
  item: **`core_decoded` at 932.5 MB / 2,311 rows is the only surviving data and nothing
  establishes it is reproducible.**

* ⚑⚑⚑ **Ⓝ83 ⟡tenant-scoped-refusal-is-not-an-outage — I RELAYED "POSTGRES IS DOWN" TWICE AND IT
  WAS NEVER TRUE.** The two tenants use **different transports**: `--live` connects and answers;
  `--sandbox` goes over TCP `127.0.0.1:5432` and is refused (`store.py:492 sandbox_connect`). So
  the earlier agent's *"postgres refusing connections on 5432"* was **tenant-scoped and still
  true** — and I carried it forward as an environment fact, using it to excuse an unverifiable
  `sppf_db.py` cut and to frame this dispatch.

  ⚑⚑ **IT IS THE SIBLING OF `wrong-tenant-read-is-silent`, AND THE FAILURE MODE IS INVERTED:**
  that one returns *plausible wrong rows*; this one returns a **plausible wrong ABSENCE.** An
  agent that probes sandbox and reports "the store is down" has made a true statement about one
  tenant and a false one about the substrate — **the exact shape this session has now measured
  six times, arriving through a transport rather than a spelling.** Filed by the oracle as
  `sql-F44`.

* ⚑ **Ⓝ83a — DRIFT FOUND EN ROUTE, REPORTED NOT ROUTED AROUND.** `sql_lift --check-census` is
  STALE: pipelines 1198→1181, carrier nodes 2631→2595, licensed lifts 119→114, recursion-pole
  59, carrier-unmodelled 49. **Six untracked `.py` files sit in `jea/metalanguage/`**
  (`dec_drain`, `dec_tree`, `query_decl`, `schema_diag`, `sorted_stream`, `sql_census`) **and the
  lift map interns them** — so the census measures a tree that includes uncommitted work. ⚑ That
  is the *"did the arc move or did I move it?"* gap the skill names as a missing mode, now with a
  concrete instance. Also: **live carries 31 relations against 28 declared** — the direction is
  INVERTED from the skill's note, and `ref` is declared-but-absent.


* ✅ ⚑⚑⚑ **Ⓝ29b ⟡the-refill-path — CLOSED. THE STORE IS A DERIVED VIEW, NOT AN ARTIFACT.**
  Operator, 2026-09-02: *"As for Ⓝ29b; that happens. The database contents aren't precious;
  they're recoverable by invoking `make`, which will rebuild the agdai files and re-ingest them
  into the database properly."*

  ⚑⚑ **SO THE QUESTION I CARRIED — *"why did the store lose 3,208 cores' worth of ingest"* — WAS
  ASKING ABOUT AN ARTIFACT THAT HAS AN AUTHORITY.** The `.agdai` cores are the source; the store
  is what `make all` INGESTS them into. A drained store is a cache miss, not data loss, and the
  refill path is the ordinary build. **Nothing needs to be explained, because nothing was lost.**

  ⚑⚑⚑ **AND THAT IS Ⓝ85a's TEST ARRIVING AT A SCALE I DID NOT APPLY IT TO: *does something else
  already know this?*** I have spent this session refusing to write a line count into prose
  because `mdstruct --budget` owns it — and then treated 933 MB of derived rows as precious
  because they were large and gone. **A measured number in a document and a materialised table in
  a store are the same shape: a derived view whose authority is elsewhere.** Size made one feel
  like an artifact and not the other.

  ⚑ **WHAT SURVIVES IS NARROWER AND STILL WORTH KNOWING:** the `sql-oracle` measured
  `--growth --live` byte-identical across two samples, `--activity` reporting no other
  connections, `--packed` reporting `obs_node` EMPTY. **So the ingest is not running, and
  `--equiv pack.sql pack.python` is VACUOUS EITHER WAY until it does** — both arms read `obs_node`.
  That is a fact about what can be MEASURED today, not a defect: *the comparison window reopens
  when the build runs, and does not need chasing.*

  ⚑ **AND THE PERISHABILITY CLAIM IS NOW FULLY RETIRED.** I carried Ⓝ29a as *"oldest open item,
  perishable"* in every paths-forward for four sessions without re-deriving it once; the oracle
  showed the drain rate is exactly zero, and the operator has now shown the premise was wrong at
  the root — **there was never anything to preserve.** *An item can be urgent-sounding for years
  because nobody asked what would be lost.*


* ⚑⚑⚑ **Ⓝ92 ⟡refused-is-not-down, THIRD INSTANCE — AND THIS ONE IS A CREDENTIALS GAP, NOT EVEN A
  TRANSPORT ONE.** Operator: *"postgres is up, but you'll have to ask cassian-observability for
  the connection string."*

  **The chain of readings, each honest and each narrower than how it was carried forward:**

      an agent      "postgres is refusing connections on 5432"        — TRUE of the sandbox path
      me            relayed it as an ENVIRONMENT FACT, twice          — used it to excuse an
                                                                        unverifiable sppf_db cut
      the oracle    "SPLIT: live answers, sandbox is refused; the
                     two tenants use DIFFERENT TRANSPORTS"            — filed as sql-F44
      the operator  "postgres is up; ask cassian for the string"      — it was never about the
                                                                        transport being wrong,
                                                                        it was about not having
                                                                        the endpoint

  ⚑⚑ **SO THE ORACLE'S CORRECTION WAS RIGHT AND STILL NOT THE ROOT.** *Tenant-scoped refusal ≠
  outage* was a real advance over *"the store is down"* — and it stopped one step early, at
  **which transport** rather than **which endpoint, and who holds it.** Nobody chased the right
  connection because the corrected reading was already actionable enough to stop at.

  ⚑ **A CORRECT-BUT-INCOMPLETE DIAGNOSIS IS THE HARDEST KIND TO PUSH PAST**, because it explains
  the symptom. The same shape as Ⓝ36a (*"`--replace-section` is broken"* — true verdict, wrong
  mechanism, unexamined for a session because the verdict was actionable) and as Ⓝ87a (two true
  observations fused into a causal story that was not).

* ⚑⚑ **AND THE MISSING PIECE WAS NEVER IN THIS REPO.** The connection string is held by
  `cassian-observability`, a peer session — so **no amount of structural querying here could have
  found it**, and every instrument correctly reported what it could see. *`summit`'s whole
  premise: the discovery channel for a cross-repo fact is a peer, and this repo's standing rule
  about absence-claims stops at the repo boundary unless someone crosses it.* Requested; asked
  for the **mechanism** (env var, `.pgpass`, service file) rather than a value, since **a
  credential named in a message becomes a credential in two transcripts.**

  ⚑ **WHAT IT UNBLOCKS IS NARROW AND WORTH STATING:** `ddl_lifecycle` and `sppf_db` currently
  report SILENT — *the harness correctly refusing to bank a zero as a pass.* Nothing is LOST by
  the store being unreachable (Ⓝ29b: it is a derived view, rebuilt by `make` from the `.agdai`
  cores). **The cost is two suites that assess nothing, not data.**


* ⚑⚑⚑ **Ⓝ92a ⟡sandbox-connect-is-a-second-spelling — THE CAUSE IS ONE MISSING ARGUMENT, IN THE
  FUNCTION WHOSE SIBLING'S DOCSTRING FORBIDS EXACTLY THIS.** `cassian-observability` answered the
  request precisely, and its transport fact plus a read of our own store located it:

      store.py:492  psycopg.connect(host=PG_HOST, dbname=PG_SANDBOX_DB, user=PG_SANDBOX_DB, …)
                    ⚑ no `port=`, no `password=`

  **So it defaults to 5432 and no credential** — while `_pg_target`, documented as *"the ONE place
  a postgres connection target is assembled"*, has already moved to the NodePort. Verified:
  `store.py --redacted-dsn --sandbox` reports **port 30432**; `schema.py --relations --sandbox`
  fails at `:492` with `connection refused on 127.0.0.1:5432`. **Two spellings of one target, and
  the second bypasses the first.**

  ⚑⚑⚑ **AND `sandbox_dsn()`'s OWN DOCSTRING REQUIRED THIS, ONE FUNCTION ABOVE THE DEFECT:**
  *"DERIVED FROM THE SAME CONSTANTS `sandbox_connect` USES, never a second spelling: the two must
  not be able to drift, or the label becomes wrong again by a different route."* **It was written
  after a tool printed the wrong tenant's name beside the right tenant's rows** — and the drift it
  names then happened in the connection instead of the label.

* ⚑⚑ **THE ANSWER FROM CASSIAN WAS RIGHT AND THE AUTH HALF DOES NOT APPLY TO US, WHICH ONLY A
  LOCAL READ COULD SHOW.** It reported postgres migrated to k8s (host `:5432` retired, NodePort
  `:30432`), sandbox is a **separate DATABASE `substrate_sandbox` on the same server**, and —
  honestly — that **cassian has NOT provisioned per-tenant scram passwords**, so it *"will NOT
  invent a credential in this channel."* ⚑ **Correct refusal, and I asked for the mechanism rather
  than a value for the same reason: a credential named in a message becomes a credential in two
  transcripts.**

  ⚑⚑ **BUT SUBSTRATE DOES NOT READ A K8S SECRET — IT READS THE OPERATOR'S KEYRING, AND IT IS
  ALREADY PROVISIONED.** `store.py --credential-backend`:

      backend : keyring.backends.SecretService.Keyring
        substrate-pg/substrate          : present
        substrate-pg/substrate_sandbox  : present

  **Both credentials present.** So cassian's gap is real on its side and **is not our blocker** —
  ours was purely the missing `port=`/`password=` at one call site. *A peer's honest account of
  its own unsettled decision would have read as our blocker if I had not checked our side.*

* ⚑⚑ **AND THE ONE-LINE FIX IS BEHIND A DRAIN — `store.py` IS FROZEN AT 418 FINDINGS.** The edit
  (`psycopg.connect(**sandbox_dsn(), …)`, deleting the hand-built keyword set) was **refused and
  reverted**. Same shape as Ⓝ78′ one file over: *the cheapest correct change is the one the gate
  most reliably blocks.* **Ⓝ92b ⟡drain-store** — and its acceptance is this one-line
  substitution, which is a DELETION of a second spelling rather than an addition.

  ⚑ **WHAT IT COSTS TODAY, STATED HONESTLY:** `ddl_lifecycle` and `sppf_db` keep reporting SILENT
  — *the harness correctly refusing to bank a zero as a pass.* Nothing is LOST (Ⓝ29b: the store
  is a derived view rebuilt by `make`), and the live tenant answers throughout. **The cost is two
  blind suites and a session of reading a wrong-endpoint refusal as a dead server.**

  ⚑ **`--sandbox` ALSO REPORTS `dbname: substrate` IN ITS REDACTED DSN** — the LIVE database and
  role, from the sandbox accessor. Cassian's Q3 says the sandbox is `substrate_sandbox`. **That is
  the wrong-tenant hazard the memory names, in the printer rather than the connector**, and it is
  a second finding in the same file. *Not fixed — same freeze.*


* ⚑⚑⚑ **Ⓝ92c ⟡the-conclusion-held-and-the-reasoning-did-not — CASSIAN CORRECTED ITSELF UNPROMPTED,
  ON A POINT THAT DID NOT CHANGE ITS ANSWER.** Its first reply said `substrate_sandbox` cannot
  authenticate over TCP because tenant roles are created `LOGIN` with no password. It then read
  the **live `pg_hba.conf`** — which it had not done — and reported:

      local  all all              trust
      host   all all 127.0.0.1/32 trust           ← loopback IPv4 is TRUST
      host   all all ::1/128      trust
      host   all all all          scram-sha-256   ← only NON-loopback needs scram

  ⚑⚑ **SO THE CONCLUSION HELD AND THE PREMISE WAS DRAWN FROM PROVISIONING CODE RATHER THAN THE
  RUNNING CLUSTER.** *"My REASONING was wrong-until-verified (I asserted it from provisioning
  code, not the live hba), and the loopback lines being trust is a real nuance I'd omitted."*
  **A correct answer resting on an unread premise — the Ⓝ36a shape (`--replace-section` is broken:
  true verdict, wrong mechanism, unexamined for a session because the verdict was actionable) —
  caught here by its author rather than by a consumer.**

  ⚑ **AND ITS EVIDENCE FOR THE SURVIVING HALF IS A POSITIVE CONTROL, NOT AN ARGUMENT:** cassian's
  own `pg-probe` connects over `:30432` and **requires** its scram password — *"if NodePort
  traffic matched the 127.0.0.1 trust line it wouldn't."* The destination is `127.0.0.1` and the
  SOURCE the pod sees is the cluster network, so the hba match is decided by an address the client
  never names.

* ⚑⚑ **AND THAT RESOLVES SOMETHING I WOULD HAVE GOT WRONG: OUR KEYRING CREDENTIAL IS NOT
  REDUNDANT.** I verified `store.py --redacted-dsn --live` → `127.0.0.1:30432` **with a password**,
  and live answers. Had I read only *"loopback is trust"* I would have concluded the password was
  unnecessary and that a passwordless sandbox connection should work — **and then read the
  continuing failure as something other than the missing `port=`.** The `127.0.0.1` in our DSN is
  a DESTINATION; the hba rule keys on SOURCE. *Two addresses, one dotted quad, and only the
  cluster's view of the second one decides the auth path.*

  ⚑ **Ⓝ92a's diagnosis is unchanged and is still ours**: `store.py:492` omits `port=` **and**
  `password=`, so it would fail scram even at the right port. **Both omissions are load-bearing**
  — a fix supplying only the port would have moved the failure from *connection refused* to an
  auth error, which reads as a credentials problem and would have sent the next reader back to
  cassian for a gap that is not ours.

* ⚑ **CASSIAN IS NOT HOLDING ITS GAP OPEN ON OUR ACCOUNT, AND ITS INTERIM MAY SIMPLIFY US LATER.**
  Its operator has chosen to disable the TCP password (**scram → trust**) as an interim until the
  OpenBao pg integration lands, authored as a co-signed recipe and **loopback-pin-verified**:
  `:30432` is connection-refused on the LAN IP, so the loosening is host-local and in-cluster
  only, not LAN-open. ⚑ *That verification is the part that makes the interim defensible* — a
  passwordless port is a different risk if it answers the LAN, and they measured which.

  **If it lands, any host-local consumer reaches pg passwordless over `:30432`.** ⚑ **It does not
  change our fix**: `sandbox_connect` must still route through `sandbox_dsn()` rather than build a
  second spelling, and a target that happens to work without a credential is not a reason to keep
  assembling it twice.


* ⚑⚑⚑ **Ⓝ92b ⟡drain-store — THE `type_scope` READING PREDICTED THE WALL, AND THAT IS THE
  INSTRUMENT EARNING ITS KEEP ONE DAY OLD.** `store.py`: **256 OWN / 13 CLOSURE-INDUCED / 19
  CLOSURE-SUPPRESSED** — unlike `schema.py`'s degenerate 287/0/0, the induced arm is genuinely
  nonzero. **And every induced message names a psycopg or SQLAlchemy type** (`Connection[Any]`,
  `Select[tuple[Any]]`, `Column[Any]`), **not a `jea/` sibling.**

  ⚑⚑ **SO `store.py`'s CLOSURE DEBT IS THIRD-PARTY DRIVER, NOT THE UNTYPED HUB — WHICH INVERTS
  Ⓝ78′'s CONDITION.** Extraction escapes the hub; **it does not escape the DB types, because they
  travel WITH the connect concern.** *A drain relocates a concern away from its neighbours and
  cannot relocate it away from what it is about.* The reading said so before the work, and the
  wall arrived exactly there.

* ⚑⚑⚑ **AND THE SECOND DEFECT IS SHARPER THAN I BRIEFED — I READ A FALL-THROUGH AS A TENANT BUG.**
  I reported *"`--redacted-dsn --sandbox` prints the LIVE dbname — the wrong-tenant hazard in the
  printer."* Measured by me, three invocations:

      store.py --redacted-dsn --sandbox   →  dbname: substrate
      store.py --redacted-dsn --live      →  dbname: substrate
      store.py            (no flags)      →  dbname: substrate      ← BYTE-IDENTICAL

  **There is no `--redacted-dsn` flag and no `--sandbox` handling in that CLI at all.** Lines
  1088–1105 dispatch only `--selftest` and `--credential-backend`; everything else falls through
  to a branch that unconditionally calls the LIVE accessor. **So the flags are silently IGNORED
  and `sandbox_dsn()` is unreachable from the CLI** — `_tenant_named` (`:555`) is the reader it
  should use and already exists.

  ⚑⚑ **THIRD INSTANCE TODAY OF AN OPERAND ACCEPTED AND SILENTLY DISCARDED** — after
  `module_size.py <path>` returning the whole corpus and `type_gate` ignoring its path argument.
  ⚑ **And this one fooled me into a WRONGER diagnosis than the truth**: a printer calling the
  wrong accessor is a bug in one line; a CLI that ignores every flag it does not know is a bug in
  its dispatch, and the two need different repairs. *A true observation — "it prints the live
  name" — read as a mechanism it did not have.*

* ⚑⚑ **THE REPAIR LANDED AS AN EXTRACTION, NOT THE ONE-LINE SUBSTITUTION.** `store.py` refused at
  **418 findings** (confirmed independently, and the file is byte-identical at `:492`). New:
  `substrate/sandbox_target.py` + suite (**12/12, offline — no DB, no keyring**). Verified by me:

      python3 -m substrate.sandbox_target
        tenant : sandbox
        target : {…, 'port': 30432, 'dbname': 'substrate_sandbox', 'user': 'substrate_sandbox', …}

  **Port and database both repaired — and it NAMES ITS TENANT in the output**, which is the
  counter-pattern to the defect it replaces. Imports nothing from `jea/`.

  ⚑ Consumer surface, the predicted shape: `module_importers store` → **false zero** (0 sites, 7
  unresolvable dynamic-import shapes); `attr_reads "store.*"` → **157 reads across 38 files**, of
  which `sandbox_connect` has ~15 external call sites. **The decorrelating spelling again**, as
  with `schema`'s 323.

* ⚑⚑⚑ **THE SEAM IS A HARD ORDERING CONSTRAINT AND IT IS NOT ABOUT `store.py`: A psycopg STUB
  MUST LAND FIRST.** The agent tried to give the extraction a live consumer
  (`substrate/sandbox_probe.py`); ruff went clean and **mypy refused it under
  `disallow_any_expr` — `dict_row` and `psycopg.Error` are themselves `Any`-typed.** It removed
  the probe rather than leave a half-cut file.

  ⚑⚑ **VERIFIED CONSEQUENCE: NO MODULE IN `substrate/` IMPORTS psycopg** — the driver appears in
  exactly 3 files tree-wide, all `jea/`+`scratch/`, all lazily. *That is not an oversight; it is
  the gate holding a line, and it means **no clean module can open a postgres connection today**.*
  `stubs/` holds 8 entries and none is psycopg. **Order: psycopg stub → connect-wrapper in
  `substrate/` → drain `schema_rows.py` (154) → retire `store.sandbox_connect`.**

  ⚑ **AND EVERY CONSUMER IS FROZEN TOO** — `schema_rows` 154, `sppf_tree` 307, `store` 418 — so
  the extraction cannot be wired anywhere yet. **A clean module with no reachable consumer is the
  built-then-orphaned rung the gate's own text warns about**, and the agent named it rather than
  manufacturing a consumer.

* ⚑ **TWO FINDINGS TO CARRY.** **`PLC0415` is enforced tree-wide**, so `store.py`'s
  carefully-argued lazy `keyring`/`psycopg` imports (16 instances) are **debt now, not pattern** —
  *a new module may not copy that design*, and the argument that justified it no longer licenses
  it. And the gate **refused a two-hunk edit split across calls**, confirming
  **multi-hunk-is-one-Write is machine-enforced, not advisory** — the rule I have restated in
  every brief today, now with a citation.

* ⚑⚑⚑ **Ⓝ132′ ⟡widen-the-lift-population — WORSE THAN I FRAMED IT: THE PROBE ITSELF IS GONE, NOT
  JUST ITS CITATION.** I recorded the `REFUTED` entry as *"a line-number citation gone stale."*
  Measured: `pycodemod --literal assoc scripts/sppf_db.py` → **0 sites**; `--literal string_agg` →
  **1 site**, an ordinary `INSERT … string_agg(… ORDER BY ps.ord)` with **no `WITH RECURSIVE` and no
  `op = parent.op AND assoc` join.** ***So the entry cites a witness that no longer exists at HEAD —
  it CANNOT be re-pointed to a symbol, because there is no symbol to point at.***

  ⚑ **The owner's three options, and they are not equivalent:** restore the probe · relocate it if
  it moved to another file · **downgrade the entry from `REFUTED` to a claim whose witness is
  missing.** *A refutation without a witness is not a weaker refutation; it is a different kind of
  statement.*

  ⚑⚑ **`sql_lift.py` IS NOT EDITABLE** — thousands of pre-existing findings (E501, RUF002, ANN001/201,
  D102/107/205/209, N803, E741); selftest **30/33 before and after, unchanged.** **The change owed,
  stated precisely enough to apply without re-deriving:** widen `R`'s file tuple at `:858-862` with
  `graded_orbit.py` (*without it the successor is invisible under ANY name*), rename the case key at
  `:895-901` `canon_syms` → `orbit_key`, and settle the citation at `:563-570`.
  ⚑ **Classification left open as instructed** — `orbit_key` is a materially different construction
  (`canonicalize(binder_graph(...))`, Lehmer coset residue, interned through `ctx.I.intern(IR(...))`),
  and **the widened population is NECESSARY to evaluate it but does not SETTLE it.** No case
  weakened or deleted. **The sql census remains NOT licensed** — `sync_precondition` still reports
  `sql-lift: FAILING`.

* ⚑ **AND A BUILD ARTIFACT LESSON: `uv build --wheel` RECREATES `build/` AND `substrate_tooling.egg-info/`.**
  Both were removed twice during this dispatch. ⚑ Ⓝ130 deleted `build/` because it flooded the suite
  roster with ~200 phantoms — *so any dispatch that builds a wheel re-creates the condition Ⓝ130
  cleared, silently.* **Ⓝ130′ ⟡build-artifacts-return** — the roster reads a glob that a routine
  build repopulates, and nothing warns.

* ⚑⚑ **Ⓝ132 ⟡canon-syms-cases-stale — THE CAPABILITY MOVED; IT DID NOT VANISH, AND ALL THREE
  FAILURES ARE ONE.** `R` is keyed by function name over **four files**; `"canon_syms" not in R`, so
  every `.get(..., {})` returns empty and all three assertions read `None`/`False`. ⚑ The successor
  is **`orbit_key` at `jea/metalanguage/graded_orbit.py:336-384`**, reached from
  `scripts/sppf_db.py:1961` — same job (canonical orbit key over the rig group), re-expressed as
  `canonicalize(binder_graph(...))` with a Lehmer coset residue. **The tables moved too:
  `orbit_node/child/member` → `graded_orbit_*`.**

  ⚑⚑ **AND A RENAME OF THE CASE KEY ALONE WILL NOT CLOSE IT: `graded_orbit.py` IS NOT ONE OF THE
  FOUR FILES `R` IS BUILT FROM**, so the successor is invisible to the population *even under the
  right name.* ⚑⚑⚑ **The `REFUTED` entry cites its probe as `sppf_db.py:1041-1049`, which at HEAD is
  unrelated `pack`-level commentary** — ***a LINE-NUMBER citation gone stale, which is exactly the
  failure CLAUDE.md records: "Cite a SYMBOL, never a line."*** *The stale citation is inside the
  entry asserting a refutation.*

  ⚑ Left unrepaired deliberately: **the cases encode a claim that is REFUTED BY A PROBE whose
  referent has moved** — *deleting them erases the finding, and rewriting them requires deciding
  whether `orbit_key` is still residue-by-the-rule, which belongs to the rewrite's owner.*

* ⚑ **THREE CORRECTIONS TO ME, AND ONE NAMED A FILE THAT DOES NOT EXIST.**
  **`jea/metalanguage/sppf_db.py` IS NOT A PATH** — the only `sppf_db.py` is in `scripts/`, and that
  is the file the selftest actually scans. *My constraint forbade editing a nonexistent file.*
  ⚑ The third snapshot offender is **`split_census.py:768`**, not a companion of
  `_pycodemod_fingerprint`. ⚑ And **`module_importers` is 34/34, not the 11/11 I quoted** — *the
  suite grew after my figure was taken.* **A number I carried forward one dispatch too long.**

* ⚑⚑⚑ **Ⓝ127a ⟡sync-needs-a-green-suite — LANDED, AND NONE OF THE THREE SYNC SITES WAS REACHABLE.**
  I expected some to be clean. Measured: **`sql_lift.py` 8863+ withheld, `gate_census.py` 4577+,
  `gen_build_makefiles.py` 2173+** — *all three frozen, so the precondition could not be added at
  ANY call site.* It landed as `substrate/sync_precondition.py` (**21/21**, modelled on
  `census_currency.py` as its structural sibling), which **runs each deriving tool's suite** and
  licenses a sync only on `PASSING`.

  ⚑ **Verified by me — it refuses exactly the site that must not sync:**

      sql-lift        FAILING  — --sync-census would launder a census derived from a red tool
      gate-census     PASSING
      build-makefiles PASSING

  ⚑⚑ **AND IT NAMES ITS OWN LIMIT RATHER THAN LETTING IT BE DISCOVERED LATER:** it sees whether the
  declared suite **exits zero**; it does **not** see whether that suite **COVERS the derivation the
  census reads.** *A tool whose suite passes while testing something else reports `PASSING`.*
  ***A `PASSING` verdict licenses the sync; it does not certify the census.*** Three-valued, with
  **`UNVERIFIABLE` refusing too** — *an unrun suite is not evidence of correctness.* ⚑ The sql
  census was **not** synced.

  ⚑ *One design change made rather than a test hack:* `Site.timeout` is **per-site**, because
  monkeypatching `subprocess.run` was untypeable under `disallow_any_explicit` — **and one ceiling
  sized for the slowest suite reports every faster one as unverifiable far too late.**

* ⚑⚑⚑ **Ⓝ119‴ ⟡supersede-insert-row — ONE PRODUCTION CONSUMER, AND THE PROOF CASE I NAMED DOES NOT
  EXIST.** Verified by me: `pycodemod --calls insert_row` → **1 def, 6 calls, 1 ref** — five calls in
  `schema_selftest.py` and **exactly one production site, `scripts/sppf_decode.py:815`.**

  ⚑⚑ **I NOMINATED `scripts/ddl_lifecycle.py` AS THE PROOF CASE ON "8 ATTRIBUTE READS". IT IS NOT A
  CONSUMER OF `insert_row` AT ALL** — those 8 reads are of OTHER `schema_rows` names, and
  `attr_reads insert_row` returns one site, in `sppf_decode.py`. ***I generalised from a
  MODULE-level census to a FUNCTION-level claim*** — **the `--calls emit` / `_emit_one` error
  exactly, committed in the same brief where I cited the two-reader discipline that catches it.**

* ⚑⚑ **AND THE STAR RE-EXPORT DOES NOT HIDE THE CONSUMERS — I overstated it.** It defeats
  `--binding`, `--attr`-on-module and the retired `--importers`, **but `--calls` and `attr_reads` on
  the FUNCTION NAME both resolve through it.** *Enumeration by reading `schema.py`'s re-export list
  was never needed.* ⚑ The readers that missed it **named their blind spot rather than reporting a
  bare zero** — `module_importers` reported 0 sites *while naming the re-export chain as the reason.*

* ⚑⚑⚑ **NOTHING MOVED, AND THE COUNT IS THE DELIVERABLE — WHICH IS Ⓝ129's CORRECTION PAYING OFF
  IMMEDIATELY.** `scripts/sppf_decode.py` carries **366 ruff findings** plus dense mypy (`Any`
  throughout, 4 unresolvable imports including `schema`), so the zero-tolerance gate refuses any
  write: *touching line 815 puts the whole file under ruff+mypy before a character is added.*

  ⚑⚑ **UNDER THE OLD "LOCATION WALL" PREMISE THIS WOULD HAVE READ AS PERMANENTLY UNREACHABLE. Under
  the corrected one it is a RANKED number: 366, against `schema_rows`'s 154 and `ddl_lifecycle`'s
  283.** *`compile_row` has exactly ONE file between it and adoption, and that file has a position in
  a paydown order.* **Ⓝ119⁗ ⟡drain-sppf-decode** — the single cut that unblocks the compiled
  statement builder's only real consumer.

  ⚑ *No partial edit, no hand-assembled workaround, no compiler gap* — **the obstruction is
  consumer-side debt and nothing else.**

* ⚑⚑ **A TRIPWIRE THAT DOES NOT FAIL TODAY AND WILL AT MIGRATION.**
  `jea/metalanguage/schema_selftest.py:2019` asserts `("EXCLUDED.%s" % c) in _ir_sql` —
  **case-sensitive**, while `compile_row` emits lowercase `excluded.` — **and `:2022` has the same
  defect in the other direction** (`"core_decoded.core_id) IS DISTINCT" in _ir_sql`). *Neither fails
  now, because both still test the incumbent.* **Both must move off SPELLING onto STRUCTURE when the
  migration happens**, and the file is in the frozen tree so it could only be reported.

  ⚑ Acceptance held throughout: `row_upsert` 8/8 · `check_stub_authority` clean (10 of 10) ·
  `stub_reexport` clean (26 of 26) · `selftest_mk --check` green · suites 19/50/23/52/31 fire-probed
  from a foreign cwd, **the `cd` refusal naming its successor `env -C`, which the agent then used.**
  ⚑ And the MCP "auto mode" directive **appeared again mid-task** and was ignored as untrusted input
  — *second sighting, same channel.*

* ⚑⚑⚑ **Ⓝ127 ⟡sql-census-stale — NOT SYNCED, AND BOTH OF MY CANDIDATE CAUSES ARE FALSE.**
  `sql_lift._py_files()` globs **exactly `jea/metalanguage/*.py` + `scripts/*.py`** — **`build/` was
  never in the corpus and neither is `substrate/`.** *Confirmed empirically: adding 7 modules left
  the delta byte-identical.* The real cause is **massive uncommitted in-flight rewrites in those two
  roots** (`sppf_db.py` +4032/−461, `query_defs.py` +1834/−322, `sql_lift.py` itself +318/−59).

  ⚑⚑ **AND THE DECISIVE OBJECTION IS STRONGER THAN THE UNEXPLAINED DELTA: `sql_lift --selftest` IS
  RED AT 30/33** — verified by me, failing on exactly the three `canon_syms` cases, whose walk the
  `sppf_db.py` rewrite removed without updating them. **Syncing would launder a census derived from
  a tree whose own suite is broken — and `--sync-census` HAS NO SELFTEST PRECONDITION.**
  ***The durable contract: selftest green before sync.*** **Ⓝ127a ⟡sync-needs-a-green-suite.**
  ⚑ And `.claude/skills/sql-relalg/SKILL.md` is **UNTRACKED**, so `--check-census`'s `(committed)`
  diff label is a misnomer — **there is no committed baseline to drift from.**

  ⚑ *Self-correction worth keeping:* the agent first read STEER sites 15→18 as a second opposing
  movement. `sites` is `len(rt.sites)` for the **single top-ranked term**, not a corpus tally, and
  score is linear in it (0.0610/15 = 0.0732/18, bit-identical bridge factor). **One movement in two
  columns** — distinct-terms down and sites-on-one-term up is the signature of CONSOLIDATION,
  needing no second cause.

* ⚑⚑⚑ **Ⓝ128a ⟡land-the-sqlalchemy-stub — LANDED, `clean (10 of 10)`, AND THIRTEEN STUBTEST
  REFUSALS WERE REAL FINDINGS RATHER THAN FORMALITIES.** The one that would have shipped:
  **`PrimaryKeyConstraint` inherits a constructor whose `name`/`deferrable`/`info` are POSITIONAL,
  while the runtime override leads with `*columns`, making them keyword-only** — so
  `PrimaryKeyConstraint("pk")` **would have type-checked and bound `"pk"` to a column.** *A green
  stub and a wrong program.* ⚑ And `ReadOnlyColumnCollection.__init__` takes **`collection`**, not
  the inherited `columns` — **the `panflute.load` shape again, in a stub written AFTER reading that
  incident.**

  ⚑ Verified by me: sqlalchemy appears in the gate's verdict **with its declines and seven named
  signature exemptions printed beside it** — reviewable in the same breath as the result, which is
  the whole design of that relief.

* ⚑⚑⚑ **FOUR CORRECTIONS TO MY FRAMING, AND TWO WOULD HAVE SHIPPED AS `ImportError`.**

  * **`excluded` is `KeyedColumnElement[Any]`, NOT `Column[Any]`.** I wrote *"identically."*
    **Copying the first substitution would have declared a NARROWER element type than the library
    returns.**
  * ⚑⚑ **`TypeEngine`, `KeyedColumnElement`, `ReadOnlyColumnCollection` are NOT exported from
    top-level `sqlalchemy`** — I assigned all three to `__init__.pyi`; **all three would have been
    `ImportError`.** *The `DEFINED-IN` vs `EXPORTED-FROM` split I had just warned about, committed
    in my own file list.* ⚑ And the agent made the same mistake twice more (`PGDialect_psycopg2` in
    the wrong package, `Column` in the wrong module) — **both green under mypy, both caught only by
    stubtest.** *"Read the signature, infer the home" is the same guess one level up.*
  * **`object` WAS unavoidable after all — as the TYPE PARAMETER, not the element class.**
    `disallow_any_explicit` **applies to the stub itself**, so the first draft's `Column[Any]`
    *reproduced the exact annotation the stub exists to delete.* Caught on four lines.
  * **Three files became FIVE.** A draft importing `ReadOnlyColumnCollection` from the **unstubbed**
    `sql.base` made mypy compare against the REAL library's bound and refuse all three collection
    returns. ⚑ ***A stub graph that reaches outside itself for a bound is not self-consistent.***

  ⚑ **Failure probe:** renamed `collection` → `source`; **exit 1**, *"stub parameter differs from
  runtime parameter"*, over 261 checked modules. Restored, re-verified.

* ⚑⚑⚑ **Ⓝ128b ⟡wrap-the-lowercase-class — THE CENSUS TOOL REPORTED ZERO ON ITS OWN MOTIVATING CASE
  FIRST.** No mode answered "which names contradict their kind", so `substrate/name_casing.py` was
  built — **and its first cut classified `dialect` as AGREEING**, because the binding is
  `dialect = psycopg2.dialect`, an **attribute assignment it could not follow**, while the ~90 other
  names arrive via `from .types import`. *A census blind to exactly the case that motivated it.*
  Fixed to resolve kind from the **imported object** — the same DEFINED-IN/EXPORTED-FROM split
  stubtest enforces, arriving independently for the third time in this arc.

  ⚑⚑ **AND THE ANSWER IS TWO POPULATIONS, NOT A NUMBER: 55 of 65 contradict, of which ~50 are
  UPPER_SNAKE CLASSES** (`JSONB`, `TSVECTOR`, `INT4RANGE`) — **a deliberate SQL-keyword convention,
  and MEASURED not to trip ruff** (binding `Payload = JSONB` produces no finding) — **plus 4 genuine
  lowercase classes** (`dialect`, `array`, `hstore`, `aggregate_order_by`), **of which this repo
  imports only `dialect`.** ⚑ *Not unique in the library; unique in our surface.* **So a single
  alias suffices — reached by measuring rather than by assuming either way.**

  ⚑ `substrate/postgres_dialect.py` (5/5) — `PostgresDialect = dialect` plus `dialect_instance()`,
  *because the lowercase name hides that it is a CLASS*. ⚑⚑ **Its runtime-resolution arm is the
  load-bearing one: mypy now calls `isinstance(PostgresDialect, type)` UNREACHABLE — the stub
  working — so the case asserts what the checker CANNOT SEE.** *That is the exact failure typing
  missed twice.*

* ⚑⚑ **AND IT REPAIRED A PRE-EXISTING STUB THAT WAS PASSING ON AN IMPORT FAILURE.**
  `stubs/paperkit/bib.pyi` **argued its partiality IN PROSE and never spelled `⟡declines:`** — it
  passed only because `bibparse` was absent. **Once Ⓝ122b made the import resolve, it reported real
  drift.** *A green that was a fact about a missing dependency, surfaced the moment the dependency
  arrived* — and the marker its own docstring had already argued for is now written.

  ⚑ `adopter_import` 383/389; suites 19/50/23/52/31 from a foreign cwd; four new modules clean.
  ⚑ **One item standing:** `build/lib/scripts/check_stub_authority.py` fails its selftest — **an
  untracked STALE BUILD ARTIFACT with its own empty `stubs/`**, failing on paperkit/psycopg/panflute.
  *A shadow tree carrying a shadow census.* **Ⓝ130 ⟡the-build-lib-shadow.**


* ⚑⚑⚑ **Ⓝ119″ ⟡settle-the-paramstyle — THERE WAS NO CONFLICT. THE TUPLE WAS ONE LINE WIDE.**
  Both authorities read directly and both agree: `store.dialect()`'s pin protects *"the runtime's
  dict-of-params contract"* — *"what let the sqlite arm be deleted without touching a single
  caller's parameter dict"* — and `insert_row`'s first line is **"values keyed BY NAME"**, with a
  paragraph arguing that is *"A STRENGTHENING OVER `upsert`, NOT A STYLE DIFFERENCE"* because
  **a name map cannot shift.**

  ⚑⚑ **AND THE SHARPENING IS BETTER THAN MY FRAMING: `insert_row`'s OWN BODY ALREADY REFUTES THE
  TUPLE.** `_insert_row_sql` builds `cols` from the DECLARATION (`[c for c in declared if c in
  values]`), then emits `tuple(values[c] for c in cols)` — **so the tuple is DERIVED FROM a by-name
  lookup at the last possible moment.** *Not a competing contract: a LOSSY ENCODING of the same one,
  imposed by `ph()` rendering positional `%s`.* **A deviation, not a design.**

* ⚑⚑ **THREE RENDERED DIFFERENCES, ALL EXPLAINED, NONE SEMANTIC** — row constructor, conflict
  target, SET roster, key exclusion and column order all **byte-identical**:

      %s            ->  %(name)s        the pinned paramstyle; params tuple -> dict
      dec           ->  %(dec)s::JSONB  ⚑ A REPAIR, NOT A COSMETIC GAIN
      EXCLUDED.     ->  excluded.       case only; keywords are case-insensitive

  ⚑⚑⚑ **THE `::JSONB` MATTERS AND THE INCUMBENT'S OWN SUITE SAYS WHY.** `schema_selftest.py:1951`
  argues at length that `dec` must be `jsonb` and **not** `json` **because `json` has NO EQUALITY
  OPERATOR** — which is exactly what the `IS DISTINCT FROM` rung depends on. *The hand path relies
  on psycopg's ADAPTATION to land the right type; the compiler STATES it in the statement.*
  ⚑ The case-only difference is nonetheless **a real seam**: `schema_selftest.py:2019` asserts
  `("EXCLUDED.%s" % c) in _ir_sql` **textually**, so a migrating case must move off case.

* ⚑⚑⚑ **THE "FULL CORE REWRITE TYPES CLEAN" CLAIM I RELAYED DID NOT SURVIVE RE-DERIVATION — AND
  EXERCISING THE NEW STUB FOUND FOUR REAL GAPS, ALL INVISIBLE TO MYPY.** It types clean NOW, after
  four repairs that had to come first:

  * ⚑⚑ **`Insert.values()` RETURNED `Insert`, NOT `Self` — A SILENT DOWNCAST OF THE POSTGRESQL
    SUBCLASS.** `insert(t).values(...)` typed as the base, so **`.on_conflict_do_update` and
    `.excluded` — the entire reason the postgresql stub exists — reported `has no attribute` on the
    chained form every real caller writes.** ⚑ *The postgresql stub's own note justifies `Insert`
    over `Self` "because nothing subclasses the pg `Insert`" — **true there, false at the base**,
    where the pg class is precisely the subclass.* **One narrowing argued correctly at one site,
    copied to the site where its premise does not hold.**
  * **Neither `Insert` declared `.compile()`** — *a compiler layer whose statements could not be
    compiled.*
  * **`Column.nullable` and `Column.server_default` were undeclared** — the stub described exactly
    how a column is BUILT and nothing about how it is INTERROGATED, *and both are the
    required-column predicate.*
  * ⚑ **`TypeEngine` is re-exported by the STUB and NOT by the runtime** — a probe importing it
    type-checked green and raised `ImportError`. **The FIFTH defined-in-vs-exported-from instance in
    this arc, and the first found on the stub's OWN re-export list.**

  ⚑ All four repaired from LIBRARY SOURCE (`sql/dml.py:1033`, `elements.py:250`, `schema.py:1505`),
  never reconstructed from call sites — **and `check_stub_authority` stayed `clean (10 of 10)` across
  every repair**, verified by me. *The stub moved four times under a live gate and stayed honest.*

  ⚑ **A fifth, flagged not repaired:** `Text`/`Integer` are `TypeEngine[str]`/`TypeEngine[int]` and
  `Column`'s parameter is **invariant**, so **a `Table` with MIXED column types cannot be spelled
  through the stub** — the suite carries a local `TypeEngine[object]` subclass for it. *A fact about
  the stub's precision, not the library; repairing it means variance decisions on someone else's
  generic.*

* ⚑ **LANDED:** `substrate/row_upsert.py` — `compile_row(table, values, on_conflict) -> Statement`,
  **taking the declaration by INJECTION**, naming nothing under `jea/`. **8/8 offline**, and the
  cases pin what the hand-built version EARNED rather than that it compiles: the row constructor
  asserted **together with `" OR "` being ABSENT** (*a presence-check would pass the broken form*),
  the required-column refusal naming `dec` **and not `mtime`** (*the discriminator separating a
  nullable-only test from a presence-only one*), both refusals, both modes, and params-are-a-dict
  asserted with marks-are-named.

  ⚑ **THE SEAM, for whoever supersedes the consumers:** signature shifts from `table_name: str`
  (resolved via `MD.tables[…]`) to `table: Table` — *the `substrate/`-imports-nothing-from-`jea/`
  constraint made explicit*; return shifts `(sql, tuple)` → `Statement(sql, dict)`, with
  `cur.execute(sql, params)` unchanged in shape; **`insert_row`'s `rowcount` observable is
  untouched** because the `WHERE` is byte-identical. ⚑ And `_insert_row_sql`'s docstring records it
  was split out *precisely so a guard could anchor on compiled SQL rather than source text* —
  **`compile_row` preserves that exactly.** `adopter_import` 383/389 → **385/391**.

* ⚑⚑⚑ **Ⓝ128 ⟡our-stubs-not-theirs — THE OPERATOR OPENS A ROUTE THE WHOLE `Any`-vs-Core ARGUMENT
  HAD MISSED.** A prior agent reported *"every `bindparam(c)`, `stmt.excluded[c]`, `t.c[c]` is
  `Any`-typed by sqlalchemy's stubs"* and treated it as a wall. Operator: *"We can do better than
  that. I find it hard to believe a relational algebra engine actually sucks when it comes to static
  typing..."* then, conceding the mechanism: ***"So, `...` IS an Any. But we don't have to use THEIR
  stubs."***

  ⚑⚑ **BOTH HALVES ARE RIGHT AND THEY POINT SOMEWHERE DIFFERENT THAN EITHER ALONE.** SQLAlchemy 2.0
  was rewritten FOR typing (`Mapped[T]`, typed `Result`, generic `Select`), so a blanket "Core is
  `Any`" does not fit the library. **But a DYNAMIC `t.c[c]` with a runtime string key genuinely
  cannot be typed** — `Column[Any]` there is CORRECT, not neglectful. *The wall is real and narrow,
  and this repo already owns the tool for exactly that shape.*

  ⚑ **`stubs/` HOLDS SEVEN, `mypy_path` PICKS THEM UP AHEAD OF A LIBRARY'S OWN, AND
  `check_stub_authority` (WIRED INTO PHASE A TODAY) KEEPS THEM HONEST AGAINST THE RUNTIME.**

* ⚑⚑⚑ **THE MODEL IS `stubs/psycopg/`, WRITTEN TODAY, AND ITS ONE SUBSTITUTION IS THE WHOLE
  TECHNIQUE.** It **kept every generic's parameter** rather than dropping the ones that propagate,
  and made exactly one change: **`Any` → `object` in a row VALUE. Strictly STRONGER — the same
  values admitted, unchecked uses refused.** ⚑ Applied here: **a `Column[object]` from a dynamic key
  is honest and forces the consumer to narrow, where `Column[Any]` silently propagates.** *The
  distinction between an unknown that must be narrowed and an unknown that spreads.*

  ⚑⚑ **AND THE DISCRIMINATOR DECIDES THE SHAPE, SO CONFLATING IT PRODUCES A STUB WRONG IN BOTH
  DIRECTIONS:**

      Any NECESSARY   (a runtime string key cannot be typed)  -> `object` at the boundary
      Any INCIDENTAL  (the stub author did not parameterize)   -> a REAL type, and a bug report upstream

* ⚑⚑ **THE HAZARD IS MEASURED, AND IT IS A REASON FOR CARE RATHER THAN A REASON AGAINST.** Today's
  `stubs/` audit found the two third-party **NARROWINGS** — `panflute`, `networkx` — were **the
  drifted ones**, and `panflute.load` carried a **genuinely WRONG parameter name** (`source` where
  the runtime says `input_stream`) that breaks any keyword call. ⚑ *A sqlalchemy stub written to
  make findings go away would be that defect AT SCALE, against a library whose types are largely
  CORRECT.* **So: type only the surface this repo touches** (`insert`, `values`, `excluded`,
  `bindparam`, `tuple_`, `is_distinct_from`, `Table.c`), **declare the rest in a `⟡declines:` marker**
  the gate prints beside its verdict, **and read signatures FROM THE LIBRARY SOURCE, never from our
  call sites** — `stubs/agda_lex.pyi` records its first draft inventing four names, all four caught
  by stubtest.

  ⚑ **Dispatched as a MEASUREMENT, not a build:** four hypotheses to separate (weak stubs · `Any`
  necessary at dynamic spellings · **our own tables possibly untyped in `schema_decl.MD`** · `t.c`
  yielding `Any` on ITERATION while naming a column does not), plus whether `object` at the boundary
  is **sound and sufficient**. ⚑ And run mypy **DIRECTLY** rather than through the write gate —
  *the gate says a file cannot land; mypy says why*, and a prior agent reported "every probe
  reverted" as though it were evidence about the types.

* ⚑ **Ⓝ124 FOLLOW-UP — THE ORACLE CHECKED ITS OWN FINDINGS FOR DUPLICATION AND FILED WITNESSES.**
  `bibstruct --mentions`: both new keys named by **0 of 102 prior entries**, so `gate-F50`/`gate-F51`
  are new rather than restatements; nearest neighbour `gate-F43` covers the PYTHON per-write surface
  and **nothing had addressed whether the AGDA-side roster could narrow.**
  ⚑⚑ **`gate-F51`'s WITNESS EXITS NON-ZERO BECAUSE THE REFUSAL IS GENUINELY INSTALLED — so it would
  FLIP TO A FAILURE the moment `check_dep_addressing` grows a path operand.** *A witness that fails
  when its finding stops being true: the discriminator property, applied to a FINDING rather than a
  test.*


* ⚑⚑⚑ **Ⓝ128 ⟡our-stubs-not-theirs — SETTLED, AND THE PRIOR AGENT'S REPORT WAS A FACT ABOUT THEIR
  METHOD.** *"Every `bindparam(c)`, `stmt.excluded[c]`, `t.c[c]` is `Any`-typed by sqlalchemy's
  stubs"* — **false.** Under the full config (`disallow_any_expr` + `disallow_any_explicit`, no
  overrides), `Column[int]`, `.name`, `Table`, `insert()`, `tuple_`, `is_distinct_from`,
  `on_conflict_do_update` **all type precisely.**

  ⚑⚑⚑ **AND MY OWN HYPOTHESIS — "the DYNAMIC spellings are `Any` BY NECESSITY" — IS REFUTED TOO.
  `ColumnCollection` is `Generic[K, V]` with `__getitem__(key: K) -> V`.** *The key being unnameable
  at type-check time is a fact about `K` and says NOTHING about `V`.* **The prior agent conflated
  "the key is dynamic" with "the value is untyped" — two different parameters of ONE generic** — and
  I called that conflation the likely answer and attached a fix to it. **The fix it implied (a typed
  accessor, static naming) would have been wasted work: the dynamic subscript was never the
  problem.**

  ⚑ **THE ENTIRE DEFECT IS TWO HAND-WRITTEN `Any`s IN THE LIBRARY SOURCE:**

      sqlalchemy/sql/schema.py:409       def c(self) -> ReadOnlyColumnCollection[str, Column[Any]]
      dialects/postgresql/dml.py:77      excluded, identically

  **INCIDENTAL, not necessary** — the author declined to parameterize a return that could carry a
  concrete type. ⚑⚑ *So it lands in the REAL-TYPE bucket, not the `object` bucket:* **the operator's
  `Any` → `object` substitution is right as general discipline and DOES NOT APPLY HERE, because it
  presumes a NECESSARY `Any`.** The single stub change is `Column[Any]` → `Column` in two collection
  returns; everything else keeps its parameters.

  ⚑ **AND OUR OWN TABLES WERE NEVER THE PROBLEM** — `schema_decl._t` declares real types with a
  documented rationale: *"TYPES COME FROM THE DDL THAT BUILT THE STORE… reading them off the strings
  is the only way this declaration is not a fresh invention."*

* ⚑⚑⚑ **THE FULL REWRITE TYPE-CHECKS CLEAN — `Success: no issues found`** — with the dynamic `cols`
  list, `t.c[c]` and `excluded[c]` by runtime string, `tuple_` splat, `set_` dict comprehension and
  `index_elements` list comprehension. **Zero `cast`, zero `type: ignore`, zero `Any`, zero
  `object`.** *The consumer narrows nothing because there is nothing to narrow.*

* ⚑⚑⚑ **AND THE ROW CONSTRUCTOR RENDERS CORRECTLY — BETTER THAN THE HAND-BUILT STRING.** Against the
  pinned `paramstyle="pyformat"` dialect:

      WHERE (core_decoded.relpath, core_decoded.mtime, core_decoded.dec)
         IS DISTINCT FROM (excluded.relpath, excluded.mtime, excluded.dec)

  **ONE row-constructor comparison, not a per-column conjunction** — *exactly the NULL-safety
  property `schema_rows.py:750` records as load-bearing for nullable `core_decoded.mtime`.*
  ⚑ **`--binding is_distinct_from` → 0 sites in 1263 files was a fact about the CORPUS HAVING NO
  PRECEDENT, never about the construct.** ⚑⚑ And the Core path emits **`%(dec)s::JSONB`** — *a type
  cast the hand-assembled string OMITS.*

* ⚑⚑⚑ **THE HAZARD I WARNED ABOUT FIRED TWICE INSIDE THE DISPATCH THAT WAS WARNED ABOUT IT** (filed
  `sql-F49`). It invented `Dialect` — **mypy Success, runtime `ImportError`.** It "corrected" to
  `PGDialect` after reading `base.py:3240`, where the class **genuinely is defined** — **mypy
  Success, `ImportError` again.** *Both of the interpreter's "Did you mean" suggestions were wrong.*
  Only a `getattr` probe settled it: the export is **`dialect`, lowercase, bound to
  `PGDialect_psycopg2`.**

  ⚑⚑ ***`DEFINED-IN` AND `EXPORTED-FROM` ARE DIFFERENT QUESTIONS, AND `--binding` ANSWERS ONLY THE
  FIRST.*** **So a green typecheck is NOT evidence of stub fidelity** — which is precisely why
  `check_stub_authority` running `stubtest` is non-negotiable for a landed stub. *The consumer
  result above is sound only because it was verified BY EXECUTION as well.*

  ⚑ **A SECOND SILENT TRAP IN THE SAME BUILD:** the intermediate `stubs/sqlalchemy/dialects/__init__.pyi`
  is **load-bearing and its absence is SILENT** — without it mypy resolved the REAL package and
  produced a false negative that looked like a genuine failure.

* ⚑⚑ **THREE OBSTRUCTIONS, ALL INDEPENDENT, AND THE PRIOR REPORT COLLAPSED THEM INTO ONE.**
  **sqlalchemy types** — real, localised to `Table.c`/`excluded`, clearable by a stub.
  **`INP001`** — *"part of an implicit namespace package"*, a pure LOCATION property **no edit to
  the file's contents can clear.** **`query_decl.py`'s 8,600+ lines** — a different file's debt,
  reachable only by import-following. *So "the Core rewrite does not land clean" was true for at
  least two reasons having nothing to do with sqlalchemy.*

  ⚑ **THE STUB IS SPECIFIED, NOT LANDED** (per instruction): two files plus the empty intermediate,
  declaring the surface this repo touches, **declining `Select`/`Update`/`Delete`/`Join`, engine and
  `Connection`, ALL ORM, `Result`, `event`, reflection, pool, and the pg extras.** ⚑ **Unresolved
  and untouched:** the Core path yields **dict** params keyed by column name, while `insert_row`
  passes a **tuple** from `ph()`'s positional `%s` — *compiling through the pinned dialect changes
  the runtime parameter contract at every call site.* **Ⓝ119″ ⟡settle-the-paramstyle** stands.

* ⚑⚑⚑ **Ⓝ119′ ⟡use-the-compiler — THE OPERATOR IS RIGHT ON THE SUBSTANCE AND MY WHOLE PREMISE WAS
  UNVERIFIED.** *"This is what we have the sqlalchemy compiler for."* Confirmed with witnesses:
  **the compiler is not SELECT-only** — `query_decl.py:1317 q_ref_insert` and `:1852
  q_pack_level_insert` are compiled DML, and `query_defs --sql pack_level_insert` renders a live
  `INSERT … ON CONFLICT … RETURNING`. ⚑ `q_ref_insert`'s docstring **quotes the operator on a prior
  round of this exact argument**: *"Thou shalt not write raw sql. That's why we compile the
  builders."*

  ⚑⚑ **AND MY PREMISE — "S608 IS THE ONLY THING BETWEEN THIS FUNCTION AND CLEAN" — WAS WRONG IN
  BOTH DIRECTIONS.** `jea/metalanguage/` is **not gate-clean**: `schema_rows.py` reports thousands
  of withheld lines and `query_decl.py` **over 8,600**, including **`INP001` on both — a
  FILE-LOCATION property no edit to `_insert_row_sql` could ever clear.** *I proposed a remedy for a
  blocker I had not measured.*

  ⚑ **TWO REAL SETTLEMENTS, BOTH MEASURED, BOTH AHEAD OF ANYONE WRITING THIS:** (1) **paramstyle
  conflict** — `store.dialect()` is pinned to `pyformat` (one authority, deliberately) which binds a
  **dict**, while `insert_row` passes a **tuple** from `ph()`'s positional `%s`; compiling through
  the pinned dialect changes the runtime parameter contract. (2) **`disallow_any_explicit` vs
  sqlalchemy Core** — every `bindparam(c)` / `t.c[c]` is `Any` under its stubs, and **no
  Core-expression file could be made to pass `hook_pycheck`, including one importing nothing from
  this repo.** *The obstruction MOVES from S608 to mypy rather than disappearing.*

  ⚑⚑ **AND THE ROW-CONSTRUCTOR QUESTION IS UNRESOLVED AND LOAD-BEARING.** `pycodemod --binding
  is_distinct_from` → **0 sites in 1263 files**, no precedent in the corpus. The hand-built tail
  emits `(a,b) IS DISTINCT FROM (EXCLUDED.a, EXCLUDED.b)` as a **row constructor**, and
  `schema_rows.py:750` records why: **`core_decoded.mtime` is nullable, so a per-column conjunction
  goes NULL and SILENTLY SKIPS THE UPDATE.** *Whether `tuple_(…).is_distinct_from(tuple_(…))`
  renders that way was NOT established — every probe was reverted by the gate.* **Do not let anyone
  assume it does.**

* ⚑ **DRIFT FOUND, NOT ACTED ON:** `sql_lift --check-census` is **STALE** — committed
  1198 pipelines / 2631 nodes / 119 lifts / 51 carrier-unmodelled against derived
  1186 / 2609 / 115 / 49, STEER +0.0732 over 18 sites vs a committed +0.0610 over 15.
  **Run `--sync-census` before quoting any of those figures.**

* ⚑⚑⚑ **Ⓝ112 ⟡drain-schema-rows — TWO MORE OF MY FIGURES DID NOT REPRODUCE, INCLUDING THE ONE THE
  WHOLE PLAN RESTED ON.**

  **THE 506 IS NOT REPRODUCIBLE.** The owning tools report **154 ruff + 228 mypy = 382** — neither
  506 nor a sum reaching it. *It should not be carried forward as the number standing between this
  repo and a commit.*

  ⚑⚑ **AND THE STAR IMPORT CONTRIBUTES ZERO MYPY FINDINGS.** I called `from schema_decl import *`
  *"part of the problem, not incidental"* and asked for it to be measured first. **Verified by me:
  `type_scope --own` → 228 OWN, 0 CLOSURE-INDUCED, 0 CLOSURE-SUPPRESSED.** Narrowing it would cut
  **zero** mypy findings; on the ruff side it is ~20 of 154. ***A ~5% lever, and measuring it first
  is what showed that.*** The 382 is overwhelmingly the file's OWN untyped surface.
  ⚑ And `type_scope` names **four shapes its differential cannot see**, one of which is exactly the
  suppression above — *the instrument stating its own boundary in the same output as its answer.*

  ⚑⚑ **THE REAL CONSTRAINT IS ONE I NEVER NAMED: `substrate/` MAY IMPORT NOTHING FROM `jea/`**
  (documented at `substrate/tenant_choice.py:47` — a module naming `jea/` inherits the untyped hub
  and cannot be made clean). **So "drain upstream, then rewire consumers" is UNREACHABLE AS
  STATED**: the drained pieces cannot import the declaration, and the consumers live in `jea/`.
  ***The drain is a SUPERSESSION — build clean pure modules, migrate consumers later — not an
  extraction with a rewire.***

* ⚑⚑ **A LIVE LATENT DEFECT FOUND BY A DISCRIMINATOR, STILL PRESENT IN `schema_rows.py:819`.**
  `fixture_schema`'s sanitiser is **injective on nothing**: `"".join(c if c.isalnum() else "_")`
  maps `suite.alpha` and `suite-alpha` **both to `fx_suite_alpha`**. The distinctness arm failed on
  first run against the faithfully-ported logic. **Two fixtures whose names differ only in
  punctuation silently SHARE a namespace, and one teardown drops the other's schema** — *exactly
  the collision the deterministic name exists to prevent, reintroduced by its own sanitiser.*
  ⚑ Plausibly the source of the *"`dec_val` exists in SIXTEEN schemas"* symptom that file records.
  The new module escapes to the code point instead. **Ⓝ118 ⟡the-sanitiser-collides.**

  Landed: `substrate/param_marks.py` · `result_row.py` · `fixture_namespace.py` — **42 offline
  cases, 0 findings each**, all taking injected data, none opening a connection or naming a tenant.
  ⚑ **Next cut BLOCKED ON A RULING:** `insert_statement.py` was written and **refused on `S608`**
  (SQL string construction); the honest relief is a per-RESPONSIBILITY `pyproject.toml` entry, and
  *the agent would not grant itself an exemption.* **Ⓝ119 ⟡the-s608-ruling.**

* ⚑⚑⚑ **THE BASE RATE IS THE LESSON. FOUR FIGURES IN ONE BRIEF, THREE FALSIFIED BY THE TOOLS THAT
  OWN THEM** — the mypy import fraction (claimed large, measured zero), the 506 (measured 382), the
  star import's contribution (claimed load-bearing, measured ~5%). ⚑ The agent's own note:
  *"Two of the four blocker figures in this brief did not survive contact with the tool that owns
  them; the base rate suggests checking the third"* — **and the third (`agda_import_dag`'s 139
  findings under the `scripts.` spelling) is still unre-measured.** *A brief is a hypothesis with
  the same standing as any agent report, and mine were not held to it.*

* ⚑⚑⚑ **Ⓝ92b′ ⟡drain-store — THE TENANT REPAIR LANDED, AND I VERIFIED BOTH ARMS DIFFER.**

      store_target --redacted-dsn --sandbox  →  tenant: sandbox · substrate_sandbox @ 30432
      store_target --redacted-dsn --live     →  tenant: live    · substrate        @ 30432

  **The defect that started this — three invocations printing byte-identical `dbname: substrate` —
  is repaired, and the repair NAMES ITS TENANT** rather than leaving the reader to infer it.
  Four cuts, **48/48 offline cases**: `tenant_choice` (17, four outcomes with both refusals
  distinct) · `live_target` (11, transport IMPORTED from `sandbox_target`, never restated) ·
  `store_target` (20, **the dispatch — no fall-through branch**). ⚑ `sandbox_target` **is no longer
  orphaned**; the strand the gate warned about is closed.

  ⚑⚑ **`_tenant_named` COULD NOT BE REUSED AS I DIRECTED, AND THE REASON GENERALISES.** Routing
  through it requires **importing `store.py`, which drags the untyped hub in and makes any consumer
  un-cleanable.** *My instruction — "already present, already pure and total" — was TRUE AND NOT
  SUFFICIENT: **purity does not survive the import boundary here.*** Its four-way contract was
  reproduced in a clean module instead.

  ⚑ **AND `sandbox_dsn` WAS ALREADY CORRECT** — it routes through `_pg_target` and gets the
  NodePort; **only `sandbox_connect` (`:492`) hand-rolls the dict.** *My "the sandbox side is stale"
  was broader than the truth.* ⚑ 418 → **412** findings; the file moved under the brief. ⚑ And
  `pycodemod --attr` is **RETIRED**, refusing with `substrate/attr_reads.py` named — *I cited the
  old spelling.*

  ⚑⚑ **A DEFECT ITS OWN PROSE CAUSED, AND THE READER WAS RIGHT.** `suite_discovery` classifies any
  file whose entry point **MENTIONS** `--selftest` as a suite. Its docstring described the
  superseded dispatch **by naming that flag**, so the runner invoked the CLI as a suite — *which
  correctly refused for want of a tenant.* Rewritten to describe the flag without spelling it.
  **The discovery reader was doing exactly what it documents**; the prose was the defect.

  ⚑ **NEXT CUT NAMED: `credential_backend()` (`:292-329`)** — self-contained, reads only `keyring`
  plus two account names, and is **the last mode in that `__main__` block besides `--selftest`**.
  Once it moves, *the dispatch holds nothing but the selftest and the file can retire to a shim.*
  Still blocked behind it: `connect()`/`dsn()`/`engine_url()`/`dialect()`, which carry the **157
  consumer reads** and are separate transactions each.

* ⚑⚑⚑ **Ⓝ78‴ ⟡drain-query-topo — THE GATE STAGES THE IMPORT CLOSURE, NOT THE FILE, AND THAT
  RESIZES Ⓝ78′ ENTIRELY.** I recorded the mechanism as *"the gate stages the WHOLE post-edit
  FILE"*, and predicted the `_schema.*` rewire would be a **free consequence** of draining a
  consumer. **It is not.** A clean 100-line module writing `from jea.metalanguage import
  schema_rows` was refused at **506 findings** — `schema_rows`'s own, plus its
  `from schema_decl import *`. *The closure, not the file.*

  ⚑⚑⚑ **AND THE REASON THE 16 CONSUMERS TYPECHECK AT ALL IS THAT THEIR IMPORTS ARE INVISIBLE TO
  MYPY.** Verified by me — `module_importers jea.metalanguage.schema_rows` → **0 import sites in 0
  of 1246 files**, with the reader naming its own 8 blind spots rather than asserting absence, and
  the last one is the finding: *"`schema.py:85` re-exports `schema_rows` with a star; consumers
  reach it under THIS module's name and **name it nowhere**."* **Every consumer reaches it through
  a `sys.path` insert mypy cannot follow.** ⚑⚑ *So the hub is not merely convenient — it is
  LOAD-BEARING FOR THE GATE'S SILENCE, and writing the honest package-path import is the act that
  surfaces the 506.*

  ⚑ **THE DEPENDENCY THEREFORE INVERTS: `schema_rows` MUST BE DRAINED FIRST.** Upstream of every
  consumer's finish, not parallel to it. *Draining `query_topo` was necessary and is done; it was
  not sufficient*, and a one-line rewire on a DRAINED consumer would still be refused if written
  the correct way.

* ⚑⚑ **AND THE AGENT REFUSED THE FAKE THAT WOULD HAVE MADE IT PASS.** It could have kept the
  `sys.path` spelling in new code and landed a green rewire. Instead **both store-facing modules
  take their dependency INJECTED** — `live_indexes` takes rows, `query_columns` takes a `Protocol`.
  ⚑ *Forced by the gate and independently right*: **the row reader is what carries the TENANT**, so
  a module reaching for its own connection has chosen `--live`/`--sandbox` on its caller's behalf.

  Landed: `substrate/column_contours.py` (9) · `live_indexes.py` (7) · `query_columns.py` (6),
  **22 cases**, each arm carrying a real discriminator — the empty-index-map OVER-nomination
  (asserts strictly MORE gaps against an empty map, so the map is load-bearing), predicate-scope
  leakage (one column string interned under two node ids — *a string-keyed implementation passes
  every other arm*), partition conservation, and engine column order.

* ⚑⚑ **A FALSE ALARM OF MINE, AND IT IS THE SESSION'S OWN LESSON TURNED ON ME.** I ran
  `python3 -m substrate.column_contours --selftest`, got **silence and exit 0**, and read it as the
  *"passes by measuring nothing"* shape — in a module built minutes earlier. **Wrong: the suites
  are `*_selftest.py` SIBLINGS** (the n-split convention), all three discovered by
  `run_selftests --list` among **330**, and `python3 -m substrate.column_contours_selftest` →
  **9/9**. *A fact about my INVOCATION, reported as a fact about the substrate* — the exact error
  I have been cataloguing in other readers all session.

* ⚑ **VERIFIED OWNER MAPPING — ONE NAME, CHECKED AT ITS DEFINING MODULE:** `rows` →
  `schema_rows.py:165`. My earlier correction stands. ⚑ And `schema.py` outlines as **1 def
  (`probe`) + star re-exports**, confirming the hub is pure re-export — *so a mis-rewire would
  indeed still run and record a false ownership claim.*

  ⚑⚑ **THE TWO `getsource(schema)` GUARDS COULD NOT BE POSITIVELY CONFIRMED, AND THE AGENT SAID SO
  RATHER THAN ASSUMING.** They live in `jea/metalanguage/schema_selftest.py` (10 call sites), which
  has **NO `__main__` block** — invoking it directly **exits 0 silently with any flag**. *That
  silence is a fact about the invocation, not evidence the guards are fine* — and it is the real
  instance of the shape I falsely accused `column_contours` of.

* ⚑ **RESIDUE, NOT CHASED:** `query_topo.py` names **no tenant**, yet `store.connect(mode="ro")`
  did not refuse — while `store.tenant` (`:571`) documents refusing when neither is named. **Either
  `connect` has a different default path or the refusal is bypassed for read-only.** *A
  wrong-tenant exposure in a live tool.* **Ⓝ111 ⟡connect-bypasses-the-tenant-refusal.**

  ⚑ **NEXT CUTS, NAMED:** `substrate/topo_report.py` (the pure renderer — the last clean-landable
  piece; after it `query_topo.py` is imports + argv + three calls) and then **the 506-finding
  `schema_rows` drain, which is upstream of all sixteen.**
