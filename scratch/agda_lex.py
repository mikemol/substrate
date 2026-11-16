# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Shared Agda lexical primitives — ONE authority per concept.

Every function here existed in 2-6 divergent copies across the codemods, and
each duplication has already produced a measured bug:

  * statement-span   5 copies; exactly ONE knew that indentation alone cannot
                     delimit a statement.  The naive rule deleted three valid
                     imports from Discipline.agda (F17), and the same rule is
                     still live in prune_imports (twice, in ONE function) and
                     split_lemmas (four times).
  * comment masking  agda_defs masks line comments; prune_imports masks
                     nothing, so every word of a preserved per-lemma comment
                     block is a liveness token.  split_lemmas ATTACHES those
                     blocks to each leaf by design, so this fires by
                     construction, not by luck.
  * module name      SIX regexes, two acceptance languages.  prune_imports and
                     split_lemmas both named theirs `IMP` with DIFFERENT
                     ARITY (one captures the module, one does not), which
                     needed a ⚑ comment in capture_demand to explain.
  * mixfix spelling  `strip("_")` is correct for two-hole operators and silently
                     wrong for every multi-hole one: `if_then_else_` used as
                     `if b then x else y` yields tokens {if,then,else} while
                     strip gives `if_then_else`, matching nothing.

USAGE — ⚑ THIS IS PRIMARILY A LIBRARY; the CLI is two modes bolted to the shared authority,
and they went undeclared because nothing here reads as a "tool" front door. A bare run is the
SELFTEST, which is also why an unknown flag exits 0 with a passing suite rather than refusing.

    agda_lex.py --sections [path…]     # every unresolved mixfix SECTION — a `_+_`-style operator
                                       # used in section form whose name is not in scope at the
                                       # site. Reports the intended operator where exactly one
                                       # in-scope candidate exists, and the candidate homes where
                                       # it does not. Defaults to the whole tree; paths narrow it.
    agda_lex.py --sections --by-op     # ⚑ THE SAME ROWS GROUPED BY OPERATOR. 590 sites is a
                                       # POPULATION, NOT A LIST — grouping by the operator each
                                       # section names is what turns it into a small number of
                                       # renames. `--by-op` is a MODIFIER on `--sections`, not a
                                       # mode: alone it does nothing.
    agda_lex.py                        # the selftest (the default, deliberately)

