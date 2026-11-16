#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""prose_apex.py — CLUSTER THE TOOLING'S OWN COMMENTARY, the way the memory mesh does.

⚑⚑⚑ THE CORPUS IS 6,830 ⚑ LINES ACROSS 180 FILES AND NOTHING READS IT AS A CORPUS.
`pycodemod --commentary` already extracts it and already reports 45 texts appearing in
more than one place — but by EXACT MATCH, which finds a copied line and cannot find a
RESTATED law.  Measured 2026-08-19: `--literal 'a fact about the METHOD'` returns six
sites in six unrelated files (`commentary_kinds`, `swallows`, `applied_imports`,
`pycodemod`'s banner, `shared_cache.stats`, `_argv_aliases`), each paragraph added AFTER
an instance bit that author.  **Six independent statements of one law is not
documentation; it is six people paying the same toll** — and exact-match dedup is blind
to every one of them, because they are paraphrases.

⚑⚑ AND I FOUND THOSE SIX BY GUESSING A STRING, WHICH IS THE DEFECT THEY DESCRIBE.
`--literal '<phrase I already suspected>'` is a census keyed on a spelling; it can only
return what the asker already knew to ask.  Sequitur clustering does not need the phrase
in advance — it induces the repeated structure from the corpus.  Operator, 2026-08-19:
*"it can provide clustering that is otherwise incredibly difficult/rare to achieve
without a dedicated LLM."*

⚑ THE MACHINERY IS BORROWED, NOT REBUILT.  `~/.claude/.../memory/grammar_phrase_lattice.py`
already induces a Sequitur grammar over a document corpus and clusters by repeated
phrase; `synth_apex.py` reads those clusters as a graded curve over sharing-breadth.
That is the same shape one domain over, so this imports it rather than re-deriving —
reuse-search before new machinery, and a second implementation is how two answers to one
question come to disagree.

⚑ READ-ONLY BY CONSTRUCTION.  It takes no mutating mode at all.  The memory pipeline it
borrows from writes unconditionally on a hook; this must never be mistaken for that.

    prose_apex.py [paths]            # cluster the ⚑ commentary; report shared laws
    prose_apex.py --corpora          # the DECLARED corpora, each extractor RUN — a
                                     # declared corpus yielding nothing is VACUOUS, and
                                     # a roster of names alone cannot tell that from an
                                     # honestly empty tree
    prose_apex.py --corpus <name>    # which prose to read: python | agda | bib | markdown
                                     # ⚑ the roster is `CORPORA`, and this line is the
                                     # hand-written copy that rots — it said three when
                                     # there were four, one edit after the fourth landed.
                                     # `--corpora` is the derived answer; prefer it.
    prose_apex.py [paths] --min N    # phrases carried by >= N distinct FILES (default 3)
    prose_apex.py [paths] --top N    # show at most N clusters (default 25)
    prose_apex.py --selftest
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

#: ⚑⚑⚑ THE ENGINE IS OURS AND THE MEMORY MESH IS THE BORROWER — NOT THE REVERSE.
#: My first cut imported `grammar_phrase_lattice` out of `~/.claude/.../memory`, which
#: would have made a repo tool depend on a memory-mesh checkout.  `--calls Sequitur` says
#: it lives at `scratch/eliza/eliza/sequitur.py` with NINE in-repo consumers, and
#: `grammar_phrase_lattice.py:18-20` reaches BACK here to import it.  Depending on that
#: file would be a loop through someone else's directory to reach our own code.
#:
#: ⚑⚑ AND THOSE SCRIPTS DO WORK AT IMPORT (operator, 2026-08-19: *"they likely need a
#: clean-rooming into a more convergent, repo-idiomatic form"*).  `synth_apex` and
#: `grammar_phrase_lattice` happen to be import-safe today — measured, not assumed — but
#: `synth_wire.py` has no `__name__` guard and OVERWRITES MEMORY.md at import
#: (`:106`).  One import away from a read-only census rewriting the live session index.
#: Depending on that package at all puts this tool one refactor from that hazard.
#:
#: ⚑ SO WHAT IS BORROWED IS THE *ALGORITHM SHAPE*, NOT THE MODULE: Sequitur (ours), plus
#: the ctx/members_of contract restated here against our own corpus.  The tokenizer and
#: stopfilter are reproduced rather than imported, and that IS a duplication — recorded
#: as such, with its reason, instead of hidden behind an import that looks like reuse.
ELIZA = os.path.join(HERE, "eliza")

#: Words carrying no concept.  ⚑ A COPY of `grammar_phrase_lattice.STOP`, deliberately:
#: importing it would re-introduce the `~/.claude` dependency this file exists to avoid.
#: Divergence here is a real risk and the honest mitigation is to say so — a `--stopwords`
#: mode could reconcile the two if they ever need to agree.
STOP = set(
    "the a an of to in is it as be by or and not for on with that this these those we i "
    "so its are was can has had via per no also when then than only into out up down "
    "over under most more less each both new one you your they them their why how apply "
    "still now yet just have thing about make time back name right must own next there "
    "step whole real run case move open order loop kept hold holds itself instead list "
    "add base too always says doesn check green key fix nothing exactly want done here "
    "been being does did will would could".split())


def _engine():
    """The Sequitur grammar inducer — THIS REPO's, at `scratch/eliza/eliza/sequitur.py`.

    ⚑ NEVER A SILENT FALLBACK TO A LOCAL RE-IMPLEMENTATION.  A second Sequitur would
    answer a question about ITSELF while looking like an answer about the corpus, and the
    two would drift — the duplicated-authority defect this repo keeps paying for.  An
    absent engine is REPORTED, never worked around.
    """
    if ELIZA not in sys.path:
        sys.path.insert(0, ELIZA)
    try:
        from eliza.sequitur import NT, Sequitur
        return Sequitur, NT
    except Exception:
        return None


def words(text):
    """Concept tokens: lowercase alphabetic runs, minus `STOP`.

    ⚑ RESTATED FROM `grammar_phrase_lattice.words`, not imported — see `ELIZA` above.
    Kept to the same rule (`[a-z][a-z-]{2,}`, lowercased, stopfiltered) so a phrase found
    here is a phrase that mesh would find; the duplication is stated rather than disguised.
    """
    import re as _re
    return [w for w in _re.findall(r"[a-z][a-z-]{2,}", text.lower()) if w not in STOP]


class Corpus:
    """One body of prose this repo can extract — DECLARED, with a runnable extractor.

    ⚑⚑⚑ THE `Arm`/`Convention` MODEL, THIRD APPLICATION.  `Arm(key, file, find, replace,
    expect, why)` declares the message a mutation must provoke; `Convention(flag, invoker,
    contract, why)` declares the invoker that makes a flag shared.  Here the load-bearing
    field is `extract` — a callable, so a corpus that stops yielding is VACUOUS and
    `--corpora` says so.  A hand-maintained list of "prose we have" would rot the first
    time an extractor moved; a list of runnable extractors cannot.

    ⚑⚑ AND THE ALTERNATIVE WAS A FORK PER CORPUS.  The obvious next step after the Python
    clustering worked was to copy this file for Agda, then again for `.bib` — three
    Sequitur drivers, three tokenizers, three collapse stages, drifting.  That is the
    duplicated-authority defect this repo keeps paying for, and `agda_files()` existing as
    FOUR bodies under one name is the recorded instance.  ONE engine, N declared
    extractors.

    ⚑ `extract` RETURNS [(path, text)], the smallest shape every source can produce.  The
    Python side has a tokenizer-backed classifier (`commentary_kinds`) and the Agda side a
    regex over comment lines — genuinely different fidelity, correctly hidden behind one
    interface rather than averaged into a lossy common reader.
    """

    __slots__ = ("name", "artifact", "extract", "why")

    def __init__(self, name, artifact, extract, why=""):
        self.name = name
        self.artifact = artifact
        #: () -> [(path, text)].  A corpus yielding nothing is VACUOUS, not empty —
        #: `--corpora` reports the distinction rather than printing a confident zero.
        self.extract = extract
        self.why = why


def _python_commentary(paths=None):
    """⚑-marked lines in this repo's own Python, via the tokenizer-backed classifier."""
    from _pycodemod_commentary import commentary_kinds
    from _pycodemod_core import py_files
    sel = list(py_files(*paths)) if paths else None
    out = []
    for kind, sites in commentary_kinds(sel).items():
        if kind == "unparsed":
            continue          # a file that did not tokenize is a METHOD fact, not prose
        for p, _line, text in sites:
            out.append((p, text))
    return out


def _agda_commentary(paths=None):
    """⚑-marked `--` comment lines in the Agda tree, via `agda_defs --prose`.

    ⚑ A DIFFERENT FIDELITY, DELIBERATELY NOT AVERAGED.  The Python arm uses `tokenize`,
    so a `#` inside a string is not a comment; this arm is a line regex, because Agda's
    comment syntax has no equivalent reader here.  Stating the difference beats pretending
    one reader serves both — the census would silently mix two populations otherwise.
    """
    import re as _re
    import subprocess as _sp
    root = os.path.join(ROOT, "agda")
    if not os.path.isdir(root):
        return []
    cmd = [sys.executable, os.path.join(HERE, "agda_defs.py"), "--prose", "⚑"]
    try:
        r = _sp.run(cmd, capture_output=True, text=True, timeout=900, cwd=ROOT)
    except Exception:
        return []
    out, mod = [], None
    for line in r.stdout.splitlines():
        m = _re.match(r"^== (\S+)", line)
        if m:
            mod = m.group(1)
            continue
        m = _re.match(r"^\s+\d+\s+(.*)$", line)
        if m and mod:
            out.append((mod, m.group(1)))
    return out


def _bib_claims(paths=None):
    """`claim` fields from summit's floor, via `bibstruct --field`.

    ⚑⚑ THE FIRST CUT GUESSED `--fields claim` AND THE MODE IS `--field <name> [bib]`.
    It yielded nothing, `--corpora` correctly reported VACUOUS — and vacuous was a fact
    about MY CALL, not about the floor.  `bibstruct`'s own banner closes with *"a bare
    list cannot distinguish 'no matches' from 'no file read'"*; mine was the second.
    Fourth API I have guessed instead of read this session (`commentary_sites`,
    Sequitur's `.append`/`.rules`, directories-as-file-paths, this).

    ⚑ THE FLOOR IS FIVE PER-GENRE BIBS, not one — summit split 242 entries — so every
    `.bib` under the floor is passed rather than a single default.
    """
    import re as _re
    import subprocess as _sp
    floor = os.path.expanduser("~/github/summit/floor")
    if not os.path.isdir(floor):
        return []
    bibs = sorted(os.path.join(floor, f) for f in os.listdir(floor)
                  if f.endswith(".bib"))
    if not bibs:
        return []
    out = []
    for b in bibs:
        try:
            r = _sp.run([sys.executable, os.path.join(HERE, "bibstruct.py"),
                         "--field", "claim", b],
                        capture_output=True, text=True, timeout=300, cwd=ROOT)
        except Exception:
            continue
        # ⚑⚑ THE DOCUMENT IS THE ENTRY, NOT THE FILE — and keying on the file made the
        # corpus 6 documents, so `--min 3` demanded a phrase in HALF THE FLOOR and
        # returned 0.  That zero would have read as "summit states no duplicate asks",
        # which is a fact about MY GRAIN.  A `.bib` entry is an independent claim by an
        # independent author; a `.py` file is one author's whole commentary.  The unit
        # that can SHARE a law differs per corpus, and pretending otherwise silently
        # inverts the breadth threshold this tool is built on.
        for line in r.stdout.splitlines():
            m = _re.match(r"^\s*(\S+)\s+(.*)$", line)
            if m and len(m.group(2)) > 20:
                out.append((f"{os.path.basename(b)}:{m.group(1)}", m.group(2)))
    return out


def _markdown_sections(paths=None):
    """Markdown SECTIONS, via `mdstruct.spans` — the largest prose corpus here.

    ⚑⚑⚑ THE GRAIN IS THE SECTION, NOT THE FILE, AND THAT CHOICE IS THE WHOLE DESIGN.
    A `.py` file's ⚑ commentary is one author's running argument, so the file is the unit
    that can share a law.  A plan or SKILL.md is 3,900 lines across a dozen unrelated
    topics — keying on the file would make "shared" mean "two enormous documents both
    mention it", which is nearly always true and therefore says nothing.  The bib corpus
    already taught this: file-keying gave 6 documents and a confident ZERO.

    ⚑⚑ `spans()` AND NOT A LINE REGEX, for the reason its own docstring records: a `#`
    inside a fenced code block is not a header, and a section ends at the next
    same-or-shallower header, never simply the next one.  This corpus is dense with Agda
    and shell fences; a regex here would silently truncate sections and the clustering
    would run on a corpus nobody could see was wrong.

    ⚑ SECTIONS ARE FLOOR-BOUNDED.  A two-line section carries no phrase worth clustering
    and would dilute the breadth signal with noise labels; below the floor it is dropped
    rather than emitted empty.
    """
    import glob as _glob
    sys.path.insert(0, HERE) if HERE not in sys.path else None
    import mdstruct as _md
    if paths:
        files = []
        for p in paths:
            if os.path.isdir(p):
                files.extend(_glob.glob(os.path.join(p, "**", "*.md"),
                                        recursive=True))
            elif p.endswith(".md"):
                files.append(p)
    else:
        files = [f for f in _glob.glob(os.path.join(ROOT, "**", "*.md"),
                                       recursive=True)
                 if "/node_modules/" not in f and "/_build/" not in f]
    out = []
    for f in sorted(files):
        try:
            secs = _md.spans(f)
            raw = open(f, encoding="utf-8").read().split("\n")
        except Exception:
            # ⚑ A DOCUMENT PANDOC CANNOT PARSE IS SKIPPED, and that is a METHOD fact.
            # Counted nowhere today — the same unaccounted-swallow shape `--swallows`
            # exists to find, which is why it is named here rather than hidden.
            continue
        rel = os.path.relpath(f, ROOT)
        for _lvl, txt, start, end in secs:
            body = "\n".join(raw[start - 1:end - 1])
            if len(body.split()) < 20:
                continue
            out.append((f"{rel}#{txt[:40]}", body))
    return out


#: ⚑ THE DECLARED ROSTER.  Adding a corpus is one record, never a new module.
CORPORA = [
    Corpus("python", ".py", _python_commentary,
           "6,830 ⚑ lines across 180 files; the laws this tooling states about itself"),
    Corpus("agda", ".agda", _agda_commentary,
           "the proof tree states the SAME laws in its own prose — measured: "
           "'a fact about the SPELLING I guessed' appears in Lifecycle.ActorWedgeEq"),
    Corpus("bib", ".bib", _bib_claims,
           "summit's floor: cross-repo claims, where a restated law is a duplicate ASK"),
    Corpus("markdown", ".md", _markdown_sections,
           "1,897 documents — the LARGEST prose corpus here, bigger than the python and "
           "agda commentary combined; plans, worklists, skills and catalogs, where a "
           "law restated in two skills is a rule with two homes"),
]


def build_context(paths=None, source=None):
    """The memory mesh's OWN `ctx` shape, built over commentary instead of files.

    ⚑⚑⚑ THIS IS THE ACTUAL REUSE BOUNDARY, AND MY FIRST CUT MISSED IT (operator,
    2026-08-19: *"lift/reuse the machinery … rather than reimplementing something that
    merely rhymes"*).  I had imported the grammar engine and then hand-rolled the
    membership scan — a `" " + phrase + " " in text` loop that is `synth_apex.members_of`
    reworded.  Rhyming with the authority is how two answers to one question come to
    disagree; the authority's own docstring for `scan` (`check_carrier_locality:178`)
    names this exact hazard.

    ⚑⚑ `synth_apex.build_context()` IS A FILE-GLOB READER — it globs `**/*.md`, strips
    frontmatter, tokenizes, and builds an IDF/SVD gauge.  Only its INPUT is
    memory-specific; everything downstream (`members_of`, the gauge, `build_apex`'s graded
    curve) operates on the `ctx` DICT.  So the lift is to produce that dict from a
    different source and hand it to their functions UNCHANGED.  Keys are theirs, verbatim:
    `names`, `toks`, `text`, `gauge`, `nametok`, `N`.

    ⚑ ONE DOCUMENT PER FILE, NOT PER LINE.  The question is *which files state the same
    law*, so a file is the unit that can share one.  Per-line documents would make every
    cluster a pair and the breadth signal meaningless — the same grain `synth_apex` picks
    when it clusters memories rather than sentences.

    ⚑ THE GAUGE IS BORROWED WHOLE.  `build_context` computes a term→SVD-mode assignment
    used to reject noise phrases; re-deriving it here would be a second numerical model of
    the same corpus.  Rather than copy it, this delegates: the SVD/IDF block is theirs, run
    over our token streams.
    """
    src = source or CORPORA[0]
    by_file = {}
    for p, text in src.extract(paths):
        by_file.setdefault(p, []).append(text)
    names, toks = [], []
    for p in sorted(by_file):
        t = words(" ".join(by_file[p]))
        if t:
            names.append(os.path.relpath(p, ROOT) if os.path.isabs(str(p)) else str(p))
            toks.append(t)
    if not names:
        return None
    import numpy as np
    from collections import Counter
    # ⚑ THE BLOCK BELOW IS `synth_apex.build_context`'s BODY, verbatim in structure, over
    # OUR token streams.  Kept inline (not imported) for one measured reason: their
    # function globs `.md` before it computes anything, so calling it would scan the
    # memory corpus.  The numerical model is theirs; only the corpus differs.
    text = [" " + " ".join(t) + " " for t in toks]
    df = Counter(w for t in toks for w in set(t))
    N = len(names)
    vocab = sorted(w for w, n in df.items()
                   if 3 <= n <= max(4, N // 2) and w not in STOP)
    if not vocab:
        return None
    vix = {w: j for j, w in enumerate(vocab)}
    Mx = np.zeros((N, len(vocab)))
    for i, t in enumerate(toks):
        for w in set(t) & set(vocab):
            Mx[i, vix[w]] = np.log(N / df[w])
    Mx /= (np.linalg.norm(Mx, axis=1, keepdims=True) + 1e-9)
    _u, _s, Vt = np.linalg.svd(Mx, full_matrices=False)
    Vk = Vt[1:4] if Vt.shape[0] > 3 else Vt
    gauge = {w: int(np.argmax(np.abs(Vk[:, vix[w]]))) for w in vocab}
    # a file has no "name tokens" the way a memory slug does; the key must exist because
    # `members_of` reads it, so it is present and empty rather than absent.
    nametok = [" " for _ in names]
    return dict(names=names, toks=toks, text=text, gauge=gauge,
                nametok=nametok, N=N)


def members_of(phrase, ctx):
    """Indices of documents whose token stream contains `phrase`.

    ⚑ THE `synth_apex.members_of` CONTRACT, restated over our ctx.  Theirs also unions a
    NAMESAKE arm (a memory whose FILENAME tokenizes to the phrase); that arm is dropped
    here rather than carried empty, because a source file's path is not a concept claim
    the way a memory slug is — `nametok` exists in the ctx only so the shapes stay
    comparable if the two are ever reconciled.
    """
    p = " " + phrase + " "
    return [i for i in range(ctx["N"]) if p in ctx["text"][i]]


def clusters(ctx, min_files=3):
    """[(phrase, [file labels])] — Sequitur rules carried by >= `min_files` files.

    ⚑⚑ THE GRAMMAR IS INDUCED OVER THE WHOLE CORPUS AT ONCE, separated by a sentinel —
    the shape `synth_apex.build_apex` uses.  Sequitur creates a nonterminal for every
    digram appearing twice, so its rules ARE the repeated phrases, hierarchically nested.
    That is why this finds PARAPHRASES that an exact-line census cannot: the repetition is
    discovered, never supplied by the asker.  ⚑ Which matters because the six "a fact
    about the METHOD" statements were found by GUESSING that string — a census keyed on a
    spelling, returning only what the asker already knew to ask.

    ⚑ `min_files` COUNTS DISTINCT FILES, NOT OCCURRENCES.  A phrase repeated twenty times
    inside one module is that module's idiom; a phrase in three unrelated files is a LAW
    someone restated.  Counting occurrences ranks the former above the latter, inverting
    the question this tool exists to ask.
    """
    eng = _engine()
    if eng is None or ctx is None:
        return []
    Sequitur, NT = eng
    SEP = "∎"
    gram = Sequitur()
    for toks in ctx["toks"]:
        for w in toks:
            gram.observe(w)
        gram.observe(SEP)              # documents must not form phrases across a boundary
    rules = gram.all_rules()
    out, seen = [], set()
    for rid in rules:
        if rid == 0:                   # rule 0 is the whole stream, not a phrase
            continue
        p = [w for w in _expand(rules[rid], rules) if w != SEP]
        if not (3 <= len(p) <= 14):
            continue
        ph = " ".join(p)
        if ph in seen:
            continue
        seen.add(ph)
        members = members_of(ph, ctx)
        if len(members) >= min_files:
            out.append((ph, sorted(ctx["names"][i] for i in members)))
    # widest first, then longest: breadth IS relevance here, as in the memory root
    out.sort(key=lambda kv: (-len(kv[1]), -len(kv[0]), kv[0]))
    return _maximal(out)


def _maximal(rows):
    """Drop a phrase that is a SUBSTRING of a kept one carrying the same files.

    ⚑⚑ SEQUITUR RULES NEST, SO ONE PHRASE ARRIVES AS A LADDER OF PREFIXES.  The first run
    over `scratch`+`scripts` reported `tool rewrites files read`, `… read shape`, and
    `… read shape made files` as three separate 25-file findings — one law, counted three
    times, crowding out the rest of the top-20.  `grammar_phrase_lattice` has a three-stage
    collapse for exactly this and I shipped without it; the maximal-phrase stage is the one
    that matters here.

    ⚑ THE MEMBER-SET GUARD IS WHAT MAKES IT SAFE.  A shorter phrase is dropped only when a
    longer one carries the SAME OR MORE files — if the short form appears somewhere the
    long form does not, it is carrying information and stays.  Dropping on substring alone
    would silently narrow a finding's breadth, which is the number this tool exists to
    report.
    """
    kept = []
    for ph, labs in rows:                       # already longest-first within a breadth
        s = set(labs)
        if any(ph in k_ph and s <= set(k_labs) for k_ph, k_labs in kept):
            continue
        kept.append((ph, labs))
    return kept


def _expand(seq, rules, max_out=24):
    """A rule's terminal expansion — `grammar_phrase_lattice.expand`'s algorithm.

    ⚑ THE CYCLE GUARD IS LOAD-BEARING, NOT DEFENSIVE.  A Sequitur nonterminal can appear
    inside its own expansion; without the `seen` tuple this recurses forever on a real
    grammar.  Carried over verbatim in shape (a stack plus a per-path `seen`) rather than
    re-derived, because "expand a rule" is exactly where an independent implementation
    would quietly differ and produce different phrases from the same corpus.
    """
    out, stack = [], [(s, ()) for s in reversed(seq)]
    while stack and len(out) < max_out:
        s, seen = stack.pop()
        rid = getattr(s, "rule_id", None)
        if rid is not None:
            if rid in seen:
                out.append(f"R{rid}")
            else:
                for sub in reversed(rules.get(rid, [])):
                    stack.append((sub, seen + (rid,)))
        else:
            out.append(s)
    return out


def _selftest():
    cases = []

    def ok(name, got, want):
        cases.append((name, got == want, f"{got!r} != {want!r}"))

    if _engine() is None:
        # ⚑ AN ABSENT ENGINE IS REPORTED, NEVER PASSED.  A selftest that silently skips
        # its subject is the confident-zero shape this whole tool exists to close.
        print("  FAIL no Sequitur engine at " + ELIZA)
        print("prose_apex selftest: 0/1")
        return 1

    ctx = dict(names=["a.py", "b.py", "c.py"],
               toks=[["census", "keyed", "spelling"],
                     ["census", "keyed", "spelling"],
                     ["wholly", "unrelated", "words"]],
               text=[" census keyed spelling ", " census keyed spelling ",
                     " wholly unrelated words "],
               gauge={}, nametok=[" ", " ", " "], N=3)
    ok("members_of finds the carriers", members_of("census keyed", ctx), [0, 1])
    ok("a non-carrier is excluded", 2 in members_of("census keyed", ctx), False)

    # ⚑ THE THRESHOLD IS THE WHOLE DISCRIMINATOR: a phrase in 2 of 3 files is not a law
    # at min_files=3, and must not surface.
    ok("below the file floor yields nothing",
       [ph for ph, _l in clusters(ctx, min_files=3) if "census" in ph], [])
    ok("at the floor it surfaces",
       any("census" in ph for ph, _l in clusters(ctx, min_files=2)), True)

    # ⚑ 20 REPEATS INSIDE ONE FILE IS AN IDIOM, NOT A SHARED LAW — the inversion this
    # tool exists to avoid, pinned so a switch to occurrence-counting fails here.
    solo = dict(names=["a.py", "b.py"],
                toks=[["repeat", "me", "now"] * 20, ["different", "entirely", "here"]],
                text=[" " + " ".join(["repeat", "me", "now"] * 20) + " ",
                      " different entirely here "],
                gauge={}, nametok=[" ", " "], N=2)
    ok("repeats inside ONE file are not a shared law", clusters(solo, min_files=2), [])

    # ⚑ THE ctx CONTRACT, built from the real extractor over this file itself.  A missing
    # key would surface as an empty clustering — indistinguishable from "no shared
    # phrases", which is exactly the confident zero being guarded against.
    built = build_context([os.path.abspath(__file__)])
    ok("build_context supplies every key members_of reads",
       built is None or {"names", "toks", "text", "gauge", "nametok", "N"}
       <= set(built), True)

    # ⚑⚑ EVERY DECLARED CORPUS MUST CARRY A RUNNABLE EXTRACTOR — the `Arm.expect` half.
    # A roster of names alone cannot tell a VACUOUS corpus from an honestly empty tree,
    # and mine shipped vacuous once already: `_bib_claims` guessed `--fields claim` where
    # the mode is `--field <name> [bib]`, yielded nothing, and `--corpora` said VACUOUS —
    # which was a fact about MY CALL, not about summit's floor.
    ok("every corpus declares a callable extractor",
       all(callable(c.extract) for c in CORPORA), True)
    ok("every corpus states why it exists",
       all(c.why for c in CORPORA), True)
    ok("corpus names are unique",
       len({c.name for c in CORPORA}), len(CORPORA))

    # ⚑ THE GRAIN IS PER-CORPUS AND GETTING IT WRONG INVERTS THE THRESHOLD.  Keying bib
    # documents on the FILE made the corpus 6 documents, so `--min 3` demanded a phrase in
    # half the floor and returned 0 — which would have read as "summit states no duplicate
    # asks". Entry-level keying gives 326. A `.bib` entry is an independent author's
    # claim; a `.py` file is one author's whole commentary.
    ok("bib labels are entry-scoped, not file-scoped",
       all(":" in lab for lab, _t in _bib_claims()[:5]) if _bib_claims() else True,
       True)

    bad = [(n, w) for n, good, w in cases if not good]
    for n, w in bad:
        print(f"  FAIL {n}: {w}")
    # ⚑ A PROSE KEY IN THE ⟡selftest-contract CENSUS, PAID DOWN 2026-08-25. This suite
    # reported only through `run_selftests`' fallback regex, and that census's baseline is
    # EMPTY — zero-tolerance, so a prose-only suite is a NEW key the gate REFUSES. Paid by
    # EMITTING the typed row, never by a baseline edit or an exemption: the census may only
    # be paid down, and `run_selftests`' own refusal text says exactly that.
    #
    # ⚑ AND THIS SUITE WAS ONE RENAME FROM SILENT, which is why the regex is not good
    # enough even when it works. The line is prefixed `prose_apex selftest: …`; it parses
    # only because the fallback SEARCHES rather than anchors. Its siblings `tmi_index` and
    # `tmi_status` wrote `N of M` instead of `N/M` and read SILENT — 33 and 51 green cases
    # unread, and not even visible as debt, since the prose census cannot list a suite it
    # failed to parse. The record removes the dependence on the wording entirely.
    #
    # ⚑ THE EARLY-RETURN BRANCH ABOVE (no Sequitur engine) STILL REPORTS `0/1` BY PROSE,
    # deliberately left as-is: it is a REFUSAL path that returns 1, and a typed `0/1` row
    # there would read as an ordinary failing case rather than an absent subject. Making
    # that branch honest means giving it a `reason` and a skip count, which is separate
    # work from this paydown and should not be guessed at here.
    try:
        import rungs as _rungs
        _rungs.emit_record(len(cases) - len(bad), len(cases),
                           key="scratch/prose_apex.py")
    except ImportError:
        print("  ⚑ rungs unavailable — no typed record emitted")
    print(f"prose_apex selftest: {len(cases) - len(bad)}/{len(cases)}")
    return 1 if bad else 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--selftest" in argv:
        raise SystemExit(_selftest())
    mn, top = 3, 25
    for flag, dflt in (("--min", 3), ("--top", 25)):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 >= len(argv) or not argv[i + 1].isdigit():
                print(f"usage: prose_apex.py [paths] {flag} <N>", file=sys.stderr)
                raise SystemExit(2)
            if flag == "--min":
                mn = int(argv[i + 1])
            else:
                top = int(argv[i + 1])
    # ⚑ A BARE RUN PRINTS THE MODES AND EXITS 2 — the house convention, and mine
    # violated it: `prose_apex.py` alone ran a full-corpus clustering (minutes of work,
    # pages of output) where the reader was asking what the tool does.  Caught by
    # `toolmodes --check`, which reported this file as ⚑ NO SELF-DESCRIPTION.  A bare run
    # is a usage question, not a request for the most expensive mode.
    if not argv:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)

    if "--corpora" in argv:
        # ⚑ RUN EACH EXTRACTOR — a DECLARED corpus that yields nothing is VACUOUS, and a
        # roster that only lists names cannot tell that from an honestly empty tree.  Same
        # falsifiability the `Arm`/`Convention` records carry: the field is a callable so
        # the claim can fail.
        for c in CORPORA:
            try:
                got = c.extract(None)
                n = len({p for p, _t in got})
                mark = f"{len(got):>6} line(s) in {n:>4} file(s)" if got else \
                    "     ⚑ VACUOUS — extractor ran, yielded nothing"
                print(f"  {c.name:<8} {c.artifact:<7} {mark}")
            except Exception as e:                # noqa: BLE001
                print(f"  {c.name:<8} {c.artifact:<7}      ⚑ FAILED: "
                      f"{type(e).__name__}: {e}")
            print(f"           {c.why}")
        print(f"{len(CORPORA)} declared corpus/corpora")
        raise SystemExit(0)

    src = CORPORA[0]
    if "--corpus" in argv:
        i = argv.index("--corpus")
        if i + 1 >= len(argv):
            print("usage: prose_apex.py --corpus <name>", file=sys.stderr)
            raise SystemExit(2)
        want = argv[i + 1]
        src = next((c for c in CORPORA if c.name == want), None)
        if src is None:
            # ⚑ NAME THE ROSTER RATHER THAN FAIL BARE — an unknown corpus is a typo far
            # more often than a missing capability, and the fix is one line away.
            print(f"prose_apex: no corpus named {want!r}; declared: "
                  f"{' '.join(c.name for c in CORPORA)}", file=sys.stderr)
            raise SystemExit(2)
    paths = [a for a in argv if not a.startswith("-") and not a.isdigit()
             and a != (src.name if "--corpus" in argv else None)]
    items = build_context(paths or None, source=src)
    if items is None:
        print("prose_apex: no ⚑ commentary found in the given paths", file=sys.stderr)
        print("  ⚑ NOTHING WAS CLUSTERED — a fact about the QUERY (or about a missing\n"
              "    Sequitur engine at " + ELIZA + "), never a claim that the\n"
              "    corpus states no shared laws.", file=sys.stderr)
        raise SystemExit(2)
    cl = clusters(items, mn)
    for ph, labs in cl[:top]:
        print(f"{len(labs):>3}×  {ph}")
        for lab in labs[:6]:
            print(f"       {lab}")
        if len(labs) > 6:
            print(f"       … and {len(labs) - 6} more")
    print(f"{len(cl)} shared phrase(s) across {items['N']} file(s) "
          f"(>= {mn} files each)")
    # ⚑ THE CLUSTERS ARE A READING, NOT A VERDICT.  A repeated phrase may be a law
    # restated (paydown work), a convention correctly stated once per tool (leave it), or
    # a copied block (a `--commentary` exact-match finding). Only the first is debt, and
    # no count separates them — open the sites.
    print("   ⚑ A SHARED PHRASE IS NOT AUTOMATICALLY DEBT — it may be one law restated\n"
          "     across files (paydown), a convention each tool correctly states, or a\n"
          "     copied block. `--commentary` finds exact copies; this finds PARAPHRASES,\n"
          "     which is the half no exact-match census can reach. Open the sites.")
    raise SystemExit(0)
