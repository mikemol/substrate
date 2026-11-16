# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE store authority: where the database is, how to reach it, which dialect it speaks.

⚑ WHY THIS EXISTS — MEASURED, not asserted (2026-08-06). Three defects, one shape:

  * `CATALOG_DB` is derived INDEPENDENTLY in EIGHT modules (`catalog_db`, `sppf_db`,
    `query_defs`, `graded_orbit`, `numpy_builders`, `autocorr_synth`, `reuse_catalog`,
    `reuse_tui`) — and they do not agree: `sppf_db` honours a `SPPF_CATALOG_DB` env
    override that the other seven ignore. That is `agda_files()`-as-four-bodies again,
    one layer down: a shared NAME is not a shared authority.
  * `catalog_db.connect()` exists and has ZERO EXTERNAL CALLERS. All ~56 `connect`
    sites bypass their own chokepoint, so the one place designed to own this owns
    nothing.
  * The DIALECT is hardcoded in two places — `query_defs.run` and
    `query_defs._compile_one`, both `sqlite.dialect(paramstyle="named")`.

⚑ AND THE MIGRATION IS WHY IT CANNOT WAIT. Porting the schema first would replicate
EIGHT hardcoded DSNs where there were eight hardcoded paths — carrying the defect into
the new store rather than leaving it behind. The authority lands first, by measurement,
not by tidiness.

⚑ THE SQLALCHEMY LAYER IS THE MIGRATION PATH, AND IT ALREADY EXISTS (user, 2026-08-06:
*"use the existing SQLAlchemy pattern _everywhere_. Consolidate it."*). MEASURED over
the corpus: **146 compiled-builder sites vs 58 raw-SQL sites**. A Core statement is
dialect-agnostic FOR EVERYTHING SQLALCHEMY MODELS — swapping the dialect ports all 63
builders at one line, because SQLAlchemy owns the per-dialect spelling of a table, a
JOIN, a paramstyle, a LIMIT. A raw string is not: the raw set contains `sqlite_master`
(4 sites), `INSERT OR REPLACE`, `INSERT OR IGNORE`, `GROUP_CONCAT` and `rowid`, none of
which survive contact with PostgreSQL. Consolidating onto Core is how the second set
shrinks.

⚑⚑⚑ BUT "DIALECT-AGNOSTIC BY CONSTRUCTION" IS FALSE AT `func.<name>`, AND THIS FILE
SAID IT FOR MONTHS. `func` passes an ARBITRARY name through VERBATIM — there is no
registry of valid names to check it against, so Core neither translates nor rejects it.
MEASURED (2026-08-19, compile-only probe, no connection):

    func.totally_made_up_xyz(c)  ->  "totally_made_up_xyz(c)"   on postgres AND sqlite
    func.string_agg(c)           ->  "string_agg(c)"            on postgres AND sqlite

An INVENTED name compiles silently, and `string_agg` — perfectly valid postgres — is
indistinguishable from it at compile time. SQLAlchemy has exactly ONE generic registry
(`sqlalchemy.sql.functions._registry["_default"]`, 52 names); everything outside it is
passed through. **So Core is dialect-agnostic exactly UP TO `func.`, and that is where
the line between "ports for free" and "must be rewritten" stops holding.**

⚑⚑ THE COST WAS A WHOLE CAPABILITY DARK, AND TWO INSTRUMENTS GREEN OVER IT.
`autocorr_synth.synth_agda` used `func.group_concat` — the very construct listed three
paragraphs up as one that "[does] not survive contact with PostgreSQL" — and raised
`UndefinedFunction` on EVERY invocation from the migration until 2026-08-19. Nothing
caught it: the sentence above filed GROUP_CONCAT under *raw-SQL* sites (this was a Core
site), and `pycodemod --portable` EXPLAINs raw LITERALS (a Core statement is never a
string, so it reported `0 blocking site(s)` on that file). A rule and a gate, each
correct about what it covered, with the defect in the gap between them.

⚑ THE CENSUS FOR THIS HALF IS `pycodemod --funcnames [--verbatim]`. It grades every
`func.<name>` call `generic` (SQLAlchemy owns the spelling — genuinely ports for free)
or `verbatim` (passed through unchanged: dialect-SPECIFIC and UNCHECKED). Current:
**40 verbatim + 85 generic**. ⚑ A verbatim row is NOT a defect — `jsonb_agg`,
`hashtext`, `convert_from` are legitimately postgres-only in a postgres-only tree — and
the census cannot say a function does not exist, because no per-dialect list exists to
check against. It reports UNVERIFIED-BY-CORE, never WRONG. That is the population a
future migration must re-read by hand, and it is the only place this module's
"ports for free" guarantee does not reach.

WHAT THIS MODULE OWNS
  backend()   — which store this process talks to, from ONE env var
  dsn()       — the connection string / path, resolved per backend
  dialect()   — the SQLAlchemy dialect to compile Core statements against
  connect()   — an open connection, row-factory set, read-only where asked

WHAT IT DELIBERATELY DOES NOT OWN
  The SCHEMA. Table shapes live with the code that builds them (`sppf_db.EVENT_SCHEMA`,
  `SPPF_SCHEMA`). This module answers *where and how*, never *what*.