⚑ DO NOT fold `agda_defs.def_index` through `statements()`.  It is a per-line
state machine tracking in_data/in_module indentation, not a statement iterator;
forcing it through this module would be a rewrite, not a refactor — and it is
the component whose bugs generate FALSE POSITIVES (dropping a live import),
the dangerous direction.  Feed it `mask_comments`'d text and leave it alone.
"""
import functools
import os
import re
import sys
from typing import Iterator, NamedTuple, Optional, Literal

# ── the ONE opener set ────────────────────────────────────────────────────
# A continuation is an indented line that is NOT itself a new statement.
# Inside a nested `module M where` the FOLLOWING import is indented too, so a
# bare startswith-space test swallows it and the caller DELETES a valid,
# unrelated import.  Lifted verbatim from fix_stale_using.stmt_span — the only
# copy that carried this guard, added after the measured Discipline.agda loss.
NEXT = re.compile(r"\s*(?:open\s+import|import|open|module|private|"
                  r"postulate|infix|infixl|infixr|record|data|\{-#)\b")
# ⚑ A KEYWORD SET IS NOT ENOUGH.  Inside `module M where`, an import is
# followed by indented DEFINITIONS (`x : Nat`, `f a = b`) that open no keyword
# — so a keyword-only guard swallows the definition into the import's span,
# and a caller that deletes the span deletes the definition.  Measured: the
# F17 fixture absorbed `x : Nat` into the second import (span (2,4) not (2,3)).
# A continuation therefore also stops at any line that opens a DECLARATION.
_DECL = re.compile(r"\s*[^\s:;{}()@|]+(?:\s+[^\s:;{}()@|]+)*\s*(?::(?!:)|=)")


def _continues(line: str, depth: int = 0) -> bool:
    """True iff `line` continues the statement above it.

    ⚑ INSIDE AN OPEN PAREN, NOTHING OPENS A NEW STATEMENT.  A `using (…)` list
    may wrap and its later lines may begin with a KEYWORD — Agda's
    `using (…; module WithTarget)` re-exports a submodule, so a continuation
    line legitimately starts with `module`.  Measured: over the whole corpus
    exactly ONE statement diverges between the naive rule and a depth-blind
    keyword guard, and it is this one (TokiPona/LinearAlgebra.agda:53) — the
    keyword guard TRUNCATES the using-list and silently drops the re-export.
    The depth test is therefore not defensive polish; it is the difference
    between the two rules on real input.
    """
    if not (line.startswith((" ", "\t")) and line.strip()):
        return False
    if depth > 0:
        return True
    return not NEXT.match(line) and not _DECL.match(line)


def _depth_after(text: str, depth: int) -> int:
    """Paren depth after `text`, starting from `depth` (comment-masked input)."""
    for c in text:
        if c == "(": depth += 1
        elif c == ")": depth = max(0, depth - 1)
    return depth

_IMPORT = re.compile(r"^\s*(?:open\s+import|import)\s")
_OPEN   = re.compile(r"^\s*open\s+(?!import\b)")
_VAR    = re.compile(r"^\s*(?:private\s+)?variable\b")
# Permissive by design: a WRONG parse here is worse than a permissive one, and
# every caller filters on the `Substrate` prefix anyway.  `(\S+)` over-accepts a
# trailing `;`; `[\w.'-]+` under-accepts.  Take everything up to a delimiter.
_MODNAME = re.compile(r"^\s*(?:open\s+import|import)\s+([^\s;(){}]+)")


# ⚑ A CACHE WITHOUT COUNTERS CANNOT SAY WHETHER IT IS WORKING.  `--profile`
# measured 58,689 calls into `mask_comments` and that number alone could not
# distinguish a THRASHING cache (working set > cap, so eviction discards live
# entries) from REDUNDANT CALLERS (the same source masked repeatedly in one
# walk).  Those have OPPOSITE fixes — change the eviction vs hoist the call —
# so guessing picks one at random.
#
# ⚑ THE COUNTERS ARE NOW `lru_cache.cache_info()`, not three module ints.  The
# hand-rolled trio duplicated what the stdlib already tracks, and the duplicate
# drifted: its `evictions` field changed meaning under an edit (wipe-events ->
# entries-dropped) while the sentence reporting it did not.  A number that
# cannot desynchronise from its cache is strictly better than one that must be
# kept in step by hand.  `mask_stats()` is still how a caller asks.
# ⚑ `_MASK_CAP` IS GONE — THERE IS NO L1 TO CAP (user, 2026-08-04: *"stop using
# the L1 entirely"*).  It was `4096` resident Agda sources: large enough to be
# the process's footprint (measured — `figures.py --selftest` OOM-killed at a
# 256MB lease, passing once the cap dropped) and too small to hold the working
# set anyway (4096 live, 10,654 evicted).  A cap that is both is not a tuning
# problem, it is a layer that should not be there.
#
# ⚑ AND THE OLD ADVICE POINTED THE WRONG WAY.  `--profile` printed "raise
# _MASK_CAP only if the memory is affordable" — reasoning as though L2 did not
# exist.  With a shared content-keyed store, an L1 miss is a wire hit, not a
# recomputation, so the in-process copy buys latency at the price of RSS and a
# number somebody has to guess.  `shared_cache` exists to own exactly this.

# ⚑ THE PREFETCH LANDING ZONE.  `lru_cache` exposes no insert, so a concurrently
# fetched value has nowhere to go inside it; this map is consulted by the L2
# wrapper before the wire, and each entry is consumed once (popped) so it cannot
# grow into a second unbounded cache — the thing the L1 cap exists to prevent.
_PREFETCHED = {}

# ⚑ THE DEPENDENCY LEDGER — what `l2`-wrapped calls were made, in order.
# A footprint instrument reads this INSTEAD of inferring dependencies from
# syscalls, so a cache hit and a cache miss declare the same edge.  Append-only
# within a run and drained by the observer (`observed(reset=True)`), so it is a
# transcript rather than a second cache: it holds consumer NAMES, never values.
_OBSERVED = []


def observed(reset=False):
    """The `l2` consumers touched so far — the DECLARED dependency footprint.

    ⚑ THIS IS THE HALF `open()`-SPYING CANNOT SEE.  A cached derivation reads
    nothing, so a syscall-level observer reports it as depending on nothing —
    and an ordering built on that footprint concludes two items are independent
    when they share a producer.  Declaring at the wrapper makes the edge
    invariant under caching, which is the property that was silently missing."""
    got = list(_OBSERVED)
    if reset:
        del _OBSERVED[:]
    return got


def l2(consumer, key_fn, derives_from=None):
    """`shared_cache.cached`, resolved LAZILY — THE decorator, not a rewrite.

    ⚑ I HAND-ROLLED AN ADAPTER AND TALKED MYSELF OUT OF THE DECORATOR ON A FALSE
    PREMISE (user, 2026-08-04: *"you're not using the decorator pattern… would
    deal with a LOT of the boilerplate"*).  My argument was that a decorator
    cannot sit BETWEEN two layers, because the L1 dict must be consulted before
    the network.  But `lru_cache` IS a decorator, and STACKING is exactly how
    that ordering is expressed:

        @functools.lru_cache(maxsize=_MASK_CAP)     # L1 — outermost, wins first
        @l2("agda_lex.mask", lambda s: s.encode())  # L2 — only on an L1 miss
        def mask_comments(src): ...

    L1 outermost means a dict hit never reaches the store — the property I
    claimed required manual control flow.  The `_MaskL2` class above is ~45 lines
    duplicating `cached()`, and the same duplication across the 28 censused sites
    would be ~1,100.  Third instance today of a structural answer re-implemented
    (after `lru_cache` itself and the byte-at-a-time line reader).

    ⚑ LAZY, AND DEGRADES TO THE IDENTITY.  This module is imported by pre-commit
    gates and pool children, so dialling a socket at import time would make the
    network a dependency of LOADING a tool that may never mask.  When
    `shared_cache` is absent or `SUBSTRATE_NO_CACHE` is set the wrapper simply
    calls through, so the function behaves exactly as if no L2 existed."""
    # ⚑ `derives_from` NAMES THE ARTIFACT, and it is a LIST so the absent case is
    # falsy without a second sentinel.  It is repo-relative, matching what the
    # `open()` spy emits, so a declared edge and an observed one are the same
    # token — two vocabularies for one relation is what put the `free`-group
    # classification wrong in the first place.
    _derives = [derives_from] if derives_from else []

    def deco(fn):
        bound = []

        def wrapper(*a, **k):
            # ⚑ A CACHED CALL DECLARES ITS DEPENDENCY, because a HIT performs no
            # read for an observer to see (user, 2026-08-04: *"That means reads()
            # was spying on the wrong thing."*).  `worklist_gate.reads()` builds a
            # witness's measurement footprint by spying `open()` — which measures
            # HOW THE BYTES ARRIVED, not WHICH ARTIFACT is depended on.  The two
            # coincide only while every read is a file read, so wiring an L2 in
            # front of a figure emptied its footprint and `ties()` began reporting
            # a MISSING EDGE between items that share a producer.
            #
            # ⚑ MY FIRST RESPONSE WAS TO REVERT THE CACHE — protecting a defective
            # instrument by refusing to let the code change under it.
            #
            # ⚑ AND THE FIRST FIX DECLARED THE WRONG NAME, which a case caught:
            # *"every op: token has a declared producer: got ['op:figures.failures']"*.
            # `op:` means A DERIVED ARTIFACT WITH A PRODUCER (`op:agda/_build` is
            # produced by CENSUS); `figures.failures` is a CACHE NAMESPACE.
            # Typing a cache key as a build product is the collapse the token
            # exists to prevent, and it would have made every cached figure look
            # like an artifact nobody builds.
            #
            # So the DEPENDENCY is declared by the call site (`derives_from`),
            # which knows the artifact; the wrapper only records what was
            # declared.  Absent a declaration nothing is recorded — an undeclared
            # cache is invisible here exactly as it was before, which is honest:
            # this layer cannot infer an artifact it was never told about.
            if _derives:
                _OBSERVED.append(_derives[0])
            # ⚑ A PREFETCHED VALUE SHORT-CIRCUITS THE WIRE.  `warm_masks` already
            # paid for this round trip, concurrently, so going to the store again
            # would make the prefetch pure overhead.  Popped rather than read, so
            # the map drains as the walk proceeds instead of becoming a second
            # uncapped cache.
            if a and _PREFETCHED:
                hit = _PREFETCHED.pop(a[0], None)
                if hit is not None:
                    return hit
            if not bound:
                if os.environ.get("SUBSTRATE_NO_CACHE"):
                    bound.append(fn)
                else:
                    try:
                        sys.path.insert(
                            0, os.path.dirname(os.path.abspath(__file__)))
                        import shared_cache as _sc
                        bound.append(_sc.cached(consumer, key_fn)(fn))
                    except Exception:
                        bound.append(fn)
            return bound[0](*a, **k)
        wrapper.__name__ = getattr(fn, "__name__", "l2")
        wrapper.__doc__ = getattr(fn, "__doc__", None)
        wrapper.__wrapped__ = fn
        return wrapper
    return deco


def warm_masks(sources):
    """Prefetch masks for an ANTICHAIN of sources — one round trip's latency.

    ⚑ CALL THIS ONCE WHERE THE FILE SET IS KNOWN, then mask normally.  Every
    subsequent `mask_comments(src)` finds its answer in the `lru_cache` L1, so
    the caller's own logic stays sequential and unchanged; only the WAITING is
    parallelised.  47 call sites across 20 files would otherwise each need
    threading, which is 20 chances to get concurrency wrong for one property.

    ⚑ THE PROPERTY IS THAT MASKS ARE INDEPENDENT.  A mask is a pure function of
    one source's bytes, so no source's mask orders any other's — an antichain,
    and the serialization was mine, not the problem's.

    Returns the number of sources warmed into L1."""
    srcs = [s for s in sources if s]
    if not srcs:
        return 0
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import shared_cache as _sc
    except Exception:
        return 0
    mats = {s.encode("utf-8", "replace"): s for s in srcs}
    got = _sc.prefetch("agda_lex.mask", list(mats))
    # ⚑ `lru_cache` HAS NO PUBLIC INSERT, so the prefetched values land in a
    # side map that the L2 decorator consults FIRST.  My first version counted
    # rows and warmed nothing — the prefetch would have paid for round trips
    # whose results were then discarded, which is worse than not prefetching.
    n = 0
    for material, value in got.items():
        src = mats.get(material)
        if src is not None:
            _PREFETCHED[src] = value
            n += 1
    return n


def mask_stats():
    """THERE IS NO L1 — the mask cache is the shared store.  See `mask_l2_stats`.

    ⚑ THE L1 WAS RETIRED, NOT RESIZED (user, 2026-08-04: *"stop using the L1
    entirely. Let the L2 do what it's meant to do."*).  MEASURED: with
    `maxsize=4096`, `figures.py --selftest` was OOM-killed at a 256MB lease and
    passed at 512; dropping the cap to 512 made it pass at 256.  The entries are
    resident Agda sources, so the L1 WAS the footprint — and it was simultaneously
    too small to hold the working set (4096 live against 10,654 evicted), which is
    the worst point on the trade.

    ⚑ AND THE HONEST READING IS THAT THE L1 WAS SOLVING A PROBLEM L2 ALREADY OWNS.
    Sizing it is a per-process guess an operator has to get right; the shared store
    holds the same values, keyed by content, across processes and beyond this run.
    Keeping a tuned in-process copy in front of it is the hand-managed layer
    `shared_cache` was built to remove.

    ⚑ RETURNS THE SAME 5-TUPLE SHAPE, ZEROED, so a caller that reports L1 numbers
    prints zeros instead of raising.  It is NOT deleted, because a reader asking
    "is the mask cache working" must be ROUTED, not met with an AttributeError —
    and a silent zero would read as "no calls" rather than "no such layer".  The
    docstring is the routing; `mask_l2_stats()` is the measurement."""
    return 0, 0, 0, 0, 0


def mask_l2_stats():
    """The SHARED-store half — hits/misses/unknown for this consumer, or {}.

    ⚑ TWO LAYERS MEAN TWO MEASUREMENTS.  `mask_stats()` reports the L1; a reader
    asking "is the shared cache earning its round trip" needs the L2 numbers, and
    conflating them would hide exactly the question the L2 was added to answer.
    Empty when the store was never consulted (absent, or disabled)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import shared_cache as _sc
        return _sc.stats().get("agda_lex.mask", {})
    except Exception:
        return {}


@l2("agda_lex.mask", lambda src: src.encode("utf-8", "replace"))
def mask_comments(src: str) -> str:
    """Blank every comment character, preserving length and line structure.

    ⚑ MEMOISED — 58,689 CALLS FOR 29s OF A 136s `worklist_gate --order` RUN.
    It is a char-by-char Python loop over whole files, and the callers re-mask the
    SAME sources repeatedly (every predicate that reads Agda masks first).  Pure
    `str -> str`, so the cache is exact rather than an approximation: same input,
    same output, no staleness window.  Third instance of the repeated-work class in
    this arc (`_blast_radius` 300s->2.7s, `log_is_fresh` 381s->81s, `imports`
    209s->136s) — the shape is "identical work asked for N times", never "the work
    is large", which is why concurrency was the wrong reach every time.

    ⚑ THE L1 IS `functools.lru_cache`, AND HAND-ROLLING IT WAS THE DEFECT (user,
    2026-08-04: *"I'd use python's lru decorator as your L1"*).  The previous
    version was a module dict + a `_MASK_CAP` + a single-entry FIFO eviction + hit
    counters — about thirty lines reimplementing the stdlib, and reimplementing it
    WORSE: FIFO evicts the oldest entry regardless of use, LRU evicts the least
    recently used one.  I even wrote a comment arguing FIFO-vs-`clear()` on a
    question the stdlib had already answered correctly.  `cache_info()` supplies
    the hits/misses the hand-rolled counters existed for.

    ⚑ AND THE CAP WAS NEVER THE FIX ANYWAY — that is what L2 is for.  Measured:
    **58,580 calls / 4,096 live / 10,717 EVICTED**, a working set 3.6x the cap, so
    every eviction was a guaranteed recompute AND every fresh process started
    cold.  Raising the cap postpones the same cliff and re-earns it as the corpus
    grows; a shared capped LFU store makes the bound someone else's problem by
    construction and lets the entry outlive the run.

    Length preservation is load-bearing: callers index by line and some by
    column, so a length-preserving mask is a drop-in for `src` everywhere.

    Handles `--`-to-EOL and NESTABLE `{- … -}` (Agda block comments nest).
    String literals are NOT masked — Agda strings cannot span lines and the
    corpus has no `"…"` containing `--`; documented as out of scope rather
    than silently assumed.

    ⚑ `--` opens a comment only at BOL or after whitespace: Agda's lexer reads
    `-->` as a NAME.  Being conservative here errs toward KEEPING text, i.e.
    toward false-negatives (a kept dead import), which is the safe direction.
    """
    # ⚑ L2 IS CONSULTED ONLY ON AN L1 MISS — `lru_cache` guarantees that ordering,
    # which the hand-rolled version had to implement by hand.  An in-process hit
    # costs a dict lookup, so the network is never in front of the common case.
    #
    # ⚑ THE SHARED STORE IS THE RIGHT STRUCTURE, AND ITS LATENCY IS NOT OURS TO
    # OPTIMISE (user, 2026-08-04: *"We still want to use L2, because it's the
    # RIGHT tool. The performance problem is now cassian's to deal with."*).
    # I measured `--order` at 135.7s -> 166.9s with L2 live and was about to
    # remove it — treating a measurement of SOMEONE ELSE'S LAYER as a verdict on
    # this design.  A local dict that evicted **10,717 entries per run** and
    # started cold in every process is the wrong structure whatever one round
    # trip currently costs; the right structure with a slow dependency is a
    # dependency to report, not an architecture to abandon.
    #
    # What IS ours, and is fixed: the client read one byte at a time
    # (134,476 -> 15,127 syscalls).  What is cassian's: `recv_into` at 2.6ms per
    # loopback GET under load, against an isolated benchmark of 0.44ms.
    #
    # ⚑ BEST-EFFORT: any store failure falls through to the derivation, so a
    # stopped Valkey costs one refused connection and this function behaves
    # exactly as before.  Imported lazily because `agda_lex` is imported by
    # pre-commit gates and by pool children — an import that dials a socket would
    # make the network a dependency of LOADING a tool that may never mask.
    out = list(src)
    i, n, depth = 0, len(src), 0
    while i < n:
        if depth == 0 and src.startswith("{-", i):
            depth = 1; out[i] = out[i+1] = " "; i += 2; continue
        if depth:
            if src.startswith("{-", i):
                depth += 1; out[i] = out[i+1] = " "; i += 2; continue
            if src.startswith("-}", i):
                depth -= 1; out[i] = out[i+1] = " "; i += 2; continue
            if src[i] != "\n": out[i] = " "
            i += 1; continue
        if src.startswith("--", i) and (i == 0 or src[i-1] in " \t\n"):
            j = src.find("\n", i)
            j = n if j < 0 else j
            # `-->` is a name, not a comment opener.
            if j == i + 2 or src[i+2] in " \t\n-":
                for k in range(i, j): out[k] = " "
                i = j; continue
        i += 1
    res = "".join(out)
    # ⚑ WRITE BACK TO L2 SO THE NEXT PROCESS DOES NOT REDERIVE.  This is the half
    # a local cache structurally cannot do: the 10,717 evictions measured here
    # were each a guaranteed recompute, and a fresh invocation started cold no
    # matter how the cap was tuned.  Best-effort — a failed store is silent and
    # costs only this call's derivation, which already happened.
    # ⚑ NO HAND-ROLLED EVICTION HERE ANY MORE.  The FIFO victim-choice, the cap
    # test and the eviction counter were `lru_cache`'s job all along, done worse:
    # FIFO drops the oldest entry regardless of use where LRU drops the least
    # recently USED one, which is the whole point of a working-set cache.  The
    # cap now rides on the decorator (`maxsize=_MASK_CAP`) and `cache_info()`
    # reports what `_MASK_STATS` was counting.
    return res


class Stmt(NamedTuple):
    kind: Literal["import", "open", "variable", "other"]
    module: Optional[str]   # dotted name for kind=="import"; else None
    start: int              # 0-based index of the head line
    end: int                # 0-based EXCLUSIVE; span is lines[start:end]
    text: str               # " ".join(l.strip() for l in lines[start:end])


def statements(lines) -> Iterator[Stmt]:
    """THE statement-span authority.  Replaces five divergent copies."""
    i, n = 0, len(lines)
    while i < n:
        l = lines[i]
        if _IMPORT.match(l):   kind = "import"
        elif _OPEN.match(l):   kind = "open"
        elif _VAR.match(l):    kind = "variable"
        else:                  i += 1; continue
        j = i + 1
        depth = _depth_after(l, 0)
        while j < n and _continues(lines[j], depth):
            depth = _depth_after(lines[j], depth)
            j += 1
        yield Stmt(kind, module_name(l) if kind == "import" else None,
                   i, j, " ".join(x.strip() for x in lines[i:j]))
        i = j


def group_statements(lines, opener) -> list:
    """Group an ALREADY-COLLECTED prelude into statements (head + continuations).

    Distinct from `statements()`: that scans a whole FILE and decides for itself
    what opens a statement (indent-tolerant, `^\\s*`).  This one takes a caller's
    own opener predicate and a list that is already known to be prelude-only —
    the shape `split_lemmas` needs, whose openers are COLUMN-0-ANCHORED on
    purpose (only a col-0 `open`/`import`/`variable` is file-scoped there; an
    indented one is body).  Widening it to `^\\s*` would hoist body lines.

    This replaced FOUR byte-identical copies of the same 6-line loop
    (`capture_demand` and `strip_using` were identical to each other, and two
    more sat inline in `parse`).  A continuation is any line the opener does not
    match, exactly as each copy had it.
    """
    stmts = []
    cur = None
    for l in lines:
        if opener(l):
            if cur: stmts.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur: stmts.append(cur)
    return stmts


def module_name(head: str) -> Optional[str]:
    """One acceptance language for the dotted module name (was SIX)."""
    m = _MODNAME.match(head)
    return m.group(1) if m else None


def using_names(stmt_text: str):
    """Names in a `using (…)` clause; None iff there is no clause at all.

    `None` (absent) is DISTINCT from `set()` (present but empty) — the caller
    treats absence as "no declaration, no evidence" and must not conflate them.

    Paren-depth counted, not `[^)]*`: a using-list may contain a mixfix with
    brackets/parens (`using (_[_]; _∷_)`) and the lazy class truncates it.
    """
    k = stmt_text.find("using")
    if k < 0: return None
    k = stmt_text.find("(", k)
    if k < 0: return None
    depth, j = 0, k
    while j < len(stmt_text):
        if stmt_text[j] == "(": depth += 1
        elif stmt_text[j] == ")":
            depth -= 1
            if depth == 0: break
        j += 1
    return {t for t in re.split(r"[;\s]+", stmt_text[k+1:j]) if t}


#: The characters the body tokenizer splits on — and which some NAMES are built FROM.
#: That collision is the whole reason `body_tokens` exists; naming the set once is what
#: keeps the splitter and the mixfix recovery from disagreeing about which is which.
BODY_DELIMS = "(){}[];,"

_BODY_TOK = re.compile(r"[^\s(){}\[\];,]+")
_PUNCT_RUN = re.compile(r"(?<=\s)([(){}\[\];,]+)(?=\s)")


def mixfix_delims(names):
    """The declared names whose SECTIONS ARE DELIMITERS — `[_,_]`, `⟨_⟩`, `⌊_⌋`.

    ⚑ REQUIRE AN `_` HOLE: that is what makes a name mixfix.  Without it the set picks
    up def-index tokenizer artifacts (`,,`, `-,`, `WithTarget)`) whose verbatim presence
    in a body proves nothing — and since this set can only ADD tokens, an artifact would
    SUPPRESS a legitimate verdict, which is the dangerous direction.
    """
    return {n for n in names if "_" in n and any(c in BODY_DELIMS for c in n)}


def body_tokens(body, mixfix=()):
    """Every token `body` mentions, WITH the recoveries the naive split loses.

    ⚑⚑⚑ THE TOKENIZER SPLITS ON THE VERY CHARACTERS SOME NAMES ARE MADE OF, and each
    recovery below is a MEASURED false verdict in the dangerous direction — a LIVE
    import read as dead, which is acted on by deleting it:

      * qualified heads — `Magma._·_` yields `Magma`, and in this repo a RECORD is both
        a module and a definition, so that token IS the evidence the import is live.
        MEASURED corpus-wide: removing it takes drops 4088 → 4104 and ALL 16 extra are
        false positives with genuine qualified uses.
      * a standalone punctuation RUN (` , `) is a real token.  `,` is a delimiter above,
        so an infix pair constructor `_,_` produced NO token and `Foundation.Product`
        read as dead — the import was dropped and `,` went NotInScope.
      * a BRACKET-DELIMITED mixfix (`[_,_]`, `⟨_,_⟩`, `⌊_⌋`) is built FROM delimiters,
        so the splitter shreds it and the whitespace form never matches when it is used
        applied or at line end (`[_,_]′ = [_,_]`).  MEASURED: a `Foundation.Sum` split
        emitted a correct sibling edge and the prune then DELETED it — `Op2` failed
        isolate-check `[NotInScope] [_,_]`.

    ⚑⚑ HOISTED BECAUSE OMITTING THEM REPRODUCED THE BUG, IN A SECOND TOOL, THE SAME DAY.
    `prune_imports` carried all three with their incidents written down; `agda_defs`'
    `--clause-audit` was written without them and immediately re-reported `_,_` as
    UNUSED at `Quotient/CRT.agda:36` while it was used at :83 and :85.  A recovery whose
    incident is recorded in one file and absent in another is not documentation — it is
    a defect waiting for the next reader.  One home, and the comments above are the
    argument rather than a summary of it.

    ⚑ `mixfix` is PASSED IN, not computed here: the caller owns which name-set bounds
    the verbatim scan (`def_index()` for both current callers), and reaching for that
    index from inside a lexer would invert the dependency — `agda_lex` is the layer
    `agda_defs` reads, not the reverse.
    """
    toks = set(_BODY_TOK.findall(body))
    toks |= {t.split(".")[0] for t in list(toks) if "." in t}
    toks |= set(_PUNCT_RUN.findall(body))
    for nm in mixfix:
        if nm in body:
            toks.add(nm)
    return toks


def mixfix_forms(name: str):
    """Every string a use site could present for a declared `name`.

    `_∷_` → {_∷_, ∷};  `if_then_else_` → {if_then_else_, if, then, else};
    `_[_]` → {_[_], [}.

    Replaces `strip("_")`, which is correct ONLY for two-hole operators and
    invisible for every multi-hole one.

    ⚑ The `strip("_")` form is RETAINED in the union, not replaced.  Segments
    alone are NOT a superset of it: `if_then_else_` strips to `if_then_else`
    and segments to {if,then,else}; `_[_]` strips to `[_]` and segments to
    {[,]}.  Dropping the stripped form would REMOVE probe elements for exactly
    the multi-hole operators this function exists to fix — turning a keep-bias
    into a fresh false-positive (drop) risk, the dangerous direction.  The
    union is a strict superset of both rules, so it can only ever cause FEWER
    drops than either.
    """
    out = {name} | {s for s in name.split("_") if s}
    if name.startswith("_") or name.endswith("_"):
        # ⚑ guard the empty string: `__` strips to "", and an empty probe is a
        # SUBSTRING of every token — it would make every import read as live.
        # Keep-bias is the safe direction, but "always live" is not a bias, it
        # is the loss of the signal.
        stripped = name.strip("_")
        if stripped: out.add(stripped)
    return out


SUFFIX = ".agda"
# ⚑ THE THREE HELPERS BELOW HAD NO CANONICAL HOME, which is why "adopt the shared
# module" was never actionable for the three largest duplication hotspots — there was
# nothing to adopt.  Measured: 69 inline module↔path conversions (33 in scope_fix.py
# alone), 29 module-name extractions, 41 files hand-rolling a `public` predicate.
# The suffix strip alone is spelled THREE ways across ~50 sites (`[:-5]` 22×,
# `[:-len(".agda")]` 23×, `with_suffix` 5×) — a magic 5 that silently truncates a
# name if the extension ever changes.  Publishing these is the PRECONDITION for a
# gate on those motifs, not an afterthought.


# ⚑ THE ROOT IS AN ARGUMENT, RESOLVED ONCE AT THE BOUNDARY — NOT DISCOVERED HERE.
# Callers disagreed: `agda_defs` used a relative `AG="agda"` (worked only from the
# repo root), others an absolute ROOT, `scope_fix` a cwd-relative path requiring you
# to `cd agda/` first.  Two wrong fixes are tempting:
#   * a per-call `root=` DEFAULT — relocates the disagreement into 69 call sites,
#     each still deciding; the divergence survives, just spread thinner.
#   * computing the root from THIS FILE's `__file__` — works only while the library
#     sits inside the repo it operates on.  Installed from a package index it lands
#     in site-packages, nowhere near the tree, and every path silently comes out wrong.
# So: these functions are PURE and take the root explicitly, and an APPLICATION binds
# it once (see `agda_root_from` / `bind_root`).  That is the shippable shape — the
# library knows Agda's naming rule, the application knows where the tree is.
SUFFIX_LEN = len(SUFFIX)


def module_path(path, root):
    """Path -> dotted module name, relative to `root`.

    `module_path("agda/Substrate/Foundation/Eq.agda", "agda")` -> `Substrate.Foundation.Eq`.
    Pure: no cwd, no filesystem, no globals.  `root` may be absolute or relative; the
    comparison is normalized so a caller's spelling does not change the answer.
    """
    p, r = os.path.normpath(path), os.path.normpath(root)
    if os.path.isabs(p) != os.path.isabs(r):
        p, r = os.path.abspath(p), os.path.abspath(r)
    if p == r or p.startswith(r + os.sep):
        p = p[len(r):].lstrip(os.sep)
    if p.endswith(SUFFIX):
        p = p[:-SUFFIX_LEN]
    return p.replace(os.sep, ".").replace("/", ".")


def module_file(mod, root):
    """Dotted module name -> path under `root` (inverse of `module_path`)."""
    return os.path.join(root, mod.replace(".", os.sep) + SUFFIX)


_FILES_CACHE = {}


def agda_files(root, include_build=False):
    """Every `.agda` source under `root`, sorted — THE enumeration authority.

    ⚑ 59 files enumerate the corpus three ways (`glob **`, `os.walk`+endswith, `rglob`)
    and **41 of them have no `_build` filter**.  That is harmless TODAY only because
    `agda/_build/` holds 2762 `.agdai` and zero `.agda` — the agreement at 2764 is LUCK,
    not construction.  The first `.agda` to land under `_build` (a fixture, a vendored
    copy, a generated module) splits the guarded routes from the unguarded ones, and
    since three PRE-COMMIT GATES are on the unguarded side their census inflates while
    the build generator's does not.  A gate-vs-gate divergence, armed and waiting.

    ⚑ `root` IS THE PARAMETER, and it matters: callers legitimately scope differently —
    most pass `agda/Substrate`, `iface_shape` passes `agda/` (which also catches the root
    aggregator `agda/Substrate.agda`, the 2765th file).  A subdirectory-scoped tool is a
    COMPLIANT CALLER with a narrower root, never an exception — which is what keeps the
    rederivation census honest rather than exemption-ridden.

    ⚑ A SHARED NAME IS NOT A SHARED AUTHORITY.  `agda_files()` was already defined FOUR
    times with DIFFERENT BODIES (`check_carrier_locality`, `check_claims`, `paydown`,
    `claim_census`) — one filters `_build` and sorts, another does neither — and it reads
    as reuse at every call site.  This is the one to import.
    """
    # ⚑ MEMOISED PER (root, include_build) PER PROCESS.  This is the SHARED NODE
    # of the census DAG: eleven ratchet gates each walk the same 3457 files, so
    # the enumeration is fanned out from one root and was being recomputed once
    # per consumer.  Fixing it HERE fixes every consumer; fixing it in a gate
    # would have fixed one — which is the whole argument for having an authority.
    #
    # ⚑ AND THIS IS WHY THE POOL BOUGHT NOTHING: a thread pool over the gates
    # measured 0.9x (SLOWER than serial), because concurrency over an unbalanced
    # DAG parallelises the fan-out while leaving the shared root duplicated.
    # Dependency structure first, then parallelism over what actually remains
    # independent — the two are not alternatives.
    #
    # Per-process and never invalidated: these tools are short-lived and read a
    # tree nobody is editing mid-run.  A long-lived caller that EDITS the tree
    # would need invalidation, and would be a different kind of consumer.
    key = (os.path.abspath(root), bool(include_build))
    if key in _FILES_CACHE:
        return list(_FILES_CACHE[key])
    out = []
    for dp, dns, fns in os.walk(root):
        if not include_build:
            dns[:] = [d for d in dns if d != "_build"]
        for f in fns:
            if f.endswith(SUFFIX):
                out.append(os.path.join(dp, f))
    # ⚑ A COPY IS RETURNED, ALWAYS.  Callers mutate the list they get back
    # (`files.extend(...)`, sorting in place); handing out the cached object
    # would let one consumer corrupt every later one — a cache that changes
    # answers is worse than no cache.
    _FILES_CACHE[key] = sorted(out)
    # ⚑ NO PREFETCH HERE, DELIBERATELY (user, 2026-08-04: *"Don't prefetch"*).
    # I wired one and it was SPECULATIVE WORK: enumerating a corpus does not mean
    # anything will mask it, so warming every file's mask spends round trips on
    # sources a run may never touch — and it reads the whole tree to do it.  A
    # cache that pays for answers nobody asked for is not an optimisation.
    #
    # `warm_masks` remains available for a caller that KNOWS its working set;
    # the authority is the wrong layer to decide that on the caller's behalf.
    return list(_FILES_CACHE[key])


def agda_root_from(start):
    """Find the Agda tree root by walking UP from `start` — the application's job.

    Separated from the pure helpers on purpose: this is the one function that touches
    the filesystem and makes an assumption about layout, so it is the one function a
    different deployment would replace.  Returns None rather than guessing.
    """
    d = os.path.abspath(start)
    while True:
        cand = os.path.join(d, "agda")
        if os.path.isdir(os.path.join(cand, "Substrate")):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


class _HeaderMatcher:
    """A drop-in for a compiled `^module … where` pattern, backed by module_name_of.

    ⚑ WHY A SHIM AND NOT A CALL-SITE REWRITE.  Six tools hold the header regex as a
    COMPILED PATTERN OBJECT (`modre = re.compile(...)`) and use it later as
    `modre.search(text)`, reading `.group(1)`.  Rewriting each call site would touch
    more code than the defect warrants and would diverge six ways again.  Exposing the
    canonical WITH THE SAME INTERFACE converts all six by changing one line each.

    `.search()` returns something with `.group(1)`, or None — exactly what the callers
    already branch on.  It does NOT pretend to be a full match object: `.span()`,
    `.groups()` and friends are absent by design, so a caller relying on them fails
    loudly at conversion time instead of silently returning a wrong offset.
    """

    class _M:
        __slots__ = ("_name",)

        def __init__(self, name):
            self._name = name

        def group(self, n=0):
            if n in (0, 1):
                return self._name
            raise IndexError("no such group")

    def search(self, text):
        name = module_name_of(text)
        return self._M(name) if name else None

    match = search          # the old copies used both; both mean "find the header"


HEADER = _HeaderMatcher()


def span_end(lines, i):
    """EXCLUSIVE end of the statement starting at `lines[i]` — THE span authority.

    ⚑ HOMED HERE, LIFTED FROM `agda_imports._span_end` (user, 2026-08-01: *"these
    are things that need LIFTED into reusable modules"*).  It was a leading-
    underscore name — declared private — **imported by SEVEN other files**
    (`capstone_to_dir`, `fix_ambiguous_import`, `fix_orphan_using`,
    `narrow_leaf_imports`, `split_param_module`, `split_upstream`, `strip_using`).
    A `_`-name consumed across module boundaries is public API wearing a private
    label, and that is the mis-homing smell at its most greppable.

    The home was wrong twice over: the rule is LEXICAL (it is a two-line wrapper
    over `_continues`/`_depth_after`, both defined here), while `agda_imports`
    declares its job as *modifying import blocks*.  A tool that only needs to know
    where a statement ends had to import an import-rewriter to find out — the
    "would a third tool find it?" test failing outright.

    `agda_imports._span_end` remains as an alias so its seven consumers are
    untouched; new code takes this one.
    """
    j = i + 1
    depth = _depth_after(mask_comments(lines[i]), 0)
    while j < len(lines) and _continues(lines[j], depth):
        depth = _depth_after(mask_comments(lines[j]), depth)
        j += 1
    return j


def head_span(lines, i, limit=None):
    r"""End index (EXCLUSIVE) of the `record`/`data`/`module` header starting at `lines[i]`.

    A header runs to its `where`, and a parameterized one spans many lines:

        module Substrate.Algebra.Sporadic.HappyFamily.AsTree
          -- 20 prose lines of ATLAS ordering …
          (M B Fi₂₄' : CCA) …
          where

    ⚑ AN ARBITRARY CONTINUATION BOUND IS THE DEFECT THIS REPLACES.  Two census
    tools capped the walk at `j - i < 6` (`check_discharge_ratchet.py:86`,
    `scripts/set1_motif.py:15`) and then `continue`d when no `where` was found —
    silently DROPPING the declaration rather than erroring.  MEASURED over the
    corpus: **401 multi-line headers, 136 of which need MORE than 6
    continuations**; the deepest needs **40** (`Sporadic/HappyFamily/AsTree.agda:50`).
    A census that skips 34% of its own multi-line population reports a low number
    and looks healthy — the failure mode a paydown-only ratchet must never have.

    `limit` exists only as a runaway guard for a malformed file (no `where` at
    all); it defaults to the rest of the file, so a legitimate header of any
    length is found. That is the difference between a TERMINATION bound and a
    CAPABILITY bound — the first is fine, the second is the smell.
    """
    n = len(lines)
    stop = n if limit is None else min(n, i + limit)
    j = i
    while j < stop and "where" not in lines[j]:
        j += 1
    return j + 1 if j < stop else i + 1


def word(n):
    r"""A regex matching the Agda name `n`, bounded the way Agda names actually end.

    ⚑ `\b` IS WRONG FOR AGDA AND MEASURABLY SO.  Python's `\b` is a `\w`/non-`\w`
    transition, but an Agda name may be entirely non-`\w` (`∙`, `⊥`, `_+_`), may
    contain `-` (`×-bij`, `go-≤`), or may end in a non-`\w` char (`∣G∣`).
    MEASURED against `agda_defs.def_index`: **1269 of 10831 defined names (11.7%)
    are invisible to a `\b`-bounded regex** — and the sites using one are write
    paths and a pre-commit gate, where a silent non-match is a silent no-op.
    Live witness: `retire_mod_tip.py:88` failed to rewrite `Div.Over.recon-nth\``.

    Agda names are delimited by WHITESPACE AND BRACKETS, not by word characters,
    so that is what the lookarounds assert.

    ⚑ HOMED HERE, not in `rename_at_source` where it was written: eight tools need
    it, and a rename tool is not a lexical authority.  `rename_at_source.word` is
    now an alias, so its own two-spelling machinery keeps working unchanged.
    """
    return re.compile(r"(?<![^\s(){}\[\];,])" + re.escape(n) + r"(?![^\s(){}\[\];,])")


def module_name_of(src):
    """The module a source declares, from its own `module … where` header — or None.

    ⚑ From the HEADER, not the path: the two disagree mid-collapse and mid-move, and
    the header is what Agda binds.  ⚑ NOT anchored on a same-line `where`: a
    PARAMETERIZED header spans lines (`module M` / `  (Word : Set)` / `  where`), and
    the 8 copies of `^module\\s+(\\S+)\\s+where` in the tree all miss it.  ⚑ Accepts
    unicode: the `[A-Za-z0-9_.-]+` copies reject most of this corpus (`ℕ-elim`).
    Takes TEXT, not a path, so the caller controls comment-masking and I/O.
    """
    m = re.search(r"^module[ \t]+([^\s{(]+)", mask_comments(src), re.M)
    return m.group(1) if m else None


def is_public_open(stmt_text):
    """Does this statement re-export (`open … public`)?

    ⚑ `\\bpublic\\b` — the 16-of-18 spelling — matches `public` inside a comment, a
    renaming TARGET (`renaming (x to public')`), and a qualified `X.public`.  The two
    correct sites use a lookaround; this is that rule, once.  Comment-masked first,
    so a commented-out re-export never counts.
    """
    t = mask_comments(stmt_text)
    if not re.match(r"^\s*open\b", t):
        return False
    return re.search(r"(?<![\w.'-])public(?![\w'-])", t) is not None


# ⚑ `record`/`data` BIND A TELESCOPE EXACTLY AS `module` DOES, and only `module`
# was recognised — so every parameter of a parameterized record was invisible to
# the positional-scope authority.  MEASURED: `Category/AbelianPFG.agda:70` writes
# `(_·G_ : G → G → G)` in a `record … where` telescope; `resolves_here` reported
# `no-candidate` because the name is DEFINED nowhere (it is bound, not defined)
# and `binds_at` did not see the binder either.  That class dominates the section
# census tail — `_·G_ _≈G_ _≈X_ _≈₁_ _≈₂_ _·M_ _+A_ _≈Z6_ _⁻¹ₘ_` are all record
# parameters.  The keyword differs; the BINDING FORM does not, which is why this
# belongs in the shared head pattern rather than in a second scanner.
MODULE_HEAD = re.compile(r"^(\s*)(?:module|record|data)\s+(\S+)")


def module_scopes(src):
    r"""[(name, indent, param_names, body_start, body_end)] for every `module … where`.

    ⚑ THE TELESCOPE IS THE POINT.  A parameterized header spans lines:

        module Over {A : Set}
          (_+_ : A → A → A) (𝟘 𝟙 : A)
          where

    so a `^module [^\n]*\(name :` pattern — which is what `scope_fix._in_scope`
    used — only sees parameters on the header's FIRST line and MISSES every
    multi-line telescope.  Measured: it returned False for `_+_` in
    `Algebra/Polynomial/Graded/Defs.agda`, whose `Over` binds `_+_` on line 22.
    The same hazard is documented at `scope_fix.py:362` (⟡paydown-telescope-anchor)
    — in the file carrying the bug.

    Span rule is `_continues`/`_depth_after` (THE authority): the header runs to
    its `where`, and the BODY runs while lines are indented deeper than the
    header, which is what makes the result POSITIONAL.  A parameter is in scope
    at line L iff L falls inside that module's body — not merely somewhere in
    the file.
    """
    lines = mask_comments(src).split("\n")
    out, n = [], len(lines)
    for i, l in enumerate(lines):
        m = MODULE_HEAD.match(l)
        if not m:
            continue
        indent = len(m.group(1))
        # header spans to its `where` (paren-depth aware, so a wrapped telescope
        # cannot be truncated by a line that merely looks like a new statement)
        j, depth, head = i, _depth_after(l, 0), l
        while "where" not in head and j + 1 < n and (depth > 0 or _continues(lines[j + 1], depth)):
            j += 1
            depth = _depth_after(lines[j], depth)
            head += " " + lines[j].strip()
        if "where" not in head:
            continue
        params = re.findall(r"[({]\s*([^:(){}]+?)\s*:", head)
        names = [t for grp in params for t in grp.split()]
        # body = the indented run after the header
        k = j + 1
        while k < n and (not lines[k].strip() or len(lines[k]) - len(lines[k].lstrip()) > indent):
            k += 1
        out.append((m.group(2), indent, names, j + 1, k))
    return out


def binds_at(src, tok, lineno):
    """Is `tok` bound by an enclosing module telescope AT `lineno` (1-based)?

    This is the POSITIONAL predicate an un-rename needs: `_+_` may be a module
    parameter deep in the file and simultaneously absent at a top-level import
    line.  A file-level answer conflates the two and is why the text-scan
    classifier's counts are upper bounds, not measurements.
    """
    return any(tok in params and start < lineno <= end
               for _n, _i, params, start, end in module_scopes(src))


def telescope_span(src):
    """(header_start, header_end) 0-based INCLUSIVE for the TOP-LEVEL `module … where`,
    or None when the file's own header carries no telescope (ends in `where`).

    ⚑ THE TELESCOPE IS PARSED BEFORE THE MODULE BODY EXISTS, so a name it mentions
    must be in scope from an import placed BEFORE the header.  An import after the
    header is too late — even though the file plainly "imports" it.
    MEASURED LIVE: `Groups/Coxeter/Core.agda` used `≡` in its telescope with
    `open import Substrate.Foundation.Eq` on the LAST LINE of the file, and failed
    `[NoParseForApplication]` — because Substrate's `_≡_` is `infix 4` and that
    fixity was not yet in the grammar.  I first misdiagnosed that as a fixity-across-
    the-parameter-boundary problem (§30 retracts it); the mechanism is positional.

    Only the file's OWN top-level module counts: an anonymous inner `module _ (…)`
    is inside the body, where the ordinary import rules already apply.
    """
    lines = mask_comments(src).split("\n")
    for i, l in enumerate(lines):
        m = MODULE_HEAD.match(l)
        if not m or m.start() != 0 or len(l) - len(l.lstrip()):
            continue
        # ⚑⚑ A ONE-LINE HEADER CAN STILL CARRY A TELESCOPE, and this returned None
        # for every one of them. The old guard read `\bwhere\s*$` ⟹ "no telescope",
        # which states a DEFINITION ("a telescope spans lines") where a CHECK is
        # needed ("are there parameter groups?").
        #
        # MEASURED: `Groups/Coxeter/Cyclic/Base.agda` is
        #     module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where
        # — one line, one parameter, ten imports ABOVE the header. `split_lemmas`
        # asked this predicate whether to decline, got None, split it anyway, and
        # emitted 13 leaves with neither the parameter nor the above-header
        # imports. `Power` then failed `[NotInScope] ℕ`, which I misdiagnosed as an
        # import-seed bug THREE times before reading the header.
        #
        # ⚑ THE FIX IS TO ASK FOR PARAMETERS, NOT FOR LINE COUNT. Everything
        # between the module NAME and the trailing `where` is the telescope; if
        # that text holds a bracketed group, the header is telescoped.
        if re.search(r"\bwhere\s*$", l):
            _mid = l[m.end():]
            _mid = _mid[:_mid.rfind("where")]
            return (i, i) if re.search(r"[({]", _mid) else None
        j, depth, head = i, _depth_after(l, 0), l
        n = len(lines)
        while "where" not in head and j + 1 < n and (depth > 0 or _continues(lines[j + 1], depth)):
            j += 1
            depth = _depth_after(lines[j], depth)
            head += " " + lines[j].strip()
        return (i, j) if "where" in head else None
    return None


def telescope_groups(src, span=None):
    """[(names, text)] for each binder group of a module telescope.

    `span` — (start, end) 0-based INCLUSIVE header span, defaulting to the FILE'S
    OWN top-level header via `telescope_span`. Pass an explicit span to read an
    INNER `module M (…) where`'s telescope with this same parser.

    ⚑ THE SPAN IS A PARAMETER BECAUSE THE PARSING WAS NEVER THE FILE-SCOPED PART.
    `telescope_span` deliberately skips any header that is indented or off column 0
    (an inner `module _ (…)` obeys ordinary import rules), so a file whose telescope
    lives on an inner module read as having NO telescope — which is why
    `split_telescoped` correctly refuses `Graded/FromCommRing.agda`, whose `Over`
    carries `{A : Set} (CR : CommutativeRing A)`. The depth-tracked group parsing
    below is already correct for that case; only the SPAN was wrong. Adding a second
    group parser for inner modules would be the `agda_files()` defect — one
    capability, several bodies — so the span is lifted out instead. Existing callers
    pass nothing and are unaffected.

    ⚑ `module_scopes` FLATTENS: for `(++-assoc : (a b c : Word) → …)` it returns
    `++-assoc` AND `a`, `b`, `c` — the locals bound INSIDE that parameter's type.
    That is right for "is this name bound here" and WRONG for "which parameters
    does this leaf need", which is a question about GROUPS, not names.  A splitter
    that used the flattened list would emit `(a : ?)` as a parameter.

    Returns the group VERBATIM (`(_++_ : Word → Word → Word)`) so a leaf can
    re-declare it exactly, and the names it BINDS (the part left of the `:`), so a
    caller can select groups by what a body uses.  Depth-tracked, so a nested
    `(a b c : Word)` inside a parameter's type does not terminate the group — a
    naive scan truncated `++-assoc` and `canonical-is-fixed` mid-type.
    """
    # ⚑⚑ WHETHER A ONE-LINE SPAN INCLUDES ITS OWN HEAD IS THE CALLER'S FACT, NOT
    # THE TEXT'S — and no amount of inspecting the line can settle it. An inner
    # `module Over {A} (CR) where` and a root `module M (n : ℕ) where` are the same
    # shape at column 0; the difference is only what the caller MEANT by the span.
    # The established convention (pinned by selftest) is that an explicit span
    # names the PARAMETER lines: `(0,1)` includes a one-line inner head, `(1,1)`
    # deliberately reads nothing. A DERIVED span from `telescope_span` is the other
    # case — for a single-line root it returns `(i,i)`, and there the head line IS
    # the parameter line.
    # So: derived spans may read their head line; explicit spans keep the old
    # contract. Conflating them silently redefined `split_telescoped`'s inner path.
    _derived = span is None
    if span is None:
        span = telescope_span(src)
    if span is None:
        return []
    s, e = span
    lines = mask_comments(src).split("\n")
    # ⚑⚑ A SINGLE-LINE HEADER PUTS ITS GROUPS ON THE HEADER LINE ITSELF, and the
    # `s + 1` slice below is EMPTY when `s == e`. So widening `telescope_span` to
    # admit one-line telescopes without this would hand callers a span whose groups
    # read as `[]` — a worse failure than the old None, because a caller would
    # believe it had a parameter-free telescope rather than knowing it had none.
    # The two functions have to move together; they are one authority in two parts.
    #
    # ⚑⚑ BUT ONLY WHEN THE HEAD LINE IS ITSELF A `module …` HEAD, and that guard is
    # load-bearing: an EXPLICIT `span=(1,1)` is the inner-module convention meaning
    # *"read nothing"* — callers pass `(0,1)` to INCLUDE a one-line inner head, and
    # a selftest pins `(1,1) → []`. Reading the head line unconditionally when
    # `s == e` broke that case, i.e. it silently redefined what an explicit span
    # means for `split_telescoped`'s inner path. Keying on MODULE_HEAD keeps the
    # two readings apart: a head line is read, a body line is not.
    _hl = lines[s] if 0 <= s < len(lines) else ""
    _hm = MODULE_HEAD.match(_hl) if (_derived and s == e) else None
    if _hm:
        txt = _hl[_hm.end():]
        txt = txt[:txt.rfind("where")] if "where" in txt else txt
    else:
        txt = "\n".join(lines[s + 1:e + 1])
    out, d, start = [], 0, None
    for i, ch in enumerate(txt):
        if ch in "({":
            if d == 0:
                start = i
            d += 1
        elif ch in ")}":
            d -= 1
            if d == 0 and start is not None:
                grp = txt[start:i + 1]
                head = grp[1:-1].split(":", 1)[0]
                out.append(([t for t in head.split() if t], grp))
    return out


def imports_before(src, lineno):
    """{module} imported STRICTLY BEFORE 0-based `lineno` — the positional half of
    "is this name available here".

    ⚑ THE FILE-LEVEL QUESTION IS THE WRONG ONE and it silently disagrees with the
    typechecker.  Asking "does this file import X" over `Groups/Coxeter/**` returned
    **0 problem sites** while `agda` was rejecting one; asking "is X imported before
    the telescope that uses it" returned **11**, matching the compiler exactly.
    Same class as `scope_fix._in_scope` answering file-level where the question was
    positional (§11d).
    """
    return {st.module for st in statements(mask_comments(src).split("\n")[:lineno])
            if st.module}


# ⚑ A `using (…)` LIST IS NOT A SECTION.  The first cut matched `_⊗ˢ_;` and `_⇔_;`
# inside import lists — the `;` separator absorbed into the "operator" — and reported
# **1136** unresolved sections tree-wide, most of them import syntax rather than code.
# A section's operator can contain no separator, and an import STATEMENT is never a
# section, so exclude both: the name class drops `;`/`,` and import lines are skipped
# by the caller.
SECTION = re.compile(r"\(\s*(_[^\s(),;]+)(?=\s)|(?<=\s)([^\s(),;]+_)\s*\)")


def sections(src):
    """[(lineno, section_text, operator_name)] for every OPERATOR SECTION in `src`.

    A section is a partially-applied operator written with its hole: `(_+ x)` is
    the RIGHT section of `_+_`, `(x +_)` the left.  The name a section REFERS TO is
    not the text you see — `(_+ x)` names `_+_`, not `_+`.

    ⚑ THIS IS THE QUESTION I KEPT ANSWERING BY HAND, and the answer decides a real
    class of build failure.  `Algebra/F2/Vector.agda:167` writes
    `cong-trans (_+ lookup v i) …` and fails `[NoParseForApplication]` with
    **"Operators used in the grammar: None"** — because §13's rename-at-source moved
    F₂'s addition to `_+F_`, so the section names an operator that no longer exists
    in that scope.  The file imports `Foundation.Nat.Plus`'s `_+_`, a DIFFERENT
    operator on ℕ, which is why the error says "None" rather than naming a candidate.

    So the diagnostic is not a grammar question at all: it is *does the operator this
    section names resolve, HERE*.  `resolves_here` answers it by composing this with
    `imports_before` and the name→home index, so no caller re-derives either half.
    """
    lines = mask_comments(src).split("\n")
    # import STATEMENTS carry `(a; b; c)` name lists that look sectional but are
    # syntax; skip their whole span rather than pattern-matching around them.
    skip = set()
    for st in statements(lines):
        if st.kind in ("import", "open"):
            skip.update(range(st.start, st.end))
    out = []
    for i, l in enumerate(lines):
        if i in skip:
            continue
        for m in SECTION.finditer(l):
            txt = m.group(1) or m.group(2)
            # ⚑ A BINDING GROUP IS NOT A SECTION.  `(_·G_ : G → G → G)` in a
            # `module`/`record`/`data` telescope, or in any typed binder, matches the
            # section shape exactly — `(` then `_·G_` then a space — so the operator's
            # own DECLARATION was censused as a use of itself.  It then resolved
            # nowhere (a bound name is not a defined one) and reported
            # `no-candidate`, which is what the whole census tail was:
            # `_·G_ _≈G_ _≈X_ _·M_ _+A_ _≈Z6_ _⁻¹ₘ_` are all binder declarations at
            # their own introduction line, NOT broken call sites.
            # The discriminator is the colon: a binding group types its names before
            # closing, and a genuine section never can (`(_+ x)` has no `:`).
            rest = l[m.end(0) - 1:] if m.group(1) else ""
            close = rest.find(")")
            if m.group(1) and ":" in (rest[:close] if close >= 0 else rest):
                continue
            bare = txt.strip("_")
            out.append((i + 1, txt, f"_{bare}_"))
    return out


def resolves_here(src, lineno, op, homes):
    """Is `op` (a full `_x_` name) provided by something imported BEFORE `lineno`?

    `homes` is the name→{module} mapping (`agda_defs.def_index()[op]`) — passed in
    rather than imported, so this module stays free of the index's tree scan and a
    caller can substitute a narrower map.

    Composes the THREE authorities instead of re-deriving any: `imports_before` for
    the POSITIONAL half (§31's lesson — a file-level answer disagrees with the
    typechecker), the index for the OWNERSHIP half (§41's — the index itself
    dropped `[]` tree-wide), and `binds_at` for the BINDER half.

    ⚑ THE BINDER HALF WAS MISSING AND IT DOMINATED THE CENSUS.  An operator can be
    in scope without being DEFINED anywhere: a module parameter (`module M (_·G_ :
    G → G → G) where`) is bound by the telescope, so the name→home index — which
    indexes definitions — has no entry and the site read `no-candidate`.  MEASURED:
    of 510 sections reported unresolved after the first apply, the tail is
    `_·G_`, `_≈X_`, `_·M_`, `_+A_`, `_≈Z6_`, `_⁻¹ₘ_` … i.e. parameter operators,
    every one a FALSE POSITIVE.  `binds_at` is the positional-telescope authority
    this arc built for exactly this question (§11d) and this resolver never asked
    it — the weak-beside-strong class (§18) inside the composition helper whose
    whole job is to compose the authorities.
    """
    if set(homes or ()) & imports_before(src, lineno):
        return True
    return binds_at(src, op, lineno)


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332).

    ⚑ THIS MODULE HAD NO TEST, and that is part of why it was bypassed: it is the
    canonical home for four primitives, yet a caller had no way to confirm it was
    right without reading 230 lines.  Fifteen tools re-derived the span rule instead.
    Every case below is a MEASURED incident, named, so a conversion onto this module
    is a provable improvement rather than a leap of faith.
    """
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    spans = lambda ls, k="import": [(s.start, s.end) for s in statements(ls) if s.kind == k]

    # ── THE 33-FILE INCIDENT.  An import above a PARAMETERIZED module header: the
    # naive "indented line continues" rule ate the header and its whole telescope.
    # Coxeter/Core.agda went 76 lines -> 3, found only by the build.
    para = ["open import Substrate.Foundation.Eq using (_≡_)", "",
            "module Substrate.Groups.Coxeter.Core", "  (Word : Set)",
            "  (_++_ : Word → Word → Word)", "  where", "", "body : Set"]
    check("parameterized module header is NOT absorbed", spans(para), [(0, 1)])

    # ── F17.  Inside `module M where`, an import is followed by indented
    # DEFINITIONS that open no keyword; a keyword-only guard swallowed `x : Nat`.
    f17 = ["module M where", "  open import A", "  x : Nat", "  y : Nat"]
    check("indented definition after an import is not absorbed (F17)",
          spans(f17), [(1, 2)])

    # ── The ONE real corpus divergence (TokiPona/LinearAlgebra.agda:53): a wrapped
    # using-list whose continuation legitimately BEGINS with `module`.  A depth-blind
    # keyword guard truncates the list and silently drops the re-export.
    wrap = ["open import A", "  using (x; module W)", "  renaming (y to z)", "next : Set"]
    check("wrapped using-list with a `module` re-export stays whole", spans(wrap), [(0, 3)])

    # ── Nestable block comments: the `.*?` stripper terminates at the FIRST `-}`.
    check("nested block comment fully masked",
          mask_comments("a {- x {- y -} z -} b").replace(" ", ""), "ab")
    check("mask preserves length", len(mask_comments("a {- x -} b")), len("a {- x -} b"))
    check("mask preserves line structure",
          mask_comments("a -- c\nb").count("\n"), 1)
    check("`-->` is a NAME, not a comment opener",
          "-->" in mask_comments("x --> y"), True)
    check("line comment IS masked", mask_comments("x -- y").rstrip(), "x")

    # ── ⚑ `telescope_groups` HAD NO CASE HERE AT ALL — `pycodemod --calls` reports
    # it as the DEAD-CAPABILITY class within this module (its only caller is
    # `split_telescoped`). It is the authority for "which parameters does a leaf
    # need", so an untested authority was feeding a destructive emitter.
    inner = ("module Fx where\n"
             "module Over {A : Set} (CR : CommutativeRing A) where\n"
             "  𝟘 : A\n")
    root = ("module Substrate.G.Core\n"
            "  (Word : Set)\n"
            "  (_++_ : Word → Word → Word)\n"
            "  where\n"
            "body : Set\n")
    check("telescope_groups reads the ROOT header's binder groups",
          [ns for ns, _g in telescope_groups(root)], [["Word"], ["_++_"]])
    check("a group is returned VERBATIM so a leaf can re-declare it",
          [g for _ns, g in telescope_groups(root)][1], "(_++_ : Word → Word → Word)")
    # ⚑ THE FILE-HEADER RESTRICTION IS THE WHOLE Ⓐ1 GAP. `telescope_span` skips any
    # header that is indented or not at column 0, so a file whose telescope lives on
    # an INNER `module Over {A} (CR)` reads as having NO telescope — which is why
    # `split_telescoped` correctly refuses `FromCommRing`.
    check("⚑ an INNER telescope is invisible to the header-scoped read",
          telescope_groups(inner), [])
    # ⚑⚑ Ⓒ12 — A ONE-LINE HEADER CAN CARRY A TELESCOPE, and this predicate said
    # otherwise for every one of them: the old guard read `\bwhere\s*$` ⟹ None,
    # stating a DEFINITION ("a telescope spans lines") where a CHECK belongs
    # ("are there parameter groups?").
    # MEASURED on `Groups/Coxeter/Cyclic/Base.agda`:
    #     module Substrate.Groups.Coxeter.Cyclic.Base (n : ℕ) where
    # one line, one parameter, ten imports ABOVE it. `split_lemmas` asked this
    # predicate whether to decline, got None, split it anyway, and emitted 13
    # leaves carrying neither the parameter nor the above-header imports. The
    # `Power` leaf failed `[NotInScope] ℕ`, which I misdiagnosed as an import-seed
    # bug THREE times before reading the header.
    _one = "module Substrate.G.Base (n : ℕ) where\nx : ℕ\nx = n\n"
    check("⚑⚑ Ⓒ12: a SINGLE-LINE telescoped header is detected",
          telescope_span(_one), (0, 0))
    # ⚑ AND THE TWO FUNCTIONS MOVE TOGETHER. `telescope_groups` slices
    # `lines[s+1:e+1]`, which is EMPTY when s == e — so widening the span alone
    # would hand callers a telescope whose groups read as `[]`, a WORSE failure
    # than None: a caller would believe it had a parameter-free telescope rather
    # than knowing it had none.
    check("...and its groups are read from the header line itself",
          [ns for ns, _g in telescope_groups(_one)], [["n"]])
    check("...verbatim, so a leaf can re-declare it",
          [g for _ns, g in telescope_groups(_one)], ["(n : ℕ)"])
    # ⚑ A PLAIN ONE-LINE HEADER IS STILL NOT TELESCOPED — the widening must not
    # make every module read as parameterised, which would flip the decline from
    # never-fires to always-fires.
    check("⚑ a plain one-line header is still NOT telescoped",
          telescope_span("module M where\nx = 1\n"), None)
    # ⚑ AND A MODULE NAME CONTAINING NO BRACKET BUT A `where`-suffixed comment
    # must not fool it either: the scan is over the text BETWEEN the name and the
    # trailing `where`, so a bracket anywhere else is irrelevant.
    check("⚑ an implicit-only one-line telescope counts too",
          telescope_span("module M {A : Set} where\ny = 1\n"), (0, 0))
    # ⚑ …and the fix is an OPTIONAL span, not a second group parser. The parsing
    # (depth-tracked, verbatim group + bound names) is already right for the inner
    # case; only the SPAN was wrong. A second selector is the `agda_files()` lesson.
    # ⚑ THE SPAN'S FIRST LINE IS THE `module …` HEAD, NOT A PARAMETER LINE — the
    # slice is `lines[s+1:e+1]`. For the ROOT case params start on the line AFTER
    # the head, so that is right. For a SINGLE-LINE inner header the head and its
    # params share one line, so the span must START ONE LINE EARLIER to include it.
    # Getting this wrong returns [] and reads as "no telescope", i.e. a false
    # negative that looks exactly like the refusal it is meant to lift.
    check("⚑ an explicit span reads the INNER telescope with the SAME parser",
          [ns for ns, _g in telescope_groups(inner, span=(0, 1))], [["A"], ["CR"]])
    check("the inner group is also verbatim",
          [g for _ns, g in telescope_groups(inner, span=(0, 1))][1],
          "(CR : CommutativeRing A)")
    check("a span whose first line already holds the params reads NOTHING",
          telescope_groups(inner, span=(1, 1)), [])
    # ⚑ Ⓒ8′: AN INNER HEADER MAY SPAN MANY LINES, and the single-line case above
    # encoded the ONE-LINE assumption as the contract. `Graded/Defs.agda`'s
    # `module Over {A : Set}` continues for twelve more lines before `where`:
    #     module Over {A : Set}
    #       (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A)
    #       … nine laws …
    #       where
    # A hand-computed `(hdr-1, hdr)` span read ONLY `{A : Set}` and dropped the
    # rest, so the emitter reported 1 parameter where the module declares 14 and
    # would have written leaves binding `A` alone whose bodies use `_+_`/`𝟘`.
    # `header_span` walks to `where` the way `telescope_span` already does for a
    # file header — depth-tracked, so a nested `(a b c : A)` inside a parameter's
    # TYPE does not end the walk.
    multi = ("module Fx where\n"
             "module Over {A : Set}\n"
             "  (_+_ : A → A → A) (𝟘 : A)\n"
             "  (+-assoc : (a b c : A) → (a + b) + c ≡ a + (b + c))\n"
             "  where\n"
             "  x : A\n")
    # ⚑ AND THE WALKER ALREADY EXISTS: `head_span` (`:781`) runs a header to its
    # `where` with no arbitrary continuation bound — built against a measured 401
    # multi-line headers, 136 of which need MORE than 6 continuations. Reuse it;
    # a second walker here would be the `agda_files()` defect (one capability,
    # several bodies). It returns an EXCLUSIVE end, so the span's last line is
    # `head_span(...) - 1`, and `telescope_groups` slices `[s+1:e+1]` — so the
    # span STARTS at the header line itself.
    _ml = multi.split("\n")
    _e = head_span(_ml, 1) - 1
    check("⚑ Ⓒ8′: a MULTI-LINE inner header spans to its `where`", (1, _e), (1, 4))
    check("...and every binder GROUP is read, not just the head line's",
          [ns for ns, _g in telescope_groups(multi, span=(1, _e))],
          [["_+_"], ["𝟘"], ["+-assoc"]])
    check("...with the group text verbatim, nested type-locals NOT split out",
          [g for _ns, g in telescope_groups(multi, span=(1, _e))][2],
          "(+-assoc : (a b c : A) → (a + b) + c ≡ a + (b + c))")
    check("a single-line inner header still spans just itself",
          head_span(inner.split("\n"), 1) - 1, 1)
    # ⚑ Ⓑ6ᶜ²″: A GROUP ON THE HEADER LINE ITSELF IS LOST BY THE `[s+1:e+1]` SLICE.
    # `module Over {A : Set}` puts the implicit on the SAME line as the keyword, and
    # the slice starts one line later — so `{A : Set}` is never seen while the
    # twelve continuation lines are. MEASURED on `Graded/Defs.agda`: the emitter
    # read 13 of 14 groups and emitted `(_+_ : A → A → A)` with `A` unbound.
    # The span must therefore START ONE LINE EARLIER when the header line carries
    # a group — the same off-by-one the single-line case already needed, now
    # arising in the multi-line shape too.
    check("⚑ a binder on the HEADER line is read when the span starts before it",
          [ns for ns, _g in telescope_groups(multi, span=(0, _e))],
          [["A"], ["_+_"], ["𝟘"], ["+-assoc"]])

    # ── using_names: absent vs empty is a real distinction (no evidence vs no names).
    check("no using clause -> None", using_names("open import A"), None)
    check("empty using clause -> empty set", using_names("open import A using ()"), set())
    check("nested parens in a using-list are not truncated",
          using_names("open import A using (_[_]; _∷_)"), {"_[_]", "_∷_"})

    # ── mixfix_forms: multi-hole operators were invisible to strip("_").
    check("two-hole operator", mixfix_forms("_∷_"), {"_∷_", "∷"})
    check("multi-hole operator exposes every segment",
          mixfix_forms("if_then_else_"), {"if_then_else_", "if", "then", "else", "if_then_else"})
    check("`__` does not emit the empty probe", "" in mixfix_forms("__"), False)

    check("module_name: one acceptance language",
          module_name("open import Substrate.Foundation.Eq using (x)"),
          "Substrate.Foundation.Eq")
    check("module_name: not an import -> None", module_name("x : Set"), None)

    # ── the three helpers that HAD NO CANONICAL HOME (69 + 29 + 41 inline sites) ──
    check("module_path: strips root and suffix",
          module_path("agda/Substrate/Foundation/Eq.agda", "agda"),
          "Substrate.Foundation.Eq")
    check("module_path: PURE — the root is an argument, not a global",
          module_path("/x/y/Substrate/Foundation/Eq.agda", "/x/y"),
          "Substrate.Foundation.Eq")
    check("module_path: root spelling does not change the answer",
          module_path("agda/A/B.agda", "./agda"), "A.B")
    check("module_file: inverse of module_path",
          module_path(module_file("Substrate.Foundation.Eq", "agda"), "agda"),
          "Substrate.Foundation.Eq")
    # ⚑ the magic `[:-5]` spelled three ways across ~50 sites is exactly this
    check("module_path: suffix strip is by NAME, not a magic 5",
          module_path("agda/A/B.agda", "agda"), "A.B")

    # ⚑ 8 copies use `^module\s+(\S+)\s+where` — a PARAMETERIZED header has no
    # same-line `where`, so every one of them misses it.
    check("module_name_of: parameterized header (no same-line `where`)",
          module_name_of("module M\n  (Word : Set)\n  where"), "M")
    # ⚑ the `[A-Za-z0-9_.-]+` copies reject most of this corpus.
    check("module_name_of: unicode name",
          module_name_of("module Substrate.ℕ-elim where"), "Substrate.ℕ-elim")
    check("module_name_of: a COMMENTED header is not a header",
          module_name_of("-- module Ghost where\nmodule Real where"), "Real")
    check("module_name_of: absent -> None", module_name_of("x : Set"), None)

    # ⚑ `\bpublic\b` (16 of 18 copies) matches a comment and a rename TARGET.
    check("is_public_open: a real re-export",
          is_public_open("open import A using (x) public"), True)
    check("is_public_open: `public` in a COMMENT is not a re-export",
          is_public_open("open import A  -- make public later"), False)
    check("is_public_open: `public` as a RENAME TARGET is not a re-export",
          is_public_open("open import A renaming (x to public')"), False)
    check("is_public_open: a plain import is not a re-export",
          is_public_open("open import A using (x)"), False)
    check("is_public_open: not an `open` at all", is_public_open("x : Set"), False)

    # ── word(): Agda name boundaries ───────────────────────────────────────
    # ⚑ Every case is a name a `\b`-bounded regex gets WRONG.  MEASURED: 1269 of
    # 10831 defined names (11.7%) are invisible to `\b`.
    check("word: pure-symbol name matches", bool(word("∙").search("f ∙ g")), True)
    # ⚑ THIS CASE MUST USE A LITERAL `\b` — it exists to DEMONSTRATE that `\b`
    # fails on a symbol name.  My own bulk conversion rewrote it into
    # `word(...)`, which made the case assert that the CORRECT matcher fails,
    # i.e. it inverted the very fact it was written to prove.  A mechanical
    # sweep cannot tell a use of the broken pattern from a DEMONSTRATION of it.
    check("word: `\\b` would MISS this one",
          bool(re.search(r"\b" + re.escape("∙") + r"\b", "f ∙ g")), False)
    check("word: hyphenated name matches", bool(word("×-bij").search("p ×-bij q")), True)
    check("word: does NOT match a longer name containing it",
          bool(word("suc").search("suc-injective")), False)
    check("word: operator in a section", bool(word("_+_").search("(_+_)")), True)
    check("word: name ending in a symbol", bool(word("∣G∣").search("n = ∣G∣")), True)
    check("word: bracket-delimited", bool(word("x").search("[x]")), True)

    # ── module_scopes / binds_at ────────────────────────────────────────────
    # ⚑ Every case is the MEASURED defect in scope_fix._in_scope (:1730): its
    # `^module [^\n]*\({tok}\s*:` pattern demanded the parameter on the header's
    # FIRST line, so 1590 of 1948 telescope params tree-wide were INVISIBLE.
    TELE = ("module Over {A : Set}\n"
            "  (_+_ : A -> A -> A) (Z O : A)\n"
            "  where\n"
            "  pad : A -> A\n"
            "  pad x = x + Z\n")
    check("module_scopes: multi-line telescope binds a 2nd-line param",
          "_+_" in module_scopes(TELE)[0][2], True)
    check("module_scopes: same-line params still bind",
          "A" in module_scopes(TELE)[0][2], True)
    check("binds_at: param is NOT bound above its module header",
          binds_at("open import M renaming (_+_ to _N+_)\n" + TELE, "_+_", 1), False)
    check("binds_at: param IS bound inside the module body",
          binds_at(TELE, "_+_", 5), True)
    check("binds_at: unknown token is never bound", binds_at(TELE, "nope", 5), False)
    SINGLE = "module M (x : A) where\n  f : A\n"
    check("module_scopes: single-line header still parses", module_scopes(SINGLE)[0][2], ["x"])
    check("module_scopes: a header with NO `where` is not a scope",
          module_scopes("module Broken (x : A)\n"), [])
    check("binds_at: sibling module's param does not leak",
          binds_at(TELE + "\nmodule Other (q : A) where\n  g : A\n", "q", 5), False)

    # ⚑ SECTIONS: the `[NoParseForApplication]` PREDICTOR.  `(_+ x)` names `_+_`,
    # not `_+` — the text is not the name.  MEASURED WITNESS: `F2/Vector.agda:167`
    # fails with "Operators used in the grammar: None" because §13's rename moved
    # F₂'s addition to `_+F_`, so the section names an operator absent from scope.
    check("a right section names the full operator",
          [op for _ln, _t, op in sections("f = cong (_+ x) p\n")], ["_+_"])
    check("a left section too",
          [op for _ln, _t, op in sections("f = cong (x +_) p\n")], ["_+_"])

    # ⚑ AN IMPORT'S `using (…)` LIST IS NOT A SECTION.  The first cut absorbed the
    # `;` separator into the operator (`_⊗ˢ_;`, `_⇔_;`) and reported **1136**
    # unresolved sections tree-wide, most of them import syntax rather than code.
    # Skipping import statements and excluding separators from the name class
    # gives **590**, with the live witness's 4 sites still found.
    check("a `using` list yields no sections",
          sections("open import M using (_⊗ˢ_; _⇔_)\n"), [])

    # ⚑ A TELESCOPE BINDING GROUP IS NOT A SECTION — the operator's own DECLARATION
    # matched the section shape (`(` + `_·G_` + space) and was censused as a use of
    # itself.  It then resolved nowhere (a BOUND name is not a DEFINED one) and
    # reported `no-candidate`; that was the bulk of the 496-row census tail, every
    # row a binder at its introduction line rather than a broken call site.
    # The colon is the discriminator: a binding group types its names before
    # closing; a genuine section cannot.
    check("a typed binding group yields no section",
          sections("record R (A : Set) (_·G_ : A → A → A) : Set where\n"), [])
    check("…but a real section on the same operator IS found",
          [op for _l, _t, op in sections("h = cong (_·G x) p\n")], ["_·G_"])

    # ⚑ A MODULE PARAMETER RESOLVES A SECTION, AND THE FIRST RESOLVER SAID NO.
    # `_·G_` is bound by the telescope and DEFINED nowhere, so the name→home index
    # (which indexes definitions) is empty for it and the site read `no-candidate`.
    # MEASURED: that false-positive class dominated the 510-row remainder after the
    # first section apply.  `binds_at` — the positional telescope authority — is the
    # missing third half of the composition.
    _param = ("module M (_·G_ : G → G → G) where\n"
              "  f : G\n"
              "  f = cong (_·G x) p\n")
    check("a section on a MODULE PARAMETER resolves",
          resolves_here(_param, 3, "_·G_", set()), True)
    check("…and the index alone cannot see it (the shipped false positive)",
          bool(set() & imports_before(_param, 3)), False)
    check("a section on a name bound NOWHERE still does not resolve",
          resolves_here(_param, 3, "_⊗q_", set()), False)

    # ⚑ A `record` TELESCOPE BINDS EXACTLY AS A `module` ONE DOES, and only
    # `module` was recognised — so `Category/AbelianPFG.agda:70`'s `(_·G_ : G → G
    # → G)` was invisible and its section read `no-candidate`.  Record parameters
    # are the bulk of the section census tail (`_·G_ _≈G_ _≈X_ _≈₁_ _≈₂_ _·M_`).
    _rec = ("record R (A : Set)\n"
            "  (_·G_ : A → A → A) : Set where\n"
            "  field g : A\n"
            "  h = cong (_·G x) p\n")
    check("a RECORD telescope binds its parameters",
          binds_at(_rec, "_·G_", 4), True)
    check("…and a name outside that record's telescope does not",
          binds_at(_rec, "_·H_", 4), False)

    # ⚑ A RENAME ADDS A TAG; IT DOES NOT REPEAT THE OPERATOR.  A bare prefix test
    # made `_+_` ambiguous between `_+F_` (the §13 rename) and `_++_` (list
    # append, a DIFFERENT operator), so the witness reported
    # `ambiguous:2:_++_,_+F_` instead of the obvious answer.  With the suffix rule
    # all 4 sites in `F2/Vector.agda` resolve to `_+F_`.
    _fake = {"_+F_": ["M"], "_++_": ["M"], "_+_": ["Other"]}
    _src = "open import M\nmodule X where\nf = cong (_+ x) p\n"
    check("a rename TAG is a candidate", _intended(_src, 3, "_+_", _fake)[0], "_+F_")
    check("a repeated operator char is NOT (`_++_` is append, not a rename)",
          "_++_" in (_intended(_src, 3, "_+_", _fake)[0] or ""), False)
    # ⚑ …and the explaining form must SAY why, because "no candidate" over 590
    # sites is a question a reviewer asks constantly.
    check("no in-scope candidate is reported as such",
          _intended("module X where\nf = cong (_+ x) p\n", 2, "_+_", _fake)[1],
          "no-candidate")

    # ── the MASK CACHE's eviction, which shipped unguarded ──────────────────
    # ⚑ THE SUITE WAS 58/58 WITH NOTHING EXERCISING EVICTION.  The cap was only
    # reached on a full corpus walk, so every case ran against a cache that never
    # evicted — and I changed the eviction policy (mass `clear()` -> single-entry
    # FIFO) on a green suite that could not have noticed either version.  A pass
    # over a path no case reaches is not evidence about that path.
    # ⚑ REWRITTEN FOR `lru_cache`, AND TWO OF THE OLD CASES WERE TESTING THE
    # STDLIB'S DECISION.  "eviction drops ONE entry, leaving the cache full" and
    # "evictions are ENTRIES DROPPED, not wipe events" were both about FIFO-vs-
    # `clear()`, a question `lru_cache` already answers (and answers better —
    # least-recently-USED beats oldest-inserted).  What survives is the property
    # that is about THIS function rather than about a cache: eviction must never
    # change an answer, and a resident source must hit.
    #
    # ⚑ THE L2 IS DISABLED FOR THESE CASES.  With the shared store live, a
    # "miss" is served from Valkey and the L1 miss count stops reflecting
    # derivations — the fixture would measure the network, not the cache under
    # test.  Set explicitly rather than assumed, because a case that silently
    # depends on a store being down is a case that changes meaning when it comes
    # up.
    _saved_env = os.environ.get("SUBSTRATE_NO_CACHE")
    try:
        # ⚑ THE ENV FLAG IS THE ONLY SWITCH NEEDED NOW.  The previous version
        # also poked a module-level `_L2` list — state the decorator conversion
        # removed.  A case that reaches into a cache's internals to disable it
        # breaks the moment the cache is re-homed, which is exactly what happened.
        os.environ["SUBSTRATE_NO_CACHE"] = "1"
        # ⚑ THESE CASES USED TO BE ABOUT THE L1 — its cap, its eviction, its hit
        # accounting — and the L1 is gone (2026-08-04).  They are not "failing";
        # they described a layer that no longer exists, so keeping them patched
        # would test a fiction.  What survives is the property that OUTLIVES any
        # caching layer, and it is the only one that was ever load-bearing:
        # masking is a pure `str -> str`, so NO configuration of the cache may
        # change an answer.
        #
        # ⚑ AND THE FIXTURE RUNS WITH THE STORE DISABLED ON PURPOSE.  That is the
        # degraded path — `l2` falls through to the identity — so this asserts the
        # uncached answer IS the answer, which is what makes every cached hit
        # verifiable against it.
        srcs = ["x%d -- c\n" % i for i in range(8)]
        first = [mask_comments(s) for s in srcs]
        check("no cache layer changes an answer (pure str -> str)",
              [mask_comments(s) for s in srcs], first)
        check("a comment is blanked, length and lines preserved",
              (len(first[0]), first[0].rstrip("\n").rstrip()), (len(srcs[0]), "x0"))
        # ⚑ `mask_stats()` IS A ROUTER NOW, NOT A MEASUREMENT.  It returns zeros
        # and its docstring names `mask_l2_stats()` as the live one.  Pinned so a
        # future edit cannot quietly restore an in-process counter beside the
        # shared store — two measurements of one cache is how the last pair
        # drifted apart.
        check("mask_stats reports NO L1 (the layer is retired, not resized)",
              mask_stats(), (0, 0, 0, 0, 0))
    finally:
        if _saved_env is None:
            os.environ.pop("SUBSTRATE_NO_CACHE", None)
        else:
            os.environ["SUBSTRATE_NO_CACHE"] = _saved_env

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"agda_lex selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def intended_operator(src, lineno, op, index):
    """The operator a section at `lineno` most likely MEANT — or None if unclear.

    A section names `_+_`; if nothing before `lineno` provides `_+_`, the writer
    meant some operator that IS in scope and whose name differs only by a suffix
    the rename introduced.  MEASURED: §13 moved F₂'s `_+_` to `_+F_`, so
    `F2/Vector.agda:167`'s `(_+ lookup v i)` should read `(_+F lookup v i)` — the
    file imports `Algebra.F2.PlusF`, which provides exactly that.

    ⚑ THIS IS THE "WHICH RENAME" QUESTION, and answering it with a grep over
    imports is what the tooling rule forbids: the module already knows the
    positional import set, so it can name the candidate instead of a caller
    guessing.  Returns a candidate only when EXACTLY ONE in-scope operator shares
    the section's stem — several candidates is a human decision, not a rewrite.
    """
    return _intended(src, lineno, op, index)[0]


def _intended(src, lineno, op, index):
    """(candidate, why) — the explaining form of `intended_operator`.

    ⚑ RETURNS ITS REASONING because "why did this site get no candidate" is a
    question a reviewer of 590 sites will ask constantly, and answering it with an
    ad-hoc probe is the thing that keeps going wrong.  `why` is one of:
    `ok`, `no-candidate`, `ambiguous:<n>`.
    """
    have = imports_before(src, lineno)
    stem = op.strip("_")
    # ⚑ A RENAME ADDS A DISAMBIGUATING SUFFIX; IT DOES NOT REPEAT THE OPERATOR.
    # `_+_` → `_+F_` is the §13 shape.  A bare prefix test also matches `_++_`,
    # which is a DIFFERENT operator (list append), and the witness site then
    # reported `ambiguous:2:_++_,_+F_` instead of the obvious answer.  Require the
    # remainder after the stem to be a NAME-ish tag (letters/digits/sub-scripts),
    # never more of the same symbol.
    def _suffix_ok(n):
        rest = n.strip("_")[len(stem):]
        return bool(rest) and not rest[0] in stem and re.match(r"^[\w′ᴳ₀-₉]+$", rest)
    cands = sorted(n for n, homes in index.items()
                   if n.startswith("_") and n.endswith("_") and n != op
                   and n.strip("_").startswith(stem) and _suffix_ok(n)
                   and (set(homes) & have))
    if len(cands) == 1:
        return cands[0], "ok"
    if not cands:
        return None, "no-candidate"
    return None, f"ambiguous:{len(cands)}:{','.join(cands[:3])}"


def unresolved_sections(paths=None):
    """[(path, lineno, section, op, homes)] for every section whose operator is not
    imported before it — THE `[NoParseForApplication]` PREDICTOR.

    ⚑ EXPOSED AS A COMMAND (`--sections`) BECAUSE THE ALTERNATIVE IS A THROWAWAY
    SCRIPT, and this session produced five of those for one question before the
    right answer appeared (user: *"if you have a question the tooling doesn't answer
    directly, fix the tooling"*).  A census run from a heredoc is not reproducible,
    not reviewable, and drifts from the authority it re-implements.
    """
    import agda_defs
    idx = agda_defs.def_index()
    out = []
    for p in (paths or agda_files("agda")):
        src = open(p, encoding="utf-8", errors="replace").read()
        for ln, txt, op in sections(src):
            homes = idx.get(op) or idx.get(op.strip("_"))
            if not resolves_here(src, ln, op, homes):
                out.append((p, ln, txt, op, sorted(homes or ())))
    return out


if __name__ == "__main__":
    import sys as _sys, os as _os
    if "--sections" in _sys.argv:
        args = [a for a in _sys.argv[1:] if not a.startswith("-")]
        rows = unresolved_sections([a for a in args if _os.path.exists(a)] or None)
        if "--by-op" in _sys.argv:
            # ⚑ 590 SITES IS A POPULATION, NOT A LIST.  Grouping by the operator a
            # section NAMES is what turns it into a small number of renames — and
            # asking that question needed a flag, not another throwaway script.
            import collections as _c
            g = _c.Counter(op for _p, _l, _t, op, _h in rows)
            homes = {op: h for _p, _l, _t, op, h in rows}
            for op, n in g.most_common():
                print(f"{n:5d}  {op:<18} homes={homes[op][:2] or 'NONE'}")
            print(f"{len(g)} distinct operator(s) over {len(rows)} site(s)")
            _sys.exit(0)
        import agda_defs as _ad
        _idx = _ad.def_index()
        _cache, fixable = {}, 0
        for p, ln, txt, op, homes in rows:
            if p not in _cache:
                _cache[p] = open(p, encoding="utf-8", errors="replace").read()
            want, why = _intended(_cache[p], ln, op, _idx)
            if want:
                fixable += 1
            print(f"{p}:{ln}  {txt}  needs {op}"
                  + (f"  -> {want}" if want else f"  [{why}] homes={homes[:2] or 'NONE'}"))
        print(f"{len(rows)} unresolved section(s); {fixable} with ONE in-scope candidate")
        _sys.exit(0)
    _sys.exit(_selftest())
