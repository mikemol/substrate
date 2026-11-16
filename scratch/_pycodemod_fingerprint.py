# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""`--fingerprint` — A PRIME PER DISTINCT REFERENT, AND THE REMAINDER IS THE FINDING.

⚑ WHY THIS EXISTS: `--control` PRODUCED A PILE WITH NO ORDER IN IT.  The control-flow
census types every site, and over the SPPF import closure 1,130 of 2,034 come back
`unclassified` — not because the sites are alike but because the classifier's row
provenance is intra-scope plus one hop, so a function that receives rows as a PARAMETER
reads as "could not determine".  That verdict is honest and it is also inert: an
undifferentiated pile has no ordering, no grouping and no progress metric, so nothing can
say which sites matter, which are related, or whether attacking them is working.

⚑⚑ THE MECHANISM CLASSIFIES NOTHING, AND THAT IS THE WHOLE TECHNIQUE.  Lifted from
`gabion/src/gabion/analysis/core/type_fingerprints.py` (a sibling repo, read-only here —
the machine is lifted, the code is NOT imported, and its seeded basis of four hand-listed
names is left behind because we seed from our own material).  Three moves:

  1. **A prime per distinct thing.**  `PrimeRegistry.get_or_assign(key)` takes any
     non-empty string; NON-EMPTY IS THE ONLY VALIDATION (gabion `type_fingerprints.py:294`:
     `if not key: raise ValueError("Type key must be non-empty.")`).  Assigning a prime
     asserts that a referent is DISTINCT AND COUNTABLE — never what it IS.  Identity
     without taxonomy.
  2. **Compose by multiplication.**  A site's fingerprint is the product over its
     referents.  Then `gcd` is shared structure, `%` is containment, `(a//g)*(b//g)` is
     structural difference — and *is A inside B* is ONE MODULO, with nothing decoded.
  3. **Decode against the primes you understand; keep the remainder as an integer.**
     `decode_with_remainder` trial-divides by every prime in the MODELLED registry and
     returns `(keys_you_understand, integer_you_do_not)`.  The remainder is EXACT:
     multiply the understood primes back and you recover the fingerprint.

⚑ `strict=False` IS THE DEFAULT AND THE RIGID MODE IS ONE KEYWORD AWAY (gabion
`type_fingerprints.py:1340` — copied deliberately).  A system that survives unknown fill
is one whose DEFAULT path returns a remainder rather than raising.  `strict=True` exists,
is tested, and is off.

⚑ THE REFERENT-EXTRACTION RULE, AND WHY IT IS NOT A TAXONOMY.  A site's referents are the
TOKENS its governing expression mentions: every `Name.id`, every `Attribute.attr`, every
keyword-argument name, and every string constant that spells a (dotted) identifier.  The
key IS the token — no prefix, no namespace, no kind.  So `core_id` reached as an attribute
and `"core_id"` written as a string literal are ONE referent, which is exactly what makes
the decode work: the string a site passes to a query and the column the schema declares
are the same countable thing.  Nothing here decides what a token is; the only rule is that
two occurrences of the same spelling are the same referent and two spellings are two.

⚑ THE GOVERNING EXPRESSION, NOT THE WHOLE STATEMENT, AND THAT IS COMMENSURABILITY RATHER
THAN THRIFT.  `_Census.classify` reads exactly the governing expression to decide a site's
kind, so a fingerprint over the same expression measures the same surface the verdict was
formed on.  Fingerprinting the enclosing statement would make the residual and the kind
answer questions about different things.  Consequence, stated rather than left to be
discovered: a `break` with no enclosing test has NO governing expression and so
fingerprints to 1 — a site that mentions nothing is a site nothing can be learned from,
and it sorts to the bottom of the residual ordering by construction.

⚑ NUMERIC AND NON-IDENTIFIER STRING CONSTANTS ARE NOT REFERENTS.  `if n > 2:` contributes
`n`, not `2`; a raw SQL blob contributes nothing (`--sql` / `--relalg` own that artifact).
This is a SHAPE rule applied identically to the seed files and to the sites — not a
judgement about which referents are interesting.

