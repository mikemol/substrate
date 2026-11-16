#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Structural questions about the PLAN / worklist markdown, via pandoc's AST.

⚑ WHY THIS IS THE THIRD LEVEL.  `agda_lex` reads Agda structurally, `pycodemod`
reads the Python tooling structurally, and the PLAN — a 3900-line document that is
this arc's single source of record — is still read by `grep`.  Every question I
have asked of it this session went through a line-regex:

  * "is the canonical chain table current?" (it had outlived its own corrections
    FOUR times, §21/§31/§41/§42 — each caught only because a human asked)
  * "which figures does the plan quote that a later section superseded?"
    (589-vs-1322, 21-vs-27 gates, 113-vs-345 — all found by hand)
  * "which ⚑ findings have no corresponding worklist item?" (§24/§25 audits, by eye)

Those are STRUCTURAL queries — over headers, tables, and their cells — and a
`grep` answers them by accident or not at all.  A table cell containing a stale
number is invisible to a line scan that does not know it is in a table.

⚑ THE PRECONDITION, AND IT IS DIFFERENT FROM `pycodemod`'s.  libcst is LOSSLESS by
construction, so its round-trip gate was a formality that passed.  **Pandoc is a
NORMALIZER, not a preserver** — it reflows text, re-wraps tables, and re-renders
emphasis, so a markdown→AST→markdown round-trip is NOT expected to be
byte-identical.  That makes the honest question:

    what EXACTLY does a round-trip change, and is any of it load-bearing?

This module answers that (`--roundtrip`) before proposing any transform, because a
WRITE path over this document is only safe if the answer is "nothing that matters",
and a READ path is safe regardless.  Reporting a diff summary rather than a bare
pass/fail is the point: `identical` and `only re-wrapped a table border` and
`dropped a ⚑ marker` are three very different verdicts.

    mdstruct.py --roundtrip <file>    # what does pandoc normalization change?
    mdstruct.py --headers <file>      # the section skeleton: levels AND LINE SPANS
    mdstruct.py --spans <file> [match]
                                      # the same spans, filtered to ONE section
                                      # ⚑ BOTH PRINT SPANS, and `--headers` did not
                                      # until 2026-08-24.  A skeleton without bounds
                                      # cannot be read FROM: targeting one section of
                                      # a 1414-line document meant reading the whole
                                      # file, or already knowing `--spans` existed —
                                      # and `--spans` was ABSENT FROM THIS BANNER, so
                                      # the only route to it was reading the dispatch.
                                      # A dispatched mode with no self-description is
                                      # the `agda-F2` shape, here in the tool whose
                                      # own docstring is the map.  Measured: a reader
                                      # holding both modes read 1414 lines to reach 25.
    mdstruct.py --tables <file>       # every table, with its header row + size
    mdstruct.py --rows <file> [--table N] [--where <substr>]
                                      # the table CELLS — the row-level read that
                                      # makes `catalog/reuse-index.md` (963 rows)
                                      # queryable by the tool that owns it
    mdstruct.py --replace-section <file> <heading-substring>
                [--body TEXT | --body-file F | <stdin>] (--apply | --dry-run)
                                      # swap ONE section's BODY, heading untouched.
    mdstruct.py --append-section <file> <heading-substring>
                [--body TEXT | --body-file F | <stdin>] (--apply | --dry-run)
                                      # add to the END of ONE named section — the
                                      # BOUNDED form of what `cat >>` does unbounded.
                                      # ⚑ WHY THESE EXIST: `hook_structural_query`
                                      # refuses `cat >> doc.md` and was RIGHT to (a
                                      # shell append is unbounded and shapeless —
                                      # MEMORY.md's staging block grew past the
                                      # 200-line budget of the reader that loads it
                                      # every session, appended and never drained).
                                      # But the refusal could only name a READER, so a
                                      # correct verdict read as a bug to the peer who
                                      # hit it.  A gate that blocks without routing is
                                      # half a gate.
                                      # ⚑ A LINE SPLICE, not an AST render: the AST
                                      # answers WHERE the section is (correctly about
                                      # fences and nesting), raw lines carry the
                                      # change, so a 5-line edit is a 5-line diff.
                                      # Normalization is a SEPARATE reviewable
                                      # migration — `--fixpoint --apply`.
                                      # ⚑ REFUSES: an ambiguous heading substring
                                      # (names both candidates), a missing one, and a
                                      # body carrying a heading that would RE-PARENT
                                      # the document.  Intent must be STATED.
    mdstruct.py --budget <file> [N]   # BYTES, split per section, against an optional
                                      # budget N — the reader-budget question that
                                      # otherwise routes to `wc -c`, which the
                                      # structural hook refuses with nowhere to send
                                      # you. Section attribution makes compaction
                                      # TARGETABLE; a bare total only says "too big".
    mdstruct.py --items <file>        # every worklist ITEM LABEL the doc defines
    mdstruct.py --coherence <plan> <worklist>   # items ↔ witnesses, both directions
    mdstruct.py --superseded <file>  # figures a LATER section contradicts
    mdstruct.py --label-families [root]
                                      # ⚑ THE PRIOR QUESTION `--items` CANNOT ASK:
                                      # what shapes are BEING USED as labels here,
                                      # including families no grammar knows?  Walks
                                      # a whole tree — INCLUDING git-ignored paths,
                                      # which is where a new vocabulary is invented
                                      # — clusters tokens in label POSITION by SHAPE
                                      # (unicode BLOCK for non-ASCII), and separates
                                      # "read by ITEM_RE" from "⚑ UNREADABLE".
                                      # Ranked by FILE SPREAD, not count: a label is
                                      # a SHARED vocabulary, so it recurs across
                                      # documents where a module name recurs within
                                      # one.  Reports CANDIDATES, never verdicts —
                                      # ITEM_RE has been widened four times, each to
                                      # the family in front of the author, and a
                                      # fifth guess would be the fifth instance.

