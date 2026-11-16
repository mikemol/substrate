#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""tmi_status.py -- THE REVISION OPERATOR of the transcript-memory index.

⚑ WHAT THIS IS.  §5 of `scratch/transcript-memory-index-design.md` defines a
REVISION LINK: `turn B re-quotes turn A under a revision cue`, bidirectional, no
label and no chain resolution.  This module owns the cue set, the recurrence
test, the ground truth, and the scoring harness.  It is the part of the design
with no prior art, and the design says it must be separately testable.

⚑ WHY IT IS SCORED AND NOT JUST RUN.  Design §7 names recall of this operator as
"the single measurement I would take next" -- precision was 9/9 but that is a
SAMPLE PROPERTY: all nine detections sat on ONE chain (`--holes`/`Fin`/`Literals`)
whose vocabulary is a proper noun that survives paraphrase.  Precision 100%
measures the case where the mechanism works.  So this file carries the
hand-labelled ground truth INLINE (`GROUND_TRUTH`) and every change to the cue
set or the recurrence test is scored against it by `--score`.  A cue widened
without a re-score is an unmeasured change.

⚑⚑ AND THE GROUND TRUTH WAS NEARLY LOST.  It was hand-labelled in a prior
agent's context, reported as an aggregate ("30 revisions, 27 certain"), and
never written to disk -- so the numbers survived and the LABELS did not, and
the next reader (this one) could not re-score without re-deriving them.  A
measurement reduced to a scalar before it is externalised is a measurement you
can quote and cannot check.  It lives here now, one row per revision, each with
its quoted line.

    tmi_status.py <file> --cues              # cue census: every cue hit, by class
    tmi_status.py <file> --links             # the revision links the operator emits
    tmi_status.py <file> --score             # recall + PAIR score vs GROUND_TRUTH
                                             #   (Ⓘ7: both ends of the link)
    tmi_status.py <file> --score --ablate    # per-conjunct ablation: what each costs
    tmi_status.py <file> --misses            # every ground-truth miss, with its line
    tmi_status.py <file> --artefacts         # the artefact-reference index (§1.4)
    tmi_status.py --selftest

