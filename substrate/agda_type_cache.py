# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Read the elaborated-type cache and say whether it is stale.

⚑ THE READ PATH, SPLIT FROM THE BUILD PATH — and the split is what the consumer
already implied. `scratch/findings.py` imports exactly three names from the origin
(`load_cache`, `cache_is_stale`, `discover_modules`) and never the four that RUN
agda. A module whose consumers use half of it is two modules; the origin held both
halves behind 134 findings, so the cheap half could not be repaired at all.

⚑⚑ AND THE ORIGIN HARDCODED THREE ABSOLUTE PATHS, one of them `/tmp`. TMPDIR does
not say /tmp, and on this box `/tmp` is a small tmpfs shared with the editor and the
agent harness that has FILLED TWICE — after which children fail at spawn with ENOSPC,
which reads as "the tool is broken" rather than "the volume is full"
(`worklist_engine.scratch_root` records the incident and owns the general form of
that choice). The paths here derive from this file's own location instead, so a
checkout anywhere works and no writable path is assumed.

The cache maps `"<Module.Name>::<def-name>"` to `{"module", "asis", "normalised"}`.
Both rewrite levels are kept because they answer different questions: AsIs preserves
an orbit's structural identity (`Stab-C` and `Stab-D` stay distinct), while
Normalised collapses definitional equalities. A scorer that had only one of them
would silently conflate one of those two.
"""

from __future__ import annotations

from pathlib import Path

from substrate import json_reply

REPO_ROOT = Path(__file__).resolve().parent.parent
AGDA_ROOT = REPO_ROOT / "agda"
SUBSTRATE_ROOT = AGDA_ROOT / "Substrate"
CACHE_PATH = REPO_ROOT / "scratch" / ".agda_types.json"

Entry = dict[str, str]
Cache = dict[str, Entry]


def discover_modules() -> list[tuple[str, Path]]:
    """Return every `Substrate.*` module as (dotted name, path), sorted by path."""
    out: list[tuple[str, Path]] = []
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        rel = path.relative_to(AGDA_ROOT)
        out.append((".".join(rel.with_suffix("").parts), path))
    return out


def load_cache(cache_path: Path | None = None) -> Cache:
    """Return the cache as written, or `{}` when it has never been built.

    ⚑ AN ABSENT CACHE AND AN EMPTY ONE ARE THE SAME VALUE HERE, DELIBERATELY: both
    mean "no elaborated types available", which is the only distinction the caller
    acts on. Staleness is the question that DOES separate them, and it is
    `cache_is_stale`'s to answer — never inferred from emptiness.

    ⚑⚑ AND EVERY ENTRY IS RE-CHECKED RATHER THAN ASSERTED. The origin wrote
    `parsed: Cache = json.loads(text)`, which typeshed's `Any` accepted as a claim
    about a file on disk that nothing verified — a hand-edited or half-written cache
    would have flowed straight into the scorer as if typed. Malformed entries are
    dropped here, so a partial cache degrades to fewer entries instead of to a
    wrong-shaped one.
    """
    path = CACHE_PATH if cache_path is None else cache_path
    if not path.exists():
        return {}
    doc = json_reply.decode(path.read_text(encoding="utf8"))
    if not isinstance(doc, dict):
        return {}
    out: Cache = {}
    for qname, entry in doc.items():
        if isinstance(qname, str):
            out[qname] = json_reply.str_map(entry)
    return out


def cache_is_stale(
    modules: list[tuple[str, Path]],
    cache_path: Path | None = None,
) -> bool:
    """Report whether any module's source is newer than the cache, or it is missing.

    ⚑ MTIME IS A PROXY FOR CONTENT AND IT IS THE RIGHT ONE HERE, which is worth
    stating because this repo treats proxy-for-witness as a defect class. The
    failure mode is BOUNDED and self-correcting in the safe direction: a touched-
    but-unchanged file costs one needless rebuild, and the alternative — hashing
    ~3.5k files on every read — would cost more than the rebuild it averts. What
    mtime cannot catch (a rebuild that leaves the cache byte-identical) is not a
    wrong answer, only a wasted one.
    """
    path = CACHE_PATH if cache_path is None else cache_path
    if not path.exists():
        return True
    cache_mtime = path.stat().st_mtime
    return any(src.stat().st_mtime > cache_mtime for _, src in modules)
