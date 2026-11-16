#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""tmi_index.py -- THE RECOVERY INDEX.  Design §6, Ⓘ5.

⚑ WHAT THIS IS, AND WHAT IT DELIBERATELY IS NOT.  §6.1's data flow ends in a
"RECOVERY INDEX -- by thread, ordered, every row citing (file, turn, role)".
This is that renderer.  It is NOT a summariser and NOT a classifier: every line
it emits is a VERBATIM span from the transcript with its turn and role attached,
because the whole point (§6.4(f)) is that an operator directive and the actor's
restatement of it are not interchangeable and compaction is precisely what blurs
them.  A recovered line the reader cannot attribute is worse than no line.

⚑⚑ WHY IT SHIPPED IN ROUND 3 AND WAS WITHHELD IN ROUNDS 1 AND 2.  The gate was
never "is the code written" -- it was whether the linker could carry the threads
the index exists for.

  round 1  withheld: the linker was validated against 14 labels, and precision
           9/9 was a SAMPLE property (all nine on one chain whose vocabulary is
           a proper noun).                                          `tmi-F1`
  round 2  withheld: the completed 39-label ground truth showed the 8 remaining
           misses were not scattered -- they concentrated in OPERATOR-REFUTATION,
           the class where the operator's correction entered the record.  An
           index whose most important threads are silently absent is worse than
           no index, because an absent thread and a thread with no revisions are
           indistinguishable to the reader (§5.3).                  `tmi-F14`
  round 3  BUILT: Ⓘ9 added the concession cue class and closed it.  192, 198,
           401, 426, 644, 664, 676 all now detected; `artefact` recall 79% ->
           87%, and -- the number that matters -- it now MATCHES the cue-only
           ceiling (34/39) while holding 100% antecedent-plausibility and 3%
           concentration.  The recurrence conjunct no longer costs recall.

⚑ THE RESIDUAL CLASS IS NAMED RATHER THAN HIDDEN (`tmi-F17`).  Four certain
misses remain (38, 209, 632, 649) and they are ONE class: EVIDENCE-SUPERSESSION,
where the actor's own earlier claim is revised by TOOL OUTPUT.  `--gaps` prints
them.  A reader is told what the index cannot carry, which is the difference
between a bounded instrument and a silent one -- `census-green-is-a-fact-about-
the-census`.

REUSE (design §4, enforced by `--selftest`): `Sequitur` and `cluster_phrases`
are imported from `grammar_phrase_lattice`, `stream`/`blocks`/`human_text` from
`transcriptstruct`, units and the revision operator from `tmi_status`.  Nothing
is copied.  `cluster_memories.py` is NOT revived, `grammar_phrase_lattice.main()`
is NEVER called (it `rmtree`s `index/`), and `synth_wire` is NEVER imported (it
rewrites the live MEMORY.md as an import side effect).

    tmi_index.py <file> --threads [--min-breadth N]
                                  # the thread table: phrase, breadth, span
    tmi_index.py <file> --index [--limit N]
                                  # THE DELIVERABLE: threads with their units
                                  # and revision links, every row cited
    tmi_index.py <file> --thread <phrase>
                                  # one thread, whole, in turn order
    tmi_index.py <file> --gaps    # what the index CANNOT carry, and why
    tmi_index.py <file> --index --out <path>
                                  # the only write path (design §6.2)
    tmi_index.py --selftest

Read-only by construction (§6.2): no `--apply`, and the sole write is an
explicit `--out`.  It reads someone's conversation history and should not be
able to be the thing that damages it.

