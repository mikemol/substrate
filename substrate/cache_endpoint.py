# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the shared cache lives — an INPUT, never a constant, and a probe that says which.

⚑⚑⚑ A HARDCODED ENDPOINT WENT STALE INVISIBLY, AND THAT IS WHY THIS MODULE EXISTS.
`scratch/shared_cache.py` names `127.0.0.1:6379`, which was cassian's cache before their
k8s cutover; the live address is a NodePort. **A cache client DEGRADES rather than fails** —
it falls through to computing the value — so the only symptom of a dead port is that the
cache never hits, which from inside is indistinguishable from a cache that is simply always
cold. Nothing crashes and nothing logs.

⚑⚑ SO THE REPAIR IS THE OVERRIDE, NOT THE NEW NUMBER. Replacing one hardcoded pair with
another leaves the next cutover exactly as silent as this one. `SUBSTRATE_VALKEY_ENDPOINT`
makes it a config change; the default tracks the current deployment so the common case needs
no ceremony.

⚑⚑⚑ AND THE PROBE MUST SEPARATE THE THREE CAUSES, which is the half an endpoint constant
cannot supply. The origin's own `--probe` says so in its output: *"a refused connection, a
stopped quadlet and a wrong endpoint are three causes; this probe separates none of them."*
Reporting a refusal against ONE address cannot distinguish *the port moved* from *the host
is unreachable* — and those want opposite responses. Probing the KNOWN ADDRESSES together
answers it: if a retired address refuses and the current one answers, the config is stale;
if all refuse, the reach is the problem, not the number.

⚑ A RETIRED ADDRESS IS THEREFORE KEPT, NOT DELETED. It is the discriminator. Deleting it
would make the next cutover undiagnosable in exactly the way this one was.

⚑ THIS MODULE OPENS NO CONNECTION BEYOND THE PROBE AND HOLDS NO CLIENT. It answers *where*
and *what is answering there*; the store, its serialization and its key discipline stay with
the cache itself. Growing a client here would make two modules each believe they own the
connection, which is the shape the repo's write-once ambient exists to refuse.

