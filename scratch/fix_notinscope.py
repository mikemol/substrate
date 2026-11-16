#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Re-supply a `[NotInScope]` name by adding the BARE import of its definer.

⟡public-policy.  Decomposition retires a barrel, and a consumer that reached a
name THROUGH it loses its provider.  Agda reports that precisely — file, name,
and sometimes a suggestion — so the repair is mechanical: look the name up in
the definition index and add `open import <definer>` with NO `using` filter
(the ban-compliant shape).

REFUSE-ON-AMBIGUITY, as everywhere in this toolchain: a name with several
definers is not repaired by guessing which one the file meant.  It is printed
with its candidates and left for the build to arbitrate.

Each addition is isolate-typechecked and REVERTED if it does not help, so a
wrong guess cannot accumulate silently.
"""
import re, sys, os, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agda_defs
from agda_imports import add_import as _add_import
import agda_lex                       # body_tokens / mask_comments — the lexer authority
import split_lemmas as _sl            # defined_names: what a file declares ITSELF

HEAD = re.compile(r"^(\S+\.agda):(\d+)\.[\d.-]+:?\s*error: \[NotInScope\]")
IMP = re.compile(r"^(?:open\s+import|import)\s+(\S+)", re.M)

AG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")

# ⚑ AGDA RESERVED WORDS — declared here because the tree has no keyword authority
# (`toolmodes --find "agda reserved keyword list"` → none). A token scan cannot
# tell `where` from a name, and the def-index will happily report a "home" for any
# module that defines something spelled the same. If a keyword authority is ever
# added to `agda_lex`, this moves there and this comment is the pointer.
KEYWORDS = {
    "open", "import", "module", "where", "let", "in", "do", "with", "rewrite",
    "record", "data", "field", "constructor", "postulate", "primitive",
    "private", "public", "abstract", "instance", "mutual", "using", "hiding",
    "renaming", "to", "infix", "infixl", "infixr", "syntax", "pattern",
    "variable", "opaque", "unfolding", "Set", "Prop", "forall", "quote",
    "quoteTerm", "unquote", "unquoteDecl", "tactic", "macro", "overlap",
    "coinductive", "inductive", "eta-equality", "no-eta-equality", "codata",
}


def imports_of(mod):
    """The modules `mod` itself imports (one hop, no directives parsed)."""
    p = os.path.join(AG, mod.replace(".", "/") + ".agda")
    try:
        return set(IMP.findall(open(p, errors="replace").read()))
    except OSError:
        return set()


def narrow_by_provenance(defs, src, depth=3):
    """Keep only definers REACHABLE from what the file already imports.

    A name that is ambiguous tree-wide is usually unambiguous FOR THIS FILE:
    it arrives through an import the file already has, and that import's own
    chain names exactly one owner.  Losing a `public` re-export is precisely
    this shape — the provider disappears but the path to it is still written
    in the file.  Following it is evidence, not a guess, so it is checked
    BEFORE refuse-on-ambiguity rather than instead of it: if the narrowing
    does not leave exactly one candidate, the refusal stands unchanged.
    """
    if len(defs) < 2:
        return defs
    seen, frontier = set(), set(IMP.findall(src))
    for _ in range(depth):
        frontier -= seen
        if not frontier:
            break
        seen |= frontier
        frontier = set().union(*(imports_of(m) for m in frontier)) if frontier else set()
    hit = [d for d in defs if d in seen]
    return hit if len(hit) == 1 else defs


def parse(log):
    out, lines = [], open(log, errors="replace").read().split("\n")
    for i, l in enumerate(lines):
        h = HEAD.match(l)
        if h and i + 2 < len(lines) and lines[i + 1].strip() == "Not in scope:":
            out.append((h.group(1), lines[i + 2].strip()))
    return out


def unresolved(path, idx=None):
    """Ⓒ6 — [(path, name)] the file USES that NO import of its provides. Static.

    ⚑ A BUILD LOG NAMES ONE MISSING IMPORT PER FILE, NOT ALL OF THEM, because
    scope checking HALTS at the first failure. Measured twice in one batch:
    `Surreal/Approx` was missing `SurrealFinite` AND `≈ⁿ`, and the log showed only
    the first; `MixColumns/Proof/G/Equiv` was missing `cong₂` AND `cong`, and
    fixing `cong₂` at :22 merely advanced the error to `cong` at :68 — one extra
    build cycle to learn something the tree already knew. **A log is a record of
    what the compiler REACHED, never of what a file is missing.** Same shape as
    `resolve_notinscope`'s own ⚑: *"a tool whose input is a BUILD ARTIFACT cannot
    answer a question about the TREE"*.

    ⚑ IT SHARES THE LOG PATH'S ENTIRE DOWNSTREAM. `classify`, `narrow_by_provenance`,
    `add_import` and `check` never touch the log — they take `(path, name)` pairs.
    So this is a second INPUT, not a second repairer; the refuse-on-ambiguity rule
    and the isolate-typecheck both apply unchanged.

    ⚑ KEEP-BIASED, LIKE EVERY PREDICATE HERE. A name is reported only when the
    def-index KNOWS a definer for it and the file imports none of them. An unknown
    name is silent: it may be a local binding, a stdlib name, or a pattern
    variable, and reporting those would bury the real finding. So a clean result is
    *"nothing I can see"*, never *"nothing is missing"* — the census-green rule.
    """
    # ⚑ KEYWORDS AND LOCAL BINDERS ARE NOT UNRESOLVED NAMES, AND THE FIRST CUT
    # REPORTED THEM. Over `TensorProductView` it printed `import`, `open`, `where`
    # (Agda KEYWORDS) and `m n p q` (lambda/telescope binders) beside the one true
    # finding, `ℕ+` — 8 false positives to 1 real. Each was "unresolved" only
    # because some module happens to DEFINE a one-letter name, so the def-index
    # lookup succeeded by coincidence of spelling.
    #
    # ⚑ A FALSE POSITIVE IN A QUERY YOU ACT ON IS A BUG, NOT A CAVEAT — the
    # toolkit's own rule. A mode that reports `where` as a missing import cannot
    # be trusted for the one line that matters, so the noise is not a cosmetic
    # issue: it destroys the mode's purpose.
    #
    # There is no keyword authority in the tree (`toolmodes --find` returns none),
    # so this list is declared HERE and is the thing to move if one appears.
    idx = idx if idx is not None else agda_defs.def_index()
    src = open(path, encoding="utf-8", errors="replace").read()
    body = agda_lex.mask_comments(src)
    have = set(IMP.findall(body))
    # ⚑ names this file DECLARES are not missing — it is their definer. Ask the
    # authority (`split_lemmas.defined_names`), not a local re-derivation: it
    # already knows constructors, record fields and pattern synonyms, each of
    # which cost a measured bug when a caller scanned column-0 signatures instead.
    local = _sl.defined_names(body.split("\n")) | _sl.field_names(body.split("\n"))
    _selfmod = os.path.relpath(path, AG)[:-5].replace(os.sep, ".")
    out, seen = [], set()
    for tok in agda_lex.body_tokens(body, set()):
        if tok in seen or tok in local or tok in KEYWORDS:
            continue
        # ⚑ A SHORT NAME IS NOT EVIDENCE. `m`, `n`, `p`, `q` are lambda and
        # telescope binders on nearly every line here, and the def-index matched
        # them against unrelated modules that happen to define a one-letter name.
        # Binders are not tracked by this static read, so a name too short to
        # discriminate is skipped rather than guessed — the same refuse-on-
        # ambiguity discipline the log path already applies, one step earlier.
        # ⚑ Ⓠ8ᵃ: `isalpha()` IS THE WRONG TEST — it is FALSE for `a₂`, because the
        # subscript `₂` is category No (numeric), not a letter. So the guard skipped
        # `m` and passed `a₂` through, and at tree scale the top of the "repairable"
        # list was binders: `a₂` 35, `c₁`/`c₂` 29 each, `L₁`/`L₂` 14 each. Strip the
        # subscripts/primes a binder conventionally carries, then judge the STEM.
        _stem = tok.rstrip("₀₁₂₃₄₅₆₇₈₉'′")
        if len(_stem) <= 2 and _stem.isalpha():
            continue
        # ⚑ A DOTTED TOKEN IS A MODULE REFERENCE, NOT A BARE NAME. The tokenizer
        # yields `Substrate.Foundation.Bool.Not` whole, and the def-index holds a
        # same-spelled entry, so it was reported 33 times as a missing import — but
        # no import can supply a name that already names its own path.
        if "." in tok:
            continue
        homes = {m for m in idx.get(tok, ()) if m}
        # ⚑ A FILE NEVER IMPORTS ITSELF. `*P-via-tensor` reported with its OWN
        # module as the sole home — the def-index knows the declaration but
        # `defined_names` did not (it is a nested or operator-shaped decl the
        # column-0 scanner misses, Ⓒ2's blind spot showing through). Dropping the
        # self-home is correct regardless of which authority was short: a
        # suggestion to `open import <this very module>` is the
        # [CyclicModuleDependency] that `add_import`'s own guard exists to stop.
        homes -= {_selfmod}
        if not homes or (homes & have):
            continue                     # unknown, self-defined, or already provided
        seen.add(tok)
        out.append((os.path.relpath(path, AG), tok))
    return out


ALIAS = re.compile(r"[^\s(){}\[\];,]*⟦[0-9a-f]{8}⟧[^\s(){}\[\];,]*")


def stripped_aliases(path):
    """Ⓜ5 — [(path, alias)] every DEDUP-HASH ALIAS this file still cites.

    ⚑⚑ THE `⟦hash⟧` IS A GATE'S REMEDY VOCABULARY, NOT DEDUP BOOKKEEPING — and
    my first reading was WRONG, recorded here as fact and reached three
    docstrings. I inferred *"marks two definitionally-EQUAL declarations"* from
    the dedup commit messages (`24cf1afa`, `8415591a`, `3b0635cc`). It encodes
    the OPPOSITE. `scripts/_agdatext.py:121` mints
        sha1(kind | sorted, whitespace-collapsed constructor/field TYPE bodies)[:8]
    and `_agdatext.genuine_ambiguity` (:131) fires when a name's shapes **DIFFER**
    across modules. The alias means *"this Name, the one shaped like THIS"* — a
    per-consumer pin against a real collision.

    ⚑ THE GATE THAT DEMANDS IT is `scripts/check_import_shape.py`, whose message
    (:79) prescribes exactly this form and whose `BASELINE = 0` (:69) makes it a
    0-TOLERANCE VIOLATION GATE, not a ratchet. The live index is
    `scratch/sppf_collision_index.md`; `decl_shape_tag.py` writes the matching
    `⟦shape:<hash> heads⟧` at the DECLARATION. Declaration tag = advertisement,
    rename target = citation — ONE vocabulary, two positions.

    ⚑⚑ SO THIS REPAIR IS HALF THE INTENDED PAYDOWN, AND THE DESIGN SAYS SO.
    `check_ban_ratchet.py:26-37` records that the two gates conflict DELIBERATELY
    and names the resolution: *"move the disambiguation to where it belongs —
    rename at the DEFINITION (`rename_at_source.py`) … Both gates therefore reach
    0 together."* Collapsing an alias to its bare name restores compilability and
    RE-CREATES the collision the alias was pinning. `rename_at_source` on the
    definition is the completion, not an optional extra.

    ⚑ AND AN ALIAS HASH MAY BE STALE — never resolve one against the live index.
    `Wedge⟦478f66a6⟧` / `Wedge⟦b7e6a995⟧` are NOT rows in today's index: those
    records' fields changed, so their shapes rehashed to `⟦9e8d371e⟧` /
    `⟦3014fd3e⟧`. The per-alias git census is the only sound route, which is why
    `repair_alias` is keyed on it rather than on a substitution table.

    ⚑ NOTHING RE-MINTS. No tool writes a `renaming (X to X⟦hash⟧)` clause — a
    human or an agent typed each one — so a repair is not silently undone. And
    `check_import_shape` `continue`s when there is no `using` clause, so the bare
    imports this repair writes are INVISIBLE to it. That is safety by accident of
    shape, not by design: adding a `using` filter would trip it.

    A `⟦hash⟧` name is a `renaming` TARGET, so it never had a definition — which
    is why every other mode is blind to it:

        open import …FUSepQSKI using (atom; app) renaming (Tm to Tm⟦27e68fcc⟧)

    The ban sweep (771283c8) stripped the `renaming` clauses and left the USE
    SITES, so the tree now cites names with no source anywhere.

    ⚑⚑ AND THE EXISTING INSTRUMENTS REPORT THIS AS THE WRONG THING — in three
    different directions, each honest about its own method:

      * `agda_defs <name>` → *"no definer in agda/Substrate"*, which reads as a
        MISSING DEFINITION (the Ⓑ6ᵇ class: real math to write). It is not; the
        definition exists under its bare name one import away.
      * `agda_defs --collide <name>` → *"0 providers"*, same misreading.
      * `fix_notinscope --unresolved` → SILENT, correctly: it is keep-biased and
        reports a name only when the def-index KNOWS a definer. A name with no
        definer anywhere is exactly the case it declines to guess about.
      * `agda_defs --orphans` → prints the rows, and carries a banner saying the
        mode does not work (115 names, 416 sites, zero true findings) because it
        cannot separate a dropped alias from a qualified name or a local binder.

    So four modes, and the class was still found by reading a compiler error and
    running `git show` by hand — four times, once per cluster. That is the
    judgement-in-the-turn shape: it evaporates when the turn ends.

    ⚑ THE HASH SHAPE IS THE DISCRIMINATOR, and it is why this mode can be exact
    where `--orphans` could not. `⟦[0-9a-f]{8}⟧` is minted by one tool for one
    purpose; no binder, qualified name, or hand-written operator wears it. This
    reports PRESENCE with witnesses, never absence — a file citing none is
    reported as such, not as clean.

    ⚑⚑⚑ AND THE PREDICATE SAID "CITED" WHERE THE NAME SAYS "STRIPPED" — a false
    positive that made me try to repair NINE HEALTHY FILES. MEASURED on
    `X8aSkiExistence.agda:32`:

        open import Substrate.FUSep.FUSepQReduce using (stop; shed; Reduce)
          renaming (Step to Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)

    The clause is INTACT and LIVE. The file compiles at exit 0 as it stands, and
    the repair BROKE it — collapsing two pinned names to bare `Step`/`Tm`, each
    of which collides (4 and 12 index nodes). The tool reported `refused … ON ITS
    OWN CONTENT` and reverted, which is the guard working, but it should never
    have tried: the file was never broken.

    ⚑ SO THE TEST IS "CITED **AND** UNBOUND", NOT "CITED". An alias whose own
    file still carries its `renaming` clause is a CORRECT, GATE-MANDATED pin —
    the construct `check_import_shape` exists to require. Reporting it as debt
    inverts the gate's intent, and repairing it re-creates the collision.
    That file's own comment (:27-30) says as much: *"the same disambiguation
    problem solved the shape-gate way."*
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    body = agda_lex.mask_comments(src)
    # ⚑ the aliases this file's OWN clauses still bind — these are healthy pins,
    # not debt. `renaming (X to Y)` may list several pairs in one clause.
    bound = set()
    for cm in CLAUSE.finditer(body):
        for pair in cm.group(1).split(";"):
            tm = re.search(r"\bto\s+(\S+)", pair)
            if tm:
                bound.add(tm.group(1).strip())
    out, seen = [], set()
    for m in ALIAS.finditer(body):
        tok = m.group(0)
        # a projection cites its PREFIX's binding (`Wedge⟦…⟧.quot`)
        if tok in seen or tok in bound or tok.split(".", 1)[0] in bound:
            continue
        seen.add(tok)
        out.append((os.path.relpath(path, AG), tok))
    return out


