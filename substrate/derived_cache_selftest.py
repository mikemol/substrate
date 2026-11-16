#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.derived_cache` — the stale read that must be unrepresentable.

⚑⚑⚑ THE DERIVER-CHANGE CASE IS THE ONE THAT MATTERS, AND THE ORIGIN SHIPPED WITHOUT IT while its
docstring claimed the property. Same bytes, upgraded library, different answer — a content-only
key hands back the OLD artifact and nothing says so. cassian-observability corrected this exact
sentence on 2026-08-03. A cache whose freshness rule is only asserted in prose is one whose rule
is not tested, and this suite exists so the claim is checkable rather than believed.

⚑⚑ AND EVERY *does not raise* CASE IS PAIRED WITH A POSITIVE CONTROL. A cache that swallowed
everything and always derived would pass the corrupt-blob case, the unwritable-store case and the
unreadable-file case all at once — while silently never caching anything. The paired hit cases are
what make those negatives mean the errors are absorbed rather than that the cache is inert.

⚑ THE DERIVER IS COUNTED, NOT ASSUMED. Several cases assert on how many times the derivation RAN,
because *was this a hit* is unobservable from the returned value alone — an equal answer is what a
correct hit and a silent re-derive both produce.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import derived_cache

_TWO = 2


class _Counter:
    """A deriver that records how many times it actually ran."""

    def __init__(self, answer: derived_cache.Record) -> None:
        """Hold the answer to return and start the call count at zero."""
        self.answer = answer
        self.calls = 0

    def __call__(self, text: str) -> derived_cache.Record:
        """Return the fixed answer and count the call."""
        self.calls += 1
        return [*self.answer, len(text)]


def a_second_read_does_not_re_derive(out: list[str]) -> int:
    """Check a repeated call for unchanged bytes hits the store.

    ⚑ THE POSITIVE CONTROL FOR THE WHOLE MODULE. Without it every error-absorbing case below would
    pass on a cache that never stored anything — and a cache that always misses is indistinguish-
    able from a correct one by its RESULTS, which is why the call count is what is asserted.
    """
    with tempfile.TemporaryDirectory() as where:
        store, src = Path(where) / "s", Path(where) / "f.py"
        src.write_text("x = 1\n", encoding="utf-8")
        deriver = _Counter(["a"])
        first = derived_cache.cached(store, src, "tag", deriver)
        second = derived_cache.cached(store, src, "tag", deriver)
        if deriver.calls != 1 or first != second:
            out.append(f"selftest: a repeated read re-derived: {deriver.calls} call(s)")
            return 1
    return 0


def a_changed_deriver_misses(out: list[str]) -> int:
    """Check the SAME bytes under a DIFFERENT deriver re-derive rather than serving the old blob.

    ⚑⚑⚑ THE CORRECTED CLAIM, MADE CHECKABLE. The origin's docstring called the content sha *"the
    only key that is exactly as fresh as the answer"*; it is not, across a library upgrade. A
    content-only key would hit here and return an artifact derived by a version that is gone —
    silently, which is what makes it worse than a crash.
    """
    with tempfile.TemporaryDirectory() as where:
        store, src = Path(where) / "s", Path(where) / "f.py"
        src.write_text("x = 1\n", encoding="utf-8")
        deriver = _Counter(["a"])
        derived_cache.cached(store, src, "libcst=1.0", deriver)
        derived_cache.cached(store, src, "libcst=2.0", deriver)
        if deriver.calls != _TWO:
            out.append(f"selftest: a changed deriver HIT a stale entry: {deriver.calls} call(s)")
            return 1
    return 0


