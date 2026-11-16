# substrate — unfreeze readiness (write-once, 2026-11-16)

Frozen artifact for github-cb's warm then cold review, under the fleet rule at host 695f3e0a
line 176325, uuid a7056eac: "make being caught up on tooling a predicate for unfreeze, with
warm/cold review." This file is not edited after it is sent. Corrections go in a new file.

Evidence was gathered by one read-only subagent and by this session. Labels: [measured] means read
during this session, with the source quoted. [inferred] means a conclusion drawn from measured items.
[not found] gives the method tried. Nothing in this file is recalled.

## 1. The freeze

- **The ruling** [measured]: host line 98633, uuid 0f249f38-4967-44bf-9b0a-ddb37b7cb889,
  2026-10-25T17:39:42Z. The operator: "I'll wake summit. Substrate is a can of worms and we _need_ the
  rest of the ecosystem stable first." The mechanism comes from line 71808, uuid a9ce76fa: work is
  "blocked on an ask for me to unfreeze".
- **Lift condition as stated**: "the rest of the ecosystem stable first". No transcript line
  declares it met. [not found] for the regex `unfreeze|can of worms|ecosystem stable`, beyond the
  lines cited here.
- **substrate's freeze card W342** [measured]: blocked, human, on two things: `operator: decide
  unfreeze substrate for burn-down (unfreeze now / keep frozen)` and W349, the red gate. On
  2026-10-16 the operator said "keep all six frozen". Four cards wait behind W342, all 33 to 36
  days old: W341 (repin to par ca6702b), W340, W339 (bump mtools pins to par a61069e) and W338.
- **Newest operator words** [measured]:
  - Line 176268: "Nemik is thinking about asking for an unfreeze".
  - Line 176303: "it's *substrate*".
  - Line 176325: "I meant it's paperkit … make being caught up on tooling a predicate for unfreeze".
  - [inferred] substrate has not itself asked for an unfreeze. This artifact answers the fleet
    predicate.
- **Is the predicate met? No** [measured].
  - W349 (red commit gate) still holds W342.
  - The bootstrap arc that W349 waits on is landing on branch gate-rebuild. It is not on main. See §5.

## 2. Toolchain model (read now)

- **Pinned bin** [measured]: /home/mikemol/.local/share/luthen-tools/live/nemik/bin/. It resolves
  to by-sha/896263e1….
  - Of the direct_url.json files, 3 of 12 were read. Each gives nemik.git commit
    896263e18243c2f8cee6926ae2ed64d9a4af7660.
  - The vendored mtools wheels carry the suffix +636e39b, except converge, which is +0f8267e.
  - [inferred] The other 9 follow the same pattern.
- **Commit path** [measured]: mikemol-commit modes are single, `--ship`, `--stack FILE`,
  `--stack FILE --freeze-from DIR`, `--withdraw KEY` and `--in-gate [--json]`. A stack is one
  gate run on the tip, and a refusal lands nothing. This session used the stack mode for the
  7-entry arc.
  - Isolation: "path: isolated (the repository's pre-commit names MIKEMOL_REAL_ROOT)".
  - "Round check": [not found] in the usage.
  - Known defects, all reported by this session today:
    - W2581: on a branch it prints `push origin HEAD:main`. This session pushed the branch by name.
    - W2584: a fixed "Claude Sonnet 5.5" trailer, verified at commit_kata.py:168.
    - W2585 (PRIORITY): a path-scoped commit reset the real index. Its output read "refreshed to
      HEAD for 0 committed path(s)". The arc was preserved at refs/preserve/W333-staged-2026-11-16.
- **Watchdog and loop** [measured]:
  - Usage: `mikemol-watchdog --state … [--writer] [--poll-s] [--phi-fire] [--min-fire-s]
    [--max-fire-s]`.
  - The line --tick-open prints is used verbatim.
  - Running this session: restarted after an exit 8 earlier today.
  - Tick hook: nemik-check scoped `--repo substrate`.
- **BES** [measured]:
  - .bazelrc:26-29 sets --remote_cache and --bes_backend to the buildbuddy service names,
    unconditionally, with a hermetic sandbox.
  - The bes-logs skill (~/.claude/skills) still shows a 127.0.0.1:31080 example. [inferred] That
    example is stale.
- **membudget** [measured]:
  - substrate/build_settings.py:37 is `MEMBUDGET = ROOT / "scripts" / "membudget"`, which is still
    the bash client.
  - W331 (the swap to mikemol-membudget) is blocked on luthen-observability:W440 and W349. It
    needs mtools 7ff52eb in the pinned fence.
- **pyproject after the arc** [measured, worktree]:
  - Every mtools package is pinned at mtools.git@03749d56.
  - paperkit is pinned `@main`. [inferred] An unpinned ref.
  - MODULE.bazel pins mikemol_rules_py at 370784d5 with `remote = "/home/mikemol/github/mtools"`.
  - [inferred] **substrate is BEHIND**: its pins (03749d56) are neither the pinned install (mtools
    636e39b, via nemik 896263e) nor the par targets W339/W341 name (a61069e, ca6702b).

## 3. Standing fleet directives held

All quotes are from the host transcript, operator lines [measured], unless the loop prompt is named.

| Directive | Warrant | substrate's standing |
|---|---|---|
| No wall-clock stops | L53578 f71b642c; loop prompt L18 | [measured] this session used background runs, not timeouts, for gates |
| cputime for safety stops | L175192 21748591 ("we use cputime for that kind of safety stop") | not yet applied anywhere in substrate [inferred] |
| Decompose, not shard | L169764 03321de3 | loop prompt L25-26 still says "sharded" [inferred: lags] |
| Named inputs | [not found] in transcript (regex `named inputs?`); BUILD.bazel:5-6 cites operator 2026-10-06 | BUILD.bazel complies for its one target |
| No Optional results | L170448 cfd3d291 | not audited |
| No sibling paths | L84035 67efb1bc | **VIOLATED** [inferred]: MODULE.bazel `remote = "/home/mikemol/github/mtools"`; generated makefiles hard-code SHIM_DIR into the live repo (gate-closure G2) |
| Load-agnostic | L94782 7e652e09 | not audited |
| Flakes block | loop prompt L27 → L99701 f11d04b8, L100099 | — |
| Gate-repair tagging | [not found] (3 regexes); loop prompt L36 nearest | — |
| No riding | [not found] (2 regexes) | — |
| Review before land | [not found] as phrased; nearest L161970 417ef966, L168330 7db84ac9 (warm/cold, not operator sign-off) | today's gate work was reviewed by github-cb before each land |
| Reviewed loop | loop prompt L31 → L112940 7e40501f, L107593 | substrate's own warm reviewer was not re-seeded after compaction [measured: none resumed this session]; github-cb ran warm/cold instead |
| Loop prompt L8-42 | ~/github/.claude/loop-prompt.md | read in full this session; one line each in the gathering report |
| Precommit is bazel | L7952 a2eeb295, L7980 e59280fa ("is a blocker for that repo"), L19653 d94430df | **NOT MET** [measured]: .githooks/pre-commit never calls bazel; BUILD.bazel has 1 py_test (check_makefiles) in `test_suite precommit` against about 35 bash gates |

## 4. Queue health [measured]

- `--check`: "OK — 353 of 353 symbols resolve". There are 64 UNSCORED cards.
- Working cards: 0, so the vector check is vacuous. `--working-stale`: none.
- Ready: 3. Inbound: empty. Standing rules: 2.
- nemik-check --warnings --repo substrate:
  - The last completed run was at tick 4's open: "OK substrate", with warnings for unwarranted
    rulings on W9, W10, W23, W26, W322 and W333, and W333's missing operator-act command.
  - The gathering run hit the 120 s foreground limit. [measured] slowness, filed with github-cb.
- "The round": [not found]. No read mode reports it.
- Tool defect: `mikemol-transcriptstruct --rulings` raises KeyError '@id' at rulingq.py:51.

## 5. First moves after an unfreeze, and how they avoid churning the fleet

The arc stays on the branch until it is green, so main never carries a red tree another repo could
inherit:

1. Finish the gate rebuild on branch gate-rebuild (W352).
   - The 7-entry bootstrap stack is landing there now.
   - The gate then runs on a consistent tree, and W352's inventory comes from its real
     failures, with aim, goal and incident recorded for each.
   - Nothing reaches main except through mtools:W2582's guard: the original gate, 771283c's
     pinned closure, must be green on the merge tree.
2. Repin to par: W339 and W341 bump the mtools pins to the fleet par sha.
   - [inferred] This only consumes. Other repos depend on substrate's published scripts by
     symlink, and those are not moved by a repin.
3. Pay down the sibling-path and precommit-is-bazel debts as W352 rows. The sibling-path debt is
   the MODULE.bazel remote and the SHIM_DIR path.
4. Anything another repo adopts goes through the census-kit and symlink census first. That rule
   is memory feedback_census_symlinks_before_deleting_scripts: 13 repos were once blocked by a
   delete in scripts/.

What substrate does NOT do on an unfreeze:
- push to main;
- change scripts/ files other repos symlink, without that census;
- open new cross-repo asks beyond the three already carded with mtools (W2581, W2584, W2585)
  and W2582.

**Verdict, self-assessed** [inferred]: **not caught up.**
- The pins are behind par.
- Precommit-is-bazel is not met.
- The sibling-path rule is violated.
- The gate is red on main.
- substrate's own warm reviewer is not running.

An unfreeze ask would be premature until W352 and the repin land. What substrate can do while
frozen is the branch-local work that the operator's 2026-11-16 ruling already permits.

---

## REV 1: after github-cb's warm review (2026-11-16)

The warm review agreed with the verdict. No cold review was run, because no claim of readiness is
made. This section corrects §3 and §5. Nothing above it is rewritten.

- **Warrants for §3** [relayed by github-cb, not re-verified here]:
  - "No riding" and "gate-repair is a true tag" are not operator transcript rows. They are host
    rulings from 2026-11-16, recorded as nemik:W2212 and nemik:W2213 (mtools b72).
  - "Named inputs, never globbed" is the operator's ruling of 2026-10-06, as recorded in host
    memory, where it corrected aeternum's first BUILD. No transcript row was recovered for it.
- **Each gap becomes a card on the path to readiness.** The next revision should be able to mark
  each one closed and measured:
  1. Repin to the fleet pin, read from the live direct_url.json at the time of the repin. Today
     that pin is mtools 636e39b via nemik 896263e. Card W339 is re-pointed at it.
  2. Sibling paths become pinned fetches: the MODULE.bazel `remote` and the SHIM_DIR hard-coded
     into the generated makefiles. New card.
  3. Precommit-is-bazel is W352's rebuild itself.
  4. Re-seed substrate's persistent warm reviewer. This is being done now.
- The `mikemol-transcriptstruct --rulings` KeyError has been reported to mtools.