# ⚑ Ⓜ5ᶜ — THE REFS TO SEARCH, NEWEST FIRST. `771283c8^` (just before the ban
# sweep) is where a surviving clause normally sits; the three after it are the
# DEDUP commits that MINTED these aliases, for a clause that was rewritten,
# moved, or removed before the ban. A single-ref search reports "no home" for
# all of those, and that reads as "this alias never had one".
ALIAS_REFS = ("771283c8^", "3b0635cc", "8415591a", "24cf1afa")


def alias_candidates(alias):
    """Ⓜ5ᶜ — every spelling of `alias` a `renaming` clause could DECLARE.

    ⚑ A CLAUSE DECLARES THE FULL MIXFIX FORM; A USE SITE WRITES A SEGMENT.
    MEASURED at `771283c8^:DiagonalLawvereSKI.agda:25` — the clause reads
    `renaming (_⇒_ to _⇒⟦66d2c034⟧_)` while line 41 uses the bare
    `⇒⟦66d2c034⟧`. Searching the literal use-site token found nothing, and the
    census reported "no home" for an alias whose clause was one line away from
    one that DID resolve. Same hash, same module, different arity.

    ⚑ AND A PROJECTION IS NOT A NAME. `Wedge⟦478f66a6⟧.quot` is a record
    projection THROUGH the alias (`771283c8^:Factoradic.agda:67`); the clause
    only ever names `Wedge`. Nobody writes `renaming (X to Wedge⟦…⟧.quot)`, so
    searching for one is guaranteed to miss. Resolve the PREFIX.

    Both were reported as missing refs. Neither is: they are matching defects,
    and widening the ref list would not have found either — which is why this
    is separated from `ALIAS_REFS` rather than folded into it.
    """
    stem = alias.split(".", 1)[0]              # drop a projection suffix
    core = stem.strip("_")
    return [stem, f"_{core}_", core]


CLAUSE = re.compile(r"renaming\s*\(([^)]*)\)", re.S)


def clause_forms(ref="771283c8^"):
    """Ⓜ5ᵉ — {form: [(relpath, line, text)]} for every `renaming` clause at `ref`.

    ⚑⚑ THE SURVEY THAT REPLACES DISCOVERING A FORM BY HAND. Two clause shapes
    were found by accident in this arc, each after a WRONG diagnosis shipped:

      * Ⓜ5ᶜ — `⇒⟦66d2c034⟧` and `Wedge⟦…⟧.quot/.rem` read as missing refs; both
        were mixfix-arity / projection-prefix MATCHING defects.
      * Ⓜ5ᵈ — `Progress⟦cbe99ef5⟧`. I confirmed its clause at
        `c3d18a33:S5Regress.agda:34` BY HAND and then built per-file ref
        derivation anyway. The cause was form (b) below plus two wrong bounds on
        the gap (`[^\\n]` — the clause is 3 lines; `[^;]` — the intervening
        `using (…)` is semicolon-separated).

    **Two forms found by accident is not a survey.** This enumerates the whole
    population so the matcher is checked against what EXISTS rather than against
    whichever file is in front of me.

    The forms, by what binds the module the clause renames FROM:

      `open-import`  `open import M … renaming (X to Y)` — M named in the clause.
      `open-alias`   `import M as Q` … `open Q … renaming (X to Y)` — M bound on
                     a DIFFERENT line; the `open` names only the local alias.
      `open-bare`    `open M … renaming (…)` where M resolves to no `import … as`
                     — a local record or an already-open module.
      `import-only`  `import M … renaming (…)` with no `open` — the names are
                     reachable only qualified.

    ⚑ REPORTS PRESENCE WITH WITNESSES (path + line + the clause text), never a
    bare count: a form with zero rows is "none at this ref", not "no such form".
    """
    import subprocess
    root = os.path.join(AG, "..")
    try:
        files = subprocess.run(
            ["git", "grep", "-l", "--", "renaming", ref],
            cwd=root, capture_output=True, text=True, timeout=300).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    out = {}
    for f in files.split("\n"):
        f = f.strip()
        if not f.endswith(".agda"):
            continue
        try:
            txt = subprocess.run(["git", "show", f], cwd=root,
                                 capture_output=True, text=True,
                                 timeout=120).stdout
        except (OSError, subprocess.SubprocessError):
            continue
        masked = agda_lex.mask_comments(txt)
        lines = masked.split("\n")
        # local `import M as Q` bindings, for resolving form (b)
        qmap = {m.group(2): m.group(1) for m in
                re.finditer(r"^\s*import\s+(\S+)\s+as\s+(\S+)\s*$", masked, re.M)}
        rel = f.split(":", 1)[1] if ":" in f else f
        for m in CLAUSE.finditer(masked):
            ln = masked[:m.start()].count("\n") + 1
            # walk BACK to the statement head that owns this clause: the nearest
            # preceding `open`/`import` at a column no deeper than the clause.
            head, hi = None, None
            for i in range(ln - 1, max(-1, ln - 40), -1):
                s = lines[i].lstrip()
                if s.startswith(("open ", "import ")):
                    head, hi = s, i + 1
                    break
            if head is None:
                out.setdefault("orphan-clause", []).append((rel, ln, m.group(1)[:60]))
                continue
            om = re.match(r"open\s+import\s+(\S+)", head)
            if om:
                form = "open-import"
            elif re.match(r"import\s+\S+", head) and not head.startswith("open"):
                form = "import-only"
            else:
                am = re.match(r"open\s+(\S+)", head)
                form = ("open-alias" if am and am.group(1) in qmap
                        else "open-bare")
            out.setdefault(form, []).append((rel, hi, head[:70]))
    return out


def alias_refs_for(path):
    """Ⓜ5ᵈ — the refs to search FOR THIS FILE, derived from its own history.

    ⚑⚑ A GLOBAL REF LIST IS A GUESS ABOUT WHEN THE CLAUSE DIED, and for three
    aliases it was the wrong guess. `ALIAS_REFS` assumes every clause survived
    until the ban sweep at `771283c8`. MEASURED: `S5Regress.agda` has exactly ONE
    commit in its history — `c3d18a33`, a MIGRATION that conformed 15 modules
    into `Substrate.S5.*` — and the clause is right there at :34
    (`renaming (Progress to Progress⟦cbe99ef5⟧)`). The file did not exist at
    `771283c8^`, so every ref in the global list searched a tree without it.

    ⚑ SO "NO HOME IN 4 REFS" WAS A FACT ABOUT MY REF LIST, exactly as the mode's
    own message said — and the fix is not a fifth hardcoded ref, which would be
    the same guess one commit further back. **Ask the file where it has been.**
    `git log --oneline -- <path>` is the per-file authority, and the commits it
    names are the only ones that can hold that file's clause.

    Returns the file's own commits (newest first) followed by the global list, so
    a clause that DID survive to the ban sweep is still found by the cheap path.
    """
    import subprocess
    root = os.path.join(AG, "..")
    try:
        out = subprocess.run(
            ["git", "log", "--format=%H", "--", os.path.relpath(path, root)],
            cwd=root, capture_output=True, text=True, timeout=120).stdout
    except (OSError, subprocess.SubprocessError):
        return list(ALIAS_REFS)
    own = [c for c in out.split("\n") if c.strip()]
    # ⚑⚑ Ⓜ5ᵉ② — A SPLIT LEAF INHERITS ITS PARENT'S CLAUSES BUT NOT ITS HISTORY.
    # MEASURED: `Step⟦f8c709b4⟧`'s clause is at **HEAD**, in the pre-split parent
    # `ExtrudeCoEmitViaTrace.agda:19` — while the citing files are its leaves
    # `ExtrudeCoEmitViaTrace/Code.agda` and `/Next.agda`. `git log -- <leaf>`
    # names only commits touching the LEAF, so the parent's clause is
    # unreachable no matter how far back the leaf's own history is walked. The
    # ref list was never short; it was searching the wrong FILE.
    #
    # ⚑ THE PARENT IS THE DIRECTORY-NAMED SIBLING: `Foo/Bar/Leaf.agda` splits out
    # of `Foo/Bar.agda`, which is the convention every emitted leaf's own header
    # states ("split horizontally out of <parent>").
    rel = os.path.relpath(path, root)
    parent = os.path.dirname(rel) + ".agda"
    if parent != ".agda" and parent != rel:
        try:
            pout = subprocess.run(
                ["git", "log", "--format=%H", "--", parent],
                cwd=root, capture_output=True, text=True, timeout=120).stdout
            own += [c for c in pout.split("\n") if c.strip()]
        except (OSError, subprocess.SubprocessError):
            pass
    # ⚑ HEAD IS TRIED TOO, and it is not redundant with the commit list: an
    # uncommitted working tree means HEAD holds a clause the leaf's own history
    # cannot reach, which is exactly the `Step` case.
    return list(ALIAS_REFS) + ["HEAD"] + own


SPPF_INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "sppf_collision_index.md")
_IDX_ROW = re.compile(r"^-\s+`⟦([0-9a-f]{8})⟧`.*?·\s+(\S+)\s*$", re.M)
_IDX_NAME = re.compile(r"^###\s+`([^`]+)`", re.M)


def alias_home_from_index(alias):
    """Ⓜ5ᶠ — (module, bare) from `scratch/sppf_collision_index.md`. THE authority.

    ⚑⚑ THE INDEX IS WHERE AN ALIAS'S HOME ACTUALLY LIVES, and I spent three
    symbols asking git instead. A `⟦hash⟧` is minted by `_agdatext.shape_decls`
    and PUBLISHED here by `scripts/sppf_node_index.py`; the `renaming` clause in
    a consumer is a CITATION of this row, not its source. So searching git for a
    clause answers *"did some consumer once cite it"* when the question is
    *"which declaration does this hash name"*.

    ⚑ MEASURED, AND IT FALSIFIED MY OWN VERDICT. `Terminal⟦ac030497⟧` reported
    `MINTED IN THE WORKING TREE — no committed ref mentions this alias` because
    no clause was found. It is row `:64` of the index —
    `Substrate.ShadowArchitecture.Raven.Grammar`, `data {awen-taso, añelē,
    other-attr}` — and `agda_defs --provides` confirms that module exports
    `Terminal`. The alias had a home the whole time; I was asking the wrong
    oracle, for the third time in this arc.

    ⚑ A MISS HERE IS STILL A REAL MISS, and differently from git: an alias whose
    hash is STALE (the declaration's fields changed, so it rehashed) is absent
    from the CURRENT index even though it named something real. `Wedge⟦478f66a6⟧`
    and `Wedge⟦b7e6a995⟧` are exactly that — today's Wedge shapes are
    `⟦3014fd3e⟧` / `⟦9e8d371e⟧`. So the index resolves the LIVE hashes and git
    resolves the STALE ones; neither subsumes the other, and the caller tries
    both rather than picking a favourite.
    """
    stem = alias.split(".", 1)[0]
    m = re.search(r"⟦([0-9a-f]{8})⟧", stem)
    if not m:
        return None
    want = m.group(1)
    try:
        txt = open(SPPF_INDEX, encoding="utf-8").read()
    except OSError:
        return None
    # ⚑⚑ A HASH MAY HAVE MANY ROWS, AND THE FIRST IS NOT THE ANSWER. The hash is
    # of the SHAPE, so every module declaring that shape shares it:
    # `Tm⟦533ef80d⟧` has SEVEN rows (index :11-:20 — NewmanKI, NewmanSKI,
    # SKIFaithfulRb, SKIGradedTraceChain, SKIShedDuality, SKITermToShedding,
    # AgdaExtrude, FUSepConvEtaWitness, FUSepQReduce). Taking the first resolved
    # it to `NewmanKI` while the pre-ban clause says `SKIShedDuality` — a WRONG
    # HOME that would compile somewhere and fail far away, which is the exact
    # failure this tool exists to refuse.
    #
    # ⚑ SO THE INDEX DISAMBIGUATES A NAME BY SHAPE, NOT A SHAPE BY MODULE. It
    # answers "which shapes does this name have"; it cannot answer "which of the
    # seven modules sharing this shape did THIS consumer mean". Only the clause
    # can, which is why git is not a fallback here but the AUTHORITY for a
    # multi-row hash. Refuse rather than pick.
    name, hits = None, []
    for line in txt.split("\n"):
        nm = _IDX_NAME.match(line)
        if nm:
            name = nm.group(1)
            continue
        rm = _IDX_ROW.match(line)
        if rm and rm.group(1) == want and name:
            hits.append((rm.group(2), name))
    return hits[0] if len(hits) == 1 else None