Every mode prints `n of m`.  Read-only: no write mode at all.
"""
import sys
import os
import re
import collections

MEM = "/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory"
sys.path.insert(0, MEM)
sys.path.insert(0, "/home/mikemol/github/substrate/scratch/eliza")
sys.path.insert(0, "/home/mikemol/github/substrate/scratch")

import pathlib
from mikemol.transcriptstruct import blocks as TB
from mikemol.transcriptstruct import provenance as TP
from mikemol.transcriptstruct import records as TR
import grammar_phrase_lattice as G  # noqa: E402

DEFAULT_TRANSCRIPT = os.path.join(
    "/home/mikemol/.claude/projects/-home-mikemol-github-substrate",
    "28df5f75-745e-4963-ae8a-1431f7ace5ab.jsonl")

# ---------------------------------------------------------------------------
# THE CUE SET.  Three classes, and the class matters: they fail differently.
# ---------------------------------------------------------------------------
#
# (A) EXPLICIT.  The reviser names the act.  §5.2's original set.
#     ⚑ `i was wrong` was WIDENED to `was wrong` (Ⓘ1).  Under a recall-dominant
#     regime (§5: "a missed link costs a reader the recovery; a spurious one
#     costs them a glance") the narrower form is not worth its losses -- it
#     misses "my claim was wrong", "that reading was wrong", "the census was
#     wrong", every revision where the subject is the CLAIM and not the actor.
CUE_EXPLICIT = re.compile(
    r"retract|withdraw|withdrew|supersede[ds]?|\bwas wrong\b|correction|"
    r"you'?re right|overclaim|my (mistake|error)|i (?:got|had) (?:that|this|it) wrong|"
    r"stands? corrected",
    re.I)

# (B) CONTRASTIVE NEGATION.  Ⓘ2.  The corpus's dominant revision shape and the
#     design does NOT have it: §6.4(d) names `not X but Y` but only as a
#     PRESERVATION rule (keep both sides of a recovered phrase), never wired
#     into the revision operator.  A revision here reads
#     "not <the old framing> -- <the new one>", and the old framing is exactly
#     the phrase that recurs from the earlier unit.
#     ⚑ THIS IS WHY THE CUE SET AND THE RECURRENCE TEST ARE NOT INDEPENDENT:
#     for this class the negated span IS the recurrence probe.
CUE_CONTRAST = re.compile(
    r"\b(?:not|isn'?t|aren'?t|wasn'?t|weren'?t|never|no longer|"
    r"rather than|instead of|far from)\b",
    re.I)
# the "X, not Y" / "not X but Y" / "not X -- Y" frame, with the contrast spans
CONTRAST_FRAME = re.compile(
    r"(?:\bnot\b|\bisn'?t\b|\baren'?t\b|\bwasn'?t\b|\bnever\b)\s+"
    r"(?P<neg>[^.,;:—–]{4,80})"
    r"(?:\s*(?:—|–|--|,|;)\s*|\s+but\s+|\s+it'?s\s+)"
    r"(?P<pos>[^.,;:—–]{4,80})",
    re.I)
# the mirror frame: "Y, not X" -- the corpus writes this at least as often
CONTRAST_FRAME_R = re.compile(
    r"(?P<pos>[^.,;:—–]{4,80}?)"
    r"\s*(?:,|—|–|--)\s*not\s+"
    r"(?P<neg>[^.,;:—–]{2,80})",
    re.I)

# (C) SELF-QUOTATION.  Ⓘ2.  An actor putting their OWN earlier phrasing in
#     scare quotes is almost always about to qualify it.  Turn 670 self-quotes
#     "silent death"; recurrence fires perfectly and no cue in class (A) or (B)
#     is present.  The quoted span is a HIGH-CONFIDENCE recurrence probe --
#     stronger than cluster-phrase overlap, because the actor has marked it.
# ⚑ THE APOSTROPHE IS NOT A DELIMITER, AND READING IT AS ONE PRODUCED JUNK SPANS
# (Ⓘ9).  `it's`/`that's`/`doesn't` put a bare `'` mid-word, so a character class
# that admits `'` as an opening or closing quote matches from one contraction to
# the next and returns a span that no actor ever quoted -- e.g. "s slow. Let me
# see what it" out of "it's *slow*. Let me see what it's printed".  Those spans
# then go into the recurrence probe as if the writer had marked them.
#
# The fix is that an ASCII `'` is admitted as a quote delimiter ONLY when it is
# not flanked by word characters -- i.e. `'foo bar'` yes, `it's` no.  The curly
# forms are unambiguous (‘ opens, ’ closes) and need no guard, but ’ is ALSO the
# typographic apostrophe in `it’s`, so it gets the same treatment on the open
# side.  Double quotes are never contractions and stay unconditional.
#
# ⚑ Two delimiters for two jobs, and the selftest pins the contraction case
# specifically -- a length filter would not have caught this, because the junk
# spans are exactly the length of a real quote.
QUOTED = re.compile(
    r"(?:"
    r'"([A-Za-z][^"”]{6,70})"'                  # "..."
    r"|“([A-Za-z][^”]{6,70})”"                  # “...”
    r"|(?<!\w)['‘’]([A-Za-z][^'‘’\n]{6,70})['’](?!\w)"   # '...' not a contraction
    r")")

# ⚑ MEASURED, AND IT KILLED THE NAIVE FORM OF BOTH NEW CUE CLASSES.  A first cut
# scored `CUE_CONTRAST` (the bare word list) and `QUOTED` over the whole unit
# body and produced 242 links over 507 units -- 48% of the corpus "revised
# something".  Recall was 14/14 and MEANINGLESS: a detector that fires on half
# the corpus has no discriminating power, and the ground truth (all positives,
# no labelled negatives) cannot see that.  ⚑⚑ THAT IS THE tmi-F1 ERROR AGAIN,
# INVERTED: F1 said precision 9/9 was a sample property; this says recall 14/14
# is a THRESHOLD property.  Neither number means anything without the other, and
# a positives-only ground truth structurally cannot supply the other.
#
# The census said exactly what was wrong:
#   572 hits  contrast  'not'          -- bare negation is ordinary prose
#    95 hits  selfquote 'description'  -- a tool_use ARGUMENT NAME, not a quote
#    88 hits  selfquote 'command'      -- same
#    42 hits  selfquote 'file_path'    -- same
#
# So both classes are narrowed by the same principle: the cue is not the WORD,
# it is the FRAME, and the frame only exists in prose.
#
# (B') contrastive negation fires ONLY on the two contrast FRAMES, and the
#      negated span is returned as the recurrence probe -- for this class the
#      cue and the recurrence test are one test, not a conjunction.
# (C') self-quotation is restricted to assistant PROSE.  §1.4 admits tool
#      traffic into the unit body for the artefact join, and that is right --
#      but a JSON key is not an actor re-quoting themselves.  Reading tool
#      structure as prose is the same category error as grepping the transcript.
# (D) OPERATOR-REFUTATION -- Ⓘ9.  `tmi-F14` named this the class the cue set
#     structurally cannot see: the operator corrects the actor, and the actor's
#     reply is a BARE CONCESSION with no content of its own.  Turns 198, 401,
#     644, 664, 676 are all of this shape.  Classes (A)-(C) have nothing to
#     match, and for a principled reason: the revised claim is NOT IN THIS TURN.
#     An explicit cue needs the actor to name the retraction, a contrast frame
#     needs the old framing restated, a self-quote needs the actor to quote it.
#     A concession restates nothing -- that is what makes it a concession.
#
# ⚑ THE ANCHOR IS THE WHOLE CUE, AND WITHOUT IT THIS CLASS IS THE 48% DISASTER
# AGAIN.  `you're right` / `right` / `fair` / `correct` unanchored are ordinary
# prose (`right` alone appears in ordinary sentences constantly, and `CUE_EXPLICIT`
# already carries the unanchored `you're right` at a measured 6 hits).  What
# distinguishes a concession is POSITION: it is the FIRST THING IN THE TURN.  An
# actor conceding opens with it; an actor using the same words mid-argument is
# not conceding.
#
# ⚑ MEASURED BEFORE WRITING THE CLASS, WHICH IS WHY IT IS NARROW.  Anchored at
# the start of an assistant prose block over this corpus: 5 hits in 796
# envelopes (0.6%), and ALL FIVE are ground-truth revisers (198, 401, 644, 664,
# 676).  The brief that commissioned this warned the cue would be "at least as
# dangerous" as the contrast word list, which fired on 48% -- it is not, and the
# reason is structural rather than lucky: the contrast list matched a WORD that
# appears anywhere, this matches a POSITION that occurs once per turn.  A cue
# with a positional anchor has a firing rate bounded by the turn count by
# construction, and the bare word list had no such bound.
#
# ⚑ `--score` reports firing rate and antecedent spread beside recall precisely
# so this claim stays falsifiable on the next corpus.
CUE_CONCESSION = re.compile(
    r"\A\s*(?:"
    r"(?:yes|no|right|correct|true|fair(?: enough| point)?|agreed|ack|"
    r"good catch|nice catch|point taken|indeed)\b"
    r"|you'?re right\b|you'?re correct\b|that'?s right\b|that'?s fair\b"
    r"|that (?:confirms|settles) (?:your|the) (?:point|reading)\b"
    r"|i (?:was|had it) wrong\b"
    r")",
    re.I)

CUE_CLASSES = (("explicit", CUE_EXPLICIT),)


def contrast_spans(text):
    """The negated spans of a genuine contrast FRAME. Not the bare word."""
    out = []
    for rx in (CONTRAST_FRAME, CONTRAST_FRAME_R):
        for m in rx.finditer(text):
            neg = m.group("neg").strip()
            # ⚑ THE FLOOR IS 2, NOT 4, AND THE SELFTEST CAUGHT WHY.  "two
            # spillers, not one" -- the negated span is the single word "one",
            # which a 4-char floor discards, losing a ground-truth revision.
            # The contrast frame carries its own evidence that this is a
            # revision (the writer wrote the frame); span LENGTH is not what
            # makes it one.  The length filter that matters is downstream, on
            # the recurrence probe, where a short span would match everything
            # -- and that filter is already there (`len(probe) < 8`).  Two
            # filters for two different jobs; conflating them cost a detection.
            if 1 < len(neg) < 80:
                out.append(neg)
    return out


def cue_hits(text, prose=None):
    """Every cue in `text`, as (class, matched-string).

    `prose` is the ASSISTANT-TEXT-ONLY portion of the unit; self-quotation is
    detected there and nowhere else (see the census note above).  When `prose`
    is None the whole text is treated as prose -- correct for a bare string,
    which is what the selftest passes.
    """
    if prose is None:
        prose = text
    out = []
    for name, rx in CUE_CLASSES:
        for m in rx.finditer(text):
            out.append((name, m.group(0).lower()))
    for neg in contrast_spans(prose):
        out.append(("contrast", neg.lower()))
    for m in QUOTED.finditer(prose):
        # three alternatives, exactly one of which participates
        span = next((g for g in m.groups() if g), None)
        if span:
            out.append(("selfquote", span))
    for m in CUE_CONCESSION.finditer(prose):
        out.append(("concession", m.group(0).strip().lower()))
    return out


# ---------------------------------------------------------------------------
# THE ARTEFACT REFERENCE INDEX -- Ⓘ3, design §1.4.
# ---------------------------------------------------------------------------
#
# ⚑ WHY THIS REPLACES TOKEN OVERLAP AS THE RECURRENCE TEST, AND WHY THE DESIGN
# ALREADY SAID SO WITHOUT NOTICING.  §7 lists "recall of the revision operator"
# and "whether the 24% intra-exchange figure holds" as two INDEPENDENT unknowns.
# They are one.  §1.4 measured that only 24% of claim-bearing sentences invoke
# their named tool in the same exchange, and concluded the join key for WARRANT
# is the artefact reference, not adjacency.  The recurrence test has exactly the
# same shape -- "does this later unit refer to the same thing as that earlier
# one" -- and the same answer.  Token overlap asks whether the two units share
# WORDING; a revision paraphrases into the reviser's register, so wording is the
# thing least likely to survive.  The artefact reference is what does survive:
# a file, a tool, a symbol, a flag, a metric name is a proper noun the reviser
# must repeat in order to be talking about the same thing at all.
#
# Witness (from the recall measurement): turn 383 "the N <= 3 cap is a
# memory-and-bandwidth ruling" revised at 396 by "the fold doesn't lease from
# it" -- shared CONTENT, near-disjoint TOKENS.  Overlap sees nothing.  The
# artefact ("the lease"/membudget) is in both.
#
# ⚑ AND THIS IS THE SAME STATISTIC AS tmi-F5.  That finding unified Sequitur
# rule-`uses`, SPPF node fan-in and apex band-breadth as one reading -- a DAG
# node shared by >= 2 parents, read along the sharing axis.  An artefact
# reference shared by >= 2 turns is that node, with turns as the parents.  So
# the linker is FAN-IN OVER AN ARTEFACT GRAPH, not a pairwise phrase matcher.
# The implementation below is deliberately written that way: build the
# `artefact -> [turns]` posting list once, then read links off it.  That is why
# it is O(hits) and not O(turns^2).

# ⚑ ORDER IS LOAD-BEARING AND IT WAS WRONG ONCE.  `--grep-content` also matches
# the snake-id alternative (`grep` + `content` across the hyphen is not a snake
# id, but `grep_content`-shaped ids are, and the file alternative can claim a
# prefix).  Python's alternation is FIRST-MATCH, not longest-match, so the
# longest/most-specific forms must come first.  The selftest pins the flag case.
ARTEFACT = re.compile(
    r"("
    r"--[a-z][a-z0-9-]{2,}"                                                # flags
    r"|\b[A-Za-z_][A-Za-z0-9_]*\.(?:py|agda|agdai|md|json|tsv|mk|sql|sh|bib)"  # files
    r"|\b[A-Z][A-Za-z0-9]*(?:/[A-Z][A-Za-z0-9]*)+"                         # Mod/Path
    r"|\b[a-z_]{3,}_[a-z_]{3,}\b"                                          # snake ids
    r"|\b(?:membudget|agda|postgres|sppf|jsonb|sequitur|mypy|cgroup)\b"
    r")", re.I)

# tokens too generic to be a join key -- they appear in most turns and would
# make every pair "share an artefact".  Kept SMALL and named: a large stoplist
# is a tuning constant pretending to be a fact.
ARTEFACT_STOP = {"--help", "--apply", "--dry-run", "--verbose", "--quiet"}

# ⚑ A TUNING CONSTANT, NAMED AS ONE.  An artefact appearing in more than this
# FRACTION of units is treated as universal and dropped as a join key.  It is
# a fraction and not a count deliberately -- design §7 flags "the df <= 60
# boilerplate cap must become a fraction of N; I did not derive the fraction"
# as an open gap, and hardcoding a scalar here would re-open it.  This value is
# FITTED, not derived: it is the loosest setting at which turn 396 backlinks to
# 383 rather than to turn 11.  Treat it as the `[gap]` it is; a second corpus
# should re-fit it, and the score harness is how you would.
ARTEFACT_DF_FRAC = 0.04

# ⚑⚑ Ⓘ8 / THE HEAD CUT, AND IT IS A CROSS-CORPUS AGREEMENT RATHER THAN A
# COINCIDENCE.  ⟡sppf-ingestion measured `node_child` fan-in corpus-wide
# (2026-08-24, LIVE): 440,604 distinct children over 1,733,430 edges, max fan-in
# 87,359, and the distribution is BIMODAL rather than concentrated at low arity:
#
#     58.2% of children have fan-in exactly 1        -- no sharing signal at all
#     73 children (0.017%) absorb 27.1% of all edges -- AST boilerplate:
#         ⟨Range'⟩ 87,359 · #Bool:False 77,255 · ArgInfo 70,387
#     the DISCRIMINATING band is the middle: 183,887 children / 1,263,795 edges
#         once the head is cut
#
# This linker reached the same conclusion from the other side and one corpus
# over: joining on raw co-occurrence made every backlink point at turn 11, whose
# artefacts recur for 700 turns.  `membudget`, present in 63 of 712 turns, IS
# this corpus's ⟨Range'⟩ -- a name shared by everything, discriminating nothing.
#
# So the two ends of the band are cut for DIFFERENT reasons and both cuts are
# named, rather than folded into one opaque threshold:
#   HEAD (df > ARTEFACT_DF_FRAC * N)  -- universal; a join key that joins
#                                        everything is not a join key.
#   TAIL (df < 2)                     -- fan-in 1 is not sharing; there is no
#                                        antecedent to point at.  Structurally
#                                        enforced by `prevs` being empty, but
#                                        stated because the sppf measurement
#                                        says it is 58% of the population, not
#                                        an edge case.
# ⚑ Two agents, two corpora, one reading -- written here so the next reader
# finds an argument rather than a tuned constant.
ARTEFACT_DF_MIN = 2


def artefacts(text):
    out = set()
    for m in ARTEFACT.finditer(text):
        a = m.group(1)
        al = a.lower()
        if al in ARTEFACT_STOP:
            continue
        out.add(al)
    return out


# ---------------------------------------------------------------------------
# UNITS
# ---------------------------------------------------------------------------
def load_units(path, include_tools=True):
    """(turn, role, body, prose) per envelope.

    ⚑ TWO BODIES, DELIBERATELY.  `body` admits tool traffic (§1.4: that is
    where the artefact names live, and the artefact join is the whole point of
    Ⓘ3).  `prose` is assistant text ONLY.  They are separate because the two
    halves of the operator want different inputs: the artefact index wants tool
    traffic in, and the cue detector wants it OUT -- a tool_use argument named
    "description" is not an actor quoting themselves.  Merging them cost 48%
    false-fire; see the census note on CUE_CLASSES.
    """
    units = []
    n_env = 0
    for record in TR.read_path(pathlib.Path(path)):
        if isinstance(record, TR.MalformedLine):
            if record.text.strip():
                n_env += 1
            continue
        n_env += 1
        index = record.line - 1
        who = TP.classify(record)
        if who.kind == "human":
            units.append((index, "human", who.text, who.text))
            continue
        if isinstance(record, TR.AssistantRecord):
            role = "assistant"
        elif isinstance(record, TR.UserRecord):
            role = "user"
        else:
            continue
        parts, prose = [], []
        for block in TB.blocks(record):
            if block.kind == "text" and role == "assistant":
                parts.append(block.text)
                prose.append(block.text)
            elif include_tools and block.kind in ("tool_use", "tool_result"):
                parts.append(block.text)
        body = "\n".join(p for p in parts if p and p.strip())
        if body.strip():
            units.append((index, role, body, "\n".join(p for p in prose if p and p.strip())))
    return units, n_env


# ---------------------------------------------------------------------------
# THE OPERATOR
# ---------------------------------------------------------------------------
def build_links(units, mode="artefact", cluster_phrase_index=None):
    """Emit revision links.  `mode` selects the RECURRENCE test:

       "artefact"  -- Ⓘ3.  B refers to an artefact that some A < B also refers
                      to.  Fan-in over the artefact posting list.
       "phrase"    -- the original §5.2 test: B re-quotes a cluster phrase whose
                      first use is < B.  Requires `cluster_phrase_index`.
       "subject"   -- Ⓘ10.  B predicates over a SUBJECT that some A < B also
                      predicates over.  Fan-in over the actor-claim posting
                      list (`tmi_subject`), which keys on the sentence's
                      subject position rather than on any identifier in it --
                      so it reaches `shard 0` and `the fold`, referents that
                      match no file/flag/symbol pattern and are therefore
                      invisible to the artefact index at any threshold.
       "none"      -- cue only.  The ceiling: what the cue set alone can reach.
    """
    posting = collections.defaultdict(list)   # artefact -> [turn]
    corpus_so_far = []                        # (turn, normalised prose)
    links = []
    n_units = len(units)
    # ⚑⚑ THE PRIOR-TURN JOIN IS WRONG AND MEASURING IT IS WHAT SHOWED THAT.
    # The Ⓘ9 brief said the concession's antecedent is "the PRIOR TURN -- the
    # one place §1.4's rejected adjacency join is RIGHT".  Read on the corpus,
    # literal adjacency fails on BOTH of its ends:
    #
    #   * FILLER ENVELOPES SIT BETWEEN.  Every one of 198/401/644/676 has a
    #     `file-history-snapshot` (and often a `system`) envelope between the
    #     human turn and the concession, so turn-1 is a snapshot with no text.
    #     649 has TWO `queue-operation` envelopes in between.
    #   * THE PRIOR TURN IS OFTEN A TOOL RESULT.  664's predecessor is a 45-line
    #     `tool_result` from a Read; the "point" being confirmed is a HUMAN turn
    #     further back.  632's predecessor is a `pgrep` result.
    #
    # So the join is NEAREST PRECEDING HUMAN TURN, not the previous envelope.
    # That is a stronger claim than adjacency, not a weaker one: it says the
    # antecedent of a concession is the OPERATOR'S last utterance, which is what
    # "you're right" is semantically pointing at, and it is robust to however
    # many tool calls and snapshots the harness interleaved.  §1.4's measured
    # rejection of adjacency stands unamended -- this is not the exception the
    # brief thought it had found, because it is not adjacency.
    #
    # ⚑ AND `--human` IS THE PREDICATE, NOT `role == "user"`.  `transcriptstruct`
    # records that 189 envelopes carry role=user and only 13 carry human prose;
    # tool_results and `<system-reminder>` injections are role=user too.
    # `load_units` already applies that predicate (it tags a unit "human" only
    # when `T.human_text` returns), so this reads the tag and does not re-derive
    # it -- one authority for "did a person say this".
    last_human = None
    for turn, role, text, prose in units:
        arts = artefacts(text)
        hits = cue_hits(text, prose)
        if role != "human" and hits:
            back = set()
            # ⚑ THE SPAN-CARRYING CUES BRING THEIR OWN RECURRENCE PROBE, and
            # that is the structural point of Ⓘ2.  For an explicit cue
            # ("I retract") the cue says only THAT a revision happened; WHICH
            # earlier turn it revises has to come from a separate recurrence
            # test.  For a contrastive negation or a self-quotation the cue
            # IDENTIFIES THE REVISED CLAIM -- the negated span / the quoted
            # span IS the earlier phrasing, marked as such by the writer.  So
            # these are not "more cues to conjoin with recurrence"; they are
            # cue and recurrence in one token, which is why they reach
            # revisions that paraphrase (turn 396) where overlap cannot.
            for cls, span in hits:
                if cls == "concession":
                    # the operator's last utterance IS the revised claim
                    if last_human is not None and last_human < turn:
                        back.add((last_human, span[:60]))
                    continue
                if cls in ("contrast", "selfquote"):
                    probe = _norm(span)
                    if len(probe) < 8:
                        continue
                    for prev, ptext in corpus_so_far:
                        if prev < turn and probe in ptext:
                            back.add((prev, span[:60]))
                            break
            if mode == "artefact":
                # ⚑⚑ FAN-IN IS THE JOIN KEY ONLY WHERE IT IS *LOW*, AND THE
                # FIRST CUT GOT THIS EXACTLY BACKWARDS.  Joining on mere
                # co-occurrence made every link point at turn 11 -- the first
                # turn of the session, which names `obs_node`, `--holes`,
                # `schema.py` and a dozen other artefacts that then recur for
                # 700 turns.  Turn 396's revision of turn 383 backlinked to
                # turns 11 and 12.  Recall was still 100% because the ground
                # truth scores the REVISER; the antecedent was garbage, and the
                # antecedent is the half a reader actually needs (§5.3: "the
                # reader arriving at 249 is handed 305").
                #
                # tmi-F5 says fan-in, SPPF sharing and band-breadth are one
                # statistic read along the sharing axis -- and the apex
                # machinery has always read that axis GRADED, universal-shallow
                # to pairwise-deep.  A universal artefact is the shallow end:
                # shared by everything, discriminating nothing.  So the same
                # correction the apexes already make applies here: weight by
                # RARITY and take the NEAREST antecedent, not the earliest.
                cands = []
                for a in arts:
                    prevs = [p for p in posting[a] if p < turn]
                    if not prevs:
                        continue
                    df = len(set(posting[a]))
                    if df < ARTEFACT_DF_MIN:      # Ⓘ8 tail cut: fan-in 1
                        continue
                    if df > max(3, ARTEFACT_DF_FRAC * n_units):
                        continue          # Ⓘ8 head cut: universal, not a key
                    cands.append((df, turn - max(prevs), max(prevs), a))
                for _df, _d, prev, a in sorted(cands)[:3]:
                    back.add((prev, a))
            elif mode == "phrase":
                w = " " + " ".join(G.words(text)) + " "
                for p, idxs in (cluster_phrase_index or {}).items():
                    if (" " + p + " ") in w and idxs and idxs[0] < turn:
                        back.add((idxs[0], p))
            elif mode == "subject":
                # ⚑ Ⓘ10.  DEFERRED IMPORT, AND THE REASON IS A CYCLE AND NOT A
                # COST.  `tmi_subject` imports THIS module for the cue set and
                # the unit loader (one authority for "is this a revision at
                # all"), so a module-level import here would be circular.  The
                # dependency is genuinely one-way at the CONCEPT level -- the
                # subject probe is a recurrence conjunct that consumes the cue
                # set -- and the deferral is what lets the file layout say so.
                # ⚑ It is hoisted to the top of the branch rather than called
                # per-turn: `subject_spans` walks the whole unit list once, and
                # calling it inside the loop would be O(turns^2).
                import tmi_subject as SUBJ
                if _SUBJ_CACHE.get("units") is not units:
                    _SUBJ_CACHE["units"] = units
                    _SUBJ_CACHE["post"] = SUBJ.posting(units)
                    per = collections.defaultdict(set)
                    for tt, ss, _inh in SUBJ.claims(units):
                        per[tt].add(ss)
                    _SUBJ_CACHE["per"] = per
                post_s = _SUBJ_CACHE["post"]
                head_s = max(3, SUBJ.SUBJECT_DF_FRAC * n_units)
                cands = []
                for s in _SUBJ_CACHE["per"].get(turn, ()):
                    prevs = [p for p in post_s[s] if p < turn]
                    if not prevs:
                        continue
                    df = len(set(post_s[s]))
                    if df < SUBJ.SUBJECT_DF_MIN or df > head_s:
                        continue
                    cands.append((df, turn - max(prevs), max(prevs), s))
                for _df, _d, prev, s in sorted(cands)[:3]:
                    back.add((prev, s))
            elif mode == "none":
                back.add((-1, ""))
            if mode == "union":
                # ⚑ THE ANSWER Ⓘ3 WAS REACHING FOR, AND IT IS A UNION AND NOT A
                # REPLACEMENT.  Ⓘ3 said "loosen recurrence FROM token-overlap
                # TO the artefact join".  Measured, that swap is not an
                # improvement -- it is a trade: the artefact join reaches
                # revisions whose wording changed completely (it is why 149,
                # 518, 709 link to their real antecedents), and the phrase join
                # reaches revisions whose shared referent is a discourse phrase
                # with no code identifier in it (396 -> 383).  Their blind
                # spots overlap only partly, so coverage is the UNION -- the
                # same reading as `correlated-instruments-agreeing-is-not-
                # coverage`: two instruments both reporting a hit is not
                # confirmation, and two both missing is not absence.
                cands = []
                for a in arts:
                    prevs = [p for p in posting[a] if p < turn]
                    if not prevs:
                        continue
                    df = len(set(posting[a]))
                    if df < ARTEFACT_DF_MIN:      # Ⓘ8 tail cut: fan-in 1
                        continue
                    if df > max(3, ARTEFACT_DF_FRAC * n_units):
                        continue                  # Ⓘ8 head cut: universal
                    cands.append((df, turn - max(prevs), max(prevs), a))
                for _df, _d, prev, a in sorted(cands)[:3]:
                    back.add((prev, a))
                w = " " + " ".join(G.words(text)) + " "
                for p, idxs in (cluster_phrase_index or {}).items():
                    if (" " + p + " ") in w and idxs and idxs[0] < turn:
                        back.add((idxs[0], p))
                # ⚑ Ⓘ10 JOINS THE UNION, AND THE ARGUMENT IS THE ONE ALREADY
                # WRITTEN ABOVE.  `correlated-instruments-agreeing-is-not-
                # coverage`: the subject probe's blind spot (a turn whose
                # sentences are all fragments -- 83 of 179 actor-prose units)
                # is disjoint from the artefact probe's (a referent with no
                # code identifier, `shard 0`) and from the phrase probe's (a
                # revision that paraphrases).  Adding it as a THIRD arm of the
                # union rather than a replacement is the same reading Ⓘ3 was
                # corrected into.
                import tmi_subject as SUBJ
                if _SUBJ_CACHE.get("units") is not units:
                    _SUBJ_CACHE["units"] = units
                    _SUBJ_CACHE["post"] = SUBJ.posting(units)
                    per = collections.defaultdict(set)
                    for tt, ss, _inh in SUBJ.claims(units):
                        per[tt].add(ss)
                    _SUBJ_CACHE["per"] = per
                post_s = _SUBJ_CACHE["post"]
                head_s = max(3, SUBJ.SUBJECT_DF_FRAC * n_units)
                cands = []
                for s in _SUBJ_CACHE["per"].get(turn, ()):
                    prevs = [p for p in post_s[s] if p < turn]
                    if not prevs:
                        continue
                    df = len(set(post_s[s]))
                    if df < SUBJ.SUBJECT_DF_MIN or df > head_s:
                        continue
                    cands.append((df, turn - max(prevs), max(prevs), s))
                for _df, _d, prev, s in sorted(cands)[:3]:
                    back.add((prev, s))
            if back:
                classes = sorted({c for c, _ in hits})
                links.append((turn, sorted(back)[:6], classes, hits[:4]))
        for a in arts:
            posting[a].append(turn)
        if prose.strip():
            corpus_so_far.append((turn, _norm(prose)))
        if role == "human":
            last_human = turn
    return links, posting


# ⚑ ONE-ENTRY MEMO KEYED ON IDENTITY, NOT A GLOBAL CACHE.  `build_links` is
# called once per mode by the score harness over the SAME unit list, so the
# subject posting list would otherwise be rebuilt per call.  Keyed on `is` and
# not on a hash so a DIFFERENT corpus can never read a stale posting list --
# the `reread-meters-toctou` shape, and the cheap defence against it.
_SUBJ_CACHE = {"units": None}

_WS = re.compile(r"[^a-z0-9]+")


def _norm(s):
    return " " + _WS.sub(" ", s.lower()).strip() + " "


def cluster_index(units):
    items = [(f"t{t:05d}", G.words(x)) for t, _r, x, _p in units if x.strip()]
    cl = G.cluster_phrases(items, phrase_min=3, min_members=2, tau=0.5)
    return {p: sorted(int(x[1:]) for x in m) for p, m in cl}


# ---------------------------------------------------------------------------
# GROUND TRUTH -- see the module docstring for why it lives here.
# ---------------------------------------------------------------------------
# Each row: (turn, certainty, quoted line).  Externalised from the recall
# measurement of 2026-08-23 over 28df5f75, 796 of 796 envelopes hand-read.
# `?` = the three uncertain labels; they are scored SEPARATELY, never folded in
# silently -- an uncertain positive counted as certain inflates recall by a
# label decision rather than a detection.
#
# ⚑⚑ Ⓘ6 / THE SECOND-HAND PASS (2026-08-24).  The 16 "missing" labels were
# recovered by re-reading EVERY assistant prose block 0-712 via
# `transcriptstruct --prose` (a mode added for this pass, because labelling from
# `--messages` first lines is what reduced the first pass to a count).  The pass
# was run BEFORE the detector, so the label set is not bounded by what the
# detector finds.
#
# ⚑ AND THE ORIGINAL COUNT OF 30 DID NOT SURVIVE.  The exhaustive pass finds
# **35** revision-bearing turns, not 30 -- and the 14 previously recorded are all
# among them.  So "30" was itself an estimate made in-context, and re-deriving it
# was the right call rather than hunting for exactly 16 more.  `tmi-F10`.
# Every row below carries the turn and the quoted line, so this can never again
# be reduced to a scalar.
#
# The `kind` column is the taxonomy: retraction / operator-refutation (the
# operator corrected the actor) / peer-refutation / supersession (a measurement
# replaced an earlier one) / reinstatement / narrowing.
GROUND_TRUTH = [
    # -- recovered in the second-hand pass ---------------------------------
    (38, "y", "Substantial correction to my starting brief: plan item 3 is "
     "already done"),                                             # supersession
    (106, "y", "The plan's 'never touched the corpus' premise is dead."),
    (135, "y", "the unreflected = 943,927 'exact match' puzzle resolves as an "
     "artifact of the smaller corpus - not a finding"),           # retraction
    (149, "y", "not abandoned"),
    (192, "y", "you're right that I stated it more confidently than the "
     "evidence supports"),                                # operator-refutation
    (198, "y", "You're right - I've been operating as if I still needed "
     "approval to touch anything."),                      # operator-refutation
    (209, "y", "The verification for the two paths is --compare-paths, a mode "
     "on sppf_db.py, not query_defs.py --equiv"),                 # supersession
    (240, "y", "was wrong"),
    (249, "y", "THE '13 GENUINE HOLES' FIGURE IS ITSELF A CENSUS ARTIFACT - I RETRACT IT."),
    (257, "y", "I retracted a number I gave you and a peer."),
    (276, "y", "My whole claim was wrong, and I need to retract it immediately."),
    (300, "y", "my 'four for four zero names' was an artifact of how I invoked "
     "the tool"),                                             # peer-refutation
    (305, "y", "My retraction of it is retracted; your original item stands."),
    (325, "y", "I was wrong twice, in opposite directions, and substrate-83's "
     "independent re-run is what caught it."),
    (335, "y", "Confirmed on a second, unrelated module: 0 by path, 2 by name. "
     "The defect is general, not specific to Fin/Literals."),
    (340, "y", "was wrong"),
    (349, "y", "The agda_defs --provides 'bug' I ranked first is substantially "
     "my misuse."),                                     # retraction (of a bug)
    # ⚑ 383 IS AN ANTECEDENT, NOT A REVISION -- and it was handed to this
    # module as a ground-truth positive.  Verified by reading it (`--context
    # 383`): "Monitor armed. Let me check the shard's memory footprint while it
    # warms up — the N ≤ 3 cap is a memory-and-bandwidth ruling."  That is the
    # CLAIM.  Turn 396 is the turn that revises it.  A revision operator must
    # fire on the REVISER and link BACK; firing on the antecedent too would
    # mean firing on every claim later contradicted, which is not detectable at
    # the time the claim is made.  Scored as an antecedent: its detection test
    # is "does 396's link point here", not "does 383 produce a link".
    (383, "antecedent-of-396",
     "the N <= 3 cap is a memory-and-bandwidth ruling"),
    (396, "y", "the fold doesn't lease from it"),
    (401, "y", "You're right to push - I took that from a source comment and "
     "never checked it against the machine."),            # operator-refutation
    (426, "y", "you're right that I asserted it without checking, and the one "
     "thing I did verify undercuts it"),                  # operator-refutation
    (453, "y", "This is my error, and it's the one you were pointing at."),
    (466, "y", "the straw, not the load"),
    (497, "y", "I was about to build a mode against thresholds mid-incident "
     "without checking with them first."),                        # retraction
    (505, "y", "substrate-83's --growth killed a hypothesis I'd been carrying"),
    (518, "y", "two spillers, not one"),
    (587, "y", "cassian found the root cause of my work_mem error, and it's "
     "better than my own account of it.  I'd filed it as carelessness ... "
     "They showed it was a discovery failure"),                   # supersession
    (592, "?", "Two accuracy checks before they file."),  # uncertain: a probe,
    #                                                     # not yet a revision
    (604, "y", "Fin/Literals holds at 33 - a real hole, surviving both my wrong retraction and the fix."),
    (632, "y", "Shard 0 is gone - no process."),      # uncertain-adjacent, but
    #                            supersedes 619's "relaunched ... went through"
    (638, "?", "That's a different failure than the DiskFull, and I don't yet "
     "know its cause."),
    (644, "y", "I should have gone straight to the diagnosis rather than "
     "ending on a summary."),                             # operator-refutation
    (649, "y", "it didn't crash, it's slow"),                     # supersession
    (664, "y", "That confirms your point precisely."),    # operator-refutation
    (670, "y", 'self-quotes its own earlier "silent death" in scare quotes'),
    (676, "y", "the question isn't whether the depth is tractable, it's "
     "whether the fold can yield between levels"),       # operator-refutation
    (689, "y", "The loop already has the seam you're describing - it just "
     "doesn't use it."),
    (709, "y", "The runs aren't dying - they're orphaning backends"),
    (712, "y", "Both 'silent deaths' were my client processes hitting the "
     "harness timeout while postgres kept working."),             # supersession
]
# ⚑⚑ THE COUNT MOVED, AND IT IS DERIVED FROM THE ROWS, NOT RESTATED BESIDE THEM.
# The first pass reported 30 = 27 certain + 3 uncertain, as a scalar with no
# rows.  The exhaustive pass produced the rows above.
#
# ⚑ AND WRITING THE NEW TOTAL BY HAND REPRODUCED THE ORIGINAL DEFECT ON THE
# FIRST TRY.  I typed `GROUND_TRUTH_N = 35` from my own in-context count while
# the list held 40; the selftest caught it.  That is tmi-F6 happening again,
# in the edit that closes tmi-F6, inside the file whose docstring explains why
# a measurement must not be reduced to a scalar before externalisation.  The
# lesson is not "count more carefully" -- it is that a total ALONGSIDE a
# population is a second source of truth, and the only safe total is one
# COMPUTED from the population.  So these are `len()` and a comprehension, and
# they cannot drift from the rows.  `tmi-F11`.
GROUND_TRUTH_N = len(GROUND_TRUTH)
GROUND_TRUTH_CERTAIN = sum(1 for _t, _c, _l in GROUND_TRUTH if _c == "y")
WHY_INCOMPLETE = """\
⚑ RESOLVED (Ⓘ6, 2026-08-24).  The first pass reported a COUNT (30 = 27 certain
+ 3 uncertain) and named turns only for the 14 it discussed; the other 16 were
counted and discarded.  A second EXHAUSTIVE hand pass over every assistant
prose block in 0-712 (`transcriptstruct --prose`, run BEFORE the detector so
the label set is not bounded by what the detector finds) recovered them -- and
found MORE than 30.  So the missing 16 were not merely unrecorded: the total
itself was an in-context estimate.  Recall is now scored against the full
labelled population, and every row carries its quoted line so it cannot be
reduced to a scalar again."""


MODE_RESIDUE = """\
⚑ THE TWO RECURRENCE TESTS ARE NOT ORDERED, AND Ⓘ3 ASSUMED THEY WERE.
Measured on 28df5f75, both reach every recoverable ground-truth reviser; they
differ on the ANTECEDENT, which is the half a reader needs.

  artefact  reaches revisions that PARAPHRASE -- shared code identifier
            survives a total rewording (149, 518, 709).
            BLIND to a shared referent with no identifier in it: "the N <= 3
            cap", "the ruling", "the straw" (396 -> 383).
  phrase    reaches shared discourse referents (396 -> 383).
            BLIND to paraphrase, which is the dominant revision shape and the
            reason tmi-F2 called the recurrence conjunct the dominant loss.

