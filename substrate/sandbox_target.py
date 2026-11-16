#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Assemble the SANDBOX tenant's postgres connection target (Ⓝ92b ⟡drain-store).

⚑⚑⚑ THIS EXISTS BECAUSE THE SANDBOX CONNECTOR ASSEMBLED A SECOND TARGET BY HAND AND IT WENT
STALE. `jea/metalanguage/store.py` documents its `_pg_target` as *"the ONE place a postgres
connection target is assembled"* and its `sandbox_dsn` as *"DERIVED FROM THE SAME CONSTANTS
`sandbox_connect` USES, never a second spelling: the two must not be able to drift"* — and
`sandbox_connect` was nonetheless a second spelling, naming host, database and role while
supplying NO port and NO credential. When the store moved to k8s and the host listener was
retired, the sole-authority accessor followed the cutover and the hand-rolled one did not: the
redacted-DSN reporter showed the NodePort while a sandbox census failed against the driver's
default port with `connection refused`. ⚑ THE DOCSTRING FORBIDDING THE DRIFT SAT ONE FUNCTION
ABOVE THE DRIFT, which is why the repair is a module and not a comment.

⚑⚑ AND THE ONE-LINE FIX COULD NOT BE APPLIED IN PLACE. That file carries a frozen census of lint
and type findings, and the per-file gate has no partial-credit path — an edit leaving it dirty is
refused and reverted, so a substitution that would have strictly improved it was refused with
everything else. The gate's own guidance names the route taken here: extract the concern into a
NEW module written clean in one pass, and let consumers import that. The monolith stays frozen;
the repair lands, and each consumer moves independently.

⚑ IT IMPORTS NOTHING FROM `jea/`, AND THAT IS LOAD-BEARING, NOT AESTHETIC. A module extracted out
of that package but still NAMING it inherits the untyped hub through the import and cannot be made
clean — measured on this tree, where the sibling extraction that succeeded did so precisely
because it reached back for nothing. So the settings and the credential source are RE-DERIVED here
from the same environment variables rather than imported. That duplicates a few `os.environ`
reads deliberately: the alternative is not "no duplication", it is "no repair".

⚑⚑ THE DUPLICATION IS PARTITIONED BY TENANT, NOT BY FIELD, WHICH IS WHAT KEEPS IT HONEST. This
module re-derives the SANDBOX target only. A copy covering both tenants would be a genuine second
authority for the whole store; covering the one tenant whose accessor is ALREADY documented as
separate — so a caller cannot reach it by passing a flag to the normal path — keeps the seam where
it was already drawn. The live target keeps its single authority and is untouched by this module.

⚑ A CREDENTIAL SOURCE IS A CALLABLE, NEVER A CAPTURED STRING, which is copied from the existing
assembler's design rather than reinvented: a value read at import is stale the moment short-lived
issued credentials arrive, and a string cannot be re-fetched while a process holds it. The keyring
is the ONE source — no environment fallback, because a variable silently outranking the stored
credential is the exact surprise a keyring exists to remove.

⚑ AN ABSENT CREDENTIAL OMITS THE KEY RATHER THAN SUPPLYING AN EMPTY ONE. The driver treats a
present-but-empty password as an ATTEMPT, so the server refuses with an authentication error that
misreports "none was ever supplied" as "wrong credential". Omitting the key lets the driver say
what actually happened — two absences needing different repairs must not collapse into one
message.

⚑ THE DRIVER IS NOT IMPORTED HERE AND NO CONNECTION IS OPENED. The older connector interleaved
target assembly, credential lookup and the `psycopg` call in one function, which is what let the
transport drift unnoticed — nothing could check the target without a live server. Assembly is
pure and total, so it is checkable on its own; a caller passes `target().keywords()` to whichever
connect it already uses. That also keeps this module importable on the pre-commit path without
pulling a database driver behind it.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

import keyring

from substrate import store_endpoint

if TYPE_CHECKING:
    from collections.abc import Callable

#: The sandbox tenant's transport and identity. Read from the environment on every assembly rather
#: than frozen at import: a cached read cannot notice a cutover, and an unnoticed cutover is
#: exactly the failure this module was written to repair.
HOST_VAR = "SUBSTRATE_PG_HOST"
PORT_VAR = "SUBSTRATE_PG_PORT"
DB_VAR = "SUBSTRATE_PG_SANDBOX_DB"

HOST_DEFAULT = "127.0.0.1"
#: ⚑ THE CONSUMER PATH IS THE NODEPORT. The host's own listener was retired when the store moved
#: to k8s, so falling through to the driver's default port is precisely the defect this replaces.
PORT_DEFAULT = "30432"
DB_DEFAULT = "substrate_sandbox"

#: The keyring service both tenants' credentials live under.
SERVICE = "substrate-pg"


@dataclass(frozen=True, slots=True)
class Target:
    """Hold one postgres connection target for the sandbox tenant.

    ⚑ THE PASSWORD IS OPTIONAL AND ITS ABSENCE IS MEANINGFUL — see `keywords`, which OMITS the key
    rather than emitting a falsy one. It is held as `None` here so the two states stay distinct all
    the way down to the driver.
    """

    host: str
    port: int
    dbname: str
    user: str
    password: str | None

    def keywords(self) -> dict[str, str | int]:
        """Render the driver keyword mapping — the form a connect call consumes.

        ⚑ OMITS `password` WHEN THERE IS NONE, so that "no credential configured" and "wrong
        credential" stay two answers rather than one.
        """
        kw: dict[str, str | int] = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
        }
        if self.password:
            kw["password"] = self.password
        return kw

    def redacted(self) -> dict[str, str | int]:
        """Render a target safe to PRINT — the credential SUBSTITUTED, never dropped.

        ⚑ IT SUBSTITUTES RATHER THAN DELETES. A dropped key reads as "no credential is
        configured", a DIFFERENT fact an operator debugging an authentication failure would act
        on. A placeholder says a secret is there and is not being shown. A reporter that was safe
        became a leak once the target gained a secret, silently — so the safe form lives beside the
        real one rather than at each call site.
        """
        return {k: ("***" if k == "password" else v) for k, v in self.keywords().items()}