def alias_in_git(alias):
    """Ⓜ5ᵉ③ — True if ANY committed ref mentions `alias` at all.

    ⚑ "NO HOME IN GIT" AND "NEVER COMMITTED" ARE DIFFERENT FINDINGS, and
    reporting them as one is true but useless. MEASURED: `Terminal⟦ac030497⟧` is
    absent at `8e04ab3e` (the decomposition that created its citing files) AND at
    `8e04ab3e^` — so it exists ONLY in the working tree. No amount of ref
    widening reaches it, because there is nothing to reach.

    That makes it a different KIND of debt: not archaeology to recover, but an
    alias minted by an uncommitted edit and never committed. The operator needs
    to know which, because the next actions are opposite — search harder vs.
    decide what the name should have been.

    ⚑⚑ NOT `git log --all -S`, WHICH I WROTE FIRST AND WHICH HUNG THE SELFTEST.
    The pickaxe re-diffs every commit in the repo; measured earlier THIS SESSION
    it exceeded a 10-minute timeout on one alias, and putting it in `_selftest`
    took a 40-case suite from seconds to over 600s. `git grep` over a bounded
    REF LIST answers the same question by reading trees instead of diffs.

    ⚑ SO THE ANSWER IS SCOPED TO THOSE REFS, and the docstring says so rather
    than the verdict implying more: "no committed ref I searched mentions it".
    That is still decisive for the case it exists for — an alias minted in the
    working tree appears in NO tree — while staying honest about the method.
    """
    import subprocess
    root = os.path.join(AG, "..")
    for r in list(ALIAS_REFS) + ["HEAD"]:
        try:
            out = subprocess.run(["git", "grep", "-l", "--", alias, r],
                                 cwd=root, capture_output=True,
                                 text=True, timeout=120).stdout
        except (OSError, subprocess.SubprocessError):
            return True      # ⚑ keep-biased: an unanswerable probe is not evidence
        if out.strip():
            return True
    return False


def alias_home(alias, ref=None):
    """Ⓜ5 — (module, bare_name) the alias was renamed FROM, recovered from git.

    ⚑ THE ARCHAEOLOGY IS THE ONLY AUTHORITY, because the current tree has no
    record: the clause that defined the alias is what the sweep deleted. A
    pre-ban ref still holds
        `open import <MOD> … renaming (<bare> to <alias>)`
    and that line is the entire mapping. Recovering it by hand is a `git show`
    plus an eye-scan, done four times in one session before this existed.

    ⚑ Ⓜ5ᶜ — SEVERAL REFS AND SEVERAL SPELLINGS, because one of each was wrong.
    The bare `⇒⟦66d2c034⟧` and the projections `Wedge⟦478f66a6⟧.quot/.rem` were
    all reported as "no home" by a single-ref, literal-token search; all three
    resolve once the mixfix/projection forms are tried (`alias_candidates`).
    The remaining misses get the DEDUP commits that minted the aliases.

    ⚑ THE RETURNED `bare` IS THE CLAUSE'S SOURCE NAME AT ITS OWN ARITY — `_⇒_`,
    not `⇒`. `repair_alias` re-shapes it to match the alias it is replacing;
    doing that here would lose the information it needs.

    Returns None when no clause names the alias in ANY searched ref — a fact
    about the SEARCHED REFS, not proof the alias was never bound. Say which.
    """
    import subprocess
    # ⚑ Ⓜ5ᵈ — `ref` may be a single ref OR a list. A file whose clause died at a
    # MIGRATION rather than at the ban sweep is invisible to the global list, so
    # the caller passes `alias_refs_for(path)` to search where the file has
    # actually been. A bare string still works for a one-off probe.
    refs = ((ref,) if isinstance(ref, str) else tuple(ref)) if ref else ALIAS_REFS
    cands = alias_candidates(alias)
    root = os.path.join(AG, "..")
    for r in refs:
        for cand in cands:
            try:
                files = subprocess.run(
                    ["git", "grep", "-l", "--", cand, r],
                    cwd=root, capture_output=True,
                    text=True, timeout=120).stdout.split("\n")
            except (OSError, subprocess.SubprocessError):
                continue
            # ⚑⚑ Ⓜ5ᵈ — TWO CLAUSE FORMS, AND MY REGEX KNEW ONLY ONE.
            #   (a) `open import <MOD> … renaming (X to <alias>)`  — one line,
            #       the module named in the clause itself.
            #   (b) `import <MOD> as Q` … `open Q … renaming (X to <alias>)` —
            #       the module is bound on a DIFFERENT LINE and the `open` names
            #       only the local alias `Q`.
            # MEASURED at `c3d18a33:S5Regress.agda:33-34`: `import
            # Substrate.S5.S5Verdict as S5Verdict` then `open S5Verdict … renaming
            # (Progress to Progress⟦cbe99ef5⟧)`. Form (b) matched nothing, so THREE
            # aliases reported "no home" while their clauses sat in the searched
            # ref — I had confirmed one BY HAND and still shipped a ref-widening
            # fix for what was a MATCHING defect. Second time in this symbol.
            # ⚑⚑ Ⓜ5ᵉ — `[^\n]*?` WAS WRONG HERE TOO, AND I FIXED IT ONLY IN
            # `pat_b`. MEASURED at `HEAD:ExtrudeCoEmitViaTrace.agda:18-19`:
            #     open import …ExtrudeCoEmitMonad ℕ
            #       using (…) renaming (Step to Step⟦f8c709b4⟧)
            # an APPLIED `open import` (argument `ℕ`) whose clause continues on
            # the NEXT line. Form (a) is not "always one line" — that was true of
            # the examples I happened to read. The census classified this row
            # `open-import` correctly; the MATCHER carried the same line-bound bug
            # I had already diagnosed and fixed one pattern away.
            # ⚑⚑ AND A BARE `.*?` IS *NOT* SAFE, WHICH MY FIRST CUT ASSUMED.
            # I argued "the alias is unique, so the first match is the right one"
            # — true of the ALIAS, false of the MODULE CAPTURE. Unbounded, the
            # gap ran ACROSS statements: `Tm⟦27e68fcc⟧` resolved to
            # `Substrate.Foundation.Eq` (an earlier `open import` in the same
            # file) and `Step⟦f8c709b4⟧` to `Substrate.Foundation.Nat`. Both
            # wrong, both plausible, and a wrong home is the failure mode this
            # whole tool exists to refuse.
            # ⚑ WHAT ACTUALLY BOUNDS THE GAP IS THE NEXT STATEMENT — so forbid a
            # statement keyword at column 0 between the head and the clause.
            _gap = r"(?:(?!\n(?:open|import|module)\b)[\s\S])*?"
            pat_a = re.compile(
                r"open\s+import\s+(\S+)" + _gap +
                r"renaming\s*\([^)]*?([^\s;(]+)\s+to\s+"
                + re.escape(cand) + r"\s*[;)]")
            # ⚑ THE CLAUSE SPANS LINES, so `[^\n]*?` cannot reach the `renaming`:
            #     open S5Verdict
            #       using (…)
            #       renaming (Progress to Progress⟦cbe99ef5⟧)
            # `pat_a` gets away with `[^\n]*?` because form (a) names its module
            # on the same line as `open import`; form (b) does not, and the very
            # file that motivated this fix is three lines tall. An Agda statement
            # is not a line — the blind spot this repo has now recorded five times.
            # ⚑ AND `[^;]*?` FAILS TOO, because the `using (...)` clause between
            # `open Q` and `renaming` is SEMICOLON-SEPARATED:
            #     open S5Verdict
            #       using (_≡_; refl; sym; …)
            #       renaming (Progress to Progress⟦cbe99ef5⟧)
            # So neither "same line" nor "no semicolons" bounds the gap. What
            # actually bounds it is the next STATEMENT — and `.*?` non-greedy up
            # to the alias is safe here precisely because the alias is unique in
            # the tree (an 8-hex hash minted once), so the first match IS the
            # right one. Uniqueness is doing the bounding that structure cannot.
            # ⚑ SAME BOUND AS `pat_a` — `pat_b`'s `.*?` had the identical
            # cross-statement flaw and simply had not been caught yet. Fixing one
            # pattern and leaving its twin is how `pat_a` survived Ⓜ5ᵈ.
            pat_b = re.compile(
                r"open\s+([A-Za-z_][^\s(]*)" + _gap +
                r"renaming\s*\([^)]*?([^\s;(]+)"
                r"\s+to\s+" + re.escape(cand) + r"\s*[;)]")
            for f in files:
                if not f.strip():
                    continue
                try:
                    txt = subprocess.run(["git", "show", f.strip()], cwd=root,
                                         capture_output=True, text=True,
                                         timeout=120).stdout
                except (OSError, subprocess.SubprocessError):
                    continue
                m = pat_a.search(txt)
                if m:
                    return (m.group(1), m.group(2))
                m = pat_b.search(txt)
                if m:
                    # resolve the local alias to the module it was bound from
                    q = re.search(r"^\s*import\s+(\S+)\s+as\s+"
                                  + re.escape(m.group(1)) + r"\s*$",
                                  txt, re.M)
                    if q:
                        return (q.group(1), m.group(2))
    return None


def topo_key(paths):
    """Ⓜ6 — {relpath: rank} in DEPENDENCY ORDER, roots first. Never a local sort.

    ⚑ THE BUILD ALREADY OWNS THIS DAG, and re-deriving it would be a third
    implementation of a relation that has one authority.
    `gen_build_makefiles.parse_tree()` returns `(disk, deps)` source-parsed from
    `open import`, and `gen_build_makefiles.kahn_depth(disk, deps)` returns
    `(critical_path_depth, topological_order)` over the WHOLE tree.
    `split_census._import_dag()` is a memo in front of the same call, not a
    second parse.

    ⚑ NOT `replay_pipeline.toposort`, though the name is a better match. That one
    re-parses the DAG with its own regex and BREAKS cycles to keep going, where
    `kahn_depth` exits — a different contract for a different job.

    ⚑ THE ORDER MUST BE WHOLE-TREE, NOT TARGET-ONLY. A target is safe to compile
    when all its TRANSITIVE deps have settled, not merely the ones that happen to
    also be targets — so ranking the 91 among themselves would still leave a
    target waiting on a non-target. Rank against the full order and index in.

    ⚑ AND `kahn_depth` EXITS ON A CYCLE (sys.exit(2)) — it is a gate, not a pure
    function. Unreachable modules simply get no rank and sort last, which is the
    keep-biased direction: an unranked file is repaired after the ranked ones,
    never silently dropped.
    """
    try:
        sys.path.insert(0, os.path.join(AG, "..", "scripts"))
        import gen_build_makefiles as _gen
        disk, deps = _gen.parse_tree()
        _depth, order = _gen.kahn_depth(disk, deps)
    except Exception:
        return {}                       # no order available: caller keeps input order
    rank = {m: i for i, m in enumerate(order)}
    # `disk` maps module -> relpath in exactly the spelling our inputs use.
    by_path = {rel: rank.get(mod, len(rank)) for mod, rel in disk.items()}
    return {p: by_path.get(p, len(rank)) for p in paths}


def _module_of(path):
    """`.../agda/Substrate/Foundation/Eq.agda` -> `Substrate.Foundation.Eq`.

    ⚑ FROM THE PATH, NOT THE `module` LINE — the two can disagree only in a broken file,
    and the build is the arbiter of that; what the cycle check needs is the name the
    IMPORT GRAPH keys on, which is the path.
    """
    p = os.path.abspath(path)
    if "Substrate" not in p.split(os.sep) or not p.endswith(".agda"):
        return None
    parts = p[:-len(".agda")].split(os.sep)
    return ".".join(parts[parts.index("Substrate"):])


