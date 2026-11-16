# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The five transcript-memory-index probes, drained from `scratch/tmi_probe*.py` (2026-09-24).

Each probe asked one question of one transcript, read-only:

    1  do grammar clusters survive the change of corpus, and is retraction grammar-visible?
    2  do clusters cross actors, and does a retraction cue re-quote an EARLIER phrase?
    3  the duplicate-envelope hazard: long text bodies that appear more than once
    4  which exchange unit clusters: prose-only, full tool traffic, or NORMALISED tool traffic?
    5  is the WARRANT recoverable: is a claim's named tool invoked in the same exchange?

    python -m substrate.tmi_probes N TRANSCRIPT.jsonl MEMORY_DIR

⚑ DRAINED, NOT REWRITTEN. The scratch probes each carried 57-124 findings, so no edit to them could
land; their logic moved here unchanged, onto `transcript_units` (mtools' reader) and
`phrase_lattice` (the memory clusterer, loaded without `sys.path`). The scratch files are now shims.
⚑ ONE MEASURED DIFFERENCE: the scratch reader truncated tool text at 20k/4k characters and mtools'
reader does not, so probes 4 and 5 can count more tokens than their historical runs did.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import phrase_lattice, transcript_units

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate.transcript_units import Unit, Units

_END = 10**9
_PHRASE_MIN, _MIN_MEMBERS, _TAU = 3, 2, 0.5
_SHOW = 25
_LONG = 400
_RESULT_KEEP = 800
_SENTENCE_MIN = 40

_RETRACT_WIDE = re.compile(
    r"retract|withdraw|superseded|I was wrong|that'?s wrong|not correct|correction|reopened|"
    r"scratch that|actually,? no|never mind|you'?re right|my (mistake|error)|overclaim|"
    r"walk (that|it) back",
    re.IGNORECASE,
)
_RETRACT_NARROW = re.compile(
    r"retract|withdraw|superseded|i was wrong|correction|"
    r"you'?re right|overclaim|my (mistake|error)",
    re.IGNORECASE,
)
_CMD = re.compile(
    r"\b([a-z_]+\.py|agda_defs|pycodemod|mdstruct|bibstruct|"
    r"transcriptstruct|membudget|sppf_db|schema|query_defs)\b"
)
_NUM = re.compile(r"\b\d[\d,]*\b")
_BOILER = re.compile(
    r"home mikemol|tmp claude|file path|github substrate|api error|"
    r"permission action|success true|list run con|^python |output command"
)
_TOOL_KEYS = (
    "command",
    "description",
    "pattern",
    "query",
    "file_path",
    "prompt",
    "old_string",
    "new_string",
)
_WHOLE_KEYS = frozenset({"command", "description", "pattern", "query"})

type Clusters = list[tuple[str, frozenset[str]]]
type Out = list[str]


def _cluster(lat: phrase_lattice.Lattice, items: list[tuple[str, list[str]]]) -> Clusters:
    """Cluster with the probes' fixed parameters."""
    return lat.cluster_phrases(items, _PHRASE_MIN, _MIN_MEMBERS, _TAU)


def _between(stream: list[Unit], lo: int, hi: int) -> list[str]:
    """Return the texts of `stream` whose line falls in `[lo, hi)`."""
    return [t for i, t in stream if lo <= i < hi]


def _bounds(human: list[Unit]) -> list[int]:
    """Return each human turn's line plus a sentinel: exchange n spans `[b[n], b[n+1])`."""
    return [i for i, _t in human] + [_END]


def _histogram(clusters: Clusters) -> dict[int, int]:
    """Return members -> number of clusters of that size."""
    return dict(sorted(collections.Counter(len(m) for _p, m in clusters).items()))


def probe1(u: Units, lat: phrase_lattice.Lattice, out: Out) -> None:
    """Measure whether clusters survive the corpus change and retraction is grammar-visible."""
    asst = transcript_units.assistant_turns(u)
    tool = sorted(u.tool_use + u.tool_result)
    for label, items in (("human", u.human), ("assistant-text", asst), ("tool", tool)):
        tokens = sum(len(lat.words(s)) for _i, s in items)
        out.append(f"{label:16s} envelopes={len(items):5d}  content-tokens={tokens}")
    bounds = _bounds(u.human)
    ex = [
        (
            f"turn{bounds[n]:05d}",
            lat.words(u.human[n][1] + "\n" + "\n".join(_between(asst, bounds[n], bounds[n + 1]))),
        )
        for n in range(len(u.human))
    ]
    out.append(f"\nexchanges={len(ex)}  tokens={[len(t) for _n, t in ex]}")
    clusters = _cluster(lat, ex)
    out.append(f"clusters={len(clusters)}")
    out.append(f"cluster-size histogram (members -> n clusters): {_histogram(clusters)}")
    out.extend(f"  [{len(m):2d}] «{p}»" for p, m in clusters[:_SHOW])
    hits: collections.Counter[tuple[str, str]] = collections.Counter()
    for label, items in (("human", u.human), ("assistant-text", asst)):
        for _i, s in items:
            for mm in _RETRACT_WIDE.finditer(s):
                hits[label, mm.group(0).lower()[:20]] += 1
    out.append("\nretraction-cue hits by (source, cue):")
    out.extend(f"  {v:4d}  {k[0]:15s} {k[1]}" for k, v in hits.most_common(30))
    out.append(f"total human cues: {sum(v for k, v in hits.items() if k[0] == 'human')}")
    out.append(f"total asst  cues: {sum(v for k, v in hits.items() if k[0] != 'human')}")


def _actor_units(
    u: Units,
    lat: phrase_lattice.Lattice,
) -> tuple[list[tuple[str, list[str]]], dict[str, str]]:
    """Return one human unit and one assistant unit per exchange, tagged by actor."""
    asst = transcript_units.assistant_turns(u)
    bounds = _bounds(u.human)
    items: list[tuple[str, list[str]]] = []
    actor: dict[str, str] = {}
    for n in range(len(u.human)):
        lo, hi = bounds[n], bounds[n + 1]
        items.append((f"H{lo:05d}", lat.words(u.human[n][1])))
        actor[f"H{lo:05d}"] = "human"
        body = "\n".join(_between(asst, lo, hi))
        if body.strip():
            items.append((f"A{lo:05d}", lat.words(body)))
            actor[f"A{lo:05d}"] = "actor"
    return items, actor


def probe2(u: Units, lat: phrase_lattice.Lattice, out: Out) -> None:
    """Measure cross-actor clusters and retraction cues that re-quote an EARLIER phrase."""
    items, actor = _actor_units(u, lat)
    clusters = _cluster(lat, items)
    out.append(f"actor-split units={len(items)}  clusters={len(clusters)}")
    crossed = 0
    for p, m in clusters:
        acts = {actor[x] for x in m}
        tag = "CROSS-ACTOR" if len(acts) > 1 else f"single:{next(iter(acts))}"
        crossed += tag == "CROSS-ACTOR"
        out.append(f"  [{len(m):2d}] {tag:14s} «{p[:80]}»")
    out.append(
        f"\ncross-actor clusters: {crossed} of {len(clusters)}"
        f"  ({100 * crossed // max(1, len(clusters))}%)"
    )
    first = {p: sorted(int(x[1:]) for x in m) for p, m in clusters}
    found = 0
    for i, s in transcript_units.assistant_turns(u):
        cue = _RETRACT_NARROW.search(s)
        if not cue:
            continue
        said = " " + " ".join(lat.words(s)) + " "
        back = [p for p, idxs in first.items() if f" {p} " in said and idxs and idxs[0] < i]
        if back:
            found += 1
            out.append(f"\nRETRACTION-CANDIDATE turn {i}: cue={cue.group(0)!r}")
            out.extend(f"    re-quotes «{p[:70]}» first used @{first[p][0]}" for p in back[:4])
    out.append(f"\ncue-turns that re-quote an earlier cluster phrase: {found}")


def probe3(path: Path, out: Out) -> None:
    """List long text bodies that appear under more than one envelope."""
    dupes: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    for i, kind, text in transcript_units.record_texts(path):
        if len(text) > _LONG:
            dupes[text[:_LONG]].append((i, kind))
    repeated = {k: v for k, v in dupes.items() if len(v) > 1}
    out.append(f"distinct long text bodies: {len(dupes)};  appearing >1x: {len(repeated)}")
    out.extend(f"  x{len(v)}  {v}   {k[:70]!r}" for k, v in repeated.items())


def norm_tool_use(text: str) -> str:
    """Keep a tool call's COMMAND and SHAPE, drop the payload."""
    try:
        body: object = json.loads(text)
    except json.JSONDecodeError:
        return ""
    if not isinstance(body, dict):
        return ""
    parts: list[str] = []
    for key in _TOOL_KEYS:
        value: object = body.get(key)
        if isinstance(value, str):
            parts.append(value[:300] if key in _WHOLE_KEYS else Path(value).name[:80])
    return " ".join(parts)


def norm_tool_result(text: str) -> str:
    """Keep a result's first and last 400 characters: the verdict lines, not the body."""
    t = text.strip()
    return t if len(t) <= _RESULT_KEEP else t[:_LONG] + " " + t[-_LONG:]


def _exchange_units(
    u: Units,
    lat: phrase_lattice.Lattice,
    mode: str,
) -> list[tuple[str, list[str]]]:
    """Build one unit per exchange: A prose-only, B full tool traffic, C normalised traffic."""
    keep: Callable[[str], str] = str
    use: Callable[[str], str] = norm_tool_use if mode == "C" else keep
    res: Callable[[str], str] = norm_tool_result if mode == "C" else keep
    bounds = _bounds(u.human)
    units: list[tuple[str, list[str]]] = []
    for n in range(len(u.human)):
        lo, hi = bounds[n], bounds[n + 1]
        parts = [u.human[n][1], *_between(u.assistant, lo, hi)]
        if mode in {"B", "C"}:
            parts += [use(t) for t in _between(u.tool_use, lo, hi)]
            parts += [res(t) for t in _between(u.tool_result, lo, hi)]
        units.append((f"turn{lo:05d}", lat.words("\n".join(parts))))
    return units


def probe4(u: Units, lat: phrase_lattice.Lattice, out: Out) -> None:
    """Compare the three exchange-unit constructions head to head."""
    for mode, label in (
        ("A", "prose-only"),
        ("B", "full tool traffic"),
        ("C", "normalised tool traffic"),
    ):
        units = _exchange_units(u, lat, mode)
        clusters = _cluster(lat, units)
        out.append(f"\n===== {mode}: {label} =====")
        out.append(
            f"units={len(units)}  tokens={sum(len(t) for _n, t in units)}  clusters={len(clusters)}"
        )
        out.append(f"band histogram (members -> n clusters): {_histogram(clusters)}")
        out.extend(f"  [{len(m):2d}] «{p[:96]}»" for p, m in clusters[:22])


_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    """Split prose after `.`, `!` or `?`, by match SPANS (`re.split` is typed `Any`)."""
    out: list[str] = []
    start = 0
    for m in _SENTENCE_END.finditer(text):
        out.append(text[start : m.start()])
        start = m.end()
    out.append(text[start:])
    return out


def _claims(prose: list[str], cmds: list[str]) -> tuple[int, int]:
    """Count claim-bearing sentences, and those whose named tool is invoked in the exchange."""
    claims = backed = 0
    for text in prose:
        for s in _sentences(text):
            if len(s) < _SENTENCE_MIN or not (_CMD.search(s) or _NUM.search(s)):
                continue
            claims += 1
            # sliced by span: `findall`/`group` are typed `Any` in the stubs.
            named = {s[m.start() : m.end()] for m in _CMD.finditer(s)}
            backed += bool(named) and any(any(x in c for x in named) for c in cmds)
    return claims, backed


def _members(cluster: tuple[str, frozenset[str]]) -> int:
    """Return a cluster's member count, the sort key for the gained-cluster listing."""
    return len(cluster[1])


def probe5(u: Units, lat: phrase_lattice.Lattice, out: Out) -> None:
    """Measure warrant recoverability and what tool-traffic clusters add."""
    bounds = _bounds(u.human)
    out.append("exchange  proseblk  toolcalls  toolres  claim-sents  cmd-matched")
    total = matched = with_cmds = 0
    for n in range(len(u.human)):
        lo, hi = bounds[n], bounds[n + 1]
        prose, cmds = _between(u.assistant, lo, hi), _between(u.tool_use, lo, hi)
        res = _between(u.tool_result, lo, hi)
        claims, backed = _claims(prose, cmds)
        total, matched, with_cmds = total + claims, matched + backed, with_cmds + bool(cmds)
        out.append(
            f"  {lo:6d}  {len(prose):8d}  {len(cmds):9d}  {len(res):7d}  {claims:11d}  {backed:11d}"
        )
    out.append(f"\nclaim-bearing sentences: {total}")
    out.append(
        f"  with the named tool INVOKED in the same exchange: {matched} "
        f"({100 * matched // max(1, total)}%)"
    )
    out.append(f"exchanges containing >=1 tool call: {with_cmds} of {len(u.human)}")
    prose_only = {p for p, _m in _cluster(lat, _exchange_units(u, lat, "A"))}
    gained = [(p, m) for p, m in _cluster(lat, _exchange_units(u, lat, "B")) if p not in prose_only]
    out.append(f"\nclusters gained by admitting tool traffic: {len(gained)}")
    boiler = 0
    for p, m in sorted(gained, key=_members, reverse=True):
        kind = "BOILERPLATE" if _BOILER.search(p) else "warrant?"
        boiler += kind == "BOILERPLATE"
        out.append(f"  [{len(m):2d}] {kind:11s} «{p[:78]}»")
    out.append(f"\n  boilerplate {boiler}   candidate-warrant {len(gained) - boiler}")


USAGE = "usage: python -m substrate.tmi_probes {1|2|3|4|5} TRANSCRIPT.jsonl MEMORY_DIR\n"


def run(probe: str, path: Path, memory: Path, out: Out) -> int:
    """Run one probe over one transcript; return 2 for an unknown probe."""
    if probe == "3":
        probe3(path, out)
        return 0
    probes = {"1": probe1, "2": probe2, "4": probe4, "5": probe5}
    chosen = probes.get(probe)
    if chosen is None:
        return 2
    out.append(f"=== {path.name} ===")
    chosen(transcript_units.split(path), phrase_lattice.load(memory), out)
    return 0


def main(argv: list[str]) -> int:
    """Parse `N PATH MEMORY_DIR` and run that probe.

    ⚑ `MEMORY_DIR` IS A REQUIRED ARGUMENT, NOT A DEFAULT (W35, operator 2026-09-24): the caller
    names the memory directory rather than this module guessing a fixed one.
    """
    expected = 3
    if len(argv) != expected:
        sys.stderr.write(USAGE)
        return 2
    out: Out = []
    code = run(argv[0], Path(argv[1]), Path(argv[2]), out)
    if code:
        sys.stderr.write(USAGE)
    sys.stdout.write("\n".join(out) + ("\n" if out else ""))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
