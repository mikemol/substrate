#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""climode.py — THE declaration shape for a CLI mode, shared across the tool corpus.

⚑⚑ THE STANDARD, AND WHY IT IS ONE (operator, 2026-08-23: *"that farm.py-inspired model
is THE INTENDED, SHOULD-BE-STANDARDIZED shape"*).  A tool's modes were declared five
different ways — a module docstring, an argparse `options:` block, a `_MODES` tuple of
`(flag, gloss)` pairs, a usage string printed from inside `__main__`, and this.  Five
shapes means five things a reader must know to ask "what modes does this tool have", and
`toolmodes` had to learn all five before it could answer.  Consistency IS the deliverable;
the extra fields are what make consistency worth having.

⚑ THE MODEL IS `Arm(key, file, find, replace, expect, why)` FROM GCALCULUS `farm.py`, and
its load-bearing property is that **the declared field is one a discriminator can CHECK**.
An `Arm` names the message its mutation must provoke, so an Arm that stops biting is
VACUOUS and detectably so.  A `Mode` declares that its branch consumes `scan()` and
therefore owes an incomplete-scan report — and `check_mode_contracts.py` (pre-commit gate,
Phase A) runs the discriminator.  A mode claiming a contract it does not honour is a GATE
FAILURE, not a code-review note.

⚑ WHY IT LIVES IN `scripts/` AND NOT WHERE IT WAS BORN.  `Mode` grew inside
`scratch/pycodemod.py`, but the four `_MODES` rosters awaiting conversion
(`schema.py`, `lifecycle.py`, `reconstruct.py`, `jea_pydecode.py`) are all in
`jea/metalanguage/` — the PROMOTED side.  Importing from `scratch/` there would add an
8th runtime coupling to `check_scratch_independence` (Λ8), which is already red at 7 and
whose refusal text says to fix it by PROMOTING the module, never by repathing.
`scripts/` is the established home for machinery both sides consume: `scripts/ratchet.py`
is imported by all 16 ratchet gates the same way.

⚑ WHAT THIS MODULE DELIBERATELY DOES NOT DO.  It does not parse argv, dispatch, or print
usage.  A declaration that also executed would be satisfied by its own execution — the
same reason `Mode.scans` is declared rather than inferred (see below).  Tools keep their
own dispatch; what they share is the SHAPE of the claim they make about it.
"""

import re


class Mode:
    """One CLI mode's argument shape AND the reporting contracts it owes.

    Fields, and which are checkable by what:

      operand  the token the flag itself consumes (None = nullary).  DERIVABLE from the
               dispatch, and `pycodemod --declare-modes` derives it — the one field a
               migration can fill in mechanically.
      paths    the mode also takes a trailing path population.
      opts     the modifier flags THIS mode accepts, so a modifier is owned by one mode
               rather than being globally true.
      scans    the verdict rests on a corpus `scan()`, so the branch MUST report what it
               could not read.  Checked by `scan_contract`.
      writes   WHICH ARTIFACT KINDS this mode mutates — a tuple of keys from the
               `struct-tools` artifact table (`.py`, `.md`, `.bib`, `.agda`, `store`, …),
               empty for a pure read.  Checked against the `--apply`/`--dry-run` refusal
               convention.
      why      the `Arm.why` field, in the reader's words.

    ⚑⚑ `scans` AND `writes` ARE DECLARED, NEVER INFERRED, AND THAT IS THE WHOLE DESIGN.
    A contract read out of the body would be satisfied BY the body by construction: it
    could never fail, so it could never find anything.  The derivers (`modes()`,
    `argopt_flags()`) can only report the spellings they already know, which is exactly
    what made them incomplete — a flag absent from a declaration is absent VISIBLY, and
    the gate says so.

    ⚑ WHAT A MISSING DECLARATION COSTS, MEASURED.  The entry point resolves operand arity
    from the roster, so an undeclared mode makes the arg-stripper guess: `--key --archive
    f.py` CRASHED because `--key`'s operand was bound as a tarball path.  The other
    direction is worse — a DECLARED-but-never-dispatched row is a promise the CLI does not
    keep and still feeds arity resolution.
    """

    __slots__ = ("operand", "paths", "opts", "scans", "writes", "why")

    def __init__(self, operand=None, paths=False, opts=(), scans=False, writes=(), why=""):
        self.operand = operand
        self.paths = paths
        self.opts = tuple(opts)
        self.scans = scans
        #: ⚑⚑ A BOOLEAN CANNOT SAY THIS, AND THE DIFFERENCE IS THE WHOLE POINT
        #: (operator, 2026-08-23): *"it matters WHAT you're mutating; a tool might read
        #: two things and only mutate one of them."*  `toolmodes --sync` reads every
        #: tool's output and writes ONE markdown block; `sppf_db --project-core` reads
        #: `.agdai` and writes the STORE.  `mutates=True` collapses both into one
        #: undifferentiated bit — unrankable, and the shape `--fingerprint` exists to
        #: give structure to.
        #:
        #: ⚑ AND IT IS CHECKABLE, WHICH IS WHAT MAKES IT A DECLARATION.  The kinds are
        #: not invented here: they are keys of the artifact→tool table that
        #: `hook_structural_query.routes()` already parses and the claims gate already
        #: enforces.  A mode declaring it writes `.md` inside a tool that claims no
        #: `.md` artifact is a DETECTABLE LIE.
        self.writes = tuple(writes)
        self.why = why

    @property
    def mutates(self):
        """Does this mode write anything at all?  DERIVED from `writes`, never stored.

        ⚑ THE BOOLEAN IS A PROJECTION OF THE TARGET SET, NOT A PEER FIELD.  Storing both
        would be two spellings of one fact that can disagree — `census-keyed-on-one-
        spelling`.  Ask `writes` for WHAT; ask this for WHETHER, and they cannot drift.
        """
        return bool(self.writes)

    def __repr__(self):
        bits = []
        if self.operand:
            bits.append("operand=%r" % self.operand)
        if self.paths:
            bits.append("paths=True")
        if self.opts:
            bits.append("opts=%r" % (self.opts,))
        if self.scans:
            bits.append("scans=True")
        if self.writes:
            bits.append("writes=%r" % (self.writes,))
        return "Mode(%s)" % ", ".join(bits)


def split_flag(spelling):
    """`"--sample REL [N]"` -> `("--sample", "REL [N]")`; `"--census"` -> `("--census", None)`.

    ⚑⚑ THE TUPLE ROSTERS ENCODE ARITY IN THE FLAG STRING, AND A NAIVE LIFT DROPS IT.
    `_MODES` entries are written `("--core PATH", "…")` — the operand is real, declared,
    and carried in PROSE inside the key.  A `{flag: Mode(why=gloss)}` comprehension would
    have produced a roster whose keys are `"--core PATH"` (matching no argv token) and
    whose arity is silently `None`.  That is a MIGRATION THAT LOSES A FIELD THE OLD SHAPE
    HAPPENED TO CARRY — the failure mode worth more than the one it fixes, because the
    new shape then reads as authoritative about arity it never learned.

    ⚑ SO THE PROSE IS PARSED, NOT DISCARDED.  Everything after the first space is the
    operand spelling, kept verbatim (`"REL [N]"`, `"{--dry-run|--apply}"`) rather than
    normalised to a name — the spelling is what a reader needs, and inventing a canonical
    form here would be a second authority over what the dispatch already accepts.
    """
    spelling = spelling.strip()
    if " " not in spelling:
        return spelling, None
    flag, operand = spelling.split(" ", 1)
    return flag, operand.strip() or None


#: The roster key for a tool's POSITIONAL invocation — no flag at all.
#: ⚑⚑ A POSITIONAL IS A DECLARATION, NOT A FLAG, AND THE LIFT MUST NOT PRETEND OTHERWISE.
#: `jea_pydecode`'s roster declares `("<file.py>", "the cores this file would produce")` —
#: its PRIMARY invocation, which takes no flag. Passed through `split_flag` that becomes a
#: key `"<file.py>"` matching no argv token, and `contract_rows` would then report it as
#: DECLARED-never-dispatched: a FALSE FINDING manufactured by the migration, in the gate
#: built to find real ones. `--conventions` already counts `(positional)` across 28 tools,
#: so this is a shape the corpus has, not an oddity of one file.
POSITIONAL = "(positional)"


def from_pairs(pairs):
    """[(spelling, gloss)] -> {flag: Mode(operand=…, why=gloss)} — the tuple-roster lift.

    ⚑ THE MIGRATION PATH FOR THE FOUR TUPLE ROSTERS, AND IT IS DELIBERATELY LOSSY UPWARD.
    A `(spelling, gloss)` pair carries two of `Mode`'s six fields — `operand` (via
    `split_flag`) and `why` — so this fills those and leaves the rest at their defaults.
    Those defaults are CLAIMS the gate will hold the tool to: `scans=False` says "this
    mode's verdict does not rest on a scan", `writes=()` says "this mode mutates nothing",
    and if either is wrong the discriminator says so.

    ⚑ SO THIS IS A STARTING POINT, NOT A CONVERSION.  A roster lifted through here and
    never revisited has traded five shapes for one — which is the point, and consistency
    is the deliverable — but has not yet declared anything the old shape could not.  The
    gate is what turns the second half from optional into owed.
    """
    out = {}
    for spelling, gloss in pairs:
        spelling = spelling.strip()
        # ⚑ A NON-FLAG ENTRY IS THE POSITIONAL INVOCATION — keyed apart so it is never
        # compared against argv as if it were a flag. See `POSITIONAL`.
        if not spelling.startswith("-"):
            out[POSITIONAL] = Mode(operand=spelling, paths=True, why=gloss)
            continue
        flag, operand = split_flag(spelling)
        out[flag] = Mode(operand=operand, why=gloss)
    return out


#: The three states a tool can be in with respect to `--selftest`, as a CLOSED set.
#: ⚑⚑ THE WHOLE POINT IS THAT THERE ARE THREE, NOT ONE SILENCE (⟡selftest-record,
#: gate-F7). `run_selftests.discover()` answers ONE question — is this file in the
#: roster — so a tool with no suite and a tool that is a deliberate failing fixture
#: are both simply ABSENT from a 96-row list, indistinguishable from each other and
#: from a tool nobody has looked at. MEASURED 2026-08-24: a standing instruction to
#: "run the selftest after you change it" was issued for `fix_notinscope.py` and
#: `check_mode_contracts.py`, NEITHER of which has one — a NON-COMMAND, and the
#: reason it could be issued is that absence had no reader.
SELFTEST_STATES = ("suite", "fixture", "none")


class Selftest:
    """One tool's `--selftest` DECLARATION — the `Mode` move, one layer over.

    ⚑⚑⚑ THE MODEL IS THE SAME ONE `Mode` ALREADY SETTLED, AND IT IS DELIBERATELY NOT A
    FORK (operator, 2026-08-24: *"our --selftest framework needs to be standardized,
    too. Preferably using the same approach as farm.py."*). `Arm(key, file, find,
    replace, expect, why)` from gcalculus `farm.py` → `Mode(operand, paths, opts, scans,
    writes, why)` → this. The load-bearing property carries through unchanged: **every
    declared field is one a discriminator can CHECK**, so a declaration that stops being
    true is detectable rather than merely stale.

    Fields:

      state    one of `SELFTEST_STATES` — the distinction that does not exist today.
               `suite`   — `python <tool> --selftest` produces a verdict record.
               `fixture` — the flag dispatches and is MEANT to fail (a positive control
                           for the runner itself). `sppf_db --selftest-demo-failure` is
                           the canonical one, and the `toolmodes:fixture` marker is the
                           same distinction already proven in the divergence census.
               `none`    — this tool HAS no selftest, DECLARED. ⚑ This is the state the
                           whole record exists for: it converts an absence that reads as
                           an oversight into a claim someone made, which a gate can then
                           hold to a reason.
      why      for `none`, WHY there is none — the field that makes the state a claim
               rather than a shrug. Required for `none`, checked by `contract`.
      key      the `rungs.emit_record` key a `suite` reports under, when it differs from
               the tool's own path (a decomposed tool reports under its PARENT).
      requires the packages the suite declares it needs (`# selftest-requires:`), so the
               runner can supply them. DECLARED here as well as in the comment because
               the comment is the runner's input and this is the reader's.
      tenant   `sandbox` / `live` / None — which store tenant the suite must resolve.

    ⚑ WHY `none` IS A STATE AND NOT AN ABSENT KEY. An absent declaration and a declared
    `none` look identical to a `dict.get`, which is precisely the collapse `SELFTEST_STATES`
    exists to break — the same reason `Mode.scans` is declared rather than inferred. A tool
    with no record at all is UNDECLARED (nobody has looked); a tool declaring `none` has
    been looked at and found to need none. Those need different next actions, and one
    silence cannot carry both.

    ⚑ AND THIS DECLARES, IT DOES NOT DISPATCH — the same boundary `climode`'s own docstring
    draws. `run_selftests` keeps discovery and invocation. What is shared is the SHAPE of
    the claim, so a discriminator can be written once instead of per tool.

    ⚑⚑ `runs_roster` IS THE FIELD THE FORK BOMB NEEDED AND NOBODY COULD WRITE. A suite
    that itself invokes `run_selftests` is a legitimate thing to want — `worklist_gate`
    wants to know the selftests pass — and it is ALSO the edge that closes the cycle. With
    membership decided by convention there was nowhere to say it, so the roster contained
    its own caller and no reader could see that from any source file. Declared, it is a
    STATIC refusal (`self_including`) rather than a runtime ppid skip.
    """

    __slots__ = ("state", "why", "key", "requires", "tenant", "runs_roster")

    def __init__(
        self, state="suite", why="", key=None, requires=(), tenant=None, runs_roster=False
    ):
        if state not in SELFTEST_STATES:
            # ⚑ REFUSED AT CONSTRUCTION, never normalised to a default. A typo'd state
            # silently becoming `suite` would put a tool in the roster that has no suite,
            # and the runner would report it SILENT — a defect manufactured by the
            # declaration built to prevent one. Same rule as `_tenant`'s regex admitting
            # only the two spellings it knows.
            raise ValueError(
                "Selftest(state=%r) — not one of %s. A state is a closed set: an "
                "unrecognised value must refuse, never default." % (state, SELFTEST_STATES)
            )
        self.state = state
        self.why = why
        self.key = key
        self.requires = tuple(requires)
        self.tenant = tenant
        self.runs_roster = bool(runs_roster)

    @property
    def runnable(self):
        """Should `run_selftests` INVOKE this tool? DERIVED from `state`, never stored.

        ⚑ THE BOOLEAN IS A PROJECTION OF THE STATE, the same relation `Mode.mutates` has
        to `Mode.writes`. Storing both would be two spellings of one fact that can
        disagree — `census-keyed-on-one-spelling`, which this corpus has already paid for
        twice inside the readers written to find spelling disagreements.
        """
        return self.state == "suite"

    def contract(self):
        """`(ok, why)` — hold THIS declaration to its own fields. The discriminator.

        ⚑ A DECLARATION NOBODY CHECKS IS A COMMENT WITH A CONSTRUCTOR AROUND IT. `Mode`'s
        fields are checked by `contract_rows` against the dispatch; these are checked
        against each other, because the disagreement they admit is internal: a `none` with
        no reason is the shrug the record exists to replace, and a `fixture` or `suite`
        carrying a `none`-style excuse is a state that contradicts its own field.
        """
        if self.state == "none" and not self.why.strip():
            return False, (
                "declares state='none' with no `why` — an undeclared absence "
                "with a constructor around it. Name the reason this tool needs "
                "no suite, or declare the state it actually has."
            )
        # ⚑ A `key` ON A NON-SUITE IS A PROMISE NOTHING KEEPS. Only a `suite` emits a
        # record, so a key elsewhere would read as wired while nothing ever reports under
        # it — the `rewire_only` shape (1 def, 0 calls) in declaration form.
        if self.key and self.state != "suite":
            return False, (
                "declares a record `key` but state=%r — only a `suite` emits a "
                "record, so this key names a report nobody writes" % self.state
            )
        # ⚑ SAME FOR `requires` / `tenant`: both are instructions to the RUNNER about how
        # to invoke a suite. Declared on a tool the runner will not invoke, they are
        # configuration for a call that never happens.
        for _f, _v in (("requires", self.requires), ("tenant", self.tenant)):
            if _v and self.state != "suite":
                return False, (
                    "declares `%s` but state=%r — that field instructs the "
                    "runner how to INVOKE a suite, and this tool is never "
                    "invoked" % (_f, self.state)
                )
        # ⚑ `runs_roster` ON A NON-SUITE IS THE SAME SHAPE, and it is the one that matters
        # most: a tool that will never be invoked cannot close a cycle, so declaring the
        # edge there is a claim with no referent — and `self_including` would then name a
        # tool no roster runs, which is a FALSE FINDING out of the reader built to prevent
        # the fork bomb.
        if self.runs_roster and self.state != "suite":
            return False, (
                "declares runs_roster but state=%r — only an invoked suite can "
                "close the roster cycle, so this edge has no referent" % self.state
            )
        return True, ""

    def __repr__(self):
        bits = ["state=%r" % self.state]
        for f in ("key", "requires", "tenant", "runs_roster"):
            v = getattr(self, f)
            if v:
                bits.append("%s=%r" % (f, v))
        return "Selftest(%s)" % ", ".join(bits)


def selftest_rows(declared, discovered):
    """[(tool, state, ok, why)] — the DECLARED roster against what discovery FOUND.

    ⚑⚑⚑ THIS IS THE READER `run_selftests` COULD NOT HAVE, and its absence is what
    admitted the fork bomb. Discovery answers "is this file in the roster"; it cannot
    answer "should it be", so a member that invokes the roster is indistinguishable from
    any other member — membership-by-convention, with no place to state an intent that
    contradicts it. Declared state and discovered membership are two independent
    readings, and every disagreement between them is a finding:

      DECLARED suite, NOT discovered   — the declaration promises a suite the runner
                                         cannot reach (no dispatch, or an unreadable file)
      DISCOVERED, DECLARED none        — the tool says it has no suite and the runner is
                                         running one anyway
      DISCOVERED, DECLARED fixture     — a deliberate failure is in the roster, so the
                                         gate is red by design. The fixture must be
                                         invoked BY the runner's own suite, never AS a
                                         member of the roster.
      neither                          — UNDECLARED. Not a failure: the census's own
                                         boundary, reported as such.

    ⚑ AND `undeclared` IS REPORTED, NOT OMITTED. A row-set that lists only disagreements
    cannot distinguish "every tool is declared and consistent" from "nothing is declared
    yet", which is `census-green-is-a-fact-about-the-census` — a false ZERO gets banked
    while a false positive gets investigated. The paydown population has to be visible.
    """
    out = []
    disc = set(discovered)
    for tool in sorted(set(declared) | disc):
        st = declared.get(tool)
        if st is None:
            out.append(
                (
                    tool,
                    "undeclared",
                    None,
                    "in the discovered roster with no Selftest declaration"
                    if tool in disc
                    else "declared nowhere and not discovered",
                )
            )
            continue
        ok, why = st.contract()
        if not ok:
            out.append((tool, st.state, False, why))
            continue
        if st.state == "suite" and tool not in disc:
            out.append(
                (
                    tool,
                    st.state,
                    False,
                    "DECLARED a suite, but discovery cannot reach it — no `--selftest` "
                    "dispatch the runner recognises, or the file is unreadable",
                )
            )
        elif st.state == "none" and tool in disc:
            out.append(
                (
                    tool,
                    st.state,
                    False,
                    "DECLARED state='none', but discovery found a suite and the runner "
                    "is invoking it — the declaration and the tree disagree",
                )
            )
        elif st.state == "fixture" and tool in disc:
            out.append(
                (
                    tool,
                    st.state,
                    False,
                    "a FIXTURE is in the roster — it is MEANT to fail, so the gate is "
                    "red by design. A fixture is invoked BY the runner's own suite as a "
                    "positive control, never AS a member of the roster",
                )
            )
        else:
            out.append((tool, st.state, True, ""))
    return out


def self_including(declared, roster_marker):
    """[tool] whose declaration says its suite RUNS THE ROSTER — refusable STATICALLY.

    `roster_marker` is the roster tool's OWN key (`scripts/run_selftests.py`), excluded
    because it legitimately runs the roster — that is what it IS. ⚑ Excluding it by NAME
    rather than by a flag on the record keeps the exemption in the READER, where a caller
    passing a different roster gets a different exemption, instead of minting a field a
    second tool could set to exempt itself.

    ⚑⚑⚑ ⟡worklist-gate-recursion, THE STATIC HALF. The live fix is a ppid walk
    (`ratchet.check_cycle`), which is the right instrument for the general case — it reads
    what ACTUALLY happened rather than what something agreed to declare — but it refuses
    only AFTER a generation has forked, and only at runtime. MEASURED: six generations,
    load 54.93, 68 concurrent selftest processes on a 10-core box.

    ⚑ A DECLARATION CAN REFUSE THE SAME EDGE BEFORE ANYTHING FORKS, and the two are not
    redundant for the reason both ENDS of the ppid guard are not redundant. `runs_roster`
    is a claim a tool makes about its own suite; this reads the claims and names every
    tool whose suite invokes the roster that contains it. That is a commit-time finding
    against a source file, not a runtime skip against a process tree.

    ⚑ AND IT CANNOT REPLACE THE PPID WALK, WHICH IS WHY BOTH SHIP. A declaration governs
    only the tools that made one — an undeclared tool, or one whose suite grows a roster
    call tomorrow, is invisible here and caught only by the walk. Naming this "the fix"
    would be the census-green error: a fact about the declared population reported as a
    fact about the process tree.
    """
    return sorted(t for t, st in declared.items() if st.runs_roster and t != roster_marker)


def branch_bounds(src):
    """{flag: (start_line, end_line)} — where each mode's dispatch branch sits.

    ⚑⚑ MATCHES ANY `argv`-ISH RECEIVER, AND THAT BREADTH IS A SCAR.  A branch is written
    `if "--x" in sys.argv:` or `if "--x" in flagged_argv():` — the latter a POSIX-`--`-aware
    accessor.  A reader keyed on `sys.argv` alone reported `--reifies` as
    `UNK branch not located` while it was discharging its contract correctly, and the FIX
    for an earlier instance of the same bug ALSO keyed on one spelling and missed the other.
    `census-keyed-on-one-spelling`, twice, inside the reader written to find spelling
    disagreements.  So: match any `in <something>argv…` receiver.

    ⚑⚑ A BRANCH ENDS WHERE ITS INDENTATION DOES, NOT WHERE THE NEXT MATCH BEGINS — AND
    THE NAIVE RULE WAS A MEASURED FALSE POSITIVE ON A REAL FILE.  `schema.py:424` opens
    `if "--coverage" in sys.argv:` and NESTS `--emit` (425) and `--reap` (427) inside it.
    Under next-match bounding, `--coverage`'s body ended at 425, so the `--apply` test its
    `--reap` sub-branch performs at 430 — with an explicit comment saying neither flag may
    default — fell OUTSIDE, and the gate reported a correctly-guarded mutator as a
    silent-default writer.  A false accusation against a compliant tool is the one failure
    a gate must not make, because the fix it demands is to break a working refusal.

    ⚑ SO NESTED SUB-FLAGS ARE NO LONGER SIBLINGS.  A match indented deeper than an open
    branch belongs to it.  Two consequences worth stating: a nested flag is still recorded
    (a reader asking where `--reap` lives gets an answer), and a mode's body now correctly
    includes its own sub-dispatch, which is where the `--apply` guard usually sits.
    """
    lines = src.splitlines()
    starts, order = {}, []
    for i, line in enumerate(lines):
        # ⚑ `[\w.]*` — THE DOT IS LOAD-BEARING. `sys.argv` is the commonest receiver of
        # all and a `\w*argv` pattern does not match it; my first cut located only the
        # `flagged_argv()` branches, so every `sys.argv` mode read UNKNOWN. The breadth
        # this function exists for, missed on the most ordinary spelling.
        m = re.match(r'(\s*)(?:el)?if "(--[a-z-]+)" in [\w.]*argv\w*\(?\)?', line)
        if not m:
            continue
        # ⚑⚑ ONE BRANCH CAN OPEN SEVERAL MODES — `if "--replace-section" in sys.argv or
        # "--append-section" in sys.argv:` is ONE line serving TWO modes that share a body.
        # Matching only the first flag made the second read DECLARED-never-dispatched: a
        # PHANTOM verdict, the dangerous direction, against a mode that dispatches fine.
        # Measured on `mdstruct` the moment it adopted the roster — and the fix it would
        # have demanded is DELETING a correct declaration.
        indent = len(m.group(1))
        for flag in re.findall(r'"(--[a-z-]+)" in [\w.]*argv\w*\(?\)?', line):
            if flag not in starts:
                starts[flag] = i
                order.append((flag, i, indent))
    out = {}
    for n, (flag, i, indent) in enumerate(order):
        end = len(lines)
        for _f, j, ind2 in order[n + 1 :]:
            # a LATER branch at the same or shallower indent closes this one; a deeper one
            # is nested INSIDE it and must not truncate it.
            # ⚑ `j > i` — co-located flags share one `if` line and one body, so a sibling
            # from the SAME line must not close it at zero length.
            if j > i and ind2 <= indent:
                end = j
                break
        out[flag] = (i, end)
    return out


def contract_rows(src, roster, skip_marker="_report_skipped("):
    """[(flag, ok, why)] — hold ANY tool's roster to its own dispatch.

    ⚑⚑⚑ THE GENERALISATION OF `pycodemod.scan_contract`, AND ⟡mode-generic-contract IS
    WHY IT EXISTS.  That reader parsed one file's `_dispatch` and read one module-global
    `MODES`, so converting a roster elsewhere produced a tool that was STANDARDISED but
    not CHECKED — and a converted-unchecked roster contributes zero keys to the gate,
    rendering exactly like a clean one.  Standardizing the shape without moving the
    enforcement would have bought consistency and nothing else.

    Three verdicts, and the third is the honest one:
      True   — the mode honours what its roster claims
      False  — a real disagreement (undeclared arity, a phantom row, an unhonoured
               contract, a silent-default writer)
      None   — UNKNOWN: the branch could not be located.  A fact about this READER, never
               banked as a pass; `scan_contract`'s own history is why (it reported UNK
               rather than PASS on a spelling it could not see, and the UNK is what kept
               the disagreement visible instead of silently green).
    """
    lines = src.splitlines()
    bounds = branch_bounds(src)
    out = []
    for flag, m in sorted(roster.items()):
        if m.scans:
            if flag not in bounds:
                out.append((flag, None, "branch not located in the dispatch"))
            else:
                i, end = bounds[flag]
                ok = skip_marker in "\n".join(lines[i:end])
                out.append(
                    (
                        flag,
                        ok,
                        "reports skips"
                        if ok
                        else "declares scans=True but never calls %s" % skip_marker,
                    )
                )
        # ⚑ THE `writes` DISCRIMINATOR — the corpus's own `--apply` convention, finally
        # bound to something checkable: *"a mutating tool invoked with NEITHER `--apply`
        # nor `--dry-run` must REFUSE, never guess"*. 39 tools are half-paired, so this
        # is the field's whole purpose.
        if m.writes and flag in bounds:
            i, end = bounds[flag]
            body = "\n".join(lines[i:end])
            if "--apply" not in body and "--dry-run" not in body:
                out.append(
                    (
                        flag,
                        False,
                        "declares writes=%r but its branch tests neither --apply nor "
                        "--dry-run — a mutating mode with a silent default" % (m.writes,),
                    )
                )
    # ⚑ BOTH DIRECTIONS. A flag in one and not the other is a defect whichever way it
    # points: DISPATCHED-undeclared runs with arity nobody stated (`--key --archive f.py`
    # crashed exactly so), and DECLARED-undispatched is a promise the CLI does not keep
    # while still feeding arity resolution.
    tested = set(re.findall(r'"(--[a-z-]+)"\s+in\s+\w*argv\w*\(?\)?', src))
    # ⚑⚑ A FLAG DECLARED AS SOME MODE'S `opts` IS A MODIFIER, NOT AN UNDECLARED MODE — and
    # this is the half of `Mode.opts` the reader did not know about. `schema.py --coverage`
    # owns `--emit` and `--reap`, which dispatch as nested `if`s inside its branch; without
    # this the gate reported two OWNED modifiers as top-level modes nobody declared,
    # demanding they be promoted to modes — the opposite of what the roster says.
    #
    # ⚑ THIS IS THE SAME DISTINCTION ⟡mode-dual-role IS UNRESOLVED ABOUT IN `pycodemod`,
    # and seeing it resolve cleanly HERE is what shows the six there are a genuine design
    # question rather than missing rows: a modifier belongs to a mode (`opts`), a mode
    # stands alone, and six flags in `pycodemod` are currently spelled as both.
    owned = {o for m in roster.values() for o in m.opts}
    for flag in sorted(set(roster) | set(bounds)):
        if flag in owned and flag not in roster:
            continue
        # ⚑ THE POSITIONAL HAS NO FLAG TO DISPATCH ON, so comparing it against argv would
        # manufacture a phantom-declaration finding out of a correct declaration.
        if flag == POSITIONAL:
            continue
        if flag in roster and flag not in bounds and flag not in tested:
            out.append(
                (
                    flag,
                    False,
                    "DECLARED in the roster, never dispatched — a promise the CLI "
                    "does not keep, and its arity still feeds the entry point",
                )
            )
        elif flag in bounds and flag not in roster:
            i, end = bounds[flag]
            hint = (
                " (its usage exists only as a runtime print — reachable only by FAILING the mode)"
                if "usage:" in "\n".join(lines[i:end])
                else ""
            )
            out.append(
                (flag, False, "DISPATCHED, absent from the roster — undeclared arity" + hint)
            )
    return out


def _selftest():
    """The guarded cases. ⚑ A SHARED DECLARATION MODULE WITHOUT THEM IS THE WORST PLACE
    FOR A SILENT DEFECT: every adopting tool inherits it, and each one's own suite tests
    its ROSTER rather than the shape underneath."""
    import sys as _sys

    fails = []

    def check(what, got, want):
        if got != want:
            fails.append("  FAIL %s\n       got %r want %r" % (what, got, want))

    check("a bare flag has no operand", split_flag("--census"), ("--census", None))
    check("an operand is split off the key", split_flag("--core PATH"), ("--core", "PATH"))
    # ⚑ THE SPELLING IS KEPT VERBATIM, never normalised to a name: `"REL [N]"` tells a
    # reader the second operand is optional, and inventing a canonical form here would be
    # a second authority over what the dispatch already accepts.
    check(
        "a multi-token operand keeps its spelling",
        split_flag("--sample REL [N]"),
        ("--sample", "REL [N]"),
    )
    check(
        "surrounding space does not invent an operand", split_flag("  --holes  "), ("--holes", None)
    )

    lifted = from_pairs([("--core PATH", "one core"), ("--census", "all of them")])
    check("from_pairs keys on the FLAG, not the spelling", sorted(lifted), ["--census", "--core"])
    check("...and recovers the operand the pair buried in prose", lifted["--core"].operand, "PATH")
    check("...and carries the gloss as why", lifted["--census"].why, "all of them")
    # ⚑ THE DEFAULTS ARE CLAIMS, NOT BLANKS — the gate holds a lifted roster to them.
    check("a lifted mode claims it scans nothing", lifted["--census"].scans, False)
    check("a lifted mode claims it writes nothing", lifted["--census"].writes, ())

    check("writes defaults to a pure read", Mode().writes, ())
    check("mutates projects writes", Mode().mutates, False)
    check("...and is True once a target is named", Mode(writes=("store",)).mutates, True)
    # ⚑ `mutates` IS DERIVED, so there is no second spelling to drift from `writes`.
    check("mutates is not a slot", "mutates" in Mode.__slots__, False)
    check("opts are normalised to a tuple", Mode(opts=["--x"]).opts, ("--x",))
    check("repr names only what is declared", repr(Mode(paths=True)), "Mode(paths=True)")

    # ── contract_rows: the generic reader (⟡mode-generic-contract) ──────────────
    # ⚑ A SYNTHETIC DISPATCH, so these cases test the READER rather than whichever real
    # tool happens to be converted today. A case pinned to a live specimen fails when the
    # migration succeeds — measured this session: two `pycodemod` cases used `--touches`
    # as their undeclared specimen and broke the moment it was declared.
    _src = (
        'if "--good" in sys.argv:\n'
        "    _report_skipped()\n"
        'if "--bad" in sys.argv:\n'
        '    print("nothing")\n'
        'if "--wet" in flagged_argv():\n'
        '    print("usage: t --wet")\n'
        # ⚑⚑ THE GUARD IS SPELLED AS A NESTED `if "--apply" in sys.argv:` DELIBERATELY
        # — it is the shape that USED to break the reader. Under next-match bounding
        # the nested flag registered as a sibling MODE and truncated its parent's body
        # to nothing, so a correctly-guarded mutator read as a silent-default writer.
        # ⚑ AND IT WAS NOT A FIXTURE ARTEFACT: `schema.py --coverage` (424) nests
        # `--reap` (427) whose `--apply` guard sits at 430, and the gate accused it.
        # Indentation-aware bounding fixed both. ⟡mode-branch-bounds, closed.
        'if "--guarded" in sys.argv:\n'
        '    if "--apply" in sys.argv:\n'
        "        write()\n"
    )

    # ⚑ ONE FLAG CAN YIELD SEVERAL ROWS — a `scans` verdict AND a roster disagreement are
    # separate findings about the same mode. My first cut used a dict comprehension, so
    # the LAST row silently won and four cases read the wrong verdict. Keep the first.
    def _first(rows):
        out = {}
        for f, ok, why in rows:
            out.setdefault(f, (ok, why))
        return out

    _rows = _first(
        contract_rows(
            _src,
            {
                "--good": Mode(scans=True),
                "--bad": Mode(scans=True),
                "--guarded": Mode(writes=("store",)),
                "--gone": Mode(),
            },
        )
    )
    check("a scanning mode that reports skips passes", _rows["--good"][0], True)
    check("...and one that does not FAILS", _rows["--bad"][0], False)
    check("a declared-never-dispatched mode is a phantom", _rows["--gone"][0], False)
    check(
        "...named as a promise the CLI does not keep",
        "never dispatched" in _rows["--gone"][1],
        True,
    )
    check("a dispatched-undeclared mode is caught", _rows["--wet"][0], False)
    # ⚑ BOTH SPELLINGS OF THE RECEIVER — `flagged_argv()` as well as `sys.argv`. Keying on
    # one is `census-keyed-on-one-spelling`, which this reader's ancestor committed TWICE.
    check(
        "...via flagged_argv(), not just sys.argv",
        "absent from the roster" in _rows["--wet"][1],
        True,
    )
    check(
        "...and the runtime-print-only usage is named",
        "reachable only by FAILING" in _rows["--wet"][1],
        True,
    )
    # ⚑ THE `writes` DISCRIMINATOR: a mutating branch that tests --apply is honest, so it
    # yields NO row at all — the check is absence, not a True verdict. (`contract_rows`
    # reports findings; a mode with nothing wrong is simply not in the output.)
    check("a writing mode that gates on --apply yields no finding", "--guarded" in _rows, False)
    # ⚑ ITS OWN SOURCE, because in `_src` the next branch's `--apply` would be swallowed
    # by an over-wide bound. Over-wide bounds can only produce a FALSE PASS, never a false
    # failure — the asymmetry `branch_bounds` states.
    _lone = 'if "--wet" in sys.argv:\n    write_the_store()\n'
    _wet = dict(
        (f, (ok, why)) for f, ok, why in contract_rows(_lone, {"--wet": Mode(writes=("store",))})
    )
    check("...and one that gates on neither FAILS", _wet["--wet"][0], False)
    check("...named as a silent default", "silent default" in _wet["--wet"][1], True)
    # ⚑ UNKNOWN IS NOT PASS — an unlocatable branch is a fact about the reader.
    # ⚑⚑ NESTED SUB-FLAGS DO NOT TRUNCATE THEIR PARENT (⟡mode-branch-bounds, closed).
    # The regression this pins was a FALSE ACCUSATION against a compliant tool — the one
    # failure a gate must not make, since the fix it demands is to break a working refusal.
    _nest = branch_bounds(_src)
    check(
        "a nested sub-flag is inside its parent's body, not a sibling",
        _nest["--guarded"][1] - _nest["--guarded"][0] >= 3,
        True,
    )
    check(
        "...so the parent's own --apply guard is seen",
        "--guarded" in _first(contract_rows(_src, {"--guarded": Mode(writes=("store",))})),
        False,
    )

    # ⚑ CO-LOCATED MODES — one `if` line, two flags, one shared body. Matching only the
    # first made the second read DECLARED-never-dispatched (a phantom, the dangerous
    # direction) and the fix it demanded was deleting a correct declaration.
    _co = 'if "--a" in sys.argv or "--b" in sys.argv:\n    shared()\n'
    check("both flags of a shared branch are located", sorted(branch_bounds(_co)), ["--a", "--b"])
    check(
        "...and neither truncates the other to nothing",
        branch_bounds(_co)["--a"][1] - branch_bounds(_co)["--a"][0] >= 2,
        True,
    )
    check(
        "...so neither is reported a phantom",
        [f for f, _o, _w in contract_rows(_co, {"--a": Mode(), "--b": Mode()})],
        [],
    )

    # ⚑ A MODE'S OWNED MODIFIER IS NOT AN UNDECLARED MODE. `schema.py --coverage` owns
    # `--emit`/`--reap`, dispatched as nested ifs; without this they read as two top-level
    # modes nobody declared, and the gate demanded promoting them — inverting the roster.
    _own = 'if "--cov" in sys.argv:\n    if "--emit" in sys.argv:\n        go()\n'
    check(
        "a flag declared in another mode's opts is not an undeclared mode",
        [f for f, _o, _w in contract_rows(_own, {"--cov": Mode(opts=("--emit",))})],
        [],
    )

    # ⚑ THE POSITIONAL — a declaration with no flag. `jea_pydecode` declares
    # `("<file.py>", …)` as its primary invocation; keyed as a flag it would be reported
    # DECLARED-never-dispatched, a false finding manufactured by the migration itself.
    _pos = from_pairs(
        [("<file.py>", "what this file would produce"), ("--selftest", "the guarded cases")]
    )
    check(
        "a non-flag entry keys as the positional", sorted(_pos), sorted([POSITIONAL, "--selftest"])
    )
    check("...keeping its spelling as the operand", _pos[POSITIONAL].operand, "<file.py>")
    check("...and taking a path population", _pos[POSITIONAL].paths, True)
    check(
        "the positional is never compared against argv",
        [f for f, _o, _w in contract_rows("x = 1\n", _pos) if f == POSITIONAL],
        [],
    )

    _unk = _first(contract_rows("x = 1\n", {"--nowhere": Mode(scans=True)}))
    check("an unlocatable branch is UNKNOWN, never a pass", _unk["--nowhere"][0], None)

    # ── Selftest: the three states (⟡selftest-record, gate-F7) ──────────────────
    # ⚑ EVERY CASE HERE IS A DISTINCTION `run_selftests.discover()` CANNOT DRAW. It
    # returns a 96-row list of files that ARE suites; a tool with none, a fixture, and a
    # tool nobody has looked at are all the same absence from that list.
    check("the default state is a suite", Selftest().state, "suite")
    check("a suite is runnable", Selftest().runnable, True)
    # ⚑ THE STATE THE RECORD EXISTS FOR. `fix_notinscope.py` and `check_mode_contracts.py`
    # have no `--selftest`, so "run the selftest after you change it" was a NON-COMMAND —
    # and it could be issued because absence had no reader.
    check(
        "a declared absence is NOT runnable",
        Selftest(state="none", why="pure dispatch over a checked library").runnable,
        False,
    )
    check("...and neither is a fixture", Selftest(state="fixture").runnable, False)
    # ⚑ REFUSED AT CONSTRUCTION. A typo'd state defaulting to `suite` would put a tool in
    # the roster that has no suite — a defect manufactured by the declaration.
    try:
        Selftest(state="sute")
        check("an unrecognised state REFUSES", "no raise", "ValueError")
    except ValueError as _e:
        check("an unrecognised state REFUSES", "closed set" in str(_e), True)

    # ── the contract: a declaration held to its own fields ──────────────────────
    check("a plain suite satisfies its contract", Selftest().contract()[0], True)
    # ⚑ A `none` WITH NO REASON IS THE SHRUG THE RECORD REPLACES. Without this the state
    # is a cheaper way to be silent than having no declaration at all.
    check("state='none' with no reason FAILS", Selftest(state="none").contract()[0], False)
    check(
        "...named as an undeclared absence",
        "no `why`" in Selftest(state="none").contract()[1],
        True,
    )
    check(
        "...and one WITH a reason passes",
        Selftest(state="none", why="a declaration module: it dispatches nothing").contract()[0],
        True,
    )
    # ⚑ A FIELD THAT INSTRUCTS THE RUNNER, ON A TOOL THE RUNNER NEVER INVOKES, is
    # configuration for a call that never happens — the `rewire_only` shape (1 def, 0
    # calls) in declaration form.
    check(
        "a record key on a non-suite FAILS",
        Selftest(state="none", why="x", key="a/b.py").contract()[0],
        False,
    )
    check(
        "requires on a non-suite FAILS",
        Selftest(state="fixture", requires=("numpy",)).contract()[0],
        False,
    )
    check(
        "tenant on a non-suite FAILS",
        Selftest(state="fixture", tenant="sandbox").contract()[0],
        False,
    )
    # ⚑ AND THE CONTRACT MUST DISCRIMINATE — a checker that fails everything passes a
    # "does it refuse" case while being useless.
    check(
        "a fully-specified suite still passes",
        Selftest(requires=("numpy",), tenant="sandbox", key="p.py").contract()[0],
        True,
    )

    # ── selftest_rows: DECLARED against DISCOVERED ──────────────────────────────
    # ⚑ TWO INDEPENDENT READINGS, and every disagreement is a finding. Discovery answers
    # "is this file in the roster"; it cannot answer "should it be" — which is exactly the
    # question the fork bomb needed asked.
    _decl = {
        "a.py": Selftest(),
        "b.py": Selftest(state="none", why="no logic to test"),
        "c.py": Selftest(state="fixture"),
        "d.py": Selftest(),
    }
    _rows = {
        t: (s, ok, why) for t, s, ok, why in selftest_rows(_decl, ["a.py", "b.py", "c.py", "e.py"])
    }
    check("a declared suite that discovery found is OK", _rows["a.py"][1], True)
    check("a declared `none` the runner is RUNNING is a disagreement", _rows["b.py"][1], False)
    # ⚑ A FIXTURE IN THE ROSTER MAKES THE GATE RED BY DESIGN — it is MEANT to fail. It
    # belongs inside the runner's own suite as a positive control, never as a member.
    check("a fixture in the roster is a finding", _rows["c.py"][1], False)
    check("...named as red-by-design", "red by design" in _rows["c.py"][2], True)
    check("a declared suite discovery CANNOT reach is a finding", _rows["d.py"][1], False)
    # ⚑ UNDECLARED IS REPORTED, NOT OMITTED. A row-set of disagreements alone cannot
    # distinguish "all consistent" from "nothing declared yet" — a false ZERO gets banked
    # while a false positive gets investigated.
    check(
        "a discovered-but-undeclared tool is reported as UNDECLARED", _rows["e.py"][0], "undeclared"
    )
    check("...and is not scored as a failure", _rows["e.py"][1], None)
    # ⚑ A BROKEN CONTRACT OUTRANKS THE MEMBERSHIP COMPARE: a declaration that contradicts
    # itself cannot be meaningfully checked against the tree.
    _bad = {
        t: (s, ok, why) for t, s, ok, why in selftest_rows({"z.py": Selftest(state="none")}, [])
    }
    check(
        "a self-contradicting declaration fails before the membership test",
        "no `why`" in _bad["z.py"][2],
        True,
    )

    # ── self_including: the STATIC half of ⟡worklist-gate-recursion ─────────────
    # ⚑ THE ROSTER CONTAINED ITS OWN CALLER AND NO SOURCE FILE COULD SAY SO. `worklist_gate
    # --selftest` runs the roster, and the roster runs `worklist_gate --selftest`. Measured:
    # six generations, load 54.93, 68 processes on 10 cores.
    _rr = {
        "scripts/run_selftests.py": Selftest(runs_roster=True),
        "scripts/worklist_gate.py": Selftest(runs_roster=True),
        "scratch/quiet.py": Selftest(),
    }
    check(
        "a member declaring it runs the roster is named STATICALLY",
        self_including(_rr, "scripts/run_selftests.py"),
        ["scripts/worklist_gate.py"],
    )
    # ⚑ THE ROSTER ITSELF IS NOT A CYCLE — running the roster is what it IS. Excluded by
    # NAME in the reader, not by a field a second tool could set to exempt itself.
    check(
        "the roster tool is not reported against itself",
        "scripts/run_selftests.py" in self_including(_rr, "scripts/run_selftests.py"),
        False,
    )
    check(
        "a tool that does not run the roster is not named",
        "scratch/quiet.py" in self_including(_rr, "scripts/run_selftests.py"),
        False,
    )
    # ⚑ AND THE EDGE IS MEANINGLESS ON A TOOL NOTHING INVOKES — declaring it there would
    # make `self_including` name a tool no roster runs: a FALSE FINDING out of the reader
    # built to prevent the fork bomb.
    check(
        "runs_roster on a non-suite FAILS its contract",
        Selftest(state="none", why="x", runs_roster=True).contract()[0],
        False,
    )

    _N = 63
    for line in fails:
        print(line)
    print("climode selftest: %d/%d" % (_N - len(fails), _N))
    return 1 if fails else 0


if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    # ⚑⚑ A BARE RUN PRINTS THE DOCSTRING AND EXITS 0 — CORRECT. ANY OTHER FLAG MUST NOT.
    # This module deliberately has no modes (see the docstring: it declares, it does not
    # dispatch), but until 2026-08-24 it printed the docstring for ANY argv and exited 0,
    # so `climode.py --rows <file>` read exactly like a mode that ran and found nothing.
    # MEASURED: I typed that, got the docstring, and had to notice the absence of a table
    # to realise no query had happened. Exit 0 is the whole defect — a refusal here is
    # cheap, and a zero-exit non-answer is the `looks like it ran` class `check_argv`'s
    # docstring is about, arriving through the tool that has no flags rather than one
    # whose flag was misspelled.
    #
    # ⚑ NOT ROUTED THROUGH `ratchet.check_argv`, and that is the honest shape. `check_argv`
    # answers "is this flag in the known set" — here the known set is EMPTY by design, so
    # importing the guard to compare against nothing would dress a categorical refusal up
    # as a membership test and imply a roster this module does not have.
    if sys.argv[1:]:
        print(__doc__)
        print(
            "climode.py: takes no arguments but --selftest (got %s)." % " ".join(sys.argv[1:]),
            file=sys.stderr,
        )
        print(
            "  This module DECLARES the Mode shape; it does not dispatch. The readers "
            "over a tool's roster live in\n  `check_mode_contracts.py` (--list, --where) "
            "and `scratch/toolmodes.py` (--all, --divergence).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print(__doc__)
