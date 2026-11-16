# External review — `scratch/agda_defs.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured. Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24).

⚑ **THE REVIEW ENDS WITH A DIRECT QUESTION TO THE AUTHOR** (regex state machine vs. a
real lexer / parser combinator). It is answered at the end of this file — as an OPEN
design question with a measured floor under it, NOT as a settled verdict.

---

Here is an analysis of your script, broken down into general thoughts on the design, specific opinions on the architecture, and technical concerns regarding edge cases.

### Thoughts: The Context & Design

This is a highly pragmatic, battle-hardened script. The extensive `⚑` comments tell a story of a tool that has evolved through painful encounters with Agda’s notoriously complex lexer and edge cases in dependency pruning.

* **The War Stories:** The documentation of exactly *why* a specific regex or filter exists (e.g., the `[]` bracket-mixfix drop causing a tree-wide `[NotInScope]`) is excellent. It turns "magic" regexes into documented constraints.
* **The "Rewire Only" Fix:** Including the source-code introspection in `_selftest()` to ensure the CLI remains reachable (`_src.count("provides(mod)") >= 1`) is unorthodox but deeply practical. It mechanically prevents the tool from degrading back into an unreachable library.

### Opinions: Architecture & Approaches

* **The Regex Approach vs. Structural Parsing:** Parsing Agda with line-by-line regex is inherently fragile due to mixfix operators, unicode, and indentation sensitivity. However, for a dependency indexer, building a full AST is usually overkill and too slow. Your approach of maintaining a lightweight state machine (`in_data`, `in_module`, `in_opaque`) based on indentation is the right compromise, provided the guardrails hold.
* **LRU Cache:** `@functools.lru_cache(maxsize=1)` on `def_index()` is perfectly applied here. It allows the script to be imported by other Python tools in your pipeline and queried thousands of times without re-walking the tree, while keeping the CLI fast.
* **The Name List Filter (`_namelist`):** The keep-biased logic (`if len(names)==1: return names`) is a clever escape hatch for single-token names like `[]` or `[_]` that look like types to your filter. It acknowledges that ambiguity only truly exists in *multi-token* sequences.

### Concerns: Edge Cases & Blind Spots

**1. File Encoding Masking Errors**

```python
for l in open(p, errors="replace"):
```

Agda files are strictly UTF-8 and frequently use complex Unicode math symbols. Using `errors="replace"` will silently convert decoding failures into the ` replacement character. If an operator containing a unique Unicode character gets mangled here, it will be indexed as ` and fail to resolve when queried by the real Unicode name.

* **Fix:** Use `open(p, encoding="utf-8")`. If there is a decoding error, you *want* the script to fail loudly so you can fix the file, rather than quietly dropping provisions.

**2. Multi-line and Inline Comments**

```python
if not l.strip() or l.lstrip().startswith("--"): continue
```

This handles blank lines and full-line comments perfectly. However, it completely ignores Agda's block comments (`{- ... -}`) and inline comments (e.g., `data List : Set where -- the list type`).

* If a block comment spans multiple lines and its contents happen to match your `multi-name` regex, it will be indexed as a provision.
* If an inline comment contains a colon (e.g., `-- note: important`), it could trick the regexes that look for `:` as a boundary.

**3. State Machine Reset Timing**
The logic to exit a block is:

```python
if l and not l[0].isspace(): in_data=False; in_module=False; in_opaque=False
```

Because this sits at the *bottom* of the loop, and you `continue` early for blank lines and `--` comments, a top-level comment directly following an indented `data` block will correctly *not* reset the state. However, if a top-level block comment `{- ... -}` appears, it isn't caught by the `startswith("--")` check. The script will see `{-` at column 0, trigger this reset, and incorrectly close the `in_data` state, potentially missing constructors that resume below it.

**4. The `_IDENT` Blacklist Brittleness**

```python
_IDENT=re.compile(r"[^\s:()@{}→←⊔⟨⟩\[\],;=|]+")
```