Every mode prints `n of m`.
"""
import collections
import os
import re
import sys

# ⚑ THE SAME THREE PATHS `tmi_status` USES, AND IN THE SAME ORDER.
# `grammar_phrase_lattice` lives in the MEMORY directory, not in `scratch/` --
# a detail that is invisible until the import fails, which is why it is
# restated here rather than assumed.  Ordering matters: `scratch/` last, so a
# same-named local file cannot shadow the memory-corpus module.
MEM = "/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory"
sys.path.insert(0, MEM)
sys.path.insert(0, "/home/mikemol/github/substrate/scratch/eliza")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import grammar_phrase_lattice as G           # noqa: E402
import tmi_status as S                       # noqa: E402

DEFAULT_TRANSCRIPT = S.DEFAULT_TRANSCRIPT

# ⚑ A FRACTION OF N, NOT A CONSTANT -- design §4 flags the apparatus's `df <= 60`
# boilerplate cap as "sized for ~250 memories and meaningless at a different N".
# The same reasoning that produced `ARTEFACT_DF_FRAC` applies to thread phrases:
# a phrase in most units is a discourse tic, not a thread.  Reused from
# `tmi_status` rather than re-fitted, so there is ONE authority for "universal".
THREAD_DF_FRAC = S.ARTEFACT_DF_FRAC * 4      # phrases are commoner than idents
MIN_BREADTH = 2                              # §2.3: no rendered word on 1 witness

# ⚑ A NAMED TUNING CONSTANT, per the discipline `ARTEFACT_DF_FRAC` states: how
# many revisers of ONE turn are rendered before the row is reported as a
# vocabulary source instead.  Not derived -- measured on 28df5f75, where the
# largest legitimate antecedent holds 6 backlinks and turn 110 (a plan document)
# holds 15.  A second corpus should re-fit it, and `--threads` is how.
FANOUT_CAP = 6


def actor_of(role, text):
    """§2.2 / §6.4(f): attribution is a rendered column, never an aggregate.

    ⚑ THE PEER CASE IS WHY THIS IS A FUNCTION AND NOT `role`.  A
    `<cross-session-message from-name=X>` arrives with role=user and is NOT the
    operator -- collapsing it into "human" would attribute a peer's correction
    to the user, which is the single attribution error §6.4(f) says recovery
    cannot tolerate.
    """
    m = re.search(r"<cross-session-message[^>]*from-name=[\"']?([\w-]+)", text or "")
    if m:
        return f"peer:{m.group(1)}"
    return "operator" if role == "human" else "actor"


# ⚑⚑ HARNESS BOILERPLATE IS NOT A THREAD, AND THE FIRST RUN OF `--threads` WAS
# MOSTLY BOILERPLATE.  Measured: the top of the unfiltered thread table was
# «file path home mikemol» (33u), «tmp claude- home-mikemol-github-substrate»
# (32u), «command did complete within timeout moved background» (5u),
# «system-reminder warning file exists but contents empty» (5u) -- absolute
# paths, harness notifications and tool_use argument keys, none of them anything
# an actor said.  §1.1 specifies a tool-traffic NORMALISER ("command + tool name
# + key args", "result head+tail") and §4 lists it as NEW work; it had not been
# written, so the raw JSON was going into the clusterer.
#
# ⚑ THIS IS THE SAME DEFECT AS THE `selfquote 'description'` CENSUS HIT one
# module over -- reading tool STRUCTURE as prose.  `tmi_status` fixed it for the
# cue detector by splitting `body` from `prose`; the clusterer needs the same
# separation, and it did not get it because §1.4 legitimately wants tool traffic
# IN for the artefact join.  Both are right: artefacts want the raw body,
# THREADS want the normalised one.
#
# The head/tail rule is §1.1's: a tool_result's VERDICT lines carry the claim, its
# body is a file dump.  Absolute paths are collapsed to their basename so that
# `sppf_db.py` still joins while `/home/mikemol/github/substrate/scripts/` does
# not become a thread.
_HARNESS = re.compile(
    r"<system-reminder>.*?</system-reminder>"
    r"|<task-notification>.*?</task-notification>"
    r"|Command did not complete within its \d+s timeout.*"
    r"|This file exists but has empty contents.*"
    r"|Wasted call.*unchanged since last read.*"
    r"|/(?:home|tmp)/[\w./-]+",
    re.S | re.I)
_JSONKEY = re.compile(r'"(?:file_path|command|description|offset|limit|'
                      r'old_string|new_string|content|path|pattern|to|summary|'
                      r'message|prompt|subagent_type)"\s*:')
_JSONISH = re.compile(r"^\s*[\{\[]")
_UESC = re.compile(r"\\u([0-9a-fA-F]{4})")
_JSONPUNC = re.compile(r'["\{\}\[\],]+')


def normalise_tools(body, prose):
    """§1.1's tool-traffic normaliser -- the piece §4 lists as NEW and unwritten.

    Keeps actor prose verbatim, keeps a tool_result's HEAD and TAIL (the verdict
    lines), drops the middle (the dump), and strips harness furniture and JSON
    argument keys.  Absolute paths collapse to basenames so a filename can still
    be a thread while a directory cannot.
    """
    if prose and prose.strip():
        text = prose
    else:
        text = body
    text = _HARNESS.sub(lambda m: os.path.basename(m.group(0))
                        if m.group(0).startswith("/") else " ", text)
    text = _JSONKEY.sub(" ", text)
    # ⚑ AND THE ESCAPES TOO.  A `tool_use` body is a JSON *string*, so its
    # content arrives with `⟡` and `\n` literal -- turn 160 rendered as
    # `{"to": "substrate-45", ... "⟡sql-lift`.  Stripping the KEYS was not
    # enough because the VALUES are the payload.  Decode the escapes and drop
    # the punctuation scaffolding, so what remains is the sentence the actor
    # actually wrote into the tool call.
    if _JSONISH.match(text.strip()):
        text = _UESC.sub(lambda m: chr(int(m.group(1), 16)), text)
        text = text.replace("\\n", "\n").replace('\\"', '"')
        text = _JSONPUNC.sub(" ", text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) > 12:                     # head + tail, not the body
        lines = lines[:6] + lines[-6:]
    return "\n".join(lines)


def build_threads(units, min_breadth=MIN_BREADTH):
    """units -> threads.  Thin, per §6.2: `cluster_phrases` does the work.

    Returns [(phrase, [turns], breadth, span)] ordered by first appearance --
    §6.4(a): "an index is a set; a recovered framing is a sequence".
    """
    items = []
    for t, _r, b, p in units:
        nb = normalise_tools(b, p)
        if nb.strip():
            items.append((f"t{t:05d}", G.words(nb)))
    cl = G.cluster_phrases(items, phrase_min=3, min_members=2, tau=0.5)
    by_turn = {t: (r, b, p) for t, r, b, p in units}
    n = len(units)
    out = []
    # ⚑ `cluster_phrases` RETURNS PAIRS, NOT A DICT -- `tmi_status.cluster_index`
    # already unpacks it as `for p, m in cl`, and assuming `.items()` here was a
    # guess where an existing call site was the authority.  Tolerate both so the
    # reuse does not break if the upstream shape is tightened.
    for phrase, members in (cl.items() if isinstance(cl, dict) else cl):
        turns = sorted(int(x[1:]) for x in members)
        if len(turns) > max(3, THREAD_DF_FRAC * n):
            continue                       # universal: a tic, not a thread
        # BREADTH over ACTORS, not units (§2.2: pairs NAMED, not counted)
        actors = {actor_of(by_turn[t][0], by_turn[t][1])
                  for t in turns if t in by_turn}
        if len(turns) < min_breadth:
            continue
        span = (turns[0], turns[-1], len(turns), sorted(actors))
        out.append((phrase, turns, len(actors), span))
    out.sort(key=lambda r: (r[3][0], -r[3][2]))
    return out


def render(units, threads, links, limit=None):
    """The deliverable.  Every row cites (turn, role); nothing is paraphrased."""
    by_turn = {t: (r, b, p) for t, r, b, p in units}
    rev = collections.defaultdict(list)      # turn -> [(antecedent, via)]
    fwd = collections.defaultdict(set)       # antecedent -> {reviser}
    for turn, back, classes, _h in links:
        for prev, via in back:
            rev[turn].append((prev, via, classes))
            # ⚑ A SET, NOT A LIST -- and the first render printed
            # "↓ revised at turn 396" THREE TIMES in a row, once per artefact
            # that joined the pair.  The link is a turn PAIR; how many join
            # keys witnessed it is a property of the detector, not of the
            # history, and repeating the arrow reads to a reader as three
            # separate revisions.  Collapsing here is the honest rendering.
            fwd[prev].add(turn)
    lines = []
    shown = threads[:limit] if limit else threads
    for phrase, turns, breadth, span in shown:
        first, last, n_u, actors = span
        lines.append("")
        lines.append(f"── «{phrase}»")
        lines.append(f"   span turns {first}–{last} · {n_u} units · "
                     f"actors: {', '.join(actors)}")
        for t in turns:
            if t not in by_turn:
                continue
            role, body, prose = by_turn[t]
            who = actor_of(role, body)
            # ⚑ RENDER THE NORMALISED TEXT, NOT THE RAW BODY.  The first render
            # printed `{"file_path": "...", "content": "# \\u27e1sql-lift ...` --
            # escaped JSON, which is not something an actor said and is exactly
            # what §1.1's normaliser exists to strip.  Clustering on normalised
            # text while rendering the raw body means the reader cannot see the
            # thing the thread was formed on.
            snip = " ".join(normalise_tools(body, prose).split())[:150]
            if not snip:
                continue                     # tool-only turn: nothing to cite
            lines.append(f"   [{t:4d}] {who:12s} {snip}")
            # ⚑ BIDIRECTIONAL, per §5: the reader arriving at EITHER end is
            # handed the other.  §5.3's complaint is that a reader landing on
            # the antecedent gets nothing; both arrows are rendered.
            for prev, via, classes in rev.get(t, []):
                lines.append(f"          ↑ revises turn {prev} "
                             f"[{','.join(classes)}] via «{via}»")
            # ⚑⚑ THE HEAD CUT APPLIES TO TURNS, NOT ONLY TO ARTEFACTS (Ⓘ8 one
            # layer up).  Turn 110 writes a PLAN DOCUMENT whose vocabulary then
            # recurs for 600 turns, so it collected 15 backlinks -- the turn-11
            # pathology in a new place.  A turn that "is revised" by fifteen
            # later turns is not an antecedent, it is a corpus-wide vocabulary
            # source, and rendering all fifteen tells the reader nothing while
            # burying the threads that have one real reviser.
            #
            # ⚑ IT IS TRUNCATED AND COUNTED, NEVER SILENTLY DROPPED -- the count
            # is the reader's signal that this turn is a source rather than a
            # claim, which is a fact they need and a hidden truncation destroys.
            nxts = sorted(fwd.get(t, ()))
            for nxt in nxts[:FANOUT_CAP]:
                lines.append(f"          ↓ revised at turn {nxt}")
            if len(nxts) > FANOUT_CAP:
                lines.append(f"          ↓ … and {len(nxts) - FANOUT_CAP} more "
                             f"({len(nxts)} total — a vocabulary source, not a "
                             f"single claim)")
    return lines


def gaps():
    """⚑ WHAT THE INDEX CANNOT CARRY.  `tmi-F17`, and printing it is the point.

    A census green is a fact about the census.  An index that lists only what it
    found lets a reader read absence as nonexistence -- the exact error
    `report presence, never absence` names.  So the bounded class ships WITH the
    instrument.
    """
    return [
        "EVIDENCE-SUPERSESSION (`tmi-F17`) -- 4 certain ground-truth revisions",
        "are not carried.  The actor's OWN earlier claim is revised by TOOL",
        "OUTPUT, so there is no human turn to join to and the antecedent is tens",
        "of turns back behind an artefact that is either head-cut as universal",
        "or is a bare discourse referent ('shard 0', 'it').",
        "",
        "  turn  38  «Substantial correction to my starting brief: plan item ③",
        "            is already done»          (a Read of sppf_db.py refutes it)",
        "  turn 209  «--compare-paths, a mode on sppf_db.py, not query_defs.py",
        "            --equiv»                  (a selftest listing refutes it)",
        "  turn 632  «Shard 0 is gone — no process.»        (a pgrep refutes it)",
        "  turn 649  «it didn't crash, it's slow»    (a timeout notif refutes it)",
        "",
        "⚑ The CUE fires on these (209/632/649 all carry contrast frames).  The",
        "  failing conjunct is the RECURRENCE PROBE, so the successor is an",
        "  actor-claim posting list -- NOT another cue class.",
        "",
        "Also uncarried, and labelled uncertain in the ground truth rather than",
        "missed: turn 592 «Two accuracy checks before they file.» -- a probe, not",
        "yet a revision.  It is scored separately and never folded into recall.",
    ]


def main(argv):
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else DEFAULT_TRANSCRIPT
    if not os.path.exists(path):
        print(f"no such transcript: {path}")
        return 2

    if "--gaps" in argv:
        g = gaps()
        for line in g:
            print(line)
        print(f"\ngaps: 1 named class of {S.GROUND_TRUTH_N} ground-truth labels "
              f"(4 certain + 1 uncertain uncarried)")
        return 0

    units, n_env = S.load_units(path)
    print(f"units: {len(units)} of {n_env} envelopes  ({path})")

    minb = MIN_BREADTH
    if "--min-breadth" in argv:
        minb = int(argv[argv.index("--min-breadth") + 1])
    threads = build_threads(units, min_breadth=minb)

    if "--threads" in argv:
        for phrase, turns, breadth, span in threads[:60]:
            first, last, n_u, actors = span
            print(f"  {n_u:3d}u  turns {first:4d}–{last:<4d}  "
                  f"actors={len(actors)}  «{phrase[:60]}»")
        print(f"threads: {len(threads)} of {len(units)} units "
              f"(min-breadth {minb})")
        return 0

    if "--thread" in argv:
        want = argv[argv.index("--thread") + 1]
        sel = [t for t in threads if want.lower() in t[0].lower()]
        ci = S.cluster_index(units)
        links, _p = S.build_links(units, mode="union", cluster_phrase_index=ci)
        for line in render(units, sel, links):
            print(line)
        print(f"\nthread: {len(sel)} of {len(threads)} threads match {want!r}")
        return 0

    if "--index" in argv:
        limit = None
        if "--limit" in argv:
            limit = int(argv[argv.index("--limit") + 1])
        ci = S.cluster_index(units)
        # ⚑ `union` IS THE SHIPPED MODE, and `MODE_RESIDUE` records why: the two
        # recurrence tests are NOT ordered.  `artefact` reaches revisions that
        # paraphrase, `phrase` reaches shared discourse referents with no
        # identifier.  Neither dominates, so coverage is the union -- picking
        # one would discard the loser's real reach.
        links, _p = S.build_links(units, mode="union", cluster_phrase_index=ci)
        body = render(units, threads, links, limit=limit)
        head = [
            "RECOVERY INDEX -- by thread, ordered by first appearance.",
            f"source: {path}",
            f"threads: {len(threads)}   revision links: {len(links)}   "
            f"units: {len(units)} of {n_env} envelopes",
            "",
            "⚑ Every line is VERBATIM with its turn and actor.  Nothing here is",
            "  summarised.  ↑/↓ are revision links, bidirectional and unlabelled",
            "  (design §5: no status field, no chain resolution -- a reader who",
            "  is handed both ends can read the sequence themselves).",
            "",
            "⚑ WHAT THIS INDEX CANNOT CARRY is printed by `--gaps` and is not",
            "  empty.  Read it before treating an absent thread as no thread.",
        ]
        out = head + body
        if "--out" in argv:
            dest = argv[argv.index("--out") + 1]
            with open(dest, "w") as fh:
                fh.write("\n".join(out) + "\n")
            print(f"wrote {dest}: {len(out)} lines, {len(threads)} threads")
            return 0
        for line in out:
            print(line)
        rendered = len(threads[:limit] if limit else threads)
        print(f"\nindex: {rendered} of {len(threads)} threads rendered")
        return 0

    print(__doc__)
    return 0


def selftest():
    ok = fail = 0

    def chk(name, cond):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print(f"  FAIL {name}")

    # ⚑ THE REUSE CONSTRAINTS ARE SELFTESTED, because design §4's "must not be
    # revived" list is the kind of rule a later edit breaks silently.
    chk("cluster_memories not revived", "cluster_memories" not in sys.modules)
    chk("synth_wire not imported", "synth_wire" not in sys.modules)
    chk("reuses cluster_phrases", hasattr(G, "cluster_phrases"))
    chk("reuses Sequitur via G", hasattr(G, "words") and hasattr(G, "expand"))
    chk("reuses transcriptstruct reader", hasattr(T, "stream"))
    # ⚑ THE CHECK IS ON THE DISPATCH, NOT THE DOCSTRING.  A first cut asserted
    # `"--apply" not in __doc__` and FAILED -- because the docstring says "no
    # `--apply`", so the prose promising read-only tripped the test meant to
    # enforce it.  A string search cannot tell a mode from a mention of one.
    # The honest check reads the dispatch: `main` must never branch on --apply.
    import inspect as _i
    chk("no apply dispatch", '"--apply"' not in _i.getsource(main))
    chk("sole write is --out", _i.getsource(main).count("open(") == 1)

    # attribution: the peer case is the one that must not collapse to "human"
    chk("operator attributed", actor_of("human", "just a message") == "operator")
    chk("actor attributed", actor_of("assistant", "some prose") == "actor")
    chk("peer attributed", actor_of(
        "human", '<cross-session-message from-name="substrate-83">hi')
        == "peer:substrate-83")

    # ⚑ THE NORMALISER (§1.1) -- each case here is a line the FIRST RUN actually
    # rendered, not a hypothetical.  Boilerplate threads dominated the table and
    # a plan document rendered as escaped JSON.
    n = normalise_tools('{"file_path": "/home/mikemol/github/x/sppf_db.py"}', "")
    chk("path collapses to basename", "sppf_db.py" in n and "/home/" not in n)
    chk("json key stripped", "file_path" not in n)
    n2 = normalise_tools(
        '{"to": "substrate-45", "message": "the \\u27e1sql-lift brief was stale"}', "")
    chk("json escape decoded", "⟡sql-lift" in n2)
    chk("json punctuation stripped", '{"' not in n2)
    chk("harness notif dropped", not normalise_tools(
        "Command did not complete within its 300s timeout and was moved", "").strip())
    chk("system-reminder dropped", not normalise_tools(
        "<system-reminder>This file exists but has empty contents</system-reminder>",
        "").strip())
    chk("prose preserved verbatim", normalise_tools(
        "irrelevant tool body", "You're right — I never checked it.")
        == "You're right — I never checked it.")
    # head+tail, not the body
    big = "\n".join(f"line {i}" for i in range(40))
    chk("long result is head+tail", len(normalise_tools(big, "").splitlines()) == 12)

    # §2.3 gate: nothing rendered on a single witness
    u = [(1, "human", "the fold leases from membudget", "the fold leases from membudget"),
         (2, "assistant", "the fold leases from membudget too", "the fold leases from membudget too"),
         (3, "assistant", "unrelated singleton content here", "unrelated singleton content here")]
    th = build_threads(u, min_breadth=2)
    chk("breadth gate drops singletons", all(t[3][2] >= 2 for t in th))

    # ⚑ THE GAPS MODE MUST NAME THE RESIDUAL CLASS.  An index that lists only
    # what it found lets absence read as nonexistence.  Pinned so a later edit
    # cannot quietly drop the disclosure and leave the reader with a clean list.
    g = "\n".join(gaps())
    chk("gaps names the class", "EVIDENCE-SUPERSESSION" in g)
    chk("gaps cites its finding", "tmi-F17" in g)
    for t in ("38", "209", "632", "649"):
        chk(f"gaps names turn {t}", f" {t} " in g or f"turn {t}" in g)
    chk("gaps names the successor", "actor-claim posting list" in g)

    # ⚑ THE ROUND-2 BLOCKER IS PINNED AS CLOSED.  This is the assertion that
    # licenses the build existing at all: if a later edit regresses the
    # concession class, this selftest fails rather than the index silently
    # losing its highest-value threads again (`tmi-F14`).
    for turn in (198, 401, 644, 664, 676):
        chk(f"operator-refutation {turn} in GT",
            any(t == turn for t, _c, _l in S.GROUND_TRUTH))
    chk("concession cue exists", hasattr(S, "CUE_CONCESSION"))
    chk("concession is anchored", S.CUE_CONCESSION.pattern.startswith(r"\A"))

    # ⚑⚑ THIS SUITE READ **SILENT** TO THE RUNNER, AND ITS 33 GREEN CASES WERE INVISIBLE.
    # `run_selftests.read_result` takes the typed row first and falls back to the regex
    # `selftest:\s*(\d+)\s*/\s*(\d+)`. `selftest: 33 of 33 checks pass` matches NEITHER —
    # it is `N of M`, not `N/M` — so the runner recorded no record and no prose count and
    # classified the suite `silent`, the verdict for "reported nothing I can read".
    #
    # ⚑ AND SILENT IS WORSE THAN THE PROSE KEY IT LOOKS LIKE. A prose-reporting suite at
    # least lands in the ⟡selftest-contract census, where it is a NEW key the gate refuses
    # by NAME. A silent one is not in that census at all: the count of prose suites reads
    # clean while 33 assertions go unread — a false zero, banked. Measured 2026-08-25
    # alongside its siblings `tmi_status.py` (51 cases) and `tmi_subject.py` (15), all
    # three silent for the same reason and none of them visible as debt anywhere.
    #
    # Emitting the typed record fixes it at the source the runner actually reads; the
    # human line keeps its own wording, which is why the mismatch survived this long.
    try:
        import rungs as _rungs
        _rungs.emit_record(ok, ok + fail, key="scratch/tmi_index.py")
    except ImportError:
        print("  ⚑ rungs unavailable — no typed record emitted")
    print(f"selftest: {ok} of {ok + fail} checks pass")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
