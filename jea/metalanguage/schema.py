# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE schema declaration: one SQLAlchemy model, DDL emitted per dialect.

⚑⚑ THE DECLARATION NOW LIVES IN `schema_decl.py`, AND THIS MODULE RE-EXPORTS IT. The
split happened 2026-08-11 because this file had reached 2,102 code lines — past the
point where the region being edited can be read whole first. That is a measured defect,
not an aesthetic one: retiring `_unreflected_floor` took FOUR edits, two of which
repaired damage the previous edit caused, and it left an assertion referring to the
retired name that took the WHOLE SUITE down with a NameError (found and fixed in the
same pass as this split).

⚑ THE PUBLIC SURFACE IS UNCHANGED — every name this module exported before the split it
still exports, via the star-import below. `import schema as _schema` then `_schema.rows`,
`_schema.upsert`, `_schema.MD`, `_schema.ddl`, … all resolve exactly as they did. The
split is a relocation, never an interface change, so no consumer was touched.

⚑ AND THE CUT STOPS WHERE THE SELF-INSPECTION BEGINS. `_selftest` reads THIS module's own
source (`getsource(sys.modules[__name__])`) to police direct-connect bypasses of the
sandbox resolver, and to drive the `--holes` CLI block. Moving the `con=None` helpers or
the dispatch to a sibling would leave those guards scanning a file that no longer
contains what they police — passing by measuring NOTHING, which is precisely the failure
they exist to catch. So the row/execute helpers, the queue tier and the CLI stay here
with the guards that read them. See `schema_decl.py` for the other side of the seam.

