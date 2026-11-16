#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""tmi_subject.py -- THE ACTOR-CLAIM POSTING LIST.  Ⓘ10, the successor `tmi-F17`
names.

⚑ WHAT THIS IS FOR, STATED AS THE FINDING THAT COMMISSIONED IT.  `tmi-F17`
measured that the four remaining certain misses of the revision operator (turns
38, 209, 632, 649 on corpus 28df5f75) are ONE class -- EVIDENCE-SUPERSESSION,
where the actor's OWN earlier claim is revised by TOOL OUTPUT.  The finding also
says exactly what the failing component is, and it is NOT the cue set:

    The CUE fires on these (209/632/649 all carry contrast frames).  The
    failing conjunct is the RECURRENCE PROBE, so the successor is an
    actor-claim posting list -- NOT another cue class.

⚑⚑ AND THAT DISTINCTION IS THE WHOLE DESIGN, BECAUSE THE OBVIOUS FIX IS THE
WRONG ONE.  A fifth cue class would raise the firing rate against a population
where the cue ALREADY FIRES -- buying nothing and costing precision.  What is
missing is an ANTECEDENT to point at.  `tmi_status.build_links` offers three
recurrence probes and all three fail here for the same structural reason:

  artefact  the antecedent's artefact is either HEAD-CUT as universal
            (turn 209's `sppf_db.py`, present in 39 turns; turn 38's likewise)
            or is not an artefact at all -- turn 632's subject is `shard 0`
            and turn 649's is the bare pronoun `it`.
  phrase    a revision paraphrases into the reviser's register, so token
            overlap is the thing least likely to survive (`tmi-F2`).
  none      no antecedent by construction; 40% plausible, 67% concentration.

⚑ SO THE JOIN KEY IS THE SUBJECT OF THE CLAIM, NOT THE ARTEFACT IN IT.  Turn 632
asserts something ABOUT shard 0; turn 649 revises that assertion while calling
the same thing `it`.  Neither turn shares a rare artefact with the other, and
both are unmistakably about one referent.  What survives paraphrase, survives
pronominalisation, and is not head-cut, is the SUBJECT POSITION: what the
sentence is predicating over.

⚑⚑⚑ THE PRONOUN IS THE HARD HALF AND IT IS RESOLVED POSITIONALLY, NOT
SEMANTICALLY.  `it didn't crash, it's slow` names nothing.  Resolving that
needs an antecedent for `it`, and the honest mechanism available here is the
NEAREST PRECEDING ACTOR CLAIM'S SUBJECT -- the same positional-anchor move that
`tmi-F16` showed bounds a cue's firing rate by construction.  A pronoun subject
therefore INHERITS the subject of the most recent prior actor claim rather than
being dropped or guessed.  That is a weaker claim than coreference resolution
and a stronger one than nothing, and it is FALSIFIABLE: `--subjects` prints
every resolution with the turn it inherited from, so a wrong inheritance is
visible rather than buried in a score.

⚑ WHAT THIS DELIBERATELY DOES NOT DO.  It does not classify a claim, does not
resolve chains, and does not decide whether a link is a revision -- the cue set
already owns that and this module is only the recurrence conjunct.  It emits a
posting list and nothing else, so it can be scored against the same ground truth
by the same harness.

    tmi_subject.py <file> --subjects [--limit N]
                                  # every actor claim with its extracted subject
                                  # and, for a pronoun, the turn it inherited from
    tmi_subject.py <file> --posting [--min-fanin N]
                                  # the subject -> [turns] posting list, by fan-in
    tmi_subject.py <file> --links # the backlinks this probe alone would emit
    tmi_subject.py <file> --gaps  # actor claims with NO recoverable subject
    tmi_subject.py --selftest