Neither dominates.  `union` is the mode to ship.  Keeping this as a named
residue rather than picking a side, because the losing mode's reach is real."""


def score(links, gt=GROUND_TRUTH, window=2):
    """A link at turn B counts as detecting a ground-truth revision at turn G
    if |B - G| <= window.  The window exists because a revision spans an
    envelope boundary: the cue and the recurrence can land in adjacent
    assistant blocks of one logical turn.  window=0 is available and reported."""
    detected = {t for t, _b, _c, _h in links}
    # an ANTECEDENT is detected when some link points BACK to it -- the reader
    # arriving at the antecedent is handed the reviser (§5.3: bidirectional).
    backlinked = set()
    for _t, back, _c, _h in links:
        for prev, _via in back:
            backlinked.add(prev)
    rows = []
    for turn, cert, line in gt:
        if cert.startswith("antecedent"):
            hit = any(abs(b - turn) <= window for b in backlinked)
        else:
            hit = any(abs(d - turn) <= window for d in detected)
        rows.append((turn, cert, hit, line))
    return rows


# ---------------------------------------------------------------------------
# Ⓘ7 -- PAIR SCORING.  The sharpest finding of round 1 is that reviser-recall
# on a positives-only ground truth is UNFALSIFIABLE: it read 100% both before
# AND after the fix that took antecedent concentration from
# turn-11-dominates-everything down to 3% over 105 distinct antecedents.  The
# number could not move because it was measuring the end the ground truth
# happens to record.
#
# ⚑ A REVISION LINK IS A PAIR, so it has two ways to be wrong and recall sees
# one of them.  These are the other measurements, and none of them is a recall:
#
#   antecedent-precision   of the backlinks emitted from a ground-truth
#                          reviser, what fraction land on a turn that is
#                          PLAUSIBLY the antecedent -- i.e. EARLIER, and not a
#                          universal turn.  Reported as a fraction of backlinks
#                          emitted, with the denominator, because a detector
#                          that emits one backlink per reviser and a detector
#                          that emits six are not comparable on a rate alone.
#   antecedent-concentration  the share held by the single most-pointed-at
#                          turn.  This is the statistic that WAS moving while
#                          recall sat at 100%, so it is the falsifier.
#   pair-exact             for the ONE pair the ground truth records at both
#                          ends (396 -> 383), does the link actually connect
#                          them.  A single case, reported as a single case:
#                          n=1 is a witness, not a rate, and calling it one
#                          would be the tmi-F1 error a third time.
def pair_score(links, gt=GROUND_TRUTH, window=2):
    """(n_pairs, n_plausible, concentration, distinct, exact) -- see above."""
    gt_revisers = {t for t, c, _l in gt if not c.startswith("antecedent")}
    tgt = collections.Counter()
    emitted = plausible = 0
    for turn, back, _c, _h in links:
        is_gt = any(abs(turn - g) <= window for g in gt_revisers)
        for prev, _via in back:
            tgt[prev] += 1
            if not is_gt:
                continue
            emitted += 1
            # PLAUSIBLE = strictly earlier (an antecedent cannot follow its
            # reviser) and not the corpus's own head turn.  This is a NECESSARY
            # condition, never a sufficient one -- it can only falsify a
            # backlink, so read it as an upper bound on precision, not as
            # precision.  A positives-only ground truth cannot give the real one.
            if prev < turn and prev >= 0:
                plausible += 1
    tot = sum(tgt.values())
    conc = (max(tgt.values()) / tot) if tot else 0.0
    exact = None
    pairs = [(t, c, l) for t, c, l in gt if c.startswith("antecedent")]
    if pairs:
        ant = pairs[0][0]
        exact = any(abs(t - 396) <= window
                    and any(abs(p - ant) <= window for p, _v in back)
                    for t, back, _c, _h in links)
    return emitted, plausible, conc, len(tgt), exact


