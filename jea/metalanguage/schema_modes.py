# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The `schema.py` CLI-flag roster — `_MODES`/`MODES`, lifted out of `schema.py`.

⚑ EXTRACTED 2026-10-02 (W63, incremental-extraction pass off the `mikemol-pycheck`
refusal on `schema.py` at 662 findings: *"this file cannot be made clean in one edit
… extract the concern you need into a NEW module written clean in one pass, then
retire this file"*). This module carries ONLY the `Mode(...)` declarations — no
dispatch, no CLI printing, no store access. `schema.py` imports `MODES` and `_MODES`
from here instead of defining them inline.

⚑ WHY THIS CONCERN FIRST. It is the most SELF-CONTAINED of `schema.py`'s remaining
regions: the roster depends on nothing else in `schema.py` (no `rows`/`scalar`/
`_cli_connect`, no store connection), and nothing outside the `if __name__ ==
"__main__":` dispatch block reads `_MODES` — only `MODES` is consumed downstream
(by `check_mode_contracts`, `toolmodes`, and `schema.py`'s own usage printing via
`from schema_modes import MODES, _MODES`). A pure-data region is the lowest-risk
cut: nothing here can observe or mutate the postgres store.

⚑ THE SHAPE FOLLOWS THE SIBLING MODULE'S OWN PRECEDENT, ADAPTED. `lifecycle.py`
already declares its own small `_MODES`/`MODES` pair with a `sys.path.insert(...)`
+ `from climode import from_pairs` shim (`climode.Mode` lives in `scripts/`, not
`scratch/`, specifically so a promoted project like this one may import it — see
`schema.py`'s own historical note on `check_scratch_independence`). This module
reaches `scripts/` the same way but through `pathlib.Path` rather than
`os.path.join`/`os.path.dirname`, which is what this file's own zero-finding bar
(PTH118/PTH120) requires of new code even though the sibling predates that bar.
"""

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from climode import Mode, from_pairs

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
        (
            "per-column max/avg OCTET width against the btree key ceiling — the "
            "reader a key-width decision needs. MAX is the constraint, not avg: a "
            "key fails on the ONE row that exceeds it, and bytes ≠ characters"
        ),
    ),
    (
        "--coverage",
        (
            "per DERIVED table: source keys, materialized keys, and BOTH residues — "
            "`owed` (the projection has not run) and `orphan` (rows outliving their "
            "source). One number cannot carry both; they want opposite repairs"
        ),
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
        (
            "the same reading as a SERIES in VictoriaMetrics, through the "
            "shared producer — the store MOVES, so a scalar is stale on arrival"
        ),
    ),
    (
        "--coverage --reap {--dry-run|--apply}",
        (
            "delete ORPHAN keys only, by key, re-derived at the moment of the delete. NOT a "
            "tier flush: no DDL, no DROP, no lock beyond the rows named"
        ),
    ),
    ("--arity", "child-count distribution — is the forest BINARY, or n-ary?"),
    (
        "--packed",
        (
            "which cores are INTERNED and how far — the `--equiv` COMPARISON WINDOW, "
            "where a core is BOTH ingested and projected (both fold arms read obs_node, "
            "so outside that window the gate is vacuous either way)"
        ),
    ),
    ("--flush TIER…", "drop and recreate tiers from the declaration (dry run; --apply)"),
    (
        "--seed",
        (
            "POPULATE a tenant by running the adversarial fixture document through the "
            "REAL rungs — the population `query_defs --verify` compares over, which no "
            "suite can leave behind (its fixtures live in private schemas it drops). "
            "Destructive to the named tenant (dry run; --apply)"
        ),
    ),
    ("--growth", "on-disk size per relation — sees UNCOMMITTED writes that --census cannot"),
    (
        "--headroom",
        (
            "does the volume ADMIT the projected promote? — a bytes/row projection "
            "DERIVED from what obs_node already holds, against BOTH halves of the "
            "ledger: the durable write AND the staged rows the drain retires behind "
            "it. --growth reports what the store OWNS, which reads healthy right up "
            "to an ENOSPC and cannot see the retirement either — sizing a promote on "
            "the write alone makes a space-RECOVERING run read as refused"
        ),
    ),
    ("--activity", "what the store's connections are doing: state, wait event, statement"),
    (
        "--locks",
        (
            "the LIVE-HANG breakdown — pg_locks ⋈ pg_stat_activity: per backend what it "
            "HOLDS vs WANTS, who blocks whom, and whether the wait-for graph has a CYCLE"
        ),
    ),
    (
        "--promotes",
        (
            "what the build is PROMOTING right now, keyed on WHOSE work it is: per "
            "in-flight promote the MODULE (from the backend's own application_name, "
            "never guessed from a bound-$1 query) and its stage, workers folded under "
            "their leader, plus the non-promote backends sharing the tenant — the half "
            "that explains a slow promote when --locks correctly says lock-waiting 0"
        ),
    ),
    (
        "--cancel PID {--dry-run|--apply}",
        (
            "stop a running statement (add --terminate to drop the connection). A PID is "
            "not a stable key — it is REUSED — so --dry-run re-reads pg_stat_activity and "
            "shows WHOSE backend that number currently is, rather than echoing the operand "
            "back"
        ),
    ),
    ("--probe SQL", "run one read against the SANDBOX tenant — ask postgres, don't assert"),
    (
        "--plan SQL",
        (
            "the LIVE plan and ESTIMATED rows, EXECUTING NOTHING — what a query "
            "would cost, without paying it (EXPLAIN, never EXPLAIN ANALYZE)"
        ),
    ),
    ("--lifecycle", "every observation's STAGE and what holds it (the located rejection)"),
    ("--migrate-queue", "retire the queue tier — registry, obs.seq, ix_obs_seq (--apply)"),
    # ⚑ ONE STRING, NOT THREE LINES — this file's code-line budget is HALVED TWICE for two
    # recorded edit-breaks-its-own-region incidents (`_pycodemod_census.INCIDENT_HALVINGS`),
    # so a 300-line cap that a three-line banner entry pushes to 301 is the ratchet doing
    # exactly its job. Paid down by writing the entry, not by editing the table.
    (
        "--reclaim",
        (
            "retire every core the durable tier can rebuild — the per-core licence, "
            "no floor and no pin (dry run; --apply)"
        ),
    ),
    (
        "--reclaim-core ID",
        (
            "retire ONE core if the licence admits it — the make-driven twin of "
            "--reclaim, using the SCOPED licence (drainable_res.one_core) so the "
            "corpus set is never computed to answer about one core "
            "(dry run; --apply). `--packed` names the candidates"
        ),
    ),
    ("--ddl [backend]", "emit the synthesized DDL for a backend (default: the live one)"),
    ("--relations", "what the live store actually holds, per the backend's catalogue"),
    (
        "--columns [REL]",
        (
            "per-relation COLUMN names, from the engine — the reader for "
            "'which relations carry a record-version column'"
        ),
    ),
    (
        "--uniqueness",
        (
            "does the data satisfy every declared UNIQUE index? — the pre-flight "
            "for adding one to a populated store"
        ),
    ),
    (
        "--index-size",
        (
            "per-index on-disk bytes, rows and BYTES/ROW — the figure a key-width "
            "decision needs (--growth reports relations, never indexes)"
        ),
    ),
    (
        "--check-indexes",
        (
            "is every DECLARED index present on this tenant? — the PRECONDITION "
            "that lets a reader assert its access paths instead of a writer "
            "creating them (--index-size reports what EXISTS, never what is OWED)"
        ),
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
        (
            "CREATE the named tiers IF NOT EXISTS — the non-resetting twin "
            "of --flush (dry run; --apply)"
        ),
    ),
    (
        "--migrate-views",
        (
            "reconcile declared VIEWS with the store (⟡view-purge) — the "
            "sibling of --migrate-queue (dry run; --apply)"
        ),
    ),
    (
        "--transport",
        (
            "the write path's own properties, READ FROM THE DRIVER — a claim about "
            "a dependency, re-derived every run"
        ),
    ),
)

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
    why=(
        "per DERIVED table: source keys, materialized keys, and BOTH residues — `owed` "
        "(the projection has not run) and `orphan` (rows outliving their source). One "
        "number cannot carry both; they want opposite repairs"
    ),
)

# ⚑ `--establish` and `--transport` DISPATCH AND WERE IN NO ROSTER — the plain undeclared
# case, found by the gate the moment this file adopted the shape.
# ⚑⚑ ARITY READ FROM THE BRANCH, AND MY FIRST CUT GUESSED IT WRONG. I wrote
# `--establish` as nullary from the NAME; the branch takes one-or-more TIER names and
# exits 2 without them. That is precisely the undeclared-arity defect this
# roster exists to prevent, committed while paying it down — the entry point resolves
# operand binding from here, so a nullary claim would let the next token be read as a path.
# ⚑ THE GLOSS AND THE OPERAND NOW COME FROM THE PAIRS ENTRY (⟡document-modes, 2026-08-24);
# this block adds only `writes`, the field the pair shape cannot carry.  Restating the
# gloss here is what made it a SECOND spelling — see the note at the pairs entry.
MODES["--establish"] = Mode(
    operand=MODES["--establish"].operand, writes=("store",), why=MODES["--establish"].why
)
# ⚑⚑⚑ AND `--transport` I GUESSED WRONG IN THE OTHER DIRECTION — I wrote it as
# `writes=("store",)`, "move rows between tenants", from the name alone. It is a PURE READ:
# it reports the DRIVER's write-path properties, re-derived per run, and
# exists because "psycopg's executemany does not batch" was once asserted as fact and
# refuted five minutes later. Two guesses, two errors, opposite directions — `--establish`
# under-declared its arity and this over-declared its effect. A false `writes` is the worse
# half: it would demand an `--apply` guard on a mode that changes nothing.
MODES["--transport"] = Mode(why=MODES["--transport"].why)  # a PURE READ: no `writes`

# ⚑⚑ `--migrate-views` WAS INVISIBLE UNTIL THE READER LEARNED CO-LOCATED BRANCHES. It
# shares one `if` line with `--migrate-queue` in `schema.py`'s dispatch — deliberately,
# since both reconcile the store's shape with the declaration and a second block would be
# a second copy of the empty-plan reading. `branch_bounds` matched only the FIRST flag on a
# line, so this mode dispatched, mutated the store, and appeared in no roster and no
# finding. Found the moment the reader was fixed for `mdstruct`'s shared
# `--replace-section`/`--append-section` line: one reader defect, two tools, and this one
# was hiding a WRITER.
MODES["--migrate-views"] = Mode(writes=("store",), why=MODES["--migrate-views"].why)