⚑⚑ REPORTED BY cassian-observability (2026-09-10), who named the under-announcement as
theirs — substrate was the SECOND consumer found on a pre-migration address that week.
Verified here rather than taken on report: a peer's verdict is a hypothesis.
"""

from __future__ import annotations

import os
import socket
import sys
from typing import NamedTuple

#: The environment variable that overrides the endpoint, so a cutover is a config change.
ENV_VAR = "SUBSTRATE_VALKEY_ENDPOINT"

#: The one mode this module has, named so it appears in the usage a bare run prints.
#: ⚑ GUESSING A MODE NAME IS THE RECURRING COST ON THIS TOOLKIT, so the spelling a reader
#: needs next time is printed rather than left to be remembered.
MODE = "--candidates"

#: What a bare or unknown invocation exits with — usage, not success and not a failed probe.
USAGE_EXIT = 2


def _run(argv: list[str]) -> int:
    """Run the one mode this module has, printing the report and returning its code.

    ⚑ THE THREE EXIT CODES ARE THE THREE OUTCOMES — 0 OK, 1 STALE CONFIG, 2 usage or
    UNREACHABLE. A caller scripting this needs to tell "repoint it" from "do not touch the
    config, you have no reach", and collapsing those would send someone to change a setting
    that was correct.

    ⚑ DEFINED BESIDE ITS IMPORTS BECAUSE THE PER-FILE GATE IS ATOMIC: an import lands in the
    same write as its use, or the write is refused and creates no file at all. That is why
    this sits above the readers it calls, which Python resolves at call time.
    """
    if argv and argv[0] == MODE:
        lines, code = report(dict(os.environ))
        for line in lines:
            print(line)  # noqa: T201 - this module IS the report
        return code
    print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
    print(
        f"    cache_endpoint.py {MODE}   "  # noqa: T201
        f"# which known address answers, and what that means"
    )
    return USAGE_EXIT


#: The argv this module runs on. Captured beside its import because the per-file gate is
#: atomic — an import lands in the same write as a use or the write creates no file — while
#: the `__main__` guard itself must sit at the END, after every reader it calls is defined.
#: ⚑ A PREDICTION THAT FAILED: the guard was first written here, next to `_run`, on the
#: reasoning that Python resolves names at call time. True of the CALL and false of the
#: GUARD, which executes as the module body reaches it — so `report` was not yet defined and
#: the mode died with a `NameError`. Reading the binding beats reasoning about it.
ARGV = sys.argv[1:]

#: Where the cache lives today. A default, not a constant — `ENV_VAR` outranks it.
DEFAULT = "127.0.0.1:30637"

#: How long to wait on a probe. A CEILING ON WAITING, NOT A PREDICTION: a generous ceiling
#: costs nothing when the connection succeeds immediately, and a tight one reports a live
#: store as dead.
TIMEOUT_S = 2.0

#: What a Valkey/Redis server answers `PING` with — the discriminator between a TCP bind and
#: a store. ⚑ A CONNECTED SOCKET IS NOT A LIVE CACHE: anything may hold a port, so a probe
#: that stopped at `connect` would report a wrong service as healthy.
PONG = b"+PONG"

#: `PING` as the RESP wire protocol spells it, so the probe needs no client library.
PING = b"*1\r\n$4\r\nPING\r\n"


class Endpoint(NamedTuple):
    """A host and port, with the spelling a caller supplied."""

    host: str
    port: int

    def __str__(self) -> str:
        """Return the `host:port` spelling, as a config value and a report both use."""
        return f"{self.host}:{self.port}"


class Probe(NamedTuple):
    """What one address answered — three outcomes, deliberately not two.

    ⚑ `connected` AND `answered` ARE SEPARATE FIELDS BECAUSE THEY ARE SEPARATE FACTS. A port
    that accepts a connection and does not speak RESP is a DIFFERENT problem from a refused
    one — it means something else has taken the address — and collapsing them into a boolean
    would report that as simply down.
    """

    endpoint: Endpoint
    connected: bool
    answered: bool
    note: str

    def why(self) -> str:
        """Return a one-line account of what this address is doing."""
        if self.answered:
            return f"{self.endpoint}  ANSWERS (RESP PONG)  — {self.note}"
        if self.connected:
            return f"{self.endpoint}  connected, NOT a cache — {self.note}"
        return f"{self.endpoint}  refused — {self.note}"


#: The addresses this store is known to have used, newest first.
#: ⚑ THE RETIRED ONE EARNS ITS PLACE: it is what makes a refusal diagnosable rather than
#: merely reported. See the module docstring.
KNOWN: tuple[tuple[str, str], ...] = (
    (DEFAULT, "cassian NodePort, post-k8s-cutover (current)"),
    ("127.0.0.1:6379", "cassian quadlet, RETIRED at the k8s cutover"),
)


def parse(spec: str) -> Endpoint:
    """Return the endpoint `spec` names, REFUSING a malformed one rather than defaulting.

    ⚑ A SILENT FALLBACK WOULD REPRODUCE THE FAILURE THIS EXISTS TO REMOVE — a client pointed
    somewhere nobody intended, degrading quietly, with the operator's own setting discarded
    and nothing saying so. An unusable setting is a defect in the invocation, and the
    invocation is what must hear about it.
    """
    host, sep, port = spec.rpartition(":")
    if not sep or not host or not port.isdigit():
        msg = (
            f"{ENV_VAR}={spec!r} is not `host:port`. The endpoint is REFUSED rather than "
            f"defaulted, because a silent fallback is how a client ends up somewhere "
            f"nobody intended — which is the defect this override exists to remove."
        )
        raise ValueError(msg)
    return Endpoint(host, int(port))


def configured(environ: dict[str, str] | None = None) -> Endpoint:
    """Return the endpoint this invocation should use — the override, else the default.

    ⚑ THE ENVIRONMENT IS A PARAMETER, so a case can state one rather than mutating the
    process's own. A reader that consulted `os.environ` directly could only be tested by a
    suite that changed the world it runs in.
    """
    env = environ if environ is not None else {}
    return parse(env.get(ENV_VAR, DEFAULT))


def probe(endpoint: Endpoint, note: str = "", timeout: float = TIMEOUT_S) -> Probe:
    """Return what `endpoint` answers — connected, speaking RESP, or refusing.

    ⚑ THE PROBE SENDS `PING` AND READS THE REPLY rather than stopping at `connect`, because
    a connected socket is not a live cache: any process may hold a port. A probe that trusted
    the connect would report a wrong service as healthy, which is the same false green the
    endpoint constant already produced once.
    """
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((endpoint.host, endpoint.port))
    except OSError as exc:
        return Probe(
            endpoint, connected=False, answered=False, note=note or f"{type(exc).__name__}: {exc}"
        )
    try:
        sock.sendall(PING)
        said = sock.recv(len(PONG))
    except OSError as exc:
        return Probe(
            endpoint, connected=True, answered=False, note=note or f"connected but silent: {exc}"
        )
    finally:
        sock.close()
    return Probe(endpoint, connected=True, answered=said.startswith(PONG), note=note)


def candidates(timeout: float = TIMEOUT_S) -> list[Probe]:
    """Return a probe of every KNOWN address, so a refusal names WHICH cause it has.

    ⚑⚑ THIS IS THE MODE THE ORIGIN LACKED. Its `--probe` reports one address and states
    plainly that it cannot separate a refused connection from a stopped service from a wrong
    endpoint. Probing the known set together answers exactly that: the CURRENT one answering
    while a RETIRED one refuses says the config is stale, and every one refusing says the
    reach is the problem rather than the number.
    """
    return [probe(parse(spec), note, timeout) for spec, note in KNOWN]


def report(environ: dict[str, str] | None = None) -> tuple[list[str], int]:
    """Return the `--candidates` report and its exit code.

    ⚑ A REFUSAL IS A RESULT, NOT AN EXCEPTION, so a case can assert on one. A tool whose main
    job is diagnosing an unreachable store must be able to report unreachability as a value.

    ⚑⚑ AND THE EXIT CODE DISTINGUISHES THE THREE OUTCOMES, because a caller scripting this
    needs to tell "stale config, repoint it" from "no reach, do not touch the config": 0 OK,
    1 STALE, 2 UNREACHABLE. Collapsing the last two would send someone to edit a setting that
    was correct.
    """
    current = configured(environ)
    probes = candidates()
    lines = [f"configured    {current}   (override with {ENV_VAR})", ""]
    lines.extend(f"  {p.why()}" for p in probes)
    said = verdict(probes, current)
    lines.extend(["", said])
    if said.startswith("OK"):
        return lines, 0
    return lines, 1 if said.startswith("STALE") else 2


def verdict(probes: list[Probe], current: Endpoint) -> str:
    """Return what the probe set establishes — or WITHHOLD when it cannot carry a verdict.

    ⚑⚑⚑ THE THIRD OUTCOME IS LOAD-BEARING. When nothing answers, this does NOT report the
    endpoint as wrong: a host with no reach at all produces exactly that reading, and the
    two want opposite responses. Saying UNREACHABLE where the evidence cannot distinguish
    them is the honest verdict, and it is the one the origin's own comment asked for.
    """
    live = [p for p in probes if p.answered]
    if not live:
        return (
            "UNREACHABLE — no known address answers, so this cannot tell a moved port "
            "from a host this session cannot reach. Establish reach before repointing."
        )
    if any(p.endpoint == current for p in live):
        return f"OK — the configured endpoint {current} answers."
    names = ", ".join(str(p.endpoint) for p in live)
    return (
        f"STALE CONFIG — {current} does not answer and {names} does. "
        f"Set {ENV_VAR}={names} (the cache degrades silently, so nothing else says so)."
    )


if __name__ == "__main__":
    raise SystemExit(_run(ARGV))