Read-only: no write mode at all.  Every mode prints `n of m`.
"""
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import tmi_status as S                          # noqa: E402

DEFAULT_TRANSCRIPT = S.DEFAULT_TRANSCRIPT

# ⚑ A FRACTION OF N, REUSED AND NOT RE-FITTED.  The head cut exists here for the
# same reason it exists on the artefact index (`tmi-F5a` / Ⓘ8): a subject that
# every turn predicates over is a discourse tic, not a join key.  It is
# DELIBERATELY LOOSER than the artefact cut, and the reason is measured rather
# than tuned: an artefact name recurs whenever a tool is MENTIONED, while a
# subject recurs only when a sentence is ABOUT that thing, so the same fraction
# would cut a discriminating band.  The multiplier is the fitted part; the
# authority for the base is `tmi_status`, so there is ONE place "universal" is
# defined.
SUBJECT_DF_FRAC = S.ARTEFACT_DF_FRAC * 2
SUBJECT_DF_MIN = 2                              # fan-in 1 is not sharing

# ⚑ THE PRONOUN SET IS CLOSED AND SMALL, WHICH IS WHY IT IS A SET AND NOT A
# HEURISTIC.  English subject pronouns that can denote a previously-named
# non-person referent.  `I`/`you`/`we` are EXCLUDED on purpose -- a claim whose
# subject is the actor or the operator is not a claim about a thing that can be
# superseded by tool output, and admitting them made every turn inherit.
PRONOUNS = {"it", "that", "this", "they", "these", "those", "he", "she"}

# ⚑ A SENTENCE-INITIAL SUBJECT, ANCHORED.  Same structural move as the
# concession cue (`tmi-F16`): matching a POSITION bounds the firing rate by the
# sentence count, where matching a WORD bounds it only by prose frequency.  The
# subject is the noun phrase before the first finite verb, so the pattern
# anchors at a sentence start and stops at the verb.
_SENT = re.compile(r"(?:^|(?<=[.!?])\s+|\n)([^.!?\n]{3,200})")
_VERB = re.compile(
    r"\b(is|are|was|were|isn't|aren't|wasn't|weren't|has|have|had|hasn't|"
    r"haven't|does|do|did|doesn't|don't|didn't|will|won't|can|can't|could|"
    r"couldn't|should|shouldn't|would|wouldn't|exists|exited|died|ran|runs|"
    r"returned|reads|read|says|said|shows|showed|means|meant|remains|stands|"
    r"went|got|came|looks|seems|appears|lives|sits|carries|holds|names|"
    r"reports|fires|fails|failed|passes|passed|crashed|vanished|produced)\b",
    re.I)

# Markdown emphasis, backticks and leading connectives are not part of a subject.
_STRIP = re.compile(r"^(?:and|but|so|then|also|now|yes|no|ok|okay|well|"
                    r"however|though|still|actually)\b[\s,]*", re.I)
_DECOR = re.compile(r"[`*_\"'“”‘’]+")
_DET = re.compile(r"^(?:the|a|an|its|their|his|her|our|your|my)\s+", re.I)
_WS = re.compile(r"\s+")

# ⚑⚑ A SUBORDINATOR OR A COLON MEANS THE VERB I FOUND IS NOT THE MAIN ONE, AND
# THE FIRST CUT SHIPPED WITHOUT THIS CHECK.  `_VERB.search` returns the FIRST
# finite verb, which is the main verb only when nothing has opened an embedded
# clause before it.  Measured on the corpus: "Let me check whether the store
# **is** ..." yielded the subject «let me check whether the store», and "Worth
# knowing before the run: --holes **is** ..." yielded the whole preamble.  Both
# are fragments whose real predication sits inside a complement, so the span
# before the verb is not a subject at all -- it is a clause the extractor
# mistook for one, and posting it inflates fan-in on exactly the strings that
# refer to nothing.  A candidate carrying any of these is REFUSED rather than
# trimmed: trimming would guess where the embedded clause began, and a guessed
# subject is worse than a declared gap (`--gaps` counts them).
_EMBED = re.compile(r"[:;]|\b(?:that|whether|if|because|since|while|when|"
                    r"where|which|who|how|why|although|unless|after|before|"
                    r"let|see)\b", re.I)

# ⚑ FIRST PERSON IS NOT A REFERENT THAT TOOL OUTPUT CAN SUPERSEDE.  A claim
# whose subject is the actor ("I was wrong", "my own queries") is a claim about
# the speaker, not about a thing in the world whose state a later measurement
# can revise -- which is precisely the EVIDENCE-SUPERSESSION class this module
# exists to key.  Excluded here rather than in SUBJECT_STOP because the test is
# on the HEAD of the phrase, not on the whole string: «my own queries» must go
# for the same reason «i» must, and a stoplist cannot enumerate the possessive
# forms.
_FIRST_PERSON = re.compile(r"^(?:i|we|my|our|me|us|you|your)\b", re.I)

# ⚑ A SUBJECT THAT IS A BARE DISCOURSE CONNECTIVE OR A META-NOUN IS NOT A
# REFERENT.  Kept SMALL and named, for the reason `ARTEFACT_STOP` states: a
# large stoplist is a tuning constant pretending to be a fact.
SUBJECT_STOP = {
    "there", "here", "what", "which", "who", "why", "how", "let", "let me",
    "one", "some", "both", "each", "either", "neither", "something",
    "nothing", "everything", "anything", "the answer", "the question",
    "the result", "the point", "the reason", "the problem", "the issue",
    "the thing", "the case", "the same", "the rest", "the following",
}


def _clean(raw):
    """A candidate subject string -> its normalised head, or None."""
    s = _DECOR.sub("", raw)
    s = _STRIP.sub("", s).strip(" ,;:-—")
    s = _WS.sub(" ", s).lower()
    if not s:
        return None
    # A subject longer than a handful of words is a clause, not a referent.
    if len(s.split()) > 6:
        return None
    return s


def subject_of(sentence):
    """The subject noun phrase of one sentence, or None.

    ⚑ THE VERB IS THE DELIMITER AND ITS ABSENCE IS A REFUSAL, NOT A FALLBACK.
    A fragment with no finite verb ("Let me read it", a heading, a bullet) is
    not an assertion, so it has no claim subject.  Returning the whole fragment
    as a "subject" would post junk into the list and inflate fan-in on exactly
    the strings that mean least -- the shape `census-green-is-a-fact-about-the-
    census` names, one layer down.
    """
    m = _VERB.search(sentence)
    if not m or m.start() == 0:
        return None
    head = sentence[:m.start()]
    if _EMBED.search(head):
        return None
    s = _clean(head)
    if s is None or _FIRST_PERSON.match(s):
        return None
    return s


def claims(units):
    """[(turn, subject, inherited_from)] over actor prose, in turn order.

    `inherited_from` is None for a named subject and the donor turn for a
    pronoun resolved positionally.
    """
    out = []
    last_named = None            # (turn, subject) -- the pronoun antecedent
    for turn, role, _body, prose in units:
        if role == "human" or not prose.strip():
            continue
        for m in _SENT.finditer(prose):
            subj = subject_of(m.group(1))
            if not subj:
                continue
            bare = _DET.sub("", subj)
            if subj in SUBJECT_STOP or bare in SUBJECT_STOP:
                continue
            if bare in PRONOUNS or subj in PRONOUNS:
                # ⚑ POSITIONAL RESOLUTION, AND IT DECLARES ITS DONOR.  A
                # pronoun inherits the nearest preceding NAMED subject.  It is
                # recorded with that donor turn so `--subjects` can be read as a
                # falsifiable claim rather than an opaque expansion.
                if last_named is not None:
                    dturn, dsubj = last_named
                    out.append((turn, dsubj, dturn))
                continue
            out.append((turn, subj, None))
            last_named = (turn, subj)
    return out


def posting(units):
    """subject -> [turns], the actor-claim posting list.  The deliverable."""
    post = collections.defaultdict(list)
    for turn, subj, _inh in claims(units):
        if turn not in post[subj]:
            post[subj].append(turn)
    return post


def build_links(units):
    """Backlinks this probe alone emits: a cued actor turn -> earlier claims
    predicating over the same subject.

    ⚑ THE CUE SET IS `tmi_status`'s AND IS NOT RE-DERIVED HERE.  This module is
    the RECURRENCE conjunct only -- `tmi-F17` is explicit that the cue is not
    the failure -- so importing `cue_hits` rather than restating it keeps ONE
    authority for "is this a revision at all".
    """
    post = collections.defaultdict(list)
    by_turn_subjects = collections.defaultdict(set)
    for turn, subj, _inh in claims(units):
        by_turn_subjects[turn].add(subj)
    n_units = len(units)
    # fan-in is computed over the WHOLE corpus, so the cuts are stable rather
    # than depending on how far the scan has got (`reread-meters-toctou`).
    whole = posting(units)
    head = max(3, SUBJECT_DF_FRAC * n_units)
    links = []
    for turn, role, text, prose in units:
        if role == "human":
            continue
        hits = S.cue_hits(text, prose)
        if not hits:
            for s in by_turn_subjects.get(turn, ()):
                post[s].append(turn)
            continue
        back = set()
        cands = []
        for s in by_turn_subjects.get(turn, ()):
            prevs = [p for p in whole[s] if p < turn]
            if not prevs:
                continue
            df = len(set(whole[s]))
            if df < SUBJECT_DF_MIN or df > head:
                continue
            # rarest first, then nearest -- the Ⓘ8 reading, unchanged
            cands.append((df, turn - max(prevs), max(prevs), s))
        for _df, _d, prev, s in sorted(cands)[:3]:
            back.add((prev, s))
        if back:
            links.append((turn, sorted(back), sorted({c for c, _ in hits})))
        for s in by_turn_subjects.get(turn, ()):
            post[s].append(turn)
    return links


# ---------------------------------------------------------------------------
def _units(path):
    return S.load_units(path)


def _hdr(path, units, n_env):
    print("units: %d of %d envelopes  (%s)" % (len(units), n_env, path))


def cmd_subjects(path, limit=None):
    units, n_env = _units(path)
    _hdr(path, units, n_env)
    rows = claims(units)
    shown = rows[:limit] if limit else rows
    for turn, subj, inh in shown:
        tag = ("  ← inherited from turn %d" % inh) if inh else ""
        print("  [%4d] «%s»%s" % (turn, subj, tag))
    n_inh = sum(1 for _t, _s, i in rows if i is not None)
    print("claims: %d of %d actor unit(s); %d subject(s) resolved from a pronoun"
          % (len(rows), sum(1 for u in units if u[1] != "human"), n_inh))


def cmd_posting(path, min_fanin=SUBJECT_DF_MIN):
    units, n_env = _units(path)
    _hdr(path, units, n_env)
    post = posting(units)
    rows = sorted(((len(set(v)), k) for k, v in post.items()), reverse=True)
    kept = [(n, k) for n, k in rows if n >= min_fanin]
    for n, k in kept[:40]:
        print("  %4d turns  %s" % (n, k))
    print("subjects with fan-in >= %d: %d of %d"
          % (min_fanin, len(kept), len(rows)))


def cmd_links(path):
    units, n_env = _units(path)
    _hdr(path, units, n_env)
    links = build_links(units)
    for turn, back, classes in links:
        print("  LINK turn %4d  cues=%s" % (turn, ",".join(classes)))
        for prev, s in back:
            print("         <-- turn %4d  via subject «%s»" % (prev, s))
    print("links: %d of %d units" % (len(links), len(units)))


def cmd_gaps(path):
    """Actor claims the probe cannot key -- reported, never hidden.

    ⚑ A NAMED RESIDUE IS THE DIFFERENCE BETWEEN A BOUNDED INSTRUMENT AND A
    SILENT ONE, which is the discipline `tmi_index --gaps` already applies one
    layer up.  A turn whose every sentence is a fragment (a heading, a "Let me
    ..." bridge) contributes nothing to the posting list, and a reader is
    entitled to know how much of the corpus that is.
    """
    units, n_env = _units(path)
    _hdr(path, units, n_env)
    keyed = {t for t, _s, _i in claims(units)}
    missing = [(t, " ".join(p.split())[:90])
               for t, r, _b, p in units
               if r != "human" and p.strip() and t not in keyed]
    for t, snip in missing[:30]:
        print("  [%4d] %s" % (t, snip))
    n_actor_prose = sum(1 for _t, r, _b, p in units
                        if r != "human" and p.strip())
    print("unkeyed: %d of %d actor-prose unit(s) yield no claim subject"
          % (len(missing), n_actor_prose))


def selftest():
    fails = []

    ran = []

    def chk(name, cond):
        print(("  ok   " if cond else "  FAIL ") + name)
        ran.append(name)
        if not cond:
            fails.append(name)

    # (i) a subject is the NP before the finite verb
    chk("named subject", subject_of("Shard 0 is gone — no process.")
        == "shard 0")
    chk("determiner kept in the key",
        subject_of("The fold has not written a step line.") == "the fold")
    # (ii) a fragment with no finite verb is NOT a claim
    chk("no verb, no subject", subject_of("Let me read it") is None)
    chk("verb-initial is not a subject",
        subject_of("Is the fold alive?") is None)
    # (iii) the stoplist rejects meta-nouns
    chk("meta-noun stopped", "the answer" in SUBJECT_STOP)
    # (iv) a clause is not a referent
    chk("long clause refused",
        subject_of("Everything that the fold wrote before the crash last "
                   "night in the other tenant is gone") is None)
    # (v) the cuts do not overlap and the head cut is looser than the artefact's
    chk("df frac is a fraction", 0 < SUBJECT_DF_FRAC < 1)
    chk("subject cut looser than artefact cut",
        SUBJECT_DF_FRAC > S.ARTEFACT_DF_FRAC)
    chk("tail cut rejects fan-in 1", SUBJECT_DF_MIN == 2)

    # (vi) PRONOUN RESOLUTION, and it must DECLARE its donor.
    fake = [(10, "assistant", "", "Shard 0 is gone."),
            (11, "assistant", "", "It is slow.")]
    rows = claims(fake)
    chk("pronoun inherits the named subject",
        (11, "shard 0", 10) in rows)
    chk("first-person is not a referent",
        not [r for r in claims([(1, "assistant", "", "I was wrong.")])])

    # (vii) END-TO-END on the real corpus, and ⚑⚑ THE ASSERTION HAD TO BE
    # REWRITTEN WHEN THE FIRST ONE FAILED, BECAUSE THE FIRST ONE ENCODED
    # `tmi-F17`'s CLAIM RATHER THAN A MEASUREMENT.  It asserted that turns 632
    # and 649 would emit links once this probe existed, on the strength of
    # `tmi-F17`'s sentence "the CUE fires on these (209/632/649 all carry
    # contrast frames); the failing conjunct is the RECURRENCE PROBE".  Both
    # halves of that are wrong on this corpus:
    #
    #   * turn 632's prose is "Shard 0 is **gone** — no process. It exited
    #     without writing a step line..." -- there is no contrast frame, no
    #     concession, no explicit retraction and no self-quotation in it.  It
    #     carries NO CUE, so no recurrence probe can ever emit a link from it.
    #   * `tmi_status --score --ablate` settles it corpus-wide: CUE-ONLY recall
    #     is 34/39, identical to artefact recurrence.  The recurrence conjunct
    #     costs ZERO recall.  The five misses are missed by the CUE SET.
    #
    # So `tmi-F17` named the wrong conjunct, and the ablation that refutes it
    # was already in the tool when it was filed.  What this probe actually buys
    # is on the ANTECEDENT side, which is the half `tmi_status`'s own ablation
    # note says matters -- and it does buy it: the evidence-supersession PAIR
    # 638 <- 632 via «shard 0» is emitted here and by no other mode, because
    # `shard 0` is a subject with fan-in 7 and is not an artefact at all.
    # THAT is the assertion, and it is a measurement rather than a restatement.
    if os.path.exists(DEFAULT_TRANSCRIPT):
        u, _n = _units(DEFAULT_TRANSCRIPT)
        lk = build_links(u)
        pairs = {(t, p) for t, back, _c in lk for p, _s in back}
        chk("the evidence-supersession pair 638<-632 is carried",
            (638, 632) in pairs)
        chk("632 carries no cue, so it cannot be a reviser",
            not S.cue_hits(*[x for x in
                             [(b, p) for t, _r, b, p in u if t == 632][0]]))
        post = posting(u)
        chk("`shard 0` is a subject the artefact index cannot see",
            len(set(post.get("shard 0", ()))) >= 2
            and "shard 0" not in S.artefacts("shard 0"))
        chk("posting list is non-trivial", len(post) > 50)
    else:
        print("  skip  corpus absent: end-to-end checks not run")

    # ⚑⚑ SILENT TO THE RUNNER UNTIL 2026-08-25, AND THE DENOMINATOR WAS A LITERAL.
    # Two defects in one line, and the second is the one with teeth:
    #
    #  (1) `selftest: %d of %d check(s) failed` matches neither the typed `#row` nor
    #      `run_selftests`' fallback regex `selftest:\s*(\d+)\s*/\s*(\d+)` — it is
    #      `N of M`, and it counts FAILURES where the regex reads PASSES, so even a
    #      shape-compatible reader would have inverted it. The suite classified
    #      `silent`: 15 green cases, none read. Siblings `tmi_status.py` (51) and
    #      `tmi_index.py` (33) were silent for the same reason.
    #
    #  (2) THE TOTAL WAS THE HARDCODED CONSTANT `15`, which is exactly the defect
    #      `rungs.Cases.report`'s own ⚑ records: *"`N/M` IS DERIVED, NEVER LITERAL —
    #      `prune_imports` once carried a hardcoded `9/9` that hid a tenth case"*.
    #      Here it hid a CONDITIONAL BRANCH: four of the fifteen only run when
    #      `DEFAULT_TRANSCRIPT` exists, and with the corpus absent the suite took the
    #      `skip` path, ran ELEVEN cases and still reported a denominator of 15. A
    #      case that ran and a case that was counted could come apart, which is the
    #      one thing a denominator exists to prevent.
    #
    # `ran` now counts registrations, so the total is what `chk` actually saw. This
    # also makes the reach ratchet's two lenses meaningful for this suite: the static
    # count is 15 call sites, the run count is now honestly 11 or 15 depending on the
    # corpus, and the DIFFERENCE is a real fact about the environment instead of a
    # constant asserting it away.
    try:
        import rungs as _rungs
        _rungs.emit_record(len(ran) - len(fails), len(ran),
                           key="scratch/tmi_subject.py")
    except ImportError:
        print("  ⚑ rungs unavailable — no typed record emitted")
    print("selftest: %d of %d check(s) failed" % (len(fails), len(ran)))
    return 1 if fails else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else DEFAULT_TRANSCRIPT
    if not os.path.exists(path):
        print("tmi_subject.py: no such transcript: %s" % path, file=sys.stderr)
        return 2

    def opt(flag, default=None, cast=int):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 < len(argv):
                return cast(argv[i + 1])
        return default

    if "--subjects" in argv:
        cmd_subjects(path, opt("--limit"))
    elif "--posting" in argv:
        cmd_posting(path, opt("--min-fanin", SUBJECT_DF_MIN))
    elif "--links" in argv:
        cmd_links(path)
    elif "--gaps" in argv:
        cmd_gaps(path)
    else:
        print(__doc__.rstrip())
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