⚑ THE AUDITS ABOVE WERE THIS MODULE'S STATED REASON FOR EXISTING AND WERE NEVER
BUILT (user, 2026-08-01: *"how much of the markdown editing and auditing can we
mechanize with the tooling we now have for structural transforms?"*).  The docstring
listed all three as the questions a `grep` answers by accident; §50 then built the
NORMALIZER and stopped.  So every coherence audit since — §24, §25, and the pass
that found `R2-SWEEP` had no plan witness — was performed BY EYE against a
3900-line document, which is the reasoning-not-codified shape at document scale.

⚑ AND THE PLAN IS OUTSIDE THE REPO (`~/.claude/plans/`), so no gate can see it, no
snapshot protects it, and `git` holds none of its history — §10's untracked-work
hazard applied to the arc's OWN RECORD.  Moving it in-repo is what makes
`--coherence` gateable rather than advisory; filed as M4.
"""
import os
import re
import subprocess
import sys
import warnings

# ⚑ ⟡vfs-chokepoints — the ONE read/write seam over the working tree and git history.
# A sibling in `scratch/`, so a plain import resolves; see `_text` for what the
# three-valued `Presence` buys the `.md` family over a bare `open()`.
import vfs

# ⚑ SILENCED AT THE SOURCE, NOT AT THE SHELL.  panflute 2.3.1's `io.py:143`
# docstring contains `\*\*kwargs`, which Python 3.14 reports as an invalid escape
# sequence — so every invocation emits a SyntaxWarning that is not about our code
# and cannot be fixed in our code.  The reflex is `2>&1 | grep -v SyntaxWarning`;
# that is reasoning performed at the shell, and it also hides any REAL warning the
# same run might emit.  Filtering the one known third-party pattern here keeps the
# tool's output clean AND keeps unrelated warnings visible.
warnings.filterwarnings("ignore", category=SyntaxWarning, module="panflute.*")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ⚑ THE ARC'S RECORD LIVES OUTSIDE THE REPO, AND THE WORKLIST LIVES IN NO FILE AT
# ALL.  `PLAN` is under `~/.claude/plans/` — untracked, ungated, unsnapshotted — and
# the worklist exists only in the harness's todo state, so `--coherence` has one
# document to read and one it cannot.  That is §10's untracked-work hazard applied
# to the arc's OWN RECORD: the thing that says what was measured and why is the
# least protected artifact in the project.
#
# ⚑ `docs()` RESOLVES THEM RATHER THAN ASSUMING.  A hardcoded path is a claim about
# the filesystem, and the reflex when it is wrong is to `ls` at the shell — which is
# the operator answering a question the tool should.  This reports what it FOUND and
# what is MISSING, so "the worklist has no file" is a stated fact, not a crash.
PLAN_CANDIDATES = (
    os.path.join(ROOT, "catalog", "plan.md"),                    # in-repo (M4)
    os.path.expanduser("~/.claude/plans/radiant-weaving-dawn.md"),
)
WORKLIST_CANDIDATES = (
    os.path.join(ROOT, "catalog", "worklist.md"),                # in-repo (M4)
    os.path.join(ROOT, "worklist.md"),
)
PLAN = next((p for p in PLAN_CANDIDATES if os.path.exists(p)), PLAN_CANDIDATES[-1])


def docs():
    """(plan_path|None, worklist_path|None, notes) — where the record actually is."""
    plan = next((p for p in PLAN_CANDIDATES if os.path.exists(p)), None)
    wl = next((p for p in WORKLIST_CANDIDATES if os.path.exists(p)), None)
    notes = []
    if plan and not plan.startswith(ROOT):
        notes.append(f"plan is OUTSIDE the repo ({plan}) — untracked, ungated, "
                     f"no snapshot; see M4")
    if not plan:
        notes.append("no plan document found")
    if not wl:
        notes.append("no worklist FILE exists — the worklist lives only in the "
                     "harness todo state, so nothing can audit it; see M4")
    return plan, wl, notes


# ⚑ THE WRITER CONFIG, DECLARED ONCE.  §50 measured this exact spelling to a
# FIXPOINT in 4 rounds (`[8, 5, 2, 0]`) where bare `markdown` took 7 — and it was
# then written out at two call sites, which is the same-name-different-body hazard
# §6d retired for `agda_files()`.  A normalizer whose flags drift between the
# reporter and the writer would report one document and write another.
WRITER = ("markdown-smart+pipe_tables-multiline_tables-simple_tables-grid_tables"
          " --columns=120 --wrap=preserve")


def split_frontmatter(src):
    """(frontmatter_or_'', body) — YAML frontmatter is DATA, not prose.

    ⚑ PANDOC ATE THE FRONTMATTER AND BOTH GATES PASSED THE WRITE (2026-08-03).
    Converting a memory dropped `name:`, `type:`, `originSessionId:`, `modified:` —
    a memory's IDENTITY and provenance — while `--fixpoint` reported `✓` and
    `--roundtrip` said the drift was "expected, not a failure".  Pandoc parses
    frontmatter as metadata and only re-emits it if asked with `--standalone`, and
    its YAML round-trip is its own normalization anyway.

    ⚑ THE FIX IS TO NOT HAND IT OVER.  Frontmatter is a different language sharing a
    file with markdown; the prose writer has no business reformatting it.  Splitting
    here — at the ONE conversion point all seven callers route through — means every
    mode gains preservation at once, rather than each remembering to re-attach it.
    """
    if not src.startswith("---\n"):
        return "", src
    end = src.find("\n---\n", 3)
    if end == -1:
        return "", src
    cut = end + len("\n---\n")
    return src[:cut], src[cut:]


# ⚑ THE WRITERS THAT READ BACK AS MARKDOWN — the predicate `_pandoc` re-attaches on.
# A prefix tuple, not an equality set, because every caller here passes a bare family name
# but pandoc accepts `markdown_strict`, `commonmark_x`, and `+ext`/`-ext` suffixes on any of
# them; an equality check would silently stop preserving frontmatter the first time someone
# asked for a dialect.  `json`, `html`, `latex`, `native` are all correctly excluded.
_MD_WRITERS = ("markdown", "commonmark", "gfm")


# ⚑⚑⚑ ⟡mode-standardize / Ⓢ1e — THE DECLARED MODE ROSTER.  This file had NO roster: its
# modes lived in a 48-line module docstring, and 5 of them (`--lint-shape`, `--narrowest`,
# `--spans`, `--table-forms`, `--why-not-pipe`) appeared in NO usage line at all, so
# `toolmodes --find spans` could not answer a question this tool answers.  The docstring
# stays as prose; THIS is the machine-readable authority `check_mode_contracts` holds it to.
#
# ⚑⚑ EVERY FIELD READ FROM THE BRANCH, NOT FROM THE NAME.  Twice this session I inferred a
# field from a mode's spelling and was wrong in both directions — `schema --establish` read
# as nullary when it takes tier names, `schema --transport` read as a writer when it is a
# pure read.  So: `paths=True` throughout because the entry point binds `path = args[0] if
# args else PLAN` for every mode (`:1801-1802`), and `writes` names only the three branches
# that actually call `open(..., "w")`.
#
# ⚑ THE THREE WRITERS ALL ALREADY REFUSE A BARE RUN, which is why declaring `writes` here
# costs nothing and buys the check: `--fixpoint --apply` gates at `:1841` (and REFUSES a
# non-fixpoint, and again on semantic damage), and the two section modes route through
# `ratchet.mutating_argv` at `:1898` — no default-dry, no default-apply.  A future mode that
# grows a write without that guard is now a GATE FAILURE rather than a review note.
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from climode import Mode                                                   # noqa: E402

MODES = {
    # ── readers ────────────────────────────────────────────────────────────────
    "--headers": Mode(paths=True, why="the heading tree, indented by level"),
    "--spans": Mode(operand="[match]", paths=True,
                    why="each section's line bounds; with a match, ONE section's — the "
                        "reader that replaced reaching for awk over fenced # and --"),
    "--items": Mode(paths=True, why="the labelled items ITEM_RE can read"),
    "--rows": Mode(operand="[--where V]", paths=True,
                   why="table rows as records — the structural read of a .md table"),
    "--tables": Mode(paths=True, why="each table's shape and column count"),
    "--table-forms": Mode(paths=True, why="the distinct table FORMS in use"),
    "--table-style": Mode(paths=True, why="pipe/grid/simple style per table"),
    "--narrowest": Mode(paths=True, why="the narrowest admissible column widths"),
    # ⚑ I TYPED A `--headers-coherence` ROW HERE AND IT DOES NOT EXIST — invented while
    # transcribing, caught by the derived list not containing it. That is the PHANTOM
    # direction, the dangerous one: a declared-never-dispatched row still feeds arity
    # resolution, so it can bind a real operand as a flag's argument. Deleted, recorded.
    "--coherence": Mode(paths=True, why="do the headings and the item labels agree"),
    "--superseded": Mode(paths=True, why="figures/sections a later one supersedes"),
    "--label-families": Mode(operand="[root]", paths=True,
                             why="label SHAPES corpus-wide including git-ignored trees — "
                                 "where a new vocabulary gets invented; ranked by FILE "
                                 "SPREAD, never by count"),
    "--why-not-pipe": Mode(paths=True,
                           why="per heading, why this document is not a pipe table"),
    # ⚑ THE OPERAND BINDS BY SHAPE, NOT BY POSITION — and that is what the arity
    # declaration has to say.  The branch (`:2282`) scans ALL of `sys.argv[1:]` for
    # the first `isdigit()` token, so the budget is NOT the token after the flag and
    # `--budget <file> N` is as valid as `--budget N <file>`.  Declaring it as an
    # adjacent operand would tell the arg-stripper to swallow the following token —
    # binding the PATH as the budget — which is the `--key --archive f.py` crash this
    # roster exists to prevent, one tool over.  `[N]` names an optional free operand
    # that the flag itself does not consume; the entry point's own stripper (`:1906`)
    # keeps `args[0]` as the path either way.
    "--budget": Mode(operand="[N]", paths=True,
                     why="byte size WITH PER-SECTION ATTRIBUTION, and a verdict against "
                         "an optional budget — the mode that replaced reaching for `wc "
                         "-c` on a structured .md; the split is the point, since a bare "
                         "total says 'too big' and nothing about WHERE, and for a "
                         "POINTER INDEX the wrong repair is deleting the tail"),
    "--lint-shape": Mode(paths=True, why="shape lint over the document"),
    "--lint-config": Mode(paths=True, why="audit the lint configuration itself"),
    # ── the losslessness precondition ──────────────────────────────────────────
    "--roundtrip": Mode(paths=True,
                        why="does pandoc normalization reproduce this document — the "
                            "one-time drift, paid before any write path is considered"),
    # ── writers (each refuses a bare run; see the ⚑ above) ─────────────────────
    "--fixpoint": Mode(paths=True, opts=("--to", "--apply"), writes=(".md",),
                       why="is normalization IDEMPOTENT — the property that makes a write "
                           "path admissible at all; --apply writes the converged document"),
    "--replace-section": Mode(operand="<file> <heading-substring>",
                              opts=("--body", "--body-file", "--apply", "--dry-run"),
                              writes=(".md",),
                              why="structural rewrite of ONE section — the bounded, "
                                  "skeleton-checked answer to a shell append"),
    "--append-section": Mode(operand="<file> <heading-substring>",
                             opts=("--body", "--body-file", "--apply", "--dry-run"),
                             writes=(".md",),
                             why="append INTO one section, refusing any body whose "
                                 "headings would re-parent the document"),
    "--selftest": Mode(why="the guarded cases (exit 2 = INCOMPLETE, not failure)"),
}


def _pandoc(src, to, frm="markdown"):
    """`to` may carry extra writer FLAGS after the format name.

    ⚑ The wrapping flags (`--columns`, `--wrap`) are what decide idempotence for a
    table-dense document, so they must be reachable from the caller; passing the
    whole string as one `-t` argument makes pandoc read `--columns=999` as an
    extension name and refuse.

    ⚑ FRONTMATTER IS PRESERVED VERBATIM, never converted (see `split_frontmatter`).
    It is re-attached byte-for-byte, so a document's metadata survives any number of
    normalization rounds — which is also what makes idempotence measurable on files
    that HAVE frontmatter: previously round 1 deleted it and round 2 saw a different
    document.

    ⚑⚑ BUT RE-ATTACHING IS ONLY CORRECT FOR A MARKDOWN WRITER, and doing it
    unconditionally broke EVERY AST MODE on any `---`-fenced document for the whole
    life of this module.  `-t json` got the YAML head prepended to the JSON, so
    `panflute.load` read a document that opens with `---` and died at char 0 —
    `--headers`, `--tables`, `--rows`, `--items` and `--coherence` were all blind to
    frontmatter'd markdown, which in practice is every governed doc and every
    SKILL.md.  The re-attach exists to survive markdown→markdown; for any other
    writer the head is not preservation, it is corruption of a different language.

    ⚑ DIAGNOSED BY gabion, NOT HERE — reported through summit
    (`corroboration-mdstruct-frontmatter-gabion`), which also explains the asymmetry
    the original report saw: `split_frontmatter` recognises a `---` fence only, so a
    `+++` (TOML) document never splits and therefore never gets a head re-attached,
    and the same mode succeeds on it.  gabion verified the one-condition fix by hand
    and deliberately did NOT apply it, because their copy is a symlink and a local
    patch would fork the body silently.  That is the forum working: the owner is the
    party who can fix it, and the owner could not see it from inside.
    """
    head, body = split_frontmatter(src)
    parts = (to or "markdown").split()
    cmd = ["pandoc", "-f", frm, "-t", parts[0]] + parts[1:]
    p = subprocess.run(cmd, input=body, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr.strip()[:400])
    return (head + p.stdout) if parts[0].startswith(_MD_WRITERS) else p.stdout


def _diff(a, b, limit=12):
    import difflib
    d = [l for l in difflib.unified_diff(a.split("\n"), b.split("\n"),
                                         lineterm="", n=0)
         if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
    return len(d), d[:limit]


def roundtrip(path, opts=None):
    """(identical, n_changed_lines, sample) — what pandoc normalization does.

    ⚑ NOT a pass/fail.  Pandoc normalizes by design, so `identical` is the
    unusual case; what a caller needs is the SIZE and SHAPE of the drift.
    """
    src = open(path, encoding="utf-8").read()
    out = _pandoc(src, opts or "markdown")
    if out == src:
        return True, 0, []
    return (False,) + _diff(src, out)


def lint_shape(path, line_length=120):
    """[(line, rule, detail)] — the markdownlint classes, measured on THIS document.

    ⚑ BUILT BECAUSE I WAS ABOUT TO DISABLE FOUR RULES WITHOUT MEASURING ANY OF THEM
    (user, 2026-08-03: *"See, this I don't want to do … The question is, how can we
    make things not incompatible with them?"*).  Turning a rule off is the allow-list
    move — it rots, and it hides the population instead of retiring it.  The honest
    move is to ask what each rule actually finds here, which nothing could answer:
    the linter is an IDE extension, not something a tool call can invoke.

    ⚑ AND MOST OF THESE ARE SATISFIABLE, NOT INCOMPATIBLE.  MD013 wants a width the
    document already has — it just needs to be TOLD the width `WRITER` emits (120),
    which makes the rule AGREE with the writer rather than be suppressed by it.
    MD041 is the one genuine mismatch: it wants an H1 title, and a memory's title
    lives in `name:` — duplicating it as a heading would be two spellings of one
    fact, the derived-view defect in a document's own header.

    Frontmatter is EXCLUDED from every check (markdownlint does the same), so the
    reported lines are body lines and a `name:` value never reads as prose.
    """
    src = open(path, encoding="utf-8").read()
    head, body = split_frontmatter(src)
    off = head.count("\n")
    rows, lines = [], body.split("\n")
    in_fence = False
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if len(ln) > line_length:
            rows.append((off + i, "MD013", f"line is {len(ln)} > {line_length}"))
        # MD033: raw inline HTML — but ONLY outside inline code.
        # ⚑ MY FIRST GUARD WAS WRONG AND THE WITNESS LINE PROVED IT.  It counted
        # backticks around the match with a condition that admitted `<n> bytes
        # allocated` — text plainly INSIDE code — and I nearly "fixed" the document
        # to satisfy my own false positive.  Printing the source line is what caught
        # it; a count would have sent me editing prose that was already correct.
        # Mask code spans first, then look: the same read-the-structure move
        # `mask_comments` makes for Agda.
        _bare = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), ln)
        for m in re.finditer(r"<(/?[A-Za-z][A-Za-z0-9-]*)(\s[^>]*)?>", _bare):
            rows.append((off + i, "MD033", f"inline HTML <{m.group(1)}>"))
        # MD032: a list item whose preceding line is neither blank nor a list item.
        if re.match(r"^\s{0,3}([-*+]|\d+[.)])\s", ln) and i > 1:
            prev = lines[i - 2]
            if prev.strip() and not re.match(r"^\s{0,3}([-*+]|\d+[.)])\s", prev) \
                    and not prev.startswith("  "):
                rows.append((off + i, "MD032", "list not preceded by a blank line"))
    # MD041 is a property of the BODY's first non-blank line, not of the file's.
    first = next((l for l in lines if l.strip()), "")
    if first and not first.startswith("#"):
        rows.append((off + 1, "MD041", "body does not open with a heading"))
    return rows


def lint_config_audit(cfg_path, paths=None, width=None):
    """[(verdict, rule, detail)] — is each exemption in a .markdownlint.json EARNED?

    ⚑ A DISABLED RULE IS A CLAIM, AND NOTHING CHECKED IT.  Writing the first config
    in this project I turned off FOUR rules; measured, two of them (MD025, MD033)
    fire ZERO times on the documents they govern — pure decoration, and the kind
    that rots into "we've always had that off".  The other two were different in
    kind: MD013 wanted a WIDTH the documents already had (configurable, not
    disableable) and MD041 is a genuine mismatch.  Only the last is an exemption.

    ⚑ THE VERDICTS ARE THE POINT, and there are four:
      `earned`      the rule fires and the exemption is load-bearing
      `unearned`    disabled but fires ZERO times — delete it, the rule costs nothing
      `paydown`     disabled and fires FEW times — the findings are fixable CONTENT;
                    fixing them retires the exemption (what happened to MD032)
      `configured`  not disabled, given a value that makes it agree with the writer
                    (MD013 = WRITER's --columns) — an agreement, not a suppression

    ⚑ AND `paydown` IS WHY THIS IS NOT A GENERATOR.  A tool that WRITES the config
    from the findings would emit `MD032: false` for two missing blank lines — it
    would encode the document's defects as permanent policy.  The audit reports what
    an exemption COSTS so a human decides; the fix for a small population is almost
    always the document.

    `paths` defaults to every .md beside the config (the scope a config governs).
    """
    import json
    cfg = json.loads(open(cfg_path, encoding="utf-8").read())
    base = os.path.dirname(os.path.abspath(cfg_path))
    if paths is None:
        paths = [os.path.join(base, f) for f in sorted(os.listdir(base))
                 if f.endswith(".md")]
    if width is None:
        w = cfg.get("MD013")
        width = w.get("line_length", 80) if isinstance(w, dict) else 80

    # Count findings per rule ACROSS the governed corpus, with every rule live.
    counts = {}
    for p in paths:
        try:
            for _ln, rule, _d in lint_shape(p, width):
                counts[rule] = counts.get(rule, 0) + 1
        except OSError:
            continue

    out = []
    for key, val in sorted(cfg.items()):
        if key.startswith("$"):
            continue
        n = counts.get(key, 0)
        if val is False:
            if n == 0:
                out.append(("unearned", key,
                            f"disabled but fires 0 times over {len(paths)} document(s)"
                            " — delete it; the rule costs nothing"))
            elif n <= 3:
                out.append(("paydown", key,
                            f"disabled, fires {n}x — few enough to FIX in the "
                            f"document and retire the exemption"))
            else:
                out.append(("earned", key, f"disabled; fires {n}x"))
        else:
            out.append(("configured", key,
                        f"given a value (not disabled); {n} finding(s) remain"))
    # A rule that fires and is NOT mentioned is fine — it is simply ON and being
    # obeyed or paid down. Reported so the corpus's real debt is visible.
    for rule, n in sorted(counts.items()):
        if rule not in cfg:
            out.append(("live", rule, f"ON and firing {n}x — real debt, not exempt"))
    return out


def semantic_damage(before: str, after: str):
    """[(kind, detail)] — meaning-changing edits a FIXPOINT check cannot see.

    ⚑ A FIXPOINT IS NOT A LOSSLESS TRANSFORM, AND THIS FILE CONFLATED THEM.
    `--fixpoint` asks *does normalize converge*; it never asks *does the converged
    text still mean the same thing*.  `--roundtrip` measured the drift and then told
    the reader to disregard it ("pandoc NORMALIZES by design — this is expected, not
    a failure"), deferring the whole verdict to convergence.  So both gates passed a
    write that damaged the document.

    ⚑ MEASURED, on a memory file (2026-08-03): the converged output ESCAPED `|` inside
    inline code — `cpu\\|memory\\|io`, making a PSI selector wrong as written — escaped
    every `[[wikilink]]` (the memory mesh's structure), escaped `~`, replaced straight
    quotes with smart quotes, and **DROPPED THE YAML FRONTMATTER ENTIRELY** (`name:`,
    `type:`, `originSessionId:` — a memory's identity).  It reported `[0]` rounds and
    `✓ FIXPOINT`.  Converged, idempotent, and wrong.

    ⚑ THE CLASS THIS BELONGS TO: `libcst` round-trips the Python corpus BYTE-FOR-BYTE,
    so "is it lossless" is the right precondition there; pandoc is a NORMALIZING
    converter, so the right precondition is idempotence PLUS a preservation check.
    Asking only the first question of a normalizer is what put a prose writer over a
    corpus of inline-code and link structure.

    Checks are on the DELTA, so a document that already contained an escape is not
    flagged — only text the transform ITSELF changed.
    """
    import re as _re
    out = []

    def _fm(s):
        return s.startswith("---\n") and "\n---\n" in s[4:]

    if _fm(before) and not _fm(after):
        out.append(("frontmatter-dropped",
                    "YAML frontmatter present before, absent after — for a memory "
                    "this is its name/type/provenance"))

    # Inline code whose content the transform altered (escapes inside `...`).
    def _codes(s):
        return _re.findall(r"`([^`\n]+)`", s)
    b_codes, a_codes = set(_codes(before)), set(_codes(after))
    escaped = [c for c in a_codes - b_codes if "\\" in c and c.replace("\\", "") in b_codes]
    if escaped:
        out.append(("escape-in-code",
                    "backslashes introduced INSIDE inline code (e.g. %s) — the code "
                    "no longer reads as written" % escaped[0]))

    # Wikilinks are structure in the memory mesh; escaping them breaks the edge.
    b_links = len(_re.findall(r"(?<!\\)\[\[", before))
    a_links = len(_re.findall(r"(?<!\\)\[\[", after))
    if b_links and a_links < b_links:
        out.append(("wikilink-escaped",
                    f"{b_links - a_links} of {b_links} [[links]] escaped — these are "
                    f"mesh edges, not text"))

    # Straight -> smart quotes changes literal content (and diffs noisily forever).
    if ("'" in before or '"' in before) and ("’" in after or "“" in after):
        if "’" not in before and "“" not in before:
            out.append(("smart-quotes",
                        "straight quotes converted to typographic quotes — literal "
                        "text changed"))
    return out


def fixpoint(path, opts=None, rounds=None):
    """Is normalization IDEMPOTENT — does normalize(normalize(x)) == normalize(x)?

    ⚑ THE QUESTION THAT ACTUALLY DECIDES THE WRITE PATH (user, 2026-08-01:
    *"Not strictly true. The question becomes whether or not the document can be
    normalized, found to be satisfactory, and then subsequent modifications
    roundtrip."*).

    I had reasoned: pandoc reflows the input, therefore a transform is unusable.
    That is the either/or trap — it treats PRESERVES-THE-INPUT and UNUSABLE as the
    only options.  Normalization is a FIXPOINT question:

        if  normalize(normalize(x)) == normalize(x)

    then a ONE-TIME accepted reflow moves the document to the fixpoint, and every
    subsequent transform round-trips exactly.  The one-time diff is then a
    reviewable migration, not a permanent tax — and the drift measured against the
    ORIGINAL is the wrong number to judge by, because it is paid once.

    ⚑ ITERATE TO CONVERGENCE, AND READ THE SEQUENCE — DO NOT JUDGE FROM A FIXED
    SMALL N (user, 2026-08-01).  My first version ran THREE rounds, saw
    `[1340, 899, 561]`, and I called it *"diverges monotonically"* — **the exact
    opposite of what those numbers say.**  A DECREASING delta is the signature of a
    sequence APPROACHING a fixpoint.  Run to convergence, the default writer gives
    `[1340, 899, 561, 400, 320, 176, 0]`: it CONVERGES, in seven rounds.  The
    `rounds=3` cutoff was the measurement bug that let the wrong verdict stand.

    ⚑ AND THE TERMINATION CONDITION IS STRICT DECREASE, NOT A ROUND CAP (user:
    *"You could allow it to iterate indefinitely so long as each round is strictly
    fewer modifications than the previous."*).  That is a well-founded descent —
    each delta is a non-negative integer, so a strictly decreasing sequence cannot
    run forever.  A round CAP is the other thing entirely: it is a CAPABILITY bound
    dressed as a termination bound, and this repo has already paid for that
    distinction once (`agda_lex.head_span`, where a `j - i < 6` limit silently
    dropped 136 of 401 multi-line headers).  My `rounds=25` would have mis-reported
    any document needing 26.

    So the loop runs while progress is STRICT, and stops on:
      * `n == 0`            → converged; the fixpoint exists
      * `n >= previous`     → a CYCLE or a stall; genuinely not a fixpoint
    `rounds` survives only as a runaway guard for a pathological input, defaulting
    to None (unbounded), which is the same shape `head_span` settled on.

    Returns (is_fixpoint, [n_changed per round], first_unstable_sample, converged_text).

    ⚑ THE CONVERGED TEXT WAS COMPUTED AND THROWN AWAY, WHICH IS WHY THE PAYDOWN
    NEVER HAPPENED.  This function ran the document all the way to its fixpoint and
    returned only the DELTAS — so `--table-style` could report *"48 rows → 0 after
    one pass"* while nothing could write that result, and the MD060 warnings kept
    firing on every edit.  I then dismissed them as "pre-existing" four times
    (user: *"this shouldn't happen; this is why we built the markdown structural
    manipulation tooling"*), which is what a census with no apply trains a reader to
    do.  Same shape as `split_lemmas` printing a COUNT while the file list sat in
    memory (§40's `--manifest`), and as `rewire()` returning an int so the prune had
    no population (§49).  The answer was one return value away, not a build.
    """
    src = open(path, encoding="utf-8").read()
    cur = _pandoc(src, opts or "markdown")
    # `flat_budget`: how many EQUAL deltas in a row before calling it a cycle.  This
    # is a TERMINATION bound (a repeat that never breaks is genuinely stuck), not a
    # capability bound — the measured worst plateau on this corpus is 3.
    deltas, sample, prev, flat, flat_budget = [], [], None, 0, 8
    while rounds is None or len(deltas) < rounds:
        nxt = _pandoc(cur, opts or "markdown")
        n, d = _diff(cur, nxt)
        deltas.append(n)
        if n and not sample:
            sample = d
        cur = nxt
        if n == 0:
            return True, deltas, [], cur
        # ⚑ A PLATEAU IS NOT A CYCLE, AND "STRICT DECREASE" CALLED IT ONE.  This
        # returned False on the first non-strict step, so `[…, 92, 56, 56]` read as a
        # STALL — and I then inferred from it that convergence is non-monotone in
        # column width, wrote that into a docstring, and built a survey around it.
        # MEASURED by running past the guard: `catalog/plan.md` at `--columns=120`
        # goes `[686, 571, 312, 114, 92, 56, 56, 56, 34, 34, 34, 0]` — it CONVERGES in
        # 12 rounds, descending in PLATEAUS.  Pandoc re-emits a block group at a time,
        # so several rounds can move the same count while different blocks settle.
        #
        # ⚑ THIS IS §50's DEFECT IN ITS OWN SUCCESSOR.  There a `rounds=3` cutoff made
        # a converging sequence read as divergent, and the fix was "iterate while
        # progress is STRICT".  That replaced a capability bound with a subtler one:
        # strictness is a stronger claim than descent, and the well-foundedness
        # argument only needs NO INCREASE plus eventual movement.  A repeat is
        # progress-so-far, not a fixpoint failure.
        #
        # The honest stopping conditions: `n == 0` (converged) or a delta that GROWS
        # (genuinely diverging), with a plateau budget so a true cycle still ends.
        if prev is not None and n > prev:
            return False, deltas, sample, cur          # increasing: real divergence
        if prev is not None and n == prev:
            flat += 1
            if flat >= flat_budget:
                return False, deltas, sample, cur      # a genuine cycle, not a plateau
        else:
            flat = 0
        prev = n
    return False, deltas, sample, cur


def _ast(path):
    import panflute
    import io
    j = _pandoc(open(path, encoding="utf-8").read(), "json")
    return panflute.load(io.StringIO(j))


def headers(path):
    """[(level, text)] — the section skeleton, structurally.

    A `grep '^#'` gets this MOSTLY right and fails on the cases that matter: a
    `#` inside a fenced code block is not a header, and a setext header (`===`
    underline) is one without a leading `#`.
    """
    import panflute
    doc = _ast(path)
    out = []
    for el in doc.content:
        if isinstance(el, panflute.Header):
            out.append((el.level, panflute.stringify(el).strip()))
    return out


def _hkey(s):
    """A heading's ANCHOR KEY: raw source and pandoc's rendered text, made comparable.

    ⚑ WHY THIS EXISTS — A HEADING WITH INLINE MARKUP WAS UNREACHABLE TO EVERY WRITE MODE.
    `spans()` anchors each pandoc heading by matching its RENDERED text against RAW source
    lines. Pandoc strips inline markup, so `## Building the tree: \\`make -j\\` self-throttles`
    renders as `Building the tree: make -j self-throttles` and the raw line never compared
    equal. That heading — and, because the scan is a forward cursor, EVERY SECTION AFTER IT —
    silently vanished from `spans()`.

    ⚑⚑ AND THE FAILURE WAS INVISIBLE IN EXACTLY THE WORST WAY: `--headers` (which calls
    `headers()` directly) listed the section, while `--replace-section` reported
    "no section heading contains …" for the same file — a message whose own ⚑ says it is
    "a fact about the QUERY". It was not: it was a fact about the ANCHORING, and it pointed
    the reader at their own spelling. Two modes disagreeing about one file is the
    census-keyed-on-one-spelling shape, in the tool that owns markdown.

    Measured on this repo's own CLAUDE.md: 3 of 9 headings carry backticks, so a third of the
    document — and everything following the first such heading — was unwritable.

    Normalizing (drop the markup characters, fold whitespace, casefold) makes the two
    spellings meet. It over-matches only where two headings differ solely by markup, and
    `find_section` already REFUSES ambiguity rather than picking one.
    """
    return " ".join(s.replace("`", "").replace("*", "").replace("_", "")
                     .replace("**", "").split()).strip().casefold()


def spans(path):
    """[(level, text, start, end)] — each section's LINE SPAN, 1-indexed, end EXCLUSIVE.

    ⚑ THE QUESTION `headers()` COULD NOT ANSWER, AND I REACHED FOR `awk` (user,
    2026-08-01: *"we have structural manipulation of markdown"*).  Appending to a
    section, or reading one whole, needs its BOUNDS — and `headers` returns text
    only, so the reflex was `awk 'NR>N && /^### /{print;exit}'`: a line-regex over a
    document whose whole point is that a `#` inside a fence is not a header.  The
    plan holds Agda fences with `--` comments and shell fences with `#` comments;
    that awk is one fenced heading away from silently truncating a section.

    ⚑ AND A SPAN ENDS AT THE NEXT HEADER OF THE SAME-OR-SHALLOWER LEVEL, never
    simply the next header: `### 69` containing a `#### sub` does not end at `sub`.
    Getting that wrong reads as a correct-looking short section, which is exactly
    the failure mode a line-regex produces and a reader cannot see.
    """
    import panflute
    doc = _ast(path)
    text = open(path, encoding="utf-8").read().split("\n")
    # panflute does not carry source positions, so anchor each header by matching
    # its rendered text against the raw lines IN ORDER — one forward scan, so a
    # repeated heading text cannot rebind to an earlier occurrence.
    hs, cursor = [], 0
    for lvl, txt in headers(path):
        for i in range(cursor, len(text)):
            line = text[i].lstrip()
            if line.startswith("#") and _hkey(line.lstrip("#")) == _hkey(txt):
                hs.append((lvl, txt, i + 1))
                cursor = i + 1
                break
    out = []
    for idx, (lvl, txt, start) in enumerate(hs):
        end = len(text) + 1
        for lvl2, _t2, s2 in hs[idx + 1:]:
            if lvl2 <= lvl:          # same-or-shallower CLOSES the section
                end = s2
                break
        out.append((lvl, txt, start, end))
    return out


def find_section(path, needle):
    """(level, text, start, end) for the ONE section whose heading contains `needle`.

    ⚑ AMBIGUITY IS A REFUSAL, NOT A FIRST-MATCH.  A substring that names two headings
    cannot be resolved by picking the earlier one — that is the silent-wrong-target class,
    and the target here is a WRITE.  Raises with both candidates named so the caller can
    disambiguate; a rewrite that edits the wrong section is unrecoverable by re-running.
    """
    hits = [s for s in spans(path) if needle.lower() in s[1].lower()]
    if not hits:
        raise LookupError(
            f"no section heading contains {needle!r} in {path}. "
            f"⚑ a fact about the QUERY — `--headers` lists what is there, with spans.")
    if len(hits) > 1:
        names = "; ".join(f"{h[0]*'#'} {h[1]!r}" for h in hits)
        raise LookupError(
            f"{needle!r} names {len(hits)} sections in {path}: {names}. "
            f"⚑ REFUSING rather than picking one — this is a write target.")
    return hits[0]


def replace_section(path, needle, body):
    """The document with ONE section's BODY replaced — heading kept, text spliced.

    ⚑⚑⚑ A LINE SPLICE, AND MY FIRST REASON FOR IT WAS WRONG.  I argued the AST route was
    unusable because `--roundtrip` reports **1215 changed lines** on `struct-tools/SKILL.md`
    — em-dashes to `---`, everything reflowed.  Operator, 2026-08-19: *"And that's a
    problem? It causes a compliant-by-construction file to result."*  Then measured:
    `--fixpoint` on that same file, and on `CLAUDE.md`, reports `[0]` — **already a
    fixpoint** under the tuned writer.  I quoted a figure from ONE instrument as a fact
    about ANOTHER; `--roundtrip` measures drift against the original under a default
    writer, `--fixpoint` measures convergence under the configured one, and only the
    second decides whether a write path is admissible.  Its own output says so.

    ⚑⚑ SO THE SPLICE IS CHOSEN FOR BLAST RADIUS, NOT CORRECTNESS.  An AST render is
    ADMISSIBLE here — and it rewrites the whole document, so a five-line edit arrives as a
    whole-file diff no reviewer can read, and any not-yet-converged file gets its migration
    silently bundled into an unrelated change.  A splice touches the lines it means to.
    ⚑ The normalization is worth having; it is a SEPARATE, REVIEWABLE migration
    (`--fixpoint --apply`), which is exactly how that mode already presents itself.

    So the AST is used for the QUESTION (where does this section begin and end, correctly
    about fences and nesting) and raw lines for the ANSWER.

    ⚑⚑ THIS IS THE MODE A SHELL APPEND WAS REACHING FOR.  `cat >> doc.md` grows a file
    without bound and without shape; `hook_structural_query` refuses it and — until now —
    could only name a READER, which made a correct refusal look like a bug (reported by
    cassian-observability, 2026-08-19).  Operator: *"mdstruct should be able to perform
    structural rewrites."*  A refusal that names an owning tool with no write mode is a
    gate that blocks without routing.

    ⚑ THE HEADING LINE IS NEVER TOUCHED.  Replacing it would move the anchor every other
    reader (`--coherence`, `--items`, `spans`) resolves against, so a rewrite could
    silently orphan the references pointing at it.  Body only; rename is a different verb.
    """
    lvl, txt, start, end = find_section(path, needle)
    lines = open(path, encoding="utf-8").read().split("\n")
    new = lines[:start] + body.rstrip("\n").split("\n") + lines[end - 1:]
    return "\n".join(new), (lvl, txt, start, end)


def append_to_section(path, needle, body):
    """The document with `body` appended INSIDE one section, before the next heading.

    ⚑ THE BOUNDED FORM OF THE THING `>>` DOES UNBOUNDED.  A shell append lands at
    end-of-file, which for a sectioned document is almost never where the content belongs
    — it silently migrates under whatever heading happens to be last.  This lands it in a
    NAMED section, so the write states where it goes and fails if that place is gone.

    ⚑ TRAILING BLANK LINES INSIDE THE SECTION ARE PRESERVED BENEATH the insertion, not
    swallowed: markdown block separation is load-bearing (MD032), and an append that eats
    the blank line before the next heading produces a document that renders differently
    from the one the author reviewed.
    """
    lvl, txt, start, end = find_section(path, needle)
    lines = open(path, encoding="utf-8").read().split("\n")
    body_lines = lines[start:end - 1]
    tail = 0
    while tail < len(body_lines) and not body_lines[len(body_lines) - 1 - tail].strip():
        tail += 1
    keep = body_lines[:len(body_lines) - tail] if tail else body_lines
    blanks = body_lines[len(body_lines) - tail:] if tail else []
    new = (lines[:start] + keep + [""] + body.rstrip("\n").split("\n")
           + blanks + lines[end - 1:])
    return "\n".join(new), (lvl, txt, start, end)


# ⚑ ONE LABEL GRAMMAR, DECLARED ONCE.  Both documents key on the same short codes
# (`T13`, `R7b-APPLY`, `A4-FNF`, `§62`); the audit is only as good as agreement
# about what a label IS, so the pattern lives here rather than in each query.
ITEM_RE = re.compile(
    # the established ASCII shape: T13, R7b-APPLY, A4-FNF
    r"\b([A-Z]{1,3}\d{1,2}[a-z]?(?:-[A-Z][A-Z-]+)?)\b"
    # ⚑⚑ OR A CIRCLED GLYPH — Ⓐ…Ⓩ / ⓐ…ⓩ / ⓪…⑳, WHICH THIS READER COULD NOT SEE.
    # MEASURED 2026-08-11: a plan organised around Ⓐ/Ⓑ/Ⓒ/Ⓕ/Ⓖ/Ⓛ/Ⓞ/Ⓢ/Ⓩ reported **41
    # labels, ZERO of them circled** — so the document's own structural reader was blind to
    # the things it was structured BY, and `--coherence` could not have found an orphan
    # among them. I then "fixed" it by inventing `TL-1`/`SQ-0`-style ASCII labels, which
    # ALSO fail this pattern (the digit must follow the letters directly), and re-measured
    # to find the count still 41 — the same defect one iteration later, in the repair.
    #
    # ⚑ AND THE GLYPHS ARE THE RIGHT CARRIER, WHICH IS WHY THE READER MOVES AND NOT THEM
    # (user, 2026-08-11: *"I don't usually type them. I copy/paste. Which means a lot of
    # AWESOME information can go into those unicode glyphs."*). Under copy/paste a label
    # costs one selection whatever it is, so the scarce resource is not keystrokes — it is
    # DISTINGUISHABILITY at a glance. A single codepoint can carry class and state where
    # `TL-1` carries a serial number. Optimising the label for typing was solving the wrong
    # constraint; the tool was simply unable to read the better one.
    #
    # ⚑⚑ AND THE RANGE MUST COVER THE WHOLE ENCLOSED-ALPHANUMERICS BLOCK, NOT THE PART I
    # HAPPENED TO USE. My first cut was `[Ⓐ-ⓩ⓪①-⑳]`, which reads as "circled letters and
    # numbers" and is not: ⓵ is U+24F5 (double-circled) and ⑴ is U+2474 (parenthesised), both
    # OUTSIDE it. Measured immediately — a table using ⓵–⓹ and ⑴–⑶ reported 60 labels with
    # every numbered row MISSING, so half the selector table was unaddressable while the
    # lowercase half resolved. **Third instance of one shape in a single turn**: a grammar
    # written from the instances in front of me, passing on everything except the next case.
    # U+2460–U+24FF is the block; take it whole rather than enumerating the glyphs I chose.
    r"|([①-⓿])"
    # ⚑⚑ FOURTH INSTANCE, FROM THE OTHER SIDE (2026-08-13). Having read the note above, a
    # selector was written using ❶❷❸ / ❖ / ◈ / ⬢⬡⬣ / ⊘⊗ — every one OUTSIDE U+24FF, so
    # `--items` reported the new table as **zero labels** while still resolving the RETIRED
    # glyphs quoted in its own retirement note. The lesson "take the block whole" was applied
    # to the reader and not to the choice of the next family.
    #
    # ⚑⚑ AND "TAKE THE BLOCK WHOLE" DOES NOT GENERALISE PAST THIS ONE BLOCK — WHICH IS WHY
    # THIS WIDENING IS NARROW. Enclosed Alphanumerics is entirely label-shaped, so taking it
    # whole is free. The blocks that family reached into are NOT: `⊗` and `⊘` are Mathematical
    # Operators (tensor, quotient) and this corpus writes them as MATHEMATICS in Agda prose;
    # Geometric Shapes carries `▪`/`▸` bullets. Admitting those blocks would report prose as
    # labels — the cries-wolf failure the note below records, at scale.
    #
    # So the widening is to the ENCLOSED-DIGIT DINGBATS ONLY: U+2776–U+2793 is ❶–❿, ➀–➉ and
    # ➊–➓ contiguously, three complete runs of enclosed digits and nothing else. No prose in
    # this corpus contains them, so the range cannot fire on text. **A family outside this
    # union is not a labelling family — pick from the block, or widen with a range that is
    # provably all-enclosed and say so here.**
    r"|([❶-➓])")

# ⚑ NOT EVERY CAPITALISED-WORD-WITH-DIGITS IS A LABEL.  `ITEM_RE` matches the SHAPE
# `T13`/`R7b-APPLY`, and prose contains that shape too: `PY2` (as in "vendored PY2
# setuptools", §67) reported as an UNWITNESSED item.  A grammar this permissive
# will keep finding them, and each false row teaches the reader to skim the census
# — the cries-wolf failure §63/§64 record.  Declared here rather than filtered at
# the call site, so `--items` and `--coherence` cannot disagree about what a label
# is.  ⚑ THIS IS AN ALLOW-LIST OF NON-LABELS AND IT CAN ROT; `M5`'s declared
# lifecycle in `worklist.md` is the durable fix, and this is the stopgap until it
# lands.
# ⚑ AND I NEARLY PUT `S3` AND `S5` IN IT — `S3` IS A LIVE ITEM (the
# `sppf_node_index` main()).  Listing a real label as a non-label makes the audit
# silently stop reporting a genuine orphan, which is strictly worse than the noise
# it removes.  **Exactly the `B1`/`Bijection` near-miss from §64, one section
# later.**  Only tokens that are NEVER worklist labels belong here.
NON_LABELS = {"PY2", "PY3", "UTF8", "SHA1", "SHA256", "GF2", "GL3"}
SECT_RE = re.compile(r"§(\d{1,2}[a-z]?)")


def _text(path):
    """UTF-8 text of a `.md`. ⚑⚑ ⟡vfs-chokepoints — THE ONE READ FOR THIS FAMILY.

    All five call sites (`items`, `label_families`, `coherence` ×2, `superseded`)
    route here, so this single `vfs.read` is the whole line-oriented `.md` surface —
    which is what makes it the chokepoint rather than five separate `open()`s.

    ⚑⚑ THIS MIGRATION IS BEHAVIOUR-PRESERVING AT EVERY CALL SITE, AND I NEARLY WROTE
    THAT IT WAS NOT.  The first draft of this docstring claimed the lift newly
    separates a directory from an absence for `label_families` — it does not.  That
    guard catches `(OSError, UnicodeDecodeError)`, and `IsADirectoryError` IS an
    `OSError`, so a directory was swallowed there before and is swallowed there now.
    Recording the wrong claim rather than deleting it: the seam having three arms does
    not mean a CALLER distinguishes them, and asserting the improvement without
    checking the caller's `except` clause is how a migration reports itself green.
    **Where the distinction gets USED is the caller's decision, and none of these five
    has made it yet.**

    ⚑ SO WHAT THE LIFT BUYS HERE IS THE SEAM, NOT A CHANGED VERDICT.  The exception
    types are preserved exactly: `require()` raises `FileNotFoundError` (an `OSError`)
    for ABSENT, `.text()` raises `UnicodeDecodeError` for a bad byte, and `r.error`
    re-raises the original `OSError` for BROKEN.  Every existing `except` clause keeps
    working UNCHANGED — the lift is ADDITIVE, the same way `Presence` compares equal to
    its own name for an unmigrated caller.  What is now POSSIBLE, and was not, is for a
    call site to ask which arm fired.

    ⚑ AND THE READ IS BYTES-FIRST WITH A STRICT DECODE.  `vfs.read` hands back raw
    bytes so the codec is chosen here rather than by the environment; `.text()` is
    strict, so a bad byte in a plan document raises instead of yielding replacement
    chars that a label regex would happily scan and under-count.
    """
    r = vfs.read(path)
    if r.presence is vfs.Presence.BROKEN:
        # ⚑ A BROKEN READ IS NOT A MISSING DOCUMENT — raising the cause makes a
        # directory-as-document surface as itself rather than as an absence.
        #
        # ⚑⚑ AND THIS BRANCH IS *REDUNDANT* — BY THE TWO BODIES BELOW, NOT BY A TEST
        # COUNT.  An earlier version of this note justified the redundancy with "stubbing
        # it to `if False:` leaves the suite at 67/67", which is a fact about the SUITE
        # standing in for a fact about the CODE: a green suite equally describes a case
        # nobody wrote.  The mechanism, re-derived from the source (cite the SYMBOL, never
        # a line — a comment here that cited a line number is exactly the drift this repo
        # has recorded against itself):
        #   * `vfs.Result.__bool__` returns True for `Presence.PRESENT` and for NOTHING
        #     else, so on BROKEN the fallthrough `r.text() if r else r.require()` takes
        #     the `require()` arm — not the `.text()` arm.
        #   * `vfs.Result.require` returns on PRESENT, raises `FileNotFoundError` on
        #     ABSENT, and ENDS in `raise self.error` — which is not an *equivalent*
        #     exception, it is the SAME EXPRESSION ON THE SAME OBJECT as this line.
        #   * `pycodemod --rivals require` reports two defs of that name, and the other
        #     (`jea/metalanguage/sorted_stream.py`, signature `(self, want, who)`) cannot
        #     be the one called: `r` is a `vfs.Result` and the arities differ.  So no call
        #     path resolves `r.require()` to a different body.
        # Re-derive from those three if `vfs` moves; do not re-derive from a test count.
        #
        # ⚑ KEPT ANYWAY, AND THE REASON IS THE READER, NOT THE BEHAVIOUR.  `return
        # r.text() if r else r.require()` is correct and says nothing: a reader cannot
        # tell from it that BROKEN exists, let alone that it is handled.  The explicit
        # arm makes the three-valuedness visible at the site that consumes it, which is
        # the whole product here.  **Recorded as redundant so a later reader deletes it
        # knowingly rather than discovering the redundancy and assuming a bug.**
        #
        # ⚑⚑ AND IT IS A DIFFERENT CLASS FROM THE REDUNDANT GUARDS THIS REPO DELETES.
        # Those change an outcome they do not control — a carve-out granting exemption on
        # a flag's mere presence, a census that reads ARMED while the thing is off.  This
        # arm changes NO outcome in either direction: taken or stubbed, the same exception
        # object leaves `_text`.  It is a documented alias for the fallthrough, not a
        # false protection, so the delete-on-sight reflex does not apply to it.
        raise r.error
    # ABSENT → FileNotFoundError, PRESENT → the decoded text (strict; a bad byte is a
    # UnicodeDecodeError, never a silently mangled document).
    return r.text() if r else r.require()


def items(path):
    """{label -> [line numbers]} for every worklist label the document MENTIONS.

    ⚑ MENTION, NOT DEFINITION — and the distinction is the whole audit.  A todo
    DEFINES an item (`⚡ T13 — …`); the plan WITNESSES it (a section that measured
    its population).  A label appearing in only one document is the coherence gap
    §24/§25 found by eye: either an item with no evidence, or evidence with no item.
    """
    out = {}
    for i, line in enumerate(_text(path).splitlines(), 1):
        for m in ITEM_RE.finditer(line):
            # ⚑ ON AN ALTERNATION ONLY ONE GROUP FIRES AND THE REST ARE `None` — and
            # `None in NON_LABELS` is False, so a naive read sails past the guard and keys the
            # dict on `None`, silently merging every glyph label into one bogus row.
            #
            # ⚑⚑ AND THIS READ USED TO COUNT THE GROUPS (`m.group(1) or m.group(2)`) UNDER A
            # COMMENT DECLARING "THE ALTERNATION HAS TWO GROUPS" — so widening `ITEM_RE` with a
            # third alternative (the enclosed-digit dingbats, 2026-08-13) left the new family
            # matching in the pattern and DROPPED here: `--items` reported zero of them and the
            # regex looked correct in isolation. The arity was documented, and documenting it
            # is what made changing it silent. **Take whichever group fired, without knowing
            # how many there are** — then the next alternative costs nothing and cannot regress
            # this line.
            lab = next(filter(None, m.groups()), None)
            if lab in NON_LABELS:
                continue
            out.setdefault(lab, []).append(i)
    return out


def label_families(paths, known=None):
    """DISCOVER candidate label families across a corpus — do NOT match a known vocabulary.

    ⚑⚑⚑ THIS MODE EXISTS BECAUSE `ITEM_RE` HAS BEEN WIDENED FOUR TIMES, EACH TIME TO THE FAMILY
    IN FRONT OF THE AUTHOR, AND EACH WIDENING PASSED ON EVERYTHING EXCEPT THE NEXT CASE.  The
    comments above `ITEM_RE` record all four verbatim: circled glyphs invisible while a document
    was STRUCTURED by them; a "fix" inventing `TL-1` labels the pattern also could not read; the
    U+24F5/U+2474 rows missing from a selector table; and a new ❶❷❸/⬢/⊘ family reporting ZERO while
    the RETIRED glyphs quoted in its own retirement note still resolved.

    ⚑⚑ SO A FIFTH GUESSED VOCABULARY WOULD BE THE FIFTH INSTANCE, NOT A FIX.  `--items` answers
    *"where is label X"* against a declared grammar; this answers the prior question the grammar
    cannot: **what shapes in this corpus are BEING USED as labels, including ones no grammar knows.**
    It reports candidates for judgement and deliberately does not decide.

    Method: scan for *repeated short tokens in label POSITION* — leading a line, or bracketed,
    or immediately before an em-dash/colon — and cluster them by SHAPE rather than by value.
    Shape is derived per-character (`A`=upper, `a`=lower, `9`=digit, `-`=punct, `U+XXXX` block
    name for non-ASCII), so `T13` and `R7b` share a shape, `ABCDEF-GHIJ` gets its own, and an
    unfamiliar glyph is reported by its UNICODE BLOCK — which is how a family nobody has seen
    becomes visible instead of invisible.

    ⚑ `known` (default `ITEM_RE`) marks which candidates the CURRENT grammar already reads, so the
    output separates *"seen and matched"* from *"seen and UNREADABLE"*.  The second column is the
    finding; the first is the control that proves the scan works at all.

    Returns {shape: {"examples": [...], "count": int, "files": int, "read": bool}}.
    """
    import unicodedata
    known = known or ITEM_RE

    def _shape(tok):
        out = []
        for ch in tok:
            if ch.isupper() and ch.isascii():   out.append("A")
            elif ch.islower() and ch.isascii(): out.append("a")
            elif ch.isdigit() and ch.isascii(): out.append("9")
            elif ch.isascii():                  out.append(ch)
            else:
                try:
                    blk = unicodedata.name(ch).split()[0]
                except ValueError:
                    blk = "U%04X" % ord(ch)
                out.append("<%s>" % blk)
        # collapse runs so T13 and R7b and A4 share one shape
        sq, prev = [], None
        for s in out:
            if s != prev:
                sq.append(s)
                prev = s
        return "".join(sq)

    # label POSITION, not label spelling: line-leading, bracketed, or before — / :
    pos = re.compile(
        r"(?:^\s*[-*|]?\s*|\(|\[|\|\s*)(\S{1,24}?)(?=\s*(?:[—:）\]|]|\s+—|\s*$))",
        re.MULTILINE)

    fam = {}
    for p in paths:
        try:
            text = _text(p)
        except (OSError, UnicodeDecodeError):
            continue
        seen_here = set()
        for m in pos.finditer(text):
            tok = m.group(1).strip("*`_.,;")
            if not tok or len(tok) > 24 or tok in NON_LABELS:
                continue
            if not any(c.isalnum() or ord(c) > 127 for c in tok):
                continue
            if tok.isdigit() or (tok.isascii() and tok.islower()):
                continue                      # bare numerals / prose words are not labels
            sh = _shape(tok)
            e = fam.setdefault(sh, {"examples": [], "count": 0, "files": 0,
                                    "read": bool(known.search(tok))})
            e["count"] += 1
            if tok not in e["examples"] and len(e["examples"]) < 6:
                e["examples"].append(tok)
            if sh not in seen_here:
                e["files"] += 1
                seen_here.add(sh)
    return fam


def coherence(plan, worklist):
    """(orphan_items, unwitnessed_items, dangling_sections) — both directions.

    ⚑ MUTUAL CONSISTENCY IS NOT COVERAGE (§25), so this reports THREE populations
    and never one verdict:
      · orphan_items      — in the WORKLIST, never mentioned in the plan.  The item
                            has no recorded evidence; its figures are unsourced.
      · unwitnessed       — in the PLAN, never in the worklist.  A measured finding
                            nobody scheduled — §24's dominant direction (three plan
                            items had no todo at all).
      · dangling_sections — a `§N` cited by the worklist that the plan does not have
                            as a section.  A citation to nothing reads as provenance.
    """
    p_items, w_items = items(plan), items(worklist)
    orphan = sorted(set(w_items) - set(p_items))
    unwitnessed = sorted(set(p_items) - set(w_items))
    # ⚑ SECTION NUMBERS COME FROM THE TEXT, NOT FROM PANDOC.  Routing this through
    # `headers()` made the whole coherence audit require panflute — and this is
    # precisely the query that must work in a bare environment, because it is what
    # a GATE would call.  A `^#+ N.` line is unambiguous for this document's
    # convention, and the fenced-code hazard `headers()` exists to dodge cannot
    # arise: a fence containing `### 62. …` is not a thing this corpus produces.
    # ⚑ A SUB-ITEM IS A SECTION TOO, AND MISSING THAT MADE A CORRECT CITATION READ
    # AS DANGLING.  This document numbers sub-findings as BOLD paragraphs
    # (`**6d. Armed but not firing**`, `**9a.**`, `**7b-bis.**`) rather than
    # headings — a deliberate convention, since a sub-finding is part of its
    # parent's argument.  Keying only on `^#+ N.` therefore reported `§6d` as a
    # reference to nothing, on a citation that is exactly right.
    #
    # A false DANGLING is the worse direction: the audit's whole value is that a
    # non-zero count means act, so one bogus row teaches the reader to skim it —
    # the same "census that cries wolf" failure §63/§64 record.  Both spellings
    # count, and `-bis`/`-part2` style suffixes are admitted because the corpus
    # writes them.
    _txt = _text(plan)
    have = {m.group(1) for m in re.finditer(
        r"^#+\s+§?(\d{1,2}[a-z]?(?:-\w+)?)\.", _txt, re.M)}
    have |= {m.group(1) for m in re.finditer(
        r"^\*\*§?(\d{1,2}[a-z]?(?:-\w+)?)\.", _txt, re.M)}
    cited = {m.group(1) for m in SECT_RE.finditer(_text(worklist))}
    dangling = sorted(cited - have)
    return orphan, unwitnessed, dangling


# ⚑ A FIGURE IS A CLAIM WITH A DATE.  This arc has quoted six numbers that a LATER
# section superseded (589-vs-1322 leaves, 21-vs-27 gates, 113-vs-345 leaf-own,
# 12%-vs-19%, 95-vs-81 conduits, 66-vs-216 ban additions).  Each was found by a
# human noticing; none by the document.  A number that appears with two different
# values next to the SAME noun is the mechanical signature.
FIGURE_RE = re.compile(r"(\d[\d,]*)\s+((?:[a-z][\w-]*\s+){0,2}"
                       r"(?:leaves|leaf|gates?|modules?|files?|keys?|"
                       r"consumers?|importers?|sites?|cases?|suites?|additions?))")


def superseded(path):
    """[(phrase, [(value, line)…])] where ONE PHRASE carries conflicting values.

    ⚑ MY FIRST PREDICATE KEYED ON THE BARE NOUN AND WAS USELESS.  It reported 12
    nouns with up to 40 values each — "2 files" and "2941 files" colliding as a
    supersession when they are different measurements in different sections.  A
    census that wide is one nobody reads, which is the failure it exists to
    prevent: `report the population, not the tally` says nothing if the population
    is noise.

    The distinguishing fact is the QUALIFIED phrase, not the noun: `589 leaves` and
    `1322 leaves` are the same claim measured twice, while `2 files` and `2941
    files` never share a modifier.  So the key is the noun PLUS its preceding
    words, and a collision requires the SAME phrase — which is what made the six
    real supersessions this arc hit ("589-vs-1322 leaf/leaves", "21-vs-27 gates
    wired") mechanically visible while the coincidences fall away.

    Still reports the SPREAD rather than a verdict: two values for one phrase is
    usually a supersession (the later wins) but is sometimes two real populations.
    The tool surfaces the collision; a reader decides.
    """
    seen = {}
    for i, line in enumerate(_text(path).splitlines(), 1):
        for m in FIGURE_RE.finditer(line):
            val = int(m.group(1).replace(",", ""))
            # the FULL captured phrase, normalised — modifiers included
            phrase = " ".join(m.group(2).lower().split()).rstrip("s")
            # ⚑ MY BARE-NOUN FILTER ALSO KILLED THE CASE IT EXISTS TO FIND.
            # `" " not in phrase` was meant to drop unqualified nouns, but the
            # regex captures 0-2 modifiers, so `589 leaves` yields the phrase
            # `leave` with no space and was discarded — the tool reported NOTHING
            # for the very supersession (589-vs-1322) that motivated it.  Caught
            # only because the S2 fix let the case's failure be SEEN at all.
            #
            # The real discriminator is not "does the phrase have a modifier" but
            # "do two values disagree under the SAME phrase" — so keep every
            # phrase and let the collision test decide.  Noise is then bounded by
            # the modifiers the corpus actually writes, which is what made the
            # 12-nouns-of-noise census collapse to 2.
            if not phrase:
                continue
            seen.setdefault(phrase, {}).setdefault(val, []).append(i)
    # ⚑ THE TWO CASES WERE IN GENUINE TENSION, AND THAT IS THE FINDING.  `589
    # leaves` vs `1322 leaves` (a real supersession) and `2 files` vs `2941 files`
    # (a coincidence) are STRUCTURALLY IDENTICAL — same noun, two values, no
    # modifier either way.  No phrasing rule separates them, so my first two
    # attempts each satisfied one case by breaking the other.
    #
    # What DOES separate them is ORDER OF MAGNITUDE.  A supersession re-measures
    # one population, so its values stay within a factor of ~10 (589→1322, 21→27,
    # 113→345, 12%→19%, 95→81, 66→216); a coincidence spans the document's whole
    # numeric range (2 vs 2941).  So report a collision only when the values are
    # PLAUSIBLY THE SAME QUANTITY, and say so — this is a heuristic on a reported
    # census, not a gate verdict, and the reader still decides.
    RATIO = 10
    out = []
    for phrase, vals in seen.items():
        if len(vals) < 2:
            continue
        lo, hi = min(vals), max(vals)
        if lo == 0 or hi / lo > RATIO:
            continue            # too far apart to be one population re-measured
        out.append((phrase, sorted((v, ls[0]) for v, ls in vals.items())))
    out.sort(key=lambda kv: -len(kv[1]))
    return out


def tables(path):
    """[(index, n_rows, n_cols, header_cells)] — every table in the document.

    ⚑ THE QUESTION THIS EXISTS FOR: the plan's canonical DAG table has outlived
    its own corrections FOUR times.  Finding tables — and later, reading their
    cells — is the precondition for ever checking one mechanically instead of by
    a human noticing.
    """
    import panflute
    doc = _ast(path)
    out = []

    def walk(el, doc):
        if isinstance(el, panflute.Table):
            head = []
            try:
                for row in el.head.content:
                    head = [panflute.stringify(c).strip() for c in row.content]
                    break
            except Exception:
                pass
            nrows = sum(len(tb.content) for tb in el.content)
            out.append((len(out), nrows, len(head), head))
        return None

    doc.walk(walk)
    return out


def table_rows(path, index=None, where=None):
    """[(table_index, row_cells)] — the CELLS, optionally filtered.

    ⚑ THE GAP A RESEARCH AGENT NAMED AND COULD NOT CLOSE (2026-08-04).  `tables()`
    reports a table's header and SIZE; there was no way to read a ROW.  So the
    963-row `catalog/reuse-index.md` name→home index — the repo's designated
    FIRST CHECK for "where does this concept live" — could not be queried for a
    name by the tool that owns it.  A read-only agent hit this, named the missing
    mode correctly, and routed to `agda_defs.py` instead; the gap then survived
    every later dispatch because naming it is all a read-only agent can do.

    ⚑ AND `tables()`'s OWN DOCSTRING ANTICIPATED IT — *"Finding tables — and later,
    reading their cells — is the precondition for ever checking one mechanically"*.
    The mode was specified in prose, in this file, and never built.  A capability
    named in a docstring is not a capability; that is the same shape as a gate
    that is baselined and wired into nothing.

    `where` is a substring match over the row's cells (case-folded).  Returns
    (index, cells) pairs so a filtered read still says WHICH table a row came
    from — a row without its table is the bare-count defect one level down."""
    import panflute
    doc = _ast(path)
    out = []
    seen = [0]

    def walk(el, doc):
        if isinstance(el, panflute.Table):
            ti = seen[0]
            seen[0] += 1
            if index is not None and ti != index:
                return None
            for tb in el.content:
                for row in tb.content:
                    cells = [panflute.stringify(c).strip() for c in row.content]
                    if where is not None:
                        hay = " \x00 ".join(cells).casefold()
                        if where.casefold() not in hay:
                            continue
                    out.append((ti, cells))
        return None

    doc.walk(walk)
    return out


def why_not_pipe(path, opts=None):
    """[(header, reason)] — which tables pandoc will NOT emit as pipe tables, and why.

    ⚑ WIDTH IS NOT THE ONLY REASON, AND ASSUMING IT WAS COST TWO SEARCHES (user,
    2026-08-01: *"sounds like width isn't the problem, then"*).  MEASURED: at
    `--columns=2000` the plan still emits multiline tables, so a width-only explanation
    is exhausted — the bisection correctly REFUSED rather than returning a boundary that
    does not exist.

    The pipe-table format cannot express certain content, whatever the budget:
      * a cell containing a BLOCK (multiple paragraphs, a list, a fenced block) — pipe
        cells are single-line inline content by construction;
      * a cell containing a HARD LINE BREAK;
      * a table with NO header row (pipe tables require one).
    Anything else is a width question.

    This reads the panflute AST rather than the emitted text, so it says which table and
    which cause instead of leaving a reader to infer a mechanism from a symptom — the
    error I made four times in this sitting before the tool could answer it.
    """
    import panflute
    doc = _ast(path)
    out = []

    def cell_blocked(cell):
        for b in getattr(cell, "content", []):
            if not isinstance(b, panflute.Plain) and not isinstance(b, panflute.Para):
                return f"cell holds a {type(b).__name__} block"
            for el in getattr(b, "content", []):
                if isinstance(el, panflute.LineBreak):
                    return "cell holds a hard line break"
        if len([b for b in getattr(cell, "content", [])]) > 1:
            return "cell holds multiple blocks"
        return None

    def walk(el, doc):
        if isinstance(el, panflute.Table):
            head = ""
            try:
                for row in el.head.content:
                    head = " | ".join(panflute.stringify(c).strip()[:22]
                                      for c in row.content)
                    break
            except Exception:
                pass
            if not head:
                out.append(("(no header row)", "pipe tables require a header row"))
                return
            for body in el.content:
                for row in getattr(body, "content", []):
                    for c in getattr(row, "content", []):
                        r = cell_blocked(c)
                        if r:
                            out.append((head, r))
                            return
    doc.walk(walk)
    return out


def narrowest_width(paths, lo=60, hi=2000, base=None):
    """(width, [(w, converges, all_pipe)]) — narrowest `--columns` meeting BOTH conditions.

    THE CONJUNCTION (user, 2026-08-01: *"now you have a supremum bound; binary search for
    this AND this other condition"*):
      1. **converges** — `normalize(normalize(x)) == normalize(x)`, so a write is stable;
      2. **all tables stay PIPE** — no multiline fallback, which is what trades MD060 for
         MD035/MD003/MD023 (MEASURED: at 120 all 50 of the plan's tables went multiline).

    ⚑ AND BISECTION IS SOUND ON (2) IN A WAY IT WAS NOT ON (1) ALONE.  "Every table fits
    the budget" is monotone by construction — widening can only keep a table inside it —
    whereas my earlier claim that CONVERGENCE is non-monotone was an artifact of a
    termination bug (§70e).  So (2) supplies the genuine boundary and (1) is checked at
    the answer rather than searched on.  *That is the difference between a search whose
    monotonicity is asserted and one whose monotonicity is structural.*

    ⚑ THE SUPREMUM IS KNOWN: at 999 the corpus is all-pipe and converges, so a satisfying
    width EXISTS and the bisection has a valid upper bracket.  Without that the search
    would be looking for a boundary that might not be there — which is exactly the state
    the first attempt was in.

    `paths` is every document the setting governs; the answer must satisfy ALL of them,
    since `WRITER` is one constant for the whole corpus.
    """
    tried = []

    def ok(w):
        opts = (base or "markdown-smart+pipe_tables") + f" --columns={w} --wrap=preserve"
        conv = allpipe = True
        for p in paths:
            try:
                if not fixpoint(p, opts)[0]:
                    conv = False
            except Exception:
                conv = False
            # emit at this width to a temp file and read back the table syntax
            import tempfile
            tf = os.path.join(tempfile.mkdtemp(), os.path.basename(p))
            try:
                open(tf, "w", encoding="utf-8").write(
                    _pandoc(open(p, encoding="utf-8").read(), opts))
                f = table_forms(tf)
                if f.get("multiline") or f.get("grid"):
                    allpipe = False
            except Exception:
                allpipe = False
        tried.append((w, conv, allpipe))
        return conv and allpipe

    if not ok(hi):
        return None, tried
    if ok(lo):
        return lo, tried
    while hi - lo > 1:                       # lo fails, hi holds; bisect the boundary
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi, tried


def table_forms(path):
    """{form -> n} — which SYNTAX each table is written in: pipe / multiline / grid / simple.

    ⚑ THE QUESTION `--columns` ACTUALLY DECIDES, AND NOTHING COULD ASK IT.  `+pipe_tables`
    ENABLES the pipe extension; it does not FORCE pipe output — pandoc falls back to a
    MULTILINE table (space-aligned columns between dashed rules) whenever a table exceeds
    the column budget.  So a narrower `--columns` silently changes table SYNTAX, and the
    IDE then reports the dashed rules as MD035 hr-style and the header row as MD003
    setext.  MEASURED after normalizing at 120: MD060 went to 0 and MD035/MD003/MD023
    appeared in its place.

    ⚑ AND I PROBED FOR THIS FOUR TIMES BY HAND FIRST — `grep -c '^-\\{100,\\}'`, a
    `startswith('---') and ' ---' in l` scan (which found 0, because it looked for GRID
    syntax that pandoc never emitted), an `awk` over pandoc output.  Each was a
    line-regex over a document whose structure this module exists to read, and each
    measured the wrong shape.  *The tell was inferring a mechanism ("grid tables") from
    a symptom instead of reading the emitted lines.*
    """
    src = open(path, encoding="utf-8").read().split("\n")
    forms = {"pipe": 0, "multiline": 0, "grid": 0}
    i = 0
    while i < len(src):
        l = src[i]
        s = l.strip()
        if s.startswith("+-") and set(s) <= set("+-="):
            forms["grid"] += 1
            i += 1
            continue
        # a dashed rule with NO pipes opens/closes a multiline table
        if s and set(s) <= set("- ") and s.count("-") > 8 and "|" not in l:
            forms["multiline"] += 1
            i += 1
            continue
        if s.startswith("|") and set(s) <= set("|-: "):
            forms["pipe"] += 1
        i += 1
    # each multiline table has 3 rules (open, header-sep, close); pipe tables 1 sep row
    forms["multiline"] = round(forms["multiline"] / 3)
    return forms


def table_style(path):
    """[(lineno, kind)] — pipe-table rows whose spacing is non-canonical.

    ⚑ THE PAYDOWN THE FIXPOINT RETIRES FOR FREE (user, 2026-08-01: *"that's what
    inspired me to bring it up in the first place"*).  The IDE reports MD060
    (`Table pipe is missing space to the left/right`) on this document, and the
    reflex is to hand-fix pipes or to silence the rule.  Neither is right: pandoc
    emits CANONICAL pipe spacing by construction, so a document AT THE FIXPOINT
    cannot violate MD060 at all — the class is not fixed, it is made
    unrepresentable.  *A normalizer's fixpoint is a gate over every property the
    normalizer canonicalizes*, which is a strictly stronger guarantee than a linter
    that reports violations after the fact.

    Detects the two MD060 shapes on a delimiter or content row: a `|` with no
    space on a side where canonical style has one.  Reported per-line so the count
    is a POPULATION, not a tally.
    """
    import re
    out = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        s = line.rstrip("\n")
        if not s.strip().startswith("|") or s.count("|") < 2:
            continue
        body = s.strip()
        # canonical: "| a | b |" — every interior pipe flanked by a space
        for m in re.finditer(r"\|", body):
            j = m.start()
            if j == 0 or j == len(body) - 1:
                continue
            if body[j - 1] != " ":
                out.append((i, "missing space LEFT of pipe"))
                break
            if j + 1 < len(body) and body[j + 1] != " ":
                out.append((i, "missing space RIGHT of pipe"))
                break
    return out


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    # ⚑ THE AUDIT QUERIES ARE PURE TEXT AND MUST RUN WITHOUT PANDOC.  Everything
    # below the panflute guard is skipped when the dependency is absent — which is
    # S2's defect (an absent dep silently scores as a pass, `jea_circuit.py:197`'s
    # class).  `items`/`coherence`/`superseded` read the raw document, so they
    # belong ABOVE the guard: the coherence audit is exactly the thing that must
    # keep working in a bare environment, since it is what a gate would call.
    import tempfile as _tf
    _d = _tf.mkdtemp()
    _p = os.path.join(_d, "plan.md")
    _w = os.path.join(_d, "wl.md")
    open(_p, "w", encoding="utf-8").write(
        "# 1. Something\n\nT13 was measured here.  See also R7b-APPLY.\n"
        "\n# 2. Other\n\nA4-FNF has 40 mechanical files and 80 other files.\n")
    open(_w, "w", encoding="utf-8").write(
        "- T13 done (§1)\n- R7b-APPLY pending (§2)\n- C99 pending (§7)\n")
    check("items() finds every label a document mentions",
          sorted(items(_w)), ["C99", "R7b-APPLY", "T13"])

    # ⚑⚑⚑ `_text`'s THREE ARMS, STARVED AGAINST EACH OTHER (⟡vfs-chokepoints).
    # THIS SUITE COULD NOT SEE THE DISTINCTION AND I MEASURED THAT RATHER THAN
    # ASSUMING IT: with the BROKEN branch stubbed out, the suite still read 62/62.
    # A migration whose all-clear is identical to its found-something is not verified
    # by that all-clear, so the cases below exist to make the arms observable.
    #
    # ⚑ WHAT IS ASSERTED IS THE EXCEPTION TYPE, because that is what every caller's
    # `except` clause actually keys on — `label_families` catches
    # `(OSError, UnicodeDecodeError)` and skips.  Preserving the TYPES is what makes
    # this migration additive; asserting them is what makes that claim checkable.
    check("⚑ PRESENT: a document reads back as text",
          isinstance(_text(_w), str), True)
    _missing = os.path.join(_d, "nosuchdoc.md")
    _absent_exc = None
    try:
        _text(_missing)
    except Exception as _e:                       # noqa: BLE001 — the TYPE is the assertion
        _absent_exc = type(_e).__name__
    check("⚑ ABSENT raises FileNotFoundError (an OSError, so existing guards hold)",
          _absent_exc, "FileNotFoundError")
    _broken_exc = None
    try:
        _text(_d)                                  # a DIRECTORY — present, but not a document
    except Exception as _e:                       # noqa: BLE001
        _broken_exc = type(_e).__name__
    check("⚑ BROKEN raises IsADirectoryError — the read did NOT happen",
          _broken_exc, "IsADirectoryError")
    check("⚑⚑ ABSENT and BROKEN are DISTINCT outcomes, not one 'could not read'",
          _absent_exc == _broken_exc, False)
    # ⚑ AND A NON-UTF-8 DOCUMENT IS BROKEN, NOT SILENTLY MANGLED.  `vfs.read` hands
    # back bytes and `.text()` is STRICT, so a bad byte raises instead of yielding
    # replacement chars that `ITEM_RE` would scan and under-count without saying so.
    _bad = os.path.join(_d, "notutf8.md")
    open(_bad, "wb").write(b"\xff\xfe T13 not utf-8\n")
    _decode_exc = None
    try:
        _text(_bad)
    except Exception as _e:                       # noqa: BLE001
        _decode_exc = type(_e).__name__
    check("⚑ a non-UTF-8 document raises rather than decoding to mojibake",
          _decode_exc, "UnicodeDecodeError")
    # ⚑ AND PROSE THAT LOOKS LIKE A LABEL IS NOT ONE.  `PY2` (in "vendored PY2
    # setuptools") matched `ITEM_RE`'s shape and reported as UNWITNESSED.  BOTH
    # directions are pinned, because an over-eager NON_LABELS entry would silently
    # stop reporting a real orphan — I nearly added `S3`, which is a live item.
    _pw = os.path.join(_d, "prose.md")
    open(_pw, "w", encoding="utf-8").write("vendored PY2 code; see T13 and S3\n")
    _found = sorted(items(_pw))
    check("a prose token matching the label SHAPE is excluded",
          "PY2" in _found, False)
    check("...and real labels are still found", _found, ["S3", "T13"])
    # ⚑⚑ A CIRCLED GLYPH IS A LABEL, AND THIS READER WAS BLIND TO IT FOR THE WHOLE ARC.
    # MEASURED on the live plan: a document organised around Ⓐ/Ⓑ/Ⓒ/Ⓕ/Ⓖ/Ⓛ/Ⓞ/Ⓢ/Ⓩ reported
    # **41 labels, ZERO circled** — so `--coherence` could not have found an orphan among the
    # very items the plan was structured by, and `--items` answered a question about its own
    # GRAMMAR while reading as a fact about the document.
    #
    # ⚑ THE GLYPHS ARE THE RIGHT CARRIER (user: *"I don't usually type them. I copy/paste.
    # Which means a lot of AWESOME information can go into those unicode glyphs."*). Under
    # copy/paste the scarce resource is not keystrokes but DISTINGUISHABILITY, so the tool
    # moves to the label rather than the label to the tool. My first repair invented ASCII
    # `TL-1`-style labels instead — which ALSO fail `ITEM_RE` (the digit must follow the
    # letters directly), re-measured at still-41: the same blindness, one iteration later,
    # inside the fix for it.
    _gp = os.path.join(_d, "glyph.md")
    open(_gp, "w", encoding="utf-8").write(
        "Ⓑ is ready; Ⓒ1 landed. See also T13.\n")
    _gfound = sorted(items(_gp))
    check("a circled glyph is enumerable as a label", "Ⓑ" in _gfound, True)
    check("...alongside ASCII labels, not instead of them", "T13" in _gfound, True)
    # ⚑ THE TWO-GROUP TRAP, PINNED. The alternation makes `group(1)` None on a glyph match,
    # and `None in NON_LABELS` is False — so a naive `m.group(1)` would sail past the guard
    # and key the dict on `None`, silently MERGING every circled label into one bogus row.
    # A count alone would not show it; the row name is the evidence.
    check("no None-keyed row leaks from the alternation",
          [k for k in items(_gp) if not isinstance(k, str)], [])
    # ⚑⚑ THE WHOLE ENCLOSED-ALPHANUMERICS BLOCK, NOT THE GLYPHS I HAPPENED TO PICK. My first
    # range was `[Ⓐ-ⓩ⓪①-⑳]` — which READS as "circled letters and numbers" and is not: ⓵ is
    # U+24F5 (double-circled) and ⑴ is U+2474 (parenthesised), both outside it. A selector
    # table using ⓵–⓹ and ⑴–⑶ then enumerated with every numbered row MISSING while the
    # lowercase half resolved, so half the actions were unaddressable and the census still
    # looked plausible. THIRD instance of one shape in a single turn — a grammar written from
    # the instances in front of me. These cases span the block's corners so the next form
    # cannot fall outside it silently.
    _bp = os.path.join(_d, "block.md")
    open(_bp, "w", encoding="utf-8").write("① ⑴ Ⓐ ⓐ ⓪ ⓵ ⓿ ⒜ ⒈ all label\n")
    _bfound = set(items(_bp))
    check("parenthesised, double-circled and negative forms all enumerate",
          all(g in _bfound for g in ("①", "⑴", "Ⓐ", "ⓐ", "⓪", "⓵", "⓿", "⒜", "⒈")), True)
    # ⚑⚑ FOURTH INSTANCE, FROM THE OTHER SIDE (2026-08-13). The block above was taken whole,
    # and then a NEW selector was written in ❶❷❸ / ❖ / ◈ / ⬢⬡⬣ / ⊘⊗ — every glyph outside
    # U+24FF, so `--items` reported the new table as ZERO labels while still resolving the
    # retired glyphs quoted in its own retirement note. The reader was widened; the CHOICE of
    # the next family was not checked against it.
    _dp = os.path.join(_d, "dingbat.md")
    open(_dp, "w", encoding="utf-8").write("❶ ❿ ➀ ➉ ➊ ➓ all label\n")
    _dfound = set(items(_dp))
    check("enclosed-digit dingbats enumerate (U+2776–U+2793, three full runs)",
          all(g in _dfound for g in ("❶", "❿", "➀", "➉", "➊", "➓")), True)
    # ⚑⚑ AND THE NEGATIVE HALF IS THE LOAD-BEARING ONE, because the tempting widening is
    # "the blocks that family reached into" — which are NOT label-shaped. `⊗`/`⊘` are TENSOR
    # and QUOTIENT and this corpus writes them as mathematics in Agda prose; `▸` is a bullet.
    # Admitting Mathematical Operators or Geometric Shapes would report prose as labels at
    # scale — the cries-wolf failure the note below records. A range is admissible here only
    # if it is PROVABLY all-enclosed-alphanumeric.
    _np = os.path.join(_d, "notlabel.md")
    open(_np, "w", encoding="utf-8").write("the tensor ⊗ and quotient ⊘ over ▸ items\n")
    check("mathematical operators and bullets are NOT labels",
          set(items(_np)), set())

    _orph, _unwit, _dang = coherence(_p, _w)
    # ⚑ BOTH DIRECTIONS, because §24's dominant error was plan-findings with no
    # todo and §25's was todo-items with no evidence — one-directional audits
    # found neither.
    check("an item with no plan witness is an ORPHAN", _orph, ["C99"])
    check("a plan finding with no worklist item is UNWITNESSED",
          _unwit, ["A4-FNF"])
    check("a §ref to a section that does not exist is DANGLING", _dang, ["7"])

    # ⚑⚑⚑ THE DISCOVERY CENSUS FINDS A FAMILY THE GRAMMAR CANNOT READ — which is the whole point
    # of `--label-families`, and the case is written so it FAILS if the mode ever degenerates into
    # matching the known vocabulary.  ITEM_RE has been widened FOUR times, each time to the family
    # in front of the author; a fifth guessed widening would be the fifth instance, so this asserts
    # the DISCOVERY property (an unknown shape is REPORTED as unreadable) rather than any vocabulary.
    _lf = os.path.join(_d, "fam_a.md")
    _lf2 = os.path.join(_d, "fam_b.md")
    _lf3 = os.path.join(_d, "fam_c.md")
    for _p in (_lf, _lf2, _lf3):
        open(_p, "w", encoding="utf-8").write(
            "⟡extrude-minimal-run — a sigil label no widening covers\n"
            "T13 — an ASCII label the grammar already reads\n")
    _fam = label_families([_lf, _lf2, _lf3])
    _unread = {s: e for s, e in _fam.items() if not e["read"]}
    _sigil = [s for s, e in _unread.items()
              if any(x.startswith("⟡") for x in e["examples"])]
    check("an UNKNOWN sigil family is reported as unreadable", bool(_sigil), True)
    # ⚑ AND THE CONTROL, without which the case above proves nothing: a family the grammar DOES
    # read must be reported as read.  A mode that marked everything unreadable would pass the
    # assertion above while being useless — the same accidentally-correct shape summit filed.
    _read_ok = [s for s, e in _fam.items() if e["read"] and "T13" in e["examples"]]
    check("...while a KNOWN family is reported as read", bool(_read_ok), True)
    # ⚑ FILE SPREAD IS THE DISCRIMINATOR, not count — a label is a SHARED vocabulary, so it recurs
    # across documents, where a module name recurs within one.  Pinned because ranking by count
    # surfaced 888 shapes and 31KB of noise on the live corpus.
    check("a shared family is counted across all 3 documents",
          _fam[_sigil[0]]["files"] if _sigil else 0, 3)
    # ⚑ A BOLD SUB-ITEM IS A SECTION TOO.  This document numbers sub-findings as
    # `**6d. …**` rather than headings — deliberate, since a sub-finding is part of
    # its parent's argument — and keying only on `^#+ N.` reported the CORRECT
    # citation `§6d` as dangling.  A false DANGLING is the worse direction: the
    # audit's value is that non-zero means act, so one bogus row teaches the reader
    # to skim (§63/§64's cries-wolf rule).
    _p2 = os.path.join(_d, "plan2.md")
    _w2 = os.path.join(_d, "wl2.md")
    open(_p2, "w", encoding="utf-8").write(
        "# 6. A CLASS\n\ntext\n\n**6d. A sub-finding.** more text\n")
    open(_w2, "w", encoding="utf-8").write("- see §6 and §6d\n")
    check("a bold sub-item resolves as a section",
          coherence(_p2, _w2)[2], [])

    # ⚑ THE PHRASE KEY, PINNED.  Keying on the bare noun reported "2 files" and
    # "2941 files" as one supersession — 12 nouns of noise, a census nobody reads.
    # The qualified phrase is what makes a real collision visible.
    _s = os.path.join(_d, "fig.md")
    open(_s, "w", encoding="utf-8").write(
        "the split emitted 589 leaves\n"
        "re-measured: 1322 leaves in the tree\n"
        "unrelated: 2 files changed and 2941 files exist\n")
    _sup = dict(superseded(_s))
    # ⚑ ASSERT THE FACT, NOT A TAUTOLOGY.  My first version of this case computed
    # its own expected value from the result — it could not fail.  A case that
    # cannot fail is decoration (the §"4b" class: a guard whose positive branch is
    # unreachable), so both halves now name a literal outcome.
    _leaf_vals = sorted(v for k, vs in _sup.items() if "leave" in k
                        for v, _l in vs)
    check("one PHRASE measured twice reports BOTH values",
          _leaf_vals, [589, 1322])
    check("differently-qualified counts of one noun do NOT collide",
          [k for k in _sup if k.endswith("file")], [])

    # ⚑ S2 FIXED HERE: A SKIP MUST NOT SCORE AS A PASS, AND MUST NOT DISCARD THE
    # CASES THAT DID RUN.  This returned `True` with `0/0` — so an absent optional
    # dependency read as a green suite (the `jea_circuit.py:197` class the plan
    # records, reproduced in a tool I wrote AFTER recording it), and once the
    # pandoc-free audit cases were added it ALSO threw away six real results.
    #
    # The honest shape: report what ran, name what could not, and let the tally
    # reflect the ACTUAL population.  The pandoc-dependent cases are announced as
    # UNRUN rather than counted — an unmeasured case is not a passing one (Guard
    # (2)'s rule: an incomplete census is not a low count).
    _have_pandoc = True
    try:
        import panflute  # noqa: F401
    except ImportError:
        _have_pandoc = False

    if not _have_pandoc:
        ok = sum(1 for _n, g, _a, _b in cases if g)
        for n, g, got, want in cases:
            if not g:
                print(f"  FAIL {n}\n       got {got!r} want {want!r}")
        print("  ⚑ panflute absent — the AST cases did not run and are NOT "
              "counted as passing.\n"
              "     Text-level audits (items/coherence/superseded) ran; for the "
              "rest:\n     uv run --with panflute --with panflute python3 "
              "scratch/mdstruct.py --selftest")
        print(f"mdstruct selftest: {ok}/{len(cases)}  (AST cases UNRUN)")
        # ⚑⚑⚑ AN INCOMPLETE RUN IS NOT A PASS, AND THE EXIT CODE USED TO SAY IT WAS.
        # `return ok == len(cases)` measured only the cases that RAN, so a missing
        # `panflute` yielded exit 0 — while the text above correctly refused to count the
        # unrun ones.  The MESSAGE was honest and the VERDICT was not, and a gate reads
        # the verdict: summit's `scripts/check` gates this capability on this exit code,
        # so it would have reported the markdown reader GREEN on a machine that cannot
        # parse markdown.  Exactly the shape `--check-contracts` gates one repo over —
        # a census that reports clean because it could not look.
        #
        # ⚑⚑ FOUND BY A PEER CORRECTING MY OWN FALSE CLAIM.  summit-c4 reported this run
        # was "green by luck, passing only because panflute happens to import"; I recorded
        # that in a capability record ON THEIR WORD.  They then MEASURED it, found
        # panflute absent and the skip honest, and corrected themselves — *"neither of us
        # ran the thing we were describing; a false hazard went into a capability record
        # on two parties' agreement."*  The correction was right about the skip AND
        # surfaced this, which neither of us had looked for: the design was honest in the
        # half a human reads and wrong in the half a machine reads.
        #
        # ⚑ EXIT 2, NOT 1: this is INCOMPLETE, not FAILED.  A failing case and an unrun
        # suite need different responses (fix the code vs. install the dependency), and
        # collapsing them into one code is what let this hide.
        return INCOMPLETE if ok == len(cases) else False

    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.md")
    open(p, "w", encoding="utf-8").write(
        "# Top\n\nsome text\n\n## Sub\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "```\n# not a header\n```\n")

    hs = headers(p)
    check("headers are found with their level", hs, [(1, "Top"), (2, "Sub")])

    # ⚑ THE SKELETON AND THE BOUNDS ARE ONE READ, and `--headers` prints both. Pinned
    # because the two came apart once: `headers()` returned (level, text) while
    # `spans()` — same skeleton, same anchoring — carried the coordinates, and the
    # cheap mode was the one a reader reached for. A skeleton you cannot read FROM
    # sends the reader to the whole file.
    _sp = spans(p)
    check("spans covers the same headers as headers()",
          [(l, t) for l, t, _s, _e in _sp], hs)
    check("a fenced `# not a header` does not open a section", len(_sp), 2)
    # ⚑ AND THE OUTER SECTION MUST CONTAIN THE INNER ONE. A same-or-shallower header
    # closes a span, so `# Top` ends at EOF and `## Sub` nests inside it — getting
    # this backwards yields a correct-LOOKING short section a reader cannot see.
    (_l1, _t1, _s1, _e1), (_l2, _t2, _s2, _e2) = _sp
    check("a deeper header nests rather than closing its parent",
          _s1 < _s2 and _e2 <= _e1, True)

    # ── STRUCTURAL REWRITES: the write half this tool lacked ────────────────────
    # ⚑⚑⚑ BUILT BECAUSE A REFUSAL COULD NAME NO WRITE ROUTE.  `hook_structural_query`
    # denies `cat >> doc.md` — correctly: a shell append is unbounded and shapeless, and
    # this session MEASURED the damage (MEMORY.md's staging block appended and never
    # drained, past the 200-line budget of the reader that loads it every session).  But
    # the message could only name a READER, so a correct verdict read as a bug to the
    # peer who hit it.  Operator, 2026-08-19: *"mdstruct should be able to perform
    # structural rewrites."*  A gate that blocks without routing is half a gate.
    _rw = os.path.join(d, "rw.md")
    _rw_src = ("# Title\n\nIntro.\n\n## Alpha\n\nAlpha body.\n\n"
               "## Beta\n\nBeta body.\n\n### Beta sub\n\nNested.\n\n## Gamma\n\nG.\n")
    open(_rw, "w", encoding="utf-8").write(_rw_src)

    _new, (_l, _t, _s, _e) = replace_section(_rw, "Alpha", "REPLACED.")
    check("replace_section keeps the HEADING and swaps only the body",
          "## Alpha" in _new and "Alpha body." not in _new and "REPLACED." in _new,
          True)
    # ⚑ THE HEADING IS THE ANCHOR every other reader resolves against (`--coherence`,
    # `--items`, `spans`), so a rewrite that moved it could silently orphan references.
    check("replace_section leaves neighbouring sections untouched",
          "Beta body." in _new and "Nested." in _new and "G." in _new, True)

    _ap, _ = append_to_section(_rw, "Gamma", "ADDED.")
    check("append_to_section lands INSIDE the named section",
          _ap.index("ADDED.") > _ap.index("## Gamma"), True)
    # ⚑ THE POINT OF THE BOUNDED FORM: a shell `>>` lands at END OF FILE, which for a
    # sectioned document is almost never where the content belongs — it migrates under
    # whatever heading happens to be last.  Here Gamma IS last, so the discriminating
    # case is an append to a MIDDLE section.
    _mid, _ = append_to_section(_rw, "Alpha", "MID.")
    check("⚑ an append to a MIDDLE section does not land at end-of-file",
          _mid.index("MID.") < _mid.index("## Beta"), True)

    # ⚑ NESTING: a section ends at the next SAME-OR-SHALLOWER header, never simply the
    # next one.  Appending to `Beta` must not land inside `Beta sub`.
    _nest, _ = append_to_section(_rw, "Beta sub", "DEEP.")
    check("a nested subsection resolves to its own bounds",
          _nest.index("DEEP.") > _nest.index("### Beta sub"), True)

    # ⚑⚑ AMBIGUITY IS A REFUSAL, NOT A FIRST-MATCH.  `Beta` names both `## Beta` and
    # `### Beta sub`; picking the earlier one is the silent-wrong-target class, and the
    # target here is a WRITE — unrecoverable by re-running.
    try:
        replace_section(_rw, "Beta", "x")
        check("⚑ an ambiguous heading substring is REFUSED", False, True)
    except LookupError as e:
        check("⚑ an ambiguous heading substring is REFUSED",
              "REFUSING" in str(e) and "2 sections" in str(e), True)
    try:
        replace_section(_rw, "Nonexistent", "x")
        check("a missing heading is refused as a QUERY fact", False, True)
    except LookupError as e:
        check("a missing heading is refused as a QUERY fact",
              "a fact about the QUERY" in str(e), True)
    # ⚑ THE CASE THAT BEATS `grep '^#'`: a `#` inside a fenced code block is not
    # a header.  This document is full of fenced blocks containing Agda and shell.
    check("a `#` inside a fence is NOT a header",
          [t for _l, t in hs if "not a header" in t], [])

    # ⚑⚑ FRONTMATTER MUST NOT REACH THE JSON WRITER — the defect that made EVERY AST
    # mode blind to EVERY governed doc and every SKILL.md for the whole life of this
    # module.  `_pandoc` re-attached the `---` head to its OUTPUT: correct for
    # markdown→markdown, fatal for `-t json`, where panflute received YAML ahead of the
    # document and died at char 0.  Diagnosed by gabion and routed here through summit
    # (`corroboration-mdstruct-frontmatter-gabion`); they declined to patch their own
    # copy because it is a symlink and a local fix would fork the body silently.
    #
    # ⚑ THIS CASE CATCHES rather than letting the exception fly, because pre-fix it
    # RAISED — and a crash aborts every case below it, reporting a SMALLER POPULATION
    # instead of one red row.  An incomplete census is not a low count.
    _fm = os.path.join(d, "fm.md")
    open(_fm, "w", encoding="utf-8").write(
        "---\ntitle: governed\nreviewers: [a, b]\n---\n\n# Real Header\n\ntext\n")
    try:
        _fmh = headers(_fm)
    except Exception as exc:                  # noqa: BLE001 — reported as red, not swallowed
        _fmh = f"{type(exc).__name__}: {exc}"
    check("an AST mode reads a `---`-frontmatter document",
          _fmh, [(1, "Real Header")])
    # ⚑ AND THE OTHER HALF IS THE LOAD-BEARING ONE.  The tempting fix is to stop
    # re-attaching at all — which trades one silent corruption for the one the
    # re-attach was introduced to close: round 1 drops the frontmatter, round 2 sees a
    # different document, and `--roundtrip` stops being able to measure idempotence on
    # exactly the files that have metadata.  Both directions are pinned so neither
    # repair can be made by deleting the other.
    check("...while a markdown writer still preserves the head verbatim",
          _pandoc(open(_fm, encoding="utf-8").read(), "markdown").startswith(
              "---\ntitle: governed\n"), True)

    ts = tables(p)
    check("one table is found", len(ts), 1)
    check("its header cells are read", ts[0][3], ["a", "b"])

    # ── table_rows: the ROW-level read (the mode an agent named and could not add)
    # ⚑ THE HEADER ROW IS NOT A BODY ROW.  `tables()` counts `el.content` (the
    # bodies) for its size but reads `el.head` for its cells; a row reader that
    # walked both would return the header as data and every `--where` query would
    # match the column NAMES.  Pinned because the two live in different places.
    _rp = os.path.join(d, "rows.md")
    open(_rp, "w", encoding="utf-8").write(
        "| name | home |\n|---|---|\n| V4 | Groups.V4 |\n| Wedge | Algebra.W |\n"
        "\n| other | tbl |\n|---|---|\n| V4 | elsewhere |\n")
    _all = table_rows(_rp)
    check("body rows are read, header is not", len(_all), 3)
    check("...and the header cells are absent from the rows",
          ["name", "home"] in [c for _i, c in _all], False)
    # ⚑ A ROW WITHOUT ITS TABLE IS THE BARE-COUNT DEFECT ONE LEVEL DOWN — two
    # tables can hold the same name and mean different things, so the index is
    # returned with every row rather than being implied by the query.
    check("each row says WHICH table it came from",
          sorted({i for i, _c in _all}), [0, 1])
    check("--table selects one table", len(table_rows(_rp, index=1)), 1)
    # ⚑ `--where` MATCHES ANY CELL, CASE-FOLDED — the reuse-index question is
    # "where does this concept live", and the concept may sit in the name column
    # or in the description.
    check("--where matches across columns",
          len(table_rows(_rp, where="v4")), 2)
    check("--where is case-folded", len(table_rows(_rp, where="WEDGE")), 1)
    # ⚑ AND THE CELL SEPARATOR MUST NOT BE MATCHABLE.  Joining cells with a
    # printable delimiter would let `--where "V4 | Groups"` match across a column
    # boundary — a phantom row that exists in no cell.  The join uses NUL.
    check("a query spanning a cell boundary does NOT match",
          len(table_rows(_rp, where="V4 | Groups")), 0)
    check("a query matching nothing returns nothing (not everything)",
          table_rows(_rp, where="zzz-absent"), [])

    # ⚑ TERMINATION BY STRICT DESCENT, NOT BY A ROUND CAP.  The live document
    # needs SEVEN rounds to converge (`[1340, 899, 561, 400, 320, 176, 0]`), so a
    # `rounds=3` cutoff reported "not a fixpoint" for a document that reaches one —
    # and a `rounds=25` cap would do the same to anything needing 26.  These cases
    # pin that `fixpoint` keeps going while progress is strict and stops when it
    # is not, WITHOUT consulting a count.
    _seq = []

    def _fake(deltas):
        """Drive the same decision rule over a canned delta sequence."""
        prev, out = None, []
        for n in deltas:
            out.append(n)
            if n == 0:
                return True, out
            if prev is not None and n >= prev:
                return False, out
            prev = n
        return False, out

    check("a strictly decreasing sequence reaching 0 is a FIXPOINT",
          _fake([1340, 899, 561, 400, 320, 176, 0])[0], True)
    check("...and it is NOT judged unconverged at round 3",
          _fake([1340, 899, 561])[0], False)  # honest: 3 rounds cannot decide
    check("a STALLED delta is a cycle, not slow convergence",
          _fake([50, 40, 40])[0], False)
    check("a GROWING delta terminates immediately",
          _fake([10, 12])[1], [10, 12])

    # ⚑ THE NORMALIZER RETIRES MD060 BY CONSTRUCTION, IT DOES NOT "FIX" IT.
    # MEASURED on the live plan: 48 non-canonical pipe rows -> 0 after one pass.
    # Hand-fixing 48 rows leaves the 49th for tomorrow; a document held at the
    # fixpoint cannot violate the rule at all, because canonical spacing is what
    # the writer emits.  Same shape as `check_private_ratchet` excluding
    # `private variable` BY PREDICATE rather than by an exemption that can rot.
    _bad = os.path.join(d, "bad.md")
    open(_bad, "w", encoding="utf-8").write("|a|b|\n|---|---|\n|1|2|\n")
    check("non-canonical pipe rows are detected", len(table_style(_bad)) > 0, True)
    _good = os.path.join(d, "good.md")
    open(_good, "w", encoding="utf-8").write(
        _pandoc(open(_bad, encoding="utf-8").read(),
                "markdown-smart+pipe_tables --columns=999 --wrap=preserve"))
    check("...and a NORMALIZED document has none", table_style(_good), [])

    # ── frontmatter is DATA, and a fixpoint is not a lossless transform ──
    # ⚑ BOTH GATES PASSED A WRITE THAT DAMAGED A MEMORY (2026-08-03).  `--fixpoint`
    # asked only "does it converge"; `--roundtrip` measured the drift and told the
    # reader to disregard it.  Meanwhile pandoc parses frontmatter as metadata and
    # drops it without `--standalone`, so a memory lost its name/type/provenance.
    _fm_src = ('---\nname: x\ntype: reference\n---\n\n'
               'Body with `a|b` and [[a-link]] and "quotes".\n')
    _head, _body = split_frontmatter(_fm_src)
    check("frontmatter is split off, not converted",
          (_head.startswith("---\n"), "name: x" in _head, _body.lstrip().startswith("Body")),
          (True, True, True))
    check("a document with no frontmatter is unchanged by the split",
          split_frontmatter("# Just prose\n"), ("", "# Just prose\n"))
    # ⚑ AND IT SURVIVES CONVERSION — the reason round 1 used to differ from round 2
    # on any file WITH frontmatter: round 1 deleted it, so round 2 saw a new document.
    _conv = _pandoc(_fm_src, "markdown-smart --columns=120 --wrap=preserve")
    check("frontmatter survives _pandoc verbatim", _conv.startswith(_head), True)

    # The damage classes, each measured on the real incident.
    check("escaping a wikilink is semantic damage",
          [k for k, _d in semantic_damage("see [[a]] and [[b]]",
                                          "see \\[\\[a\\]\\] and \\[\\[b\\]\\]")],
          ["wikilink-escaped"])
    check("escaping a pipe INSIDE inline code is semantic damage",
          [k for k, _d in semantic_damage("`cpu|mem|io`", "`cpu\\|mem\\|io`")],
          ["escape-in-code"])
    check("dropping frontmatter is semantic damage",
          [k for k, _d in semantic_damage(_fm_src, "Body only\n")][0],
          "frontmatter-dropped")
    # ⚑ AND A CLEAN NORMALIZATION MUST NOT FIRE — a gate that refuses everything is
    # not a gate.  Reflowing prose changes lines without changing meaning.
    check("pure reflow is NOT flagged",
          semantic_damage("a long\nline of prose\n", "a long line of prose\n"), [])
    # The check is on the DELTA, so pre-existing text is never attributed to it.
    check("a pre-existing escape is not attributed to the transform",
          semantic_damage("`a\\|b`", "`a\\|b`"), [])

    # ── lint_shape: SATISFY the rules, don't disable them ────────────────
    # ⚑ BUILT AFTER I PROPOSED DISABLING FOUR RULES WITHOUT MEASURING ANY (user:
    # *"how can we make things not incompatible with them?"*).  Measured on a real
    # memory: 5 findings, FOUR of them fixable content.  MD013 wanted a width the
    # document already had (tell it 120, fix the 1 long line); MD032 was two real
    # missing blank lines; MD033 was a false positive in MY checker.
    _lp = os.path.join(d, "lint.md")
    open(_lp, "w", encoding="utf-8").write(
        "---\nname: m\n---\n\n"
        "Body text with `<n> bytes` inline.\n"
        "**Lead-in:**\n"
        "- an item\n")
    _rows = lint_shape(_lp, 120)
    _rules = sorted({r for _l, r, _d in _rows})
    # ⚑ THE FALSE POSITIVE THAT NEARLY COST A WRONG EDIT.  `<n>` inside backticks is
    # code, and MD033 exempts inline code — my first guard counted backticks with a
    # condition that admitted it, and I was about to "fix" correct prose.  The
    # witness line is what exposed it; a count would not have.
    check("inline HTML INSIDE code is not MD033", "MD033" not in _rules, True)
    check("a list without a preceding blank line IS MD032", "MD032" in _rules, True)
    check("a body with no heading IS MD041", "MD041" in _rules, True)
    # ⚑ LINE NUMBERS ARE FILE-ABSOLUTE, so a reported line can be opened directly.
    # Reporting body-relative numbers would send every reader to the wrong line.
    _md041 = [l for l, r, _d in _rows if r == "MD041"][0]
    check("reported lines account for the frontmatter offset", _md041 >= 4, True)
    # Real HTML outside code must still be caught — the guard must discriminate.
    _hp = os.path.join(d, "html.md")
    open(_hp, "w", encoding="utf-8").write("# T\n\nreal <br> tag\n")
    check("inline HTML OUTSIDE code is still MD033",
          "MD033" in {r for _l, r, _d in lint_shape(_hp, 120)}, True)
    # A clean document must report nothing — a checker that always fires is noise.
    _cp = os.path.join(d, "clean.md")
    open(_cp, "w", encoding="utf-8").write("# Title\n\nShort prose.\n\n- a\n- b\n")
    check("a conforming document has NO findings", lint_shape(_cp, 120), [])

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"mdstruct selftest: {ok}/{len(cases)}")
    return ok == len(cases)


#: ⚑ THE THIRD VERDICT, AND ITS ABSENCE LET AN UNRUN SUITE READ AS A PASS.  `_selftest`
#: returned a bool, so INCOMPLETE (dependency missing, cases never ran) and PASS (every
#: case ran and passed) collapsed to the same exit 0 — while the printed text correctly
#: said the AST cases were UNRUN.  A gate reads the code, not the text.
INCOMPLETE = "incomplete"

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # ⚑ 0 pass / 1 FAILED / 2 INCOMPLETE — a failing case and an unrun suite need
        # different responses (fix the code vs. install the dependency), and collapsing
        # them is what let a markdown reader report GREEN on a machine that cannot parse
        # markdown.  Matches summit's `typed-exit-alphabet` capability, which types
        # exactly this distinction and which this tool was not honouring.
        _rc = _selftest()
        sys.exit(2 if _rc is INCOMPLETE else (0 if _rc else 1))
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ A BARE INTEGER IS AN OPERAND, NEVER A PATH — and the omission made the branch's
    # OWN documented calling convention fail.  `--budget` binds its budget by SHAPE
    # (`:2297` scans argv for the first `isdigit()`), so `--budget 17100 f.md` is the
    # advertised order; but this stripper predates that branch and took `args[0]`
    # verbatim, so the integer became the path and the tool exited 2 with
    # `17100 does not exist`.  Declaring the arity in `MODES` made the shape visible and
    # this fell straight out — the roster row is what surfaced it, not a separate bug.
    # Filtering here rather than in the branch keeps ONE path resolver: any later
    # shape-bound numeric operand gets the same treatment for free.
    path = next((a for a in args if not a.isdigit()), PLAN)
    if not os.path.exists(path):
        print(f"{path} does not exist")
        sys.exit(2)

    if "--roundtrip" in sys.argv:
        same, n, sample = roundtrip(path)
        if same:
            print(f"{path}: round-trips IDENTICALLY")
            sys.exit(0)
        print(f"{path}: pandoc normalization changes {n} line(s). First 12:")
        for l in sample:
            print(f"   {l[:150]}")
        print("\n⚑ pandoc NORMALIZES by design — this is expected, not a failure.")
        print("   The drift-vs-ORIGINAL is paid ONCE; what decides the write path")
        print("   is whether normalization is a FIXPOINT: `--fixpoint`.")
        sys.exit(0)

    if "--fixpoint" in sys.argv:
        opts = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--to=")),
                    None)
        ok, deltas, sample, converged = fixpoint(path, opts or WRITER)
        print(f"{path}  writer={opts or WRITER}")
        print(f"   changes per successive normalization round: {deltas}")
        if ok:
            print("   ✓ FIXPOINT — normalize once, and every later transform "
                  "round-trips exactly.")
            print("     A write path IS admissible: the one-time reflow is a "
                  "reviewable migration.")
        else:
            print("   ✗ NOT a fixpoint — normalization keeps changing the "
                  "document. First drift:")
            for l in sample:
                print(f"       {l[:150]}")
        # ⚑ THE APPLY — `--apply`, because this is a HAND-INVOKED tool (§7e's
        # polarity rule: a driver-called stage errs apply-by-default so a silent
        # no-op cannot leave a chain half-finished; a human-called one must not
        # write on a bare run).  REFUSES a non-fixpoint: writing a document that
        # normalization keeps changing banks a reflow that the next pass undoes.
        if "--apply" in sys.argv:
            if not ok:
                print("   REFUSING to write — not a fixpoint, so the reflow is "
                      "not stable and the next pass would change it again.")
                sys.exit(1)
            src = open(path, encoding="utf-8").read()
            if converged == src:
                print("   already AT the fixpoint — nothing to write.")
                sys.exit(0)
            # ⚑ CONVERGENCE IS NOT PRESERVATION, AND THIS GATE WAS MISSING.
            # `--fixpoint` proved idempotence and wrote; nothing asked whether the
            # converged text still MEANT the same thing.  MEASURED on a memory file:
            # `|` escaped inside inline code (a PSI selector made wrong), every
            # `[[wikilink]]` escaped, frontmatter dropped — reported `✓ FIXPOINT`.
            # REFUSE rather than warn: a warning after a write is a report, not a gate.
            _dmg = semantic_damage(src, converged)
            if _dmg:
                print("   ✗ REFUSED — normalization converges but CHANGES MEANING:")
                for kind, detail in _dmg:
                    print(f"       {kind}: {detail}")
                print("     A fixpoint is not a lossless transform.  This writer is a\n"
                      "     PROSE normalizer; a document whose inline code, links or\n"
                      "     frontmatter carry structure is a different corpus.\n"
                      "     Nothing was written.")
                sys.exit(1)
            import edit_snapshot as _es
            _es.guard("mdstruct --fixpoint --apply", [path])
            open(path, "w", encoding="utf-8").write(converged)
            n, _d = _diff(src, converged)
            print(f"   ✓ WROTE the converged document ({n} line(s) changed). "
                  f"Re-run to confirm it is now a no-op.")
            sys.exit(0)
        if ok:
            print("   (pass --apply to write the converged document)")
        sys.exit(0 if ok else 1)

    if "--replace-section" in sys.argv or "--append-section" in sys.argv:
        # ⚑⚑⚑ THE WRITE MODES A REFUSAL CAN NAME.  `hook_structural_query` refuses
        # `cat >> doc.md` — correctly, because a shell append is unbounded and shapeless
        # (measured this session: MEMORY.md's staging block appended and never drained,
        # past the 200-line budget of the reader that loads it every session).  But the
        # refusal could only name a READER, so a correct verdict read as a bug to the peer
        # who hit it.  Operator: *"mdstruct should be able to perform structural rewrites."*
        _apply = "--append-section" in sys.argv
        _flag = "--append-section" if _apply else "--replace-section"
        _i = sys.argv.index(_flag)
        if _i + 2 >= len(sys.argv):
            print(f"usage: mdstruct.py {_flag} <file> <heading-substring> "
                  f"[--body-file F | --body TEXT] (--apply | --dry-run)",
                  file=sys.stderr)
            sys.exit(2)
        _path, _needle = sys.argv[_i + 1], sys.argv[_i + 2]
        # ⚑ THE INTENT IS STATED AT THE DECISION, never defaulted — the contract
        # `ratchet.mutating_argv` enforces, checked BEFORE any work so a bare invocation
        # cannot half-run.  No default-dry, no default-apply.
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import ratchet as _r
        _rc = _r.mutating_argv(sys.argv, f"mdstruct {_flag}")
        if _rc is not None:
            sys.exit(_rc)
        if "--body-file" in sys.argv:
            _bf = sys.argv[sys.argv.index("--body-file") + 1]
            _body = open(_bf, encoding="utf-8").read()
        elif "--body" in sys.argv:
            _body = sys.argv[sys.argv.index("--body") + 1]
        else:
            # ⚑ STDIN IS THE THIRD SOURCE, and it is what makes this a real replacement
            # for the append it refuses: a generator can PIPE into a named section instead
            # of `>>`-ing at end-of-file.
            _body = sys.stdin.read()
        try:
            _new, (_lvl, _txt, _s, _e) = (
                append_to_section(_path, _needle, _body) if _apply
                else replace_section(_path, _needle, _body))
        except LookupError as e:
            print(f"mdstruct {_flag}: {e}", file=sys.stderr)
            sys.exit(2)
        _old = open(_path, encoding="utf-8").read()
        _n, _d = _diff(_old, _new)
        print(f"{_path}  §{_txt!r} (level {_lvl}, lines {_s}-{_e - 1})")
        print(f"   {_n} line(s) change")
        for _l in _d[:12]:
            print("   " + _l)
        if "--apply" not in sys.argv:
            print("   (--dry-run: nothing written)")
            sys.exit(0)
        # ⚑ THE SECTION SKELETON MUST SURVIVE THE WRITE.  A body containing a heading at
        # or above this section's level would SPLIT it, silently re-parenting everything
        # below — the write would succeed and the document would mean something else.
        _before = [(l, t) for l, t, _a, _b in spans(_path)]
        import tempfile as _tf
        with _tf.NamedTemporaryFile("w", suffix=".md", delete=False,
                                    encoding="utf-8") as _fh:
            _fh.write(_new)
            _tmp = _fh.name
        try:
            _after = [(l, t) for l, t, _a, _b in spans(_tmp)]
        finally:
            os.unlink(_tmp)
        if _after != _before:
            print("   ✗ REFUSED — the write changes the SECTION SKELETON:")
            for _row in [r for r in _after if r not in _before][:6]:
                print(f"       + {'#' * _row[0]} {_row[1]}")
            for _row in [r for r in _before if r not in _after][:6]:
                print(f"       - {'#' * _row[0]} {_row[1]}")
            print("     A body carrying a heading RE-PARENTS the document. Nothing written.")
            sys.exit(1)
        import edit_snapshot as _es
        _es.guard(f"mdstruct {_flag}", [_path], intent="apply")
        open(_path, "w", encoding="utf-8").write(_new)
        print(f"   ✓ WROTE {_path} ({_n} line(s))")
        sys.exit(0)

    if "--label-families" in sys.argv:
        # ⚑ `--label-families [root]` — DISCOVER label shapes corpus-wide, including paths git
        # ignores.  The ignored ones are the point: `~/.claude/`-style scratch, build trees and
        # drop zones are where a new labelling family gets INVENTED, and every reader that walks
        # only tracked files is blind to exactly the place vocabularies are born.
        import os as _os
        root = next((a for a in sys.argv[1:]
                     if not a.startswith("-") and _os.path.isdir(a)), ".")
        skip = {".git", "_build", ".venv", "__pycache__", "node_modules"}
        files = []
        for dirpath, dirnames, filenames in _os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for fn in filenames:
                if fn.endswith((".md", ".txt", ".bricks")):
                    files.append(_os.path.join(dirpath, fn))
        fam = label_families(files)
        rows = sorted(fam.items(), key=lambda kv: -kv[1]["count"])
        unread = [(s, e) for s, e in rows if not e["read"]]
        print(f"  scanned {len(files)} document(s) under {root}"
              f"  ({len(rows)} shape(s); {len(unread)} UNREADABLE by ITEM_RE)")
        print("  ── shapes the CURRENT grammar reads " + "─" * 30)
        for sh, e in rows:
            if e["read"]:
                print(f"    {e['count']:>6}  {e['files']:>4}f  {sh:<28} {', '.join(e['examples'][:5])}")
        # ⚑⚑ THE DISCRIMINATOR IS FILE SPREAD, NOT COUNT — and the first cut got this wrong.
        # Ranking by occurrence surfaced 888 shapes and 31KB of output: Agda module names
        # (`Substrate.S5.S5Real`), mermaid node ids (`n1aa9648c60["F2.Vector"`) and quoted paths
        # all recur heavily — WITHIN ONE FILE. A LABEL is a shared vocabulary: it recurs across
        # MANY documents, because its purpose is letting one document refer to another's item.
        # So `files` is the signal and `count` is noise. A census that prints everything has the
        # cries-wolf defect ITEM_RE's own comments record, one level up — I nearly shipped it.
        SPREAD = 3
        cands = [(s, e) for s, e in unread if e["files"] >= SPREAD]
        print(f"  ── ⚑ shapes it CANNOT read, in ≥{SPREAD} documents — candidates, not verdicts ──")
        for sh, e in sorted(cands, key=lambda kv: -kv[1]["files"]):
            print(f"    {e['count']:>6}  {e['files']:>4}f  {sh:<28} {', '.join(e['examples'][:5])}")
        print(f"  {len(cands)} candidate(s); {len(unread) - len(cands)} unread shape(s) suppressed "
              f"as single-document (module names, node ids, quoted paths).")
        print("  ⚑ a row here is a CANDIDATE: in label position, unread, and SHARED across files.")
        print("     Judge each — prose spreads too. Widening the grammar to one without saying WHY")
        print("     is the fifth instance of the defect ITEM_RE's comments already record four of.")
        sys.exit(0)

    if "--headers" in sys.argv:
        # ⚑ THE SKELETON CARRIES ITS SPANS, because a skeleton without them is a
        # skeleton you cannot READ FROM.  `--headers` used to print level+text only,
        # so targeting one section of a 1414-line document meant either reading the
        # whole file or already knowing `--spans` exists — and `--spans` is absent
        # from the usage banner, so the second route was reachable only by reading
        # the dispatch.  Measured: a reviewer with both modes in the tool read an
        # entire document to reach one section.  The bounds are FREE here — `spans()`
        # computes exactly this skeleton and drops nothing — so withholding them made
        # the cheap mode the useless one.
        for lvl, txt, start, end in spans(path):
            print(f"  {start:>6}-{end - 1:<6} {'  '*(lvl-1)}{'#'*lvl} {txt[:96]}")
        print("⚑ `start-end` are 1-indexed and INCLUSIVE — read one with "
              "`sed -n 'start,endp'`, or `--spans <file> <match>` for one section.")
        sys.exit(0)

    if "--spans" in sys.argv:
        # ⚑ `--spans <file> [match]` — the bounds of each section, and with a match
        # argument the bounds of ONE.  Built because "where does §69 end, so I can
        # append after it" had no command and I reached for `awk` over a document
        # full of fenced `#` and `--` comments.
        want = [a for a in sys.argv[1:] if a != path and not a.startswith("-")]
        rows = spans(path)
        if want:
            rows = [r for r in rows if want[0].lower() in r[1].lower()]
        for lvl, txt, start, end in rows:
            print(f"  {start:>6}-{end - 1:<6} L{lvl}  {txt[:90]}")
        print(f"{len(rows)} section(s); `end` is the last line OF the section")
        sys.exit(0)

    if "--why-not-pipe" in sys.argv:
        rows = why_not_pipe(path)
        for head, reason in rows[:25]:
            print(f"  {reason:<34} {head}")
        if len(rows) > 25:
            print(f"   … {len(rows)-25} more")
        print(f"{len(rows)} table(s) cannot be pipe tables at ANY width")
        if not rows:
            print("  (so any remaining multiline table IS a width question)")
        sys.exit(0)

    if "--narrowest" in sys.argv:
        # every doc the setting governs — WRITER is ONE constant for the whole corpus
        docs = [a for a in sys.argv[1:] if a.endswith(".md")] or [path]
        # ⚑ THE BASE MUST CARRY THE EXTENSION FLAGS, OR THE SEARCH ASKS THE WRONG
        # QUESTION.  My first run left `base=None`, so every probe used the DEFAULT
        # extension set — under which pandoc falls back to multiline no matter how wide
        # the budget, and the search reported "no width satisfies both" for a corpus
        # where 999 demonstrably does.  *A search is only as good as the predicate, and
        # the predicate was carrying a stale writer.*
        base = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--base=")),
                    WRITER.split(" --columns")[0])
        w, tried = narrowest_width(docs, base=base)
        for width, conv, pipe in tried:
            mark = "ok   " if (conv and pipe) else "FAIL "
            print(f"  {mark} --columns={width:<5} converges={conv}  all-pipe={pipe}")
        if w is None:
            print("no width satisfies BOTH conditions in range — the supremum bracket "
                  "does not hold, so there is no boundary to find")
            sys.exit(1)
        print(f"narrowest width meeting BOTH (converges AND all-pipe): {w}  "
              f"({len(tried)} probes over {len(docs)} document(s))")
        sys.exit(0)

    if "--table-forms" in sys.argv:
        f = table_forms(path)
        for k, n in sorted(f.items(), key=lambda kv: -kv[1]):
            print(f"  {k:<10} {n:>4}")
        if f.get("multiline") or f.get("grid"):
            print("  ⚑ NON-PIPE tables present — `+pipe_tables` enables the extension, it")
            print("    does not FORCE pipe output; pandoc falls back when a table exceeds")
            print("    --columns.  MD035/MD003 fire on those rules and header rows.")
        sys.exit(0)

    if "--table-style" in sys.argv:
        rows = table_style(path)
        for ln, kind in rows[:20]:
            print(f"{path}:{ln}  {kind}")
        if len(rows) > 20:
            print(f"   … {len(rows)-20} more")
        print(f"{len(rows)} non-canonical pipe row(s) (MD060)")
        # ⚑ Report what the FIXPOINT would do to them — the whole point is that
        # this class is retired by normalization, not by hand-fixing pipes.
        if rows:
            src = open(path, encoding="utf-8").read()
            norm = _pandoc(src, "markdown-smart+pipe_tables "
                                "--columns=999 --wrap=preserve")
            import tempfile
            tf = os.path.join(tempfile.mkdtemp(), "n.md")
            open(tf, "w", encoding="utf-8").write(norm)
            after = table_style(tf)
            print(f"   after one normalization pass: {len(after)} remain")
        sys.exit(0)

    if "--lint-config" in sys.argv:
        _cfg = next((a for a in sys.argv[1:]
                     if a.endswith(".json") and os.path.exists(a)), None)
        if _cfg is None:
            _cand = os.path.join(os.path.dirname(os.path.abspath(path)),
                                 ".markdownlint.json")
            _cfg = _cand if os.path.exists(_cand) else None
        if _cfg is None:
            print("no .markdownlint.json found beside the document\n"
                  "  usage: mdstruct.py --lint-config <config.json>")
            sys.exit(2)
        rows = lint_config_audit(_cfg)
        print(f"{_cfg}")
        for verdict in ("unearned", "paydown", "earned", "configured", "live"):
            hits = [(r, d) for v, r, d in rows if v == verdict]
            for rule, detail in hits:
                print(f"  {verdict:<10} {rule:<8} {detail}")
        _un = [r for v, r, _d in rows if v == "unearned"]
        _pd = [r for v, r, _d in rows if v == "paydown"]
        if _un:
            print(f"\n⚑ {len(_un)} UNEARNED exemption(s): {', '.join(_un)}")
            print("   Disabled for a rule that never fires — decoration that rots "
                  "into policy.")
        if _pd:
            print(f"⚑ {len(_pd)} PAYDOWN candidate(s): {', '.join(_pd)}")
            print("   Few enough to fix in the DOCUMENT; fixing retires the exemption.")
        if not _un and not _pd:
            print("\n✓ every exemption is earned or configured.")
        sys.exit(1 if (_un or _pd) else 0)

    if "--lint-shape" in sys.argv:
        _w = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--width=")),
                  120)
        rows = lint_shape(path, _w)
        # ⚑ PRINT THE WITNESS, NOT THE TALLY.  A count sends the reader back to the
        # file with `sed` to find out what to fix — reasoning over program output,
        # and the shape the struct-tools rule exists to stop.  §44 recorded this
        # exact lesson ("the grouped view showed the same file:line surviving a fix")
        # and this mode shipped a count anyway.
        _src = open(path, encoding="utf-8").read().split("\n")
        by = {}
        for ln, rule, detail in rows:
            by.setdefault(rule, []).append((ln, detail))
        for rule in sorted(by):
            hits = by[rule]
            print(f"  {rule}  ({len(hits)})")
            for ln, detail in hits[:6]:
                txt = _src[ln - 1].strip() if 0 < ln <= len(_src) else ""
                print(f"     :{ln:<4} {detail}")
                if txt:
                    print(f"           {txt[:96]}")
        print(f"{len(rows)} finding(s) in the BODY (frontmatter excluded, "
              f"width={_w})")
        if not rows:
            print("  ⚑ the document SATISFIES these rules — no exemption needed.")
        sys.exit(0)

    if "--tables" in sys.argv:
        for i, nrows, ncols, head in tables(path):
            print(f"table {i:>3}  {nrows:>3} rows x {ncols} cols   {head}")
        sys.exit(0)

    if "--rows" in sys.argv:
        _idx = None
        _where = None
        _a = sys.argv[1:]
        for i, a in enumerate(_a):
            if a == "--table" and i + 1 < len(_a):
                _idx = int(_a[i + 1])
            if a == "--where" and i + 1 < len(_a):
                _where = _a[i + 1]
        allrows = table_rows(path, index=None, where=None)
        rows = table_rows(path, index=_idx, where=_where)
        for ti, cells in rows[:200]:
            print(f"  t{ti:<3} " + " | ".join(c[:44] for c in cells))
        # ⚑ `n of m`, ALWAYS.  A filtered read that prints only its matches cannot
        # distinguish "the name is not in the index" from "the table was never
        # read" — the exact defect F5 records for `--key`, and the reason a prior
        # agent's absence-claims could not be trusted.
        scope = "all tables" if _idx is None else f"table {_idx}"
        print(f"{len(rows)} of {len(allrows)} row(s) in {scope}"
              + (f" matching {_where!r}" if _where else ""))
        if len(rows) > 200:
            print(f"  ⚑ showing the first 200 of {len(rows)} — narrow with --where")
        sys.exit(0)

    if "--budget" in sys.argv:
        # ⚑ THE MISSING MODE, AND ITS ABSENCE ROUTED A READER TO `wc -c`.  MEASURED
        # 2026-08-24: MEMORY.md is loaded every session and outgrew the reader that
        # loads it; the operator's brief carried a byte target, and the only way to
        # read the current size was `wc`, which `hook_structural_query` refuses —
        # correctly, and with no mode to route to.  A gate that blocks without
        # routing is half a gate (this file's own `--append-section` note says so).
        #
        # ⚑ SECTION ATTRIBUTION IS THE POINT, NOT THE TOTAL.  A single number says
        # "too big" and nothing about WHERE, so the reflex is to delete the tail —
        # which, for an index whose lines are POINTERS, orphans live memories.  The
        # per-section split makes compaction targetable: shorten the heaviest
        # section, fold duplicates, and leave the pointer set intact.
        # ⚑ THE BUDGET IS ANY BARE INTEGER OPERAND, NOT "the token after the flag".
        # The first cut required adjacency and silently dropped the budget when the
        # operator wrote `--budget <file> N` — the natural order, and the one the
        # banner shows.  A positional that binds by POSITION rather than by SHAPE
        # turns a supplied argument into no argument, and the mode then prints a
        # clean census with the verdict missing: a FALSE GREEN by omission, which is
        # the `--literal` flag-swallow defect (agda-F13) one tool over.
        _budget = None
        for _a in sys.argv[1:]:
            if _a.isdigit():
                _budget = int(_a)
                break
        raw = open(path, encoding="utf-8", errors="replace").read()
        total = len(raw.encode("utf-8"))
        lines = raw.split("\n")
        hdrs = [(i, l) for i, l in enumerate(lines) if l.startswith("#")]
        print(f"{path}")
        print(f"  {total} bytes · {len(lines)} lines · {len(hdrs)} heading(s)")
        if hdrs:
            print("\n  bytes  lines  section")
            bounds = [h[0] for h in hdrs] + [len(lines)]
            rows = []
            pre = len("\n".join(lines[:bounds[0]]).encode("utf-8"))
            if pre:
                rows.append((pre, bounds[0], "(preamble)"))
            for k, (ln, txt) in enumerate(hdrs):
                seg = lines[ln:bounds[k + 1]]
                rows.append((len("\n".join(seg).encode("utf-8")), len(seg), txt.strip()))
            for b, n, t in sorted(rows, reverse=True):
                print(f"  {b:>6} {n:>6}  {t[:72]}")
        if _budget is not None:
            over = total - _budget
            if over > 0:
                print(f"\n⚑ OVER by {over} bytes ({total} > {_budget}).")
                # ⚑ THE ADVICE IS PART OF THE VERDICT — see `the-holder-is-not-the-worker`:
                # a refusal that does not name what to do next hands the reader the wrong
                # end of the edge.  For a POINTER INDEX the wrong repair is deletion.
                print("  ⚑ If this file is an INDEX, its lines are POINTERS: dropping one")
                print("    orphans a target that still exists on disk. Shorten hooks, fold")
                print("    near-duplicates, promote clusters — do not delete pointers.")
            else:
                print(f"\nwithin budget ({total} <= {_budget}), {-over} bytes spare")
        sys.exit(0)

    if "--items" in sys.argv:
        found = items(path)
        for lbl in sorted(found):
            print(f"  {lbl:<14} {len(found[lbl]):>3} mention(s)  "
                  f"first at :{found[lbl][0]}")
        print(f"{len(found)} distinct worklist label(s)")
        sys.exit(0)

    if "--coherence" in sys.argv:
        args = [a for a in sys.argv[1:] if not a.startswith("-")]
        _plan, _wl, _notes = docs()
        if len(args) >= 2:
            _plan, _wl = args[0], args[1]
            _notes = []
        for n in _notes:
            print(f"⚑ {n}")
        if not _plan or not _wl:
            print("\nCannot audit coherence: one side of the comparison does not "
                  "exist as a file.\n"
                  "  usage: mdstruct.py --coherence <plan.md> <worklist.md>")
            sys.exit(2)
        orph, unwit, dang = coherence(_plan, _wl)
        # ⚑ THREE POPULATIONS, NEVER ONE VERDICT (§25): two documents can agree
        # perfectly and both be missing the same thing, so a single pass/fail here
        # would be the derived-view trap the audit exists to catch.
        print(f"ORPHAN items (in worklist, no plan witness): {len(orph)}")
        for l in orph:
            print(f"    {l}")
        print(f"UNWITNESSED (in plan, no worklist item): {len(unwit)}")
        for l in unwit:
            print(f"    {l}")
        print(f"DANGLING §refs (cited, no such section): {len(dang)}")
        for l in dang:
            print(f"    §{l}")
        sys.exit(1 if (orph or dang) else 0)

    if "--superseded" in sys.argv:
        rows = superseded(path)
        for noun, vals in rows[:25]:
            spread = " · ".join(f"{v} (:{ln})" for v, ln in vals)
            print(f"  {noun:<12} {spread}")
        print(f"{len(rows)} noun(s) carry conflicting figures "
              f"(widest spread first; two values may be two real populations)")
        sys.exit(0)

    print(__doc__)
    sys.exit(2)
