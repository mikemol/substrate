#!/usr/bin/env python3
"""reuse_tui.py — a TUI browser over the interned SPPF (the whole agglomerated structural space).

Navigate the SHARED SUBTREES — every canonical node with fanin ≥ 2 is duplicated structure = a
consolidation opportunity (N instances of one pattern → parameterize; fanin = instances = the win).
Ranked by impact (fanin × size). Select one to see its instances (the units that share it), its head,
what it contains, and pick which instance is canonical.

  scripts/reuse_tui.py --build     # intern the forest (~90s) → cache (do once)
  scripts/reuse_tui.py             # load cache, launch the curses browser

Keys:  ↑/↓ k/j  move   PgUp/PgDn  page   /  filter by head   s  cycle sort (impact/size/fanin)
       f  cycle min-fanin   Enter  toggle full instance list   q  quit
"""
import sys, os, json, argparse, glob, curses

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGDA = os.path.join(REPO, "agda")
CACHE = os.path.join(REPO, "scratch", "generated", "sppf_index.json")

# --------------------------------------------------------------------------- build
def build(cache_path, min_size, min_fanin, cap):
    sys.path.insert(0, os.path.join(REPO, "jea", "metalanguage"))
    import jea_pysim as J, typeholer_path as tp
    cores = sorted(glob.glob(os.path.join(AGDA, "_build", "**", "agda", "Substrate", "**", "*.agdai"),
                             recursive=True))
    print(f"interning {len(cores)} cores …", flush=True)
    C = J.Corpus()
    for c in cores:
        try: C.add_agdai(c)
        except Exception: pass
    print(f"{len(C.units)} units; extracting shared subtrees (min_size≥{min_size}, min_fanin≥{min_fanin}) …",
          flush=True)
    cands = tp.extract_cands(C, min_fanin=min_fanin, min_size=min_size)
    cands.sort(key=lambda c: -(c.units * c.size))
    keep = cands[:cap]
    print(f"{len(cands)} candidates; containment tower on the top {min(len(keep), cap)} …", flush=True)
    direct, rung, _ = tp.containment_dag(keep)
    by_nid = {c.nid: c for c in keep}
    rows = []
    for c in keep:
        insts = sorted({C.units[i].name for i in c.unit_ids})
        contains = sorted({tp._head_str(by_nid[b].head) for b in direct.get(c.nid, []) if b in by_nid})
        rows.append({"fanin": c.units, "size": c.size, "head": tp._head_str(c.head),
                     "rung": rung.get(c.nid, 0), "contains": contains, "instances": insts})
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    json.dump({"rows": rows, "units": len(C.units), "cores": len(cores),
               "n_candidates": len(cands)}, open(cache_path, "w"))
    print(f"✓ cached {len(rows)} shared subtrees → {cache_path}")

# --------------------------------------------------------------------------- browser
SORTS = [("impact", lambda r: -(r["fanin"] * r["size"])), ("size", lambda r: -r["size"]),
         ("fanin", lambda r: -r["fanin"]), ("rung", lambda r: -r["rung"])]