def a_changed_file_misses(out: list[str]) -> int:
    """Check edited bytes re-derive — the content half of the key.

    ⚑ AN MTIME KEY RE-PARSES ON EVERY CHECKOUT AND A PATH KEY GOES STALE SILENTLY ON EDIT. This is
    the case that says the key is over the CONTENT, which is the only thing as fresh as the answer.
    """
    with tempfile.TemporaryDirectory() as where:
        store, src = Path(where) / "s", Path(where) / "f.py"
        src.write_text("x = 1\n", encoding="utf-8")
        deriver = _Counter(["a"])
        derived_cache.cached(store, src, "tag", deriver)
        src.write_text("x = 2\n", encoding="utf-8")
        derived_cache.cached(store, src, "tag", deriver)
        if deriver.calls != _TWO:
            out.append(f"selftest: an edited file HIT a stale entry: {deriver.calls} call(s)")
            return 1
    return 0


def the_schema_is_part_of_the_key(out: list[str]) -> int:
    """Check the record-shape version reaches the deriver tag.

    ⚑ IT IS THE ONE KEY COMPONENT NO LIBRARY REPORTS. A reshaped record under an unchanged library
    would otherwise deserialise an old shape into a new reader — the same stale read, arriving
    through the only door the version check does not cover.
    """
    if str(derived_cache.SCHEMA) not in derived_cache.deriver_tag("1.0"):
        out.append(f"selftest: the schema is absent from {derived_cache.deriver_tag('1.0')!r}")
        return 1
    return 0


def two_derivers_do_not_share_a_key(out: list[str]) -> int:
    """Check the key changes with the deriver for identical bytes."""
    if derived_cache.key(b"same", "one") == derived_cache.key(b"same", "two"):
        out.append("selftest: two derivers produced one key")
        return 1
    return 0


def two_contents_do_not_share_a_key(out: list[str]) -> int:
    """Check the key changes with the content under one deriver."""
    if derived_cache.key(b"one", "tag") == derived_cache.key(b"two", "tag"):
        out.append("selftest: two contents produced one key")
        return 1
    return 0


def the_key_hashes_deriver_and_content_together(out: list[str]) -> int:
    """Check the two halves cannot be traded off against each other.

    ⚑ CONCATENATION WITHOUT HASHING BOTH would let `(b"ab", "c")` and `(b"a", "bc")` address ONE
    entry — a caller could then read an artifact derived from different bytes by a different
    deriver, which is the stale read reached by arithmetic rather than by an upgrade.
    """
    if derived_cache.key(b"ab", "c") == derived_cache.key(b"a", "bc"):
        out.append("selftest: the key splits ambiguously between content and deriver")
        return 1
    return 0


def a_corrupt_blob_is_a_miss(out: list[str]) -> int:
    """Check an unparseable entry derives again rather than raising.

    ⚑ A HALF-WRITTEN FILE FROM A KILLED PROCESS must not permanently break the tool the cache was
    added to accelerate. The failure mode without this is a cache that poisons itself.
    """
    with tempfile.TemporaryDirectory() as where:
        store = Path(where) / "s"
        cache_key = derived_cache.key(b"x", "tag")
        blob = derived_cache.blob_path(store, cache_key)
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_text("{not json", encoding="utf-8")
        if derived_cache.read(store, cache_key) is not None:
            out.append("selftest: a corrupt blob was served as a hit")
            return 1
    return 0


def a_foreign_blob_shape_is_a_miss(out: list[str]) -> int:
    """Check a well-formed JSON value of the wrong SHAPE is refused.

    ⚑⚑ `json.load` HANDS BACK `Any`, and returning it unchecked would type-launder an object into
    a `Record` — the checker then verifies nothing downstream, precisely where a foreign blob
    arrives. The narrowing is what makes the annotation true, and this is the case that holds it.
    """
    with tempfile.TemporaryDirectory() as where:
        store = Path(where) / "s"
        cache_key = derived_cache.key(b"x", "tag")
        blob = derived_cache.blob_path(store, cache_key)
        blob.parent.mkdir(parents=True, exist_ok=True)
        blob.write_text('{"a": 1}', encoding="utf-8")
        if derived_cache.read(store, cache_key) is not None:
            out.append("selftest: a foreign blob shape was served as a hit")
            return 1
    return 0