def repair_imports_in_file(path, names, idx):
    """Add every single-definer import ONE file needs, then compile ONCE.

    Returns (verdict, detail) — 'repaired' / 'reverted' / 'blocked' / 'no-op'.

    ⚑⚑⚑ THE UNIT IS THE FILE, AND `repair_file`'s DOCSTRING IS WHY — I wrote the per-NAME
    loop first and it has the defect that function already records: *"a per-alias sweep
    over multi-alias files is not slow, it is NON-CONVERGENT."*  A file missing three
    imports cannot typecheck until all three land, so a per-name loop adds one,
    isolate-checks, sees the OTHER two still failing, and REVERTS the correct fix it just
    made.  Next pass repeats it exactly.  Same shape, different tool, and the sibling had
    it written down — reuse-search on my own file, not a rediscovery.

    ⚑ SO: snapshot, add ALL of them, ONE isolate-check, and on failure restore the
    ORIGINAL text — never a half-repaired state, which is worse than either endpoint.

    ⚑ AMBIGUOUS NAMES DO NOT BLOCK THE OTHERS but they do keep the file failing, so a
    file whose remaining errors are ambiguous reports 'reverted' honestly rather than
    claiming a repair that did not make it compile.  A green verdict on a file that still
    cannot build would be the census-green-is-a-fact-about-the-census shape.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    FALLBACK = {",": "Substrate.Foundation.Product",
                "tt": "Substrate.Foundation.Unit",
                "[]": "Substrate.Foundation.List",
                "∷": "Substrate.Foundation.List"}
    adds = []
    for name in names:
        defs = sorted(idx.get(name, []) or idx.get(f"_{name}_", []))
        if not defs and name in FALLBACK:
            defs = [FALLBACK[name]]
        defs = [d for d in defs if not re.search(
            r"^(open\s+import|import)\s+" + re.escape(d) + r"\b", src, re.M)]
        defs = narrow_by_provenance(defs, src)
        if len(defs) == 1:
            adds.append((name, defs[0]))
    # ⚑⚑ DEDUPE THE MODULES — several missing names commonly share ONE home, and the
    # per-name loop added it once per name. Measured on the S5 trial: `S5EEA.agda` got
    # `+3 import(s): Foundation.List, Foundation.List, Foundation.List`. That is not
    # cosmetic — `split_lemmas.strip_using`'s own note records that a parameterized module
    # imported twice is APPLIED and ELABORATED twice, which is the ⟡cap-ratchet blowup
    # mechanism. A repair tool that inflates elaboration cost while fixing scope trades
    # one gate's debt for another's.
    _seen, _uniq = set(), []
    for _n, _m in adds:
        if _m not in _seen:
            _seen.add(_m)
            _uniq.append((_n, _m))
    adds = _uniq
    # ⚑⚑⚑ REFUSE AN IMPORT THAT WOULD CLOSE A CYCLE — the isolate-check CANNOT catch this,
    # and that is the defect class this guard exists for. `check(path)` compiles ONE file;
    # a cycle is a property of the import GRAPH, so a repair can pass its own check and
    # break the tree. MEASURED 2026-08-23 on the tree-wide sweep: `Foundation.Eq` — the
    # most-imported leaf in the corpus — was given `open import Substrate.Category.
    # BoundaryEvent` to supply a name, closing `Eq → BoundaryEvent → Eq` and producing 12
    # CyclicModuleDependency failures where there had been ZERO.
    #
    # ⚑ THE ASYMMETRY IS WHY THIS IS A REFUSAL AND NOT A WARNING. A missing import leaves
    # one file failing; a cycle can take out every consumer of a hub. The candidate's own
    # transitive closure is the authority (`agda_defs.closure_of`), and a candidate that
    # already reaches THIS module is refused outright — never guessed at, never applied and
    # rolled back, because by the time the build reports it the sweep has moved on.
    # ⚑⚑⚑ REFUSE AN IMPORT WHOSE NAME THIS FILE ALREADY DEFINES — the ClashingDefinition
    # class, and the largest single cost of the tree-wide sweep. MEASURED 2026-08-23:
    # `Foundation/Hedberg/DecidableUIP.agda` defines `cong-trans` locally; the sweep added
    # `open import Substrate.Foundation.Eq.CongTrans`, which exports a `cong-trans`, and
    # Agda refused BOTH. That one file blocked a cone of 691 modules, and a second clash
    # (`Groups/Coxeter/Word.agda:38`) blocked ~450 more.
    #
    # ⚑ THE NAME IS UNRESOLVED *AND* LOCALLY DEFINED, WHICH SOUNDS CONTRADICTORY AND IS
    # NOT. `unresolved()` reports a name the file USES and cannot bind at the use site —
    # a local definition inside a `where`, a private block, or a later module does not
    # bind it there. So "missing" and "already defined" are both true, and supplying it by
    # import turns a scope error into a clash: strictly worse, because the clash blocks
    # the file's whole consumer cone rather than the one lemma.
    #
    # ⚑ CHEAP, AND THE AUTHORITY IS THE SAME INDEX. `def_index` maps name → definers; if
    # THIS module is among a candidate name's definers, importing another home for it
    # clashes by construction. No compile needed.
    _self = _module_of(path)
    _clashfree = []
    for _n, _m in adds:
        if _self and _self in (idx.get(_n, ()) or idx.get(f"_{_n}_", ())):
            print(f"  ⚑ REFUSED {_m} for {_n} — {_self} already DEFINES {_n}; importing "
                  f"another home is a ClashingDefinition, not a repair")
            continue
        _clashfree.append((_n, _m))
    adds = _clashfree
    _safe = []
    for _n, _m in adds:
        try:
            _cone = agda_defs.closure_of(_m)
        except Exception:
            _cone = ()                      # unknown cone: fall through, the build arbitrates
        if _self and _self in _cone:
            print(f"  ⚑ REFUSED {_m} for {_n} — importing it would close a cycle "
                  f"({_m} already reaches {_self})")
            continue
        _safe.append((_n, _m))
    adds = _safe
    if not adds:
        return ("blocked", f"{len(names)} name(s), none single-definer")
    # ⚑ THE SNAPSHOT IS ARMED BEFORE THE FIRST WRITE — the repo-wide precondition for an
    # in-place source editor, and the reason it exists is that a rewrite once left 33
    # files unrecoverable. A tree-wide sweep is exactly that shape.
    import edit_snapshot as _es
    _es.guard("fix_notinscope --unresolved", [path], intent="apply")
    for _name, mod in adds:
        add_import(path, mod)
    ok, out = check(path)
    if ok:
        return ("repaired", f"+{len(adds)} import(s): "
                            + ", ".join(m for _n, m in adds))
    still = [n for n, _m in adds if n in out]
    if still:
        open(path, "w", encoding="utf-8").write(src)
        return ("reverted", f"{', '.join(still)} still unbound "
                            f"(shadowed by a stale `using`? — fix_stale_using.py)")
    # ⚑ A DIFFERENT ERROR REMAINS — the imports we added DID supply their names, so they
    # are kept. The file still fails, on the ambiguous names this mode refuses to guess.
    return ("repaired", f"+{len(adds)} import(s), a DIFFERENT error remains — kept")


def repair_file(path, homes, apply=False):
    """Ⓜ6 — repair EVERY alias in one file, then compile ONCE.

    `homes` is {alias: (module, bare)}. Returns (verdict, detail).

    ⚑⚑ THE UNIT IS THE FILE, NOT THE ALIAS — and the per-alias loop could not
    converge. MEASURED on the Ⓜ5ᶜ re-run: `DiagonalLawvereSKI.agda` was
    `[rewrote]` for `⇒⟦66d2c034⟧` and `[refused] … ON ITS OWN CONTENT; REVERTED`
    for `Tm⟦533ef80d⟧` — the SAME file, in one run. A file citing two aliases
    cannot typecheck until BOTH are rewritten, so whichever alias the loop
    reached first was reverted for an error the second one caused. The revert
    then put the first alias back, and the next pass repeated it exactly.
    **A per-alias sweep over multi-alias files is not slow, it is non-convergent.**

    ⚑ SO THE COMPILE MOVES TO THE END. All rewrites land, one isolate-check
    arbitrates, and a failure reverts the file to its ORIGINAL text — not to a
    half-repaired state, which would be worse than either endpoint.

    ⚑ AN ALIAS WITH NO KNOWN HOME BLOCKS THE FILE, and that is deliberate. Its
    citations stay, so the file still cannot compile; repairing its siblings and
    reporting success would be a green that hides the remaining debt. Report the
    file as blocked and name the alias.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    cited = [a for _p, a in stripped_aliases(path)]
    if not cited:
        return ("no-op", "cites no alias outside comments")
    unknown = [a for a in cited if a not in homes]
    if unknown:
        return ("blocked", f"no home for {', '.join(sorted(unknown))}")
    n = 0
    for alias in sorted(cited, key=len, reverse=True):   # longest first: `_x_` before `x`
        mod, bare = homes[alias]
        v, d = repair_alias(path, alias, mod, bare, apply=False)
        if v == "rewrote":
            n += 1
    if not apply:
        return ("would-rewrite", f"{len(cited)} alias(es), {n} rewritable")
    # ⚑ REWRITE ALL, THEN BIND ALL, THEN COMPILE ONCE.
    for alias in sorted(cited, key=len, reverse=True):
        mod, bare = homes[alias]
        _apply_alias_text(path, alias, bare)
    for alias in cited:
        mod, _bare = homes[alias]
        ok, why = _add_import(path, mod)
        if not ok and why not in ("present",):
            open(path, "w", encoding="utf-8").write(src)
            return ("refused", f"import not added: {why}")
    good, log = check(path)
    if good:
        return ("rewrote", f"{len(cited)} alias(es) repaired")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from split_pipeline import blame as _blame
        who, cited_at = _blame(os.path.relpath(path, AG), log)
    except Exception:
        who, cited_at = "own", None
    if who == "own":
        open(path, "w", encoding="utf-8").write(src)
        return ("refused", "did not typecheck ON ITS OWN CONTENT; REVERTED")
    return ("rewrote-blocked",
            f"{len(cited)} alias(es) repaired; blocked upstream by "
            f"{os.path.basename(cited_at or '?')}")


def _apply_alias_text(path, alias, bare):
    """Ⓜ6 — the TEXT half of `repair_alias`, without the import or the compile.

    ⚑ FACTORED OUT SO THE COMPILE CAN MOVE TO THE END OF THE FILE'S REPAIR.
    `repair_alias` is retained whole for the single-alias case and for its
    selftest coverage; this is the same substitution with the two side effects
    lifted to the caller, so there is ONE rewrite rule, not two.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    masked = agda_lex.mask_comments(src)
    if alias.startswith("_") and alias.endswith("_"):
        repl = f"_{bare.strip('_')}_"
    elif bare.startswith("_") and bare.endswith("_"):
        repl = bare.strip("_")
    else:
        repl = bare
    out, i = [], 0
    for m in re.finditer(re.escape(alias), src):
        if masked[m.start():m.end()] != alias:
            continue
        out.append(src[i:m.start()])
        out.append(repl)
        i = m.end()
    out.append(src[i:])
    open(path, "w", encoding="utf-8").write("".join(out))


def repair_alias(path, alias, mod, bare, apply=False):
    """Ⓜ5ᵇ — rewrite one stripped alias to its bare name and bind its home.

    Returns (verdict, detail). Verdicts: `rewrote` / `no-op` / `refused: …`.

    ⚑⚑ THE HOME IS PER-ALIAS AND MUST NOT BE INFERRED FROM THE BARE NAME —
    this is the whole reason the write is keyed on the census rather than on a
    substitution table. MEASURED: `Wedge⟦478f66a6⟧` (15 files) resolves to
    `Substrate.Algebra.Wedge` while `Wedge⟦b7e6a995⟧` (8 files) resolves to
    `Substrate.Algebra.Nat.GCD.Wedge`. BOTH spell out as `Wedge`. A uniform
    "strip the hash, add the obvious import" sweep would silently point the 8
    GCD files at the wrong module — and it would very likely TYPECHECK
    somewhere before failing far away, which is the shape that gets banked.
    **The hash was carrying the disambiguation the bare name cannot.**

    ⚑ THE ALIAS IS REPLACED BY ITS BARE COUNTERPART AT THE SAME MIXFIX ARITY.
    `_⇒⟦66d2c034⟧_` is the DECLARATION form of `⇒⟦66d2c034⟧`, and the census
    reports both; each maps to the correspondingly-shaped bare name (`_⇒_` /
    `⇒`). Rewriting the bare form to the underscored one (or vice versa) is a
    parse error at best and a silently different fixity at worst.

    ⚑ A QUALIFIED SUFFIX IS PART OF THE TOKEN, NOT A SEPARATE NAME.
    `Wedge⟦478f66a6⟧.quot` is a projection THROUGH the alias; the census lists
    it as its own row precisely so this function is never asked to guess
    whether a trailing `.quot` belongs to the name. It rewrites the alias
    PREFIX and leaves the suffix untouched.

    ⚑ COMMENTS ARE MASKED BEFORE MATCHING BUT WRITTEN BACK VERBATIM. The
    repaired files in this arc carry ⚑ notes that QUOTE the alias they removed;
    rewriting those would corrupt the archaeology that explains the fix — and
    counting them would make every repaired file look unrepaired.
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    masked = agda_lex.mask_comments(src)
    if alias not in masked:
        return ("no-op", "alias not cited outside comments")
    # the bare name at the SAME mixfix arity as the alias
    if alias.startswith("_") and alias.endswith("_"):
        repl = f"_{bare.strip('_')}_"
    elif bare.startswith("_") and bare.endswith("_"):
        repl = bare.strip("_")
    else:
        repl = bare
    out, i, n = [], 0, 0
    for m in re.finditer(re.escape(alias), src):
        # ⚑ ONLY OUTSIDE COMMENTS. `mask_comments` blanks comment spans while
        # PRESERVING offsets, so a hit whose masked span differs is commentary.
        if masked[m.start():m.end()] != alias:
            continue
        out.append(src[i:m.start()])
        out.append(repl)
        i, n = m.end(), n + 1
    if not n:
        return ("no-op", "every citation is in a comment")
    out.append(src[i:])
    new = "".join(out)
    if apply:
        open(path, "w", encoding="utf-8").write(new)
        # the shared writer: self-import guard + topo order + permutation check
        ok, why = _add_import(path, mod)
        # ⚑ "ALREADY PRESENT" IS SUCCESS, NOT REFUSAL — and my first cut reported
        # it as `refused` on 6 files whose rewrite had ACTUALLY LANDED. The
        # shared writer returns False for "I did not write a line", which
        # conflates "the import is there already" with "I could not add it".
        # The verdict said the repair failed while the tree said it succeeded;
        # a census that misreports its own writes is the shape that gets banked.
        # Verified on `Algebra/Wedge/Compose.agda`: reported refused, cites zero
        # aliases afterwards.
        if not ok and why != "present":
            return ("refused", f"import not added: {why}")
        # ⚑ ISOLATE-TYPECHECK AND REVERT, as every repair here already does. A
        # wrong home compiles nowhere, so the compiler is the arbiter — and a
        # guess that does not help must not accumulate silently.
        good, log = check(path)
        if not good:
            # ⚑⚑ A FAILURE IN A DEPENDENCY IS NOT THIS FILE'S FAULT, AND MY FIRST
            # CUT REVERTED ON IT — refusing every file in dependency order.
            # MEASURED on `ExtrudeSKISetoid`: both its aliases were rewritten
            # correctly and both were reverted, because the compile failed at
            # `DiagonalLawvereSKI:41` (an UPSTREAM file still citing an alias).
            # An alias sweep repairs a DAG: until the roots are done, every leaf
            # legitimately fails on someone else, so a blind revert makes the
            # sweep unable to ever start. `split_pipeline.blame` is the authority
            # that already draws this line — 9 of 12 "failures" it examined cited
            # a dependency — and it is why that function exists.
            _sp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "split_pipeline.py")
            try:
                sys.path.insert(0, os.path.dirname(_sp))
                from split_pipeline import blame as _blame
                _who, _cited = _blame(os.path.relpath(path, AG), log)
            except Exception:
                _who, _cited = "own", None
            if _who == "own":
                open(path, "w", encoding="utf-8").write(src)
                return ("refused", "did not typecheck ON ITS OWN CONTENT; REVERTED")
            # KEPT: the rewrite stands, the blocker is elsewhere in the DAG.
            return ("rewrote-blocked",
                    f"{n} site(s) -> {repl}, bound at {mod}; "
                    f"blocked upstream by {os.path.basename(_cited or '?')}")
    return ("rewrote", f"{n} site(s) -> {repl}, bound at {mod}")