⚑ PRIMES ARE ASSIGNED IN DESCENDING CORPUS FREQUENCY, ties broken by key.  This is a
COUNT, not a classification, and it is what makes the residual ORDERING readable: the most
common referent gets 2, so a large residual means *many unmodelled referents, weighted
toward RARE ones* — least-understood in the sense the ordering is asked for.  It also
bounds magnitude (Zipf puts the small primes where the mass is), which is the measurement
the "beware unbounded products" concern wants.  Encounter-order assignment (gabion's) is
equally correct algebraically and would make magnitude an artifact of walk order.

⚑ FINGERPRINTS ARE SQUAREFREE — the product runs over the DISTINCT referent set, so a
token mentioned five times contributes one factor.  That is why NO EXPONENT SIDECAR is
warranted here even though gabion has one (`fingerprint_exponent_vector`,
`type_fingerprints.py:1434`): with every exponent in {0,1} the exponent vector carries
exactly the information the integer already does.  Multiplicity is a real signal for
gabion's containers; for "which referents does this site touch" it is not.

⚑ THE TOTAL REMAINDER IS MONOTONE BY CONSTRUCTION, NOT BY DISCIPLINE.  Growing the
modelled set M ⊆ M' can only REMOVE factors from a site's remainder, so `r' | r` and
therefore `Ω(r') ≤ Ω(r)` and `bit_length(r') ≤ bit_length(r)` — site by site, hence in the
sum.  The metric CANNOT rise as understanding grows; a rise is a defect in the decoder,
which is why a case asserts the divisibility rather than the totals.

NOTHING IS PERSISTED.  The registry is DERIVED from the corpus plus the seed files on
every run and is a pure function of them, so there is no ledger to drift and no file in
`jea/metalanguage/` to reach into (that tree is in active use by another arc).  A future
persisted registry would need a stability contract this deliberately does not claim.
"""
import ast
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _pycodemod_core
import _pycodemod_core
import _pycodemod_control as _ctl

# ⚑ THE AUTHORITIES WE ALREADY MODEL.  Relative to ROOT and resolved at call time, not
# frozen into a constant a caller cannot widen: `--seed` ADDS to this, which is what makes
# the monotonicity demonstration a re-run rather than an edit.
DEFAULT_SEED = ("jea/metalanguage/schema_decl.py", "jea/metalanguage/query_decl.py")

# A token longer than this is prose, not a referent.  It is a SHAPE bound applied
# identically on both sides; nothing about the token's meaning is consulted.
MAX_TOKEN = 64


# ── the token rule ────────────────────────────────────────────────────────────────
def token_parts(s):
    """A string → the referent tokens it spells, or `()`.

    ⚑ ONE RULE, BOTH SIDES.  This runs over the seed files and over the sites, so a
    referent the declaration names and a referent a site mentions are compared as the
    same kind of thing by construction rather than by two matching rules kept in step.
    """
    if not isinstance(s, str) or not s or len(s) > MAX_TOKEN:
        return ()
    parts = s.split(".")
    if not all(p.isidentifier() for p in parts):
        return ()
    return tuple(parts)


def referents(nodes):
    """The DISTINCT referent tokens an expression (or list of them) mentions.

    ⚑ NO KIND SURVIVES INTO THE KEY.  A name, an attribute, a keyword and a string
    literal all contribute the bare token — so `terms`, `.terms` and `"terms"` are one
    referent.  Losing that collapse is what would make the decode blind to exactly the
    sites it exists to explain (a column named in a string, a relation named in a call).
    """
    out = set()
    for top in _ctl._as_list(nodes):
        for n in ast.walk(top):
            if isinstance(n, ast.Name):
                out.add(n.id)
            elif isinstance(n, ast.Attribute):
                out.add(n.attr)
            elif isinstance(n, ast.keyword) and n.arg:
                out.add(n.arg)
            elif isinstance(n, ast.Constant):
                out.update(token_parts(n.value))
    return {t for t in out if t and len(t) <= MAX_TOKEN}


# ── the registry ──────────────────────────────────────────────────────────────────
def _is_prime(v):
    if v < 2:
        return False
    if v in (2, 3):
        return True
    if v % 2 == 0 or v % 3 == 0:
        return False
    step = 5
    while step * step <= v:
        if v % step == 0 or v % (step + 2) == 0:
            return False
        step += 6
    return True


def _next_prime(start):
    c = max(start, 2)
    while not _is_prime(c):
        c += 1
    return c


class PrimeRegistry:
    """key → prime.  NON-EMPTY IS THE ONLY VALIDATION.

    ⚑ THE ABSENCE OF A CHECK IS THE FEATURE.  Any rule here about what a key may look
    like — a namespace prefix, a known-kinds roster, a length floor — would be the
    taxonomy this mechanism exists to avoid, and it would put the 1,130 back where they
    came from.  `get_or_assign` asserts only that a referent is distinct and countable.
    """

    def __init__(self):
        self.primes = {}
        self.next_candidate = 2

    def get_or_assign(self, key):
        if not key:
            raise ValueError("referent key must be non-empty")
        existing = self.primes.get(key)
        if existing is not None:
            return existing
        p = _next_prime(self.next_candidate)
        self.primes[key] = p
        self.next_candidate = p + 1
        return p

    def prime_for(self, key):
        return self.primes.get(key)

    def __contains__(self, key):
        return key in self.primes

    def __len__(self):
        return len(self.primes)


def fingerprint(keys, reg):
    """The product over the DISTINCT referents — squarefree by construction."""
    fp = 1
    for k in sorted(set(keys)):
        fp *= reg.get_or_assign(k)
    return fp


def reverse_index(reg, only=None):
    """[(prime, key)] ASCENDING BY PRIME — the decode order.

    `only` restricts the index to the keys we claim to model; that restricted index IS
    "the primes you understand", and decoding against it is the whole of move 3.
    """
    items = [(p, k) for k, p in reg.primes.items()
             if only is None or k in only]
    return sorted(items)


def decode_with_remainder(fp, rev):
    """`(keys_you_understand, integer_you_do_not)` — EXACT.

    ⚑ THE `while` RATHER THAN AN `if` IS LIFTED VERBATIM (gabion :1331) even though our
    fingerprints are squarefree, so the decoder stays correct for a multiset fingerprint
    if one is ever built here.  Removing it would make the function silently wrong for an
    input this module does not produce TODAY — the shape a later reader pays for.
    """
    remaining, keys = fp, []
    if remaining <= 1:
        return keys, remaining
    for p, k in rev:
        while remaining % p == 0:
            keys.append(k)
            remaining //= p
        if remaining == 1:
            break
    return keys, remaining


def decode(fp, rev, strict=False):
    """`strict=False` IS THE DEFAULT (gabion :1340).  Rigid mode is one keyword away."""
    keys, rem = decode_with_remainder(fp, rev)
    if strict and rem not in (0, 1):
        raise ValueError("fingerprint %d carries primes outside the registry" % fp)
    return keys


# ── the lattice (multiplication IS the algebra; nothing is decoded) ───────────────
def fp_shared(a, b):
    return math.gcd(a, b)


def fp_contains(container, part):
    return part != 0 and container % part == 0


def fp_difference(a, b):
    g = math.gcd(a, b)
    return (a // g) * (b // g)


def omega(n):
    """Ω over a SQUAREFREE fingerprint — how many referents it carries.

    ⚑ IT COUNTS FACTORS AGAINST THE REGISTRY, NOT BY FACTORISING.  A general integer
    factorisation would be a second, slower authority on a number whose factors are
    already known; worse, it would disagree with the registry on a composite the registry
    never assigned.  `omega_against` is the real entry point; this one exists for the
    cases and takes the prime list explicitly.
    """
    raise NotImplementedError("use omega_against(n, primes)")


def omega_against(n, primes):
    """How many of `primes` divide `n` (with multiplicity)."""
    c, rem = 0, n
    for p in primes:
        while rem % p == 0:
            c += 1
            rem //= p
        if rem == 1:
            break
    return c


# ── the modelled set, and the site population ────────────────────────────────────
def modelled_keys(paths):
    """Every referent token the AUTHORITY FILES mention — the set we claim to model.

    ⚑ THE SAME EXTRACTOR, RUN OVER THE DECLARATION.  `schema_decl.py` names its relations
    and columns as string arguments and as module-level bindings; `query_decl.py` names
    its builders as defs.  Reading them with the site extractor means the two sides cannot
    drift apart by one of them growing a rule the other lacks — and it means the modelled
    set is a fact about what the declaration SAYS, never a hand-kept list.

    ⚑ IT IS DELIBERATELY WIDE, AND THE REPORT NAMES WHAT IS DOING THE WORK.  A token like
    `select` or `sys` enters M because the declaration mentions it, so a site is credited
    for sharing it.  That is over-credit, it is measurable, and the per-key explanation
    table prints it — which is the honest form.  Narrowing it would take a rule about
    which referents "really" count, i.e. the taxonomy.
    """
    out = set()
    for p in paths:
        try:
            tree = ast.parse(open(p, encoding="utf-8").read(), filename=str(p))
        except (OSError, SyntaxError, ValueError):
            continue
        out |= referents(tree)
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out.add(n.name)
    return {t for t in out if t and len(t) <= MAX_TOKEN}


class _FpCensus(_ctl._Census):
    """`_Census` with the governing expression KEPT.

    ⚑ A SUBCLASS AND NOT A COPY.  Every classification predicate, the row-provenance
    fixpoint, the one-hop ε rule and the elif/else bookkeeping stay in
    `_pycodemod_control` — this overrides exactly one method to retain the node the
    verdict was formed on.  Re-implementing the walk would give a second census free to
    disagree with the one whose numbers this report quotes.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.gov = []

    def emit(self, lineno, construct, g, snippet, mode_g=False):
        before = len(self.out)
        super().emit(lineno, construct, g, snippet, mode_g=mode_g)
        for _ in range(len(self.out) - before):
            self.gov.append(g)


def site_referents(path, src=None):
    """[(line, construct, kind, scope, snippet, frozenset(referents))] for one file.

    `src` supplies the SOURCE TEXT directly; `path` is then only the name that
    appears in `ast.parse`'s errors and in the desync `AssertionError` below.

    ⚑ THE PATH WAS DOING TWO JOBS AND ONLY ONE OF THEM IS INTRINSIC.  Everything
    downstream operates on `tree`; the read is incidental.  Fusing them made the
    function uncallable on source text, so every caller — the suite included — had
    to MATERIALISE A FILE to ask a question about a string.  Splitting the two
    restores `filename=` to its actual role (a label in a diagnostic) rather than
    a coincidence of where the bytes came from.

    ⚑ THIS IS DELIBERATELY *NOT* ROUTED THROUGH `vfs`.  `vfs` earns its keep where
    ABSENT must be told from BROKEN, and above all where a caller reads AT A
    REVISION.  This reader has neither need: it is called over a population that
    `py_files()`/`local_closure()` ALREADY ENUMERATED FROM THE WORKING TREE, so a
    file that is absent here is a race, not an answer a caller branches on — and
    nothing fingerprints sites at a `Rev`.  Taking `src` is the weaker, sufficient
    lift; a `Rev`-reading caller would pass `vfs.read_text(p, Rev(...))` INTO it,
    which is the composition that keeps `vfs` optional rather than load-bearing.

    ⚑ THE `except -> []` SWALLOW IS KEPT, AND IT IS A REAL WEAKNESS.  An
    unparseable file and a file with no sites are the SAME ANSWER here, which is
    `census-green-is-a-fact-about-the-census` at a function boundary.  It is kept
    because `collect()` sweeps hundreds of files, several of which are Python-2 or
    templated and have never parsed, and a raise would make the census
    unrunnable — the caller wants "skip what I cannot read". Changing it is a
    CALLER-VISIBLE contract change and belongs to its own item, not to this one.
    """
    if src is None:
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            return []
    try:
        tree = ast.parse(src, filename=str(path))
    except (SyntaxError, ValueError):
        return []
    rfns = _ctl.store_reader_fns(tree)
    consts = _ctl._module_consts(tree)
    out = []
    for scope, label in _ctl.scopes(tree):
        own = list(_ctl._own_walk(scope))
        rows = _ctl.row_names(own, rfns)
        rows |= _ctl.derived_names(own, rows)
        cen = _FpCensus(rows, _ctl.ext_names(own), _ctl._params(scope), consts,
                        rfns, label)
        body = scope.body
        if body and isinstance(body[-1], ast.Return):
            cen.tail.add(id(body[-1]))
        cen.stmts(body)
        cen.exprs(scope)
        # ⚑ THE ALIGNMENT IS ASSERTED BECAUSE `zip` WOULD HIDE ITS FAILURE.  `emit`
        # appends exactly one row today, so the `for _ in range(...)` above is
        # extensionally a single append — MEASURED: replacing it with one is an
        # EQUIVALENT MUTANT that no case can catch.  It is kept anyway, and this check is
        # what makes keeping it meaningful: if `_Census.emit` ever appends zero or two
        # rows, `zip` TRUNCATES SILENTLY and every subsequent site is fingerprinted
        # against another site's expression — a wrong answer that reports as a clean run,
        # which is the failure shape this whole toolkit is written against.
        if len(cen.out) != len(cen.gov):
            raise AssertionError(
                "governing-expression track desynced from the site rows in %s (%d vs %d)"
                % (path, len(cen.out), len(cen.gov)))
        for (line, construct, kind, _form, lbl, snip), g in zip(cen.out, cen.gov):
            out.append((line, construct, kind, lbl, snip, frozenset(referents(g))))
    return sorted(out, key=lambda r: (r[0], r[1]))


# ── the local-import closure (the population the control census was read over) ────
def local_closure(entries):
    """Every repo `.py` transitively reachable by a LOCAL import from `entries`.

    ⚑ THIS IS A MISSING MODE, BUILT RATHER THAN ROUTED AROUND.  `toolmodes --find closure`
    reports `--closure` on `agda_defs` and *"⚑ NOT on: scratch/pycodemod.py"* — so the
    population the control census is quoted over ("the SPPF import closure, 22 files")
    could be typed by hand and could not be COMPUTED.  A population that only exists in a
    sentence is not reproducible, and every count read over it inherits that.

    ⚑ RESOLUTION IS BY FILENAME OVER THE CORPUS, WHICH IS WHAT THE CODE ACTUALLY DOES.
    These modules import each other as bare top-level names (`import schema`,
    `from query_defs import …`) because each inserts its own directory on `sys.path`; a
    package-qualified resolver would find none of them.  A name matching several files is
    reported as AMBIGUOUS and every candidate is taken, because silently picking one is
    how a population narrows without saying so.
    """
    corpus = {}
    for p in _pycodemod_core.py_files():
        corpus.setdefault(os.path.basename(p)[:-3], []).append(p)
    seen, stack = set(), []
    for e in entries:
        e = e if os.path.isabs(e) else os.path.join(_pycodemod_core.ROOT, e)
        stack.append(os.path.abspath(e))
    while stack:
        p = stack.pop()
        if p in seen or not os.path.isfile(p):
            continue
        seen.add(p)
        try:
            tree = ast.parse(open(p, encoding="utf-8").read(), filename=str(p))
        except (OSError, SyntaxError, ValueError):
            continue
        names = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                names.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names.add(n.module.split(".")[0])
        for nm in names:
            for cand in corpus.get(nm, ()):
                if cand not in seen:
                    stack.append(cand)
    return sorted(seen)


# ── the census ────────────────────────────────────────────────────────────────────
class Census:
    """The whole reading: registry, per-site fingerprints, decode, residual, groups."""

    def __init__(self, files, sites, seed):
        self.files, self.seed = files, seed
        self.modelled = modelled_keys(seed)
        counts = {}
        for s in sites:
            for t in s[6]:
                counts[t] = counts.get(t, 0) + 1
        self.counts = counts
        # ⚑ DESCENDING FREQUENCY, TIES BY KEY — deterministic, and the reason a residual
        # MAGNITUDE means "rare referents" rather than "walked late".
        self.reg = PrimeRegistry()
        for t in sorted(counts, key=lambda k: (-counts[k], k)):
            self.reg.get_or_assign(t)
        self.known_rev = reverse_index(self.reg, only=self.modelled)
        self.known_primes = [p for p, _k in self.known_rev]
        self.all_primes = sorted(self.reg.primes.values())
        self.rows = []
        for path, line, construct, kind, scope, snip, refs in sites:
            fp = fingerprint(refs, self.reg)
            keys, rem = decode_with_remainder(fp, self.known_rev)
            self.rows.append({
                "path": path, "line": line, "construct": construct, "kind": kind,
                "scope": scope, "snippet": snip, "refs": refs, "fp": fp,
                "known": keys, "rem": rem,
                "omega": omega_against(rem, self.all_primes),
            })

    # -- the monotone metric ------------------------------------------------------
    def total_remainder_omega(self):
        return sum(r["omega"] for r in self.rows)

    def total_remainder_bits(self):
        return sum(r["rem"].bit_length() for r in self.rows)

    def explained_sites(self):
        return sum(1 for r in self.rows if r["rem"] == 1)

    def referent_incidences(self):
        return sum(len(r["refs"]) for r in self.rows)

    def max_fingerprint(self):
        return max((r["fp"] for r in self.rows), default=1)

    def residual_order(self, n):
        return sorted(self.rows, key=lambda r: (-r["rem"].bit_length(), -r["omega"],
                                                r["path"], r["line"]))[:n]

    def explaining_keys(self, n):
        """Which modelled referents are doing the explaining — presence with counts."""
        c = {}
        for r in self.rows:
            for k in set(r["known"]):
                c[k] = c.get(k, 0) + 1
        return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

    # -- the gcd classes ----------------------------------------------------------
    def gcd_classes(self, top, min_omega=2):
        """[(g, Ω(g), [row…])] — sites sharing UNKNOWN structure, ranked by size.

        ⚑ CANDIDATES ARE PAIRWISE gcds AND MEMBERSHIP IS ONE MODULO — nothing is decoded
        to build a class, which is the property that lets two sites be attacked together
        BEFORE either is understood.  A class is kept only if its shared part carries at
        least `min_omega` unmodelled referents: a single shared token is a co-occurrence
        of one thing, and this report is about shared STRUCTURE.

        ⚑ CLASSES WITH IDENTICAL MEMBERSHIP COLLAPSE TO THE LARGEST SHARED PART, so what
        is reported is the MAXIMAL structure those sites share rather than an arbitrary
        divisor of it.  Without this the top of the table is one member-set spelled a
        dozen ways.
        """
        rems = [r["rem"] for r in self.rows]
        cand = set()
        for i in range(len(rems)):
            ri = rems[i]
            if ri == 1:
                continue
            for j in range(i + 1, len(rems)):
                g = math.gcd(ri, rems[j])
                if g > 1:
                    cand.add(g)
        cand = [g for g in cand if omega_against(g, self.all_primes) >= min_omega]
        by_members = {}
        for g in cand:
            members = tuple(i for i, r in enumerate(rems) if fp_contains(r, g))
            prev = by_members.get(members)
            if prev is None or g > prev:
                by_members[members] = g
        out = [(g, omega_against(g, self.all_primes),
                [self.rows[i] for i in members])
               for members, g in by_members.items()]
        out.sort(key=lambda t: (-len(t[2]), -t[1], t[0]))
        return out[:top], len(cand)


def collect(paths, from_entries, kind=None):
    """(files, sites) — the population, and every site in it with its referents."""
    files = local_closure(from_entries) if from_entries else (
        _pycodemod_core.py_files(*paths) if paths else _pycodemod_core.py_files())
    sites = []
    for p in files:
        rel = os.path.relpath(p, _pycodemod_core.ROOT)
        for line, construct, k, scope, snip, refs in site_referents(p):
            if kind and k != kind:
                continue
            sites.append((rel, line, construct, k, scope, snip, refs))
    return files, sites


# ── the report ────────────────────────────────────────────────────────────────────
def _print_monotone(files, sites, seed_paths):
    """The seed LADDER, and the per-site divisibility that makes it a law.

    ⚑ THIS IS A MODE BECAUSE THE ALTERNATIVE IS THE JUDGEMENT HAPPENING IN THE TURN.
    Demonstrating monotonicity by running the census three times and comparing the totals
    by eye is exactly the shape the standing rule forbids: the comparison evaporates when
    the session ends and the next reader re-derives it — differently, or not at all.

    ⚑ AND A FALLING TOTAL IS NOT THE PROOF, WHICH IS THE HALF A LADDER OF NUMBERS WOULD
    MISS.  Two totals can both fall while individual sites move the wrong way (a decoder
    that re-multiplied, a registry that renumbered).  The law is PER SITE — `r' | r` — so
    the ladder checks divisibility site by site at every rung and reports the count of
    violations, which is `0` or the whole claim is void.
    """
    rungs = [([], "the declaration only")]
    for k in range(len(seed_paths)):
        rungs.append((seed_paths[:k + 1],
                      "+ " + os.path.basename(seed_paths[k])))
    base = [os.path.join(_pycodemod_core.ROOT, s) for s in DEFAULT_SEED]
    base = [s for s in base if os.path.isfile(s)]
    prev, viol = None, 0
    print("  ── monotonicity: the seed LADDER (Ω and bits may only FALL) ──")
    print("     %6s %6s %8s  %s" % ("Ω", "bits", "expl", "modelled set"))
    for extra, label in rungs:
        cen = Census(files, sites, base + list(extra))
        print("     %6d %6d %7d%%  %s"
              % (cen.total_remainder_omega(), cen.total_remainder_bits(),
                 round(100.0 * cen.explained_sites() / max(len(cen.rows), 1)), label))
        if prev is not None:
            viol += sum(1 for a, b in zip(prev.rows, cen.rows)
                        if a["rem"] % b["rem"] != 0)
        prev = cen
    print("     ⚑ per-site divisibility r_wider | r_narrower: %d violation(s) over %d "
          "site(s) × %d rung transition(s)" % (viol, len(sites), max(len(rungs) - 1, 0)))
    print("       A FALLING TOTAL IS NOT THE PROOF — two totals can fall while individual")
    print("       sites move the wrong way.  The law is per site, and it is checked here.")
    return viol


def _print_fingerprint(paths, from_entries=(), kind=None, top=10, seed=(),
                       groups=0, keys=0, monotone=False):
    seed_paths = [os.path.join(_pycodemod_core.ROOT, s) for s in DEFAULT_SEED] + \
                 [s if os.path.isabs(s) else os.path.join(_pycodemod_core.ROOT, s) for s in seed]
    seed_paths = [s for s in seed_paths if os.path.isfile(s)]
    files, sites = collect(paths, from_entries, kind)
    if not files:
        print("   ⚑ NO FILES SEARCHED — a fact about the QUERY, not the code.")
        return 0
    cen = Census(files, sites, seed_paths)
    print("  ── population ──")
    print("     files                  %6d" % len(files))
    print("     sites                  %6d%s"
          % (len(cen.rows), ("  (kind=%s)" % kind) if kind else ""))
    print("     distinct referents     %6d   (one prime each)" % len(cen.reg))
    print("     modelled referents     %6d   of which %d occur in a site"
          % (len(cen.modelled), len(cen.known_rev)))
    for s in seed_paths:
        print("       seed  %s" % os.path.relpath(s, _pycodemod_core.ROOT))
    # ⚑ THE POPULATION IS NAMED, NOT JUST COUNTED, WHENEVER IT IS SMALL ENOUGH TO READ.
    # A count alone cannot be checked against a population someone else quoted — "22
    # files" and "24 files" are the same sentence until the two lists are put side by
    # side, and the difference is where a number silently stops being comparable.  The
    # bound is a DISPLAY bound: over it the list is the report's bulk rather than its
    # content, and the per-file split belongs to `--control` anyway.
    if len(files) <= 40:
        per = {}
        for r in cen.rows:
            per[r["path"]] = per.get(r["path"], 0) + 1
        print("     ── the population, named ──")
        for f in files:
            rel = os.path.relpath(f, _pycodemod_core.ROOT)
            print("        %5d  %s" % (per.get(rel, 0), rel))
    inc = cen.referent_incidences()
    unk = cen.total_remainder_omega()
    print("  ── the first reading ──")
    print("     sites fully explained  %6d of %d  (%.1f%%)   remainder == 1"
          % (cen.explained_sites(), len(cen.rows),
             100.0 * cen.explained_sites() / max(len(cen.rows), 1)))
    print("     referent incidences    %6d  of which modelled %d  (%.1f%%)"
          % (inc, inc - unk, 100.0 * (inc - unk) / max(inc, 1)))
    print("  ── the monotone metric (falls only; see the divisibility case) ──")
    print("     TOTAL REMAINDER  Ω     %6d   unmodelled referent-incidences" % unk)
    print("     TOTAL REMAINDER  bits  %6d   Σ bit_length(remainder)"
          % cen.total_remainder_bits())
    mx = cen.max_fingerprint()
    print("  ── magnitude ──")
    print("     max fingerprint        %6d bits  (%d decimal digits)"
          % (mx.bit_length(), len(str(mx))))
    print("     largest prime assigned %6d" % (cen.all_primes[-1] if cen.all_primes
                                               else 0))
    print("     ⚑ squarefree — every exponent is 0 or 1, so an exponent sidecar")
    print("       carries nothing the integer does not.  NOT warranted here.")
    if top:
        print("  ── residual ordering (largest remainder = least understood) ──")
        for r in cen.residual_order(top):
            print("     %5d bits  Ω=%-3d %-12s %-13s %s:%d  (%s)  %s"
                  % (r["rem"].bit_length(), r["omega"], r["kind"], r["construct"],
                     r["path"], r["line"], r["scope"], r["snippet"][:52]))
    if keys:
        print("  ── what the modelled set is explaining (referent → sites) ──")
        for k, n in cen.explaining_keys(keys):
            print("     %-28s %5d" % (k, n))
    if monotone:
        _print_monotone(files, sites,
                        [s for s in seed_paths
                         if os.path.relpath(s, _pycodemod_core.ROOT) not in DEFAULT_SEED])
    if groups:
        classes, ncand = cen.gcd_classes(groups)
        print("  ── gcd classes (sites sharing UNKNOWN structure) ── %d candidate "
              "divisor(s) with Ω>=2" % ncand)
        for g, om, members in classes:
            shared = sorted({t for m in members for t in m["refs"]}
                            - set(cen.modelled))
            common = set(members[0]["refs"])
            for m in members[1:]:
                common &= set(m["refs"])
            print("     ── %d site(s), Ω(gcd)=%d, gcd=%s"
                  % (len(members), om, str(g)[:24] + ("…" if len(str(g)) > 24 else "")))
            print("        shared unmodelled referents: %s"
                  % ", ".join(sorted(common - set(cen.modelled))))
            for m in members[:12]:
                print("        %-13s %s:%d  (%s)  %s"
                      % (m["construct"], m["path"], m["line"], m["scope"],
                         m["snippet"][:48]))
            if len(members) > 12:
                print("        … %d more" % (len(members) - 12))
            del shared
    print("fingerprint: %d site(s) over %d file(s); total remainder Ω=%d bits=%d"
          % (len(cen.rows), len(files), unk, cen.total_remainder_bits()))
    return 0


# ── the cases ─────────────────────────────────────────────────────────────────────
def _cases(check):
    """Guards for the mechanism.  Called from `_pycodemod_selftest._selftest`.

    ⚑ THE CASES LIVE BESIDE THE CODE AND ARE COUNTED BY THE PARENT SUITE.  This module
    has no `__main__` dispatch, so `run_selftests.discover()` does NOT see it as a suite —
    the phantom-suite shape (a docstring mentioning the flag minting a 70th suite) is
    avoided by construction rather than by remembering not to trip it.

    ⚑ BEHAVIOURAL AND SHAPE CASES CATCH DISJOINT CLASSES, so each is labelled with the
    property it holds.  A behavioural case (this input produces that output) cannot see a
    decoder that is right on the fixture and non-exact in general; a shape case (this
    algebraic law holds) cannot see an extractor that returns the wrong tokens.
    """
    # ── SHAPE: identity without taxonomy.  Non-empty is the ONLY validation.
    reg = PrimeRegistry()
    check("registry accepts ANY non-empty key (no taxonomy)",
          [reg.get_or_assign(k) for k in ("if", "3", "ζ", "core_id", "x" * 64)],
          [2, 3, 5, 7, 11])
    check("registry is idempotent on a repeated key",
          reg.get_or_assign("core_id"), 7)
    try:
        reg.get_or_assign("")
        empty = "accepted"
    except ValueError:
        empty = "refused"
    check("an EMPTY key is refused — the one validation", empty, "refused")

    # ── SHAPE: distinct keys get distinct primes; the product is squarefree.
    r2 = PrimeRegistry()
    check("distinct keys → distinct primes",
          len({r2.get_or_assign(k) for k in "abcdef"}), 6)
    check("fingerprint is SQUAREFREE — a repeat adds no factor",
          fingerprint(["a", "b", "a", "a"], r2), fingerprint(["a", "b"], r2))

    # ── BEHAVIOURAL: the decode is EXACT — multiply back and recover the identity.
    r3 = PrimeRegistry()
    fp = fingerprint(["core_id", "relpath", "wobble", "flange"], r3)
    rev = reverse_index(r3, only={"core_id", "relpath"})
    ks, rem = decode_with_remainder(fp, rev)
    prod = 1
    for k in ks:
        prod *= r3.prime_for(k)
    check("decode is EXACT: understood × remainder == fingerprint", prod * rem, fp)
    check("decode returns the understood keys", sorted(ks), ["core_id", "relpath"])
    check("the remainder is the UNMODELLED product",
          rem, r3.prime_for("wobble") * r3.prime_for("flange"))

    # ── BEHAVIOURAL: strict=False is the DEFAULT; the rigid mode is one keyword away.
    # ⚑ THE DEFAULT-STRICTNESS CASE CATCHES ITS OWN MUTANT RATHER THAN CRASHING ON IT.
    # Flipping the default makes this call RAISE, and an unguarded call would abort the
    # whole suite — one mutation turning 241 clean results into a traceback, which reports
    # "the suite is broken" where the truth is "one property regressed".  A guard that
    # takes the run down with it is a worse instrument than one that fails.
    try:
        _lax = sorted(decode(fp, rev))
    except ValueError:
        _lax = "RAISED — strict is no longer the OFF-by-default mode"
    check("strict=False (the default) returns keys and swallows the remainder",
          _lax, ["core_id", "relpath"])
    try:
        decode(fp, rev, strict=True)
        strict = "returned"
    except ValueError:
        strict = "raised"
    check("strict=True raises on an unknown remainder — off by default",
          strict, "raised")
    full = reverse_index(r3)
    check("strict=True with a COMPLETE registry does not raise",
          sorted(decode(fp, full, strict=True)),
          ["core_id", "flange", "relpath", "wobble"])

    # ── SHAPE: the lattice.  gcd is shared structure, % is containment.
    r4 = PrimeRegistry()
    a = fingerprint(["p", "q", "r"], r4)
    b = fingerprint(["q", "r", "s"], r4)
    check("gcd IS the shared referent product",
          fp_shared(a, b), fingerprint(["q", "r"], r4))
    check("containment is ONE modulo — subset",
          fp_contains(a, fingerprint(["p", "q"], r4)), True)
    check("containment is ONE modulo — non-subset",
          fp_contains(a, fingerprint(["p", "s"], r4)), False)
    check("structural difference drops the shared part",
          fp_difference(a, b), fingerprint(["p", "s"], r4))

    # ── SHAPE: MONOTONICITY.  Growing M can only remove factors — r' DIVIDES r.
    r5 = PrimeRegistry()
    fp5 = fingerprint(["aa", "bb", "cc", "dd"], r5)
    _, rem_small = decode_with_remainder(fp5, reverse_index(r5, only={"aa"}))
    _, rem_big = decode_with_remainder(fp5, reverse_index(r5, only={"aa", "bb", "cc"}))
    check("a LARGER modelled set gives a remainder that DIVIDES the smaller one",
          rem_small % rem_big, 0)
    check("the remainder cannot RISE as the modelled set grows",
          rem_big <= rem_small, True)
    check("Ω(remainder) cannot rise either",
          omega_against(rem_big, sorted(r5.primes.values()))
          <= omega_against(rem_small, sorted(r5.primes.values())), True)
    _, rem_none = decode_with_remainder(fp5, reverse_index(r5, only=set()))
    check("an EMPTY modelled set leaves the whole fingerprint as remainder",
          rem_none, fp5)

    # ── BEHAVIOURAL: the referent extractor.  Tokens, not kinds.
    tree = ast.parse('f(row["core_id"], sys.argv, key=lim) or 17')
    got = referents(tree)
    check("referents: names, attributes, keywords and identifier strings",
          sorted(got), ["argv", "core_id", "f", "key", "lim", "row", "sys"])
    check("a NUMERIC constant is not a referent", "17" in got, False)
    check("a non-identifier string is not a referent",
          referents(ast.parse('g("select * from t")')), {"g"})
    check("a dotted string contributes each part",
          sorted(referents(ast.parse('h("a.b")'))), ["a", "b", "h"])
    check("an over-long token is dropped (shape bound, both sides)",
          token_parts("z" * (MAX_TOKEN + 1)), ())

    # ── BEHAVIOURAL: a string literal and an attribute are ONE referent.
    check("`terms` as a string and as an attribute are the SAME referent",
          referents(ast.parse('q("terms")')) & referents(ast.parse('x.terms')),
          {"terms"})

    # ── BEHAVIOURAL: the site walk keeps the governing expression.
    # ⚑ NO FILE IS WRITTEN FOR THIS GROUP.  `site_referents` takes the source text,
    # so the cases below state what they mean directly instead of round-tripping a
    # string through the filesystem to satisfy a signature.  The `filename=` label
    # is still exercised — it is what a parse error and the desync assertion name.
    FIXTURE_SRC = ("def f(rows, lim):\n"
                   "    for r in rows:\n"
                   "        if r['core_id'] and lim:\n"
                   "            return r\n")
    sr = site_referents("fp_fixture.py", src=FIXTURE_SRC)
    byline = {(ln, ctor): refs for ln, ctor, _k, _s, _sn, refs in sr}
    check("a `for` site carries its ITERABLE as a referent",
          "rows" in byline[(2, "for")], True)
    check("an `if` site carries the column string as a referent",
          "core_id" in byline[(3, "if")], True)
    check("the `if` site also carries its bound names",
          {"r", "lim"} <= byline[(3, "if")], True)

    # ── BEHAVIOURAL, END-TO-END: the total remainder FALLS when the seed grows.
    # ⚑ THE TEMPFILE STARTS HERE, AND THIS IS THE HONEST BOUNDARY.  `collect`,
    # `Census` and `local_closure` are POPULATION resolvers: their whole contract is
    # walking the working tree, so a real file is what they are FOR, not a prop
    # standing in for a string.  Only the `site_referents` group above was a
    # signature artefact, and only that group lost its file.  ⚑ SO THIS FILE DOES
    # NOT LEAVE `snapshot-guard`'s census, and that is CORRECT rather than a
    # shortfall: six of the seven write arms are load-bearing fixtures.
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "fp_fixture.py")
    open(p, "w", encoding="utf-8").write(FIXTURE_SRC)
    seed_a = os.path.join(d, "seed_a.py")
    seed_b = os.path.join(d, "seed_b.py")
    open(seed_a, "w", encoding="utf-8").write('T = "core_id"\n')
    open(seed_b, "w", encoding="utf-8").write('T = "core_id"\nU = "rows"\nV = "lim"\n')
    _f, sites = collect([p], (), None)
    ca = Census([p], sites, [seed_a])
    cb = Census([p], sites, [seed_b])
    check("a WIDER seed lowers the total remainder Ω",
          cb.total_remainder_omega() < ca.total_remainder_omega(), True)
    check("a WIDER seed lowers the total remainder bits",
          cb.total_remainder_bits() < ca.total_remainder_bits(), True)
    check("a WIDER seed explains at least as many sites fully",
          cb.explained_sites() >= ca.explained_sites(), True)
    check("every site's remainder DIVIDES its narrower-seed remainder",
          all(x["rem"] % y["rem"] == 0 for x, y in zip(ca.rows, cb.rows)), True)

    # ── SHAPE: the population resolver reaches a transitive local import.
    # ⚑ THE FIXTURE NEEDS A SUBDIRECTORY, AND FINDING THAT OUT IS THE CASE EARNING ITS
    # KEEP.  `_roots()` enumerates DIRECTORIES under ROOT, so files sitting directly in
    # ROOT are in no root at all — a flat fixture makes `py_files()` empty, the name
    # resolver find nothing, and the closure report a population of one WHILE PASSING any
    # assertion phrased as "the entry is in the closure".
    sub = os.path.join(d, "pkg")
    os.makedirs(sub, exist_ok=True)
    m1 = os.path.join(sub, "fp_m1.py")
    m2 = os.path.join(sub, "fp_m2.py")
    m3 = os.path.join(sub, "fp_m3.py")
    m4 = os.path.join(sub, "fp_m4.py")
    open(m1, "w", encoding="utf-8").write("import fp_m2\n")
    open(m2, "w", encoding="utf-8").write("from fp_m3 import z\n")
    open(m3, "w", encoding="utf-8").write("z = 1\n")
    open(m4, "w", encoding="utf-8").write("# imported by nothing\n")
    saved = _pycodemod_core.ROOT
    try:
        _pycodemod_core.ROOT = d
        clo = local_closure([m1])
        check("local_closure follows a TRANSITIVE local import (two hops)",
              sorted(os.path.basename(x) for x in clo),
              ["fp_m1.py", "fp_m2.py", "fp_m3.py"])
        check("local_closure does not drag in an unimported sibling",
              any(os.path.basename(x) == "fp_m4.py" for x in clo), False)
    finally:
        _pycodemod_core.ROOT = saved

    # ── SHAPE: gcd classes group sites that share unknown structure.
    r6 = PrimeRegistry()
    rems = [fingerprint(["u", "v", "w"], r6), fingerprint(["u", "v", "z"], r6),
            fingerprint(["q"], r6)]
    g01 = fp_shared(rems[0], rems[1])
    check("two sites sharing two unknown referents have a gcd of Ω=2",
          omega_against(g01, sorted(r6.primes.values())), 2)
    check("a third site sharing nothing is NOT in the class",
          fp_contains(rems[2], g01), False)
