# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Does a VictoriaLogs endpoint actually INGEST — verified by reading the write back.

⚑⚑⚑ A TRANSPORT 200 IS NOT INGESTION, AND THIS SURFACE IS WHERE THAT WAS MEASURED.
`ratchet_log`'s own docstring records it: VictoriaLogs answers HTTP 200 to an integer
timestamp while ingesting ZERO rows. So a probe that posted a record and reported the status
code would confirm nothing, and would confirm it confidently — which is worse than no probe,
because a green reading gets banked. **The only honest check is read-your-write**: post a
value this process chose, then query until that exact value comes back.

⚑⚑⚑ AND THE INSTRUMENT THAT ALREADY EXISTS CANNOT ANSWER THIS. `tsdbprobe` speaks PromQL and
reports `UNREACHABLE` for a VictoriaLogs port — on an `HTTP 400: unsupported path requested`,
which is **a live server refusing a query it does not speak**. That verdict is a fact about
the instrument, not about the store, and reading it as "the endpoint is dead" is exactly the
census-green-inverted error this repo keeps paying for. A logs engine needs a logs reader.

⚑⚑ NOT CONFIRMED IS NOT FAILED, AND THE THIRD OUTCOME IS WHY THIS MODULE EXISTS AT ALL. An
empty read has causes that no predicate here distinguishes — not written, written but not yet
queryable, store down, or a query this reader spelled wrong. Collapsing them into "failed"
would send someone to repoint a correct address; collapsing them into "fine" would bank a
silent drop. `Ingest.UNCONFIRMED` is a first-class outcome and never an error.

⚑ A FETCH ERROR IS A RETRY, NEVER A VERDICT — the store may be settling under the write. The
deadline is a CEILING ON WAITING, not a prediction: a generous one costs nothing when the read
succeeds early, and a tight one reports a successful write as unconfirmed.

⚑⚑ BOTH HALVES RIDE `curl`, WHICH IS A TYPING DECISION AND ALSO THE RIGHT ONE. `urlopen` is
untyped, so its response and everything read off it arrive as `Any` — the leak this repo's
gate refuses, and the one that lets a misspelled attribute typecheck and fail at runtime.
Routing the read through the same subprocess the emitter already uses keeps the seam typed
AND means the probe exercises the transport the real writer takes, rather than a second one
that might succeed where the first fails.

⚑ THIS WRITES ONE RECORD PER PROBE, into the stream the emitter already uses, tagged as a
probe. It is a diagnostic that leaves a trace, which is the honest shape — a check that wrote
nowhere could not verify ingestion, and one that wrote to a private stream would verify a path
nothing else uses.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.parse
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from shutil import which
from typing import NamedTuple

#: The argv this module runs on. Bound beside its import because the per-file gate is atomic
#: — an import lands in the same write as a use, or the write is refused and creates no file
#: at all — while the `__main__` guard must sit at the END, after every reader it calls is
#: defined. ⚑ A GUARD PLACED BESIDE ITS IMPORT EXECUTES AS THE MODULE BODY REACHES IT, which
#: a sibling module in this session established by `NameError` rather than by reasoning.
ARGV = sys.argv[1:]

#: The mode this module has, named so a bare run prints the spelling a reader needs next.
MODE = "--ingest"

#: What a bare or unknown invocation exits with — usage, never a verdict about a store.
USAGE_EXIT = 2

#: What an UNCONFIRMED probe exits with. ⚑ DISTINCT FROM REFUSED (1), because "the write did
#: not read back" and "the store would not take the write" are different facts, and a caller
#: scripting this must be able to tell them apart without parsing prose.
UNCONFIRMED_EXIT = 3

#: What a SLOW probe exits with. ⚑⚑ DISTINCT FROM UNCONFIRMED (3) FOR THE SAME REASON ONE
#: LEVEL IN: a query that never completed says nothing about the row, and a caller that
#: treated it as "not ingested" would repoint a working endpoint. This code means READ THE
#: QUERY, not read the store.
SLOW_EXIT = 4