"""

import os
import sys

# The tenant provisioned on cassian's managed service (docs/operating-postgres.md,
# `host/tenants.tsv`). Database and owning role both take the tenant name.
#
# ⚑⚑⚑ THE TRANSPORT CHANGED (A193, 2026-08-26): pg moved from a rootless quadlet to a k8s
# pod and the UNIX SOCKET IS GONE. The comment here used to read "access is over a UNIX
# socket with no TCP surface and no password" — that was TRUE, was the whole reason `dsn()`
# had no port and no password field, and stopped being true the moment the pod came up.
# Access is now a LOOPBACK-PINNED NodePort with scram-sha-256: verified by cassian that
# `127.0.0.1:30432` answers and the LAN address is REFUSED, so the no-exposure property is
# preserved by the pin rather than by the socket.
#
# ⚑⚑ AND THE PASSWORD IS NOT IN THIS FILE, BY CONSTRUCTION. It is read from the environment
# with NO DEFAULT — a literal here would be a secret in git, and a fallback would let a
# misconfigured caller connect as someone else or fail with the wrong diagnosis. Absent
# env ⟹ `None` ⟹ psycopg omits the key ⟹ the server refuses and SAYS SO. That refusal is
# the correct behaviour: "you have not been given a credential" must not look like "the
# store is down", which is exactly the confusion this file's own `backend()` refusal exists
# to prevent one layer up.
#
# ⚑ PORT IS SEPARATE FROM HOST AND BOTH ARE OVERRIDABLE. Folding `:30432` into PG_HOST would
# make a host override silently drop the port — the shape where one field carries two facts
# and a caller changing one loses the other.
PG_HOST = os.environ.get("SUBSTRATE_PG_HOST", "127.0.0.1")
PG_PORT = int(os.environ.get("SUBSTRATE_PG_PORT", "30432"))
PG_DB = os.environ.get("SUBSTRATE_PG_DB", "substrate")
PG_USER = os.environ.get("SUBSTRATE_PG_USER", "substrate")
# ⚑⚑ A SOURCE, NOT A VALUE — see `_pg_target`. Captured at import, a password is stale the
# moment A197 issues short-lived credentials; a callable re-reads. And no env-var default: the
# operator chose the keyring, and a second source that silently outranks it is the surprise a
# keyring exists to remove.
PG_CREDENTIAL = None  # bound below

# ⚑ THE SANDBOX TENANT — a SECOND database whose whole purpose is being mutated by
# measurement (user, 2026-08-06: *"You can enroll another tenant, this one as a
# sandbox"*).
#
# The problem it dissolves: validating DDL requires EXECUTING it (postgres's `EXPLAIN`
# accepts only DML — measured: `EXPLAIN CREATE TABLE …` → "syntax error at or near
# TEXT"), and executing inside `con.transaction()` does NOT roll back — that context
# manager COMMITS on success, so a probe CREATED a table in the real store and it
# persisted. I read that as "DDL cannot be validated" — treating a property of WHICH
# DATABASE I pointed at as a property of the TECHNIQUE.
#
# With a sandbox the technique is fine: run the DDL, inspect, and the only thing harmed
# is a database that exists to be harmed. ⚑ It is never a source of truth and nothing
# reads it for facts about the corpus; `sandbox_dsn()` is separate from `dsn()` so a
# caller cannot reach it by passing a flag to the normal path.
PG_SANDBOX_DB = os.environ.get("SUBSTRATE_PG_SANDBOX_DB", "substrate_sandbox")
# ⚑ A SEPARATE ROLE MEANS A SEPARATE CREDENTIAL, AND SHARING ONE WOULD DISSOLVE THE TENANT
# SPLIT. The sandbox exists to be harmed; if it could authenticate as `substrate` the "only
# thing harmed is a database that exists to be harmed" guarantee would rest on a `dbname`
# field rather than on the credential. A SOURCE, not a value, for the same reason as the
# live one — and separately sourced, so a vault issuing per-role leases cannot collapse them.
PG_SANDBOX_CREDENTIAL = None  # bound below

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))


def backend():
    """'postgres' — the only store. A REFUSAL, not a selector.

    ⚑⚑ SQLITE IS GONE (⓺, 2026-08-11) AND THIS FUNCTION IS WHAT MAKES THAT LOUD. It
    returned `'postgres' | 'sqlite'` and every consumer branched on the answer; the
    branches are deleted, so the honest thing would be a constant. It is kept as a
    FUNCTION because `SUBSTRATE_STORE=sqlite` still exists — in a shell someone
    exported, in a script, in a habit — and the one behaviour that must not happen is
    for it to be ignored. A stale pin now EXITS naming the migration; it does not
    silently get postgres, and it certainly does not get sqlite.

    ⚑ THE PRIOR VERSION'S OWN NOTE IS WHY. It recorded that the default routed every
    unpinned caller to the tier this file called retired, and that `0 of 30` call sites
    pinned the var — so the default was not one behaviour among several, it was the ONLY
    behaviour. The same reasoning applied one step further says the VARIABLE should stop
    being a selector at all: a knob with one legal setting is not a knob, and leaving it
    readable is how the second value gets re-added.

    ⚑ AND THE MEASURED REASON THE BRANCHES HAD TO GO, not just the store: `ph()`
    dispatched on THIS function's answer rather than on the connection it was binding
    to, so a postgres ambient produced `%s` for a sqlite cursor and a sqlite ambient
    produced `?` for a psycopg one. The second is what broke the Agda write path —
    `demand_imports` failed with *"the query has 0 placeholders but 1 parameters were
    passed"*, four occurrences of one shape. With one backend there is no ambient to
    disagree with, which is why this is a defect-class removal and not a cleanup.
    """
    b = os.environ.get("SUBSTRATE_STORE", "postgres").strip().lower()
    if b != "postgres":
        sys.exit(
            f"store: SUBSTRATE_STORE={b!r} — the only store is 'postgres'.\n"
            f"  ⚑ the sqlite backend was REMOVED (2026-08-11), not merely defaulted\n"
            f"    away from: `ph()`, `upsert()`, `relations()` and `connect()` no\n"
            f"    longer have a sqlite arm. Unset SUBSTRATE_STORE, or set it to\n"
            f"    'postgres'."
        )
    return b


def dsn(back=None):
    """The connection target: the postgres keyword dict.

    ⚑ `back` IS RETAINED AND IGNORED, DELIBERATELY, AND IT IS DEBT WITH A NAME. Thirteen
    functions across `store` and `schema_rows` carry this parameter; it selected an arm,
    and the arms are gone. Removing it is a mechanical sweep over every signature AND
    every positional caller (`ph(1, back)`, `dialect('sqlite')` in the suites), which is
    a second change — so it is recorded here rather than half-done. What matters now is
    that no value of `back` can reach a different store, which is true.

    ⚑ THE PASSWORD RIDES HERE OR NOWHERE. Both tenants derive from `_pg_target`, so the
    transport can never be right for one and stale for the other — the drift `sandbox_dsn`
    was written to prevent, one field over.
    """
    return _pg_target(PG_DB, PG_USER, PG_CREDENTIAL)


def _pg_target(db, user, source):
    """The ONE place a postgres connection target is assembled. Both tenants route here.

    ⚑⚑⚑ `source` IS A CREDENTIAL SOURCE — A CALLABLE — NOT A PASSWORD, AND THAT IS THE WHOLE
    DESIGN (operator, 2026-08-26). The first cut of this function took a password STRING read
    from a module constant at import. That is the right shape for a static secret and the
    WRONG one for what is coming: A197 migrates this store to OpenBao-issued credentials that
    are SHORT-LIVED, so a value captured at import is a value that expires while the process
    holds it. A string cannot be re-fetched; a callable can.
    #
    ⚑⚑ AND THE MIGRATION DOES NOT REMOVE A SECRET, IT RELOCATES ONE. Authenticating to a vault
    needs its own credential — a token or an AppRole secret-id — which is LONGER-lived than
    the pg password, grants everything the vault holds rather than one database, and by
    construction cannot itself be fetched from the vault. So "wait for OpenBao and the
    credential question goes away" is false: the question moves and gets sharper. Building the
    seam now, against a low-stakes interim password, is how the high-stakes one arrives into
    an existing shape rather than a fourth spelling.
    #
    ⚑ CALLED AT ASSEMBLY TIME, EVERY TIME. `dsn()` is already documented as un-memoised for
    the `reread-meters-toctou` reason; that argument was about the ENVIRONMENT changing under
    a cached read, and it applies with more force to a lease that expires on a clock. A source
    returning a fresh value per call is what makes a re-connect after expiry a re-fetch rather
    than a restart.
    #
    ⚑ AN ABSENT CREDENTIAL OMITS THE KEY RATHER THAN PASSING `None` OR `""`. psycopg treats a
    present-but-empty password as an ATTEMPT — the server then refuses with an authentication
    error, which reads as "wrong credential" when the truth is "no credential was ever
    supplied". Omitting the key lets libpq say what actually happened. Two absences needing
    different repairs must not produce one message; that is the ABSENT-vs-BROKEN distinction
    `vfs.Presence` exists for, applied to a DSN.
    """
    t = {"host": PG_HOST, "port": PG_PORT, "dbname": db, "user": user}
    secret = source() if callable(source) else source
    if secret:
        t["password"] = secret
    return t


def redacted_dsn(t):
    """A connection target safe to PRINT — the credential replaced, never dropped.

    ⚑⚑⚑ A REPORTER THAT WAS SAFE BECAME A LEAK THE MOMENT THE DSN GAINED A SECRET, and it
    did so silently. `schema_diag.census_report` prints the whole dict as its footer — correct
    and harmless while `dsn()` was `{host, dbname, user}`, and on the first successful connect
    after A193 it printed the live password to stdout, in a census mode any agent or hook may
    run. ⚑ NOTHING CHANGED IN THE REPORTER. The invariant it relied on — "this dict holds no
    secrets" — was never written down, so nothing could notice when it stopped holding.
    #
    ⚑⚑ SO THE REDACTION LIVES HERE, WITH THE ASSEMBLER, NOT AT THE CALL SITES. A helper each
    printer must remember to call is a discipline; `dsn()` and `sandbox_dsn()` have at least
    four consumers between them and the next one will not know. What this CAN do is make the
    safe form available beside the real one and say why.
    #
    ⚑ IT SUBSTITUTES RATHER THAN DELETES. A dropped key reads as "no credential is configured",
    which is a DIFFERENT fact and one an operator debugging an auth failure would act on — the
    same absent-vs-present collapse `_pg_target` refuses one function up. `***` says a secret
    is there and is not being shown.
    """
    return {k: ("***" if k == "password" else v) for k, v in t.items()}


def _keyring_credential(service, account):
    """Credential source: the operator's keyring. ⚑ THE KEYRING, NOT AN ENV FALLBACK.

    ⚑⚑⚑ THE FIRST CUT OF THIS READ `os.environ` FIRST AND FELL BACK TO THE KEYRING, AND THAT
    WAS THE WRONG ANSWER TO A QUESTION THAT HAD ALREADY BEEN DECIDED. The operator chose the
    keyring (2026-08-26: *"keyring, for now; openbao isn't up yet"*) after weighing env
    explicitly; re-admitting env as a "scoped override" put the rejected option back on the
    path and dressed it as a feature. ⚑ AND IT WAS NOT INERT: an env var silently outranking
    the stored credential is exactly the surprise a keyring exists to remove — two sources for
    one secret, with the weaker one winning and nothing saying so.
    #
    ⚑⚑ ONE SOURCE IS ALSO WHAT MAKES A197 A ONE-FUNCTION REPLACEMENT. A vault fetch replaces
    THIS; it does not have to also reason about an env var that may or may not shadow it.
    A second source would have to be retired before the migration could land — the seam would
    have bought less than it cost.
    #
    ⚑ A MISSING BACKEND AND A MISSING KEY ARE DIFFERENT ANSWERS AND THIS DOES NOT COLLAPSE
    THEM. `keyring get` exits 1 with NO MESSAGE for both — measured, in the tool itself — so a
    caller reading the CLI cannot tell "you have not stored a credential" from "there is no
    keyring here". At the library level they separate: an absent key returns None, an unusable
    backend RAISES. This returns None for the first (the caller then omits the password key and
    libpq says what happened) and lets the second surface AS ITSELF, because the repairs
    differ: place a secret, versus run somewhere with a session bus.
    #
    ⚑ IMPORTED LAZILY. `store.py` is on the pre-commit path (`check_import_shape` → … → here)
    and `keyring` pulls in D-Bus machinery; a module-level import would make every gate run pay
    for a dependency only a connect needs. The same laziness `vfs` gives pygit2 — and it keeps
    a broken backend from being an IMPORT error, which would take down readers that never
    connect.
    #
    ⚑ TO PLACE ONE: `python3 -m keyring set <service> <account>`.
    """

    def _read():
        try:
            import keyring as _kr
        except ImportError:
            return None  # declared dep absent — behave as "no credential"
        return _kr.get_password(service, account)

    return _read


def credential_backend():
    """WHICH keyring backend answers — the third state `_keyring_credential` could not report.

    ⚑⚑⚑ THIS MODE EXISTS BECAUSE THE OPERATOR WAS PROMPTED FOR A PASSWORD BY A STORE THEY HAD
    NEVER CHOSEN (2026-08-26: *"I keep getting prompted for my keyring password. Somehow it's
    not routing to my kde wallet, which is already unlocked."*). `keyring` SELECTS a backend at
    call time by priority over whatever is importable, so a working, unlocked KWallet and a
    `keyrings.alt` encrypted FILE are BOTH "a keyring present" — and the file backend has its
    own separate passphrase. **The prompt was not KWallet asking; it was a second store asking.**
    #
    ⚑ SO THE DOCSTRING ABOVE HAD THE RIGHT DISTINCTION AND STILL MISSED THIS CASE. It separates
    an absent KEY (returns None) from an unusable BACKEND (raises) — two states, correctly. The
    third is a backend that is present, usable, and THE WRONG ONE: it neither returns None nor
    raises, it succeeds against a store nobody meant to use. A credential placed here would be
    real, retrievable, and invisible to KWallet — findable only by asking which backend answered.
    #
    ⚑⚑ AND IT IS THE `the-holder-is-not-the-worker` SHAPE. `PG_CREDENTIAL` names the SERVICE and
    ACCOUNT — the thing being asked for — and says nothing about WHO answers. The roster keyed
    the request; the responder was never named, so the report could not distinguish two stores.
    #
    ⚑ REPORTS PRESENCE, NEVER ABSENCE. It names the backend that WOULD answer and, per account,
    whether a secret is retrievable — it does not claim a secret is unset anywhere else. A
    `keyring` that cannot even be imported is itself an answer, returned as such.
    """
    try:
        import keyring as _kr
    except ImportError:
        return {"backend": None, "detail": "keyring not importable — declared dep absent"}
    kr = _kr.get_keyring()
    cls = type(kr)
    name = f"{cls.__module__}.{cls.__name__}"
    accounts = {}
    for account in (PG_USER, PG_SANDBOX_DB):
        try:
            accounts[account] = "present" if _kr.get_password("substrate-pg", account) else "absent"
        except Exception as exc:  # an unusable backend surfaces AS ITSELF
            accounts[account] = f"backend error: {type(exc).__name__}: {exc}"
    return {"backend": name, "priority": getattr(kr, "priority", None), "accounts": accounts}


# ⚑ THE INTERIM INHABITANTS. Bound here rather than at the constants above because they need
# the source constructors, and a forward reference would be the ordering bug this file already
# carries a comment about elsewhere. ⚑⚑ A197 REPLACES THESE TWO LINES AND NOTHING ELSE — that
# is the measure of whether the seam was worth introducing.
#
# ⚑ THE SERVICE/ACCOUNT PAIR NAMES THE ROLE, NOT THE HOST. A credential is scoped to a postgres
# ROLE; keying it on `127.0.0.1:30432` would strand it the next time the transport moves — which
# it did today, socket → NodePort, and will again at A197.
PG_CREDENTIAL = _keyring_credential("substrate-pg", PG_USER)
PG_SANDBOX_CREDENTIAL = _keyring_credential("substrate-pg", PG_SANDBOX_DB)


def sandbox_dsn():
    """The SANDBOX tenant's connection target — what `sandbox_connect` actually opens.

    ⚑ THIS EXISTS BECAUSE A TOOL PRINTED THE WRONG TENANT'S NAME BESIDE THE RIGHT TENANT'S
    ROWS. `schema.py --census --sandbox` read the sandbox correctly and then labelled the
    output `dbname: substrate`, because the only DSN accessor was the live one. A caller
    that wants to NAME the tenant it read had no way to ask, so it named the other one —
    and a footer that can disagree with its own table is worse than one that is simply
    absent, since the disagreement is invisible unless you already know the answer.

    ⚑ DERIVED FROM THE SAME CONSTANTS `sandbox_connect` USES, never a second spelling: the
    two must not be able to drift, or the label becomes wrong again by a different route.
    """
    return _pg_target(PG_SANDBOX_DB, PG_SANDBOX_DB, PG_SANDBOX_CREDENTIAL)


# ⚑ NO `tune()`. I wrote one — a guard that applied `PRAGMA journal_mode=WAL` and
# `PRAGMA busy_timeout=120000` on sqlite and no-op'd on postgres — and it was the wrong
# instinct (user, 2026-08-06: *"we can actually remove any sqlite3-specific tuning
# material. Shifting to pgsql is happening in part because we hit a wall on what can
# actually be done with sqlite3 tuning, and I don't want the shape of sqlite3 holding us
# back in that way"*).
#
# The reasoning I had was "preserve the sqlite path so it does not silently regress."
# That is correct maintenance of a backend that is STAYING, and this one is not: those
# PRAGMAs exist because sqlite serialises writers at the FILE level, and working around
# that ceiling is part of why the store is moving at all. Keeping the workaround keeps
# the constraint — a compatibility shim for the thing being left behind quietly makes it
# a peer again.
#
# PostgreSQL needs no per-connection concurrency setup: MVCC makes concurrent writers the
# normal case. There is nothing to translate, so there is nothing to keep.


def sandbox_reset(con):
    """Drop every relation in the sandbox, so a probe starts from empty.

    ⚑ A PROBE WHOSE VERDICTS DEPEND ON ITS OWN HISTORY IS NOT A PROBE. The portability
    census executes DDL here to validate it; without a reset the SECOND run sees tables
    the FIRST run created and reports `DuplicateTable` — MEASURED: `CREATE TABLE core_fp
    (…)` came back as a defect purely because an earlier census had already created it.
    The same source, censused twice, gave two different answers.

    ⚑ VIEWS BEFORE TABLES, and `CASCADE` on both: a view depends on the tables it selects
    from, so dropping tables first would fail on the dependency — and a partial reset is
    worse than none, since it leaves exactly the ambiguity this exists to remove.
    """
    cur = con.cursor()
    cur.execute("""
        SELECT table_name, table_type FROM information_schema.tables
         WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    """)
    rels = [
        (r["table_name"], r["table_type"]) if isinstance(r, dict) else (r[0], r[1])
        for r in cur.fetchall()
    ]
    for name, kind in rels:
        if kind == "VIEW":
            cur.execute(f'DROP VIEW IF EXISTS "{name}" CASCADE')
    for name, kind in rels:
        if kind != "VIEW":
            cur.execute(f'DROP TABLE IF EXISTS "{name}" CASCADE')
    return len(rels)


#: ⟡runtime-tenant-lens — every store OPEN this process performed, in order.
#: (opener, tenant, mode, label, caller) — see `_lens_record`.
_LENS = []


def _lens_record(opener, tenant, mode, label):
    """Record that a store connection was OPENED. ⟡runtime-tenant-lens.

    ⚑⚑⚑ IT OBSERVES OPENS RATHER THAN INFERRING THEM, AND THAT IS THE WHOLE POINT.
    Two SOURCE censuses already existed — import-reach and call-site — and they are
    CORRELATED: both ask which code *mentions* a store API, so both share `sql-F23`'s
    blind spot, a reacher whose tenant is unsayable because it never calls `tenant`.
    Their agreeing was therefore not coverage (`correlated-instruments-agreeing-is-not-
    coverage`). MEASURED: `pycodemod`'s `_pg_probe_con` held a live read-WRITE handle
    inside the pre-commit selftest roster and was invisible to `--calls tenant` for
    exactly that reason — found on a seventh careful read. A runtime lens is decorrelated
    by construction: it cannot miss an open, because it IS the open.

    ⚑⚑ THERE ARE EXACTLY THREE OPENERS AND THIS SITS IN ALL THREE. `tenant`, `connect`
    and `sandbox_connect` are the complete roster (`psycopg.connect` appears nowhere else
    in the tenant path), so the lens is TOTAL over this module rather than sampled. A
    fourth opener added later is the thing to guard: it must call this, and its absence is
    the defect to look for — not a reason to treat the lens as approximate.

    ⚑⚑ NO OPT-OUT FROM BEING OBSERVED (`gate-F24`). Recording is UNCONDITIONAL and
    in-process — no env var suppresses it, because a lens with a bypass measures only the
    callers who did not use the bypass, which is the population that needed no lens. What
    IS env-gated is only the EXPORT sink (`SUBSTRATE_TENANT_LENS`), and a sink is not the
    observation: with it unset the record still exists and `lens_report()` still reads it.

    ⚑ IT CANNOT CHANGE A VERDICT. Best-effort throughout, swallowing every failure and
    returning None — same contract as `ratchet.log_fallthrough`, and for the same reason:
    these paths run inside pre-commit gates, and an instrument that can fail a commit is
    worse than no instrument. It also never opens a connection of its own, which would
    make the lens a fourth reacher measuring itself.
    """
    import os as _os
    import sys as _sys

    try:
        # the CALLER, not this frame — which file reached the store.
        caller = ""
        try:
            f = _sys._getframe(2)
            caller = f"{_os.path.basename(f.f_code.co_filename)}:{f.f_lineno}"
        except Exception:
            pass
        _LENS.append((opener, tenant, mode, label or "", caller))
        if _os.environ.get("SUBSTRATE_TENANT_LENS"):
            print(
                f"⟡lens open opener={opener} tenant={tenant} mode={mode} "
                f"label={label or '-'} caller={caller or '-'}",
                file=_sys.stderr,
            )
    except Exception:
        pass
    return None


def lens_report():
    """The opens this process performed — the decorrelated census. ⟡runtime-tenant-lens.

    ⚑ A CALLER THAT OPENED NOTHING AND A CALLER NOT UNDER THE LENS BOTH RETURN []. The
    lens is total over `store.py`, so within a process that imported this module the empty
    list is a real zero; across processes it is not, which is why a runner reads this
    per-process rather than aggregating a global.
    """
    return list(_LENS)


def sandbox_connect(reset=True):
    """A connection to the THROWAWAY tenant — safe to mutate, never a source of truth.

    `reset=True` (the default) empties it first; see `sandbox_reset` for why that is the
    default rather than an option a caller must remember.

    ⚑ A SEPARATE FUNCTION, NOT A FLAG ON `connect()`. A `connect(sandbox=True)` would put
    the real store one boolean away from a probe that creates and drops tables; keeping
    the entry points distinct means reaching the sandbox is a deliberate act at the call
    site, and a reader can see which database a function touches without tracing an
    argument.

    ⚑ POSTGRES ONLY. A sqlite "sandbox" is just another file, and callers wanting one
    already use `:memory:` — offering a sqlite path here would imply the two are
    interchangeable when the sandbox exists specifically to answer POSTGRES questions.
    """
    import psycopg
    from psycopg.rows import dict_row

    _lens_record("sandbox_connect", "sandbox", "rw", "")
    con = psycopg.connect(
        host=PG_HOST,
        dbname=PG_SANDBOX_DB,
        user=PG_SANDBOX_DB,
        row_factory=dict_row,
        autocommit=True,
    )
    if reset:
        sandbox_reset(con)
    return con


def engine_url(back=None):
    """A SQLAlchemy Engine URL for the store.

    ⚑ A FOURTH SPELLING OF THE BACKEND EXISTED and this retires it: `autocorr_synth`
    built `sqlite:///<path>` by hand, so it kept reading the OLD store after a
    migration while every other reader followed `SUBSTRATE_STORE`. Its queries would
    still have returned plausible rows — the silent-wrong-answer shape, which is worse
    than a crash because nothing reports it. That is why the URL is CONSTRUCTED here
    even now that there is only one of them: the defect was a second spelling, not a
    second backend, and one spelling is what prevents it.
    """
    # ⚑⚑⚑ THIS WAS THE FOURTH SPELLING'S OWN BLIND SPOT (A193, 2026-08-26). The body read
    # `postgresql+psycopg://{PG_USER}@/{PG_DB}?host={PG_HOST}` — an EMPTY NETLOC with the
    # socket DIRECTORY in a query param, which is libpq's convention for a unix socket and
    # carried NO PORT AND NO PASSWORD. When pg moved to a TCP NodePort, `dsn()` was repaired
    # and this was not: every SQLAlchemy consumer (`autocorr_synth`, `graded_orbit`) would
    # have kept failing while `connect()` worked, and the docstring above is the reason —
    # the defect it records is A SECOND SPELLING, and a second spelling repaired on only one
    # of its paths is the same defect wearing a fix.
    #
    # ⚑ SO IT IS DERIVED FROM `_pg_target`, NOT RE-ASSEMBLED. The URL and the keyword dict
    # cannot now disagree about host, port, database, user or credential — which is the
    # property the whole function exists to hold, extended to the fields it did not have.
    from urllib.parse import quote as _q

    t = _pg_target(PG_DB, PG_USER, PG_CREDENTIAL)
    auth = _q(str(t["user"]), safe="")
    if t.get("password"):
        auth += ":" + _q(str(t["password"]), safe="")
    return f"postgresql+psycopg://{auth}@{t['host']}:{t['port']}/{t['dbname']}"


def dialect(back=None):
    """The SQLAlchemy dialect Core statements compile against.

    ⚑ THIS IS THE WHOLE POINT OF THE SQLALCHEMY LAYER. `query_defs` bound
    `sqlite.dialect(paramstyle="named")` in TWO places — `run()` and `_compile_one()` —
    so the compiled cache and the live executor could in principle drift apart while
    both looked correct. One authority, both consumers.

    ⚑ `paramstyle="pyformat"` IS NOW THE ONLY ONE, AND THE OLD NOTE HERE IS THE REASON
    THE SWAP WAS SURVIVABLE. It read: *"`named` is retained for BOTH dialects
    deliberately: psycopg3 accepts `%(name)s` and SQLAlchemy's postgres dialect emits
    that under `named`, so the runtime's dict-of-params contract is unchanged across the
    swap."* That held the two arms to ONE runtime contract, which is what let the sqlite
    arm be deleted without touching a single caller's parameter dict.
    """
    from sqlalchemy.dialects import postgresql

    return postgresql.dialect(paramstyle="pyformat")


#: The two ways an invocation may NAME its tenant.  Both spellings exist so that neither
#: is a default: `--sandbox` was already the throwaway selector, and `--live` is the half
#: that was MISSING — which is exactly what made its absence mean "live" silently.
TENANT_FLAGS = ("--sandbox", "--live")


def _tenant_named(argv):
    """Which tenant this argv NAMES: 'live' | 'sandbox' | 'unstated' | 'both'.

    ⚑ SPLIT OUT SO THE CONTRACT IS TESTABLE WITHOUT A STORE.  `tenant()` opens a
    connection, so a case driving it would need postgres up and would be asserting the
    connection rather than the DECISION.  This is the decision alone — pure, total, and
    the thing the cases actually pin.  `tenant()` is its only production caller.
    """
    stated = [f for f in TENANT_FLAGS if f in argv]
    if len(stated) == 2:
        return "both"
    if not stated:
        return "unstated"
    return "sandbox" if stated[0] == "--sandbox" else "live"


def tenant(argv=None, mode="ro", label="", require=None):
    """The store THIS invocation names — REFUSING if it named neither.

    ⚑⚑⚑ NO DEFAULT TENANT (operator, 2026-08-18: *"I've seen many errors because
    something inspected sandbox when it meant to inspect the main thing. And when
    something modified the main thing when it meant to go to sandbox. Or when something
    simply forgot to care."*).  THREE failure modes, and the third is the one a default
    guarantees: **forgetting to care is indistinguishable from choosing.**

    ⚑⚑ AND THE MISSING HALF IS THE MECHANISM.  Before this there was no `--live` flag
    anywhere in the toolkit — only `--sandbox`, with `else connect()` as the silent
    other branch.  An option that does not exist cannot be stated, so "no flag" MEANT
    live and nobody had to decide.  Adding `--live` is what makes the tenant sayable;
    the refusal is only enforceable once both spellings exist.

    ⚑ MEASURED IN BOTH DIRECTIONS, which is why neither branch may be the default:
      * READ HIT THE WRONG TENANT — `--fibre --sandbox` reported *"152 cores, every core
        positional"* over a sandbox holding ONE.  The live store's answer, printed under
        the sandbox's question.  `_cli_connect`'s own note: a write to the wrong tenant
        is loud, a READ just returns plausible rows nobody can distinguish.
      * SANDBOX READ AS LIVE — a `--probe` plan returned `rows=124772` from the
        sandbox's ~4 cores against live's 93,439,732: three orders of magnitude low,
        and *looking exactly like an answer*.

    ⚑⚑⚑ THE REFUSAL IS THE DEFAULT AS OF 2026-08-24 (⟡tenant-mandatory).  Operator:
    *"I want target-tenant to be specified from the CLI **manditorially**, not
    advisorially. It is an error not to specify. And that error is worth forcing on."*
    An unstated tenant now EXITS 2 with no env var involved.

    ⚑⚑ AND `SUBSTRATE_EXPLICIT_TENANT` IS GONE ENTIRELY — its role did not invert, it
    ENDED.  It used to be how strictness was turned ON; leaving it readable in any
    direction would leave a silent route back to "default to live", which is how a policy
    decays into an advisory again.  The variable is no longer consulted here: setting it
    is inert, and unsetting it does not restore the old behaviour.

    ⚑ WHY THE ADVISORY PHASE ENDED RATHER THAN COMPLETED.  The prior note said *"warn
    now, measure the population, refuse when it is paid down — a ratchet over a census"*.
    That inverts the operator's ruling: the BREAKAGE IS THE CENSUS.  A refusal names each
    offending site precisely, at the moment it runs, with its own label — which is a
    better census than `log_fallthrough` could produce, because a warning that nothing
    consumes is a census nothing acts on (`ratchet.store_argv`'s own docstring says so).
    Keeping it advisory to preserve a green suite is the ABSENT-baseline free pass in
    policy form.

    ⚑ THE ONE SURVIVING OPT-OUT IS `require=`, AND IT IS NOT A BYPASS.  `require="live"` /
    `"sandbox"` STATES the tenant IN CODE for a caller whose tenant is not the operator's
    to choose — a fixture, or a mode meaningless against one of them.  It does not skip
    naming a tenant; it names one at a different site, and that site is greppable, typed,
    and refuses an unrecognised value rather than passing (a typo would otherwise satisfy
    the contract silently).  Same escape as `edit_snapshot.guard(intent=…)`.  There is no
    opt-out that leaves the tenant UNNAMED, by construction: `named` has no fourth arm.
    """
    import os as _os
    import sys as _sys

    if require is not None:
        if require not in ("live", "sandbox"):
            print(
                f"⚑ {label or 'tenant'}: require={require!r} is not 'live' or 'sandbox'.",
                file=_sys.stderr,
            )
            _sys.exit(2)
        named = require
    else:
        argv = _sys.argv if argv is None else argv
        named = _tenant_named(argv)
        if named == "both":
            # ⚑ BOTH IS ALWAYS AN ERROR, even in advisory mode: two contradictory
            # intents, and no reading of that is safe.
            print(
                f"⚑ {label or 'tenant'}: BOTH --sandbox and --live given — they are "
                f"mutually exclusive. Refusing rather than picking one.",
                file=_sys.stderr,
            )
            _sys.exit(2)
        if named == "unstated":
            msg = (
                f"⚑ {label or 'tenant'}: neither --sandbox nor --live was given.\n"
                f"  A read that hits the wrong tenant returns PLAUSIBLE ROWS nobody "
                f"can distinguish;\n  a write that does is worse. State one."
            )
            # ⚑ THE CENSUS IS KEPT THOUGH THE ADVISORY PHASE IS OVER, and the reason is
            # that the two answer different questions.  The refusal tells THIS invocation
            # what it did wrong; `log_fallthrough` accumulates WHICH SITES keep doing it,
            # across runs, in one stream — the only thing that can say whether the
            # population is shrinking.  Deleting it with the advisory would trade a
            # measured paydown for a per-run error message.  Best-effort; the exit below
            # is unconditional and never depends on whether this emitted.
            try:
                _sys.path.insert(
                    0,
                    _os.path.join(
                        _os.path.dirname(
                            _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
                        ),
                        "scripts",
                    ),
                )
                import ratchet as _r

                _r.log_fallthrough(
                    label or "tenant", "unstated-tenant", known=TENANT_FLAGS, argv=argv, exit_code=2
                )
            except Exception:
                pass
            # ⚑ UNCONDITIONAL.  No env var, no bare-run exemption, no "defaulting to
            # LIVE as before" — that last clause is the one that had to go, because it
            # made the error message itself the documentation for how to keep ignoring
            # it.  A caller that legitimately has no operator-chosen tenant passes
            # `require=`, which is a code change at a named site, not an environment.
            print(
                msg + "\n  Pass --live or --sandbox.  A caller whose tenant is not the "
                "operator's to choose\n  states it in code: tenant(require='live'|"
                "'sandbox').",
                file=_sys.stderr,
            )
            _sys.exit(2)
    # ⚑ THE LABEL TRAVELS TO THE BACKEND HERE. `tenant` already takes it for its refusal
    # messages; passing it on is what turns a name this process knows into a name the
    # STORE can be asked. The sandbox arm keeps its own signature — a throwaway tenant
    # has no in-flight population worth attributing.
    # ⚑ THE RESOLUTION, NOT A SECOND OPEN. `tenant` delegates to the other two openers,
    # which record their own row; this records HOW the tenant was chosen (`flag` vs
    # `require=`), which is the fact neither delegate can see. A reach whose row shows
    # opener=connect with no preceding tenant row is one that bypassed the contract —
    # which is precisely the `_pg_probe_con` shape this lens was built to catch.
    _lens_record("tenant", named, "require" if require is not None else "flag", label)
    # ⚑⚑⚑ BIND THE TENANT AS A PER-INVOCATION AMBIENT (⟡intent-contextvar).  THIS IS THE
    # EXISTING AUTHORITY GAINING A CHANNEL, NOT A SECOND RESOLVER — `tenant()` was already
    # THE resolver and stays so; what it could not do was make its answer visible to code
    # that never called it.  MEASURED: `pycodemod --calls tenant` reports 14 calls while
    # `--calls connect` reports 59, so most reaches never pass through here at all.
    #
    # ⚑⚑ WHICH IS EXACTLY ⟡index-coverage-wrong-store.  `_live_indexed` opened
    # catalog.db (sqlite, two weeks stale) while `_selectivity` read live postgres — TWO
    # STORES IN ONE REPORT, with every PRAGMA returning nothing, the OperationalError
    # swallowed, and the relations defaulting to `candidate`.  A false positive in the
    # direction that GENERATES WORK (32 candidates → 26 once coverage read one store).
    # NOBODY PASSED A WRONG FLAG: two functions each resolved the tenant independently and
    # disagreed.  Under a WRITE-ONCE ambient the first resolution is the answer and the
    # second RAISES, naming the site that already bound it — which needs no cooperation
    # from either site, and is why this is the right shape and refuse-on-comparison was
    # not (neither of those two routed through a comparison, which is why it shipped).
    #
    # ⚑ BEST-EFFORT AND CANNOT ALTER THE VERDICT.  `edit_snapshot` lives in `scratch/`,
    # which is not always importable from every consumer of this module; a tenant that
    # cannot be published must not break a connection that is otherwise correct.  The
    # AmbientConflict is deliberately allowed to propagate — that one IS the finding.
    try:
        import sys as _s2, os as _o2

        _s2.path.insert(
            0,
            _o2.path.join(
                _o2.path.dirname(_o2.path.dirname(_o2.path.dirname(_o2.path.abspath(__file__)))),
                "scratch",
            ),
        )
        import edit_snapshot as _es2

        if _es2.TENANT.get() is None:
            _es2.TENANT.set(named, f"store.tenant({label or 'unlabelled'})")
        elif _es2.TENANT.get() != named:
            # ⚑ A SECOND, DISAGREEING RESOLUTION. Raise through the shared authority so
            # the message, the successors and the write-once semantics are stated once.
            _es2.TENANT.set(named, f"store.tenant({label or 'unlabelled'})")
    except ImportError:
        pass
    return sandbox_connect(reset=False) if named == "sandbox" else connect(mode=mode, label=label)


def connect(mode="ro", *, require=True, back=None, label=""):
    """An open connection to the store.

    mode='ro'      the caller INTENDS only to read (see below — not enforced)
    mode='rw'      read-write (the projection/builders)
    require=True   accepted and inert; there is no longer a file that can be absent
    label=''       what this connection IS — published as `application_name`

    ⚑⚑ `label` EXISTED AND STOPPED AT THE PROCESS BOUNDARY, WHICH IS THE WHOLE DEFECT.
    Every `tenant(label=…)` caller already names itself, and that name was used only for
    this process's own stderr — so from INSIDE the store a backend was anonymous.
    MEASURED 2026-08-23: five `--promote-core` processes ran 1–3.5h and answering *which
    module is that backend promoting* required reading raw `pg_stat_activity` and matching
    SQL text by eye, because `application_name` was empty on every connection in the
    tenant (`--calls application_name store.py` → 0 sites). The identity was known at the
    call site and thrown away one layer before the only place that needed it.

    ⚑ PUBLISHED, NOT DERIVED. A reader that infers the caller from query TEXT is guessing
    — `INSERT INTO _ht_map` says which STAGE, never which module, since `core_id` travels
    as a bound `$1` the view renders unexpanded. Two spellings of one fact is the census-
    keyed-on-one-spelling shape; this makes the backend carry its own name.

    ⚑ `mode='ro'` IS NOT ENFORCEABLE AT ALL NOW, AND SAYING SO IS THE HONEST MOVE. The
    prior note recorded that `ro` meant two DIFFERENT guarantees: sqlite got a genuine
    read-only URI connection that the engine refused writes on, while postgres gets a
    per-transaction `SET TRANSACTION READ ONLY` against a tenant role that OWNS its
    database — so a determined writer still writes. Dropping the sqlite arm therefore
    removes the STRONGER of the two guarantees, and a caller that was relying on it is
    now relying on an intent. That is a real loss, recorded rather than papered over:
    the flag says what this caller means to do, not what the engine will permit.
    """
    import psycopg
    from psycopg.rows import dict_row

    # ⚑ THE LENS FIRES BEFORE THE SOCKET, so an open that FAILS is still observed. A
    # recorder placed after the connect would be blind to exactly the reachers that
    # crash — and "it errored" is a fact about a reach that happened.
    _lens_record("connect", "live", mode, label)
    con = psycopg.connect(**dsn(back), row_factory=dict_row)
    # ⚑⚑⚑ A KILLED CLIENT DOES NOT STOP ITS QUERY, AND THAT IS WHAT MADE EVERY MISTAKE
    # COST DISK RATHER THAN BEING FREE.  Closing the socket does not cancel work already
    # running: postgres notices only when it next tries to WRITE to the client, which a
    # long aggregate does not do until it finishes.  MEASURED 2026-08-18, THREE TIMES in
    # one incident — `TaskStop` killed the python process and the backend kept executing
    # and kept spilling, in each case caught only by checking `--activity` on reflex and
    # cancelling by pid.  A cancelled investigation that keeps costing is the reason a
    # cheap mistake became an expensive one.
    #
    # ⚑ `client_connection_check_interval` IS POSTGRES' OWN ANSWER, and it is a SESSION
    # GUC, so it needs no server change and no privilege: the backend polls the socket
    # every N ms during execution and aborts when the client is gone.  10s is chosen to
    # be far below the minutes a runaway costs and far above any plausible poll cost.
    #
    # ⚑ SET ON EVERY CONNECTION, NOT ONLY THE `ro` ARM — a writer orphaned mid-statement
    # is strictly worse than a reader, since it holds a transaction the whole time.  This
    # is a REAPING guarantee, not a read/write distinction.
    #
    # ⚑ AND IT IS BEST-EFFORT BY CONSTRUCTION: the GUC is unsupported on some builds and
    # a no-op where the platform cannot poll, so a failure here must never make the store
    # unreachable.  Absent it, the manual mitigation stands (check `--activity` after any
    # kill) — which is exactly the attention-layer remedy this is meant to replace.
    #
    # ⚑⚑ IT RUNS **AFTER** THE MODE FLAGS, NOT BEFORE, AND THE ORDER IS LOAD-BEARING.
    # `SET` is a statement, so issuing it first opens an implicit transaction and psycopg
    # then refuses `read_only` outright: `ProgrammingError: can't change 'read_only' now:
    # connection in transaction status INTRANS`.  Caught on the first invocation after
    # this edit — a reaping guarantee that makes the store unreachable is worse than the
    # orphan it prevents.
    if mode == "ro":
        con.read_only = True
        # ⚑⚑ WITHOUT THIS A READ HOLDS AN OPEN TRANSACTION UNTIL THE PROCESS EXITS.
        # psycopg opens an implicit transaction on the first statement and keeps it
        # until commit/close, so a CLI read mode that queries and then goes back to
        # Python sits `idle in transaction` holding every lock it touched.  MEASURED
        # 2026-08-18: one selftest backend sat there **25 minutes** on a `ClientRead`
        # wait holding ~80 `AccessShareLock`s, during an incident where a DDL writer
        # would have been the recovery path.
        #
        # ⚑ AND `--locks` REPORTED `lock-waiting 0`, WHICH WAS TRUE.  Nothing was
        # blocked *yet* — an AccessShareLock conflicts only with AccessExclusive, so
        # the hold is invisible until someone needs DDL, and then it is a hang whose
        # cause left no trace in the instrument.  The same footprint-not-headroom
        # shape as the incident it sat inside: a correct answer to the question the
        # tool asked, not the one that mattered.
        #
        # ⚑ SAFE PRECISELY BECAUSE IT IS THE `ro` ARM.  Autocommit removes the
        # transaction WRAPPER, not any guarantee this mode had: a read-only caller
        # spans no multi-statement invariant, and `mode="rw"` is untouched, so the
        # projection/builder paths keep their explicit transactions.  A per-statement
        # snapshot is what a census wants anyway — a long-lived one would report
        # figures from whenever the connection opened.
        con.autocommit = True
    try:
        con.execute("SET client_connection_check_interval = '10s'")
    except Exception:
        pass
    # ⚑ SAME BEST-EFFORT CONTRACT, SAME PLACE, AND FOR THE SAME REASON as the GUC above:
    # after the mode flags (a `SET` opens an implicit transaction, which `read_only`
    # then refuses), and never able to make the store unreachable. An unnamed backend is
    # a diagnostic gap; a failed connection is an outage.
    #
    # ⚑ TRUNCATED TO 63 BYTES BECAUSE POSTGRES DOES IT SILENTLY OTHERWISE (NAMEDATALEN-1).
    # A module path is routinely longer than that, and a silent truncation would make two
    # different modules present as one identical `application_name` — a reader could not
    # tell the collision from a genuine repeat. Truncating HERE, visibly, keeps the
    # ambiguity where it can be seen and documented rather than manufactured in the server.
    if label:
        try:
            con.execute("SELECT set_config('application_name', %s, false)", (str(label)[:63],))
        except Exception:
            pass
    return con


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ⚑ THE BACKEND SELECTOR REFUSES A TYPO rather than falling back. A silent fallback
    # to sqlite would let a migration test read the OLD store and report success.
    _saved = os.environ.get("SUBSTRATE_STORE")
    try:
        # ⚑ THE UNSET CASE IS THE ONLY ONE THAT TESTS THE DEFAULT, and the case that
        # stood here did not: labelled "default backend resolves", it SET
        # SUBSTRATE_STORE=sqlite first and then asserted `backend() == "sqlite"` — an
        # explicit-value case wearing the default's label. It passed identically before
        # and after the default flipped from sqlite to postgres, so the one property it
        # named was the one property it could not see. Measured: 0 of 30 call sites pin
        # the var, so the default IS the behaviour of the whole tree.
        os.environ.pop("SUBSTRATE_STORE", None)
        check("UNSET defaults to postgres (the live store)", backend(), "postgres")
        os.environ["SUBSTRATE_STORE"] = "postgres"
        check("postgres selectable", backend(), "postgres")
        # ⚑⚑ THE SQLITE CASE INVERTED, AND THAT INVERSION IS THE DELIVERABLE OF ⓺. It
        # read *"sqlite still selectable (comparison against the retired tier)"* and
        # asserted `backend() == "sqlite"`. A removal that left this case passing would
        # mean the backend was still reachable; a removal that merely DELETED it would
        # leave `SUBSTRATE_STORE=sqlite` silently answering "postgres" — the shape where
        # a stale pin in someone's shell gets ignored instead of reported. So the case
        # stays and asserts the opposite: the value that used to select the retired
        # store now REFUSES.
        os.environ["SUBSTRATE_STORE"] = "sqlite"
        try:
            backend()
            check("SUBSTRATE_STORE=sqlite now REFUSES", "returned", "SystemExit")
        except SystemExit:
            check("SUBSTRATE_STORE=sqlite now REFUSES", "SystemExit", "SystemExit")
        os.environ["SUBSTRATE_STORE"] = "postgre"  # a plausible typo
        try:
            backend()
            check("a typo'd backend REFUSES", "returned", "SystemExit")
        except SystemExit:
            check("a typo'd backend REFUSES", "SystemExit", "SystemExit")
    finally:
        if _saved is None:
            os.environ.pop("SUBSTRATE_STORE", None)
        else:
            os.environ["SUBSTRATE_STORE"] = _saved

    # ── tenant(): the contract is the PAIR, and neither side may be a default ────
    # ⚑ DRIVEN ON A CONSTRUCTED argv, NEVER `sys.argv` — a case reading the process
    # argv would pass because of how the SUITE happens to be invoked, which is the
    # "explicit-value case wearing the default's label" defect recorded above, one
    # function over.  These assert the RESOLUTION, not the connection: opening one
    # would make the suite depend on a live store being up.
    check("`--live` names the live tenant", _tenant_named(["t", "--live"]), "live")
    check("`--sandbox` names the throwaway", _tenant_named(["t", "--sandbox"]), "sandbox")
    # ⚑ THE MISSING HALF IS THE FINDING: before `--live` existed, "no flag" MEANT live
    # and nobody had to decide.  This case pins that the absence is NAMED — `unstated`
    # is a fourth answer, not a silent fallthrough to live.
    #
    # ⚑⚑ WHAT THIS CASE DOES **NOT** WITNESS, AND THE OLD COMMENT HERE CLAIMED OTHERWISE.
    # It said *"it still resolves live (advisory today), but it is reported rather than
    # silent"* — a STATUS restated in a comment, which `tenant()`'s own docstring had
    # already contradicted since 2026-08-24 (⟡tenant-mandatory: the refusal is
    # unconditional and `SUBSTRATE_EXPLICIT_TENANT` is gone entirely).  A reader auditing
    # this suite concluded the mechanism was advisory when it is mandatory.
    # `fresh-comments-are-hypotheses-too`: the comment was written after the advisory
    # phase and never re-derived when the phase ENDED.  ⚑ SO IT NOW CITES ITS AUTHORITY
    # RATHER THAN RESTATING ONE — read `tenant.__doc__` for what happens on `unstated`;
    # this line deliberately does not say, because saying it is what let it drift.
    #
    # ⚑⚑⚑ AND `_tenant_named` IS A DIFFERENT FUNCTION FROM `tenant`, WHICH IS THE WHOLE
    # DEFECT (Ⓐ8 ⟡store-selftest-blind).  Every tenant case here drove the NAMING helper,
    # so the suite passed 17/17 whether or not `tenant()` refused at all — a green
    # unrelated to the claim a reader takes from it.  The case below drives `tenant`.
    check("NEITHER is detected, not silently defaulted", _tenant_named(["t"]), "unstated")
    # ⚑ A LONGER FLAG CONTAINING THE SPELLING MUST NOT SATISFY IT — `--live-only` is a
    # different flag, and reading it as consent is the substring defect this repo has
    # recorded on operand handling.
    check(
        "a longer flag containing `--live` does NOT state the tenant",
        _tenant_named(["t", "--live-only"]),
        "unstated",
    )

    # ── tenant() ITSELF REFUSES — the cases the four above could not witness ─────────
    # ⚑⚑⚑ Ⓐ8 ⟡store-selftest-blind.  THE FOUR CASES ABOVE ARE ALL ABOUT `_tenant_named`,
    # and a suite that only drives the naming helper cannot see whether the REFUSAL is
    # installed.  Measured 2026-08-24: `store.py --selftest` read 17/17 while asserting
    # nothing about `tenant()`, so removing the `_sys.exit(2)` at the `unstated` arm left
    # the suite green — the `census-green-is-a-fact-about-the-census` shape, in the
    # tenant authority every tool in the tree reads.
    #
    # ⚑⚑ HOW THESE ARE ESTABLISHED TO DISCRIMINATE, WHICH IS THE POINT OF ADDING THEM.
    # Not by argument: by RUNNING the suite against a `tenant` whose refusal is disabled.
    # `_no_refusal` below monkeypatches `_sys.exit` — the exact call the refusal makes —
    # so the `unstated` arm falls through instead of exiting, which is precisely what a
    # revert of ⟡tenant-mandatory would do.  Under that patch these cases FAIL and the
    # four `_tenant_named` cases still PASS.  That is the negative control the ledger's
    # own `sql-F13-fixture-is-not-a-negative-control` says an assertion must have before
    # it may be trusted: *"a green from an instrument is a fact about the instrument's
    # INPUT as much as its logic"*.
    #
    # ⚑ NO STORE IS OPENED.  `tenant()` exits at the `unstated` arm BEFORE `_lens_record`
    # and before any connect, so these cases cannot depend on a live store being up —
    # the same constraint the four cases above state for themselves.  `argv` is
    # CONSTRUCTED, never `sys.argv`, for the same reason they are.
    def _refuses_tenant(name, argv=None, **kw):
        """PASS iff `tenant(...)` raises SystemExit. A RETURN is the failure."""
        try:
            tenant(argv=argv, **kw)
            check(name, "returned — the refusal is GONE", "SystemExit")
        except SystemExit:
            check(name, "SystemExit", "SystemExit")

    _refuses_tenant("an UNSTATED tenant REFUSES (not defaults to live)", ["t"])
    # ⚑ THE SUBSTRING ARM, DRIVEN THROUGH `tenant` RATHER THAN THE HELPER — a longer flag
    # must not satisfy the contract at the REFUSING site either, since that is the site
    # whose bypass would matter.
    _refuses_tenant("`--live-only` does not satisfy the refusal", ["t", "--live-only"])
    # ⚑ BOTH IS AN ERROR TOO, and it is a DIFFERENT arm of the same function — an
    # implementation that refused only `unstated` would pass the case above and still be
    # wrong.  Two arms make the case-set discriminate on the arm, not just the function.
    _refuses_tenant("BOTH --live and --sandbox REFUSES", ["t", "--live", "--sandbox"])
    # ⚑ AND THE `require=` ESCAPE REFUSES AN UNRECOGNISED VALUE rather than passing it
    # through — the docstring calls this out as the reason `require=` is not a bypass, so
    # it is asserted rather than left to be discovered. A typo must not satisfy the
    # contract silently.
    _refuses_tenant("require= with an unrecognised value REFUSES", ["t"], require="livee")

    # ── the runtime tenant lens: TOTAL over this module, or it is not a lens ─────────
    # ⚑⚑ Ⓐ4b. `_lens_record`'s docstring names exactly one thing to guard — *"a fourth
    # opener added later ... must call this, and its absence is the defect to look for"* —
    # and nothing checked it.  sql-F32's original witness was a scratchpad script that no
    # longer exists, so the claim "the lens is total over the three openers" had no
    # standing reader at all: `store.py --selftest` mentioned the lens nowhere.
    #
    # ⚑ THIS ASSERTS THE ROSTER, NOT A CALL COUNT IN THE ABSTRACT.  A grep-shaped "there
    # are 3 calls" would pass if someone moved one of them into a helper and added a
    # fourth opener that skips it. Asserting the SET of function names that reach
    # `_lens_record` is the property the docstring actually claims.
    _openers = set()
    for _fn in (tenant, connect, sandbox_connect):
        _co = _fn.__code__
        if "_lens_record" in _co.co_names:
            _openers.add(_fn.__name__)
    check(
        "the lens is wired into ALL THREE openers",
        sorted(_openers),
        ["connect", "sandbox_connect", "tenant"],
    )
    # ⚑ AND RECORDING IS UNCONDITIONAL — `gate-F24`, no opt-out from being observed. Only
    # the EXPORT SINK is env-gated, so with `SUBSTRATE_TENANT_LENS` unset the record must
    # STILL exist. A lens whose observation is suppressible measures only the callers who
    # chose not to suppress it, which is the population that needed no lens.
    _lens_before = len(lens_report())
    _saved_sink = os.environ.pop("SUBSTRATE_TENANT_LENS", None)
    try:
        _lens_record("probe", "sandbox", "ro", "selftest")
        _rows = lens_report()
        check("the lens records with the export sink UNSET", len(_rows) - _lens_before, 1)
        # ⚑ INDEX GUARDED, AND THE NEGATIVE CONTROL IS WHY. Written as `_rows[-1][:4]` this
        # raised IndexError under the sink-gated revert instead of reporting FAIL — the
        # suite DIED mid-run, which is strictly worse than a red case: it also skips every
        # case after it, so one regression hides the others. A case must fail, never crash,
        # on the very state it exists to detect.
        check(
            "the recorded row carries opener/tenant/mode",
            _rows[-1][:4] if len(_rows) > _lens_before else "NOTHING RECORDED",
            ("probe", "sandbox", "ro", "selftest"),
        )
    finally:
        if _saved_sink is not None:
            os.environ["SUBSTRATE_TENANT_LENS"] = _saved_sink

    # ⚑ ONE DIALECT, AND THE ARGUMENT IS NOW IGNORED — which this asserts rather than
    # leaves to be discovered. The retired case read `dialect("sqlite").name ==
    # "sqlite"`; the danger in deleting it is that `dialect("sqlite")` still LOOKS like
    # it selects something. Asserting that the retired argument yields the postgres
    # dialect is the only case that can catch an arm being quietly restored.
    dp = dialect("postgres")
    check("postgres dialect is postgresql", dp.name, "postgresql")
    check("the retired argument is INERT, not honoured", dialect("sqlite").name, "postgresql")

    # ⚑ THE DSN IS A KEYWORD DICT FOR EVERY ARGUMENT. It used to be a filesystem PATH
    # under sqlite and a dict under postgres — two different TYPES from one function,
    # which every caller had to branch on. One shape is the removal's other half.
    # ⚑⚑ THESE TWO PINNED A KEY ROSTER AND THE TRANSPORT CHANGED UNDER THEM (A193,
    # 2026-08-26): pg moved to a k8s NodePort, `port` joined the dict, and both cases went
    # red against a CORRECT dsn. They were right to fire — a silent shape change in the
    # tenant authority is what they exist to refuse — but a literal roster fails on every
    # legitimate addition and stays green while the MEANING rots, which is the wrong
    # polarity. Assert the invariant: the identity keys are present, and no value is None.
    _d = dsn()
    check("dsn carries the tenant identity", {"dbname", "host", "user"} <= set(_d), True)
    check(
        "⚑ no dsn value is None (an absent field is OMITTED, never passed empty)",
        [k for k, v in _d.items() if v is None],
        [],
    )
    check("the retired argument does not change the dsn SHAPE", sorted(dsn("sqlite")), sorted(_d))

    # ⚑⚑⚑ THE LEAK THAT ACTUALLY HAPPENED, PINNED. On the first successful connect after the
    # store gained TCP auth, `schema.py --census --live` printed the live password in its
    # footer — a census mode any agent or hook may run. Nothing in the reporter changed; the
    # unwritten invariant it relied on ("this dict holds no secrets") stopped holding, and
    # nothing could notice. These cases are what notice.
    # ⚑ STARVED BOTH WAYS with a synthetic secret, so the check cannot pass because the
    # environment happens to hold no credential — an all-clear that has never been shown to
    # differ from a found-something is not a measurement.
    _fake = {"host": "h", "port": 1, "dbname": "d", "user": "u", "password": "s3cr3t"}
    check("⚑ redacted_dsn removes the secret", "s3cr3t" in str(redacted_dsn(_fake)), False)
    check(
        "⚑ ...and SUBSTITUTES rather than drops it (absent ≠ present-but-hidden)",
        "password" in redacted_dsn(_fake),
        True,
    )
    check(
        "⚑ ...and leaves every non-secret field readable",
        [redacted_dsn(_fake)[k] for k in ("host", "port", "dbname", "user")],
        ["h", 1, "d", "u"],
    )
    check(
        "⚑ a credential-free dsn is unchanged by redaction",
        redacted_dsn({"host": "h", "dbname": "d"}),
        {"host": "h", "dbname": "d"},
    )

    # ⚑ THE ENGINE URL IS A SEPARATE SURFACE and needs its own case: `autocorr_synth`
    # reached the store through `create_engine`, not `connect`, so a fix that only
    # covered `connect` would have left one module reading the old store. Asserting the
    # SCHEME is what distinguishes the two — a case checking "a string is returned"
    # would pass against a hardcoded sqlite URL, which is exactly the defect.
    check(
        "postgres engine url uses the psycopg driver",
        engine_url("postgres").startswith("postgresql+psycopg://"),
        True,
    )
    # ⚑⚑ THIS CASE READ *"carries the socket dir as a host param"* AND WENT STALE WITH THE
    # TRANSPORT — it asserted `"host=" in url`, the libpq unix-socket spelling, which a TCP
    # URL does not use. It passed for the wrong reason right up to the move. The invariant
    # that survives a transport change: the URL and the keyword dict must not DISAGREE.
    check(
        "⚑ the engine url and the dsn agree on the target",
        (
            str(dsn()["host"]) in engine_url("postgres"),
            str(dsn()["port"]) in engine_url("postgres"),
            engine_url("postgres").endswith("/" + str(dsn()["dbname"])),
        ),
        (True, True, True),
    )

    # ⚑ A Core STATEMENT STILL COMPILES, AND THE RENDERED PARAMSTYLE IS STILL ASSERTED.
    # The retired case read *"the SAME Core statement must compile under BOTH — that is
    # the migration property in one assertion"*, and it did its job: the 63 builders
    # were portable, which is why the sqlite arm could be deleted at all. What survives
    # it is the half that is still checkable — that the ONE dialect renders `%(name)s`,
    # because that is the string psycopg binds on and the exact thing `ph()` was getting
    # wrong when it dispatched on the ambient backend.
    from sqlalchemy import MetaData, Table, Column, String, select

    _md = MetaData()
    t = Table("core_fp", _md, Column("core_id", String), Column("mtime", String))
    stmt = select(t.c.core_id).where(t.c.mtime == "x")
    p_sql = str(stmt.compile(dialect=dp))
    check("a Core stmt compiles under postgres", "core_fp" in p_sql, True)
    check("postgres renders %(name)s", "%(mtime_1)s" in p_sql, True)
    # ⚑ AND THE NEGATIVE HALF: the sqlite paramstyle must not appear. A case asserting
    # only what IS rendered passes against an emitter that renders both.
    check("...and NOT the sqlite :named style", ":mtime_1" in p_sql, False)

    bad = [c for c in cases if not c[1]]
    for label, _, got, want in bad:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    if "--credential-backend" in sys.argv:
        # ⚑ WHICH store answers, not merely whether one does — see credential_backend.
        info = credential_backend()
        print(f"backend  : {info['backend']}")
        if info.get("priority") is not None:
            print(f"priority : {info['priority']}")
        if "detail" in info:
            print(f"detail   : {info['detail']}")
        for acct, state in info.get("accounts", {}).items():
            print(f"  substrate-pg/{acct} : {state}")
        raise SystemExit(0)
    b = backend()
    print(f"backend : {b}")
    print(f"dsn     : {redacted_dsn(dsn(b))}")  # ⚑ never the raw dict — see redacted_dsn
    print(f"dialect : {dialect(b).name}")