⚑⚑ AND WRITING THAT SENTENCE FIRED THE GUARD, WHICH IS THE FINDING. My first draft of the
paragraph above spelled the bypass pattern literally, and the case failed with `got [17]`
— the guard matches any line containing the pattern, skipping only lines that START with
`#`, so DOCSTRING PROSE counts as a bypass site. It is doing something real (it caught a
line I added) and it is imprecise in a way worth naming rather than working around: the
finder reads TEXT, not the AST, so it cannot tell a call from a mention. The paragraph is
reworded; the guard is left as it is, because tightening it is a separate change from
this relocation and `--size` is what this pass is paying down.
"""

import sys

# ⚑⚑ THE RE-EXPORT CHAIN, AND ITS ORDER IS THE DEPENDENCY GRAPH MADE LITERAL.
#
#     schema_decl   the SQLAlchemy model, the tier map, DDL emission
#         ↑
#     schema_rows   the portable row/param/execute helpers + the sandbox resolver
#         ↑
#     schema_queue  the postgres-only watermark / registry / reclamation tier
#         ↑
#     schema        this module: the CLI, the diagnostics, and the re-export surface
#
# Every arrow points ONE way. That is not a stylistic preference — the first cut of this
# split had `schema_queue` importing `schema` while `schema` imported `schema_queue`, and
# it failed with `ImportError: cannot import name '_require_pg'` against a half-built
# module. The cycle was fixed by MOVING the helpers below their consumer, not by deferring
# an import, because a deferred import would have hidden the cycle rather than removing it.
#
# ⚑ THE STAR-IMPORTS ARE THE RE-EXPORT AND THEY ARE DELIBERATE. This module's contract is
# "everything the schema layer defines is reachable as `schema.<name>`", which nine
# importing modules rely on (`import schema as _schema`, then `_schema.rows`,
# `_schema.upsert`, `_schema.ph`, `_schema.hwm`, `_schema.drained`, …). An explicit list
# would be a SECOND roster to keep in step with four files — the same defect `_TIERS` is
# derived rather than typed to avoid. The private names are re-imported by name beside
# each star because `import *` skips a leading underscore by construction.
from schema_decl import *  # noqa: F401,F403  (declaration + DDL)

# ⚑ `VIEWS`, `_TIER_VIEWS`, `_view_ddl_named`, `table` AND `CreateView` LEFT THIS LINE
# 2026-08-12 (⟡view-purge) WITH THE CAPABILITY THEY NAMED. `schema_decl` no longer emits
# view DDL, so re-exporting the names would keep `schema.VIEWS` resolving to nothing a
# consumer could use — the re-export surface's whole job is to say what the layer HAS.
from schema_decl import (
    MD,
    INDEXES,
    _TIERS,
    _tier,
    MetaData,
    Table,
    Column,
    Text,
    Integer,
    BigInteger,
    Index,
    Identity,
    PrimaryKeyConstraint,
    select,
    func,
    exists,
    literal,
    CreateTable,
    CreateIndex,
)

# ⚑⚑ THE UNDERSCORE-PREFIXED *TABLES* MUST BE NAMED EXPLICITLY, AND MISSING THEM WAS A
# REAL REGRESSION THAT EVERY SELFTEST PASSED THROUGH. `import *` skips a leading
# underscore by construction, so `_node`, `_unit`, `_unit_cod` and `_orbit_def` — which
# are TABLE OBJECTS in the public schema, not private helpers — silently stopped being
# reachable as `schema._node` while `schema.py --selftest` still read 123/123 and every
# importing module's suite still passed.
#
# ⚑ THE SUITES COULD NOT HAVE CAUGHT IT, WHICH IS THE POINT. Most cases never touch most
# names, so an attribute that vanishes from the re-export surface is invisible to a green
# suite; it surfaces at the first consumer that reads it, which is a different run on a
# different day. The check that found it asks the surface directly — "does every name the
# consumer census named still resolve on `schema`" — rather than inferring it from a pass.
#
# ⚑ AND THE LEADING UNDERSCORE HERE MEANS "RAW, PRE-QUOTIENT", NOT "PRIVATE". `_node` is
# the interned projection table that the `node` VIEW is built over; the sigil distinguishes
# the base relation from the compat view of the same name, so it is part of the published
# vocabulary despite looking private to `import *`.
from schema_decl import _node, _unit, _unit_cod, _orbit_def
from schema_rows import *  # noqa: F401,F403  (row/execute helpers)

# ⚑ `_insert_row_sql` IS NAMED BESIDE THE STAR for the reason recorded above: `import *`
# skips a leading underscore by construction. It is the statement BUILDER the ⟡ladder-1
# cases anchor on — a guard that cannot reach it would have to scan source text instead,
# which is the substitution this file already records costing `schema._node` its surface.
from schema_rows import _cli_connect, _insert_row_sql


# ── the store-shape QUESTIONS — MOVED to `schema_diag.py` 2026-08-11 ────────────────
#
# ⚑ `census`, `core_path`, `core_id_for`, `classify_hole`, `positional`, `_dialects_differ`.
# The seam is one this file ALREADY TOOK ONCE and argued for in `positional`'s own docstring:
# *"LIFTED OUT OF THE CLI SO IT CAN BE TESTED … no case could drive it, and a wrong predicate
# would read as a clean measurement."* Six functions of that shape, now in one place that
# reaches DOWN to `schema_rows`/`schema_decl` and is reached by this module — the same
# one-way arrow as the rest of the chain.
#
# ⚑ AND `_dialects_differ` IS NAMED BESIDE THE STAR because `import *` skips a leading
# underscore by construction. `schema_selftest` imports it from HERE, so an unnamed star
# would have removed it from the re-export surface silently — the defect that took
# `schema._node`, `_unit`, `_unit_cod` and `_orbit_def` off this module while `--selftest`
# still read 123/123, because most cases never touch most names.
from schema_diag import *  # noqa: F401,F403,E402  (store-shape questions)
from schema_diag import _dialects_differ  # noqa: F401,E402

# ⚑ NAMED EXPLICITLY RATHER THAN LEFT TO THE STAR (⟡star-import-retire). The star above
# WOULD carry these — they are public — so this line is not required to make the dispatch
# work. It is here because the star is the pattern being retired, and every new name added
# through it is one more the retirement has to discover later. `--attr _schema.*` measured
# 336 attribute reads across 14 files against this module's surface; growing that blind
# spot to add a mode would be paying interest on the debt while filing it.
from schema_diag import (
    coverage_report,
    coverage_emit,
    coverage_reap,  # noqa: F401,E402
    width_report,
    promotes_report,
)


# ── `_selftest` — MOVED to `schema_selftest.py` 2026-08-11 ──────────────────────────
#
# ⚑ IT WAS 878 OF THIS FILE'S LINES, and its size was the reason the file could not be
# read whole before editing it. The cases are VERBATIM in the sibling — every ⚑ block
# moved with the case it explains — and the entry point is unchanged: `--selftest` below
# still runs them, still prints `selftest: N/N`, and `run_selftests` still finds this
# module's suite under this module's name.
#
# ⚑ THE IMPORT IS DEFERRED, AT THE DISPATCH, AND THAT IS LOAD-BEARING RATHER THAN
# STYLISTIC. `schema_selftest` imports `schema` — so a module-scope import here would be
# a cycle. It is the same shape as the deferred `import reconstruct` / `import lifecycle`
# / `import query_builders` elsewhere in this file, and for the same reason: the arrow
# runs consumer → schema, so schema may only reach back inside a function body.


def probe(sql, params=(), con=None, require=None):
    """Run one read against the tenant THIS INVOCATION NAMED and return its rows — the
    "ask postgres rather than assert" instrument.

    ⚑ THIS EXISTS SO A DESIGN QUESTION IS MEASURED, NOT REMEMBERED. Deciding whether
    `pg_visible_in_snapshot` exists, what `xmin` compares as, or how a plan degrades was
    otherwise a `python3 -c` against the LIVE store — a composition, and one pointed at
    the source of truth. The sandbox was enrolled for exactly this and had no reader.

    ⚑⚑ IT USED TO HARDCODE THE SANDBOX (`sandbox=True`), AND THAT MADE IT UNUSABLE FOR THE
    QUESTIONS IT EXISTS TO ANSWER. Measured 2026-08-22: three separate structural questions
    about the LIVE corpus — the widest event document, whether `UnknownFVs`/`KnownFVs` both
    intern, what a `QName` node's children are — each came back `0 row(s) [sandbox]` against
    an empty tenant, and the honest-looking output gave no hint that the question had been
    redirected. `--plan` does not execute and `--probe` could not reach live, so the reader
    was routed to composing shell instead, which is the shape the standing rule forbids.

    ⚑ THE OLD DEFAULT'S ARGUMENT WAS ABOUT WRITES AND DID NOT REACH READS. It read: *"a probe
    is a question, and a question should not be able to mutate the corpus by forgetting a
    flag."* Sound about mutation, and the protection it actually bought was
    `store.sandbox_connect` keeping the entry points distinct — which is unchanged. What the
    default ADDED was a silent tenant redirect on the read path, and a read against the wrong
    tenant returns plausible rows nobody can distinguish (memory:
    `wrong-tenant-read-is-silent`). That is the worse failure of the two.

    ⚑ SO THE CHOICE MOVES TO THE INVOCATION, resolved by `store.tenant` like every other
    mode: `--live` or `--sandbox`, STATED, with a refusal when neither is. Callers passing
    their own `con` are unaffected; there is no tenant default left to forget.
    """
    # ⚑ A NON-RETURNING STATEMENT IS A SUCCESS, NOT AN ERROR. `rows()` demands a result
    # set, so a sandbox `CREATE TABLE` raised ProgrammingError AFTER the DDL had already
    # run — an exception reporting a completed operation, which is the worst kind: the
    # reader concludes it failed and re-runs. Probing a design question needs DDL as much
    # as SELECT, so the distinction is handled here rather than pushed onto the caller.
    _require_pg("probe()")
    # ⚑ ONE RESOLVER, the same one `_cli_connect` routes through. `store.tenant` reads
    # `--live`/`--sandbox` from the invocation and REFUSES when neither is stated, so the
    # "nobody chose" case is representable here instead of silently meaning sandbox.
    # ⚑ `mode="ro"` ON THE LIVE ROUTE: a probe is a question. The sandbox route opens
    # read-write by design (it exists to be mutated), which is why DDL probes still work
    # there and are refused against live — see `store.sandbox_connect`'s note.
    # ⚑⚑ `require=` IS NOT OPTIONAL POLISH — WITHOUT IT THIS CHANGE POINTED THE SUITE'S DDL
    # PROBES AT THE CORPUS. `schema_selftest` calls `probe("CREATE TABLE _rc_probe(i int)")`
    # and `probe("CREATE TABLE _prune_probe(…)")`; under argv resolution those inherited the
    # invocation's tenant — and `--selftest` names none, so `store.tenant`'s advisory branch
    # defaulted them to LIVE. Caught because the suite hung after four tenant warnings, not
    # because anything checked. A fixture's tenant is NOT the operator's to choose, which is
    # precisely the case `store.tenant(require=…)` exists for (same escape as
    # `edit_snapshot.guard(intent=…)`).
    if con is None:
        import store as _store

        con = _store.tenant(mode="ro", label="probe", require=require)
    cur = con.cursor()
    cur.execute(sql, params or None)
    if cur.description is None:
        return []  # DDL/DML: ran, produced no rows
    return [
        Row(
            tuple(d[0] for d in cur.description),
            list(r.values()) if isinstance(r, dict) else list(r),
        )
        for r in cur
    ]


# ── the QUEUE tier — MOVED to `schema_queue.py` 2026-08-11 ──────────────────────────
#
# ⚑ 741 LINES: `_require_pg`, `hwm`, `lwm`, `consumers`, `register`, `advance`,
# `reclaimable`, `PERSISTENT_READERS`, `_READER_NEEDS`, `_repair_registry`,
# `pin_persistent`, `lifecycle_census`, `reclaim`, `activity`, `flush`, `migrate_queue`,
# `cancel`, `drained`. Every one is postgres-only behind `_require_pg`, which is the
# tier's single precondition and is why this is a capability seam rather than a size cut.
#
# ⚑⚑ THAT ROSTER IS A 2026-08-11 SNAPSHOT AND IS NOW HALF OBITUARY — SAID HERE RATHER THAN
# EDITED AWAY, because this exact note has already been the file's own recorded example of a
# relocation list that *"reads as authoritative while being false"*. `lwm`, `consumers`,
# `register`, `advance`, `reclaimable`, `PERSISTENT_READERS`, `_READER_NEEDS`,
# `_repair_registry` and `pin_persistent` are DELETED (2026-08-12, the queue-tier retirement);
# each left a residue block at its own site in `schema_queue.py`, which is where the reader
# should go. A relocation note records a MOVE; it is not a live census, and reading it as one
# is the defect it records.
#
# ⚑⚑ AND THREE OF THAT ROSTER HAD NOT ACTUALLY MOVED — THE NOTE WAS WRITTEN FROM THE PLAN,
# NOT FROM THE RESULT. `activity`, `flush` and `migrate_queue` were still DEFINED IN THIS
# FILE, above this comment, while this comment said they were in the sibling; measured with
# `pycodemod --binding activity`, which returned exactly one binding, at `schema.py:125`.
# That is the same defect class as a banner advertising a mode the dispatch never grew: it
# **reads as authoritative while being false**, and it sends the next reader to the wrong
# file. Corrected 2026-08-11 by doing the move the note described — the membership test
# (`_require_pg`, or the same refusal inline) was already satisfied by all three.
#
# ⚑⚑ THE IMPORT SITS HERE — WHERE THE CODE WAS — AND THE POSITION IS LOAD-BEARING.
# `schema_queue` imports `rows`/`scalar`/`execute`/`ph`/`upsert`/`_cli_connect` from THIS
# module, so this module may only import it back once those are bound. At the top of the
# file it would execute `schema_queue`'s body against a half-initialised `schema` and fail.
# Keeping it at the original site preserves the definition order exactly as it was, which
# is also what keeps `census`/`--watermark` below able to call these names unqualified.
from schema_queue import *  # noqa: F401,F403,E402  (re-export)
from schema_queue import (
    _require_pg,
)  # (_repair_registry/_READER_NEEDS/PERSISTENT_READERS: retired with the pin, 2026-08-12)


# ⚑⚑⚑ ⟡mode-standardize — THIS ROSTER IS THE `Mode(...)` SHAPE, LIFTED FROM `(flag, gloss)`
# PAIRS.  The corpus declared its CLI modes five different ways (module docstring, argparse
# block, this tuple form, a usage string printed from `__main__`, and the `Mode` dict); five
# shapes meant `toolmodes` had to learn all five before it could answer "what modes does this
# tool have".  Consistency is the deliverable (operator, 2026-08-23: *"the POINT of the
# standard is standardizing shape and achieving consistency"*).
#
# ⚑⚑ AND THE LIFT RECOVERED A FIELD THE PAIR SHAPE CARRIED IN PROSE.  Entries were written
# `("--core PATH", …)` — the operand real, declared, and buried INSIDE the key.  A naive
# `{flag: Mode(why=gloss)}` would have keyed the roster on `"--core PATH"`, matching no argv
# token, with arity silently `None`: a migration that loses a field the old shape happened to
# hold, which is worse than the drift it fixes because the new shape then reads as
# authoritative about arity it never learned.  `climode.split_flag` parses it out.
#
# ⚑ `writes` IS WHY THIS FILE IS THE RIGHT FIRST CONVERSION.  Eight of these modes MUTATE —
# `--flush`, `--seed`, `--reclaim`, `--reclaim-core`, `--migrate-queue`, `--cancel` and
# `--coverage --reap` write the STORE, and each already carries a hand-written "(dry run;
# --apply)" in its gloss.  That was prose no discriminator could read.  Declared as
# `writes=("store",)`, the `--apply`/`--dry-run` refusal convention finally binds to
# something checkable — which is the whole reason the field is a TARGET SET and not a bool
# (operator: *"it matters WHAT you're mutating"*).
_MODES = (
    ("--census", "row count per declared relation, grouped by tier (missing reads '-')"),
    ("--core PATH", "is THIS core in the store, and how many obs/edge rows does it hold"),
    ("--spread", "per-core row DISTRIBUTION — min/median/mean/max, not one sample"),
    ("--fibre", "is obs.local_id DENSE per core? — whether the residue can be POSITIONAL"),
    ("--holes", "cores with a fingerprint but no observations (an unfinished ingest)"),
    ("--sample REL [N]", "N rows of a live relation, base64 fields DECODED — read the data"),
    ("--nullity REL", "per-column NULL/empty rate — which columns are identity vs payload"),
    # ⚑ THESE FOUR DISPATCHED WITH NO USAGE LINE UNTIL `toolmodes --check` CAUGHT THEM
    # (2026-08-22). I added the modes and the dispatch branches and never declared them, so
    # they were invisible to `--find` — the exact undocumented-mode defect this list exists
    # to prevent, four times in one session, by the person reading the census that reports it.
    (
        "--widest REL",
        "per-column max/avg OCTET width against the btree key ceiling — the "
        "reader a key-width decision needs. MAX is the constraint, not avg: a "
        "key fails on the ONE row that exceeds it, and bytes ≠ characters",
    ),
    (
        "--coverage",
        "per DERIVED table: source keys, materialized keys, and BOTH residues — "
        "`owed` (the projection has not run) and `orphan` (rows outliving their "
        "source). One number cannot carry both; they want opposite repairs",
    ),
    # ⚑⚑ THESE TWO ARE MODIFIERS OF `--coverage`, AND THEY COLLIDE WITH IT IN `from_pairs`
    # (⟡document-modes, 2026-08-24).  All three entries `split_flag` to the key `--coverage`,
    # so the LAST wins and `MODES["--coverage"].why` silently became `--reap`'s sentence —
    # the roster described the census mode as *"delete ORPHAN keys only"*.  Unobservable
    # while the usage block printed `_MODES`, because the pairs still rendered correctly and
    # nothing read the corrupted roster entry.
    #
    # ⚑ THEY STAY HERE ANYWAY, AND THE COLLISION IS REPAIRED AT THE ROSTER.  `toolmodes`
    # reads these lines from SOURCE to know the two modifiers are documented; deleting them
    # made `--emit` and `--reap` read as undocumented dispatches.  The post-hoc
    # `MODES["--coverage"]` below now writes its gloss EXPLICITLY instead of reading back a
    # colliding key, so the pairs stay the census's source and `MODES` stays the roster's —
    # two readers, one file, and neither can corrupt the other.
    (
        "--coverage --emit",
        "the same reading as a SERIES in VictoriaMetrics, through the "
        "shared producer — the store MOVES, so a scalar is stale on arrival",
    ),
    (
        "--coverage --reap {--dry-run|--apply}",
        "delete ORPHAN keys only, by key, re-derived at the moment of the delete. NOT a tier "
        "flush: no DDL, no DROP, no lock beyond the rows named",
    ),
    ("--arity", "child-count distribution — is the forest BINARY, or n-ary?"),
    (
        "--packed",
        "which cores are INTERNED and how far — the `--equiv` COMPARISON WINDOW, "
        "where a core is BOTH ingested and projected (both fold arms read obs_node, "
        "so outside that window the gate is vacuous either way)",
    ),
    ("--flush TIER…", "drop and recreate tiers from the declaration (dry run; --apply)"),
    (
        "--seed",
        "POPULATE a tenant by running the adversarial fixture document through the "
        "REAL rungs — the population `query_defs --verify` compares over, which no "
        "suite can leave behind (its fixtures live in private schemas it drops). "
        "Destructive to the named tenant (dry run; --apply)",
    ),
    ("--growth", "on-disk size per relation — sees UNCOMMITTED writes that --census cannot"),
    (
        "--headroom",
        "does the volume ADMIT the projected promote? — a bytes/row projection "
        "DERIVED from what obs_node already holds, against BOTH halves of the "
        "ledger: the durable write AND the staged rows the drain retires behind "
        "it. --growth reports what the store OWNS, which reads healthy right up "
        "to an ENOSPC and cannot see the retirement either — sizing a promote on "
        "the write alone makes a space-RECOVERING run read as refused",
    ),
    ("--activity", "what the store's connections are doing: state, wait event, statement"),
    (
        "--locks",
        "the LIVE-HANG breakdown — pg_locks ⋈ pg_stat_activity: per backend what it "
        "HOLDS vs WANTS, who blocks whom, and whether the wait-for graph has a CYCLE",
    ),
    (
        "--promotes",
        "what the build is PROMOTING right now, keyed on WHOSE work it is: per "
        "in-flight promote the MODULE (from the backend's own application_name, "
        "never guessed from a bound-$1 query) and its stage, workers folded under "
        "their leader, plus the non-promote backends sharing the tenant — the half "
        "that explains a slow promote when --locks correctly says lock-waiting 0",
    ),
    (
        "--cancel PID {--dry-run|--apply}",
        "stop a running statement (add --terminate to drop the connection). A PID is not a "
        "stable key — it is REUSED — so --dry-run re-reads pg_stat_activity and shows WHOSE "
        "backend that number currently is, rather than echoing the operand back",
    ),
    ("--probe SQL", "run one read against the SANDBOX tenant — ask postgres, don't assert"),
    (
        "--plan SQL",
        "the LIVE plan and ESTIMATED rows, EXECUTING NOTHING — what a query "
        "would cost, without paying it (EXPLAIN, never EXPLAIN ANALYZE)",
    ),
    ("--lifecycle", "every observation's STAGE and what holds it (the located rejection)"),
    ("--migrate-queue", "retire the queue tier — registry, obs.seq, ix_obs_seq (--apply)"),
    # ⚑ ONE STRING, NOT THREE LINES — this file's code-line budget is HALVED TWICE for two
    # recorded edit-breaks-its-own-region incidents (`_pycodemod_census.INCIDENT_HALVINGS`),
    # so a 300-line cap that a three-line banner entry pushes to 301 is the ratchet doing
    # exactly its job. Paid down by writing the entry, not by editing the table.
    (
        "--reclaim",
        "retire every core the durable tier can rebuild — the per-core licence, "
        "no floor and no pin (dry run; --apply)",
    ),
    (
        "--reclaim-core ID",
        "retire ONE core if the licence admits it — the make-driven twin of "
        "--reclaim, using the SCOPED licence (drainable_res.one_core) so the "
        "corpus set is never computed to answer about one core "
        "(dry run; --apply). `--packed` names the candidates",
    ),
    ("--ddl [backend]", "emit the synthesized DDL for a backend (default: the live one)"),
    ("--relations", "what the live store actually holds, per the backend's catalogue"),
    (
        "--columns [REL]",
        "per-relation COLUMN names, from the engine — the reader for "
        "'which relations carry a record-version column'",
    ),
    (
        "--uniqueness",
        "does the data satisfy every declared UNIQUE index? — the pre-flight "
        "for adding one to a populated store",
    ),
    (
        "--index-size",
        "per-index on-disk bytes, rows and BYTES/ROW — the figure a key-width "
        "decision needs (--growth reports relations, never indexes)",
    ),
    (
        "--check-indexes",
        "is every DECLARED index present on this tenant? — the PRECONDITION "
        "that lets a reader assert its access paths instead of a writer "
        "creating them (--index-size reports what EXISTS, never what is OWED)",
    ),
    ("--selftest", "the guarded cases"),
    # ⚑⚑⚑ ⟡document-modes (2026-08-24) — THESE THREE WERE DECLARED IN `MODES` ONLY, AND
    # THAT IS WHY THEY READ AS UNDOCUMENTED FOR AS LONG AS THEY HAVE.  Each was added as a
    # post-hoc `MODES[...] = Mode(...)` when `check_mode_contracts` caught it dispatching in
    # no roster — a correct paydown of the ROSTER half that left the USAGE half untouched.
    #
    # ⚑ AND THE TWO CENSUSES READ DIFFERENT SPELLINGS, WHICH IS WHY PAYING ONE DID NOT PAY
    # THE OTHER.  `check_mode_contracts` imports the module and reads `MODES` — the runtime
    # object, so a post-hoc entry satisfies it.  `toolmodes --divergence` reads this file's
    # SOURCE for the usage lines a bare run would print, so a post-hoc entry is invisible to
    # it no matter what the bare run actually emits.  My first cut here made the PRINTER
    # read `MODES`, which fixed the human-visible output and moved the census not at all:
    # a fix aimed at the wrong instrument, and the census was right to keep failing.
    # `census-keyed-on-one-spelling`, with the two spellings being *declared* and *printed*.
    (
        "--establish TIER…",
        "CREATE the named tiers IF NOT EXISTS — the non-resetting twin "
        "of --flush (dry run; --apply)",
    ),
    (
        "--migrate-views",
        "reconcile declared VIEWS with the store (⟡view-purge) — the "
        "sibling of --migrate-queue (dry run; --apply)",
    ),
    (
        "--transport",
        "the write path's own properties, READ FROM THE DRIVER — a claim about "
        "a dependency, re-derived every run",
    ),
)

# ⚑ ONE AUTHORITY, IMPORTED FROM `scripts/` — not a copy.  `Mode` lives in
# `scripts/climode.py` rather than where it was written (`scratch/pycodemod.py`) precisely
# so THIS file can use it: `check_scratch_independence` (Λ8) refuses a promoted project
# importing from `scratch/`, and its refusal text says to fix that by PROMOTING the module,
# never by repathing.  `scripts/` is where `ratchet.py` already sits for the same reason.
# ⚑ `os` IS NOT BOUND AT MODULE SCOPE HERE — it is imported inside functions, so the
# obvious `os.path.join(...)` raised `NameError` at import time. Imported locally rather
# than hoisting a module-level `import os`, which would change this file's import surface
# for one path computation.
import os.path as _osp  # noqa: E402

sys.path.insert(
    0, _osp.join(_osp.dirname(_osp.dirname(_osp.dirname(_osp.abspath(__file__)))), "scripts")
)
from climode import Mode, from_pairs  # noqa: E402

#: The declared roster, `{flag: Mode}` — arity and gloss lifted from the pairs above.
MODES = from_pairs(_MODES)

# ⚑⚑ THE MUTATING MODES, DECLARED — the half the pair shape could only say in prose.
# Each of these already carried "(dry run; --apply)" or "(--apply)" in its gloss, which is
# a sentence a reader honours and a discriminator cannot.  `writes=("store",)` is the same
# claim in a form `check_mode_contracts` can FAIL: a mode declaring it writes whose branch
# tests neither `--apply` nor `--dry-run` is a gate failure, not a review note.
#
# ⚑ THE TARGET IS `store`, NOT A FILE EXTENSION, AND THAT IS THE POINT OF A TUPLE.  These
# modes read `.agdai`-derived rows and write the POSTGRES STORE — two different artifacts,
# one of them mutated.  A boolean `mutates=True` could not have said which, and `--growth`
# / `--census` touch the same store while writing nothing.
#
# ⚑ DECLARED AT CONSTRUCTION, NOT PATCHED AFTERWARDS.  My first cut assigned
# `MODES[k].writes = …` in a loop, which splits one mode's declaration across two places
# in the file — the reader who finds the entry does not see the contract, and the two can
# drift.  A rebuild keeps each `Mode` whole.
_WRITES_STORE = (
    "--flush",
    "--seed",
    "--reclaim",
    "--reclaim-core",
    "--migrate-queue",
    "--cancel",
    "--coverage",
)
MODES = {
    f: Mode(
        operand=m.operand,
        paths=m.paths,
        opts=m.opts,
        scans=m.scans,
        writes=("store",) if f in _WRITES_STORE else (),
        why=m.why,
    )
    for f, m in MODES.items()
}

# ⚑⚑ `--emit` AND `--reap` ARE MODIFIERS OF `--coverage`, NOT MODES — declared as its
# `opts` so the roster says which mode OWNS them.  The pair roster could not express
# ownership at all: it spelled them `"--coverage --emit"` and `"--coverage --reap
# {--dry-run|--apply}"`, two keys that match no argv token, so `contract_rows` read the
# nested dispatch as two undeclared top-level modes.  A modifier owned by one mode is
# exactly the distinction `Mode.opts` exists for, and the same one ⟡mode-dual-role is
# unresolved about in `pycodemod`.
# ⚑⚑⚑ AND `why=MODES["--coverage"].why` WAS READING THE WRONG GLOSS, silently, since the
# lift (found 2026-08-24 by ⟡document-modes making the usage block read `MODES`).  The
# pairs list spells THREE entries beginning `--coverage` — the mode, `--coverage --emit`,
# and `--coverage --reap …` — and `from_pairs` keys all three on the flag `--coverage`, so
# the LAST one wins.  `MODES["--coverage"].why` was therefore `--reap`'s sentence: the
# roster described the census mode as *"delete ORPHAN keys only"*, the destructive
# modifier, and the two modifier glosses were gone entirely.
#
# ⚑ IT WAS UNOBSERVABLE WHILE THE USAGE BLOCK PRINTED `_MODES`.  The pairs still held all
# three lines, so a bare run rendered correctly and the corrupted roster entry was read by
# nothing that printed.  A migration that keeps the OLD spelling as the display path hides
# whether the NEW one survived the lift — the two-spellings shape, with one spelling never
# looked at.  Making `MODES` the single authority is what made the defect visible at all.
#
# ⚑ SO THE GLOSS IS WRITTEN HERE, not recovered from a lookup whose key collides.  The
# modifiers keep their own lines in `_MODES`, which is what the source-reading census sees;
# `opts` says WHICH modifiers this mode owns and was never able to say what they do.
MODES["--coverage"] = Mode(
    paths=False,
    opts=("--emit", "--reap"),
    writes=("store",),
    why="per DERIVED table: source keys, materialized keys, and BOTH residues — `owed` "
    "(the projection has not run) and `orphan` (rows outliving their source). One "
    "number cannot carry both; they want opposite repairs",
)

# ⚑ `--establish` and `--transport` DISPATCH AND WERE IN NO ROSTER — the plain undeclared
# case, found by the gate the moment this file adopted the shape.
# ⚑⚑ ARITY READ FROM THE BRANCH, AND MY FIRST CUT GUESSED IT WRONG. I wrote
# `--establish` as nullary from the NAME; the branch takes one-or-more TIER names and
# exits 2 without them (`:663-668`). That is precisely the undeclared-arity defect this
# roster exists to prevent, committed while paying it down — the entry point resolves
# operand binding from here, so a nullary claim would let the next token be read as a path.
# ⚑ THE GLOSS AND THE OPERAND NOW COME FROM THE PAIRS ENTRY (⟡document-modes, 2026-08-24);
# this block adds only `writes`, the field the pair shape cannot carry.  Restating the
# gloss here is what made it a SECOND spelling — see the note at the pairs entry.
MODES["--establish"] = Mode(
    operand=MODES["--establish"].operand, writes=("store",), why=MODES["--establish"].why
)
# ⚑⚑⚑ AND `--transport` I GUESSED WRONG IN THE OTHER DIRECTION — I wrote it as
# `writes=("store",)`, "move rows between tenants", from the name alone. It is a PURE READ
# (`:945-951`): it reports the DRIVER's write-path properties, re-derived per run, and
# exists because "psycopg's executemany does not batch" was once asserted as fact and
# refuted five minutes later. Two guesses, two errors, opposite directions — `--establish`
# under-declared its arity and this over-declared its effect. A false `writes` is the worse
# half: it would demand an `--apply` guard on a mode that changes nothing.
MODES["--transport"] = Mode(why=MODES["--transport"].why)  # a PURE READ: no `writes`

# ⚑⚑ `--migrate-views` WAS INVISIBLE UNTIL THE READER LEARNED CO-LOCATED BRANCHES. It
# shares one `if` line with `--migrate-queue` (`:849`) — deliberately, since both reconcile
# the store's shape with the declaration and a second block would be a second copy of the
# empty-plan reading. `branch_bounds` matched only the FIRST flag on a line, so this mode
# dispatched, mutated the store, and appeared in no roster and no finding. Found the moment
# the reader was fixed for `mdstruct`'s shared `--replace-section`/`--append-section` line:
# one reader defect, two tools, and this one was hiding a WRITER.
MODES["--migrate-views"] = Mode(writes=("store",), why=MODES["--migrate-views"].why)


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — READ BY `run_selftests._tenant`, WHICH APPENDS THIS FLAG WHEN IT RUNS THE
# SUITE. Not decoration: `store.tenant` exits 2 on an unstated tenant since ⟡tenant-mandatory
# (2026-08-24), and this suite is the ONE of twelve OWED that measurably aborted mid-run —
# `sql-F19` recorded it exiting 2 with no record at all, which typed as `silent` and sent a
# reader hunting a missing emitter rather than a missing declaration.
# ⚑ SANDBOX AND NOT LIVE, and the reason is the whole point of having two tenants: a suite that
# reaches the LIVE store can corrupt the corpus it is meant to be checking. Verified before
# choosing — no `--live` literal on any selftest path in this file, only usage strings.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # ⚑ DEFERRED, BECAUSE `schema_selftest` IMPORTS `schema` — a module-scope import
        # here would be a cycle. Same shape, same reason, as the deferred `reconstruct` /
        # `lifecycle` / `query_builders` imports throughout this file.
        from schema_selftest import _selftest

        raise SystemExit(_selftest())
    import store

    if "--census" in sys.argv:
        raise SystemExit(census_report("--sandbox" in sys.argv))

    # ── the READ-ONLY REPORTS — bodies in `schema_diag.py` since 2026-08-11 ────────────
    #
    # ⚑ THE DISPATCH STAYS HERE; ONLY THE RENDERING MOVED, and the line between them is
    # WHERE EACH BLOCK'S ⚑ NOTES POINT. `--spread`/`--arity`/`--nullity`/`--sample`/
    # `--fibre`/`--growth` carry notes about what the NUMBERS mean, so they travel with the
    # computation; the admin modes below carry notes about the CALL the dispatch makes
    # (`--advance`'s defaulted `kind`, `--retype`'s `strict=True`, `--reclaim`'s
    # never-passed connection), so those blocks stay whole, here, with their commentary.
    #
    # ⚑ AND `--holes` IS THE DELIBERATE EXCEPTION, PINNED BY A GUARD IN ANOTHER FILE.
    # `schema_selftest` slices `getsource(schema)` between `'if "--holes" in sys.argv:'` and
    # `'if "--fibre"'` and asserts `"*.agdai"` / `"PARTIAL INGEST"` / `"on_disk"` are inside
    # it. Move that body and the guard scans a file that no longer contains what it polices —
    # passing by measuring NOTHING. So `--holes` keeps its body, and `--fibre`'s dispatch
    # keeps its literal spelling because it is the slice's closing delimiter.
    if "--uniqueness" in sys.argv:
        raise SystemExit(uniqueness_report())

    if "--index-size" in sys.argv:
        raise SystemExit(index_size_report())

    # ⚑ Ⓢ1 — PASSES `--sandbox` THROUGH, unlike its neighbours. A missing index on a
    # SANDBOX reported as a live-store defect sends someone to repair a store that is
    # fine (memory `wrong-tenant-read-is-silent`), so the tenant travels to the
    # report and appears in its output rather than being inferred by the reader.
    if "--check-indexes" in sys.argv:
        raise SystemExit(check_indexes_report(sandbox="--sandbox" in sys.argv))

    # ⚑ `--locks` SITS BESIDE `--activity`, NOT INSIDE IT. `--activity` answers *what is this
    # connection running*; this answers *who waits on whom*, and the 2026-08-14 incident is
    # that the first cannot be read as the second — an `active` backend with no `wait_event`
    # is WORKING, and a flat progress counter over it means slow, not stalled.
    if "--locks" in sys.argv:
        raise SystemExit(locks_report(sandbox="--sandbox" in sys.argv))

    # ⚑ `--promotes` IS `--locks`' THIRD SIBLING, KEYED ON ATTRIBUTION. `--activity` asks
    # *what is this connection running*, `--locks` asks *who waits on whom*, and this asks
    # *whose work is this* — the question the 2026-08-23 incident left unanswerable. Five
    # promoters at 1–3.5h all had IDENTICAL lock state (`lock-waiting 0`, correctly), so
    # neither sibling could distinguish them and the module attribution had to be done by
    # eye over raw `pg_stat_activity`. Splitting it out rather than widening `--locks`
    # keeps each mode's verdict readable, the reason `--widest` sits beside `--nullity`.
    if "--promotes" in sys.argv:
        raise SystemExit(promotes_report(sandbox="--sandbox" in sys.argv))

    if "--spread" in sys.argv:
        raise SystemExit(spread_report())

    # ⚑ `--sizes` joins the STORE's document sizes to the FILESYSTEM's `.agdai` sizes, so it
    # sits beside `--spread` (the other distribution mode) rather than with the per-relation
    # readers. See `corpus_size_report`: it exists because a capacity knob was about to be
    # sized on the file size, and the file size does not predict the document size.
    if "--sizes" in sys.argv:
        raise SystemExit(corpus_size_report())

    if "--packed" in sys.argv:
        raise SystemExit(packed_report())

    # ⚑ `--emit` IS A MODIFIER ON `--coverage`, NOT A MODE — the same relationship
    # `--autosync` has to `--check`. Reading and publishing are one question asked at two
    # audiences; a separate mode would be a second place for the reader to drift from.
    # ⚑ AND IT DOES NOT DEFAULT TO EMITTING: writing to a shared store is an outward-facing
    # act, so it is STATED, per the explicit-axes rule (no dry-by-default, no apply-by-default).
    if "--coverage" in sys.argv:
        if "--emit" in sys.argv:
            raise SystemExit(coverage_emit())
        if "--reap" in sys.argv:
            # ⚑ NEITHER IS THE DEFAULT — the caller states one. A delete that runs because a
            # flag defaulted is what `write_events`' `finalize=True` was, removed today.
            _dry, _app = "--dry-run" in sys.argv, "--apply" in sys.argv
            if _dry == _app:
                print(
                    "schema.py --coverage --reap: state --dry-run OR --apply "
                    "(never both, never neither — this DELETES rows)."
                )
                raise SystemExit(2)
            raise SystemExit(coverage_reap(apply=_app))
        coverage_report()
        raise SystemExit(0)

    if "--arity" in sys.argv:
        raise SystemExit(arity_report())

    if "--nullity" in sys.argv:
        raise SystemExit(nullity_report(sys.argv[sys.argv.index("--nullity") + 1]))

    # ⚑ `--widest` IS `--nullity`'s SIBLING, NOT A MODE ON IT. Both are per-column censuses of
    # one relation, and both answer a KEY-DESIGN question — but nullability and width are
    # independent constraints (a narrow nullable column fails the PK test; a wide NOT NULL one
    # fails the btree test), so folding them into one report would make each verdict harder to
    # read for the sake of one fewer flag.
    if "--widest" in sys.argv:
        raise SystemExit(width_report(sys.argv[sys.argv.index("--widest") + 1]))

    if "--sample" in sys.argv:
        _i = sys.argv.index("--sample")
        _lim = int(sys.argv[_i + 2]) if len(sys.argv) > _i + 2 and sys.argv[_i + 2].isdigit() else 5
        raise SystemExit(sample_report(sys.argv[_i + 1], _lim))

    if "--holes" in sys.argv:
        # ⚑ A CORE IN `core_fp` WITH NO `obs` ROWS IS NOT A ZERO — IT IS AN UNFINISHED
        # INGEST, and the two censuses could not tell them apart. `--census` reported
        # core_fp=168 and `--spread` reported 152 cores; the 16-core difference was visible
        # only by comparing two modes by eye, which is the judgement-in-the-turn shape.
        #
        # ⚑ THIS BLOCKS THE RECONSTRUCT, WHICH IS WHY IT IS MEASURED FIRST. `reflected` is
        # "the durable form rebuilds this record". Run against a core whose ingest was
        # interrupted, a reconstruction MISMATCH is ambiguous between a bug in the rebuild
        # and rows that were never written — and the ambiguity resolves the wrong way,
        # because "reconstruct failed" reads as "do not drain" and looks safe.
        #
        # ⚑ AND A FINGERPRINT IS A CLAIM OF COMPLETION. `core_fp` is written to say "this
        # core at this mtime is ingested"; a row there with no observations is that claim
        # contradicted by the store itself. Report the direction too — an obs-without-fp
        # core is the opposite failure (rows with no completion record) and wants a
        # different repair.
        con = _cli_connect()
        # ⚑⚑ THE SAME SPILL SHAPE AS `n_obs` BELOW, and per-site repair would have left it.
        # `LEFT JOIN (SELECT DISTINCT core_id FROM obs)` MATERIALISES the distinct set over
        # all 93.4M rows before joining 2,084 fingerprints against it — the whole corpus
        # aggregated to answer a per-fingerprint question.  Found by censusing the file's SQL
        # after fixing the line that actually filled the disk; one incident, two sites.
        #
        # ⚑ `NOT EXISTS` IS THE RIGHT SHAPE HERE, and it is strictly better than the GROUP BY
        # used below: the question is asked ONCE PER FINGERPRINT ROW and each ask is an index
        # probe into `ix_obs_pk` that stops at the first hit.  ~2,084 probes, no aggregate, no
        # spill — the width of the answer instead of the width of the corpus.  (`n_obs` cannot
        # use this form: it counts DISTINCT cores in `obs` with no per-row driver to probe from.)
        fp_only = list(
            rows(
                con,
                "SELECT f.core_id, f.mtime FROM core_fp f "
                "WHERE NOT EXISTS (SELECT 1 FROM obs o WHERE o.core_id = f.core_id) "
                "ORDER BY f.core_id",
            )
        )
        obs_only = list(
            rows(
                con,
                "SELECT o.core_id, count(*) AS n FROM obs o "
                "LEFT JOIN core_fp f ON f.core_id = o.core_id "
                "WHERE f.core_id IS NULL GROUP BY o.core_id ORDER BY count(*) DESC",
            )
        )
        n_fp = scalar(con, "SELECT count(*) FROM core_fp")
        # ⚑⚑⚑ THIS LINE FILLED THE DISK AND TOOK THE BOX TO 97%, 2026-08-18.  It was
        # `count(DISTINCT core_id) FROM obs` — a DISTINCT over **93,362,846 rows** to
        # answer a question whose answer is ~2,084.  At the live `work_mem` (8MB) the
        # aggregate spills almost entirely to `base/pgsql_tmp`: one backend held 18
        # spill files of 1GB each after 91 minutes and was still growing ~20MB/s.  It
        # killed a peer session's fold with ENOSPC and would have taken postgres down
        # for every session on the box.  Cancelling it and its twin returned 38GB.
        #
        # ⚑ CORPUS-SCALE WORK FOR A CORE-SCALE ANSWER, which is the shape to look for.
        # The row count and the answer differ by four orders of magnitude, so the
        # aggregate's width is doing nothing the result can use.
        #
        # ⚑ `GROUP BY` AND NOT `DISTINCT`, and the difference is the plan.  Both are
        # exact and both return the same integer, but the subquery lets the planner
        # HashAggregate and stream a count over the groups instead of materialising a
        # sort/hash of every row's key — far less to spill, and it degrades gracefully
        # when it does.  Not an approximation: `--holes` compares this against `core_fp`
        # to find unfinished ingests, so an estimate (`reltuples`, HyperLogLog) would
        # make the PARTIAL-INGEST warning below unsound.
        #
        # ⚑ AND THE REAL FIX IS ONE LEVEL UP, RECORDED HERE RATHER THAN GUESSED AT:
        # every core with `obs` rows should have a `core_fp` row, so this count is
        # derivable from the fingerprint tier without touching `obs` at all.  It is not
        # done that way BECAUSE THAT IS THE INVARIANT THIS MODE EXISTS TO TEST — reading
        # the answer off `core_fp` would assume exactly what `obs_only` below measures.
        # The census must ask `obs` directly or it cannot report the disagreement.
        n_obs = scalar(con, "SELECT count(*) FROM (SELECT core_id FROM obs GROUP BY core_id) t")
        # ⚑ THE STORE'S COUNTS ARE MEANINGLESS WITHOUT THE CORPUS DENOMINATOR. `core_fp 168`
        # reads like completeness until you know the tree holds thousands — and every
        # per-core figure derived from the store (`--spread`'s 152, the reflection census,
        # the drain sizing) is scoped to whatever fraction was ingested. Reporting the
        # numerator alone is how a PARTIAL ingest reads as a finished one.
        import glob as _glob
        import os as _os

        _base = _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
            "agda",
            "_build",
        )
        on_disk = len(_glob.glob(_os.path.join(_base, "**", "*.agdai"), recursive=True))
        print(
            "core_fp %s core(s) · obs %s core(s) · on disk %s"
            % (
                format(n_fp, ","),
                format(n_obs, ","),
                format(on_disk, ",") if on_disk else "(none found)",
            )
        )
        if on_disk and n_fp < on_disk:
            print(
                "  ⚑ PARTIAL INGEST — %s of %s cores (%.0f%%). Every per-core figure in "
                "this store\n     is scoped to that fraction, NOT to the corpus."
                % (format(n_fp, ","), format(on_disk, ","), 100.0 * n_fp / on_disk)
            )
        print()
        if not fp_only and not obs_only:
            print("  every core has BOTH a fingerprint and observations — no holes")
        if fp_only:
            # ⚑ AN EMPTY CORE AND AN INTERRUPTED ONE ARE BOTH "fp, no obs" AND ARE OPPOSITE
            # FACTS, so this must not be reported as one population. A module that DEFINES
            # NOTHING (the §20 empty-stub class — `Algebra.F2.GF256` is one) correctly
            # produces a fingerprint and zero rows: the ingest did its job. A module that
            # defines names and has no rows is a genuine hole.
            #
            # ⚑ I READ THE FIRST AS THE SECOND, from the alphabetical clustering — 15 of 16
            # under `Algebra/F2/`, which looked exactly like an ingest cut mid-alphabet. The
            # 16th (`Algebra/F1/Capstone`) sorts BEFORE the run and did not fit, which is
            # the only reason I checked instead of banking the story. The clustering is real
            # and means something else: the empty stubs are concentrated in one subtree.
            #
            # ⚑ AND THE PROVIDER IS `agda_defs`, NOT A SECOND SCANNER. It is the name→home
            # authority 19 tools resolve through; a `^name :` scan here would miss
            # constructors and record fields and manufacture "empty" modules that are not.
            import os as _os, subprocess

            _repo = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
            _defs = _os.path.join(_repo, "scratch", "agda_defs.py")

            def _defines(relpath):
                """How many names this core's module provides — None if unaskable."""
                mod = "Substrate." + relpath.replace("/", ".").rsplit(".agdai", 1)[0]
                try:
                    out = subprocess.run(
                        [sys.executable, _defs, "--provides", mod],
                        capture_output=True,
                        text=True,
                        cwd=_repo,
                        timeout=60,
                    )
                    tail = out.stdout.strip().rsplit(":", 1)[-1].strip()
                    return int(tail.split()[0])
                except Exception:
                    return None

            _bucket = {"empty": [], "hole": [], "unclassified": []}
            for r in fp_only:
                p = core_path(r["core_id"], con)
                n = _defines(p)
                _bucket[classify_hole(n)].append((p, n))
            empty, holes, unknown = (_bucket["empty"], _bucket["hole"], _bucket["unclassified"])

            if empty:
                print(
                    "  %s EMPTY MODULE(S) — define no names, so zero rows is CORRECT:"
                    % format(len(empty), ",")
                )
                for p, _ in empty[:20]:
                    print("    %s" % p)
                if len(empty) > 20:
                    print("    … %s more" % format(len(empty) - 20, ","))
                print("    (the ingest did its job; these are not holes)")
            if holes:
                print(
                    "\n  %s GENUINE HOLE(S) — the module defines names and has NO rows:"
                    % format(len(holes), ",")
                )
                for p, n in holes[:20]:
                    print("    %-60s %s name(s)" % (p[-60:], n))
                if len(holes) > 20:
                    print("    … %s more" % format(len(holes) - 20, ","))
                print("\n  ⚑ these must be EXCLUDED from a reconstruct run or re-ingested —")
                print("    a rebuild that finds no rows to compare is not a passing check.")
            if unknown:
                print(
                    "\n  %s UNCLASSIFIED — `agda_defs` could not be asked:"
                    % format(len(unknown), ",")
                )
                for p, _ in unknown[:20]:
                    print("    %s" % p)
                print("    ⚑ unmeasured, NOT empty — do not read this as 'no holes'.")
        if obs_only:
            print(
                "\n  %s OBSERVED, NO FINGERPRINT (rows with no completion record):"
                % format(len(obs_only), ",")
            )
            for r in obs_only[:20]:
                print(
                    "    %-60s %9s rows" % (core_path(r["core_id"], con)[-60:], format(r["n"], ","))
                )
            if len(obs_only) > 20:
                print("    … %s more" % format(len(obs_only) - 20, ","))
        raise SystemExit(0)

    if "--fibre" in sys.argv:
        raise SystemExit(fibre_report())

    if "--growth" in sys.argv:
        raise SystemExit(growth_report())

    if "--headroom" in sys.argv:
        raise SystemExit(headroom_report())

    # ⚑⚑⚑ `--establish` IS `--flush`'s IDEMPOTENT TWIN, AND ITS ABSENCE FORCED AN INLINE SCRIPT.
    # `--flush` DROPs and recreates: correct for resetting a tier, catastrophic for establishing
    # one beside live data. The only route to `apply(con, only=TIER)` — the declared, additive
    # `CREATE TABLE … IF NOT EXISTS` that 28 call sites already use internally — was
    # `python3 -c`, which this repo's own no-chaining hook refuses BY DESIGN: a live DDL write
    # is exactly the judgement that must live in a program rather than evaporate with the turn.
    #
    # ⚑⚑ MEASURED 2026-08-17: `--equiv pack.sql pack.python` stalled twice at 600s and 300s
    # against `relation "obs_node" does not exist`. The verification gate reads a tier only the
    # FOLD establishes, so on a clean tenant the gate cannot run before the thing it verifies —
    # an ordering gap in the arc, not a missing table. This mode is what lets the precondition be
    # met explicitly, by name, instead of as a side effect of the first write.
    #
    # ⚑ IT IS STILL A WRITE, so it honours `--apply` exactly as `--flush` does: bare prints the
    # plan. `IF NOT EXISTS` means a present tier costs nothing and an absent one is created, so
    # re-running is a no-op rather than a reset — the distinction the two modes exist to keep.
    if "--establish" in sys.argv:
        i = sys.argv.index("--establish")
        want = [a for a in sys.argv[i + 1 :] if not a.startswith("-")]
        if not want:
            print("--establish needs at least one tier: %s" % " ".join(sorted(_TIERS)))
            raise SystemExit(2)
        unknown = [t for t in want if t not in _TIERS]
        if unknown:
            print(
                "unknown tier(s): %s\n  known: %s" % (" ".join(unknown), " ".join(sorted(_TIERS)))
            )
            raise SystemExit(2)
        apply_it = "--apply" in sys.argv
        # ⚑ `mode="rw"` ONLY UNDER `--apply`, and the read-only default is a GATE that fired: the
        # first run of this mode died with `ReadOnlySqlTransaction: cannot execute CREATE TABLE`,
        # which is `_cli_connect`'s `ro` default correctly refusing a write from a tool whose
        # other twenty modes are diagnostics. A dry run must not be able to acquire a writable
        # connection at all — otherwise the plan/apply split is a convention rather than a bound.
        con = _cli_connect("rw" if apply_it else "ro")
        # ⚑ `relations()` IS THE EXISTING PRESENCE READER — `--relations` already routes through
        # it, so a second spelling here would be the fourth-parser shape this tree keeps paying
        # for. Read BEFORE, so "created" can be told from "already present".
        _before = set(relations(con))
        if not apply_it:
            for t in want:
                for rel in _TIERS[t]:
                    print("  plan  CREATE TABLE IF NOT EXISTS %s" % rel)
            print("%d tier(s) — re-run with --apply; additive, nothing is dropped" % len(want))
            raise SystemExit(0)
        for t in want:
            apply(con, only=t)
        con.commit()
        # ⚑ REPORT PRESENCE, AND REPORT WHETHER THIS CALL IS WHAT ESTABLISHED IT. "created" and
        # "already present" are different facts and collapsing them is how a no-op reads as work.
        _after = set(relations(con))
        for t in want:
            for rel in _TIERS[t]:
                print(
                    "  %-8s %s"
                    % (
                        "CREATED"
                        if rel in _after - _before
                        else "present"
                        if rel in _after
                        else "ABSENT",
                        rel,
                    )
                )
        raise SystemExit(0)

    if "--flush" in sys.argv:
        i = sys.argv.index("--flush")
        want = [a for a in sys.argv[i + 1 :] if not a.startswith("-")]
        if not want:
            print("--flush needs at least one tier: %s" % " ".join(sorted(_TIERS)))
            raise SystemExit(2)
        apply_it = "--apply" in sys.argv
        try:
            steps = flush(want, dry_run=not apply_it)
        except ValueError as e:
            print(str(e))
            raise SystemExit(2)
        for s in steps:
            print(("  RAN  " if apply_it else "  plan ") + s)
        print(
            "%d step(s) %s; tiers recreated from the declaration"
            % (len(steps), "applied" if apply_it else "— re-run with --apply")
        )
        raise SystemExit(0)

    if "--seed" in sys.argv:
        # ⚑⚑⚑ THIS EXISTS BECAUSE `--verify` COULD NOT BE RUN AGAINST A POPULATION.
        # `query_defs --verify` compares each builder's rows against its ORIGINAL raw SQL —
        # so on an EMPTY tenant both arms return nothing, agree, and the gate reported
        # `PASS — 12/12` having compared nothing. `verify` now says UNMEASURED instead
        # (⟡verify-repair), which converts a false pass into an honest refusal but does not
        # produce a verdict. This is the half that does.
        #
        # ⚑⚑ AND THE DEFAULT SANDBOX IS EMPTY BY CONSTRUCTION, WHICH IS WHY NO SUITE COULD
        # SUPPLY IT. `sandbox_fixture` scopes each case to a PRIVATE schema (`fx_<name>`) and
        # drops it, deliberately — two fixtures sharing a namespace once had the second's
        # `DROP SCHEMA … CASCADE` delete the first's search_path out from under it. So a green
        # `sppf_db --selftest --sandbox` leaves `0 rows total`, correctly. The gate needs the
        # opposite: rows that OUTLIVE the run, in the DEFAULT schema, which is exactly what a
        # fixture must not do. Different lifetimes, so a separate mode rather than a flag on
        # the suite.
        #
        # ⚑ THE DOCUMENT IS `tree_cases`' FIXTURE VERBATIM, AND THAT IS THE WHOLE POINT — it
        # is adversarial in ways a real core cannot be on demand: an empty object BESIDE an
        # empty array, two objects sharing a TAIL but not a head, an array whose tail equals a
        # standalone array, and a key whose text also occurs as a value. A seeder inventing its
        # own document would verify the builders against a population chosen to be easy.
        #
        # ⚑ MUTATION-INTENT, LIKE `--flush`: dry-run by default, `--apply` to write. It DELETEs
        # `core_decoded` first, so it is destructive to the tenant it names — and the tenant is
        # never defaulted (`_cli_connect` → `store.tenant`, which refuses `--sandbox --live`
        # together and warns when neither is stated).
        import json as _json

        apply_it = "--apply" in sys.argv
        _con = _cli_connect(mode="rw")
        _plan = [
            "DELETE FROM core_decoded",
            "INSERT INTO core_decoded … 'fixture/tree.agdai' (the adversarial document)",
            "sppf_vocab.intern_scalars  → dec_scalar",
            "sppf_tree.build_skeleton   → dec_stage",
            "sppf_tree.run_rounds       → dec_node, dec_ref  (to fixpoint)",
            "dec_drain.rebuild_sql      → dec_val  (to fixpoint)",
            "dec_drain.root_sql         → dec_root",
        ]
        # ⚑ THE PLAN PRINTS AS `plan` AND EACH STEP REPORTS `RAN` ONLY AFTER IT RETURNS.
        # A first cut printed all seven as RAN up front and then died on step 3 — seven lines
        # claiming completed work, none of which had happened. `--flush`'s dispatch can print
        # ahead because its steps are strings it then executes in a loop; these are function
        # calls with side effects, so the report has to follow the effect.
        if not apply_it:
            for s in _plan:
                print("  plan " + s)
            print("%d step(s) — re-run with --apply" % len(_plan))
            raise SystemExit(0)
        # ⚑ IMPORTED AT THE SITE, like every other `store`/tool reach in this file's `__main__`.
        # `scripts/` is not on the path at module scope, and the rungs live there.
        import os as _os

        sys.path.insert(
            0,
            _os.path.join(
                _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
                "scripts",
            ),
        )
        import sppf_vocab as _V
        import sppf_tree as _TR
        import dec_drain as _DD

        _doc = {
            "e_obj": {},
            "e_arr": [],
            "tail": {"a": 1, "b": 2, "c": 3},
            "head2": {"A": 9, "b": 2, "c": 3},
            "alone": {"b": 2, "c": 3},
            "arr3": [7, 8, 9],
            "arr2": [8, 9],
            "deep": [[{"k": [1]}]],
            "k": "k",
        }
        execute(_con, "DELETE FROM core_decoded")
        print("  RAN  " + _plan[0])
        execute(
            _con,
            "INSERT INTO core_decoded (core_id, relpath, mtime, dec) "
            "VALUES ('t1', 'fixture/tree.agdai', 1, %s)",
            (_json.dumps(_doc),),
        )
        _con.commit()
        print("  RAN  " + _plan[1])
        _V.intern_scalars(_con)
        _con.commit()
        print("  RAN  " + _plan[2])
        _TR.build_skeleton(_con, None)
        _con.commit()
        print("  RAN  " + _plan[3])
        _TR.run_rounds(_con, None)
        _con.commit()
        print("  RAN  " + _plan[4])
        # ⚑ THE TWO FIXPOINTS ARE THE CALLER'S, NOT THE RUNG'S — `dec_drain`'s seam: the rung is
        # ONE statement and *"the caller runs it until it writes nothing"*. Bounded rather than
        # `while True` so a rung that stopped converging fails loudly here instead of hanging a
        # seeding command; the corpus's max_depth is 4, so 30 is far above any real need.
        for _ in range(30):
            _sql, _p = _DD.rebuild_sql()
            _c = _con.cursor()
            _c.execute(_sql, _p)
            if _c.rowcount == 0:
                break
        _con.commit()
        print("  RAN  " + _plan[5])
        _sql, _p = _DD.root_sql(None)
        _con.cursor().execute(_sql, _p)
        _con.commit()
        print("  RAN  " + _plan[6])
        # ⚑ THE REPORT IS THE POPULATION, PER RELATION — a seeder that printed "done" would be
        # unfalsifiable, and `core_decoded_shadow` is the one that matters: it is the RECONSTRUCTION,
        # so a non-zero count is the only evidence the tiers actually compose.
        for _rel in (
            "core_decoded",
            "dec_scalar",
            "dec_stage",
            "dec_ref",
            "dec_node",
            "dec_val",
            "dec_root",
            "core_decoded_shadow",
        ):
            print("  %-22s %d" % (_rel, scalar(_con, "SELECT count(*) FROM %s" % _rel)))
        _shadow = scalar(_con, "SELECT count(*) FROM core_decoded_shadow")
        if not _shadow:
            # ⚑ AN EMPTY SHADOW MEANS THE TIERS DID NOT COMPOSE, and seeding SUCCEEDED at
            # writing rows nobody can verify against. Exit non-zero: the caller's next command
            # is `--verify`, which would read UNMEASURED and blame itself.
            print(
                "  ⚑ THE SHADOW IS EMPTY — rows were written but the tree does not "
                "reconstruct\n    the document, so `--verify` has nothing to compare. "
                "This is a SEEDING failure."
            )
            raise SystemExit(1)
        print("seeded; `query_defs.py --verify --sandbox` now has a population to compare over")
        raise SystemExit(0)

    if "--core" in sys.argv:
        raise SystemExit(core_report(sys.argv[sys.argv.index("--core") + 1]))

    if "--activity" in sys.argv:
        raise SystemExit(activity_report())

    # ⚑ ONE DISPATCH, TWO MIGRATIONS — `--migrate-views` reuses this block rather than
    # copying it (⟡view-purge). Both answer "reconcile this store's shape with the
    # declaration", both are dry-run-by-default, both return a plan, and both mean
    # RECONCILED by an empty one. A second block would be a second copy of the
    # empty-plan reading that F35 already got backwards once.
    if "--migrate-queue" in sys.argv or "--migrate-views" in sys.argv:
        _views = "--migrate-views" in sys.argv
        apply_it = "--apply" in sys.argv
        steps = (migrate_views if _views else migrate_queue)(dry_run=not apply_it)
        if not steps:
            # ⚑ IT SAID "queue tier already present" — a FORWARD-migration message printed by a
            # migration that now RETIRES the tier, so an empty plan read as *"the thing you are
            # deleting is installed"*. F35's class: the report whose whole job is explaining the
            # state, describing the opposite one. An empty plan means RECONCILED, in whichever
            # direction the steps run.
            print(
                "no view remains — nothing to reconcile"
                if _views
                else "queue tier already retired — nothing to reconcile"
            )
            raise SystemExit(0)
        for s in steps:
            print(("  RAN  " if apply_it else "  plan ") + s.replace("\n", " ")[:150])
        print(
            "%d step(s) %s"
            % (len(steps), "applied" if apply_it else "— re-run with --apply to write")
        )
        raise SystemExit(0)

    # ── `--advance NAME` / `--watermark` / `--retype NAME KIND` — DELETED 2026-08-12 ────────
    #
    # ⚑ `--advance` moved a consumer's cursor to the settled hwm, and its one ⚑ note is kept
    # because it names a conflation, not a mechanism: *"THIS PRESERVED THE EXISTING KIND,
    # because defaulting to 'cursor' silently retyped a PIN and walked past `register`'s
    # pin→cursor guard — **advancing is not retyping**, and the line had conflated them."*
    #
    # ⚑ `--retype` went one step earlier, with `consumer.kind`. It existed because *"the
    # alternative is a raw UPDATE that bypasses the guard"* — **a dangerous operation with no
    # safe command grows an unsafe one**, which is the rule worth keeping. There is no kind, no
    # floor and no registry now, so there is no dangerous operation left for a command to wrap.
    #
    # ⚑ `--watermark` is retired in `schema_queue.py`, where the report lived and where its
    # incident note (a report whose prose contradicted its own figures) is preserved in full.
    if "--reclaim" in sys.argv:
        apply_it = "--apply" in sys.argv
        # ⚑ `reclaim` ALREADY TAKES A CONNECTION; the dispatch simply never passed one, so
        # the only reachable target was the live store. The drain has never run, and the
        # first place to run it is the tenant that exists to be harmed — which was
        # unreachable through the one command that performs it.
        _rc = store.sandbox_connect(reset=False) if "--sandbox" in sys.argv else None
        # ⚑⚑ `--residue` IS GONE BECAUSE THE FORK IT SELECTED IS GONE (2026-08-12). It was
        # added so `q_drainable_res` — the licence `sppf_db --converge` actually deletes
        # under — had a CLI at all; the two settings then ran two DESIGNS, and the default
        # ran the one nothing in production used. `reclaim` now has one licence, so the flag
        # would select between a thing and itself.
        r = reclaim(con=_rc, dry_run=not apply_it)
        print("floor   %s" % ("none" if r["floor"] is None else format(r["floor"], ",")))
        print("obs     %s" % format(r["obs"], ","))
        # ⚑ `edge` IS REPORTED BESIDE `obs` BECAUSE IT IS THE LARGER HALF (⑹, 2026-08-12).
        # `edge` held 627,077 rows — 46% of the store — while `obs` held 0, so a report naming
        # only `obs` describes the smaller relation and reads as the whole sweep. `.get` rather
        # than `[...]`: the `obs_node`-absent REFUSAL returns before either count exists, and
        # that branch must stay printable rather than raising a KeyError over a held sweep.
        print("edge    %s" % ("-" if r.get("edge") is None else format(r["edge"], ",")))
        print("events  %s" % ("-" if r["events"] is None else format(r["events"], ",")))
        print("why     %s" % r["why"])
        raise SystemExit(0)

    # ⚑⚑⚑ ⟡reclaim-core — THE PER-CORE RETIRE, and it exists to be CALLED BY MAKE. `--reclaim`
    # sweeps the whole corpus; the `.drained` stamp needs one core at a time, so that a module
    # is finished when the staged copy it no longer needs has been reclaimed rather than when
    # someone remembers to run a sweep.
    #
    # ⚑⚑ A DISPATCH, BECAUSE A FUNCTION NOTHING CALLS IS THE `rewire_only` SHAPE. `reclaim_core`
    # was written, documented with its own argument, and had ZERO callers — the exact defect
    # `pycodemod`'s docstring opens by recording (*"written, documented with its own
    # 354-consumer justification, and left with ZERO CALLERS — the dispatch branch was never
    # added"*). Adding the branch is the second half of the edit, not a follow-up.
    #
    # ⚑ DRY BY DEFAULT AND `--apply` TO WRITE, like `--reclaim` beside it: this DELETES, and a
    # mutating mode that runs bare is what `--establish`'s guard was built to prevent.
    if "--reclaim-core" in sys.argv:
        _i = sys.argv.index("--reclaim-core")
        _rc_id = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _rc_id is None:
            print(
                "schema.py --reclaim-core <core_id> [--apply] (--live|--sandbox)", file=sys.stderr
            )
            print(
                "  retire ONE core IF the licence admits it. `--packed` names the candidates.",
                file=sys.stderr,
            )
            raise SystemExit(2)
        # ⚑ DEFERRED, LIKE EVERY SIBLING IN THIS BLOCK — `schema_queue` is not bound at module
        # scope here, and `reclaim` above reaches it the same way. MEASURED: a module-level
        # reference raised `NameError: name 'schema_queue' is not defined` on the first run.
        from schema_queue import reclaim_core as _reclaim_core, reclaim_verdict as _rv

        _rcc = _cli_connect(mode="rw" if "--apply" in sys.argv else "ro")
        _r = _reclaim_core(_rc_id, con=_rcc, dry_run="--apply" not in sys.argv)
        print("⟡reclaim-core — %s" % _rc_id)
        # ⚑ `staged_any` IS ASKED OF `obs` DIRECTLY, NOT DERIVED FROM THE DRY RUN'S COUNTS —
        # those count rows MATCHING THE LICENCE, so a refused core reports 0 whatever its
        # staged size. `reclaim_verdict`'s docstring carries the measurement and the defect.
        print(
            "  licensed  %s"
            % _rv(
                _r["licensed"],
                scalar(_rcc, "SELECT 1 FROM obs WHERE core_id = %s LIMIT 1" % ph(), (_rc_id,)),
            )
        )
        print("  obs       %s" % format(_r["obs"] or 0, ","))
        print("  edge      %s" % format(_r["edge"] or 0, ","))
        print("  why       %s" % _r["why"])
        # ⚑ A REFUSED CORE IS NOT AN ERROR. The licence holding a core is the gate working —
        # `converge`'s own note: *"a held core is not an error and must not stall the loop."*
        # Exit 0 either way; the verdict is in the output, not the code.
        raise SystemExit(0)

    if "--lifecycle" in sys.argv:
        raise SystemExit(lifecycle_report())

    if "--transport" in sys.argv:
        # ⚑ THE WRITE PATH'S OWN PROPERTIES, READ FROM THE DRIVER — not asserted about it.
        # This mode exists because "psycopg's executemany does not batch" was stated as fact,
        # built on, and refuted by five minutes in `cursor.py`. A claim about a dependency
        # belongs in a mode that re-derives it on every run, not in a comment that ages.
        for k, v in transport_report().items():
            print("  %-22s %s" % (k, v))
        raise SystemExit(0)

    if "--probe" in sys.argv:
        i = sys.argv.index("--probe")
        got = probe(sys.argv[i + 1])
        for r in got:
            print(" | ".join("%s=%s" % (k, r[k]) for k in r._keys))
        # ⚑ THE TENANT IS REPORTED, NOT ASSERTED. This printed a LITERAL `[sandbox]`, so it
        # could not have told the truth about any other tenant even once the choice was
        # honoured — a label that is right by construction is not a reading. Naming the
        # tenant in the output is the other half of `wrong-tenant-read-is-silent`: the
        # resolver decides, and the report says which it got.
        # ⚑ `_tenant_named` IS THE READER, and it reports `unstated` as its own value
        # rather than collapsing it into a default — which is the distinction the whole
        # tenant ratchet exists to keep. A label saying `unstated` tells the reader the
        # invocation did not choose; `live` would hide that behind the advisory fallback.
        import store as _store

        print("%d row(s) [%s]" % (len(got), _store._tenant_named(sys.argv)))
        raise SystemExit(0)

    if "--plan" in sys.argv:
        # ⚑⚑⚑ "MEASURE WHAT THIS COSTS" AND "INCUR WHAT THIS COSTS" WERE THE SAME OPERATION,
        # AND THAT IS WHY THIS MODE EXISTS.  `query_defs --scans` is documented as *"which
        # relations a builder READS"* — which reads as plan-only — and it runs
        # `EXPLAIN (ANALYZE, FORMAT JSON)`.  `ANALYZE` EXECUTES the query to collect actual
        # row counts.  MEASURED 2026-08-18: reaching for it as a SAFETY probe during a disk
        # incident took the volume 76G → 65G before it was killed, and the backend survived
        # the kill and kept spilling.  A reader reaching for the safe instrument got the
        # hazard.
        #
        # ⚑ `EXPLAIN` WITHOUT `ANALYZE` IS THE WHOLE FIX, and it needs no new machinery:
        # postgres plans from `pg_statistic` and executes NOTHING.  Verified against the
        # exact query that spilled — returned instantly, `df` unchanged to the byte.  The
        # estimated rows and the node types (`HashAggregate`, `Parallel Hash Anti Join`,
        # `Seq Scan`) are what say "this will spill" BEFORE it does.
        #
        # ⚑⚑ AND IT MUST BE THE **LIVE** TENANT, WHICH IS WHY IT IS NOT A `--probe` FLAG.
        # `probe()` is sandbox-only by design, and the sandbox holds ~4 cores against the
        # live store's 93.4M `obs` rows — so a plan taken there reports costs three orders
        # of magnitude too small while looking exactly like an answer.  That is the
        # wrong-tenant read this file records for `--fibre`, and quoting a sandbox
        # `work_mem` as a live one is how the incident's expected-spill was first misread.
        # `_cli_connect` resolves the tenant once and names it in the footer.
        #
        # ⚑ ESTIMATES, NOT MEASUREMENTS, AND THE FOOTER SAYS SO.  A planner estimate can be
        # wrong by orders of magnitude on stale statistics; it is a fact about what postgres
        # BELIEVES, which is the fact that determines the plan it will actually run.  Naming
        # that is the difference between this mode and the one it replaces.
        i = sys.argv.index("--plan")
        if len(sys.argv) <= i + 1:
            print("usage: schema.py --plan <SQL>   (EXPLAIN only — executes nothing)")
            raise SystemExit(2)
        _sql = sys.argv[i + 1]
        # ⚑ REFUSE AN OPERAND THAT ALREADY SAYS `ANALYZE` — the one input that would turn
        # this mode into the hazard it exists to replace, and a caller pasting a statement
        # from `--scans` would do exactly that.
        if "analyze" in _sql.lower():
            print(
                "⚑ REFUSED — the SQL names ANALYZE, which EXECUTES. This mode plans only;\n"
                "  strip it, or use --probe if you genuinely mean to run against the sandbox."
            )
            raise SystemExit(2)
        _pcon = _cli_connect()
        _pcur = _pcon.cursor()
        _pcur.execute("EXPLAIN " + _sql)
        for _r in _pcur:
            print(list(_r.values())[0] if isinstance(_r, dict) else _r[0])
        print(
            "plan only — NOTHING was executed; rows are ESTIMATES from pg_statistic [%s]"
            % ("sandbox" if "--sandbox" in sys.argv else "live")
        )
        raise SystemExit(0)

    if "--cancel" in sys.argv:
        # ⚑⚑ `--sandbox` REACHES THIS MODE, AND ITS ABSENCE WAS A MEASURED DEAD END (⟡ladder-4,
        # 2026-08-13). A runaway statement in the SANDBOX tenant could not be stopped from here
        # at all: `cancel` connected to the LIVE store, whose role does not own that backend, so
        # postgres answered `InsufficientPrivilege: permission denied to cancel query`. The mode
        # was therefore only ever usable against the one tenant an operator is least likely to be
        # experimenting in — the wrong-tenant defect this file already records for the READ
        # modes, present here in the WRITE direction and invisible because the failure looks
        # like a permissions problem rather than like a missing flag.
        #
        # ⚑ AND `cancel` ALREADY TOOK `con=` — the capability was there and nothing passed it.
        # That is `rewire_only`'s shape exactly (a parameter written, documented, never reached),
        # so the fix is one argument and not new machinery.
        # ⚑⚑⚑ AND IT DECLARED `writes=('store',)` WHILE TESTING NEITHER `--apply` NOR
        # `--dry-run` (⟡cancel-mutation-intent, 2026-08-24).  Of the seven modes in
        # `_WRITES_STORE` this was the ONLY one with a silent default — the other six each
        # carry the pair — and it is the one whose mutation is UNRECOVERABLE: `--reclaim`
        # retires rows the durable tier can rebuild, but a cancelled statement is a
        # half-finished promote and `--terminate` drops a connection whose transaction
        # rolls back.  A mistyped PID under a silent default killed whatever backend now
        # holds that number, which under a live swarm is a SIBLING'S writer.
        #
        # ⚑ THE PID IS THE REASON THE GUARD IS NOT MERELY CONVENTIONAL.  Every other
        # mutator here names its target by a stable key (a tier, a core id) that identifies
        # the same object between the read that chose it and the write that acts on it.  A
        # PID does not: `--promotes` prints one, the backend exits, postgres reuses the
        # number, and the operand now denotes a DIFFERENT connection.  `--dry-run` closes
        # exactly that window by RE-READING who the PID currently is before anything stops
        # it — the check the operator was performing in their head, moved into the program.
        i = sys.argv.index("--cancel")
        if len(sys.argv) <= i + 1 or not sys.argv[i + 1].lstrip("-").isdigit():
            print("usage: schema.py --cancel <PID> {--dry-run|--apply} [--terminate] [--sandbox]")
            raise SystemExit(2)
        target = int(sys.argv[i + 1])
        term = "--terminate" in sys.argv
        sbx = "--sandbox" in sys.argv
        apply_ = "--apply" in sys.argv
        dry = "--dry-run" in sys.argv
        verb = "pg_terminate_backend" if term else "pg_cancel_backend"
        if apply_ == dry:
            # ⚑ BOTH IS AS WRONG AS NEITHER — a caller who passed both did not decide, and
            # guessing the safer one still runs a command nobody wrote.
            print(
                "⚑ REFUSED — %s(%d) mutates the %s store and no mutation intent was stated.\n"
                "  pass --dry-run to see WHOSE backend that PID currently is, or --apply to stop it."
                % (verb, target, "sandbox" if sbx else "live")
            )
            raise SystemExit(2)
        # ⚑ DEFERRED, LIKE EVERY OTHER `store` REACH IN THIS FILE — see `_cli_connect`'s note on
        # why module-scope `store` is not available here.
        import store as _cstore

        con = _cstore.sandbox_connect(reset=False) if sbx else None
        if dry:
            # ⚑ A DRY RUN THAT PRINTS THE OPERAND BACK IS VACUOUS.  What the caller cannot
            # check by hand is whether the PID still denotes the backend they read it from,
            # so the dry run READS pg_stat_activity for that PID and shows what would be
            # stopped.  An absent PID is the finding, not an error: it means the statement
            # already ended and the cancel would have hit whatever inherits the number.
            _dcon = con if con is not None else _cli_connect()
            _dcur = _dcon.cursor()
            _dcur.execute(
                "SELECT pid, usename, application_name, state, wait_event_type,"
                "       now() - query_start AS ran_for, left(query, 120) AS query"
                "  FROM pg_stat_activity WHERE pid = %s",
                (target,),
            )
            rows = list(_dcur)
            if not rows:
                print(
                    "⚑ NO BACKEND WITH PID %d on the %s tenant — nothing to stop, and an\n"
                    "  --apply now would act on whatever process next holds that number."
                    % (target, "sandbox" if sbx else "live")
                )
                raise SystemExit(1)
            for r in rows:
                r = (
                    r
                    if isinstance(r, dict)
                    else dict(
                        zip(
                            (
                                "pid",
                                "usename",
                                "application_name",
                                "state",
                                "wait_event_type",
                                "ran_for",
                                "query",
                            ),
                            r,
                        )
                    )
                )
                for k in (
                    "pid",
                    "usename",
                    "application_name",
                    "state",
                    "wait_event_type",
                    "ran_for",
                    "query",
                ):
                    print("   %-18s %s" % (k, r.get(k)))
            print(
                "would %s(%d) — NOTHING was stopped [%s]"
                % (verb, target, "sandbox" if sbx else "live")
            )
            raise SystemExit(0)
        ok = cancel(target, terminate=term, con=con)
        print("%s(%d) -> %s [%s]" % (verb, target, ok, "sandbox" if sbx else "live"))
        raise SystemExit(0 if ok else 1)

    if "--relations" in sys.argv:
        live = relations(_cli_connect())
        for name in sorted(live):
            print("%-28s %s" % (name, live[name]))
        # ⚑ THE BACKEND IS NOT THE TENANT. This printed "N relation(s) in postgres"
        # for both stores, so the one line that could have caught a wrong-tenant read
        # named the ENGINE and not the database — which is why `--fibre --sandbox`
        # could report the live store's 152 cores with nothing looking amiss.
        print(
            "%d relation(s) in %s [%s]"
            % (len(live), store.backend(), "sandbox" if "--sandbox" in sys.argv else "live")
        )
        raise SystemExit(0)

    # ⚑⚑ THE MODE EXISTS BECAUSE THE CAPABILITY ALREADY DID — `columns_of` has been in
    # `schema_rows` with three live consumers, and NO mode exposed it, so "which
    # relations carry a record-version column?" had no reader across 22 declared modes.
    # A dispatched survey named it as a missing tool; it was a missing CLI SURFACE on a
    # function already written, which is the reuse-search result rather than new work.
    #
    # ⚑ THE BARE FORM IS THE POINT.  Per-relation the question is answerable by reading
    # the DDL; ACROSS relations it is not, and "which of the 28 carry `mtime`" is exactly
    # the shape that was being answered by opening files.  A named relation narrows it.
    if "--columns" in sys.argv:
        i = sys.argv.index("--columns")
        want = [a for a in sys.argv[i + 1 :] if not a.startswith("-")]
        con = _cli_connect()
        live = relations(con)
        # ⚑ AN UNKNOWN NAME IS A REFUSAL NAMING THE POPULATION, never an empty listing:
        # a bare "no columns" cannot be told from a relation that exists and has none.
        unknown = [n for n in want if n not in live]
        if unknown:
            print(
                "unknown relation(s): %s\n  known: %s" % (" ".join(unknown), " ".join(sorted(live)))
            )
            raise SystemExit(2)
        targets = want or sorted(live)
        for name in targets:
            cols = columns_of(con, name)
            print("%-28s %s" % (name, " ".join(cols) if cols else "(no columns)"))
        # ⚑ THE TENANT IS NAMED, not the engine — the wrong-tenant read `--relations`
        # records is silent, and a column listing is exactly as silent about it.
        print(
            "%d relation(s) in %s [%s]"
            % (len(targets), store.backend(), "sandbox" if "--sandbox" in sys.argv else "live")
        )
        raise SystemExit(0)

    if "--ddl" in sys.argv:
        i = sys.argv.index("--ddl")
        back = sys.argv[i + 1] if len(sys.argv) > i + 1 else store.backend()
        for s in ddl(back):
            print(s + ";")
        raise SystemExit(0)

    # ⚑ A BARE RUN USED TO DUMP THE WHOLE DDL, which is an ANSWER, not a mode list — so
    # the tool could not tell you what else it could do. Bare now enumerates.
    print(__doc__.strip().splitlines()[0] if __doc__ else "schema.py")
    print("\nmodes:")
    # ⚑ THE TOOL NAME IS ON EVERY MODE LINE, AND THAT IS NOT COSMETIC (2026-08-14).
    # `toolmodes.py` derives a DOCUMENTED mode from a bare-output line that names the tool AND
    # a `--flag`; without the name every mode here landed in the UNDOCUMENTED bucket — visible
    # to `--find` only as *"dispatched, in no usage line"*. Twenty-two real modes described as
    # undeclared is the same false-absence this file's row in the skill table was added to fix.
    # ⚑⚑⚑ ⟡document-modes (2026-08-24) — THIS PRINTED `_MODES`, THE PAIRS, AND THAT WAS THE
    # STRUCTURAL CAUSE OF ALL THREE UNDOCUMENTED MODES.  `--establish`, `--transport` and
    # `--migrate-views` are declared in `MODES` and ONLY there — they were added as
    # post-hoc `Mode(...)` entries precisely because the gate caught them dispatching in no
    # roster.  Paying down the ROSTER left the USAGE untouched, so `toolmodes --divergence`
    # went on reporting three modes *"dispatched on argv, in no usage line and no prose"*
    # while their declarations sat forty lines above, complete and correct.
    #
    # ⚑ SO THE FIX IS NOT THREE MORE PAIRS — that is the two-spellings shape this file keeps
    # retiring (`census-keyed-on-one-spelling`), and it would put each of the three modes'
    # gloss in two places that can disagree.  `MODES` is the authority the gate already
    # checks; the usage block now READS it, so a mode declared anywhere is documented
    # everywhere, and the next post-hoc entry cannot repeat this.
    #
    # ⚑ THE OPERAND IS RE-JOINED TO THE FLAG because `split_flag` took it off — a usage line
    # that prints `--establish` without `TIER…` states an arity the branch refuses, which is
    # the undeclared-arity defect pointed at the READER instead of the entry point.
    # ⚑⚑⚑ THIS PRINTS `_MODES`, THE PAIRS, AND THAT IS DELIBERATE — I CHANGED IT TO `MODES`
    # AND HAD TO CHANGE IT BACK (⟡document-modes, 2026-08-24).  `MODES` is the ROSTER's
    # authority and `check_mode_contracts` reads it by importing this module; `toolmodes
    # --divergence` reads this file's SOURCE for the lines a bare run would print, and a
    # roster entry built at runtime is invisible to it however the bare run renders.  So
    # printing `MODES` fixed what a human sees and moved the census by zero — the three
    # modes stayed UNDOCUMENTED and two modifiers newly joined them.
    #
    # ⚑ THE FIX IS THEREFORE IN THE PAIRS, NOT HERE: every mode has a source-visible entry
    # above, including the three that used to exist only as post-hoc `Mode(...)` rows.  The
    # thing to remember is that a mode is documented when its line is READABLE FROM SOURCE,
    # not when the tool can be made to print it.
    for flag, why in _MODES:
        print("  schema.py %-18s %s" % (flag, why))
    raise SystemExit(0)