#: The mode plus its one operand — the shortest argv this tool can act on.
_WITH_OPERAND = 2

#: How long to keep re-reading before reporting UNCONFIRMED. A ceiling on waiting, never a
#: prediction of when the store will settle.
DEADLINE_S = 20.0

#: How long between reads. Short enough to finish early, long enough not to hammer the store.
POLL_S = 1.0

#: Per-request timeout. The store answering slowly is a retry, not a verdict.
REQUEST_S = 3.0

#: The stream this probe writes into — the emitter's own, so the path verified is the path
#: used. ⚑ A PRIVATE STREAM WOULD VERIFY A ROUTE NOTHING ELSE TAKES.
STREAM_FIELDS = "tool,reason"

#: What this probe calls itself in the `tool` field, so its rows are filterable and a reader
#: seeing them in the log knows they are diagnostics rather than real refusals.
PROBE_TOOL = "logs-probe"

#: The content type VictoriaLogs' jsonline ingest expects.
CONTENT_TYPE = "Content-Type: application/stream+json"

#: ⚑⚑⚑ THE TIME BOUND, AND ITS ABSENCE COST A FALSE UNCONFIRMED. An unbounded LogsQL filter
#: scans the WHOLE RETENTION, so a deadline expires inside the scan rather than on a missing
#: row — and the two are indistinguishable from the caller's side. Measured by cassian on this
#: store: `unit:"kernel"` returned nothing inside 120s while `_time:5m unit:"kernel"` returned
#: rows in 0.76s. Same filter, same server, one prefix.
#:
#: ⚑⚑ THE WINDOW MUST COVER THE WRITE THIS PROBE JUST MADE, and 5m is generous for a write
#: that happened seconds ago. Widening it does not make the probe more thorough — it makes it
#: scan more and re-approach the hang it exists to avoid.
READ_WINDOW = "_time:5m"


class Ingest(StrEnum):
    """What a probe established — four outcomes, and the last two were once one.

    ⚑ `UNCONFIRMED` IS NOT `REFUSED`. A write that cannot be read back may be a dropped write,
    a store still settling, or a query this reader spelled wrong — and those want different
    responses. Reporting the honest gap keeps someone from repointing a working address
    because a probe was impatient.

    ⚑⚑⚑ AND `SLOW` IS NOT `UNCONFIRMED`, WHICH THIS ENUM LEARNED THE EXPENSIVE WAY. The first
    cut had three members and reported UNCONFIRMED for an endpoint that ingests perfectly:
    the read-back query was unbounded, so it scanned the whole retention and the deadline
    expired INSIDE THE SCAN rather than on a missing row. From the caller's side those are
    identical — a timeout with nothing returned — and collapsing them let a working store read
    as a possibly-broken one. **A wallclock deadline cannot, by itself, distinguish "the row
    is not there" from "the question was too expensive to answer."**

    ⚑⚑ THE SPLIT IS NOW STRUCTURAL RATHER THAN A JUDGEMENT: a read that exceeds its per-request
    timeout is SLOW, and a read that ANSWERS without the token is UNCONFIRMED. Those are
    different observations, not different confidences about one observation.
    """

    CONFIRMED = "CONFIRMED"
    UNCONFIRMED = "UNCONFIRMED"
    SLOW = "SLOW"
    REFUSED = "REFUSED"


class Result(NamedTuple):
    """One probe: what it established, against which base, and what it saw."""

    ingest: Ingest
    base: str
    token: str
    detail: str

    def __bool__(self) -> bool:
        """Report whether the write was read back — CONFIRMED-ness and nothing else."""
        return self.ingest is Ingest.CONFIRMED

    def why(self) -> str:
        """Return a one-line account naming the base, the outcome and the reason."""
        return f"{self.base}  {self.ingest}  — {self.detail}"


