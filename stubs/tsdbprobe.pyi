# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scratch/tsdbprobe.py` — the metrics-surface authority.

⚑⚑ A DYNAMICALLY-LOADED MODULE IS `Any` AT EVERY REACH, AND THAT `Any` PROPAGATES. Loading the
probe by location makes it importable without touching `sys.path`, but every attribute read off
it is untyped — so a reader consulting it fails the strict bar on six lines that are individually
correct. A `.pyi` supplies signatures independently of packaging, which is the same repair
`check_scratch_independence.pyi` records for the promoted-project authority.

⚑⚑ THE WHOLE SURFACE IS DECLARED, NOT THE THREE NAMES THIS REPO READS, and the reason is
measured: `stubtest` in strict mode requires every runtime name to be present, so a narrow stub
fails with one error per undeclared name. The narrowness `bib.pyi` argues for buys silence only
with an allowlist that then has to be maintained against someone else's edits.

⚑⚑⚑ AND THE FIRST DRAFT INVENTED FIVE DECLARATIONS, EXACTLY AS THE PRECEDENT PREDICTED.
`HEARTBEATS`, `PRODUCERS`, `QUERY_BASE` and `VLOGS_BASE` were written from the shape a metrics
probe *ought* to have and are not present at runtime; `main` was declared parameterless and takes
`argv`. Every one of those would have type-checked at the call site against a fiction — which is
the precise reason `check_scratch_independence.pyi` says **a stub is a CLAIM, and an unverified
claim about types is worth less than no claim.** `stubtest` reported all five in one run; they
are corrected here to what the module actually declares.

⚑ THE UNANNOTATED FUNCTIONS ARE A READING, NOT A TRANSCRIPTION. `stubtest` verifies ARITY and
NAMES, never that a parameter type is what the body assumes.

⚑⚑⚑ AND THE SENTENCE THAT USED TO STAND HERE — *"`query`, `series`, `names`, `label_values`,
`export_samples`, `producers` and `transitions` return `_get`'s parsed body, so `object` is the
honest declaration"* — WAS FALSE OF THREE OF THE SEVEN, and one `object` spelling over all seven is
what hid that. Reading each return site splits them into two classes that are not alike:

  · `query`, `series`, `names`, `label_values` ARE one-line passthroughs of `_get`, whose body is
    `json.loads(...)`. Typeshed types that `Any`, and an `Any` from the oracle is an ABSENCE of an
    answer, not an answer. `object` STAYS on these four — it is the narrowing of an unconstrained
    `Any` at the seam, the same move `stub_declines._captured` makes, and stating a JSON shape
    here would be inventing the schema of someone else's store.
  · `export_samples`, `producers` and `transitions` NEVER RETURN `_get`'s body. Each builds a
    LOCAL list and appends tuples the reader can see assembled — `out.append((obj.get("metric")
    or {}, pairs))` at `:215`, `out.append((service, metric, max(vals) if vals else None, exists))`
    at `:603`, `out.append((ts, prev, v))` at `:233`. Those element types are read off the
    construction, so they are stated below. A derived type is correct by CONSTRUCTION; that it
    cannot be falsified is not a reason to withhold it.

⚑⚑ THE TWO CLASSES WERE INDISTINGUISHABLE WHILE BOTH WERE SPELLED `object`, which is the general
defect: `object` is the TOP TYPE, so `stubtest` can never contradict it and a green verdict on such
a slot is a fact about what `object` admits. A declined slot and an underived one must not share a
spelling — the sibling `agda_lex.pyi` keeps `HEADER: _HeaderLike` precisely so its refusal reads as
a judgement rather than as debt.

⚑ `KNOWN_PRODUCERS` IS DECLARED WIDER THAN THE DERIVATION AND STAYS THAT WAY. `iface_construct`
computes the positional `tuple[tuple[str, str], tuple[str, str], tuple[str, str]]` — the literal
holds three entries TODAY. Arity is not part of this constant's contract; every consumer iterates
it. A homogeneous variadic `tuple[tuple[str, str], ...]` is the correct WIDENING, and matching the
stub to the derivation here would over-specify the slot and break on the next producer added.
"""

from collections.abc import Callable

class Unreachable(Exception): ...

DEFAULT_BASE: str
DEFAULT_DEADLINE: float
DEFAULT_POLL: float

# The heartbeat convention both live producers adopted: (service, metric) pairs.
KNOWN_PRODUCERS: tuple[tuple[str, str], ...]

def extract_values(body: object) -> list[float]: ...
def extract_names(body: object) -> list[str]: ...
def extract_rows(body: object) -> list[tuple[str, dict[str, object], float | None]]: ...
def extract_series(body: object) -> list[dict[str, object]]: ...
def matches(values: list[float], expected: float, tol: float = ...) -> bool: ...
def transitions(
    pairs: list[tuple[int, float]],
) -> list[tuple[int, float | None, float]]: ...
def query(base: str, promql: str) -> object: ...
def series(base: str, selector: str) -> object: ...
def names(base: str) -> object: ...
def label_values(base: str, label: str, selector: str | None = ...) -> object: ...
def export_samples(
    base: str, selector: str, since: object = ..., timeout: float = ...
) -> list[tuple[dict[str, object], list[tuple[int, float]]]]: ...
def reachable(base: str) -> tuple[bool, str]: ...
def producers(
    base: str,
) -> list[tuple[str, str, float | None, bool | None]]: ...
def otlp_gauge_payload(
    metric: str, value: float, at_unix: float, service: str, instance: str
) -> bytes: ...
def ping(
    base: str, at_unix: float, metric: str = ..., service: str = ...
) -> tuple[bool, str]: ...
def verify(
    base: str,
    selector: str,
    expected: float,
    deadline_s: float = ...,
    poll_s: float = ...,
    sink: Callable[[str], None] | None = ...,
) -> int: ...
def main(argv: list[str] | None = ...) -> int: ...