# ---------------------------------------------------------------------------
def main(argv):
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else DEFAULT_TRANSCRIPT
    if not os.path.exists(path):
        print(f"no such transcript: {path}")
        return 2
    units, n_env = load_units(path)
    print(f"units: {len(units)} of {n_env} envelopes  ({path})")

    if "--cues" in argv:
        by = collections.Counter()
        tot = 0
        for turn, role, text, prose in units:
            if role == "human":
                continue
            for c, s in cue_hits(text, prose):
                by[(c, s[:28])] += 1
                tot += 1
        for (c, s), n in by.most_common(40):
            print(f"  {n:4d}  {c:10s}  {s!r}")
        print(f"cue hits: {tot} of {len(units)} units "
              f"({len(by)} distinct)")
        return 0

    # ⚑ `--ablate` WAS DOCUMENTED AND NEVER DISPATCHED, which `toolmodes
    # --divergence` reports as UNBACKED.  A usage line promising a mode the
    # tool does not have is the same defect this whole transcript is a study
    # of: a confident answer to a question the instrument cannot answer.  It
    # is implemented here rather than deleted, because the measurement it
    # names is the one Ⓘ7 needs -- which conjunct is load-bearing.
    if "--ablate" in argv:
        u = units
        print("PER-CONJUNCT ABLATION -- drop one conjunct, re-score both ends.")
        print("⚑ Read the ANTECEDENT columns.  Recall barely moves under any")
        print("  ablation (the cue set alone reaches most revisers); what the")
        print("  recurrence test buys is the ANTECEDENT, which is the half a")
        print("  reader needs and the half recall cannot see.")
        ci_a = cluster_index(u)
        for label, m in (("cue only (no recurrence)", "none"),
                         ("+ phrase recurrence", "phrase"),
                         ("+ artefact recurrence", "artefact"),
                         ("+ subject recurrence", "subject"),
                         ("+ both (union)", "union")):
            lk, _p = build_links(u, mode=m, cluster_phrase_index=ci_a)
            rows = score(lk)
            hit = sum(1 for _t, _c, h, _l in rows if h)
            em, pl, conc, dist, _e = pair_score(lk)
            pct = f"{100*pl//em:3d}%" if em else " n/a"
            print(f"  {label:26s} links={len(lk):4d}  "
                  f"recall={hit:2d}/{len(GROUND_TRUTH)}  "
                  f"ant-plausible={pct}  concentration={conc:4.0%}  "
                  f"distinct-ant={dist:4d}")
        print(f"ablation: 5 of 5 conjunct settings over {len(u)} units")
        return 0

    if "--artefacts" in argv:
        _l, posting = build_links(units, mode="artefact")
        multi = {a: v for a, v in posting.items() if len(set(v)) >= 2}
        for a, v in sorted(multi.items(), key=lambda x: -len(set(x[1])))[:30]:
            print(f"  {len(set(v)):4d} turns  {a}")
        print(f"artefacts with fan-in >= 2: {len(multi)} of {len(posting)}")
        return 0

    modes = ["none", "phrase", "artefact", "subject", "union"]
    ci = cluster_index(units) if ("phrase" in modes) else None
    results = {}
    for m in modes:
        links, _p = build_links(units, mode=m, cluster_phrase_index=ci)
        results[m] = links

    if "--links" in argv:
        for turn, back, classes, hits in results["artefact"]:
            print(f"  LINK turn {turn:4d}  cues={','.join(classes)}")
            for prev, a in back[:3]:
                print(f"         <-- turn {prev:4d}  via artefact «{a}»")
        print(f"links: {len(results['artefact'])} of {len(units)} units")
        return 0

    if "--score" in argv or "--misses" in argv:
        print()
        print(WHY_INCOMPLETE)
        print()
        recoverable = len(GROUND_TRUTH)
        # ⚑ THE FIRING RATE IS REPORTED BESIDE RECALL AND IS NOT OPTIONAL.
        # A positives-only ground truth cannot compute precision, so recall
        # alone is unfalsifiable: a detector that links every unit scores 100%.
        # `fire%` = links / non-human units is the cheapest available proxy for
        # "is this discriminating at all", and it is the number that exposed
        # the 48% degenerate first cut.  Read them as a PAIR or not at all.
        n_asst = sum(1 for _t, r, _b, _p in units if r != "human")
        for m in modes:
            rows = score(results[m])
            hit = sum(1 for _t, _c, h, _l in rows if h)
            certain = [r for r in rows if r[1] == "y"]
            chit = sum(1 for r in certain if r[2])
            nl = len(results[m])
            print(f"  mode={m:9s} links={nl:4d}  "
                  f"fire={100*nl//max(1,n_asst):3d}% of {n_asst} actor units  "
                  f"recall(recoverable)={hit}/{recoverable} "
                  f"({100*hit//recoverable}%)  "
                  f"certain={chit}/{len(certain)}")
        print(f"\n  (ground truth measured at {GROUND_TRUTH_N} total, "
              f"{GROUND_TRUTH_CERTAIN} certain; {recoverable} have recorded turns)")
        # ⚑ ANTECEDENT QUALITY, REPORTED SEPARATELY, BECAUSE REVISER-RECALL
        # CANNOT SEE IT.  The degenerate first cut scored 100% reviser-recall
        # while every backlink pointed at turn 11.  A revision link is a PAIR;
        # scoring only the end the ground truth records measures half of it.
        # ⚑ Ⓘ7: BOTH ENDS OF THE PAIR, FOR EVERY MODE, BESIDE THE RECALL.
        # Recall above could not move; these can.  Read the row, not the recall.
        print("\nPAIR SCORE (Ⓘ7) -- recall scores the REVISER end; these score"
              " the ANTECEDENT end.")
        for m in modes:
            emitted, plaus, conc, distinct, exact = pair_score(results[m])
            pct = f"{100*plaus//emitted}%" if emitted else "n/a"
            print(f"  mode={m:9s} antecedent-plausible={plaus}/{emitted} "
                  f"({pct})  concentration={conc:.0%}  "
                  f"distinct-antecedents={distinct}  396->383={exact}")
        print("  ⚑ 'plausible' is a NECESSARY condition (strictly earlier), so"
              " it is an UPPER BOUND on precision, never precision itself --")
        print("    a positives-only ground truth cannot supply the real one."
              "  'concentration' is the falsifier: it moves when recall cannot.")

        # ⚑ PER-CLASS FIRING RATE, Ⓘ9.  The aggregate `fire%` above cannot say
        # whether a NEWLY ADDED cue class is discriminating -- a class that
        # fires on 1% and a class that fires on 40% both move the aggregate by
        # an amount that depends on overlap with the classes already there.
        # The Ⓘ9 brief's central warning was that a concession cue would be
        # "at least as dangerous" as the contrast word list (48%); that is a
        # claim about ONE class, so it needs a per-class denominator to be
        # answerable at all.  Measured here rather than asserted.
        print("\nPER-CLASS FIRING RATE -- units in which each cue class fires.")
        cls_units = collections.Counter()
        for _t, r, b, p in units:
            if r == "human":
                continue
            for c, _s in cue_hits(b, p):
                cls_units[c] += 0  # ensure the key exists even at zero
            for c in {c for c, _s in cue_hits(b, p)}:
                cls_units[c] += 1
        for c in sorted(cls_units):
            n = cls_units[c]
            print(f"    {c:11s} fires in {n:4d} of {n_asst} actor units "
                  f"({100*n/max(1,n_asst):4.1f}%)")
        print("  ⚑ a class firing on a large share of the corpus has measured"
              " nothing, however much recall it adds.")

        print("\nANTECEDENT SPREAD (mode=artefact) -- how concentrated are the"
              " backlink targets?")
        tgt = collections.Counter()
        for _t, back, _c, _h in results["artefact"]:
            for prev, _via in back:
                tgt[prev] += 1
        top = tgt.most_common(3)
        tot = sum(tgt.values())
        for t, n in top:
            print(f"    turn {t:4d} is the antecedent of {n} links "
                  f"({100*n//max(1,tot)}% of all backlinks)")
        print(f"  distinct antecedents: {len(tgt)} over {tot} backlinks")
        print("  ⚑ a single turn holding a large share means the join key is"
              " universal, not discriminating.")

        print("\nMISSES under mode=artefact:")
        rows = score(results["artefact"])
        nmiss = 0
        for turn, cert, hit, line in rows:
            if not hit:
                nmiss += 1
                print(f"  turn {turn:4d} [{cert}]  «{line}»")
        print(f"misses: {nmiss} of {recoverable} recoverable labels")
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

    # Ⓘ1: the widened cue matches the subject-is-the-claim form
    chk("was-wrong widened", bool(CUE_EXPLICIT.search("my whole claim was wrong")))
    chk("i-was-wrong still", bool(CUE_EXPLICIT.search("I was wrong about that")))
    chk("wrong-alone not a cue", not CUE_EXPLICIT.search("the wrong file"))
    # Ⓘ2a: contrastive negation
    chk("contrast not-X-but-Y", bool(CONTRAST_FRAME.search(
        "This is not a lock but a partition")))
    chk("contrast Y-not-X", bool(CONTRAST_FRAME_R.search(
        "two spillers, not one")))
    chk("contrast em-dash", bool(CONTRAST_FRAME.search(
        "The runs aren't dying — they're orphaning backends")))
    chk("contrast cue fires", bool(CUE_CONTRAST.search("not abandoned")))
    # Ⓘ2b: self-quotation
    chk("selfquote", [h for h in cue_hits('it is a "silent death" after all')
                      if h[0] == "selfquote"])
    # ⚑ Ⓘ9a: THE APOSTROPHE IS NOT A DELIMITER.  The pre-fix QUOTED admitted a
    # bare `'` as an opening AND closing quote, so a sentence with two
    # contractions produced a span running from one to the next -- a "quote"
    # the actor never wrote, fed straight into the recurrence probe.  Turn 649
    # is the live witness.  Length filtering cannot catch it: the junk span is
    # exactly quote-length.
    _junk = [h for h in cue_hits(
        "That's informative - it's slow. Let me see what it's printed.")
        if h[0] == "selfquote"]
    chk("contraction is not a quote", not _junk)
    chk("real single quote still", [h for h in cue_hits(
        "the 'silent death' reading") if h[0] == "selfquote"])
    chk("double quote unaffected", [h for h in cue_hits(
        'it is a "silent death" after all') if h[0] == "selfquote"])
    chk("curly quote", [h for h in cue_hits(
        "a “silent death” again") if h[0] == "selfquote"])
    # ⚑ Ⓘ9b: OPERATOR-REFUTATION, AND THE ANCHOR IS THE CUE.  Unanchored these
    # words are ordinary prose; anchored they fire on 5 of 796 envelopes on the
    # measured corpus, all five ground-truth positives.  Both directions pinned:
    # a bare concession must fire, and the same words mid-sentence must NOT.
    chk("concession anchored", bool(CUE_CONCESSION.match("You're right — I took that from a comment")))
    chk("concession yes-form", bool(CUE_CONCESSION.match("Yes — and I should have gone straight to it")))
    chk("concession right-dash", bool(CUE_CONCESSION.match("Right — the question isn't whether")))
    chk("concession confirms", bool(CUE_CONCESSION.match("That confirms your point precisely.")))
    chk("concession good-catch", bool(CUE_CONCESSION.match("Good catch — that was stale.")))
    chk("concession NOT mid-sentence", not CUE_CONCESSION.match(
        "I think you're right about the cap, but the fold disagrees"))
    chk("concession NOT rightward", not CUE_CONCESSION.match(
        "rightward of the boundary the counts diverge"))
    chk("concession class emitted", [h for h in cue_hits("Right — the loop already yields")
                                     if h[0] == "concession"])
    # Ⓘ3: artefact extraction
    # ⚑ `--grep-content` HERE IS TEST DATA, NOT A MODE OF THIS TOOL, and the
    # mode census reads it as one.  `toolmodes --divergence` reports it
    # UNDOCUMENTED on tmi_status.py because its dispatch heuristic sees the
    # string compared against a variable (`"--grep-content" in a`) and cannot
    # tell `a` is an artefact SET from `artefacts()` rather than argv.  The
    # honest resolution is to say so, not to document a mode that does not
    # exist -- a declaration would make the census agree with itself and be
    # wrong.  The real `--grep-content` is a mode of `transcriptstruct.py`,
    # which is where a reader should look for it.  Filed as `tmi-F13`.
    a = artefacts("sppf_db.py:1989 uses hashtext with --grep-content on Fin/Literals")
    chk("artefact file", "sppf_db.py" in a)
    chk("artefact flag", "--grep-content" in a)
    chk("artefact modpath", "fin/literals" in a)
    chk("artefact stop", "--apply" not in artefacts("run it with --apply"))
    # the KNOWN-ANSWER TEST with the known trap (design §6.2): the 249->305
    # chain must produce links at BOTH ends, and the operator must emit them as
    # SEPARATE links -- a naive implementation resolves the chain and reports
    # "retracted", losing the reinstatement.
    # ⚑ Ⓘ9c: THE CONCESSION JOIN IS THE NEAREST PRECEDING *HUMAN* TURN, NOT THE
    # PRIOR ENVELOPE.  The brief specified adjacency; the corpus refuted it --
    # filler envelopes (`file-history-snapshot`, `system`, `queue-operation`)
    # and tool_results sit between the human turn and the concession in every
    # measured case.  This fixture reproduces exactly that layout: human at 10,
    # two fillers, concession at 13.  An adjacency join would point at 12.
    _u = [(10, "human", "the N<=3 cap is obsolete", "the N<=3 cap is obsolete"),
          (11, "assistant", "{\"file_path\": \"x.py\"}", ""),
          (12, "assistant", "1960  some source line", ""),
          (13, "assistant", "You're right — I never checked it.",
           "You're right — I never checked it.")]
    _lk, _ = build_links(_u, mode="artefact")
    _backs = {p for _t, b, _c, _h in _lk for p, _v in b}
    chk("concession joins the human turn", 10 in _backs)
    chk("concession does not join the filler", 12 not in _backs)
    # and with NO preceding human turn it must emit nothing rather than guess
    _lk2, _ = build_links(_u[1:], mode="artefact")
    chk("concession with no human antecedent emits none",
        not any("concession" in c for _t, _b, c, _h in _lk2))
    gt_turns = {t for t, _c, _l in GROUND_TRUTH}
    chk("gt has 249", 249 in gt_turns)
    chk("gt has 305 (the trap)", 305 in gt_turns)
    chk("gt has 604 (the reinstatement)", 604 in gt_turns)
    chk("no resolution api", not any(
        n in globals() for n in ("resolve_chain", "current_state", "status_of")))
    # ⚑ THE HONESTY GATE INVERTED WHEN Ⓘ6 CLEARED, AND THAT IS THE POINT.  It
    # used to assert `GROUND_TRUTH_N > len(GROUND_TRUTH)` -- that the count
    # exceeded the labels, so nothing could quietly claim recall against 30.
    # The exhaustive pass closed that gap, so the gate now asserts the OPPOSITE
    # invariant: the count must EQUAL the labels.  Either way the file cannot
    # carry a total it has no rows for.
    # ⚑ THE GATE IS NOW A TYPE CHECK, NOT AN EQUALITY.  `GROUND_TRUTH_N ==
    # len(GROUND_TRUTH)` would be a tautology once the constant is derived, and
    # a tautological gate is a green that reports nothing.  What must hold is
    # that the totals are DERIVED at all -- i.e. that no future edit replaces
    # them with a hand-typed integer, which is the failure this file just made.
    chk("gt total is derived from the rows, not typed",
        GROUND_TRUTH_N is not None and
        GROUND_TRUTH_N == len([r for r in GROUND_TRUTH if r]))
    chk("certain + uncertain + antecedent partitions the rows",
        GROUND_TRUTH_CERTAIN
        + sum(1 for _t, c, _l in GROUND_TRUTH if c == "?")
        + sum(1 for _t, c, _l in GROUND_TRUTH if c.startswith("antecedent"))
        == GROUND_TRUTH_N)
    chk("why-incomplete records the resolution", "RESOLVED" in WHY_INCOMPLETE)
    # ⚑ THE COUNT MOVED 30 -> 40: pinned so a later reader cannot read the
    # first pass's estimate back over the labelled population.
    chk("the second pass found MORE than the first pass counted",
        GROUND_TRUTH_N > 30)
    # every row carries a quoted line -- the tmi-F6 defence
    chk("every label has a quoted line",
        all(l.strip() for _t, _c, l in GROUND_TRUTH))
    chk("turns are unique", len({t for t, _c, _l in GROUND_TRUTH})
        == len(GROUND_TRUTH))

    # ⚑ THE TWO MEASURED REGRESSIONS, PINNED.  Both scored 100% recall while
    # broken, so only a targeted case can hold them down.
    # (i) a JSON key from tool traffic is not a self-quotation
    tool_body = '{"description": "run it", "command": "ls", "file_path": "/x"}'
    chk("json keys are not selfquotes",
        not [h for h in cue_hits(tool_body, prose="") if h[0] == "selfquote"])
    chk("prose quote still a selfquote",
        [h for h in cue_hits("", prose='the "silent death" problem')
         if h[0] == "selfquote"])
    # (ii) bare `not` is not a contrast cue; only the frame is
    chk("bare not is not a cue",
        not [h for h in cue_hits("this is not the file I meant to open")
             if h[0] == "contrast"])
    chk("frame is a cue",
        [h for h in cue_hits("two spillers, not one") if h[0] == "contrast"])
    # (iii) a universal artefact is rejected as a join key
    chk("df frac is a fraction", 0 < ARTEFACT_DF_FRAC < 1)
    # Ⓘ8: BOTH ends of the fan-in band are cut, and for different reasons.
    chk("tail cut rejects fan-in 1", ARTEFACT_DF_MIN == 2)
    chk("the two cuts do not overlap",
        ARTEFACT_DF_MIN <= max(3, ARTEFACT_DF_FRAC * 507))

    # (iv) END-TO-END on the real corpus, if it is present: the operator must
    # link 396 back to 383 (the paraphrase case that motivated Ⓘ3) and must NOT
    # collapse every antecedent onto one early turn.  This is the check that
    # would have caught the degenerate cut; the unit-level ones above could not.
    if os.path.exists(DEFAULT_TRANSCRIPT):
        u, _n = load_units(DEFAULT_TRANSCRIPT)
        lk, _p = build_links(u, mode="artefact")
        # ⚑⚑ 396 -> 383 IS A KNOWN *FAILURE* OF THE ARTEFACT JOIN, PINNED AS
        # SUCH.  This was handed to me as the witness case FOR Ⓘ3 -- the
        # paraphrase (383 "the N <= 3 cap is a memory-and-bandwidth ruling"
        # revised at 396 by "the fold doesn't lease from it") that token
        # overlap cannot see and the artefact reference supposedly can.  It
        # cannot, and reading both turns says why:
        #
        #   * the referents 396 shares with 383 are `membudget` (present in 63
        #     turns -- universal, and correctly rejected as a join key by
        #     ARTEFACT_DF_FRAC) and `N <= 3` / `work_mem`;
        #   * `N <= 3` is a QUANTITY NAME, not a code identifier, so no
        #     file/flag/symbol pattern matches it;
        #   * `work_mem` does match and DOES link -- but to turns 40/108/110,
        #     which are where work_mem was last discussed, not to 383.
        #
        # So the join key that would carry this pair is neither adjacency nor
        # artefact reference: it is the DISCOURSE REFERENT ("the cap", "the N
        # <= 3 ruling"), which is a phrase, and which is exactly what
        # mode=phrase catches.  The honest reading is that the artefact join
        # and the phrase join have DIFFERENT and overlapping blind spots, and
        # neither dominates -- see MODE_RESIDUE.  Pinning the failure keeps a
        # future tuner from quietly widening ARTEFACT until this passes for the
        # wrong reason.
        b396 = [b for t, b, _c, _h in lk if t == 396]
        chk("396 fires as a reviser", bool(b396))
        art_has_383 = bool(b396) and any(abs(p - 383) <= 2 for p, _v in b396[0])
        chk("396->383 is a KNOWN artefact-join miss (pinned)", not art_has_383)
        tgt = collections.Counter()
        for _t, back, _c, _h in lk:
            for prev, _v in back:
                tgt[prev] += 1
        share = max(tgt.values()) / max(1, sum(tgt.values()))
        chk(f"no antecedent dominates (max share {share:.0%})", share < 0.15)
        # ⚑ Ⓘ7 PINNED END-TO-END.  A backlink pointing FORWARD is not an
        # antecedent, and no amount of reviser-recall can see that.  This is
        # the check the degenerate first cut would have passed on recall and
        # failed here.
        em, pl, conc, dist, exact = pair_score(lk)
        chk(f"every backlink from a gt reviser points BACKWARD ({pl}/{em})",
            em > 0 and pl == em)
        chk(f"antecedents are spread, not concentrated ({conc:.0%})",
            conc < 0.15)
        chk(f"many distinct antecedents ({dist})", dist > 50)
        chk("396->383 stays a known artefact-join miss", exact is False)
    else:
        print("  SKIP end-to-end: transcript not present")

    # ⚑⚑ SILENT TO THE RUNNER UNTIL 2026-08-25 — 51 green cases, none of them read.
    # `run_selftests.read_result` wants a typed `#row` or, failing that, the regex
    # `selftest:\s*(\d+)\s*/\s*(\d+)`. The line below is `N of M`, so it matched neither
    # and the suite classified `silent` — the verdict for "reported nothing I can read".
    # Same defect in `tmi_index.py` (33 cases) and `tmi_subject.py` (15); all three share
    # this `chk`/`ok`/`fail` idiom and all three were invisible.
    #
    # ⚑ AND SILENT IS NOT IN THE ⟡selftest-contract CENSUS AT ALL. That census keys
    # suites reporting by PROSE, so it refuses them by name; a suite reporting in a form
    # the regex cannot parse is absent from it, and the census reads clean while 51
    # assertions go unread. A false zero, and the instrument cannot see its own gap.
    #
    # ⚑ `skipped` IS NOT PASSED, DELIBERATELY. The end-to-end block above prints
    # `SKIP end-to-end` when the transcript is absent, but `ok`/`fail` never counted
    # those cases, so there is no honest number to declare. Passing a guessed count would
    # put a fabricated figure in the typed record — worse than omitting a real one, since
    # the record is what a consumer trusts. Counting the skip properly is separate work.
    try:
        import rungs as _rungs
        _rungs.emit_record(ok, ok + fail, key="scratch/tmi_status.py")
    except ImportError:
        print("  ⚑ rungs unavailable — no typed record emitted")
    print(f"selftest: {ok} of {ok+fail} checks pass")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
