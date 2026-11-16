# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Assemble the elaborated-type cache: discover, drive agda, fold replies, write.

The orchestration over `substrate.agda_type_build`'s pieces and
`substrate.agda_type_cache`'s paths. Run as a CLI (`--force` to rebuild regardless of
staleness) or call `build_cache` directly.

⚑ THE DISPATCH LIVES HERE SO THE ORIGIN CAN BE RETIRED. `scratch/agda_types.py` held
discovery, wrapper-writing, the agda invocation, reply parsing, cache folding AND the
`__main__` block in one file with 134 findings — where the per-file gate refuses every
edit, so the `/tmp` hardcoding inside it could not be repaired at all. Extracting one
concern would have stranded (the only consumer of the extracted half was the origin
itself); moving the dispatch is what finishes the drain rather than starting one.

⚑⚑ THE WRAPPER GOES IN A TEMPORARY DIRECTORY THAT IS REMOVED AFTER THE RUN. The origin
left `/tmp/AgdaQueryAll.agda` behind on every invocation, so a later agda run with
`-i /tmp` could resolve `AgdaQueryAll` from a previous run's leftovers. A
`TemporaryDirectory` honours TMPDIR and cleans up, so neither hazard survives.

⚑⚑⚑ AND PROGRESS IS RETURNED, NOT PRINTED. `build_cache` hands back the lines it would
have emitted, so a caller can test what a run reported without capturing a stream — and
the partial-result notice (agda erroring mid-batch) becomes a value a test can assert on
rather than text nobody checks.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

from substrate import agda_type_build as build
from substrate import json_reply
from substrate.agda_type_cache import (
    CACHE_PATH,
    Cache,
    cache_is_stale,
    discover_modules,
    load_cache,
)

REWRITE_LEVELS = ("asis", "normalised")
MAX_REPORTED_ERRORS = 5

_USAGE = """\
usage: agda_types.py [--force]

Build the elaborated-type cache for every Substrate module.

  --force   rebuild even when the cache is newer than every source
"""


def fold_payloads(
    modules: list[tuple[str, Path]],
    payloads: list[list[object]],
) -> Cache:
    """Fold positional agda replies into `{qname: {module, asis, normalised}}`.

    ⚑ THE TWO PASSES ARE SLICED BY COUNT, NOT SEARCHED FOR. `batch_script` emits AsIs
    for every module and then Normalised for every module, so reply *i* belongs to
    `modules[i % len(modules)]` at level `i // len(modules)`. A short reply list (agda
    erroring partway) therefore truncates the TAIL rather than mis-assigning the head,
    which is why each window is bounded by what arrived rather than what was asked for.
    """
    cache: Cache = {}
    count = len(modules)
    for level_index, level in enumerate(REWRITE_LEVELS):
        window = payloads[level_index * count : (level_index + 1) * count]
        for module_index, items in enumerate(window):
            module, _ = modules[module_index]
            for item in items:
                name = json_reply.text_field(item, "name")
                if not name:
                    continue
                entry = cache.setdefault(
                    f"{module}::{name}",
                    {"module": module, "asis": "", "normalised": ""},
                )
                entry[level] = " ".join(json_reply.text_field(item, "term").split())
    return cache


def build_cache(*, force: bool = False) -> tuple[Cache, list[str]]:
    """Rebuild the cache when stale or forced, returning it with a progress report."""
    log: list[str] = []
    modules = discover_modules()
    log.append(f"discovered {len(modules)} Substrate modules")

    if not force and not cache_is_stale(modules):
        log.append(f"cache fresh ({CACHE_PATH})")
        return load_cache(), log

    agda = build.resolve_agda()
    log.append(f"using {agda}")

    with tempfile.TemporaryDirectory(prefix="agda-types-") as tmp:
        wrapper = Path(tmp) / f"{build.WRAPPER_NAME}.agda"
        wrapper.write_text(build.wrapper_text(modules), encoding="utf8")
        log.append(f"running agda (1 load + {2 * len(modules)} queries)")
        started = time.time()
        proc = build.run_agda(wrapper, build.batch_script(wrapper, modules))
        elapsed = time.time() - started

    log.append(f"agda done in {elapsed:.1f}s (exit {proc.returncode})")

    payloads, errors = build.parse_module_contents(proc.stdout)
    log.extend(f"agda error: {msg[:200]}" for msg in errors[:MAX_REPORTED_ERRORS])
    if len(errors) > MAX_REPORTED_ERRORS:
        log.append(f"{len(errors)} error(s) reported by agda in total")

    expected = len(REWRITE_LEVELS) * len(modules)
    if len(payloads) != expected:
        log.append(f"PARTIAL: expected {expected} payloads, got {len(payloads)}")

    cache = fold_payloads(modules, payloads)
    CACHE_PATH.write_text(json_reply.dumps_stable(cache), encoding="utf8")
    log.append(f"wrote {len(cache)} defs to {CACHE_PATH}")
    return cache, log


def main(argv: list[str]) -> int:
    """Build the cache and report what it holds.

    ⚑ ARGV IS READ DIRECTLY RATHER THAN THROUGH `argparse`, whose `Namespace`
    attributes are untyped — `args.force` is an `Any` that spreads into every use.
    One flag does not need a parser, and the repo's other CLIs read argv the same way.
    """
    if "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0
    unknown = [a for a in argv if a != "--force"]
    if unknown:
        sys.stderr.write(f"agda_types: unrecognised argument(s): {' '.join(unknown)}\n")
        sys.stderr.write(_USAGE)
        return 2
    try:
        cache, log = build_cache(force="--force" in argv)
    except build.AgdaMissingError as exc:
        sys.stderr.write(f"agda_types: {exc}\n")
        return 1
    for line in log:
        sys.stderr.write(f"agda_types: {line}\n")
    sys.stderr.write(f"agda_types: {len(cache)} entries cached\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