Agda's lexer is famously permissive. By using a blacklist, you are in a perpetual game of whack-a-mole with characters that indicate a type rather than a name. For instance, string delimiters (`"`), dot patterns (`.`), or implicit argument braces (`{}`) aren't fully accounted for in all edge cases. While this works for the `Substrate` codebase currently, it is structurally fragile.

---

Given your previous note that faced with an either/or fork, the answer is to look for the structural correspondence recursively: Do you think there is a way to structurally adapt Agda's actual lexer or a simplified parser combinator here to replace the regex state machine entirely, or is the performance penalty not worth the accuracy gain for this specific indexing tool?

---

## Reading, for the unification planning

### ⚑ CONCERNS 2 AND 3 ARE THE HIGHEST-STAKES FINDING IN ANY OF THE SIX REVIEWS

`agda_defs` is the **name→home authority that 19 importing tools resolve through**
(measured, §48/§53). A wrong answer here does not fail loudly — it propagates as a
wrong import, a wrong rename target, or a wrong "no owner found". This repo has already
paid for exactly that twice:

  * §41: `_namelist` dropped every bracket-mixfix constructor, so **`def_index()["[]"]`
    was EMPTY TREE-WIDE**; the splitter emitted a leaf with no import of
    `Foundation.List` and it failed `[NotInScope] []`. The filter's own docstring
    asserted this could not happen.
  * §27: `fix_stale_using.owner()` resolved through a raw-text regex and named a
    module `def_index` does not record as a home at all — **39 sites**, fixed only by
    routing through `def_index`.

**So the pattern is established: when `agda_defs` is blind, the blindness ships as a
broken edit somewhere else.** The reviewer is naming two more blind spots of exactly
that kind.

⚑ **AND CONCERN 2 IS A CLASS THIS REPO HAS FIXED IN FOUR OTHER TOOLS AND APPARENTLY
NOT HERE.** `agda_lex.mask_comments` is THE comment authority — it handles NESTED
`{- -}` blocks and knows `-->` is a name. It was adopted into `set1_motif` (§20, where
`re.sub(r"--.*$")` counted a block-commented `record … Set₁` as live), into
`split_lemmas` (§37, where a `-----` banner parsed as a definition named `--`), and
`check_carrier_locality.strip_comments` was measured behaviourally identical to it on
**all 2764 files** (§9f). §9f also recorded that **32 tools still scan unmasked,
including `agda_defs`** — with the note *"inconsistency, no measured wrong answer"*.

**The reviewer is proposing the measured wrong answer that note lacked.** A block
comment containing a `name : Type` line would be indexed as a provision; a `{-` at
column 0 would reset `in_data` and drop the constructors after it. ⚑ **UNVERIFIED —
neither has been demonstrated on the live corpus, and §9f's "no measured wrong answer"
may still hold.** But the right response to a hypothesis with a named mechanism is to
run it, not to re-assert the note.

**Cheap, decisive probe:** compare `def_index()` built as-is against one built over
`mask_comments`-filtered text, and diff the name→home maps. That is the same
build-it-both-ways method that settled §7b (rank-1 was 115 under BOTH regexes — a
sound argument that happened not to bind) and §6a (8 missing build edges, real). **It
can only return a fact, and either fact is worth having.**

### Concern 1 — `errors="replace"` — is the ABSENT-DEPENDENCY CLASS wearing a decoder's clothes

A decode failure silently becomes `�`, and the name indexes under a spelling
nobody will ever query. **That is "an unmeasured thing scoring as a measured one"** —
ruled against three times already in this repo (`jea_circuit` returning `True` on
`SKIP (numpy absent)`; `mdstruct` reporting `0/0` and PASSING with pandoc missing;
`dagcone`'s broad `except Exception` on the networkx import, in
[review-dagcone.md](review-dagcone.md)).

The reviewer's fix — fail loudly — is the repo's own rule (*an incomplete census is
not a low count*, Guard (2)). ⚑ **Severity is UNMEASURED and probably low**: the corpus
is machine-written UTF-8, so a decode failure may be genuinely impossible today. But
"impossible today" is the condition under which a silent fallback is most dangerous,
because nothing exercises it and its first firing is invisible.