def keyring_credential(account: str) -> Callable[[], str | None]:
    """Build a credential SOURCE for one account — a callable, re-read on every assembly.

    ⚑ A MISSING BACKEND AND A MISSING KEY ARE DIFFERENT ANSWERS AND THIS DOES NOT COLLAPSE THEM.
    An absent key yields None, and the caller then omits the password key so the driver reports
    what actually happened; an unusable backend RAISES and surfaces as itself. The repairs differ —
    place a secret, versus run somewhere with a session bus — so one message for both would be the
    absent-versus-broken collapse this tree refuses elsewhere.
    """

    def _read() -> str | None:
        secret: str | None = keyring.get_password(SERVICE, account)
        return secret

    return _read


def transport() -> tuple[str, int]:
    """Return the store's `(host, port)`: an explicit override, else the owner's resolver.

    ⚑⚑ THE DEFAULTS ABOVE NAMED A RETIRED LISTENER (2026-09-22): nothing answers on
    `127.0.0.1:30432` any more — luthen retired its loopback NodePorts, and the store now lives in
    luthen's tenants. So the address is ASKED of its owner (`store_endpoint.resolve`, which refuses
    rather than guessing) whenever the environment does not name it. An explicit
    `SUBSTRATE_PG_HOST`/`SUBSTRATE_PG_PORT` still wins: an override is an instruction, and it is
    what lets a case assemble a target with no resolver present. The two defaults are kept only as
    the record of what was retired; nothing reads them.
    """
    host = os.environ.get(HOST_VAR)
    port = os.environ.get(PORT_VAR)
    if host and port:
        return host, int(port)
    ep = store_endpoint.resolve()
    return host or ep.host, int(port) if port else ep.port


def target(source: Callable[[], str | None] | None = None) -> Target:
    """Assemble the sandbox tenant's target — THE one place, for this tenant.

    ⚑⚑ THE DEFAULT CREDENTIAL IS NOW THE TENANT'S k8s SECRET, NOT THE KEYRING (operator,
    2026-09-22: luthen provisions `pg-tenant-<tenant>`). `keyring_credential` stays for callers
    that still hold a keyring entry; it is no longer what an unconfigured caller gets.

    `source` is the credential callable, defaulting to the tenant's Secret. It is
    a parameter so that a case can drive assembly with no keyring present: the credential source
    and the transport are separate concerns, and a check of the second should not require the
    first.

    ⚑ THE ROLE AND THE DATABASE SHARE A NAME, DELIBERATELY. A separate role is what makes the
    tenant split rest on the CREDENTIAL rather than on a database field: could the sandbox
    authenticate as the live role, "the only thing harmed is a database that exists to be harmed"
    would be a naming convention instead of a guarantee.
    """
    db = os.environ.get(DB_VAR, DB_DEFAULT)
    src = source if source is not None else store_endpoint.credential(db)
    host, port = transport()
    return Target(
        host=host,
        port=port,
        dbname=db,
        user=db,
        password=src(),
    )


#: The query naming every relation a reset must drop.
RELATIONS_QUERY = (
    "SELECT table_name, table_type FROM information_schema.tables"
    " WHERE table_schema NOT IN ('pg_catalog', 'information_schema')"
)


def reset_statements(relations: list[tuple[str, str]]) -> list[str]:
    """Order the DROP statements that empty the sandbox, views before tables.

    ⚑ VIEWS BEFORE TABLES, AND CASCADE ON BOTH: a view depends on the tables it selects from, so
    dropping tables first fails on the dependency — and a PARTIAL reset is worse than none, since
    it leaves exactly the ambiguity a reset exists to remove.

    ⚑ IT RETURNS STATEMENTS RATHER THAN EXECUTING THEM, so the ORDERING is checkable without a
    database. The rule being asserted is about sequence, and a case that needed a live server to
    read it would be asserting the connection instead of the rule.
    """
    views = [n for n, kind in relations if kind == "VIEW"]
    tables = [n for n, kind in relations if kind != "VIEW"]
    return [f'DROP VIEW IF EXISTS "{n}" CASCADE' for n in views] + [
        f'DROP TABLE IF EXISTS "{n}" CASCADE' for n in tables
    ]


def main(argv: list[str]) -> int:
    """Print the assembled sandbox target, redacted.

    ⚑⚑ IT NAMES ITS TENANT IN THE OUTPUT, WHICH IS THE HALF THE PREDECESSOR GOT WRONG. The store
    module's own reporter accepts a tenant flag, ignores it, and prints the LIVE target whatever it
    was asked for — so `--sandbox` there reports the live database name, and a reader who did not
    already know that reads a confident wrong answer. A footer that can disagree with its own
    subject is worse than one that is simply absent. This mode has no tenant flag to ignore: it
    assembles one tenant, and says which.

    ⚑ THE ONLY MODE IS THE REDACTED ONE. There is no flag that prints the credential: a target is
    printed to be read by a person or pasted into a report, and a reporter that was safe became a
    leak once the target gained a secret. The safe form is not the default here, it is the whole
    surface.
    """
    if argv:
        sys.stderr.write("usage: python3 -m substrate.sandbox_target\n")
        return 2
    sys.stdout.write(f"tenant : sandbox\ntarget : {target().redacted()}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
