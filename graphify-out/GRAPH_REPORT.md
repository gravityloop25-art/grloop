# Graph Report - grloop  (2026-11-15)

## Corpus Check
- 29 files · ~25,739 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 3, .example 1, .webmanifest 1)

## Summary
- 271 nodes · 723 edges · 23 communities (21 shown, 2 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 22 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f0672602`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.js
- app.js
- package.json
- font
- random
- gv.py
- demo.js
- common.py
- hit.py
- gb.py
- wl.py
- mux
- gearpl.py
- tu.py
- pil
- cd.py
- ls.py
- plinko.py
- rb.py
- compose
- math
- Sky
- Writer

## God Nodes (most connected - your core abstractions)
1. `make_audio()` - 27 edges
2. `Writer` - 22 edges
3. `compose()` - 21 edges
4. `mux()` - 20 edges
5. `font()` - 19 edges
6. `lerp()` - 16 edges
7. `renderPlan()` - 15 edges
8. `openVideo()` - 11 edges
9. `getKV()` - 10 edges
10. `overview()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `draw()` --calls--> `compose()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `font()`  [EXTRACTED]
  code/bk.py → code/common.py
- `draw()` --calls--> `lerp()`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `make_audio()`  [EXTRACTED]
  code/bk.py → code/common.py
- `run()` --calls--> `mux()`  [EXTRACTED]
  code/bk.py → code/common.py

## Import Cycles
- None detected.

## Communities (23 total, 2 thin omitted)

### Community 0 - "server.js"
Cohesion: 0.09
Nodes (45): Database, db, delKV(), fs, getKV(), path, setKV(), ApiError (+37 more)

### Community 1 - "app.js"
Cohesion: 0.15
Nodes (34): addDays(), api(), app, axes(), bestTimes(), C, charts, COLS (+26 more)

### Community 2 - "package.json"
Cohesion: 0.11
Nodes (21): dependencies, better-sqlite3@^13.2.0, chart.js@^4.4.0, dotenv@^18.0.10, express@^5.0.0, express-session@^1.18.0, description, engines (+13 more)

### Community 3 - "font"
Cohesion: 0.19
Nodes (19): font(), lerp(), adf(), draw(), rot(), run(), step(), th1() (+11 more)

### Community 4 - "random"
Cohesion: 0.33
Nodes (5): run(), step(), draw(), run(), step()

### Community 5 - "gv.py"
Cohesion: 0.35
Nodes (9): arm_state(), draw(), gear_hit(), obb(), rot(), run(), seg_hit(), step() (+1 more)

### Community 6 - "demo.js"
Cohesion: 0.20
Nodes (7): ch, fs, insD, insP, insV, names, now

### Community 7 - "common.py"
Cohesion: 0.47
Nodes (5): click(), finale(), make_audio(), pop(), tone()

### Community 8 - "hit.py"
Cohesion: 0.38
Nodes (8): ballcol(), corners(), draw(), obb(), obstacles(), rot(), run(), step()

### Community 9 - "gb.py"
Cohesion: 0.42
Nodes (7): bloop(), draw(), make_audio_gb(), run(), scol(), shimmer(), step()

### Community 10 - "wl.py"
Cohesion: 0.57
Nodes (6): colr(), draw(), run(), scr(), splash(), wave_step()

### Community 11 - "mux"
Cohesion: 0.48
Nodes (5): dang(), draw(), run(), step(), mux()

### Community 12 - "gearpl.py"
Cohesion: 0.52
Nodes (6): ballcol(), draw(), run(), spawn(), step(), update_gears()

### Community 13 - "tu.py"
Cohesion: 0.48
Nodes (5): arm_hit(), draw(), rot(), run(), step()

### Community 14 - "pil"
Cohesion: 0.53
Nodes (4): draw(), rot(), run(), step()

### Community 15 - "cd.py"
Cohesion: 0.67
Nodes (5): draw(), rot(), run(), step(), theta()

### Community 16 - "ls.py"
Cohesion: 0.67
Nodes (5): draw(), mcol(), rad(), run(), step()

### Community 17 - "plinko.py"
Cohesion: 0.60
Nodes (5): ballcol(), draw(), run(), spawn(), step()

### Community 18 - "rb.py"
Cohesion: 0.60
Nodes (5): bcol(), draw(), rot(), run(), step()

### Community 19 - "compose"
Cohesion: 0.48
Nodes (5): compose(), bar(), draw(), run(), step()

### Community 20 - "math"
Cohesion: 0.60
Nodes (3): draw(), run(), step()

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `make_audio()` connect `common.py` to `font`, `random`, `gv.py`, `hit.py`, `wl.py`, `mux`, `gearpl.py`, `tu.py`, `pil`, `cd.py`, `ls.py`, `plinko.py`, `rb.py`, `compose`, `math`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `server.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09155844155844156 - nodes in this community are weakly interconnected._
- **Why does `Writer` connect `Writer` to `font`, `random`, `gv.py`, `common.py`, `hit.py`, `gb.py`, `wl.py`, `mux`, `gearpl.py`, `tu.py`, `pil`, `cd.py`, `ls.py`, `plinko.py`, `rb.py`, `compose`, `math`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `package.json` be split into smaller, more focused modules?**
  _Cohesion score 0.11255411255411256 - nodes in this community are weakly interconnected._
- **Why does `compose()` connect `compose` to `font`, `random`, `gv.py`, `common.py`, `hit.py`, `gb.py`, `wl.py`, `mux`, `gearpl.py`, `tu.py`, `pil`, `cd.py`, `ls.py`, `plinko.py`, `rb.py`, `math`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._