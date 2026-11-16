# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run a store-using script against luthen's tenants, with `store.py`'s dead wiring replaced.

⚑⚑⚑ THE STORE MODULE IS FROZEN AND WIRED TO A RETIRED LISTENER. `jea/metalanguage/store.py`
carries 142 lint findings, so the per-file gate refuses any edit to it, and three of its
connection facts are wrong since the 2026-09-22 cutover to luthen's tenants: its host defaults to
`127.0.0.1`, its port to the retired NodePort `30432`, and `sandbox_connect` hand-assembles a
connection with NO port and NO password — so every `--sandbox` path in `schema.py`/`sppf_db.py`
(which reach it through `store.tenant()`) is refused, a dry run included. Measured:
`schema.py --establish event --sandbox` → `127.0.0.1:5432 … Connection refused`.

⚑⚑ SO THIS PATCHES THE MODULE AT RUNTIME, THEN RUNS THE SCRIPT. Before handing control to
`runpy`, it sets `store.PG_HOST`/`PG_PORT` from luthen's resolver, rebinds both credential
sources to the tenants' k8s Secrets, and REPLACES `store.sandbox_connect` with one built from
`sandbox_target` (port and password present). That reaches every caller because `store.tenant()`
reads `sandbox_connect` from the module's globals at call time, and the script is executed AFTER
the patch, so even a `from … import sandbox_connect` inside it binds the replacement. No frozen
file is edited, and the secret is never placed in the environment or a file.

⚑ THE REPLACEMENT KEEPS THE ORIGINAL'S OBLIGATIONS: it still records the lens event and still
honours `reset=` through the store's own `sandbox_reset` — only the connection is replaced.

⚑ IT IS TYPED THROUGH A PROTOCOL, NOT BY IMPORTING THE MODULE'S SURFACE. `store.py` is untyped;
naming its attributes directly would pull that `Any` into this clean module. The Protocol states
exactly the six members this module reads or replaces, and nothing else of `store` is touched.
"""

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

import psycopg
from psycopg.rows import dict_row

from substrate import sandbox_target, store_endpoint

if TYPE_CHECKING:
    from collections.abc import Callable

#: The frozen module this launcher patches, under both names it resolves by: the jea scripts
#: bind it BARE (`import store as _s`, their directory on sys.path), a package import dotted.
BARE = "store"
STORE = "jea.metalanguage.store"

USAGE = (
    "usage: python3 -m substrate.store_launch <script.py> [args…]\n"
    "  runs <script.py> as __main__ with jea.metalanguage.store wired to luthen's tenants\n"
)


class StoreModule(Protocol):
    """The six members of `jea.metalanguage.store` this launcher reads or replaces."""

    PG_HOST: str
    PG_PORT: int
    PG_CREDENTIAL: Callable[[], str | None]
    PG_SANDBOX_CREDENTIAL: Callable[[], str | None]
    sandbox_connect: Callable[[bool], object]
    sandbox_reset: Callable[[object], None]
    _lens_record: Callable[[str, str, str, str], None]


def sandbox_connector(store: StoreModule) -> Callable[[bool], object]:
    """Return a `sandbox_connect` replacement: same contract, a connection with port + password."""

    def connect(reset: bool = True) -> object:  # noqa: FBT001, FBT002 - the original's signature
        store._lens_record("sandbox_connect", "sandbox", "rw", "")  # noqa: SLF001 - its own record
        kw = sandbox_target.target().keywords()
        con = psycopg.connect(
            host=str(kw["host"]),
            port=int(kw["port"]),
            dbname=str(kw["dbname"]),
            user=str(kw["user"]),
            password=str(kw["password"]) if "password" in kw else None,
            row_factory=dict_row,
            autocommit=True,
        )
        if reset:
            store.sandbox_reset(con)
        return con

    return connect


def patch(store: StoreModule, endpoint: store_endpoint.Endpoint) -> None:
    """Rewire the store module's transport, credentials and sandbox connector, in place."""
    store.PG_HOST = endpoint.host
    store.PG_PORT = endpoint.port
    store.PG_CREDENTIAL = store_endpoint.credential(store_endpoint.LIVE)
    store.PG_SANDBOX_CREDENTIAL = store_endpoint.credential(store_endpoint.SANDBOX)
    store.sandbox_connect = sandbox_connector(store)


#: The store's own home — where `sppf_db` and the jea scripts find the BARE `store` at runtime.
STORE_HOME = Path(__file__).resolve().parent.parent / "jea" / "metalanguage"


def prepare_path(script: Path) -> None:
    """Put the script's directory first and the store's home last, as the patch requires.

    ⚑⚑ THE STORE'S HOME GOES LAST, so the BARE `store` resolves before the script runs.
    `sppf_db` puts `jea/metalanguage` on sys.path ITSELF, at runtime (sppf_db.py:22/26), so at
    patch time a bare `store` did not resolve, the patch skipped it, and the script then imported
    a fresh UNPATCHED copy — measured: the ingest reached store.sandbox_connect and 127.0.0.1.
    Appended LAST it shadows nothing; the patched module then sits in sys.modules, which every
    later `import store` returns, whatever path the script sets.
    """
    sys.path.insert(0, str(script.parent))
    if str(STORE_HOME) not in sys.path:
        sys.path.append(str(STORE_HOME))


def main(argv: list[str]) -> int:
    """Patch the store, then run `argv[0]` as `__main__` with the rest as its argv.

    ⚑⚑ THE SCRIPT'S DIRECTORY GOES FIRST ON `sys.path` BECAUSE `python3 script.py` PUTS IT
    THERE, and `runpy.run_path` does not. This reproduces the interpreter's own invocation
    semantics for the script being run; it adds no search root the script did not already have.
    ⚑⚑ AND THAT IS WHY THE BARE `store` IS PATCHED: the jea scripts bind it as
    `import store as _s` (schema_rows._cli_connect), which under that path is a DIFFERENT module
    object from `jea.metalanguage.store`. Patching only the dotted name reached nothing they call
    — measured on the first run. Both spellings are patched when both resolve.
    """
    if not argv or not argv[0].endswith(".py"):
        sys.stderr.write(USAGE)
        return 2
    script = Path(argv[0]).resolve()
    prepare_path(script)
    endpoint = store_endpoint.resolve()
    for name in (BARE, STORE):
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        patch(cast("StoreModule", module), endpoint)
    sys.argv = [str(script), *argv[1:]]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