def add_import(path, mod):
    """Delegates to the ONE import-writer (`agda_imports.add_import`).

    ⚑ This was a SECOND, unguarded implementation, and the duplication cost exactly
    what duplication always costs here: when a self-import guard was added to the
    shared writer, five files kept getting `open import <their own module>` written
    back — because this copy never saw the guard.  Agda reports that as
    [CyclicModuleDependency] ("X importing X"), which reads like a real structural
    cycle.  The shared writer also does topo ordering and the permutation check that
    this copy's blind `insert(last+1)` skipped.
    """
    ok, _ = _add_import(path, mod)
    return ok


def check(path):
    r = subprocess.run(["../scripts/membudget", "run", "384", "nis", "--",
                        "agda", "--safe", "--without-K", "-i.", os.path.relpath(path, "agda")],
                       cwd="agda", capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr


def classify(log):
    """[(path, name, verdict, homes)] — the DIAGNOSIS half, without repairing.

    ⚑ THIS TOOL IS TWO TOOLS, AND ONE OF THEM IS WITNESS-SHAPED (user,
    2026-08-03: *"fix_notinscope is two tools in one. One is witness-shaped in
    a way that should be surfacing more virtual items."*).  It CLASSIFIES every
    not-in-scope name — resolvable / ambiguous / no-definer — and then REPAIRS
    the resolvable ones.  The classification was computed inline in `__main__`,
    printed, and discarded, so the only way to reach it was to read a run.

    ⚑ AND THE VERDICTS ARE DIFFERENT VIRTUAL ITEMS, not one.  Measured over the
    44-module class: ~19 names have NO DEFINER ANYWHERE (`<ℕ`,
    `Tm⟦27e68fcc⟧`) — a name that was renamed at its definer or whose binder was
    deleted; ~8 are AMBIGUOUS with several real homes (`≡`, `,`, `Word`) — a
    name whose provenance the file cannot narrow.  Those want different work:
    the first is rename-at-source or recover-the-binder, the second is
    narrowing evidence.  Reporting them under one `NotInScope` row reads as one
    problem with one tool.

    ⚑ NO REPAIR HAPPENS HERE.  The verdict is a measurement; the write lives in
    `__main__` behind `--apply`.  Splitting them is what lets a witness consume
    the diagnosis without risking the tree.

    ⚑ `ℕ+` WAS LISTED ABOVE AS NO-DEFINER AND IS NOT ONE. It resolves to
    `Foundation.Nat.Plus` — confirmed by `resolve_notinscope` and by `unresolved`'s
    static read. A quoted EXAMPLE ages into a false claim the moment the tree moves
    under it, which is the same defect class this census exists to catch; the
    counts (~19 / ~8) are equally a snapshot and should be re-measured, not cited."""
    idx = agda_defs.def_index()
    out, seen = [], set()
    for path, name in parse(log):
        if (path, name) in seen:
            continue
        seen.add((path, name))
        defs = sorted(idx.get(name, []) or idx.get(f"_{name}_", []))
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        defs = [d for d in defs
                if not re.search(r"^(open\s+import|import)\s+" + re.escape(d) + r"\b",
                                 src, re.M)]
        defs = narrow_by_provenance(defs, src)
        if len(defs) == 1:
            out.append((path, name, "resolvable", defs))
        elif defs:
            out.append((path, name, "ambiguous", defs))
        else:
            out.append((path, name, "no-definer", []))
    return out


def _selftest():
    """Counted from len(cases). Fixture-driven — no live tree, no build.

    ⚑ THIS TOOL HAD NO SELFTEST AT ALL (`pycodemod --calls _selftest` → 0 defs),
    and it WRITES to the tree behind `--apply`. Ⓒ6 added a mode to it and shipped
    without the guard every sibling here has, which is the gap this closes.

    ⚑ EVERY CASE IS A FALSE POSITIVE `--unresolved` ACTUALLY EMITTED on its first
    run over `TensorProductView`: 9 findings, of which 8 were noise and 1 was real.
    A mode that reports `where` as a missing import cannot be trusted for the line
    that matters — the toolkit's own rule that a false positive in a query you act
    on is a BUG, not a caveat.
    """
    import tempfile
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    d = tempfile.mkdtemp()
    ag = os.path.join(d, "agda", "Substrate", "T")
    os.makedirs(ag, exist_ok=True)

    def _write(name, body):
        p = os.path.join(ag, name + ".agda")
        open(p, "w", encoding="utf-8").write(body)
        return p

    # A def-index stub: the NAME → {modules} map `unresolved` consults. Hand-built
    # so the cases do not depend on tree state this tool cannot control.
    idx = {
        "ℕ+": {"Substrate.Foundation.Nat.Plus"},
        "where": {"Substrate.Some.Module"},        # a keyword that IS defined somewhere
        "open": {"Substrate.Other.Module"},        # ditto
        "m": {"Substrate.Unrelated.OneLetter"},    # a binder, matched by coincidence
        "mine": {"Substrate.T.Self"},              # this file's OWN declaration
        "wanted": {"Substrate.Foundation.Wanted"},
        "already": {"Substrate.Foundation.Have"},
    }

    p = _write("Self",
               "module Substrate.T.Self where\n"
               "open import Substrate.Foundation.Have\n"
               "\n"
               "mine : Set\n"
               "mine = wanted ℕ+ already\n"
               "f : (m : Set) → Set\n"
               "f m = m\n")
    got = {n for _p, n in unresolved(p, idx)}

    check("⚑ a genuinely missing name IS reported", "ℕ+" in got, True)
    check("...and so is a second one in the SAME file (the whole point of Ⓒ6)",
          "wanted" in got, True)
    # ⚑ THE THREE FALSE-POSITIVE CLASSES, each measured on the live tree
    check("⚑ an Agda KEYWORD is never reported, even when some module defines it",
          {"where", "open"} & got, set())
    check("⚑ a short BINDER is not reported (def-index matched it by spelling)",
          "m" in got, False)
    # ⚑ Ⓠ8ᵃ: A SUBSCRIPTED BINDER IS STILL A BINDER, AND `isalpha()` SAID NO.
    # `a₂` is two code points, so `len(tok) <= 2` held — but `'a₂'.isalpha()` is
    # FALSE, because `₂` is category No (a numeric subscript), not a letter. The
    # guard therefore skipped `m` and passed `a₂` straight through.
    # MEASURED AT TREE SCALE: `a₂` 35 sites, `c₁`/`c₂` 29 each, `L₁`/`L₂` 14 each,
    # `r₁`/`r₂` 14 each — all lambda/telescope binders, all reported as missing
    # imports. The single-file validation never saw them because those files were
    # not in the sample: PRECISION VALIDATED ON ONE FILE IS NOT PRECISION AT TREE
    # SCALE, which is the same lesson as the census that read 2 for a cluster of 272.
    sub = _write("Sub", "module Substrate.T.Sub where\n"
                        "open import Substrate.Foundation.Have\n"
                        "f : (a₂ L₁ c₀ : Set) → Set\n"
                        "f a₂ L₁ c₀ = a₂\n")
    subgot = {n for _p, n in unresolved(sub, {**idx,
                                              "a₂": {"Substrate.Groups.Z2.A"},
                                              "L₁": {"Substrate.Shadow.Fano"},
                                              "c₀": {"Substrate.Pipeline.Crumb"}})}
    check("⚑ Ⓠ8ᵃ: a SUBSCRIPTED short binder is not reported",
          subgot & {"a₂", "L₁", "c₀"}, set())
    # ⚑ AND A QUALIFIED MODULE PATH IS NOT A NAME. `Substrate.Foundation.Bool.Not`
    # was reported 33 times: the tokenizer yields the dotted path and the def-index
    # holds a same-spelled entry. A token containing a dot is a module reference,
    # never a bare name that an import could supply.
    dot = _write("Dot", "module Substrate.T.Dot where\n"
                        "open import Substrate.Foundation.Have\n"
                        "f = Substrate.Foundation.Bool.Not\n")
    check("⚑ Ⓠ8ᵃ: a DOTTED module path is not reported as a missing name",
          any("." in n for _p, n in unresolved(
              dot, {**idx, "Substrate.Foundation.Bool.Not": {"Substrate.WT.B3"}})),
          False)
    check("⚑ the file's OWN declaration is not reported (self-import is cyclic)",
          "mine" in got, False)
    check("a name the file ALREADY imports is not reported",
          "already" in got, False)

    # ── Ⓜ5 stripped_aliases ─────────────────────────────────────────────
    # ⚑ THE CLASS FOUR MODES REPORTED AS SOMETHING ELSE. A `⟦hash⟧` name is a
    # dedup `renaming` TARGET whose clause the ban sweep deleted; it never had a
    # definition, so `agda_defs` says "no definer" (reads as MISSING MATH),
    # `--collide` says "0 providers" (same), `--unresolved` is correctly SILENT
    # (keep-biased: no known definer, no guess), and `--orphans` prints it under
    # a banner saying that mode does not work. Found by hand, four times.
    al = _write("Alias",
                "module Substrate.T.Alias where\n"
                "open import Substrate.Foundation.Have\n"
                "PIdx = Tm⟦27e68fcc⟧ × Tm⟦27e68fcc⟧\n"
                "step : x ⇒⟦66d2c034⟧ y\n")
    algot = {n for _p, n in stripped_aliases(al)}
    check("⚑ Ⓜ5: a stripped dedup alias IS reported",
          algot, {"Tm⟦27e68fcc⟧", "⇒⟦66d2c034⟧"})
    # ⚑ AND `--unresolved` CANNOT SEE IT — not a defect there, but the reason
    # this mode has to exist rather than being a filter on that one.
    check("...where --unresolved is silent (no definer ⇒ no guess)",
          {n for _p, n in unresolved(al, idx)} & algot, set())
    # ⚑ THE HASH SHAPE IS THE DISCRIMINATOR. `--orphans` failed precisely because
    # it could not separate a dropped alias from a qualified name or a binder;
    # `⟦8-hex⟧` is minted by one tool for one purpose and wears no other hat.
    nb = _write("NoAlias",
                "module Substrate.T.NoAlias where\n"
                "open import Substrate.Foundation.Have\n"
                "f = ⟦ x ⟧\n"          # the real semantic-bracket operator
                "g = S₃.Carrier\n"       # a qualified name --orphans over-reported
                "h : (a₂ : Set) → Set\n")
    check("⚑ the ⟦_⟧ semantic bracket is NOT an alias",
          stripped_aliases(nb), [])
    # ⚑ REPORT PRESENCE, NEVER ABSENCE: a file citing none returns [], which is
    # "none found by this shape", not "this file is clean".
    check("a file citing no alias returns an empty list",
          stripped_aliases(_write("Plain", "module Substrate.T.Plain where\n"
                                           "f = g\n")), [])
    # ⚑ A COMMENTED alias is not a citation — the archaeology notes written into
    # the repaired files QUOTE these names, and counting those would make every
    # fix look like it left the debt behind.
    # ⚑⚑⚑ THE FALSE POSITIVE THAT COST NINE HEALTHY FILES A REPAIR ATTEMPT.
    # The predicate reported every `⟦hash⟧` CITATION while the mode is named
    # STRIPPED. MEASURED on `X8aSkiExistence.agda:32` — its `renaming (Step to
    # Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)` clause is INTACT, the file compiles at
    # exit 0, and the "repair" BROKE it by collapsing two gate-mandated pins to
    # bare names that collide (4 and 12 index nodes). An alias its own file still
    # binds is the construct `check_import_shape` REQUIRES, not debt.
    _bound = _write("Bound",
                    "module Substrate.T.Bound where\n"
                    "open import Substrate.FUSep.FUSepQReduce using (stop)\n"
                    "  renaming (Step to Step⟦c0e06c56⟧; Tm to Tm⟦533ef80d⟧)\n"
                    "f : Step⟦c0e06c56⟧ → Tm⟦533ef80d⟧\n")
    check("⚑⚑⚑ an alias its OWN file still binds is NOT reported as stripped",
          stripped_aliases(_bound), [])
    # ⚑ AND ONE BOUND ALIAS DOES NOT EXCUSE AN UNBOUND SIBLING — the test is per
    # alias, not per file, or a file with one live clause would hide the rest.
    _half = _write("Half",
                   "module Substrate.T.Half where\n"
                   "open import M using (stop) renaming (Step to Step⟦c0e06c56⟧)\n"
                   "f : Step⟦c0e06c56⟧ → Tm⟦533ef80d⟧\n")
    check("⚑ a BOUND alias beside an UNBOUND one reports only the unbound",
          [n for _p, n in stripped_aliases(_half)], ["Tm⟦533ef80d⟧"])
    # ⚑ A PROJECTION CITES ITS PREFIX'S BINDING: `Wedge⟦…⟧.quot` is bound when
    # `Wedge⟦…⟧` is, or the prefix's clause would look irrelevant to the suffix.
    _proj = _write("Proj",
                   "module Substrate.T.Proj where\n"
                   "open import M renaming (Wedge to Wedge⟦478f66a6⟧)\n"
                   "q = Wedge⟦478f66a6⟧.quot\n")
    check("⚑ a projection is bound when its PREFIX is bound",
          stripped_aliases(_proj), [])
    check("⚑ an alias named only in a COMMENT is not a citation",
          stripped_aliases(_write("Cmt", "module Substrate.T.Cmt where\n"
                                         "-- was Tm⟦27e68fcc⟧ before the sweep\n"
                                         "f = g\n")), [])

    # ── Ⓜ5ᵇ repair_alias (dry: no write, no compile) ────────────────────
    def _rw(body, alias, mod, bare):
        return repair_alias(_write("RW", body), alias, mod, bare)

    check("⚑ Ⓜ5ᵇ: the alias is rewritten to its bare name",
          _rw("module Substrate.T.RW where\nPIdx = Tm⟦27e68fcc⟧ × Tm⟦27e68fcc⟧\n",
              "Tm⟦27e68fcc⟧", "Substrate.FUSep.FUSepQSKI", "Tm"),
          ("rewrote", "2 site(s) -> Tm, bound at Substrate.FUSep.FUSepQSKI"))
    # ⚑⚑ THE TWO-`Wedge` CASE — why the write is keyed on the CENSUS, not on a
    # substitution table. Both aliases spell out as `Wedge`; only the hash says
    # which module. A uniform sweep points 8 GCD files at the wrong one, and it
    # would likely typecheck somewhere before failing far away.
    check("⚑⚑ two aliases with the SAME bare name keep DIFFERENT homes",
          (_rw("module Substrate.T.RW where\nf : Wedge⟦478f66a6⟧\n",
               "Wedge⟦478f66a6⟧", "Substrate.Algebra.Wedge", "Wedge")[1],
           _rw("module Substrate.T.RW where\nf : Wedge⟦b7e6a995⟧\n",
               "Wedge⟦b7e6a995⟧", "Substrate.Algebra.Nat.GCD.Wedge", "Wedge")[1]),
          ("1 site(s) -> Wedge, bound at Substrate.Algebra.Wedge",
           "1 site(s) -> Wedge, bound at Substrate.Algebra.Nat.GCD.Wedge"))
    # ⚑ MIXFIX ARITY IS PRESERVED. `_⇒⟦…⟧_` is the DECLARATION form; rewriting
    # it to the bare `⇒` (or the reverse) is a parse error or a changed fixity.
    check("⚑ the underscored DECLARATION form maps to the underscored bare name",
          _rw("module Substrate.T.RW where\ndata _⇒⟦66d2c034⟧_ : Set where\n",
              "_⇒⟦66d2c034⟧_", "Substrate.Algebra.R.Trace.SKIReductionToList",
              "_⇒_")[1], "1 site(s) -> _⇒_, bound at Substrate.Algebra.R.Trace.SKIReductionToList")
    check("...and the BARE use form maps to the bare name",
          _rw("module Substrate.T.RW where\nstep : x ⇒⟦66d2c034⟧ y\n",
              "⇒⟦66d2c034⟧", "Substrate.Algebra.R.Trace.SKIReductionToList",
              "_⇒_")[1], "1 site(s) -> ⇒, bound at Substrate.Algebra.R.Trace.SKIReductionToList")
    # ⚑ A COMMENT-ONLY CITATION IS A NO-OP, not a rewrite. The repaired files in
    # this arc QUOTE the alias they removed; corrupting that destroys the
    # archaeology that explains the fix.
    check("⚑ a comment-only citation is a no-op, not a rewrite",
          _rw("module Substrate.T.RW where\n-- was Tm⟦27e68fcc⟧ before\nf = g\n",
              "Tm⟦27e68fcc⟧", "Substrate.FUSep.FUSepQSKI", "Tm")[0], "no-op")
    # ⚑ AND A MIXED FILE REWRITES ONLY THE CODE SITE.
    _mx = _write("Mix", "module Substrate.T.Mix where\n"
                        "-- was Tm⟦27e68fcc⟧ before the sweep\n"
                        "f : Tm⟦27e68fcc⟧\n")
    repair_alias(_mx, "Tm⟦27e68fcc⟧", "Substrate.FUSep.FUSepQSKI", "Tm")
    check("⚑ a mixed file reports ONE site (the code one), leaving the note",
          repair_alias(_mx, "Tm⟦27e68fcc⟧", "Substrate.FUSep.FUSepQSKI", "Tm")[1],
          "1 site(s) -> Tm, bound at Substrate.FUSep.FUSepQSKI")
    # ⚑ A QUALIFIED SUFFIX IS PART OF THE TOKEN. `Wedge⟦…⟧.quot` is a projection
    # THROUGH the alias; the prefix is rewritten and `.quot` survives.
    # ⚑⚑ THE DAG DEFECT, PINNED. An alias sweep repairs a DEPENDENCY GRAPH: until
    # the roots are done, a correctly-repaired leaf still fails to compile — on
    # SOMEONE ELSE's error. My first cut reverted on any non-zero exit, which
    # refuses every file in dependency order and makes the sweep unable to start.
    # MEASURED on `ExtrudeSKISetoid`: both aliases rewritten correctly, both
    # reverted, because `DiagonalLawvereSKI:41` (upstream) still cited one.
    # `split_pipeline.blame` is the authority; this asserts we consult it.
    _dep = ("/home/mikemol/github/substrate/agda/Substrate/Other/Up.agda"
            ":41.51-62: error: [NotInScope]")
    _sp_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _sp_dir)
    from split_pipeline import blame as _blame_t
    check("⚑⚑ an upstream failure is NOT this file's fault (blame consulted)",
          _blame_t("Substrate/Category/UniversalProperty/ExtrudeSKISetoid.agda",
                   _dep)[0], "dependency")
    check("...while an error citing the file ITSELF is its own",
          _blame_t("Substrate/Other/Up.agda", _dep)[0], "own")

    # ── Ⓜ5ᶜ alias_candidates ────────────────────────────────────────────
    # ⚑ TWO OF THE SIX "MISSING REF" ALIASES WERE MATCHING DEFECTS, NOT MISSING
    # REFS — and widening the ref list would not have found either.
    # ⚑ MEASURED at `771283c8^:DiagonalLawvereSKI.agda:25`: the clause declares
    # `renaming (_⇒_ to _⇒⟦66d2c034⟧_)` while :41 uses the bare `⇒⟦66d2c034⟧`.
    # A literal search on the use-site token reported "no home" for an alias
    # whose underscored sibling resolved from the SAME line.
    check("⚑ Ⓜ5ᶜ: a BARE use-site form also probes its underscored declaration",
          "_⇒⟦66d2c034⟧_" in alias_candidates("⇒⟦66d2c034⟧"), True)
    check("...and the underscored form probes the bare one",
          "⇒⟦66d2c034⟧" in alias_candidates("_⇒⟦66d2c034⟧_"), True)
    # ⚑ AND A PROJECTION IS NOT A NAME. `Wedge⟦…⟧.quot` is a record projection
    # THROUGH the alias (`Factoradic.agda:67`); no clause ever names it, so a
    # search for one is guaranteed to miss. Resolve the PREFIX.
    check("⚑ Ⓜ5ᶜ: a projection resolves through its alias PREFIX",
          alias_candidates("Wedge⟦478f66a6⟧.quot")[0], "Wedge⟦478f66a6⟧")
    check("...and a plain alias is unchanged by the projection strip",
          alias_candidates("Tm⟦27e68fcc⟧")[0], "Tm⟦27e68fcc⟧")
    # ⚑ THE REF LIST IS ORDERED NEWEST-FIRST and includes the DEDUP commits that
    # minted these aliases — a clause rewritten or moved before the ban sweep is
    # invisible at `771283c8^` alone.
    check("⚑ the pre-ban ref is tried FIRST, then the minting commits",
          ALIAS_REFS[0], "771283c8^")
    # ── Ⓜ5ᵈ alias_refs_for ──────────────────────────────────────────────
    # ⚑⚑ A GLOBAL REF LIST IS A GUESS ABOUT WHEN THE CLAUSE DIED, and for three
    # aliases it was wrong. `S5Regress.agda` has ONE commit — `c3d18a33`, a
    # migration — and its clause is at :34 there. The file did not EXIST at
    # `771283c8^`, so all four global refs searched a tree without it. "No home
    # in 4 refs" was a fact about MY REF LIST, exactly as the message said.
    _refs = alias_refs_for(os.path.join(AG, "Substrate/S5/S5Regress.agda"))
    check("⚑⚑ Ⓜ5ᵈ: a file's OWN commits are searched, not just the global refs",
          len(_refs) > len(ALIAS_REFS), True)
    check("...with the cheap global refs still tried FIRST",
          _refs[:len(ALIAS_REFS)], list(ALIAS_REFS))
    # ⚑ AND A FILE WITH NO HISTORY DEGRADES TO THE GLOBAL LIST, never to empty —
    # an empty ref list would make every alias unresolvable and read as "no home".
    # ⚑ Ⓜ5ᵉ② WIDENED THIS: HEAD is now always tried, because an uncommitted
    # parent clause is reachable from no commit list at all (the `Step` case).
    # A path with no history still degrades to the GLOBAL refs — never to empty,
    # which would make every alias unresolvable and read as "no home".
    check("⚑ a path with no git history falls back to the global refs + HEAD",
          alias_refs_for("/nonexistent/Nope.agda"), list(ALIAS_REFS) + ["HEAD"])
    # ⚑ `alias_home` MUST ACCEPT A LIST, not only a single ref — the one-off
    # string form is still used for probes.
    check("⚑ a single-ref string is still accepted",
          alias_home("Tm⟦27e68fcc⟧", "771283c8^"),
          ("Substrate.FUSep.FUSepQSKI", "Tm"))
    # ⚑⚑ THE SECOND CLAUSE FORM, AND THE REASON THIS SYMBOL RAN TWICE. A clause
    # may bind its module on a DIFFERENT LINE:
    #     import Substrate.S5.S5Verdict as S5Verdict
    #     open S5Verdict … renaming (Progress to Progress⟦cbe99ef5⟧)
    # so the `open` names only the local alias. MEASURED at
    # `c3d18a33:S5Regress.agda:33-34`. Three aliases read "no home" while their
    # clauses sat in a searched ref — a MATCHING defect wearing a missing-ref
    # costume, which I diagnosed as the latter after confirming one BY HAND.
    check("⚑⚑ Ⓜ5ᵈ: `import M as Q` + `open Q … renaming` resolves to M",
          alias_home("Progress⟦cbe99ef5⟧", "c3d18a33"),
          ("Substrate.S5.S5Verdict", "Progress"))
    # ── Ⓜ5ᵉ clause_forms ────────────────────────────────────────────────
    # ⚑⚑ THE SURVEY THAT REPLACES DISCOVERY-BY-HAND. Two forms were found by
    # accident in this arc, each AFTER a wrong diagnosis shipped. MEASURED at
    # `771283c8^`: THREE forms over 440 clauses —
    #     open-import  416   `open import M … renaming (…)`
    #     open-bare     22   `open <expr> … renaming (…)` — INCLUDING APPLIED
    #                        modules (`open ModExpand.Over F₂-CommRing 7 m-lo …`)
    #     open-alias     2   `import M as Q` … `open Q … renaming (…)`
    # ⚑ SO `open-alias` — the form whose absence cost Ⓜ5ᵈ a wrong fix — is the
    # RAREST at 2 clauses, and `open-bare` at 22 is TEN TIMES more common while
    # being the one my matcher still handles wrong. Frequency and my attention
    # were inversely correlated, which is exactly what a survey corrects.
    _cf = clause_forms()
    check("⚑ Ⓜ5ᵉ: the census finds the dominant `open import` form",
          len(_cf.get("open-import", [])) > 100, True)
    check("⚑ …and the rare `open-alias` form that cost Ⓜ5ᵈ a wrong diagnosis",
          len(_cf.get("open-alias", [])) >= 2, True)
    # ⚑ AN APPLIED MODULE IS A THIRD SHAPE, and it is NOT `import M as Q`:
    # `open ModExpand.Over F₂-CommRing 7 m-lo renaming (hsum to hsum-g)` names a
    # module APPLICATION, so there is no `as` binding to resolve through.
    check("⚑ …and `open-bare`, which includes APPLIED modules",
          len(_cf.get("open-bare", [])) >= 10, True)
    # ⚑ REPORT PRESENCE: an unseen form is 'none at this ref', never 'no such form'.
    check("⚑ every censused form carries witnesses (path, line, text)",
          all(len(r) == 3 for rows in _cf.values() for r in rows), True)
    # ── Ⓜ5ᵉ② parent-ref derivation ──────────────────────────────────────
    # ⚑⚑ A SPLIT LEAF INHERITS ITS PARENT'S CLAUSES BUT NOT ITS HISTORY.
    # MEASURED: `Step⟦f8c709b4⟧`'s clause is at HEAD in the pre-split PARENT
    # `ExtrudeCoEmitViaTrace.agda:19`, while the citing files are its leaves. So
    # `git log -- <leaf>` can never reach it — the ref list was never short, it
    # was searching the wrong FILE.
    _lr = alias_refs_for(os.path.join(
        AG, "Substrate/Category/UniversalProperty/ExtrudeCoEmitViaTrace/Code.agda"))
    check("⚑⚑ Ⓜ5ᵉ②: a leaf's refs include HEAD (an uncommitted parent clause)",
          "HEAD" in _lr, True)
    check("...and the PARENT's commits, which the leaf's own history omits",
          len(_lr) > len(ALIAS_REFS) + 1, True)
    # ── Ⓜ5ᵉ③ uncommitted-mint verdict ───────────────────────────────────
    # ⚑ "NO HOME IN THE REFS" AND "NEVER COMMITTED" ARE DIFFERENT FINDINGS, and
    # their next actions are opposite. `Tm⟦27e68fcc⟧` is committed (its clause is
    # recoverable); a name no ref ever mentioned is not reachable by any widening.
    # ⚑⚑ THE FOURTH SHAPE, AND IT IS A `pat_a` BUG NOT A NEW FORM. An APPLIED
    # `open import M ℕ` whose `renaming` continues on the NEXT line:
    #     open import …ExtrudeCoEmitMonad ℕ
    #       using (…) renaming (Step to Step⟦f8c709b4⟧)
    # `pat_a`'s `[^\n]*?` could not cross the newline — the SAME bound I had
    # already diagnosed and fixed in `pat_b`, left standing one pattern away.
    # The census classified the row `open-import` CORRECTLY; the matcher was wrong.
    check("⚑⚑ Ⓜ5ᵉ: an APPLIED multi-line `open import … renaming` resolves",
          alias_home("Step⟦f8c709b4⟧", "HEAD"),
          ("Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad", "Step"))
    # ── Ⓜ5ᶠ the collision index is THE authority for a hash's home ───────
    # ⚑⚑ MY OWN VERDICT WAS FALSIFIED BY IT. `Terminal⟦ac030497⟧` reported
    # "MINTED IN THE WORKING TREE — no committed ref mentions this alias" because
    # no `renaming` CLAUSE was found. It is row :64 of
    # `scratch/sppf_collision_index.md` — `ShadowArchitecture.Raven.Grammar` —
    # and `agda_defs --provides` confirms that module exports `Terminal`. The
    # hash is MINTED by `_agdatext.shape_decls` and PUBLISHED by
    # `sppf_node_index.py`; a consumer's clause is a CITATION of the row, never
    # its source. Third time this arc I asked the wrong oracle.
    # ⚑ THIS CASE USED `Terminal⟦ac030497⟧` AND WENT STALE BY ITS OWN SUCCESS:
    # `rename_at_source … Terminal Terminal-Raven` retired that collision, so the
    # index row is GONE (11 names → 10). It was then repointed to `Step⟦c0e06c56⟧`
    # with the note *"when THAT one is paid down, repoint again"*.
    #
    # ⚑⚑ AND IT AGED AGAIN, EXACTLY AS PREDICTED, AND THE PREDICTION IS THE DEFECT.
    # MEASURED 2026-08-24 at 55/56: `c0e06c56` has ZERO rows today (the index was
    # regenerated — `FUSepQReduce`/`Step` is now `dd7bab21`), so the case failed
    # against a resolver that is working correctly. A case that must be hand-repointed
    # every time the tree moves is a case that reports TREE MOTION as a code defect,
    # and the instruction "repoint again" schedules the same false alarm forever.
    #
    # ⚑ SO THE HASH IS DERIVED FROM THE INDEX, NOT PINNED TO IT. The claim worth
    # pinning was never "this particular hash lives here" — it is that the resolver
    # RESOLVES A UNIQUELY-HOMED HASH TO ITS MODULE. Reading one such hash out of the
    # live index and asserting the round-trip tests exactly that, and survives every
    # regeneration. ⚑ The population is asserted NON-EMPTY first, or an index that
    # lost all its rows would make this case vacuously green — the `0/0` shape.
    _uniq = {}
    _nm = None
    for _ln in open(SPPF_INDEX, encoding="utf-8").read().split("\n"):
        _m1 = _IDX_NAME.match(_ln)
        if _m1:
            _nm = _m1.group(1)
            continue
        _m2 = _IDX_ROW.match(_ln)
        if _m2 and _nm:
            _uniq.setdefault(_m2.group(1), []).append((_m2.group(2), _nm))
    _solo = sorted(h for h, rs in _uniq.items() if len(rs) == 1)
    check("the collision index HAS uniquely-homed hashes to resolve "
          "(else the case below is vacuous)", bool(_solo), True)
    if _solo:
        _h = _solo[0]
        check("...and the resolver returns that row's (module, bare)",
              alias_home_from_index("X⟦%s⟧" % _h), _uniq[_h][0])
    # ⚑ A STALE HASH IS ABSENT FROM THE CURRENT INDEX and still names something
    # real — the declaration's fields changed, so it rehashed. Today's Wedge
    # shapes are ⟦3014fd3e⟧ / ⟦9e8d371e⟧, so the git route stays load-bearing.
    check("⚑ a STALE hash misses the index (git remains the fallback)",
          alias_home_from_index("Wedge⟦478f66a6⟧"), None)
    check("a non-alias name is not resolved by the index",
          alias_home_from_index("Tm"), None)
    # ⚑⚑ THE REFUSAL THAT MATTERS: a hash is of the SHAPE, so many modules share
    # one. `Tm⟦533ef80d⟧` has SEVEN index rows (:11-:20). Taking the first gave
    # `NewmanKI` where the pre-ban clause says `SKIShedDuality` — a WRONG HOME
    # that compiles somewhere and fails far away. The index disambiguates a NAME
    # BY SHAPE; it cannot say which of seven same-shaped modules a consumer
    # meant. Only the clause can, so refuse and let git answer.
    check("⚑⚑ Ⓜ5ᶠ: a MULTI-ROW hash is REFUSED, not guessed",
          alias_home_from_index("Tm⟦533ef80d⟧"), None)
    check("⚑ Ⓜ5ᵉ③: a committed alias reports as present in git",
          alias_in_git("Tm⟦27e68fcc⟧"), True)
    check("...and an invented one does not",
          alias_in_git("Nope⟦deadbeef⟧"), False)
    # ⚑ "ALREADY PRESENT" IS SUCCESS, NOT REFUSAL. `agda_imports.add_import`
    # returns `(False, "present")` when the import is already there — the same
    # False it returns for `self-import refused` and `no module header`, which
    # ARE failures. Reading the bool alone reported `refused` on 6 files whose
    # rewrite HAD landed (verified: `Algebra/Wedge/Compose.agda` cites zero
    # aliases afterwards). A census that misreports its own writes is worse than
    # one that reports nothing.
    # ── Ⓜ6 repair_file / topo_key ───────────────────────────────────────
    # ⚑⚑ THE UNIT IS THE FILE. A file citing TWO aliases cannot typecheck until
    # BOTH are rewritten, so a per-alias loop reverts each for the other's error
    # and NEVER CONVERGES. MEASURED on the Ⓜ5ᶜ run: `DiagonalLawvereSKI.agda`
    # was [rewrote] for `⇒⟦66d2c034⟧` and [refused … REVERTED] for
    # `Tm⟦533ef80d⟧` — same file, same run, one undoing the other.
    _two = _write("Two", "module Substrate.T.Two where\n"
                         "f : Tm⟦27e68fcc⟧ → Wedge⟦478f66a6⟧\n")
    check("⚑⚑ Ⓜ6: a file citing TWO aliases is repaired as ONE unit",
          repair_file(_two, {"Tm⟦27e68fcc⟧": ("Substrate.FUSep.FUSepQSKI", "Tm"),
                             "Wedge⟦478f66a6⟧": ("Substrate.Algebra.Wedge",
                                                 "Wedge")})[1],
          "2 alias(es), 2 rewritable")
    # ⚑ AN ALIAS WITH NO KNOWN HOME BLOCKS THE FILE, deliberately. Repairing its
    # siblings and reporting success would be a green over a file that still
    # cannot compile — the census-green shape.
    check("⚑ one unknown home BLOCKS the file rather than half-repairing it",
          repair_file(_two, {"Tm⟦27e68fcc⟧":
                             ("Substrate.FUSep.FUSepQSKI", "Tm")})[0], "blocked")
    check("...and names the alias it could not place",
          "Wedge⟦478f66a6⟧" in repair_file(
              _two, {"Tm⟦27e68fcc⟧": ("Substrate.FUSep.FUSepQSKI", "Tm")})[1], True)
    check("a file citing no alias is a no-op",
          repair_file(_write("None2", "module Substrate.T.None2 where\nf = g\n"),
                      {})[0], "no-op")
    # ⚑ THE ORDER COMES FROM THE BUILD'S OWN DAG, never a local sort:
    # `gen_build_makefiles.parse_tree` + `kahn_depth` (roots first, whole-tree).
    # A target is safe when its TRANSITIVE deps have settled, not merely the
    # targets among them — so ranking the 91 against each other is not enough.
    _tk = topo_key(["Substrate/Foundation/Eq.agda",
                    "Substrate/Algebra/Polynomial/Graded/Defs.agda"])
    check("⚑ Ⓜ6: a Foundation root outranks a deep Algebra module",
          _tk.get("Substrate/Foundation/Eq.agda", 1 << 30)
          < _tk.get("Substrate/Algebra/Polynomial/Graded/Defs.agda", 1 << 30), True)
    # ⚑ AND AN UNRANKED PATH SORTS LAST, never silently drops — keep-biased, the
    # same direction every predicate in this file takes.
    check("⚑ an unknown path still gets a rank (sorts last, is not dropped)",
          "not/a/module.agda" in topo_key(["not/a/module.agda"]), True)

    check("⚑ the shared writer's 'present' is a SUCCESS string, not a failure",
          _add_import(_write("Present",
                             "module Substrate.T.Present where\n"
                             "open import Substrate.Foundation.Have\n"),
                      "Substrate.Foundation.Have"),
          (False, "present"))

    check("⚑ a projection through the alias keeps its suffix",
          _rw("module Substrate.T.RW where\nq = Wedge⟦478f66a6⟧.quot\n",
              "Wedge⟦478f66a6⟧", "Substrate.Algebra.Wedge", "Wedge")[1],
          "1 site(s) -> Wedge, bound at Substrate.Algebra.Wedge")
    # ⚑ THE FLOOR: an unknown name is SILENT, never reported as missing. It may be
    # a local binding, a stdlib name, or a pattern variable — and reporting those
    # would bury the real finding. So a clean result means "nothing I can SEE".
    check("⚑ a name with NO known definer is SILENT, not reported",
          any(n == "mystery" for _p, n in unresolved(
              _write("Unknown", "module Substrate.T.Unknown where\n"
                                "x = mystery\n"), idx)), False)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n_, g, got_, want in cases:
        if not g:
            print(f"  FAIL {n_}\n       got {got_!r} want {want!r}")
    print(f"fix_notinscope selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    # ⚑ Ⓜ5ᵉ — BEFORE the positional check: this mode's argument is OPTIONAL (it
    # defaults to the pre-ban ref), so requiring one would refuse the common call.
    if "--clause-forms" in sys.argv:
        _r = next((a for a in sys.argv[1:]
                   if not a.startswith("--") and a != "--clause-forms"), None)
        _forms = clause_forms(_r) if _r else clause_forms()
        _tot = sum(len(v) for v in _forms.values())
        for _f in sorted(_forms, key=lambda k: -len(_forms[k])):
            print(f"{_f}   {len(_forms[_f])} clause(s)")
            for _rel, _ln, _t in _forms[_f][:6]:
                print(f"     {_rel}:{_ln}  {_t}")
            if len(_forms[_f]) > 6:
                print(f"     … and {len(_forms[_f]) - 6} more")
        print(f"{len(_forms)} form(s) over {_tot} clause(s) at "
              f"{_r or ALIAS_REFS[0]} — PRESENCE with witnesses; a form with no "
              f"rows is 'none at this ref', not 'no such form'.")
        sys.exit(0)
    log = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    apply = "--apply" in sys.argv
    if not log:
        print(__doc__)
        print("usage: fix_notinscope.py <build.log> [--apply]")
        print("       fix_notinscope.py --unresolved <file|dir>   # STATIC, no build")
        print("       fix_notinscope.py --clause-forms [<ref>]")
        print("                                    # Ⓜ5ᵉ — every `renaming` clause")
        print("                                    # shape at a ref, so the matcher is")
        print("                                    # checked against a SURVEY, not")
        print("                                    # against whichever file is in hand.")
        print("       fix_notinscope.py --aliases <file|dir> [--homes]")
        print("                                    # Ⓜ5 — stripped dedup `⟦hash⟧`")
        print("                                    # aliases, which every other mode")
        print("                                    # reports as a MISSING DEFINITION.")
        print("                                    # --homes recovers each alias's")
        print("                                    # `renaming` source from pre-ban git.")
        # ⚑⚑ Ⓜ11 / ⟡mode-consolidation — TWO MODES THAT DISPATCHED AND WERE NEVER
        # NAMED HERE, so `check_divergence_ratchet` carried them as UNDOCUMENTED
        # (agda-F2, agda-F2b). Both are the SIZING form of a mode whose per-row
        # output is too large to read, which is exactly the case an operator reaches
        # for first on a tree-wide run — and it was the one form the usage did not
        # mention. Documented from their dispatch sites, not from memory:
        print("       fix_notinscope.py --unresolved <file|dir> --summary")
        print("                                    # a MODIFIER on --unresolved, not a")
        print("                                    # mode: the per-row form printed 668 KB")
        print("                                    # over the tree and cannot size a")
        print("                                    # population. Splits names into 1-HOME")
        print("                                    # (mechanically repairable) vs AMBIGUOUS")
        print("                                    # (the use site's type decides).")
        print("       fix_notinscope.py <build.log> --classify")
        print("                                    # the DIAGNOSIS without the write path,")
        print("                                    # so a witness can consume it read-only.")
        print("                                    # Groups every site by verdict:")
        print("                                    # resolvable / ambiguous / no-definer.")
        sys.exit(2)
    # ⚑ Ⓜ5 — THE STRIPPED-ALIAS CENSUS. A `⟦hash⟧` name never had a definition:
    # it is a dedup `renaming` target whose clause the ban sweep deleted. So
    # `agda_defs` says "no definer" (reads as MISSING MATH, the Ⓑ6ᵇ class),
    # `--unresolved` is correctly silent, and `--orphans` prints it under a
    # banner saying that mode does not work. Found by hand four times before this.
    if "--aliases" in sys.argv:
        _paths = (agda_lex.agda_files(log) if os.path.isdir(log) else [log])
        _rows = [r for p in _paths for r in stripped_aliases(p)]
        _by = {}
        for _p, _nm in _rows:
            _by.setdefault(_nm, []).append(_p)
        _write_it = "--apply" in sys.argv
        _homes_map = {}
        # ⚑ Ⓜ5ᵇ — THE WRITE NEEDS THE HOME, so `--apply` implies `--homes`.
        # Without it there is nothing to bind and the rewrite would strip the
        # one piece of information that says WHICH module (the two-`Wedge` case).
        for _nm in sorted(_by, key=lambda k: -len(_by[k])):
            # ⚑ Ⓜ5ᵈ — RESOLVE AGAINST A CITING FILE'S OWN HISTORY, not just the
            # global refs. A clause that died at a MIGRATION (not at the ban
            # sweep) exists only in commits touching that file, so the global
            # list searches trees the file was never in. Try each citing file in
            # turn: the first that yields a clause settles the alias, since the
            # hash IS the identity — one hash, one source declaration.
            _home = None
            if "--homes" in sys.argv or _write_it:
                # ⚑⚑ THE INDEX FIRST — it is the AUTHORITY for what a hash names
                # (`sppf_node_index.py` publishes what `_agdatext.shape_decls`
                # mints). A consumer's `renaming` clause is a CITATION of that
                # row. Asking git first answered "did someone once cite it" and
                # wrongly reported `Terminal⟦ac030497⟧` as never-committed.
                _home = alias_home_from_index(_nm)
                # ⚑ GIT IS THE FALLBACK FOR A STALE HASH — an alias whose
                # declaration changed shape is absent from the CURRENT index
                # while still naming something real (`Wedge⟦478f66a6⟧`).
                if not _home:
                    for _cand_p in sorted(_by[_nm]):
                        _home = alias_home(
                            _nm, alias_refs_for(os.path.join(AG, _cand_p)))
                        if _home:
                            break
            # ⚑ Ⓜ5ᵉ③ — SAY WHICH KIND OF MISS. "No clause in the searched refs"
            # and "never committed at all" need opposite next actions: search
            # harder, vs. decide what the name should have been. Collapsing them
            # is true and useless.
            if _home:
                _h = f"  -> was `{_home[1]}` from {_home[0]}"
            elif "--homes" in sys.argv or _write_it:
                _h = ("  -> ⚑ MINTED IN THE WORKING TREE — no committed ref "
                      "mentions this alias at all; widening the search cannot "
                      "help" if not alias_in_git(_nm) else
                      "  -> no `renaming` clause in the searched refs (a fact "
                      "about the REFS, not proof it was never bound)")
            else:
                _h = ""
            print(f"{_nm}   {len(_by[_nm])} file(s){_h}")
            # ⚑ ONLY RECOVERED HOMES ENTER THE MAP. `repair_file` treats an
            # absent key as "no home" and BLOCKS the whole file, which is right:
            # repairing an alias's siblings while it still has citations would
            # report success over a file that still cannot compile.
            if _home is not None:
                _homes_map[_nm] = _home
            if not _write_it:
                for _p in sorted(_by[_nm])[:8]:
                    print(f"     {_p}")
                if len(_by[_nm]) > 8:
                    print(f"     … and {len(_by[_nm]) - 8} more")
                continue
            # ⚑ REFUSE-ON-UNKNOWN-HOME, the discipline this whole toolchain runs
            # on. Rewriting without a recovered clause means GUESSING the module,
            # and a wrong home is a name that resolves somewhere else entirely.
            if _home is None:
                print(f"     (no home recovered — files citing this alias are "
                      f"blocked below; widen the ref, do not guess)")
        _files = {p for _ps in _by.values() for p in _ps}
        if _write_it:
            # ⚑⚑ Ⓜ6 — FILE-MAJOR, IN DEPENDENCY ORDER. Two defects in one fix:
            #   (a) the UNIT is the file. A file citing two aliases cannot
            #       typecheck until BOTH are rewritten, so a per-alias loop
            #       reverted each for the other's error and never converged —
            #       MEASURED on `DiagonalLawvereSKI.agda`, [rewrote] for one
            #       alias and [refused … REVERTED] for another in ONE run.
            #   (b) the ORDER is topological. Repairing a leaf whose upstream is
            #       still broken yields `rewrote-blocked` and a second pass;
            #       roots-first converges in one.
            _rank = topo_key(_files)
            print(f"\n-- repairing {len(_files)} file(s), roots first "
                  f"({'ranked' if _rank else 'UNRANKED: no DAG available'}) --")
            for _p in sorted(_files, key=lambda q: (_rank.get(q, 1 << 30), q)):
                _v, _d = repair_file(os.path.join(AG, _p), _homes_map, apply=True)
                print(f"  [{_v}] {_p}  {_d}")
        print(f"{len(_by)} stripped alias(es) over {len(_files)} file(s) — "
              f"PRESENCE with witnesses; a file citing none is not thereby clean.")
        sys.exit(0)
    # ⚑ Ⓒ6 — THE STATIC INPUT. A log names ONE missing import per file (scope
    # checking halts at the first failure); this reads the tree and names them all.
    # The dispatch branch is the half that gets forgotten — `rewire_only` was
    # written, documented, and left with ZERO callers because nobody added it.
    if "--unresolved" in sys.argv:
        _idx = agda_defs.def_index()
        _paths = (agda_lex.agda_files(log) if os.path.isdir(log) else [log])
        # ⚑⚑ KEY THE WRITE PATH ON THE REAL PATH, NOT THE REPORTED ONE. `unresolved()`
        # returns a DISPLAY-relative path (`Substrate/S5/S5Carrier.agda`) while the file
        # on disk is `agda/Substrate/...` — the report never opened it again, so the
        # difference was invisible until `--apply` tried and got FileNotFoundError. A
        # display string reused as a handle is the same two-spellings shape as
        # `census-keyed-on-one-spelling`: fine for printing, wrong for acting.
        _rows, _real = [], {}
        for _p in _paths:
            for _dp, _nm in unresolved(_p, _idx):
                _rows.append((_dp, _nm))
                _real[_dp] = _p
        _by = {}
        for _p, _nm in _rows:
            _by.setdefault(_p, []).append(_nm)
        # ⚑ --summary FOR THE THIRD TIME IN THIS TOOL FAMILY, and the third time
        # the per-row form was written first and measured too large: this printed
        # 668 KB over the tree. A census that can ONLY print per-row cannot size a
        # population — which is the one question a tree-wide run is asked. The
        # per-row listing stays for the file being repaired.
        if "--summary" in sys.argv:
            import collections as _c
            _one = _c.Counter()      # 1 home  — mechanically repairable
            _amb = _c.Counter()      # N homes — needs the use site's type
            for _p, _nm in _rows:
                _n = len({m for m in _idx.get(_nm, ()) if m})
                (_one if _n == 1 else _amb)[_nm] += 1
            print("=== 1 HOME — mechanically repairable (the name has ONE definer) ===")
            for _nm, _c2 in _one.most_common(25):
                _h = sorted({m for m in _idx.get(_nm, ()) if m})[0]
                print(f"  {_c2:4d}  {_nm:<24} -> {_h}")
            if len(_one) > 25:
                print(f"       … and {len(_one) - 25} more name(s)")
            print("\n=== AMBIGUOUS — several definers; the use site's TYPE decides ===")
            for _nm, _c2 in _amb.most_common(15):
                print(f"  {_c2:4d}  {_nm:<24} "
                      f"{len({m for m in _idx.get(_nm, ()) if m})} homes")
            if len(_amb) > 15:
                print(f"       … and {len(_amb) - 15} more name(s)")
            print(f"\n{sum(_one.values())} repairable site(s) over {len(_one)} name(s); "
                  f"{sum(_amb.values())} ambiguous site(s) over {len(_amb)} name(s).")
        else:
            for _p in sorted(_by):
                print(f"{_p}")
                for _nm in sorted(_by[_p]):
                    _homes = sorted({m for m in _idx.get(_nm, ()) if m})
                    _tag = ("1 home" if len(_homes) == 1
                            else f"{len(_homes)} homes — AMBIGUOUS, not repaired")
                    print(f"   {_nm:<20} {_tag}")
                    for _h in _homes[:6]:
                        print(f"        -> open import {_h}")
        print(f"\n{len(_rows)} unresolved name(s) in {len(_by)} of "
              f"{len(_paths)} file(s) — a FLOOR: a name with no known definer is "
              f"SILENT (local binding, stdlib, or pattern variable), so this "
              f"reports what it can SEE, never that nothing is missing.")
        # ⚑⚑ THE WRITE PATH FOR THE STATIC CENSUS — ⟡ban-migration-scope.  Until now
        # `--unresolved` could SIZE the population (2,824 names in 940 files, 919 of them
        # single-definer) and not touch it: the only `--apply` was log-driven, and a build
        # log names ONE missing import per file because scope checking halts at the first
        # failure.  Repairing 919 sites that way means 919 builds.
        #
        # ⚑ SAFE TREE-WIDE FOR THE SAME REASON THE LOG MODE IS: `repair_one` snapshots
        # before writing, isolate-typechecks after, and REVERTS anything that did not
        # supply the name.  Ambiguous names are refused, never guessed.  What scales here
        # is the number of ISOLATE CHECKS — one agda invocation per repair — so this is
        # slow by construction, and that is the right trade against a hand sweep.
        if apply:
            print("\n── APPLYING single-definer repairs "
                  "(snapshot → add ALL → isolate-check ONCE → revert file if unhelped) ──")
            _k = _r = _b = 0
            for _p in sorted(_by):
                _v, _d = repair_imports_in_file(_real[_p], sorted(set(_by[_p])), _idx)
                print(f"  {_v:<14} {_p}  {_d}")
                _k += _v == "repaired"
                _r += _v == "reverted"
                _b += _v == "blocked"
            print(f"\n{_k} file(s) repaired · {_r} reverted · {_b} blocked "
                  f"(every single-definer name ambiguous or unknown)")
        sys.exit(0)
    if "--classify" in sys.argv:
        # ⚑ THE DIAGNOSIS IS REACHABLE ON ITS OWN, so a witness can consume it
        # without the write path.  Grouped by verdict — the population is the
        # report, and a bare count would hide which names are which problem.
        import collections as _c
        rows = classify(log)
        by = _c.defaultdict(list)
        for _p, nm, verdict, homes in rows:
            by[verdict].append((nm, len(homes)))
        for verdict in ("resolvable", "ambiguous", "no-definer"):
            names = by.get(verdict, [])
            uniq = sorted({n for n, _h in names})
            print("%-11s %3d site(s), %d distinct name(s): %s"
                  % (verdict, len(names), len(uniq), ", ".join(uniq[:8])
                     + (" …" if len(uniq) > 8 else "")))
        print("%d site(s) total" % len(rows))
        sys.exit(0)
    idx = agda_defs.def_index()
    seen = set()
    for path, name in parse(log):
        if (path, name) in seen:
            continue
        seen.add((path, name))
        repair_one(path, name, idx, apply)
    sys.exit(0)


def repair_one(path, name, idx, apply):
    """Re-supply ONE name in ONE file. Returns 'add' / 'revert' / 'refuse'.

    ⚑⚑ EXTRACTED SO `--unresolved` CAN WRITE, AND THAT WAS THE WHOLE BLOCKER. The
    log-driven mode had the only write path; `--unresolved` (the STATIC census, which
    sees every missing name rather than the one Agda halted on) could only REPORT.  So
    the tree-wide population — 919 mechanically-repairable sites over 357 names — had no
    route to repair except re-running the build once per name, since scope checking stops
    at the FIRST failure per file.  A census that can size a population and not act on it
    leaves the work to a hand sweep, which is what this tool exists to replace.

    ⚑ THE SAFETY IS UNCHANGED AND IS WHY THIS IS SAFE TO RUN TREE-WIDE: every addition is
    isolate-typechecked, and REVERTED if the name is still unbound — so a wrong guess
    cannot accumulate.  A revert that finds a stale `using` shadowing the name says so,
    rather than leaving a bare failure for a human to re-derive.
    """
    # Agda reports an operator by its BARE spelling (`,`), while the index
    # records the mixfix one (`_,_`) — try both, or every operator refuses.
    # `def_index` also indexes only TOP-LEVEL defs: it misses constructors,
    # record fields and anything nested in a `module _ … where`.  For the
    # Foundation constructors that recur, name the home directly rather than
    # let a known case refuse forever.
    FALLBACK = {",": "Substrate.Foundation.Product",
                "tt": "Substrate.Foundation.Unit",
                "[]": "Substrate.Foundation.List",
                "∷": "Substrate.Foundation.List"}
    defs = sorted(idx.get(name, []) or idx.get(f"_{name}_", []))
    if not defs and name in FALLBACK:
        defs = [FALLBACK[name]]
    src = open(path).read()
    defs = [d for d in defs
            if not re.search(r"^(open\s+import|import)\s+" + re.escape(d) + r"\b", src, re.M)]
    defs = narrow_by_provenance(defs, src)
    if len(defs) != 1:
        print(f"REFUSE {path}  {name}  -> {defs or 'no definer in index'}")
        return "refuse"
    mod = defs[0]
    print(f"{'ADD   ' if apply else 'WOULD ADD'} {path}  {name} <- {mod}")
    if not apply:
        return "add"
    before = src
    # ⚑⚑ THE SNAPSHOT IS ARMED BEFORE THE WRITE, NOT ON THE REVERT PATH — and it was on
    # the revert path until 2026-08-23 (operator: *"make sure the snapshot thing is
    # employed"*).  That ordering had it backwards: a snapshot taken as part of undoing a
    # change protects nothing, because the state worth recovering is the one BEFORE the
    # first `add_import`.  The reverting case was in fact the ONE case already safe — it
    # holds `before` in memory and restores it.  The unprotected case was the SUCCESS
    # path: an addition that isolate-checks OK is kept, on disk, with no snapshot behind
    # it.  Sixteen files were rewritten that way earlier this session.
    #
    # ⚑ AND IT MATTERS MORE NOW THAT `--unresolved --apply` EXISTS.  Log-driven repair
    # touches the handful of files the build reached; the static census touches up to 940.
    # `edit_snapshot.guard` is the repo-wide precondition for an in-place source editor
    # (it exists because a rewrite once left 33 files unrecoverable), and a tree-wide
    # sweep is exactly the shape that rule was written for.
    import edit_snapshot as _es
    _es.guard("fix_notinscope", [path], intent="apply")
    add_import(path, mod)
    ok, out = check(path)
    if not ok and name in out:
        open(path, "w").write(before)
        print(f"  REVERTED — {mod} did not supply {name}")
        # A correct import that STILL leaves the name unbound means the name
        # is SHADOWED: some other import carries a `using (… name …)` that no
        # longer exports it, and Agda binds to that empty provision instead.
        # That is fix_stale_using's case, not this tool's — name it rather
        # than leave a bare revert for a human to re-derive (measured: this
        # exact shape cost a hand-diagnosis on SBoxTable/∧-elimˡ).
        for m in re.finditer(r"^(?:open\s+import|import)\s+(\S+)([^\n]*(?:\n[ \t]+[^\n]*)*)",
                             before, re.M):
            if re.search(r"\busing\b", m.group(2)) and re.search(
                    r"(?<![\w'-])" + re.escape(name) + r"(?![\w'-])", m.group(2)):
                print(f"  ↳ SHADOWED by `{m.group(1)}`'s stale `using` — "
                      f"drop {name} from it (scratch/fix_stale_using.py)")
                break
        return "revert"
    print(f"  isolate-check {'OK' if ok else 'a DIFFERENT error remains — kept'}")
    return "add"
