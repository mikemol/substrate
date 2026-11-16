#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""An on-disk memo for a PURE FUNCTION OF FILE CONTENT, keyed by the content AND the deriver.

⚑⚑⚑ THE DERIVER BELONGS IN THE KEY, AND THE ORIGIN'S DOCSTRING WAS WRONG ABOUT THIS IN PRINT.
It claimed the sha of a file's bytes was *"the only key that is exactly as fresh as the answer"*.
It is not: same bytes, upgraded parsing library, DIFFERENT ANSWER — and a content-only key
deserialises the old artifact with no signal that it did. cassian-observability corrected this on
2026-08-03, reviewing an ask that quoted the sentence as the design to copy. Folding the deriver's
identity in makes a stale read UNREPRESENTABLE rather than merely unlikely.

⚑⚑ SCOPING TO FIT THE INSTRUMENT IS NOT FIXING THE INSTRUMENT, which is the incident that bought
this capability. A full-corpus parse blew a 120-second timeout twice, and the response was to
narrow the corpus to three directories — which makes the question cheaper by making it SMALLER,
i.e. answers a different question. The derivation is a pure function of content, so it is
cacheable and the scope can stay whole (user, 2026-08-02: *"not a problem or reason not to do the
analysis. But a good reason to hash-cons and memoize"*).

⚑ PROMOTED AS ITS OWN MODULE, NOT INLINED INTO THE FIRST READER THAT WANTS IT (⟡promote-pycodemod,
operator instruction). At the origin the cache is welded to ONE deriver — a libcst def-scanner —
so a second reader wanting memoisation either copies it or imports a def-scanner it does not need.
The cacheable thing is *a pure function of file bytes*; the def-scan is one instance. Here the
deriver is a PARAMETER and its identity is the caller's to declare, which is the only arrangement
where the freshness rule above can hold for a caller this module has never seen.

⚑ THE DERIVER TAG IS DECLARED BY THE CALLER, AND THAT IS DELIBERATE. This module cannot read the
version of a library it does not import. A tag it guessed would be the content-only key's failure
one level up — a key that LOOKS deriver-aware and is not, which is worse than none because it
stops anyone looking. `deriver_tag()` builds the string; the caller supplies the version.

⚑ A MISS MUST NEVER FAIL A QUERY. Every disk error falls through to the derivation. A cache is an
accelerator; a caller that crashes because its accelerator could not write has traded a slow
answer for no answer.

⚑ NOT `shared_cache`, WHICH IS A DIFFERENT CAPABILITY. That is a redis-backed store shared ACROSS
PROCESSES AND MACHINES under an LFU cap, with no-TTL/no-DELETE semantics and pickle serialisation.
This is a local directory of JSON blobs that a cold clone fills once — no daemon, no reachability
question, nothing to be down. A tool that must run when the store is unreachable needs this one.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# Bumped BY HAND when the shape of a cached record changes. ⚑ IT IS PART OF THE KEY, so a reshape
# MISSES rather than deserialising an old shape into a new reader — the same rule as the library
# version, applied to the one component no library reports.
SCHEMA = 1

# A record is whatever the deriver returns, provided it survives a JSON round-trip. ⚑ JSON, NOT
# PICKLE: this store is a build-artefact directory that a cold clone fills and a human may read,
# and an unpickle executes whatever it is handed. The narrower type is the point, not a limitation
# — a deriver returning something JSON cannot carry is one whose records this module must refuse
# rather than silently reshape.
Record = list[object]


def deriver_tag(version: str) -> str:
    """Return a deriver identity from a library version string.

    ⚑ THE VERSION IS READ FROM THE INSTALLED DISTRIBUTION BY THE CALLER, never declared as a
    constant. A declared version is a promise that must be kept by hand at every upgrade, and the
    upgrade is exactly the moment it will not be — which puts the stale read back.
    """
    return f"v={version};schema={SCHEMA}"


def key(raw: bytes, deriver: str) -> str:
    """Return the cache key for these bytes under this deriver.

    ⚑ THE DERIVER IS HASHED WITH THE CONTENT, NOT APPENDED TO THE PATH. A key that separated them
    would let a caller construct one half and read the other's artifact; hashing both together
    means a changed deriver cannot address a stale entry at all.

    ⚑⚑⚑ AND THE JOIN IS LENGTH-PREFIXED, BECAUSE PLAIN CONCATENATION IS AMBIGUOUS — INHERITED FROM
    THE ORIGIN AND CAUGHT BY THIS MODULE'S OWN SUITE. `sha1(raw + deriver.encode())` maps
    `(b"ab", "c")` and `(b"a", "bc")` to ONE key, so a caller can be served an artifact derived
    from different bytes by a different deriver. That is the stale read the deriver tag exists to
    make unrepresentable, reached by arithmetic instead of by an upgrade — the whole property
    defeated at the boundary between its two halves. The length pins where the content ends, so
    exactly one (content, deriver) pair addresses any key.
    """
    joined = b"%d:" % len(raw) + raw + deriver.encode()
    return hashlib.sha1(joined, usedforsecurity=False).hexdigest()


def blob_path(store: Path, cache_key: str) -> Path:
    """Return where an entry lives — fanned out by the key's first byte.

    ⚑ THE FAN-OUT IS NOT COSMETIC. A flat directory of one file per corpus file per deriver
    version reaches tens of thousands of entries, where several filesystems degrade on lookup.
    """
    return store / cache_key[:2] / (cache_key[2:] + ".json")


def read(store: Path, cache_key: str) -> Record | None:
    """Return a cached record, or None on any miss.

    ⚑⚑ THE DESERIALISED VALUE IS NARROWED BEFORE IT IS RETURNED, not annotated into shape. `json`
    hands back `Any`, and an `Any` returned as `Record` propagates into every consumer's type —
    the checker then verifies nothing downstream, silently, exactly where a corrupt or foreign
    blob would arrive. The `isinstance` is the narrowing that makes the annotation TRUE.

    ⚑ EVERY FAILURE IS A MISS, INCLUDING A CORRUPT BLOB. A half-written file from a killed process
    must derive again rather than raise — the alternative is a cache that can permanently break the
    tool it was added to accelerate.
    """
    try:
        with blob_path(store, cache_key).open(encoding="utf-8") as fh:
            got: object = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(got, list):
        return None
    return list(got)


def write(store: Path, cache_key: str, record: Record) -> bool:
    """Store a record. Returns whether it landed — never raises.

    ⚑ THE RETURN IS A FACT ABOUT THE WRITE, NOT A VERDICT ON THE CALL. A caller that treats False
    as failure has misread the contract; it is offered so a caller that WANTS to know (a warm-up
    pass reporting whether it warmed anything) can ask, instead of inferring from a later miss.
    """
    path = blob_path(store, cache_key)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(record, fh)
    except (OSError, TypeError, ValueError):
        # ⚑ `TypeError` IS THE DERIVER HANDING BACK SOMETHING JSON CANNOT CARRY. It is a real
        # contract violation, and it is still not this module's to raise: the caller's answer is
        # correct and complete, and only its memoisation failed.
        return False
    return True


def cached(store: Path, path: Path, deriver: str, derive: Callable[[str], Record]) -> Record:
    """Return `derive(text)` for one file, memoised on its content and the deriver's identity.

    ⚑⚑ THE FILE IS READ AS BYTES AND HASHED BEFORE IT IS DECODED, because the KEY must be over
    exactly what was on disk. Hashing a decoded-and-re-encoded string makes two files that differ
    only in invalid bytes collide — and this corpus is read with `errors="replace"`, which maps
    many distinct byte strings onto one.

    ⚑ AN UNREADABLE FILE DERIVES NOTHING AND CACHES NOTHING. Caching the empty answer for a file
    that was merely locked would serve that emptiness back forever, which is a false zero with a
    persistence layer.
    """
    try:
        raw = path.read_bytes()
    except OSError:
        return []
    cache_key = key(raw, deriver)
    hit = read(store, cache_key)
    if hit is not None:
        return hit
    out = derive(raw.decode("utf-8", "replace"))
    write(store, cache_key, out)
    return out