def insert_url(base: str) -> str:
    """Return the jsonline ingest URL for `base`, declaring the stream fields.

    ⚑⚑ THE FIELD LIST IS INTERPOLATED, NOT `urlencode`d, AND A CASE CAUGHT THE DIFFERENCE.
    `urlencode` percent-escapes the separating comma, so the probe sent `tool%2Creason` while
    the emitter sends `tool,reason` — the two are equivalent to the server, and that is
    exactly why it would have gone unnoticed. **A probe that does not send what the emitter
    sends is verifying a path nothing else takes**, and the whole argument for writing into
    the emitter's own stream was that the route under test is the route in use.

    ⚑ THE VALUE IS A MODULE CONSTANT OF KNOWN SHAPE, not caller input, so interpolating it
    introduces nothing to escape.
    """
    return f"{base.rstrip('/')}/insert/jsonline?_stream_fields={STREAM_FIELDS}"


def query_url(base: str, logsql: str) -> str:
    """Return the LogsQL select URL for `base` and `logsql`."""
    return f"{base.rstrip('/')}/select/logsql/query?{urllib.parse.urlencode({'query': logsql})}"


def record(token: str) -> str:
    """Return one jsonline record carrying `token`, shaped as the emitter shapes its own.

    ⚑⚑ RFC3339 MICROSECONDS, NEVER AN INTEGER. VictoriaLogs answers 200 to an integer
    timestamp and ingests nothing — the measured incident this whole module is built around.
    A probe that used the wrong timestamp format would report the endpoint dead when the
    endpoint was fine, which is the failure mode in the opposite direction.
    """
    event: dict[str, object] = {
        "_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "_msg": f"ingest probe {token}",
        "tool": PROBE_TOOL,
        "reason": "probe",
        "token": token,
    }
    return json.dumps(event)


