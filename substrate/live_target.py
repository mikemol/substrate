#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Assemble the LIVE tenant's postgres connection target (drain-store).

⚑⚑⚑ THIS IS THE TWIN `sandbox_target` DELIBERATELY DID NOT BUILD, AND THE REASON IT NOW EXISTS IS
A DIFFERENT ONE. That module argues at length for covering the SANDBOX tenant only: a copy
covering both would be *"a genuine second authority for the whole store"*, while covering the one
tenant whose accessor was already documented as separate kept the seam where it had been drawn.
That argument was correct for an extraction whose job was repairing a hand-rolled connector. It
does not survive the next step, and the reason is not that the argument was wrong.

⚑⚑ WHAT CHANGED IS THAT THE DISPATCH IS MOVING OUT. The defect being repaired is not a stale
target — it is a CLI that ignores `--sandbox` and `--live` alike and reports the live store under
every question. A tenant-dispatching reporter must be able to assemble EITHER tenant, so the live
half stops being a duplicate of a single authority and becomes the other arm of a two-arm choice.
Leaving it in the monolith would mean the new dispatch reached back into a file the per-file gate
freezes, which is the reach that made the sibling extraction unable to be clean.

⚑ AND THE "SECOND AUTHORITY" CONCERN IS ANSWERED BY RETIREMENT, NOT BY ABSTENTION. Two spellings
of the live target is a real hazard for exactly as long as both are live; the monolith's accessor
is on its way out, and this arc is what removes it. A duplicate that exists to REPLACE its
original is a migration; one that exists beside it forever is the drift `sandbox_dsn` warns about.
⚑ Until the retirement lands, the monolith's `dsn()` is still the authority its own callers use —
this module does not change what they read, and nothing here writes to that path.

⚑ IT IMPORTS NOTHING FROM `jea/`, FOR THE SAME LOAD-BEARING REASON AS ITS SIBLING. A module
extracted out of that package but still NAMING it inherits the untyped hub through the import and
cannot be made clean under the per-file gate. The environment variables and the keyring service
are therefore re-derived here rather than imported, and the sibling's spellings are reused exactly
so the two tenants cannot disagree about transport.

⚑ THE TRANSPORT IS SHARED WITH THE SANDBOX AND IS IMPORTED FROM IT, NOT RESTATED. Host, port and
keyring service are properties of the STORE, not of a tenant; only the database and the role
differ. Restating the port here is precisely the second spelling that let one tenant follow the
NodePort cutover while the other kept the retired listener — so the field that drifted is the one
field this module refuses to own.

⚑ A CREDENTIAL SOURCE IS A CALLABLE, NEVER A CAPTURED STRING. A value read at import is stale the
moment short-lived issued credentials arrive, and a string cannot be re-fetched while a process
holds it. The keyring is the ONE source: no environment fallback, because a variable silently
outranking the stored credential is the exact surprise a keyring exists to remove.

⚑ NO CONNECTION IS OPENED AND NO DRIVER IS IMPORTED. Assembly is pure and total, so it is
checkable with no server — the property that let the sandbox target's cases run offline, kept here
for the same reason.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from substrate import store_endpoint
from substrate.sandbox_target import Target, transport

if TYPE_CHECKING:
    from collections.abc import Callable

#: The live tenant's database and role. ⚑ ONLY THESE TWO FIELDS DIFFER FROM THE SANDBOX'S — the
#: host, the port and the keyring service are the store's, and are imported rather than restated.
DB_VAR = "SUBSTRATE_PG_DB"
USER_VAR = "SUBSTRATE_PG_USER"

DB_DEFAULT = "substrate"
USER_DEFAULT = "substrate"


def target(source: Callable[[], str | None] | None = None) -> Target:
    """Assemble the live tenant's target — THE one place, for this tenant.

    ⚑⚑ TRANSPORT AND DEFAULT CREDENTIAL FOLLOW THE SANDBOX'S (2026-09-22): the address comes from
    `sandbox_target.transport()` (an override, else luthen's resolver), and the default source
    is the live tenant's k8s Secret rather than the keyring — one rule for both tenants.

    `source` is the credential callable, defaulting to the live tenant's Secret. It is a
    parameter so that a case can drive assembly with no keyring present: the credential source and
    the transport are separate concerns, and a check of the second should not require the first.

    ⚑ THE ROLE IS READ SEPARATELY FROM THE DATABASE, WHICH IS WHERE THIS DIFFERS FROM THE SANDBOX.
    There the two share a name deliberately, so the tenant split rests on the credential. Here
    they are independently configurable because a live deployment may grant several roles against
    one database, and folding them into one variable would make that unsayable.

    ⚑ THE CREDENTIAL IS KEYED ON THE ROLE, NOT THE DATABASE AND NOT THE HOST. A credential is
    scoped to a postgres ROLE; keying it on the transport would strand it the next time the
    listener moves, which has already happened once.
    """
    user = os.environ.get(USER_VAR, USER_DEFAULT)
    src = source if source is not None else store_endpoint.credential(store_endpoint.LIVE)
    host, port = transport()
    return Target(
        host=host,
        port=port,
        dbname=os.environ.get(DB_VAR, DB_DEFAULT),
        user=user,
        password=src(),
    )