### Concern 4 — the blacklist — is REAL AND ALREADY HALF-ANSWERED, and the answer is a shared authority

`_IDENT` as a blacklist is whack-a-mole, exactly as the reviewer says. But the repo
already built the positive form for the adjacent question: **`agda_lex.word` is THE
name-boundary authority**, created because `\b` is a `\w` transition and an Agda name
may be entirely non-`\w` (`∙`, `⊥`), contain `-` (`×-bij`), or end in a symbol (`∣G∣`)
— measured at **1269 of 10831 names (11.7%) invisible to `\b`** (§14).

⚑ **AND THIS IS THE FOURTH SIGHTING TODAY OF ONE CLASS.** `--attr`/`--discards` keying
by bare name (T20, corroborated in [review-pycodemod.md](review-pycodemod.md));
`def_index` merging `_-ℤ_` and `-ℤ_` under bare `-ℤ`, MANUFACTURING a collision the
language does not have (§22); `bibstruct.mentions()` needing hyphen-safe boundaries
(see [review-bibstruct.md](review-bibstruct.md)); now `_IDENT`. **A bare name is not a
decidable unit — in Python, in Agda, and in BibTeX keys**, and the tokenizer is the
layer where that gets decided once.

Live worklist correspondence: **R4 — "CENTRALIZE ALL NAME INTERPRETATION"**, §29's
standing point, which already SUBSUMES T1 and T7. The reviewer has independently
argued its motivation from a fourth direction.

### ⚑ THE REVIEWER'S CLOSING QUESTION — answered as OPEN, with the fork DISSOLVED first

*"Adapt Agda's actual lexer / a parser combinator to replace the regex state machine,
or is the performance penalty not worth the accuracy gain?"*

**The either/or should be collapsed before it is answered, and this repo has the
material to do it — `agda_defs` is not the only reader of this corpus.**

  * `agda_lex` already owns the LEXICAL layer as a real span authority — `statements`,
    `_continues`, `_depth_after`, `mask_comments`, `head_span`, `module_scopes`,
    `binds_at`, `span_end`, `telescope_groups`, `word`. That is not a regex pile; it is
    an indentation-and-span model with a positional scope walk.
  * **`agda_defs` is DELIBERATELY NOT part of it** — `agda_lex.py:24-29` records that
    `def_index` is a per-line state machine, not a statement iterator, and that folding
    it inward is a documented trap. §6c moved CALLERS inward instead.
  * **And a THIRD reader already exists and is authoritative: the `.agdai` CORES.**
    `catalog.db` is populated from typechecked cores via the `agdai_shim`, which is
    Agda's own elaborated output — no parsing of surface syntax at all. §8 measured it
    covering **842 of 2762 cores (~30%)**, which is why it is not the everyday
    instrument.

So the real space is not *regex vs lexer*. It is **which layer answers which question,
and what does each layer's blindness cost** — a graded division of labour, the same
shape as `bibstruct`'s engine-truth vs file-truth. A core-derived index is
authoritative and incomplete; a lexical index is complete and approximate; the
question is where each is load-bearing.

⚑ **I am NOT answering it here, and the reason is a rule this arc earned.** Answering
"is the accuracy gain worth it" requires knowing what the current accuracy IS, and
that is exactly the unmeasured quantity concern 2 names. **Measure the
mask_comments diff first**; if it is empty, §9f's note stands and the state machine is
sound in practice. If it is not, the size of the diff sizes the rewrite. Declaring a
verdict before that measurement would be the wall-declaration reflex — and §30 is the
cautionary case: I declared "fixity does not cross the parameter boundary" a genuinely
new class, and the measured population was **ZERO**.

### What this review does NOT cover

The reviewer did not exercise `def_index` against the live tree, did not see `R5`
(*"`def_index` still indexes NON-definitions"* — `variable`, `private`, and `_` with
**200 homes**, already filed), and did not comment on the CLI added in §53 (`<name>` /
`--provides <Mod>`). Silence there is scope, not a pass.