def browser(stdscr, allrows, meta):
    curses.curs_set(0)
    curses.use_default_colors()
    for i in range(1, 6):
        try: curses.init_pair(i, i, -1)
        except curses.error: pass

    def sa(y, x, s, n, a=0):                                       # safe add: curses raises at the corner cell
        try: stdscr.addnstr(y, x, s, max(0, n), a)
        except curses.error: pass
    filt, sort_i, min_fanin, expand = "", 0, 2, False
    idx = off = 0

    def view():
        rows = [r for r in allrows if r["fanin"] >= min_fanin and (not filt or filt.lower() in r["head"].lower())]
        rows.sort(key=SORTS[sort_i][1])
        return rows

    rows = view()
    while True:
        h, w = stdscr.getmaxyx()
        listw = max(40, w * 55 // 100)
        stdscr.erase()
        title = (f" SPPF reuse browser — {len(rows)}/{len(allrows)} shared subtrees "
                 f"| {meta['units']} units, {meta['cores']} cores "
                 f"| sort:{SORTS[sort_i][0]} fanin≥{min_fanin} filt:'{filt}' ")
        sa(0, 0, title.ljust(w), w - 1, curses.A_REVERSE)
        rows = view()
        if idx >= len(rows): idx = max(0, len(rows) - 1)
        if idx < off: off = idx
        if idx >= off + h - 3: off = idx - (h - 4)
        # list pane
        for i in range(off, min(len(rows), off + h - 3)):
            r = rows[i]; y = i - off + 1
            line = f"{r['fanin']:>4}× s{r['size']:<3} r{r['rung']:<2} {r['head']}"
            attr = curses.A_REVERSE if i == idx else curses.color_pair((r['size'] % 5) + 1)
            sa(y, 0, line.ljust(listw - 1)[:listw - 1], listw - 1, attr)
        for y in range(1, h - 2):
            try: stdscr.addch(y, listw, curses.ACS_VLINE)
            except curses.error: pass
        # detail pane
        if rows:
            r = rows[idx]; dx = listw + 2; dw = w - dx - 1; dy = 1
            def put(s, a=0):
                nonlocal dy
                if dy < h - 2: sa(dy, dx, s[:dw], dw, a); dy += 1
            put(r["head"], curses.A_BOLD)
            put(f"{r['fanin']} instances · size {r['size']} · rung {r['rung']} · impact {r['fanin']*r['size']}")
            if r["contains"]:
                put("⊃ contains: " + ", ".join(r["contains"])[:dw], curses.color_pair(3))
            put("")
            put(f"instances (canonical = topmost by module depth):", curses.A_UNDERLINE)
            insts = sorted(r["instances"], key=lambda n: (n.count("."), n))
            shown = insts if expand else insts[:h - dy - 2]
            for n in shown:
                put("  " + n)
            if not expand and len(insts) > len(shown):
                put(f"  … (+{len(insts)-len(shown)}; Enter to expand)")
        sa(h - 1, 0, " ↑↓/jk move  PgUp/Dn page  / filter  s sort  f fanin  Enter expand  q quit ".ljust(w), w - 1, curses.A_REVERSE)
        stdscr.refresh()

        c = stdscr.getch()
        if c in (ord("q"), 27): break
        elif c in (curses.KEY_DOWN, ord("j")): idx = min(len(rows) - 1, idx + 1)
        elif c in (curses.KEY_UP, ord("k")): idx = max(0, idx - 1)
        elif c == curses.KEY_NPAGE: idx = min(len(rows) - 1, idx + (h - 4))
        elif c == curses.KEY_PPAGE: idx = max(0, idx - (h - 4))
        elif c in (curses.KEY_ENTER, 10, 13): expand = not expand
        elif c == ord("s"): sort_i = (sort_i + 1) % len(SORTS); idx = 0
        elif c == ord("f"): min_fanin = 2 if min_fanin >= 8 else min_fanin + (2 if min_fanin > 1 else 1); idx = 0
        elif c == ord("/"):
            curses.curs_set(1); curses.echo()
            stdscr.addnstr(h - 1, 0, "filter: ".ljust(w), w)
            try: filt = stdscr.getstr(h - 1, 8, 40).decode("utf-8", "replace").strip()
            except Exception: filt = ""
            curses.noecho(); curses.curs_set(0); idx = 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--min-fanin", type=int, default=2)
    ap.add_argument("--cap", type=int, default=12000, help="max candidates to keep (by impact)")
    args = ap.parse_args()
    if args.build:
        build(args.cache, args.min_size, args.min_fanin, args.cap); return
    if not os.path.exists(args.cache):
        print(f"no cache at {args.cache} — run:  scripts/reuse_tui.py --build"); return
    data = json.load(open(args.cache))
    curses.wrapper(browser, data["rows"], data)

if __name__ == "__main__":
    main()
