# Gate rebuild on a feature branch — plan for review (W353, W352)

Operator ruling, 2026-11-16 (substrate-a5 transcript): "Switch to a feature branch and rebuild the
commit gate from the ground up, tracking it's aims and goals. Permit committing to feature branches.
Don't permit merging to main until the original commit gate would be green on the merge commit."
Then: "Use the warm/cold reviewer process with the GitHub session to perform the steps of these properly."

State at writing: HEAD 771283c on main; 7035 staged paths (bootstrap arc W332/W333) never committed;
a whole-arc probe commit (mikemol-commit --stack) is in flight; its first gated run was refused at
⟡census-sync (sql census + tool-mode census stale), both re-synced in the real tree and restaged.

## W353 — guard main (lands first)

1. After the probe exits: `git switch -c gate-rebuild` (the staged index carries over).
2. Freeze the ORIGINAL gate: `.githooks/gate-original` = HEAD 771283c's `.githooks/pre-commit`,
   byte-identical (blob sha recorded on W353). It is never edited afterwards.
3. `.githooks/reference-transaction`: on the `prepared` phase, for any update of `refs/heads/main`,
   refuse unless the new tip's TREE has a green gate-original verdict in a verdict ledger keyed by
   tree sha. Covers fast-forward merges, which fire no commit hook.
4. Verdicts are produced by running gate-original against a snapshot of the candidate merge tree
   (mikemol-commit's isolated path, MIKEMOL_REAL_ROOT), never by hand.
5. `.githooks/pre-commit` off main: runs, records its verdict, exits 0 (commits permitted).
   On main: unchanged blocking behaviour.

Open questions for review:
- Q1. Does mikemol-commit / post-commit / pre-push assume main (auto-push, marker check)? A branch
  commit must not push to main or fail post-commit.
- Q2. Is reference-transaction the right enforcement layer, or does mtools own an equivalent
  (fence / gate-ledger / presubmit) that should carry it instead (substrate defers to mtools)?
- Q3. "green on the merge commit": verdict keyed by tree sha is sufficient iff gate-original is a
  pure function of the tree plus host state; it is not (venv, postgres, ledgers). Record host
  fingerprint with the verdict?

## W352 — rebuild the gate, tracking aims

1. Inventory: every gate in gate-original (name, phase, statistic, baseline, blocking/advisory),
   derived by the gate-oracle, not by hand.
2. For each: its AIM (what failure it exists to stop, with the incident/ruling that motivated it)
   and GOAL (the measurable state it drives toward). Unrecoverable aims are recorded as UNKNOWN.
3. Rebuilt gate: each check carries its aim/goal as data; target structure is bazel (hermetic
   checks as cached test targets; postgres ingest + query orchestration as tagged non-hermetic).
4. Nothing dropped silently: a gate not carried forward goes to residue with its aim.

Done-witness for the whole arc: gate-original green on a merge commit of gate-rebuild into main.

---

## REV 1 — after warm + cold review (github-cb, 2026-11-16; cold verdict REVISE)

Sources: warm review W0–W5 (recorded on W353 evidence); cold review JSON
/var/tmp/claude-1000/-home-mikemol-github/695f3e0a-d36f-4080-9c67-7548978cd99e/scratchpad/cold-substrate-gate.json
(github-cb scratchpad: to be cited by git blob sha on W353 once copied, not by path).

Changes to the plan above (the original text is kept as written; this section supersedes it where they differ):

- R1 (BLOCKING, replaces W353 step 2). "The original gate" = 771283c's WHOLE gate closure: the
  pre-commit driver plus every check it reaches ($ROOT/scripts, $ROOT/jea, substrate.*, in-tree
  baselines, gate_ledger.py). The file list is derived by the gate-oracle from the hook, never by
  hand, and pinned at 771283c (a worktree or archive at that sha, not files in the branch). It runs
  against the candidate merge tree as DATA, so a branch edit to any check cannot change the verdict.
- R2 (answers Q1). post-commit never pushes and pre-push.local is branch-agnostic. mikemol-commit
  assumes main: it reads origin/main and prints `push origin HEAD:main` for any commit not yet on
  the remote main. On gate-rebuild that printed line is NEVER followed; branch pushes name the
  branch explicitly. github-cb is carding the defect with mtools.
- R3 (answers Q2; replaces W353 steps 3–4). No substrate reference-transaction hook. The main guard
  belongs in mtools, reading mtools' own tree-keyed record (the Gated-Tree: trailer; whether
  .git/mtools/gate-verdicts.jsonl or the trailer is the authority gets asked of mtools). Action:
  an ask to mtools citing W353; W353 is blocked on that mtools card once it is minted.
- R4 (answers Q3; replaces W3's "host fingerprint"). Verdict key = (tree sha, frozen gate-closure
  sha, venv lock sha, schema version). An update of main is admitted only on a FRESH green run of
  the frozen closure on that merge tree at merge time; a stored verdict is evidence, never admission.
- R5 (new risks).
  - core.hooksPath runs the checked-out branch's own hooks, so the guard must not live in any file
    the branch can edit (another reason it lives in mtools, per R3).
  - A ref guard could block mikemol-commit's own landings on main; the guard is designed with mtools
    so its landing path is the admitted one.
  - CLAUDE.md's commit policy ("work and commit directly on main") is amended in the SAME change
    that lands the guard, per the operator's 2026-11-16 ruling; not before.
- W0. Both operator rulings are warranted on W352 and W353 by transcript line and uuid before any
  build step.
- W4. gate-original is expected RED on main until the bootstrap arc's content is in the merge tree;
  W353 says so, so the red is not read as a guard malfunction.
- W5 (W352). Each gate's aim/goal row cites its incident or ruling (line, uuid or card), or UNKNOWN.

Revised order: W0 warrants → gate-oracle derives the closure (R1) → ask mtools for the main guard
(R3/R4/R5) → switch to gate-rebuild and make pre-commit advisory off main → W352 inventory.
Branch switching still waits for the in-flight probe to exit.