def _curl(args: list[str], timeout: float, stdin: str | None = None) -> tuple[bool, str]:
    """Run `curl` with `args`. Returns `(ok, output_or_reason)`.

    ⚑ THE ABSENT-CURL CASE IS NAMED RATHER THAN SWALLOWED. A missing binary and a store that
    is down both produce a failed call, and reporting them alike is how "the endpoint is
    dead" gets recorded about a machine that simply lacks a tool.
    """
    found = which("curl")
    if found is None:
        return False, "curl is not on PATH — this probe cannot reach the store"
    try:
        done = subprocess.run(  # noqa: S603 - fixed argv; any payload rides on stdin
            [found, *args],
            input=stdin,
            text=True,
            capture_output=True,
            timeout=timeout + 1,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{type(exc).__name__}: {exc}"
    if done.returncode != 0:
        return False, (done.stderr.strip() or f"curl exit {done.returncode}")
    return True, done.stdout


def post(base: str, line: str, timeout: float = REQUEST_S) -> tuple[bool, str]:
    """POST one record. Returns `(transport_ok, detail)` — NOT a verdict about ingestion.

    ⚑ THE NAME SAYS `transport_ok` BECAUSE THAT IS ALL IT KNOWS. Treating this boolean as
    "the write landed" is precisely the 200-is-not-ingestion error; the caller must read it
    back. Naming the variable for what it measures is what keeps the next reader from
    shortcutting the verification.
    """
    ok, said = _curl(
        [
            "-fsS",
            "--max-time",
            str(timeout),
            "--data-binary",
            "@-",
            "-H",
            CONTENT_TYPE,
            insert_url(base),
        ],
        timeout,
        stdin=line,
    )
    if not ok:
        return False, said
    return True, "transport ok (NOT yet evidence of ingestion)"


def read_back(base: str, token: str, timeout: float = REQUEST_S) -> tuple[bool, bool]:
    """Return `(answered, found)` for one read of `token` at `base`.

    ⚑⚑⚑ TWO BOOLEANS, NOT ONE, AND THAT IS THE WHOLE CORRECTION. A first cut returned a single
    `False` for both "the store answered and the row was absent" and "the store never
    answered" — which is precisely the collapse that made a working endpoint read as
    UNCONFIRMED. `answered` is an observation about the QUERY; `found` is an observation about
    the ROW, and a caller cannot reconstruct the first from the second.

    ⚑ A FETCH FAILURE IS STILL NOT AN EXCEPTION, because the caller is polling: the store may
    be settling under the write, and a raise would turn an ordinary retry into a verdict.
    """
    ok, said = _curl(
        ["-fsS", "--max-time", str(timeout), query_url(base, f'{READ_WINDOW} token:"{token}"')],
        timeout,
    )
    return ok, (ok and token in said)


def probe(base: str, deadline: float = DEADLINE_S, poll: float = POLL_S) -> Result:
    """Write a chosen value to `base` and poll until it reads back, or the deadline passes.

    ⚑⚑ THE TOKEN IS THIS PROCESS'S OWN, which is what makes the read a verification rather
    than a coincidence. Querying for any row at all would pass against a store holding only
    old data — including a store that stopped accepting writes an hour ago.

    ⚑⚑⚑ AND WHETHER ANY READ EVER ANSWERED IS CARRIED OUT OF THE LOOP, because it is the only
    thing that separates SLOW from UNCONFIRMED. A deadline that expires having never received
    an answer says the QUESTION was too expensive; one that expires having received answers
    without the row says the ROW is not there. Reporting both as UNCONFIRMED is what made a
    perfectly healthy endpoint read as suspect for a whole tick.
    """
    token = uuid.uuid4().hex
    sent, detail = post(base, record(token))
    if not sent:
        return Result(Ingest.REFUSED, base, token, detail)

    ever_answered = False
    end = time.monotonic() + deadline
    while time.monotonic() < end:
        answered, found = read_back(base, token)
        ever_answered = ever_answered or answered
        if found:
            return Result(
                Ingest.CONFIRMED, base, token, "the written value read back — the ingest path works"
            )
        time.sleep(poll)

    if not ever_answered:
        return Result(
            Ingest.SLOW,
            base,
            token,
            f"the write was accepted and NO read answered within {deadline:g}s — "
            f"the query never completed, so this says nothing about the row. An "
            f"unbounded LogsQL filter scans the whole retention: check the "
            f"{READ_WINDOW!r} bound before concluding anything about ingestion",
        )
    return Result(
        Ingest.UNCONFIRMED,
        base,
        token,
        f"reads ANSWERED within {deadline:g}s and none carried the token — the "
        f"write was accepted and the row is not queryable. NOT the same as "
        f"refused: the store may still be settling, or the row may have been "
        f"dropped after acceptance",
    )


def run(argv: list[str]) -> int:
    """Probe the base named on the command line, printing what was established.

    ⚑ ONE EXIT CODE PER OUTCOME — 0 CONFIRMED, 1 REFUSED, 2 usage, 3 UNCONFIRMED, 4 SLOW.
    Collapsing UNCONFIRMED into failure would report a settling store as a broken one, and
    collapsing SLOW into UNCONFIRMED would report an expensive QUERY as a missing ROW — which
    is exactly what happened here before the split existed.
    """
    if len(argv) < _WITH_OPERAND or argv[0] != MODE:
        print(__doc__)  # noqa: T201 - the usage, for a bare or unknown invocation
        print(
            f"    logs_probe.py {MODE} <base-url>   "  # noqa: T201
            f"# write one record and read it back — does this endpoint INGEST"
        )
        return USAGE_EXIT
    got = probe(argv[1])
    print(got.why())  # noqa: T201 - this module IS the report
    codes = {
        Ingest.CONFIRMED: 0,
        Ingest.REFUSED: 1,
        Ingest.UNCONFIRMED: UNCONFIRMED_EXIT,
        Ingest.SLOW: SLOW_EXIT,
    }
    return codes[got.ingest]


if __name__ == "__main__":
    raise SystemExit(run(ARGV))