def an_absent_entry_is_a_miss(out: list[str]) -> int:
    """Check reading an entry that was never written returns None rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        if derived_cache.read(Path(where) / "s", "deadbeef") is not None:
            out.append("selftest: an absent entry was served as a hit")
            return 1
    return 0


def an_unwritable_store_still_derives(out: list[str]) -> int:
    """Check a store that cannot be written falls through to the derivation.

    ⚑ A CACHE IS AN ACCELERATOR. A caller that crashed because its accelerator could not write
    would have traded a slow answer for no answer — and it would do so on exactly the machines
    where the cache matters least and the tool matters most.
    """
    with tempfile.TemporaryDirectory() as where:
        # A FILE where the store directory should be: every write beneath it must fail.
        store, src = Path(where) / "s", Path(where) / "f.py"
        store.write_text("not a directory\n", encoding="utf-8")
        src.write_text("x = 1\n", encoding="utf-8")
        deriver = _Counter(["a"])
        got = derived_cache.cached(store, src, "tag", deriver)
        if deriver.calls != 1 or not got:
            out.append(f"selftest: an unwritable store broke the derivation: {got!r}")
            return 1
    return 0


def an_unjsonable_record_does_not_raise(out: list[str]) -> int:
    """Check a record JSON cannot carry fails the WRITE without failing the CALL.

    ⚑ THE CALLER'S ANSWER IS CORRECT AND COMPLETE; only its memoisation failed. Raising here would
    make a deriver's return type a runtime hazard introduced by the cache, not by the deriver.
    """
    with tempfile.TemporaryDirectory() as where:
        store = Path(where) / "s"
        if derived_cache.write(store, "abcdef", [object()]):
            out.append("selftest: an unjsonable record reported a successful write")
            return 1
    return 0


def a_writable_record_reports_success(out: list[str]) -> int:
    """Check a normal write returns True — the control for the case above.

    ⚑ WITHOUT THIS, A `write` THAT ALWAYS RETURNED FALSE would pass, and the boolean a warm-up
    pass reports would be a constant rather than a measurement.
    """
    with tempfile.TemporaryDirectory() as where:
        if not derived_cache.write(Path(where) / "s", "abcdef", ["ok"]):
            out.append("selftest: a normal write reported failure")
            return 1
    return 0


def an_unreadable_file_caches_nothing(out: list[str]) -> int:
    """Check a missing file derives nothing AND stores nothing.

    ⚑ CACHING THE EMPTY ANSWER for a file that was merely absent would serve that emptiness back
    forever — a false zero with a persistence layer, which outlives the condition that caused it.
    """
    with tempfile.TemporaryDirectory() as where:
        store, src = Path(where) / "s", Path(where) / "gone.py"
        deriver = _Counter(["a"])
        got = derived_cache.cached(store, src, "tag", deriver)
        if got != [] or deriver.calls:
            out.append(f"selftest: a missing file derived {got!r} in {deriver.calls} call(s)")
            return 1
    return 0


def the_blob_path_fans_out(out: list[str]) -> int:
    """Check entries are nested by the key's first byte rather than laid flat."""
    path = derived_cache.blob_path(Path("/s"), "abcdef")
    if path.parent.name != "ab" or path.name != "cdef.json":
        out.append(f"selftest: the blob path does not fan out: {path}")
        return 1
    return 0


_ARMS = (
    a_second_read_does_not_re_derive,
    a_changed_deriver_misses,
    a_changed_file_misses,
    the_schema_is_part_of_the_key,
    two_derivers_do_not_share_a_key,
    two_contents_do_not_share_a_key,
    the_key_hashes_deriver_and_content_together,
    a_corrupt_blob_is_a_miss,
    a_foreign_blob_shape_is_a_miss,
    an_absent_entry_is_a_miss,
    an_unwritable_store_still_derives,
    an_unjsonable_record_does_not_raise,
    a_writable_record_reports_success,
    an_unreadable_file_caches_nothing,
    the_blob_path_fans_out,
)

_CASE_COUNT = 15


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"derived-cache selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"derived-cache selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
