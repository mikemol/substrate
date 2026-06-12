"""
brick-schedule.py — the Čech reading protocol (S29, author method).

A document is read as a DYADIC OVERLAPPING COVER, in this order:
  1. H1  [0, 1/2)      first half
  2. H2  [1/2, 1]      second half
  3. Q1  [0, 1/4)      first quarter
  4. M   [1/4, 3/4)    middle half
  5. Q4  [3/4, 1]      last quarter
  6. A   [0, 3/4)      first quarter + middle half   (gluing pass)
  7. B   [1/4, 1]      middle half + last quarter    (gluing pass)
  8. A'  [0, 3/4)      first three-quarters          (gluing pass)
  9. B'  [1/4, 1]      last three-quarters           (gluing pass)

Per brick, capture insights TYPED: ACT (actionable now), OBL (obligation
queued), GLU (overlap agreement), COC (overlap CONFLICT — a cocycle: the
document's meaning depends on entry context; a finding, not an error).
Every cut point (1/4, 1/2, 3/4) is interior to some brick: no seam is
only a seam. Commit per brick: a context flush between bricks severs
nothing — the ledger holds the sections, the next brick re-covers the
boundary. Acquisition discipline for remote docs: fetch once -> save
verbatim to disk -> commit; digest from disk in bricks across sessions.

Usage: python3 tools/brick-schedule.py <file> [--init]
Prints the line-range schedule; --init writes reading-ledgers/<name>.bricks.
"""
import sys, os, io
f = sys.argv[1]
L = sum(1 for _ in io.open(f, encoding='utf-8', errors='replace'))
q = lambda x: max(1, int(round(x*L)))
S = [("H1", 1, q(.5)), ("H2", q(.5)+1, L), ("Q1", 1, q(.25)),
     ("M", q(.25)+1, q(.75)), ("Q4", q(.75)+1, L),
     ("A", 1, q(.75)), ("B", q(.25)+1, L), ("A2", 1, q(.75)), ("B2", q(.25)+1, L)]
print(f"{f}: {L} lines; brick schedule (sed -n 'a,bp'):")
for n, a, b in S: print(f"  {n:3s} lines {a}-{b}  ({b-a+1} lines)")
if "--init" in sys.argv:
    os.makedirs("reading-ledgers", exist_ok=True)
    p = "reading-ledgers/" + os.path.basename(f) + ".bricks"
    if not os.path.exists(p):
        io.open(p, "w", encoding='utf-8').write(
            f"# brick ledger: {f} ({L} lines)\n# states: PENDING/DONE; append insights as ACT:/OBL:/GLU:/COC: lines under each brick\n"
            + "".join(f"{n} {a}-{b} PENDING\n" for n, a, b in S))
        print(f"ledger initialized: {p}")
    else:
        print(f"ledger exists: {p}")
