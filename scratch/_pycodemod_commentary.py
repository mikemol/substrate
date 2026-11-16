# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The ⚑ INCIDENT-LOG census and its preservation gate — `pycodemod --commentary`.

⚑⚑ SPLIT OUT OF `_pycodemod_census.py` 2026-08-11, AND BY THAT MODULE'S OWN SEAM RULE. Its
header states the rule: *"THE SEAM IS THE UNIT OF THE ANSWER, NOT THE TOPIC. Everything here
answers about the CORPUS — how big are the modules, what state do they hold, what do they
import."* Every one of those reads CODE STRUCTURE. These two read the COMMENTARY — the ⚑ lines
that are this corpus's incident log, which `module_size` deliberately refuses to count as bulk
and `--roundtrip` exists to protect. Same corpus, different substrate.

⚑ AND THE SECOND HALF IS NOT A CENSUS AT ALL — IT IS A GATE. `commentary_census` reports;
`commentary_lost` compares against a git ref and its CLI exits 1 when a ⚑ line vanished. A
module of read-only reports is a different object from one that can refuse a change, and
filing them together is how a reader loses track of which of their calls can block.

⚑ THE IMMEDIATE CAUSE WAS THE RULE FIRING ON ME. Adding these to `_pycodemod_census.py` took
it from 1,113 to 1,201 code lines — ONE over its own 1,200 cap, reported by the very `--size`
mode this session extended. Paying it down here rather than raising a threshold is what the
census is for; `INCIDENT_HALVINGS`'s note says it directly: *"never lower a count — this is a
ratchet, and paying it down means SPLITTING the file"*.
"""
import ast
import os
import re

import _pycodemod_core
import _pycodemod_core

#: The glyphs that mark a line of INCIDENT COMMENTARY in this corpus.
#:
#: ⚑ PARAMETERIZED BECAUSE A HARDCODED VOCABULARY ROTS. The struct-tools rule records this
#: exact defect one level up — an `--items` matcher that knew only one repo's marker glyphs
#: could not see another's. This tooling is borrowed by several checkouts, so the mark set is
#: a constant a caller can widen rather than a literal buried in a comprehension.
COMMENTARY_MARKS = ("⚑",)


def commentary_census(paths=None, marks=COMMENTARY_MARKS):
    """[(path, lines, distinct)], {normalized text: [(path, lineno)]}, nfiles — the ⚑ COMMENTARY
    census: how much incident log each module carries, and WHICH lines they are.

    ⚑ THIS EXISTS BECAUSE `--roundtrip` GUARDS THE WRONG BOUNDARY FOR A SPLIT. Losslessness is
    per-file: it proves parse→emit reproduced THIS file byte-for-byte, which is exactly what a
    decomposition does not do. Moving a def to a sibling passes `--roundtrip` on both files while
    silently dropping the ⚑ block that explained it — and that block is the more valuable half
    (`module_size` refuses to count comment lines as bulk for the same reason). The preservation
    question is a SET question across a GROUP of files, and no mode asked it: verifying it by
    hand meant `grep -c ⚑`, which the structural-query hook correctly refuses.

    ⚑ NORMALIZED, BECAUSE A RELOCATION RE-INDENTS AND RE-COMMENTS. A ⚑ line moving from a def
    body to module scope loses four spaces; one moving from a docstring into a `#` block gains a
    sigil. A byte-compare reports every moved line as lost-and-gained at once, which answers a
    formatting question while claiming to answer a preservation one. Leading comment sigils,
    quotes and all runs of whitespace are collapsed, so the key is the SENTENCE.

    ⚑ AND IT COUNTS EVERY LINE CARRYING A MARK, NOT ONLY COMMENT LINES. This corpus writes ⚑
    notes in three places — `#` comments, docstrings, and the literal strings a CLI PRINTS
    (`print("  ⚑ a column that is EVER null is payload…")`). Restricting to `tokenize`'s COMMENT
    tokens would silently exclude the third, so a split that dropped a printed caveat would read
    as clean. The distinction `_code_lines` draws is about BULK; this one is about the log.
    """
    rows, texts = [], {}
    files = list(paths) if paths else _pycodemod_core.py_files()
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n, seen = 0, set()
        for i, line in enumerate(src.splitlines(), 1):
            if not any(_mark_hit(m, line) for m in marks):
                continue
            n += 1
            key = _commentary_key(line)
            seen.add(key)
            texts.setdefault(key, []).append((p, i))
        if n:
            rows.append((p, n, len(seen)))
    return rows, texts, len(files)


def commentary_kinds(paths=None, marks=COMMENTARY_MARKS):
    """{kind: [(path, lineno, text)]} — each marker line by WHERE IT LIVES: comment, docstring,
    or EXECUTABLE (a string literal the running program emits or names).

    ⚑⚑ THE EXECUTABLE MARKS ARE NOT DOCUMENTATION OF BEHAVIOUR — THEY ARE THE BEHAVIOUR, and
    the flat census cannot tell them apart. Measured by summit reading this repo through a
    symlink: of 20 marks in `hook_structural_query.py`, FIVE are code — two are the refusal
    message a blocked reader actually sees, three are selftest case NAMES. A selftest named
    `⚑ a .py in ANOTHER repo is still claimed` is an executable assertion whose name IS the
    claim: argument and check already welded, which is the end state a claim-migration is
    trying to REACH. Counting them as migratable prose overcounts the population and would
    move an argument away from the code that executes it.

    ⚑ `tokenize` IS THE AUTHORITY, NOT A REGEX. A `#` inside a string is not a comment and a
    `⚑` inside a comment is not code; only the tokenizer draws that line, and this corpus
    writes marks in all three places deliberately (`commentary_census`'s third ⚑). A file that
    does not tokenize (a syntax error, a PY2 leftover) is reported under `unparsed` rather
    than silently dropped — an absent classification is a fact about the METHOD.
    """
    import io
    import tokenize as _tk
    out = {"comment": [], "docstring": [], "executable": [], "unparsed": []}
    files = list(paths) if paths else _pycodemod_core.py_files()
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        hits = {}
        for i, line in enumerate(src.splitlines(), 1):
            if any(_mark_hit(m, line) for m in marks):
                hits[i] = _commentary_key(line)
        if not hits:
            continue
        comment_lines, string_lines = set(), set()
        try:
            for tok in _tk.generate_tokens(io.StringIO(src).readline):
                if tok.type == _tk.COMMENT:
                    for ln in range(tok.start[0], tok.end[0] + 1):
                        comment_lines.add(ln)
                elif tok.type == _tk.STRING:
                    for ln in range(tok.start[0], tok.end[0] + 1):
                        string_lines.add(ln)
        except (_tk.TokenError, IndentationError, SyntaxError):
            for ln, txt in sorted(hits.items()):
                out["unparsed"].append((p, ln, txt))
            continue
        # ⚑ A DOCSTRING IS A STRING IN STATEMENT POSITION; every other string is EXECUTABLE
        # payload. `ast` knows which strings are docstrings and `tokenize` knows which lines
        # are strings, so the two are combined rather than either guessed at.
        doc_lines = set()
        try:
            tree = ast.parse(src)
            for node in ast.walk(tree):
                body = getattr(node, "body", None)
                if not isinstance(body, list) or not body:
                    continue
                first = body[0]
                if (isinstance(first, ast.Expr)
                        and isinstance(first.value, ast.Constant)
                        and isinstance(first.value.value, str)):
                    for ln in range(first.lineno, (first.end_lineno or first.lineno) + 1):
                        doc_lines.add(ln)
        except SyntaxError:
            pass
        for ln, txt in sorted(hits.items()):
            if ln in comment_lines:
                out["comment"].append((p, ln, txt))
            elif ln in doc_lines:
                out["docstring"].append((p, ln, txt))
            elif ln in string_lines:
                out["executable"].append((p, ln, txt))
            else:
                out["comment"].append((p, ln, txt))
    return out


def commentary_blocks(paths=None, marks=COMMENTARY_MARKS):
    """[(path, start, end, enclosing, [cited symbols], text)] — each ⚑ INCIDENT as a BLOCK,
    with the code it is ATTACHED TO and the symbols it NAMES.

    ⚑⚑⚑ THE LINE IS NOT THE UNIT OF AN INCIDENT, AND EVERY EXISTING READER SPLITS ONE.
    `commentary_census` and `--lines` key on a single physical line, so a five-line ⚑ paragraph
    reads as five independent records — and only the FIRST carries the mark, so the other four
    are invisible to a mark-keyed census entirely. Measured on this very module: the block at
    :3 spans lines 3-8 and `--lines` reports it as `:3` and `:6`, two fragments of one sentence,
    with the clause naming the seam rule split away from the clause naming the rule. A corpus
    read that way clusters on line-fragments rather than on incidents.

    ⚑⚑ AND THE JOIN TO THE REMEDY IS THE BACKTICKED SYMBOL, WHICH NOTHING EXTRACTED. This corpus
    writes an incident and its fix together — *"`--roundtrip` GUARDS THE WRONG BOUNDARY … the
    preservation question is a SET question"* names `--roundtrip` and `commentary_census` in the
    same block. That is an EDGE from a defect shape to the tool that addresses it, already
    present in 10,958 lines of prose and reachable by no query: `--commentary` counted, `--lines`
    printed text, and neither surfaced the citation. The symbols are what makes a shape resolve
    to a mode instead of to a paragraph.

    ⚑ THE ENCLOSING SCOPE COMES FROM `ast`, NOT FROM INDENTATION. A block sits in a module
    docstring, a def docstring, or a `#` run above a statement, and only the tree says which def
    owns line N. A file that does not parse yields blocks with `enclosing=None` rather than being
    dropped — an absent classification is a fact about the METHOD, and dropping the file would
    make an unparseable module read as carrying no incidents at all.

    ⚑ CONTIGUITY IS THE GROUPING PREDICATE, AND IT IS DELIBERATELY SYNTACTIC. Two ⚑ paragraphs
    separated by a blank line are two incidents; consecutive non-blank lines are one. A semantic
    grouping would be a judgement, and this returns the extent so the caller can make it.
    """
    rows = []
    files = list(paths) if paths else _pycodemod_core.py_files()
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        lines = src.splitlines()
        owners = _scope_index(src, len(lines))
        i, n = 0, len(lines)
        while i < n:
            if not any(_mark_hit(m, lines[i]) for m in marks):
                i += 1
                continue
            start = i
            j = i + 1
            # ⚑ THE BLOCK RUNS TO THE FIRST BLANK OR CLOSING QUOTE, not to the next mark. A
            # continuation line carries no ⚑ by construction — that is what makes it a
            # continuation — so a mark-terminated scan would end every block at length one and
            # reproduce exactly the fragmentation this exists to remove.
            while j < n and lines[j].strip() and not lines[j].strip().startswith(('"""', "'''")):
                if any(_mark_hit(m, lines[j]) for m in marks):
                    break
                j += 1
            text = " ".join(_commentary_key(x) for x in lines[start:j])
            rows.append((p, start + 1, j, owners.get(start + 1),
                         sorted(set(_BACKTICKED.findall(text))), text))
            i = j
    return rows


#: Symbols an incident CITES — a backticked token that looks like a flag or an identifier.
#:
#: ⚑ BACKTICKS ARE THE CONVENTION AND THEY ARE LOAD-BEARING. This corpus marks up every mode,
#: function and constant it names in prose; an unbackticked capitalised word is emphasis, not a
#: citation. Keying on the markup rather than on capitalisation is what keeps `SET question` out
#: of the citation set while keeping `--roundtrip` in.
_BACKTICKED = re.compile(r"`(--?[A-Za-z][\w-]*|[A-Za-z_][\w.]*(?:\(\))?)`")


def _scope_index(src, nlines):
    """{lineno: 'qualified.name'} — which def/class OWNS each line.

    ⚑ INNERMOST WINS, so a nested def is reported rather than its module-level parent. Walking
    outermost-first and overwriting achieves that without a second pass, because `ast.walk` yields
    a parent before its children.
    """
    out = {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    stack = [(tree, "")]
    while stack:
        node, prefix = stack.pop(0)
        for child in ast.iter_child_nodes(node):
            name = prefix
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}.{child.name}" if prefix else child.name
                for ln in range(child.lineno, (child.end_lineno or child.lineno) + 1):
                    out[ln] = name
            stack.append((child, name))
    return out


#: Cache of compiled mark matchers — `commentary_census` tests every mark against every line
#: of every file, so recompiling per line would be the dominant cost on a corpus scan.
_MARK_RE = {}


def _mark_hit(mark, line):
    """Does `mark` occur in `line` AS A MARK, rather than inside a word?

    ⚑⚑ IT WAS A BARE SUBSTRING TEST, AND A TWO-LETTER MARK FIRED ON ANY WORD CONTAINING IT.
    Measured: `--marks 'NB'` reported a hit on *"⚑ AN UNBALANCED QUOTE IS BASH'S VERDICT"* —
    `NB` inside "U**NB**ALANCED". So a peer widening the mark set to read another repo's
    conventions got a count inflated by the widening itself, and the inflation is invisible
    without `--lines`. A census whose PRECISION depends on how short the caller's sigil is
    cannot be compared across repos, which is the one thing a widenable mark set exists for.

    ⚑ THE BOUNDARY IS CONDITIONAL, BECAUSE `⚑` HAS NO WORD BOUNDARY. `\\b` is defined against
    `\\w`, and a glyph is not a word character — anchoring it would break the DEFAULT mark and
    report this corpus as empty, which is the failure this fix exists to prevent, inverted.
    Alphanumeric marks (`NB`, `TODO`, `RACE`) get boundaries; symbolic ones are matched raw.
    """
    rx = _MARK_RE.get(mark)
    if rx is None:
        if mark and (mark[0].isalnum() or mark[-1].isalnum()):
            lead = r"\b" if mark[0].isalnum() else ""
            trail = r"\b" if mark[-1].isalnum() else ""
            rx = re.compile(lead + re.escape(mark) + trail)
        else:
            rx = re.compile(re.escape(mark))
        _MARK_RE[mark] = rx
    return bool(rx.search(line))


def _commentary_key(line):
    """One marker line → its NORMALIZED sentence. See `commentary_census`'s second ⚑."""
    return re.sub(r"\s+", " ", line.strip().lstrip("#:'\" ").strip())


def commentary_lost(paths, ref=":", marks=COMMENTARY_MARKS, _origins=False):
    """(lost, gained, n_before, n_after) — which ⚑ lines a SPLIT dropped, by text.

    ⚑ COUNTING WAS NOT ENOUGH, AND THE GAP IS THE WHOLE POINT OF THE GATE. `commentary_census`
    over a group answers "is the total the same"; a split that drops one note and adds another
    keeps the total and passes. The question a decomposition actually asks is a SET DIFFERENCE
    across a REVISION — *of the lines that were there before, which are not there now* — and
    reconstructing that by comparing two printed censuses by eye is exactly the judgement this
    repo's standing rule says must live in a program.

    ⚑ THE BASELINE DEFAULTS TO THE INDEX (`:`), NOT `HEAD`, BECAUSE A SPLIT'S INPUT IS OFTEN
    NOT COMMITTED YET. `scope_fix.py` was staged-added and absent from HEAD entirely, so a
    HEAD baseline would have read as "nothing existed before" — an empty diff that looks like
    a clean split and measures nothing. Any git ref works; `:` is what "before I started" means
    in a working tree.

    ⚑⚑ AND THE INDEX IS ONLY "BEFORE I STARTED" IF NOTHING ELSE IS UNSTAGED — MEASURED ON THE
    FIRST REAL RUN. Both files this gate was built for had UNCOMMITTED in-flight edits from a
    concurrent migration, so `:` sat BEHIND the split's actual starting point and the gate
    attributed that migration's removals to the split. The ref is the caller's to choose and
    no default can be right for every tree; what the gate owes is the ORIGIN of each lost line,
    so the caller can tell whose removal it is.

    ⚑ AND A PATH MISSING AT THE REF CONTRIBUTES NOTHING RATHER THAN FAILING. The new siblings a
    split creates do not exist in the baseline by construction; treating that as an error would
    make the gate unusable for the only transform it exists to check.
    """
    import subprocess
    before, after = {}, {}
    for p in paths:
        rel = os.path.relpath(os.path.abspath(p), _pycodemod_core.ROOT)
        got = subprocess.run(["git", "show", f"{ref}{rel}"], cwd=_pycodemod_core.ROOT,
                             capture_output=True, text=True)
        for line in (got.stdout if got.returncode == 0 else "").splitlines():
            if any(m in line for m in marks):
                before.setdefault(_commentary_key(line), []).append(rel)
    _rows, after, _n = commentary_census(paths, marks)
    out = (sorted(set(before) - set(after)), sorted(set(after) - set(before)),
           sum(len(v) for v in before.values()), sum(len(v) for v in after.values()))
    return out + (before,) if _origins else out
